import mimetypes
import smtplib
import urllib.request

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText

import vbx
import vbx.config


class Email(vbx.Device):
    def __init__(self, from_, to):
        self.from_ = from_
        self.to = to

    def send(self, event, message, response):
        msg = MIMEMultipart()

        if event.from_ in vbx.config.contacts:
            from_ = vbx.config.contacts[events.from_]
        else
            from_ = events.from_

        msg['Subject'] = 'SMS From {}'.format(from_)
        msg['From'] = self.from_
        msg['To'] = self.to

        msg.attach(MIMEText(message))

        if event.media_url:
            main_type, sub_type = event.media_type.split('/', 1)
            part = MIMENonMultipart(main_type, sub_type)
            part.set_payload(urllib.request.urlopen(event.media_url).read())
            encoders.encode_base64(part)
            part['Content-Disposition'] = 'attachment; filename="media.{}"'.format(mimetypes.guess_extension(event.media_type))
            msg.attach(part)

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
