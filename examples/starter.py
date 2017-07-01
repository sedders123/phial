from phial import Phial, command, Message

slackbot = Phial('token-goes-here')


@slackbot.command('ping')
def ping():
    return Message(text="Pong", channel=command.channel)


@slackbot.command('hello <name>')
def hello(name):
    return Message(text="Hi {0}".format(name), channel=command.channel)


slackbot.run()
