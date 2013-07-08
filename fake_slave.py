# -*- coding: utf-8 -*-

import sys
import pprint
from twisted.internet import reactor, defer
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList, RemotePrint, RemoteStartCommand,\
    RemoteAcceptLog, RemoteAuth


MAGIC_NUMBER = 4095

class Bot(amp.AMP):
    @GetInfo.responder
    def getInfo(self):
        commands = [
            {'name': 'shell', 'version': 1},
            {'name': 'uploadFile', 'version': 1},
            {'name': 'uploadDirectory', 'version': 1},
            {'name': 'downloadFile', 'version': 1},
            {'name': 'svn', 'version': 1},
            {'name': 'bk', 'version': 1},
            {'name': 'cvs', 'version': 1},
            {'name': 'darcs', 'version': 1},
            {'name': 'git', 'version': 1},
            {'name': 'repo', 'version': 1},
            {'name': 'bzr', 'version': 1},
            {'name': 'hg', 'version': 1},
            {'name': 'p4', 'version': 1},
            {'name': 'mtn', 'version': 1},
            {'name': 'mkdir', 'version': 1},
            {'name': 'rmdir', 'version': 1},
            {'name': 'cpdir', 'version': 1},
            {'name': 'stat', 'version': 1},
        ]
        environ = [{'key': 'foo', 'value': 'bar'}, {'key': 'asd', 'value': 'qwe'}]
        system = 'SYSTEM'
        basedir= 'BASEDIR'
        version = '0.1'
        return {'commands': commands, 'environ': environ, 'system': system,
            'basedir': basedir, 'version': version,
        }

    @SetBuilderList.responder
    def setBuilderList(self, builders):
        log.msg('Setting builders')
        for builder in builders:
            log.msg("(%s, %s)" % (builder['name'], builder['dir']))
        log.msg('Done with builders')
        return {'result': 0} # assume that all builders were created successfully

    @RemotePrint.responder
    def remotePrint(self, message):
        log.msg('Message from master: "%s"' % message)
        return {'result': 0}

    @RemoteStartCommand.responder
    @defer.inlineCallbacks
    def remoteStartCommand(self, environ, command, args, builder):
        log.msg('Master asks me to execute a command: "%s" "%s' % (
                command, " ".join(args)
        ))
        log.msg('For builder: "%s" with environ: %s' % (builder, pprint.pformat(environ)))
        sometext = "Just a short line"
        sometext2 = u"Привет мир! Hello world! こんにちは、世界！"
        yield self.callRemote(RemoteAcceptLog, line=sometext)
        yield self.callRemote(RemoteAcceptLog, line=sometext2)

        defer.returnValue({'result': 0, 'builder': builder})


@defer.inlineCallbacks
def sendAuthReq(ampProto):
    user, password = 'user', 'password'
    my_features = [{'key': 'feature1', 'value': 'bar'}, {'key': 'feature2', 'value': 'baz'}]
    master_features = yield ampProto.callRemote(RemoteAuth, user=user, password=password, features=my_features)
    defer.returnValue(master_features)


@defer.inlineCallbacks
def doConnection():
    def connect():
        from twisted.internet.endpoints import TCP4ClientEndpoint
        from twisted.internet.protocol import Factory
        endpoint = TCP4ClientEndpoint(reactor, "127.0.0.1", 1235)
        factory = Factory()
        factory.protocol = Bot
        return endpoint.connect(factory)
    ampProto = yield connect()
    master_feautures = yield sendAuthReq(ampProto)


def main():
    d = doConnection()
    log.msg('fake_slave can now accept request from fake_master')
    return d

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
