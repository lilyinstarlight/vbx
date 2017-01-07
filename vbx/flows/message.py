import vbx

class Message(vbx.Flow):
    def __init__(self, message, to=None, **kwargs):
        self.message = message
        self.to = to

        super().__init__(**kwargs)

    def dial(self, event, response):
        response.message(self.message, to=self.to)

        self.completed = True

    def send(self, event, message, response):
        response.message(self.message, to=self.to)

        self.completed = True
