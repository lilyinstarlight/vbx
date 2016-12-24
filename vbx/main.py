import argparse
import importlib.util
import signal

from vbx import config


parser = argparse.ArgumentParser(description='serve up a vbx management system for Twilio')
parser.add_argument('-a', '--address', dest='address', help='address to bind')
parser.add_argument('-p', '--port', type=int, dest='port', help='port to bind')
parser.add_argument('-t', '--template', dest='template', help='template directory to use')
parser.add_argument('-l', '--log', dest='log', help='log directory to use')
parser.add_argument('flows', help='flows file to use')

args = parser.parse_args()

if args.address:
    config.addr = (args.address, config.addr[1])

if args.port:
    config.addr = (config.addr[0], args.port)

if args.template:
    config.template = args.template

if args.log:
    if args.log == 'none':
        config.log = None
        config.httplog = None
    else:
        config.log = args.log + '/vbx.log'
        config.httplog = args.log + '/http.log'

flows_spec = importlib.util.spec_from_file_location('flows', args.flows)
flows = importlib.util.module_from_spec(flows_spec)
flows_spec.loader.exec_module(flows)

config.auth = flows.auth
config.calls = flows.calls
config.messages = flows.messages


from vbx import name, version
from vbx import log, http


log.vbxlog.info(name + ' ' + version + ' starting...')

# start everything
http.start()


# cleanup function
def exit():
    http.stop()


# use the function for both SIGINT and SIGTERM
for sig in signal.SIGINT, signal.SIGTERM:
    signal.signal(sig, exit)
