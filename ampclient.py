import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList


def doConnection():
    creator = ClientCreator(reactor, amp.AMP)
    getInfo = creator.connectTCP('127.0.0.1', 1234)
    def connected(ampProto):
        return ampProto.callRemote(GetInfo)
    getInfo.addCallback(connected)

    setBuilderList = creator.connectTCP('127.0.0.1', 1234)
    def connected(ampProto):
        builders = [
            {'name': 'python2.7', 'dir': '/build/py2.7'},
            {'name': 'python3', 'dir': '/build/py3'}
            ]

        return ampProto.callRemote(SetBuilderList, builders=builders)
    setBuilderList.addCallback(connected)


    def done(result):
        log.msg('Slave info: %s' % pprint.pformat(result))
        reactor.stop()
    getInfo.addCallback(done)

def main():
    doConnection()

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
