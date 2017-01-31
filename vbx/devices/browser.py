import datetime
import threading

import vbx


last = datetime.datetime.now()
last_lock = threading.Lock()
delta = datetime.timedelta(seconds=10)


class Browser(vbx.Device):
    def online(self):
        with last_lock:
            return (datetime.datetime.now() - last) < delta

    def dial(self, event, response):
        response.dial().client('vbx')

    def send(self, event, message, response):
        pass
