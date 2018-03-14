import datetime

import twilio.base.values
import twilio.rest
import twilio.jwt.client

import fooster.web
import fooster.web.file
import fooster.web.form
import fooster.web.json
import fooster.web.page
import fooster.web.query

import vbx.config
import vbx.events
import vbx.devices.browser
import vbx.util


alias = '([a-zA-Z0-9._-]+)'
query = '(?:\?([\w=&+.:%-]*))?'

http = None

token = twilio.jwt.client.ClientCapabilityToken(account_sid=vbx.config.auth[0], auth_token=vbx.config.auth[1])
token.allow_client_outgoing(vbx.config.app)
token.allow_client_incoming('vbx')

client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])
vbx.util.api_base = client.api.base_url

routes = {}
error_routes = {}


class IndexPage(fooster.web.page.PageHandler):
    directory = vbx.config.template
    page = 'index.html'


class AccountHandler(fooster.web.json.JSONHandler):
    pass


class ListHandler(fooster.web.query.QueryMixIn, AccountHandler):
    pass


class BrowserHandler(AccountHandler):
    def do_get(self):
        return 200, {'number': vbx.config.number, 'token': token.to_jwt().decode(), 'socket': vbx.config.socket, 'key': vbx.devices.browser.component.gen()}


class OutgoingHandler(AccountHandler):
    def do_post(self):
        try:
            body = self.request.body['body']
            media_url = vbx.util.get_media_url(body.split(' ', 1)[0], twilio.base.values.unset)

            message = client.messages.create(self.request.body['to'], body=body, from_=vbx.config.number, media_url=media_url)

            return 200, vbx.util.message_encode(message)
        except KeyError:
            raise fooster.web.HTTPError(400)


class ContactListHandler(AccountHandler):
    def do_get(self):
        return 200, vbx.config.contacts


class ContactHandler(AccountHandler):
    def do_get(self):
        try:
            return 200, vbx.config.contacts[self.groups[0]]
        except KeyError:
            raise fooster.web.HTTPError(404)


class CallListHandler(ListHandler):
    def do_get(self):
        try:
            if 'from' in self.request.query:
                self.request.query['from_'] = self.request.query['from']
                del self.request.query['from']

            return 200, [vbx.util.call_encode(call) for call in client.calls.list(**self.request.query)]
        except TypeError:
            raise fooster.web.HTTPError(400)


class CallHandler(AccountHandler):
    def do_get(self):
        try:
            call = client.calls.get(self.groups[0])

            return 200, vbx.util.call_encode(call.fetch())
        except:
            raise fooster.web.HTTPError(404)

    def do_delete(self):
        try:
            call = client.calls.get(self.groups[0])

            call.delete()

            return 204, ''
        except:
            raise fooster.web.HTTPError(404)


class MessageListHandler(ListHandler):
    def do_get(self):
        try:
            if 'from' in self.request.query:
                self.request.query['from_'] = self.request.query['from']
                del self.request.query['from']

            return 200, [vbx.util.message_encode(message) for message in client.messages.list(**self.request.query) if not message.error_code]
        except TypeError:
            raise fooster.web.HTTPError(400)


class MessageHandler(AccountHandler):
    def do_get(self):
        try:
            message = client.messages.get(self.groups[0])

            return 200, vbx.util.message_encode(message.fetch())
        except:
            raise fooster.web.HTTPError(404)

    def do_delete(self):
        try:
            message = client.message.get(self.groups[0])

            message.delete()

            return 204, ''
        except:
            raise fooster.web.HTTPError(404)


class FlowHandler(fooster.web.form.FormHandler):
    pass


class CallFlowHandler(FlowHandler):
    def do_post(self):
        self.event = vbx.events.Call(self.request.body)

        try:
            self.response.headers['Content-Type'] = 'text/xml'
            return 200, str(self.event.handle(vbx.config.calls[self.groups[0]]))
        except ValueError:
            raise fooster.web.HTTPError(400)
        except IndexError:
            raise fooster.web.HTTPError(404)


class MessageFlowHandler(FlowHandler):
    def do_post(self):
        self.event = vbx.events.Message(self.request.body)

        try:
            self.response.headers['Content-Type'] = 'text/xml'
            return 200, str(self.event.handle(vbx.config.messages[self.groups[0]]))
        except ValueError:
            raise fooster.web.HTTPError(400)
        except IndexError:
            raise fooster.web.HTTPError(404)


routes.update({'/': IndexPage, '/browser': BrowserHandler, '/msg': OutgoingHandler, '/contacts/': ContactListHandler, '/contacts/' + alias: ContactHandler, '/calls/' + query: CallListHandler, '/calls/' + alias: CallHandler, '/msgs/' + query: MessageListHandler, '/msgs/' + alias: MessageHandler, '/flow/voice/' + alias: CallFlowHandler, '/flow/msg/' + alias: MessageFlowHandler})
routes.update(fooster.web.file.new(vbx.config.resource, '/res'))
error_routes.update(fooster.web.json.new_error())


def start():
    global http

    http = fooster.web.HTTPServer(vbx.config.addr, routes, error_routes)
    http.start()


def stop():
    global http

    http.stop()
    http = None


def join():
    global http

    http.join()
