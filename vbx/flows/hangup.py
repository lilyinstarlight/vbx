import vbx

class Hangup(vbx.Flow):
    def dial(self, event, response):
	response.hangup()

	self.completed = True
