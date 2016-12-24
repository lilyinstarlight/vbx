class Device:
    def online(self):
	return False

    def dial(self, event):
	raise NotImplementedError

    def send(self, event, message):
	raise NotImplementedError
