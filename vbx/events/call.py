import vbx

class Call(vbx.Event):
    def handle(self, flow):
	return flow.dial()
