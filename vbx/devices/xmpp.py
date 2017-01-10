import asyncio
import functools
import importlib
import queue
import threading

import twilio.twiml
import twilio.rest

import slixmpp

import vbx


class XMPP(vbx.Device):
    def __init__(self, jid, secret, server, port, target):
        self.component = XMPPComponent(jid, secret, server, port, target)

    def online(self):
        return self.component.target_online

    def send(self, event, message, response):
        self.component.send_from_twilio(event, message)

class XMPPComponent(slixmpp.ComponentXMPP):
    def __init__(self, jid, secret, server, port, target):
        self.target = target
        self.twilio_queue = queue.Queue()

        self.config = None

        self.target_online = False

        self.thread = threading.Thread(target=functools.partial(self.component_thread, jid, secret, server, port), name='XMPPComponent')
        self.thread.start()

    def component_thread(self, jid, secret, server, port):
        asyncio.set_event_loop(asyncio.new_event_loop())

        super().__init__(jid, secret, server, port)

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.recv_from_xmpp)
        self.add_event_handler('got_offline', self.set_offline)
        self.add_event_handler('got_online', self.set_online)

        self.connect()

        while True:
            self.process(timeout=0.5)

            try:
                args = self.twilio_queue.get_nowait()
                self._send_from_twilio(*args)
            except queue.Empty:
                pass

    def session_start(self, data):
        self.vbx_config = importlib.import_module('vbx.config')
        self.vbx_config.revcontacts = {contact: number for number, contact in self.vbx_config.contacts.items()}

        self.twilio_client = twilio.rest.Client(username=self.vbx_config.auth[0], password=self.vbx_config.auth[1])

        self.send_presence_subscription(self.target)

    def recv_from_xmpp(self, msg):
        if not self.vbx_config:
            return

        to = msg['to'].node

        if to in self.vbx_config.revcontacts:
            to = self.vbx_config.revcontacts[to]

        self.twilio_client.messages.create(to, body=msg['body'], from_=self.vbx_config.number)

    def _send_from_twilio(self, event, msg):
        if not self.vbx_config:
            return

        from_ = event['From']

        if from_ in self.vbx_config.contacts:
            from_ = self.vbx_config.contacts[from_]

        self.send_message(self.target, msg, mfrom=from_ + '@' + self.boundjid.domain)

    def set_offline(self, data):
        self.target_online = False

    def set_online(self, data):
        self.target_online = True

    def send(self, event, msg):
        self.twilio_queue.put((event, msg))
