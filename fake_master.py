# -*- coding: utf-8 -*-

import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList, RemotePrint, RemoteStartCommand, RemoteAcceptLog,\
    RemoteAuth
from protocols import DebugAMP
from twisted.internet.endpoints import TCP4ClientEndpoint


@defer.inlineCallbacks
def getInfo(ampProto):
    info = yield ampProto.callRemote(GetInfo)
    defer.returnValue(info)

@defer.inlineCallbacks
def setBuilders(ampProto):
    builders = [
        {'name': 'python2.7', 'dir': '/build/py2.7'},
        {'name': 'python3', 'dir': '/build/py3'}
        ]
    builderListResult = yield ampProto.callRemote(SetBuilderList, builders=builders) 
    defer.returnValue(builderListResult)

@defer.inlineCallbacks
def remotePrint(ampProto):
    message = "Just test message from master"
    res = yield ampProto.callRemote(RemotePrint, message=message)
    defer.returnValue(res)

@defer.inlineCallbacks
def remoteStartCommand(ampProto):
    environ = [{'key': 'foo', 'value': 'bar'}, {'key': 'baz', 'value': 'quux'}]
    cmd = '/bin/ls'
    args = ['-la', '/']
    builder = 'py2.7'
    res = yield ampProto.callRemote(RemoteStartCommand, environ=environ, command=cmd,
        args=args, builder=builder
    )
    defer.returnValue(res)

@defer.inlineCallbacks
def requestSlave(ampProto):
    info, builderListResult = yield defer.gatherResults([
            getInfo(self),
            setBuilders(self)
    ])
    remPrintRes = yield remotePrint(self)
    remStartCmd = yield remoteStartCommand(self)

    log.msg('Slave info: %s' % pprint.pformat(info))
    log.msg('Slave setBuilderList result: %s' % builderListResult)
    log.msg('Remote print result: %s' % remPrintRes)
    log.msg('Remote execution\'s result: %s' % pprint.pformat(remStartCmd))


class Master(DebugAMP):
    @RemoteAuth.responder
    @defer.inlineCallbacks
    def authSlave(self, user, password, features):
        if user == 'user' and password != 'password':
            self.disconnect()
        self.slave_authenticated = True
        yield requestSlave(self)
        log.msg('Slave feauture negotiation vector: %s' % pprint.pformat(feautures))
        features = [{'key': 'feature1', 'value': 'bar1'}, {'key': 'feature2', 'value': 'baz1'}]
        defer.returnValue({'features': features})

#     @defer.inlineCallbacks
#     def connectionMade(self):
#         yield amp.AMP.connectionMade(self)
#         info, builderListResult = yield defer.gatherResults([
#                 getInfo(self),
#                 setBuilders(self)
#         ])
#         remPrintRes = yield remotePrint(self)
#         remStartCmd = yield remoteStartCommand(self)
#
#         log.msg('Slave info: %s' % pprint.pformat(info))
#         log.msg('Slave setBuilderList result: %s' % builderListResult)
#         log.msg('Remote print result: %s' % remPrintRes)
#         log.msg('Remote execution\'s result: %s' % pprint.pformat(remStartCmd))

    @RemoteAcceptLog.responder
    def remoteAcceptLog(self, line):
        if hasattr(self, 'slave_authenticated') is False:
            self.disconnect()
        log.msg('Slave send me a log line: %s' % line.encode('utf-8'))
        return {}


def main():
    pf = Factory()
    pf.protocol = Master
    reactor.listenTCP(1235, pf) 
    log.msg('fake_master can now accept request from fake_slave')

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
