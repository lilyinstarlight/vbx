import vbx

class SMS(vbx.Device):
    def __init__(self, number):
	self.number = number

    def online(self):
	return True

    def send(self, event, message, response):
	response.message(message, to=self.number, sender=event.from_)
