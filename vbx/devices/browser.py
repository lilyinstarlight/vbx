import asyncio
import datetime
import multiprocessing
import queue

import websockets

import vbx
import vbx.util


class BrowserComponent:
    def __init__(self, host, port, timeout=0.5):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.call_queue = multiprocessing.Queue()
        self.message_queue = multiprocessing.Queue()

        self.clients = multiprocessing.Value('B')

        self.websockets = []

    def start(self):
        self.server = websockets.serve(self.serve, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def serve(self, websocket, path):
        self.websockets.append(websocket)

        with self.clients.get_lock():
            self.clients += 1

        try:
            while True:
                    try:
                        call = vbx.util.call_encode(self.call_queue.get_nowait())
                        yield from asyncio.wait(ws.send(call) for ws in self.websockets)
                    except queue.Empty:
                        pass

                    try:
                        message = vbx.util.message_encode(self.message_queue.get_nowait())
                        yield from asyncio.wait(ws.send(message) for ws in self.websockets)
                    except queue.Empty:
                        pass

                    yield from websocket.ping()
                    yield from asyncio.sleep(self.timeout)
        finally:
            yield from websocket.close()

            with self.clients.get_lock():
                self.clients -= 1

            self.websockets.remove(websocket)

    def online(self):
        return self.clients.value > 0

    def dial(self, event):
        self.call_queue.put(event)

    def send(self, event):
        self.message_queue.put(event)


class Browser(vbx.Device):
    def __init__(self):
        self.component = BrowserComponent(*vbx.config.wsocket)

        self.process = multiprocessing.Process(target=self.component.start, name='BrowserComponent')
        self.process.start()

    def online(self):
        return self.component.online()

    def dial(self, event, response):
        response.dial('vbx').client('vbx')

        self.component.dial(event)

    def send(self, event, message, response):
        self.component.send(event)
