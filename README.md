vbx
===

vbx is an application for managing Twilio numbers. It features a browser interface with making and receiving calls and ability to see messages to and from your contacts. It additionally features the ability to connect arbitrary flows that optionally connect to devices it determines are online. It does not feature any ability to login or password protect so I recommend running it behind a reverse-proxy server (such as nginx) and use its HTTP authentication to protect all resources except for the '/flow' resource. See below for how to write simple flows.


Flow File
---------


The following file is the example configuration that comes with the program. It details the structure for certain variables and shows example flows and flow chaining. Flows are chained via the 'next' parameter which gets the response gets redirected to if the given flow is not complete (e.g. no devices were online). Other flows not shown here are `vbx.flows.Hangup`, `vbx.flows.Message`, `vbx.flows.Pause`, `vbx.flows.Play`, `vbx.flows.Record`, `vbx.flows.Redirect`, `vbx.flows.Reject`, and `vbx.flows.Say`. The `vbx.flows.Device` flow can take several devices that it tries in order until it finds one that is online or then finds one that has no online/offline distinction. Other devices not detailed here are `vbx.devices.XMPP`, which is a gateway to a component for an XMPP server, and `vbx.devices.Email` which is a simple one-way gateway to notify you of unseen messages.

```python
import vbx.devices
import vbx.flows

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
```
