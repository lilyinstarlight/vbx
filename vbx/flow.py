class Flow:
    def __init__(self, next=None):
	self.next = next

    def dial(self, event, response):
	raise NotImplementedError

    def send(self, event, message, response):
	raise NotImplementedError
