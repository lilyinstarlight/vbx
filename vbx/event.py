class Event:
    def __init__(self, request):
	self.account = request['AccountSid']
	self.from_ = request['From']
	self.to = request['To']

	try:
	    self.from_city = request['FromCity']
	except KeyError:
	    self.from_city = None

	try:
	    self.from_state = request['FromState']
	except KeyError:
	    self.from_state = None

	try:
	    self.from_zip = request['FromZip']
	except KeyError:
	    self.from_zip = None

	try:
	    self.from_country = request['FromCountry']
	except KeyError:
	    self.from_country = None

	try:
	    self.to_city = request['ToCity']
	except KeyError:
	    self.to_city = None

	try:
	    self.to_state = request['ToState']
	except KeyError:
	    self.to_state = None

	try:
	    self.to_zip = request['ToZip']
	except KeyError:
	    self.to_zip = None

	try:
	    self.to_country = request['ToCountry']
	except KeyError:
	    self.to_country = None

    def handle(self, flow):
	raise NotImplementedError
