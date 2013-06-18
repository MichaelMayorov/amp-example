import sys
from twisted.internet import reactor
from twisted.protocols import amp
from twisted.python import log
from protocols import GetInfo, SetBuilderList


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
        for builder_name, build_dir in builders:
            log.msg("(%s, %s)" % (builder_name, build_dir))
        log.msg('Done with builders')
        return {'result': 0} # assume that all builder were created successfully


def main():
    from twisted.internet.protocol import Factory
    pf = Factory()
    pf.protocol = Bot
    reactor.listenTCP(1234, pf)
    log.msg('server started')

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    main()
    reactor.run()
