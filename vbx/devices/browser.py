import datetime

import twilio.twiml

import vbx


last = datetime.datetime.now()
delta = datetime.timedelta(seconds=10)


class Browser(vbx.Device):
    def online(self):
        return (datetime.datetime.now() - last) > delta

    def dial(self, event, response):
        response.dial().client('vbx')

    def send(self, event, message, response):
        pass
