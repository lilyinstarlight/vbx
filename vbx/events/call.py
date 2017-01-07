import twilio.twiml

import vbx

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

	for flow in flows:
	    flow.dial(self, response)

	    if not flow.completed and flow.next:
		response.redirect(flow.next)
		break

	return response