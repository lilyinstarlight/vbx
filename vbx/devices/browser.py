import asyncio
import ctypes
import datetime
import importlib
import itertools
import json
import multiprocessing
import random
import string

import twilio

import websockets

import vbx
import vbx.util


class BrowserComponent:
    def __init__(self, ignored=[], timeout=0.5):
        self.ignored = ignored
        self.timeout = timeout

        self.clients = multiprocessing.Value(ctypes.c_ubyte)
        self.key = multiprocessing.Array(ctypes.c_char, 17)

        self.clients.value = 0
        self.key.value = b''

        self.running = multiprocessing.Value(ctypes.c_bool)

        self.running.value = False

        self.websockets = []

    def run(self):
        self.running.value = True

        self.vbx_config = importlib.import_module('vbx.config')

        self.twilio_client = twilio.rest.Client(username=self.vbx_config.auth[0], password=self.vbx_config.auth[1])

        self.stop = asyncio.get_event_loop().create_future()

        asyncio.get_event_loop().create_task(self.check_running())
        asyncio.get_event_loop().run_until_complete(self.server())

    def stop(self):
        self.running.value = False

    async def check_running(self):
        while True:
            if not self.running.value:
                self.stop.set_result(None)
                break

            await asyncio.sleep(self.timeout)

    async def server(self):
        async with websockets.serve(self.serve, self.vbx_config.wsocket[0], self.vbx_config.wsocket[1]):
            await self.stop

    async def serve(self, websocket, path):
        key = await websocket.recv()

        with self.key.get_lock():
            if not self.key.value.decode('ascii') or key != self.key.value.decode('ascii'):
                return

            self.key.value = b''

        self.websockets.append(websocket)

        current_call = await websocket.recv()
        current_message = await websocket.recv()

        start_time = datetime.datetime.now() - datetime.timedelta(days=7)

        with self.clients.get_lock():
            self.clients.value += 1

        try:
            while True:
                if self.websockets.index(websocket) == 0:
                    last_call = None
                    wait_call = None
                    last_message = None

                    events = sorted(list(itertools.chain(
                        self.twilio_client.calls.page(from_=self.vbx_config.number, start_time_after=start_time),
                        self.twilio_client.calls.page(to=self.vbx_config.number, start_time_after=start_time),
                        self.twilio_client.messages.page(from_=self.vbx_config.number, date_sent_after=start_time),
                        self.twilio_client.messages.page(to=self.vbx_config.number, date_sent_after=start_time))), key=lambda obj: obj.date_created)

                    send_call = False
                    send_message = False
                    for event in events:
                        if event.from_ in self.ignored or event.to in self.ignored:
                            continue

                        if event.sid[:2] == 'CA':
                            if not send_call:
                                if event.sid == current_call or current_call is None:
                                    send_call = True

                                continue

                            if not wait_call and (event.status == 'queued' or event.status == 'ringing' or event.status == 'in-progress'):
                                wait_call = event.sid

                            last_call = event.sid

                            await asyncio.wait([ws.send(json.dumps(vbx.util.call_encode(event))) for ws in self.websockets])
                        elif event.sid[:2] == 'SM' or event.sid[:2] == 'MM':
                            if not send_message:
                                if event.sid == current_message or current_message is None:
                                    send_message = True

                                continue

                            last_message = event.sid

                            if not event.error_code:
                                await asyncio.wait([ws.send(json.dumps(vbx.util.message_encode(event))) for ws in self.websockets])

                        current_call = wait_call if wait_call else last_call
                        current_message = last_message

                        start_time = event.date_created

                await websocket.ping()
                await asyncio.sleep(self.timeout)
        except websockets.exceptions.ConnectionClosed:
            pass
        except ConnectionError:
            pass
        except Exception:
            try:
                await websocket.close()
            except websockets.exceptions.ConnectionClosed:
                pass

            raise
        finally:
            with self.clients.get_lock():
                self.clients.value -= 1

            self.websockets.remove(websocket)

    def gen(self):
        with self.key.get_lock():
            self.key.value = ''.join(random.choice(string.ascii_letters) for _ in range(16)).encode('ascii')

            return self.key.value.decode('ascii')

    def online(self):
        return self.clients.value > 0


component = None
started = False


class Browser(vbx.Device):
    def __init__(self, ignored=[]):
        global component

        if component:
            self.component = component
        else:
            self.component = BrowserComponent(ignored)
            component = self.component

    def start(self):
        global started

        if not started:
            self.process = multiprocessing.Process(target=self.component.run, name='BrowserComponent')
            self.process.start()

            started = True

    def stop(self):
        self.component.stop()

    def online(self):
        return self.component.online()

    def dial(self, event, response):
        response.dial('vbx').client('vbx')

    def send(self, event, message, response):
        pass
