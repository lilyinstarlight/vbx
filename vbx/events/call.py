import re

import twilio.twiml

import vbx
import vbx.config


number = re.compile("^[\d\+\-\(\) ]+$")


class Call(vbx.Event):
    def __init__(self, request):
        super().__init__(request)

        self.sid = request['CallSid']
        self.status = request['CallStatus']
        self.direction = request['Direction']

        try:
            self.forwarded_from = request['ForwardedFrom']
        except KeyError:
            self.forwarded_from = None

        try:
            self.caller_name = request['CallerName']
        except KeyError:
            self.caller_name = None

    def handle(self, flows):
        response = twilio.twiml.Response()

        if self.to == vbx.config.number:
            for flow in flows:
                flow.dial(self, response)

                if not flow.completed and flow.next:
                    response.redirect(flow.next)
                    break
        else:
            dial = response.dial(callerId=vbx.config.number)

            if number.match(event.to):
                dial.number(event.to)
            else:
                dial.client(event.to)

        return response
