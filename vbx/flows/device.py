import vbx

class Device(vbx.Flow):
    def __init__(self, devices, **kwargs):
	self.devices = devices

	super().__init__(**kwargs)

    def dial(self, event, response):
	for device in self.devices:
	    if device.online():
		device.dial(event, response)
		self.completed = True
		break

    def send(self, event, message, response):
	for device in self.devices:
	    if device.online():
		device.send(event, message, response)
		self.completed = True
		break
