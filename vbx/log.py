import log

import vbx.config


vbxlog = log.Log(vbx.config.log)
httplog = log.HTTPLog(vbx.config.log, vbx.config.httplog)
