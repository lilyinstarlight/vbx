import twilio.rest

import web
import web.file
import web.json
import web.page

import vbx.config
import vbx.events
import vbx.devices.browser


alias = '([a-zA-Z0-9._-]+)'

http = None

client = twilio.rest.Client(username=vbx.config.auth[0], password=vbx.config.auth[1])

routes = {}
error_routes = {}


class IndexPage(web.page.PageHandler):
    directory = config.template
    page = 'index.html'


class AccountHandler(web.json.JSONHandler):
    def call_encode(self, call):
	return {'annotation': call.annotation, 'date': call.date_created, 'direction': call.direction, 'duration': call.duration, 'from': call.from_formatted, 'to': call.to}

    def message_encode(self, call):
	return {'body': instance.body, 'date': instance.date_created, 'direction': instance.direction, 'from': instance.from_, 'to': instance.to}


class BrowserHandler(AccountHandler):
    def do_get(self):
	return {'username': vbx.config.auth[0], 'password': vbx.config.auth[1]}

    def do_post(self):
	vbx.devices.browser.online = self.request.body['online']


class ContactListHandler(AccountHandler):
    def do_get(self):
	return config.contacts


class ContactHandler(AccountHandler):
    def do_get(self):
	try:
	    return config.contacts[self.groups[0]]
	except:
	    raise web.HTTPError(404)


class CallListHandler(AccountHandler):
    def do_get(self):
	return [self.call_encode(call) for call in client.calls.stream()]


class CallHandler(AccountHandler):
    def do_get(self):
	try:
	    call = client.calls.get(self.groups[0])

	    return self.call_encode(call.fetch())
	except:
	    raise web.HTTPError(404)

    def do_delete(self):
	try:
	    call = client.calls.get(self.groups[0])

	    call.delete()

	    return 204, ''
	except:
	    raise web.HTTPError(404)


class MessageListHandler(AccountHandler):
    def do_get(self):
	return [self.message_encode(message) for message in client.messages.stream()]


class MessageHandler(AccountHandler):
    def do_get(self):
	try:
	    message = client.messages.get(self.groups[0])

	    return self.message_encode(message.fetch())
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
	self.event = vbx.events.Call(self.body)

	try:
	    return 200, str(self.event.handle(vbx.config.calls[self.groups[0]]))
	except ValueError:
	    raise web.HTTPError(400)
	except IndexError:
	    raise web.HTTPError(404)


class MessageFlowHandler(FlowHandler):
    def do_post(self):
	self.event = vbx.events.Message(self.body)

	try:
	    return 200, str(self.event.handle(vbx.config.messages[self.groups[0]]))
	except ValueError:
	    raise web.HTTPError(400)
	except IndexError:
	    raise web.HTTPError(404)


routes.update({'/': IndexPage, '/browser': BrowserHandler, '/contacts/': ContactListHandler, '/contacts/' + alias: ContactHandler, '/calls/': CallListHandler, '/calls/' + alias: CallHandler, '/msgs/': MessageListHandler, '/msgs/' + alias: MessageHandler, '/flow/voice/' + alias: CallFlowHandler, '/flow/msg/' + alias: MessageFlowHandler})
error_routes.update(web.json.new_error())


def start():
    global http

    http = web.HTTPServer(config.addr, routes, error_routes, log=log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
