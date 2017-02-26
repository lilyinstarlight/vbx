import smtplib

from email.mime.text import MIMEText

import vbx
import vbx.config


class Email(vbx.Device):
    def __init__(self, from_, to):
        self.from_ = from_
        self.to = to

    def send(self, event, message, response):
        msg = MIMEText(message)

        if event.from_ in vbx.config.contacts:
            from_ = vbx.config.contacts[events.from_]
        else
            from_ = events.from_

        msg['Subject'] = 'SMS From {}'.format(from_)
        msg['From'] = self.from_
        msg['To'] = self.to

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
