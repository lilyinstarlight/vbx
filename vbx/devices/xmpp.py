import vbx

class XMPP(vbx.Device):
    def __init__(self, jid):
	self.jid = jid

    def online(self):
	pass

    def dial(self, event, response):
	pass

    def send(self, event, message, response):
	pass
