import logging
import twilio.base.values
import urllib.parse
import urllib.request


api_base = 'https://api.twilio.com/2010-04-01'


log = logging.getLogger('vbx')


def get_media_url(url, default=None):
    url = urllib.parse.urlparse(url)
    url = url._replace(path=urllib.parse.quote(urllib.parse.unquote(url.path)), params=urllib.parse.quote(urllib.parse.unquote(url.params)), query=urllib.parse.quote(urllib.parse.unquote(url.query)), fragment=urllib.parse.quote(urllib.parse.unquote(url.fragment)))
    if (url.scheme == 'http' or url.scheme == 'https') and url.netloc:
        try:
            with urllib.request.urlopen(urllib.request.Request(url=url.geturl(), method='HEAD')) as response:
                if response.getheader('Content-Type').split('/', 1)[0] in ['image', 'video', 'audio']:
                    return response.geturl()
        except (IOError, urllib.error.HTTPError):
            pass

    return default


def get_split_media(body):
    media_split = body.split(' ', 1)
    media_url = get_media_url(media_split[0], twilio.base.values.unset)

    if media_url is not twilio.base.values.unset and len(media_split) == 1:
        media_split.append('')

    return body if media_url is twilio.base.values.unset else media_split[1], media_url


def call_encode(call):
    return {'sid': call.sid, 'annotation': call.annotation, 'date': call.date_created.isoformat().replace('+00:00', 'Z'), 'direction': call.direction, 'duration': call.duration, 'from': call.from_, 'to': call.to, 'status': call.status}


def message_encode(msg):
    encoded = {'sid': msg.sid, 'body': msg.body, 'date': msg.date_created.isoformat().replace('+00:00', 'Z'), 'direction': msg.direction, 'from': msg.from_, 'to': msg.to, 'media_url': None, 'media_type': None}

    if int(msg.num_media) > 0:
        try:
            media = msg.media.list(limit=1)[0]
            encoded.update({'media_url': (api_base + media.uri)[:-5], 'media_type': media.content_type})
        except IndexError:
            log.exception('Message with media count greater than zero has no media')

    return encoded
