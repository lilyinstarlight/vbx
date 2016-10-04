class Flow:
    next = None

    def dial(self):
	raise NotImplementedError

    def send(self, message):
	raise NotImplementedError
