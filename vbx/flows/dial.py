import vbx


class Dial(vbx.Flow):
    def __init__(self, number=None, client=None, conference=None, queue=None, sip=None, **kwargs):
        self.number = number
        self.client = client
        self.conference = conference
        self.queue = queue
        self.sip = sip

        super().__init__(**kwargs)

    def dial(self, event, response):
        dial = response.dial()

        if self.number:
            dial.number(self.number)

        if self.client:
            dial.client(self.client)

        if self.conference:
            dial.conference(self.conference)

        if self.queue:
            dial.queue(self.queue)

        if self.sip:
            dial.sip(self.sip)

        self.completed = True
