import urllib.parse
import urllib.request


api_base = 'https://api.twilio.com/2010-04-01'


def get_media_url(url, default=None):
    url = urllib.parse.urlparse(url)
    if url.scheme and url.netloc:
        with urllib.request.urlopen(urllib.request.Request(url=url.geturl(), method='HEAD')) as response:
            if response.getheader('Content-Type').split('/', 1)[0] in ['image', 'video', 'audio']:
                return response.geturl()

    return default


def call_encode(call):
    return {'sid': call.sid, 'annotation': call.annotation, 'date': call.date_created.isoformat().replace('+00:00', 'Z'), 'direction': call.direction, 'duration': call.duration, 'from': call.from_, 'to': call.to, 'status': call.status}


def message_encode(msg):
    encoded = {'sid': msg.sid, 'body': msg.body, 'date': msg.date_created.isoformat().replace('+00:00', 'Z'), 'direction': msg.direction, 'from': msg.from_, 'to': msg.to, 'media_url': None, 'media_type': None}

    if int(msg.num_media) > 0:
        media = msg.media.list(limit=1)[0]
        encoded.update({'media_url': (api_base + media.uri)[:-5], 'media_type': media.content_type})

    return encoded
