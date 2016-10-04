class Device:
    def online(self):
	return False

    def dial(self):
	raise NotImplementedError

    def send(self, message):
	raise NotImplementedError
