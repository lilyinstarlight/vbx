import vbx


class SMS(vbx.Device):
    def __init__(self, number):
        self.number = number

    def send(self, event, message, response):
        response.message('From: ' + event.from_ + '\n' + message, to=self.number)
