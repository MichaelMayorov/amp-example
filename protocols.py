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
