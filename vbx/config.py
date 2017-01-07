import vbx.devices
import vbx.flows

# address to listen on
addr = ('', 8080)

# log locations
log = '/var/log/vbx/vbx.log'
httplog = '/var/log/vbx/http.log'

# template directory to use
import os.path
template = os.path.dirname(__file__) + '/html'

# account sid and auth token
auth = ('AC0123456789abcdef0123456789abcdef', '0123456789abcdef0123456789abcdef')

# number from account to use
number = '+18001234567'

# call flows (make sure they connect properly by key)
calls = {
    'call': [vbx.flows.Device(devices=[vbx.devices.Browser()], next='phone')],
    'phone': [vbx.flows.Dial(number='+18005555555')],
}

# message flows (make sure they connect properly by key)
messages = {
    'message': [vbx.flows.Device(devices=[vbx.devices.Browser(), vbx.devices.SMS(number='+18005555555')])],
}

# contacts
contacts = {
    'BusinessName': '+18005555555'
}