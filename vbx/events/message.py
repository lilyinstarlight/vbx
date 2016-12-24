import vbx

class Message(vbx.Event):
    def __init__(self, request):
	super().__init__(request)

	self.sid = request['MessageSid']
	self.service_sid = request['MessagingServiceSid']
	self.body = request['Body']
	self.num_media = request['NumMedia']

	try:
	    self.media_type = request['MediaContentType']
	except KeyError:
	    self.media_type = None

	try:
	    self.media_url = request['MediaUrl']
	except KeyError:
	    self.media_url = None

    def handle(self, flow):
	return flow.send(self, self.body)
