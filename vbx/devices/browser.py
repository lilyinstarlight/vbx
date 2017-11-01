import asyncio
import importlib
import itertools
import json
import multiprocessing
import time

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

        current_status = {}

        with self.clients.get_lock():
            self.clients.value += 1

        try:
            while True:
                last_call = None
                wait_call = None
                last_message = None

                events = sorted(list(itertools.chain(
                    self.twilio_client.calls.page(from_=self.vbx_config.number),
                    self.twilio_client.calls.page(to=self.vbx_config.number),
                    self.twilio_client.messages.page(from_=self.vbx_config.number),
                    self.twilio_client.messages.page(to=self.vbx_config.number))), key=lambda obj: obj.date_created)

                send_call = False
                send_message = False
                for event in events:
                    if event.sid[:2] == 'CA':
                        if not send_call:
                            if event.sid == current_call:
                                send_call = True

                            continue

                        if not wait_call and (event.status == 'queued' or event.status == 'ringing' or event.status == 'in-progress'):
                            wait_call = event.sid

                        last_call = event.sid

                        yield from asyncio.wait([ws.send(json.dumps(vbx.util.call_encode(event))) for ws in self.websockets])
                    elif event.sid[:2] == 'SM' or event.sid[:2] == 'MM':
                        if not send_message:
                            if event.sid == current_message:
                                send_message = True

                            continue

                        last_message = event.sid

                        if not event.error_code:
                            yield from asyncio.wait([ws.send(json.dumps(vbx.util.message_encode(event))) for ws in self.websockets])

                    current_call = wait_call if wait_call else last_call
                    current_message = last_message

                yield from websocket.ping()
                yield from asyncio.sleep(self.timeout)
        except websockets.exceptions.ConnectionClosed:
            pass
        except ConnectionError:
            pass
        except:
            try:
                yield from websocket.close()
            except websockets.exceptions.ConnectionClosed:
                pass

            raise

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
