from phial import Phial, command, Response, Attachment, g, help_command
import os

slackbot = Phial('token-goes-here')

slackbot.add_command("help", help_command)


@slackbot.command('ping')
def ping():
    '''Simple command which replies with a message'''
    return "Pong"


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


@slackbot.command('start')
def start():
    '''A command which uses an application global variable'''
    g['variable'] = True
    return "Started"


@slackbot.command('stop')
def stop():
    '''A command which uses an application global variable'''
    g['variable'] = False
    return "Stopped"


@slackbot.command('check')
def check():
    '''A command that reads an application global variable'''
    if g['variable']:
        return "Process Started"
    else:
        return "Process Stopped"


@slackbot.command('caseSensitive', case_sensitive=True)
def case_sensitive():
    '''Simple command which replies with a message'''
    return "You typed caseSensitive"


if __name__ == '__main__':
    slackbot.run()
