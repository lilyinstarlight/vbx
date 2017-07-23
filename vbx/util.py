import urllib.parse
import urllib.request

def get_media_url(url, default=None):
    url = urllib.parse.urlparse(url)
    if url.scheme and url.netloc:
        with urllib.request.urlopen(urllib.request.Request(url=url.geturl(), method='HEAD')) as response:
            if response.getheader('Content-Type').split('/', 1)[0] in ['image', 'video', 'audio']:
                return response.geturl()

    return default
