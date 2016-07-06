import os
import sys
import time
import traceback

from vbx import config


storelog = None
httplog = None


class Log(object):
    def __init__(self, log):
        if log:
            os.makedirs(os.path.dirname(log), exist_ok=True)
            self.log = open(log, 'a', 1)
        else:
            self.log = sys.stdout

    def timestamp(self):
        return time.strftime('[%d/%b/%Y:%H:%M:%S %z]')

    def write(self, string):
        if self.log:
            self.log.write(string)

    def message(self, message):
        self.write(self.timestamp() + ' ' + message + '\n')

    def head(self, header):
        self.message(header)
        self.message('=' * len(header))

    def info(self, message):
        self.message('INFO: ' + message)

    def warning(self, message):
        self.message('WARNING: ' + message)

    def error(self, message):
        self.message('ERROR: ' + message)

    def exception(self, message='Caught Exception'):
        self.error(message + ':\n\t' + traceback.format_exc().replace('\n', '\n\t'))


class HTTPLog(Log):
    def __init__(self, log, access_log):
        Log.__init__(self, log)

        if access_log:
            os.makedirs(os.path.dirname(access_log), exist_ok=True)
            self.access_log = open(access_log, 'a', 1)
        else:
            self.access_log = sys.stdout

    def access_write(self, string):
        if self.access_log:
            self.access_log.write(string)

    def request(self, host, request, code='-', size='-', rfc931='-', authuser='-'):
        self.access_write(host + ' ' + rfc931 + ' ' + authuser + ' ' + self.timestamp() + ' "' + request + '" ' + code + ' ' + size + '\n')


storelog = Log(config.log)
httplog = HTTPLog(config.log, config.httplog)
