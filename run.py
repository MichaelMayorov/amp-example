import sys
from twisted.python import log
from twisted.internet import reactor
import ampclient
import ampserver

class Logger(log.Logger):

    def __init__(self, prefix):
        self._pfx = prefix

    def logPrefix(self):
        return self._pfx


if __name__ == "__main__":
    log.startLogging(sys.stderr)
    log.callWithLogger(Logger('ampserver'), ampserver.main)
    log.callWithLogger(Logger('ampclient'), ampclient.main)
    reactor.run()
