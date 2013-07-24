# -*- coding: utf-8 -*-

import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.python import log
from protocols import DebugAMP
from twisted.internet.endpoints import TCP4ClientEndpoint
from protocols import GetInfo, SetBuilderList, RemotePrint, RemoteStartCommand, RemoteAcceptLog,\
RemoteAuth, RemoteInterrupt, RemoteSlaveShutdown, ShellBbCommand, RemoteUpdateSendRC,\
MkdirBbCommand


@defer.inlineCallbacks
def getInfo(ampProto):
    info = yield ampProto.callRemote(GetInfo)
    defer.returnValue(info)

@defer.inlineCallbacks
def setBuilders(ampProto):
    builders = [
        {'name': 'python2.7', 'dir': 'py2.7'},
        {'name': 'python3', 'dir': 'py3'}
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
def remoteRunShellCommand(ampProto):
    error = yield ampProto.callRemote(ShellBbCommand,
        builder='python2.7', command=['/bin/ls', '-l', '/'], workdir='./',
        env=[{'key': 'foo', 'value': 'bar'}], initial_stdin='Initial stdin',
        want_stdout='want_stdout', want_stderr='want_stderr', usePTY=True,
        not_really=True, timeout=60.0, maxTime=300.0, 
        logfiles=[{'key': 'bb', 'value': 'slave.log'}], follow='follow',
        logEnviron=True
    )
    defer.returnValue(error)

@defer.inlineCallbacks
def remoteRunMkdirCommand(ampProto):
    error = yield ampProto.callRemote(MkdirBbCommand,
        builder='python2.7', dir="remote-mkdir",
    )
    defer.returnValue(error)

@defer.inlineCallbacks
def Hello(ampProto):
    info, builderListResult = yield defer.gatherResults([
            getInfo(ampProto),
            setBuilders(ampProto)
    ])
    remPrintRes = yield remotePrint(ampProto)
    # remStartCmd = yield remoteStartCommand(ampProto) # not function
    shellCmdErr = yield remoteRunShellCommand(ampProto)
    mkdirErr = yield remoteRunMkdirCommand(ampProto)

    log.msg('Slave info: %s' % pprint.pformat(info))
    log.msg('Slave setBuilderList result: %s' % builderListResult)
    log.msg('Remote print result: %s' % remPrintRes)
    # log.msg('Remote execution\'s result: %s' % pprint.pformat(remStartCmd))
    if shellCmdErr['error'] != '':
        log.msg('Error while trying to execute shell command on slave: "%s"' % shellCmdErr)
    if mkdirErr['error'] != '':
        log.msg('Error while trying to execute mkdir command on slave: "%s"' % mkdirErr)

    yield ampProto.callRemote(RemoteInterrupt, command='ls')
    yield ampProto.callRemote(RemoteSlaveShutdown)


class Master(DebugAMP):
    @RemoteAuth.responder
    def authSlave(self, user, password, features):
        if user == 'user' and password != 'password':
            log.msg('Invalid credentials!')
            error = [{'key': 'Error', 'value': 'Login or password incorrect'}]
            return {'features': error}
        log.msg('Slave authenticated!')
        self.slave_authenticated = True
        Hello(self)
        log.msg('Slave feature negotiation vector: %s' % pprint.pformat(features))
        features = [{'key': 'feature1', 'value': 'bar1'}, {'key': 'feature2', 'value': 'baz1'}]
        return {'features': features}

    @RemoteAcceptLog.responder
    def remoteAcceptLog(self, builder, logName, stream, data):
        if hasattr(self, 'slave_authenticated') is False:
            log.msg('Log streaming rejected, because slavery didn\'t pass authentication')
            return {}
        log.msg('Slave builder: "%s", stream: "%s", log name: "%s", data:\n%  s'\
            % (builder, stream, logName, data)
        )
        return {}

    @RemoteUpdateSendRC.responder
    def remoteUpdateRC(self, builder, rc):
        log.msg('Slave builder: "%s" done command with rc: %d' % (builder, rc))
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
