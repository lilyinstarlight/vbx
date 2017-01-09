import twilio.twiml

import vbx


online = False


class Browser(vbx.Device):
    def online(self):
        global online

        return online

    def dial(self, event, response):
        response.dial().client('vbx')

    def send(self, event, message, response):
        pass
