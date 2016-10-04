class Flow:
    def __init__(self, next=None):
	self.next = next

    def dial(self):
	raise NotImplementedError

    def send(self, message):
	raise NotImplementedError
