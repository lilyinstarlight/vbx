import os

import vbx.devices
import vbx.flows

# address to listen on
addr = ('', 8080)

# log locations
log = '/var/log/vbx/vbx.log'
http_log = '/var/log/vbx/http.log'

# template directory to use
template = os.path.dirname(__file__) + '/html'
resource = os.path.dirname(__file__) + '/res'

# account sid and auth token
auth = ('AC0123456789abcdef0123456789abcdef', '0123456789abcdef0123456789abcdef')

# app sid
app = 'AP0123456789abcdef0123456789abcdef'

# number from account to use
number = '+18001234567'

# call flows (make sure they connect properly by key)
calls = {
    'default': [vbx.flows.Device(devices=[vbx.devices.Browser()], next='phone')],
    'phone': [vbx.flows.Dial(number='+18005555555')],
}

# message flows (make sure they connect properly by key)
messages = {
    'default': [vbx.flows.Device(devices=[vbx.devices.Browser(), vbx.devices.SMS(number='+18005555555')])],
}

# contacts
contacts = {
    '+18005555555': 'BusinessName'
}
