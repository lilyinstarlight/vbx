import vbx

class Message(vbx.Event):
    def handle(self, flow):
	return flow.send(self.body['message'])
