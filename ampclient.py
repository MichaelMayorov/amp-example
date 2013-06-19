import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList


def doConnection():
    creator = ClientCreator(reactor, amp.AMP)
    conn = creator.connectTCP('127.0.0.1', 1234)
    def getInfoConnected(ampProto):
        return ampProto.callRemote(GetInfo)
    conn.addCallback(getInfoConnected)

    def setBuilderListConnected(ampProto):
        builders = [
            {'name': 'python2.7', 'dir': '/build/py2.7'},
            {'name': 'python3', 'dir': '/build/py3'}
            ]
        return ampProto.callRemote(SetBuilderList, builders=builders)
    conn.addCallback(setBuilderListConnected)


    def getInfoDone(result):
        log.msg('Slave info: %s' % pprint.pformat(result))
    conn.addCallback(getInfoDone)
    def setBuilderListDone(result):
        log.msg('Slave setBuilderList result: %d' % result)
    conn.addCallback(setBuilderListDone)
    reactor.stop() # kills connection even if one of this function uses it


def main():
    doConnection()

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
