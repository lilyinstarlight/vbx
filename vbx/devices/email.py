import smtplib

from email.mime.text import MIMEText

import vbx


class Email(vbx.Device):
    def __init__(self, from_, to):
        self.from_ = from_
        self.to = to

    def send(self, event, message, response):
        msg = MIMEText(message)

        msg['Subject'] = 'SMS From {}'.format(event.from_)
        msg['From'] = self.from_
        msg['To'] = self.to

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
