import asyncio
import functools
import importlib
import multiprocessing
import queue
import time

import twilio.base.values
import twilio.rest

import slixmpp

import vbx
import vbx.util


class XMPPComponent(slixmpp.ComponentXMPP):
    def __init__(self, jid, secret, server, port, target, timeout=0.5):
        self.target = target
        self.twilio_queue = multiprocessing.Queue()

        self.timeout = timeout

        self.vbx_config = None

        self.target_online = multiprocessing.Value('B')

        super().__init__(jid, secret, server, port)

    def start(self):
        self.register_plugin('xep_0030')  # service discovery
        self.register_plugin('xep_0004')  # data forms
        self.register_plugin('xep_0060')  # pubsub
        self.register_plugin('xep_0199')  # ping
        self.register_plugin('xep_0172')  # nick

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('disconnect', self.reconnect)
        self.add_event_handler('got_offline', self.set_offline)
        self.add_event_handler('got_online', self.set_online)
        self.add_event_handler('message', self.recv_from_xmpp)

        self.schedule('Check Twilio Queue', self.timeout, self.check_twilio, repeat=True)

        self.connect()

        self.process()


    def session_start(self, data):
        self.vbx_config = importlib.import_module('vbx.config')

        self.twilio_client = twilio.rest.Client(username=self.vbx_config.auth[0], password=self.vbx_config.auth[1])

        self.send_presence_subscription(self.target)

    def reconnect(self, data):
        while not self.connect():
            time.sleep(5)

    def set_offline(self, presence):
        if presence['from'].bare != self.target:
            return

        self.target_online.value = 0

    def set_online(self, presence):
        if presence['from'].bare != self.target:
            return

        self.target_online.value = 1

        for number, name in self.vbx_config.contacts.items():
            self.send_presence(pto=self.target, pfrom=number + '@' + self.boundjid.domain, pnick=name, ptype='available')

    def recv_from_xmpp(self, msg):
        if not self.vbx_config:
            return

        if msg['from'].bare != self.target:
            return

        to = msg['to'].node

        media_url = vbx.util.get_media_url(msg['body'].split(' ', 1)[0], twilio.base.values.unset)

        self.twilio_client.messages.create(to, body=msg['body'], from_=self.vbx_config.number, media_url=media_url)

    def _send_from_twilio(self, event, msg):
        if not self.vbx_config:
            return

        from_ = event.from_ + '@' + self.boundjid.domain

        if msg:
            self.send_message(self.target, msg, mfrom=from_)

        if event.media_url:
            self.send_message(self.target, 'Media: ' + event.media_url, mfrom=from_)

    def check_twilio(self):
        try:
            self._send_from_twilio(*self.twilio_queue.get_nowait())
        except queue.Empty:
            pass

    def send_from_twilio(self, event, msg):
        self.twilio_queue.put((event, msg))

    def online(self):
        return self.target_online.value > 0


class XMPP(vbx.Device):
    def __init__(self, jid, secret, server, port, target):
        self.component = XMPPComponent(jid, secret, server, port, target)

    def start(self):
        self.process = multiprocessing.Process(target=self.component.start, name='XMPPComponent')
        self.process.start()

    def online(self):
        return self.component.online()

    def send(self, event, message, response):
        self.component.send_from_twilio(event, message)
