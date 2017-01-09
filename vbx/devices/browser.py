import re

import twilio.twiml

import vbx
import vbx.config


online = False
number = re.compile("^[\d\+\-\(\) ]+$")


class Browser(vbx.Device):
    def online(self):
        global online

        return online

    def dial(self, event, response):
        dial = response.dial(callerId=vbx.config.number)

        if number.match(event.to):
            dial.number(event.to)
        else:
            dial.client(event.to)

    def send(self, event, message, response):
        pass
