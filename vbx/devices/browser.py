import asyncio
import datetime
import importlib
import itertools
import json
import multiprocessing

import twilio

import websockets

import vbx
import vbx.util


class BrowserComponent:
    def __init__(self, timeout=0.5):
        self.timeout = timeout

        self.clients = multiprocessing.Value('B')

        self.websockets = []

    def start(self):
        self.vbx_config = importlib.import_module('vbx.config')

        self.twilio_client = twilio.rest.Client(username=self.vbx_config.auth[0], password=self.vbx_config.auth[1])

        self.server = websockets.serve(self.serve, self.vbx_config.wsocket[0], self.vbx_config.wsocket[1])

        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def serve(self, websocket, path):
        self.websockets.append(websocket)

        current_call = yield from websocket.recv()
        current_message = yield from websocket.recv()

        with self.clients.get_lock():
            self.clients.value += 1

        try:
            while True:
                last_call = None;
                last_message = None;

                send = False
                for call in itertools.chain(self.twilio_client.calls.page(to=self.vbx_config.number), self.twilio_client.calls.page(from_=self.vbx_config.number)):
                    if send:
                        last_call = call
                        yield from asyncio.wait(ws.send(json.dumps(vbx.util.call_encode(call))) for ws in self.websockets)

                    if call.sid == current_call:
                        send = True

                send = False
                for message in itertools.chain(self.twilio_client.messages.page(to=self.vbx_config.number), self.twilio_client.messages.page(from_=self.vbx_config.number)):
                    if send:
                        if not message.error_code:
                            last_message = message
                            yield from asyncio.wait(ws.send(json.dumps(vbx.util.message_encode(message))) for ws in self.websockets)

                    if message.sid == current_message:
                        send = True

                if last_call:
                    current_call = last_call.sid

                if last_message:
                    current_message = last_message.sid

                yield from websocket.ping()
                yield from asyncio.sleep(self.timeout)
        finally:
            yield from websocket.close()

            with self.clients.get_lock():
                self.clients.value -= 1

            self.websockets.remove(websocket)

    def online(self):
        return self.clients.value > 0


component = None
master = False


class Browser(vbx.Device):
    def __init__(self):
        global component

        if component:
            self.component = component
        else:
            self.component = BrowserComponent()
            component = self.component

    def start(self):
        global master

        if not master:
            master = True

            self.process = multiprocessing.Process(target=self.component.start, name='BrowserComponent')
            self.process.start()

    def online(self):
        return self.component.online()

    def dial(self, event, response):
        response.dial('vbx').client('vbx')

    def send(self, event, message, response):
        pass
