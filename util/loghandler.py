#!/usr/bin/python
import logging

CONSOLELOGLEVEL = logging.DEBUG
LOGPREFIX = "logs/bot"

"""
Someone fix this ;)

Didn't get 'log' available for other modules...
"""

log = logging.getLogger("log")
	
log.setLevel(logging.DEBUG)

# Error log file
elog = logging.FileHandler("%s_error.log" % LOGPREFIX)
elog.setLevel(logging.ERROR)

# Console logging
clog = logging.StreamHandler()
clog.setLevel(CONSOLELOGLEVEL)

formatter = logging.Formatter("%(asctime)s - %(module)-20s - %(message)s")

clog.setFormatter(formatter)
elog.setFormatter(formatter)

log.addHandler(elog)
log.addHandler(clog)