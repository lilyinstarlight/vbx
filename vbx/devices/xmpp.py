import asyncio
import functools
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
        return self.component.online

    def send(self, event, message, response):
        self.component.send(event, message)

class XMPPComponent(slixmpp.ComponentXMPP):
    def __init__(self, jid, secret, server, port, target):
        self.target = target
        self.queue = queue.Queue()

        self.config = None

        self.online = False

        self.thread = threading.Thread(target=functools.partial(self.component_thread, jid, secret, server, port), name='XMPPComponent')
        self.thread.start()

    def component_thread(self, jid, secret, server, port):
        asyncio.set_event_loop(asyncio.new_event_loop())

        super().__init__(jid, secret, server, port)

        self.add_event_handler('message', self.recv)
        self.add_event_handler('got_offline', self.offline)
        self.add_event_handler('got_online', self.online)

        if not self.connect():
            raise Exception('Could not connect to XMPP server')

        self.send_presence_subscription(self.target)

        while True:
            self.process(timeout=0.5)

            try:
                args = self.queue.get_nowait()
                self._send(*args)
            except queue.Empty:
                pass

    def create_config(self):
        self.config = __import__('vbx.config')
        self.config.revcontacts = {contact: number for number, contact in self.config.contacts.items()}

        self.twilio_client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])

    def recv(self, msg):
        if not self.config:
            self.create_config()

        to = msg['to'].node

        if to in self.config.revcontacts:
            to = self.config.revcontacts[to]

        self.twilio_client.messages.create(to, body=msg['body'], from_=vbx.config.number)

    def _send(self, event, target, msg):
        if not self.config:
            self.create_config()

        from_ = event['From']

        if from_ in self.config.contacts:
            from_ = self.config.contacts[from_]

        self.send_message(target, msg, mfrom=from_ + '@' + self.boundjid.domain)

    def offline(self):
        self.online = False

    def online(self):
        self.online = True

    def send(self, event, target, msg):
        self.queue.put((event, target, msg))
