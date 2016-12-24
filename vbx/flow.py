class Flow:
    def __init__(self, next=None):
	self.next = next

    def dial(self, event):
	raise NotImplementedError

    def send(self, event, message):
	raise NotImplementedError
