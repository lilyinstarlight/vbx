import os

import vbx.devices
import vbx.flows

# address to listen on
addr = ('', 8000)
wsocket = ('', 8001)

# path to websocket
socket = 'ws://localhost:' + str(wsocket[1]) + '/'

# log locations
log = '/var/log/vbx/vbx.log'
http_log = '/var/log/vbx/http.log'

# template directory to use
template = os.path.dirname(__file__) + '/html'
resource = os.path.dirname(__file__) + '/res'

# account sid and auth token
auth = ('', '')

# app sid
app = ''

# number from account to use
number = ''

# call flows (make sure they connect properly by key)
calls = {}

# message flows (make sure they connect properly by key)
messages = {}

# contacts
contacts = {}
