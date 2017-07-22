from phial import Phial, command, Response, Attachment
import os

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
    '''Simple command that reacts to the original message'''
    return Response(reaction="x",
                    channel=command.channel,
                    original_ts=command.message_ts)


@slackbot.command('upload')
def upload():
    '''Simple command that uploads a set file'''
    project_dir = os.path.dirname(__file__)
    file_path = os.path.join(project_dir, 'phial.png')
    return Attachment(channel=command.channel,
                      filename='example.txt',
                      content=open(file_path, 'rb'))


@slackbot.command('reply')
def reply():
    '''Simple command that replies to the original message in a thread'''
    return Response(text="this is a thread",
                    channel=command.channel,
                    original_ts=command.message_ts)


slackbot.run()
