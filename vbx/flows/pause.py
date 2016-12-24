import vbx

class Pause(vbx.Flow):
    def __init__(self, length, **kwargs):
	self.length = length

	super().__init__(**kwargs)

    def dial(self, event, response):
	response.pause(length=self.length)
