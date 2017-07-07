import asyncio
import functools
import importlib
import queue
import threading

import twilio.twiml
import twilio.rest

import vbx


class XMPP(vbx.Device):
    def __init__(self, jid, secret, server, port, target):
        import slixmpp

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

                self.register_plugin('xep_0030')  # service discovery
                self.register_plugin('xep_0004')  # data forms
                self.register_plugin('xep_0060')  # pubsub
                self.register_plugin('xep_0199')  # ping
                self.register_plugin('xep_0172')  # nick

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

                self.twilio_client = twilio.rest.Client(username=self.vbx_config.auth[0], password=self.vbx_config.auth[1])

                self.send_presence_subscription(self.target)

            def recv_from_xmpp(self, msg):
                if not self.vbx_config:
                    return

                if msg['from'].bare != self.target:
                    return

                to = msg['to'].node

                body_url = urllib.parse.urlparse(msg['body'].split(' ', 1)[0])
                if body_url.scheme and body_url.netloc:
                    with urllib.request.urlopen(urllib.request.Request(url=body_url.geturl(), method='HEAD')) as response:
                        if response.getheader('Content-Type').split('/', 1)[0] in ['image', 'video', 'audio']:
                            media_url = response.geturl()

                self.twilio_client.messages.create(to, body=msg['body'], from_=self.vbx_config.number, media_url=media_url)

            def _send_from_twilio(self, event, msg):
                if not self.vbx_config:
                    return

                from_ = event.from_ + '@' + self.boundjid.domain

                if msg:
                    self.send_message(self.target, msg, mfrom=from_)

                if event.media_url:
                    self.send_message(self.target, 'Media: ' + event.media_url, mfrom=from_)

            def set_offline(self, presence):
                if presence['from'].bare != self.target:
                    return

                self.target_online = False

            def set_online(self, presence):
                if presence['from'].bare != self.target:
                    return

                self.target_online = True

                for number, name in self.vbx_config.contacts.items():
                    self.send_presence(pto=self.target, pfrom=number + '@' + self.boundjid.domain, pnick=name, ptype='available')

            def send_from_twilio(self, event, msg):
                self.twilio_queue.put((event, msg))

        self.component = XMPPComponent(jid, secret, server, port, target)

    def online(self):
        return self.component.target_online

    def send(self, event, message, response):
        self.component.send_from_twilio(event, message)
