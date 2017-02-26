import datetime

import twilio.rest
import twilio.jwt.client

import web
import web.file
import web.form
import web.json
import web.page
import web.query

import vbx.config
import vbx.events
import vbx.devices.browser
import vbx.log


alias = '([a-zA-Z0-9._-]+)'
query = '(?:\?([\w=&+.:%-]*))?'

http = None

token = twilio.jwt.client.CapabilityToken(account_sid=vbx.config.auth[0], auth_token=vbx.config.auth[1])
token.allow_client_outgoing(vbx.config.app)
token.allow_client_incoming('vbx')

client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])

routes = {}
error_routes = {}


class IndexPage(web.page.PageHandler):
    directory = vbx.config.template
    page = 'index.html'


class AccountHandler(web.json.JSONHandler):
    def call_encode(self, call):
        return {'sid': call.sid, 'annotation': call.annotation, 'date': call.date_created.isoformat().replace('+00:00', 'Z'), 'direction': call.direction, 'duration': call.duration, 'from': call.from_formatted, 'to': call.to}

    def message_encode(self, msg):
        encoded = {'sid': msg.sid, 'body': msg.body, 'date': msg.date_created.isoformat().replace('+00:00', 'Z'), 'direction': msg.direction, 'from': msg.from_, 'to': msg.to, 'media_url': None, 'media_type': None}

        if int(msg.num_media) > 0:
            media = msg.media.list(limit=1)[0]
            encoded.update({'media_url': (client.base + media.uri)[:-5], 'media_type': media.content_type})

        return encoded


class ListHandler(web.query.QueryMixIn, AccountHandler):
    pass


class BrowserHandler(AccountHandler):
    def do_get(self):
        return 200, {'number': vbx.config.number, 'token': token.generate()}

    def do_post(self):
        with vbx.devices.browser.last_lock:
            vbx.devices.browser.last = datetime.datetime.now()

        return 204, ''


class OutgoingHandler(AccountHandler):
    def do_post(self):
        try:
            client.messages.create(self.request.body['to'], body=self.request.body['body'], from_=vbx.config.number)

            return 204, ''
        except KeyError:
            raise web.HTTPError(400)


class ContactListHandler(AccountHandler):
    def do_get(self):
        return 200, vbx.config.contacts


class ContactHandler(AccountHandler):
    def do_get(self):
        try:
            return 200, vbx.config.contacts[self.groups[0]]
        except KeyError:
            raise web.HTTPError(404)


class CallListHandler(ListHandler):
    def do_get(self):
        try:
            if 'from' in self.request.query:
                self.request.query['from_'] = self.request.query['from']
                del self.request.query['from']

            return 200, [self.call_encode(call) for call in client.calls.page(**self.request.query)]
        except TypeError:
            raise web.HTTPError(400)


class CallHandler(AccountHandler):
    def do_get(self):
        try:
            call = client.calls.get(self.groups[0])

            return 200, self.call_encode(call.fetch())
        except:
            raise web.HTTPError(404)

    def do_delete(self):
        try:
            call = client.calls.get(self.groups[0])

            call.delete()

            return 204, ''
        except:
            raise web.HTTPError(404)


class MessageListHandler(ListHandler):
    def do_get(self):
        try:
            if 'from' in self.request.query:
                self.request.query['from_'] = self.request.query['from']
                del self.request.query['from']

            return 200, [self.message_encode(message) for message in client.messages.page(**self.request.query)]
        except TypeError:
            raise web.HTTPError(400)


class MessageHandler(AccountHandler):
    def do_get(self):
        try:
            message = client.messages.get(self.groups[0])

            return 200, self.message_encode(message.fetch())
        except:
            raise web.HTTPError(404)

    def do_delete(self):
        try:
            message = client.message.get(self.groups[0])

            message.delete()

            return 204, ''
        except:
            raise web.HTTPError(404)


class FlowHandler(web.form.FormHandler):
    pass


class CallFlowHandler(FlowHandler):
    def do_post(self):
        self.event = vbx.events.Call(self.request.body)

        try:
            self.response.headers['Content-Type'] = 'text/xml'
            return 200, str(self.event.handle(vbx.config.calls[self.groups[0]]))
        except ValueError:
            raise web.HTTPError(400)
        except IndexError:
            raise web.HTTPError(404)


class MessageFlowHandler(FlowHandler):
    def do_post(self):
        self.event = vbx.events.Message(self.request.body)

        try:
            self.response.headers['Content-Type'] = 'text/xml'
            return 200, str(self.event.handle(vbx.config.messages[self.groups[0]]))
        except ValueError:
            raise web.HTTPError(400)
        except IndexError:
            raise web.HTTPError(404)


routes.update({'/': IndexPage, '/browser': BrowserHandler, '/msg': OutgoingHandler, '/contacts/': ContactListHandler, '/contacts/' + alias: ContactHandler, '/calls/' + query: CallListHandler, '/calls/' + alias: CallHandler, '/msgs/' + query: MessageListHandler, '/msgs/' + alias: MessageHandler, '/flow/voice/' + alias: CallFlowHandler, '/flow/msg/' + alias: MessageFlowHandler})
routes.update(web.file.new(vbx.config.resource, '/res'))
error_routes.update(web.json.new_error())


def start():
    global http

    http = web.HTTPServer(vbx.config.addr, routes, error_routes, log=vbx.log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
