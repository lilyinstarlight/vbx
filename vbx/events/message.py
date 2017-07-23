import twilio.twiml.messaging_response

import vbx


class Message(vbx.Event):
    def __init__(self, request):
        super().__init__(request)

        self.sid = request['MessageSid']
        self.body = request['Body']
        self.num_media = request['NumMedia']

        try:
            self.service_sid = request['MessagingServiceSid']
        except KeyError:
            self.service_sid = None

        try:
            self.media_type = request['MediaContentType0']
        except KeyError:
            self.media_type = None

        try:
            self.media_url = request['MediaUrl0']
        except KeyError:
            self.media_url = None

    def handle(self, flows):
        response = twilio.twiml.messaging_response.MessagingResponse()

        for flow in flows:
            flow.send(self, self.body, response)

            if not flow.completed and flow.next:
                response.redirect(flow.next)
                break

        return response
