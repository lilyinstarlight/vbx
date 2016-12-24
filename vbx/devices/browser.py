import twilio.twiml

online = False

class Browser(vbx.Device):
    def online(self):
	global online

	return online

    def dial(self, event, response):
	return twilio.twiml.Client('browser')

    def send(self, event, message, response):
	return None
