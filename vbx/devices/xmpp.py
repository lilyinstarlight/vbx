import queue
import threading

import twilio.twiml
import twilio.rest

import slixmpp.componentxmpp

import vbx


class XMPP(vbx.Device):
    def __init__(self, jid, secret, server, port, target):
        self.component = XMPPComponent(jid, secret, server, port, target)

    def online(self):
        return self.component.online

    def send(self, event, message, response):
        self.component.send(event, message)

class XMPPComponent(slixmpp.componentxmpp.ComponentXMPP):
    def __init__(self, jid, secret, server, port, target):
        self.jid = jid
        self.target = target
        self.queue = queue.Queue()

        self.config = None

        self.online = False

        def component_thread():
            super().__init__(jid, secret, server, port)

            self.add_event_handler('message', self.recv)
            self.add_event_handler('got_offline', self.offline)
            self.add_event_handler('got_online', self.online)

            self.connect()

            self.send_presence_subscription(self.target)

            while True:
                self.process(timeout=0.5)

                try:
                    args = self.queue.get_nowait()
                    self._send(*args)
                except queue.Empty:
                    pass

        self.thread = threading.Thread(target=component_thread, name='XMPPComponent')
        self.thread.start()

    def create_config(self):
        self.config = __import__('vbx.config')

        self.twilio_client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])

    def recv(self, msg):
        if not config:
            self.create_config()

        self.twilio_client.messages.create(msg['to'].node, body=msg['body'], from_=vbx.config.number)

    def _send(self, event, target, msg):
        if not config:
            self.create_config()

        from_ = event['From']

        if from_ in config.contacts:
            from_ = config.contacts[from_]

        self.send_message(target, msg, mfrom=from_ + '@' + self.jid)

    def offline(self):
        self.online = False

    def online(self):
        self.online = True

    def send(self, event, target, msg):
        self.queue.put((event, target, msg))
