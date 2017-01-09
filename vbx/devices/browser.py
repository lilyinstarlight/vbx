import re

import twilio.twiml

import vbx


online = False
number = re.compile("^[\d\+\-\(\) ]+$")


class Browser(vbx.Device):
    def online(self):
        global online

        return online

    def dial(self, event, response):
        if number.match(event.to):
            response.dial(event.to)
        else:
            dial = response.dial()
            dial.client(event.to)

    def send(self, event, message, response):
        pass
