import twilio.twiml
import twilio.rest

import slixmpp.componentxmpp

import vbx

online = False

client = None

class XMPP(vbx.Device):
    def __init__(self, jid, secret, server, port, target):
        self.component = XMPPComponent(jid, secret, server, port)
        self.target = target

    def online(self):
        return True

    def send(self, event, message, response):
        self.component.send(event, self.target, message)

class XMPPComponent(slixmpp.componentxmpp.ComponentXMPP):
    def __init__(self, jid, secret, server, port):
        pass

    def recv(self, msg):
        global client

        if not client:
            import vbx.config
            client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])

        client.messages.create('', body='', from_=config.number)

    def send(self, event, target, msg):
        pass
