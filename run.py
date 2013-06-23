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
    def runClientAndStop():
        d = ampclient.main()
        @d.addBoth
        def stop(x):
            reactor.stop()
            return x
        d.addErrback(log.msg, 'from ampclient')
    log.callWithLogger(Logger('ampclient'), runClientAndStop)
    reactor.run()
