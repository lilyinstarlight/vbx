import vbx

class Play(vbx.Flow):
    def __init__(self, url=None, digits=None, loop=1, **kwargs):
	self.url = url
	self.digits = digits
	self.loop = loop

	super().__init__(**kwargs)

    def dial(self, event, response):
	response.play(self.url, self.digits, loop=self.loop)
