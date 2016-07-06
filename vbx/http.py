from lib import web, file, json, page


alias = '([a-zA-Z0-9._-]+)'

http = None

routes = {}
error_routes = {}


class IndexPage(page.PageHandler):
    directory = os.path.dirname(__file__) + '/html'
    page = 'index.html'


class AccountHandler(json.JSONHandler):
	pass


class CallHandler(AccountHandler):
	pass


class MessageHandler(AccountHandler):
	pass


class FlowHandler(AccountHandler):
	pass


class CallFlowHandler(FlowHandler):
	pass


class MessageFlowHandler(FlowHandler):
	pass


routes.update({'/': IndexPage, '/calls/' + alias: CallHandler, '/msgs/' + alias: MessageHandler, '/flow/call/' + alias + alias: CallFlowHandler, '/flow/msg/' + alias: MessageFlowHandler})
error_routes.update(json.new_error())


def start():
    global http

    http = web.HTTPServer(config.addr, routes, error_routes, log=log.httplog)
    http.start()


def stop():
    global http

    http.stop()
    http = None
