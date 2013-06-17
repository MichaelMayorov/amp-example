from twisted.protocols import amp

class GetInfo(amp.Command):
    arguments = []
    response = [
        ('commands', amp.AmpList([
            ('name', amp.String()),
            ('version', amp.Integer()),
            ])
        ),
        ('environ', amp.AmpList([
            ('key', amp.String()),
            ('value', amp.String()),
            ])
        ),
        ('system', amp.String()),
        ('basedir', amp.String()),
        ('version', amp.String()),
    ]


class Bot(amp.AMP):
    def get_info(self):
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
    GetInfo.responder(get_info)


def main():
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory
    pf = Factory()
    pf.protocol = Bot
    reactor.listenTCP(1234, pf)
    print 'started'
    reactor.run()

if __name__ == '__main__':
    main()
