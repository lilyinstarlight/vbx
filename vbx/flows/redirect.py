import vbx

class Redirect(vbx.Flow):
    def __init__(self, url, **kwargs):
	self.url = url

	super().__init__(**kwargs)

    def dial(self, event, response):
	response.redirect(self.url)

	self.completed = True

    def send(self, event, message, response):
	response.redirect(self.url)

	self.completed = True
