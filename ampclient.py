import sys
import pprint
from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList
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
def doConnection():
    def connect():
        endpoint = TCP4ClientEndpoint(reactor, "127.0.0.1", 1234)
        factory = Factory()
        factory.protocol = amp.AMP
        return endpoint.connect(factory)
    ampProto = yield connect()

    info, builderListResult = yield defer.gatherResults([
            getInfo(ampProto),
            setBuilders(ampProto)])

    log.msg('Slave info: %s' % pprint.pformat(info))
    log.msg('Slave setBuilderList result: %s' % builderListResult)

def main():
    d = doConnection()
    return d

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    d = main()
    @d.addBoth
    def stop(x):
        reactor.stop()
        return x
    d.addErrback(log.msg, 'from ampclient')
    reactor.run()
