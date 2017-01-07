class Flow:
    def __init__(self, next=None):
        self.next = next

        self.completed = False

    def dial(self, event, response):
        raise NotImplementedError

    def send(self, event, message, response):
        raise NotImplementedError
