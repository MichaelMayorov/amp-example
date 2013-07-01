import sys
from twisted.python import log
from twisted.internet import reactor
import fake_master
import fake_slave

class Logger(log.Logger):

    def __init__(self, prefix):
        self._pfx = prefix

    def logPrefix(self):
        return self._pfx


if __name__ == "__main__":
    log.startLogging(sys.stderr)
    log.callWithLogger(Logger('fake_slave'), fake_slave.main)
    log.callWithLogger(Logger('fake_master'), fake_master.main)
    reactor.run()
