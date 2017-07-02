from phial import Phial, command, Response

slackbot = Phial('token-goes-here')


@slackbot.command('ping')
def ping():
    '''Simple command which replies with a message'''
    return Response(text="Pong", channel=command.channel)


@slackbot.command('hello <name>')
def hello(name):
    '''Simple command with argument which replies to a message'''
    return Response(text="Hi {0}".format(name), channel=command.channel)


@slackbot.command('react')
def react():
    '''Simple command that reacts to the orginal message'''
    return Response(reaction="x",
                    channel=command.channel,
                    original_ts=command.message_ts)


@slackbot.command('reply')
def reply():
    '''Simple command that replies to the original message in a thread'''
    return Response(text="this is a thread",
                    channel=command.channel,
                    original_ts=command.message_ts)


slackbot.run()
