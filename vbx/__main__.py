import argparse
import importlib.util
import itertools
import logging
import multiprocessing
import signal
import sys

import fooster.web

from vbx import config


def main():
    parser = argparse.ArgumentParser(description='serve up a vbx management system for Twilio')
    parser.add_argument('-a', '--address', dest='address', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', help='port to bind')
    parser.add_argument('-s', '--socketport', dest='socketport', help='websocket port to bind')
    parser.add_argument('-u', '--socketuri', dest='socketuri', help='websocket uri for connections')
    parser.add_argument('-r', '--resource', dest='resource', help='resource directory to use')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('-l', '--log', dest='log', help='log directory to use')
    parser.add_argument('flows', help='flows file to use')

    args = parser.parse_args()

    if args.address:
        config.addr = (args.address, config.addr[1])

    if args.port:
        config.addr = (config.addr[0], args.port)

    if args.socketport:
        config.wsocket = (args.address, args.socketport)

    if args.socketuri:
        config.socket = args.socketuri

    if args.resource:
        config.resource = args.resource

    if args.template:
        config.template = args.template

    if args.log:
        if args.log == 'none':
            config.log = None
            config.http_log = None
        else:
            config.log = args.log + '/vbx.log'
            config.http_log = args.log + '/http.log'

    flows_spec = importlib.util.spec_from_file_location('flows', args.flows)
    flows = importlib.util.module_from_spec(flows_spec)
    flows_spec.loader.exec_module(flows)

    config.auth = flows.auth
    config.app = flows.app
    config.number = flows.number
    config.calls = flows.calls
    config.messages = flows.messages
    config.contacts = flows.contacts


    # setup logging
    log = logging.getLogger('vbx')
    if config.log:
        log.addHandler(logging.FileHandler(config.log))
    else:
        log.addHandler(logging.StreamHandler(sys.stdout))

    if config.http_log:
        http_log_handler = logging.FileHandler(config.http_log)
        http_log_handler.setFormatter(fooster.web.HTTPLogFormatter())

        logging.getLogger('http').addHandler(http_log_handler)


    from vbx import name, version
    from vbx import http

    import vbx.flows


    log.info(name + ' ' + version + ' starting...')

    # ignore SIGINT in manager and components
    orig_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
    sync = multiprocessing.Manager()

    # start device components
    for flows in itertools.chain(config.calls.values(), config.messages.values()):
        for flow in flows:
            if isinstance(flow, vbx.flows.Device):
                flow.start()

    # re-enable sigint
    signal.signal(signal.SIGINT, orig_sigint)

    # start everything
    http.start(sync=sync)


    # cleanup function
    def exit(signum, frame):
        http.stop()


    # use the function for both SIGINT and SIGTERM
    for sig in signal.SIGINT, signal.SIGTERM:
        signal.signal(sig, exit)

    # join against the HTTP server
    http.join()

    # stop device components
    for flows in itertools.chain(config.calls.values(), config.messages.values()):
        for flow in flows:
            if isinstance(flow, vbx.flows.Device):
                flow.stop()


if __name__ == '__main__':
    main()
