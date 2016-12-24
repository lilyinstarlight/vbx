import web
import web.file
import web.json
import web.page

import vbx.config
import vbx.events


alias = '([a-zA-Z0-9._-]+)'

http = None

routes = {}
error_routes = {}


class IndexPage(web.page.PageHandler):
    directory = config.template
    page = 'index.html'


class AccountHandler(web.json.JSONHandler):
	pass


class CallHandler(AccountHandler):
	pass


class MessageHandler(AccountHandler):
	pass


class FlowHandler(web.form.FormHandler):
	pass


class CallFlowHandler(FlowHandler):
    def do_post(self):
	self.event = new vbx.events.Call(self.body)

	try:
	    return 200, str(self.event.handle(vbx.config.calls[int(self.groups[0])]))
	except ValueError:
	    raise web.HTTPError(400)
	except IndexError:
	    raise web.HTTPError(404)


class MessageFlowHandler(FlowHandler):
    def do_post(self):
	self.event = new vbx.events.Message(self.body)

	try:
	    return 200, str(self.event.handle(vbx.config.messages[int(self.groups[0])]))
	except ValueError:
	    raise web.HTTPError(400)
	except IndexError:
	    raise web.HTTPError(404)


routes.update({'/': IndexPage, '/calls/' + alias: CallHandler, '/msgs/' + alias: MessageHandler, '/flow/voice/' + alias: CallFlowHandler, '/flow/msg/' + alias: MessageFlowHandler})
error_routes.update(web.json.new_error())


def start():
    global http

    http = web.HTTPServer(config.addr, routes, error_routes, log=log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
