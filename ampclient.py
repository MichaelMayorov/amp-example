import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from twisted.python import log
from ampserver import GetInfo


def doConnection():
    creator = ClientCreator(reactor, amp.AMP)
    getInfo = creator.connectTCP('127.0.0.1', 1234)
    def connected(ampProto):
        return ampProto.callRemote(GetInfo)
    getInfo.addCallback(connected)
    def returnedInfo(result):
        return result
    getInfo.addCallback(returnedInfo)

    def done(result):
        log.msg('Slave info: %s' % pprint.pformat(result))
        reactor.stop()
    defer.DeferredList([getInfo,]).addCallback(done)

def main():
    doConnection()

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
