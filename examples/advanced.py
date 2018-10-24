from phial import Phial, command, Response, Schedule, MessageAttachment, MessageAttachmentField
from multiprocessing import Process
from time import sleep
import logging

slackbot = Phial('token-goes-here')
SCHEDULED_CHANNEL = "channel-id"


@slackbot.command('cent(er|re)')
def regex_in_command():
    '''Command that uses regex to define structure'''
    base_command = command.message.text.split(" ")[0]
    if slackbot.config['prefix']:
        base_command = base_command[1:]
    if base_command == "center":
        return Response(text="Yeehaw! You're a Yank", channel=command.channel)
    elif base_command == "centre":
        return Response(text="I say! You appear to be a Brit",
                        channel=command.channel)
    else:
        return Response(text="Well this is awkward... this isn't meant to \
                        happen", channel=command.channel)


@slackbot.command('colo[u]?r <arg>')
def regex_in_command_with_arg(arg):
    '''Command that uses regex to define structure with an arg'''
    base_command = command.message.text.split(" ")[0]
    return Response(text="My favourite {0} is {1}"
                    .format(base_command, arg),
                    channel=command.channel)


def fire_and_forget(channel):
    '''
        Example function used by background_processing().Sends a message
        outside of a command context.
    '''
    sleep(3)
    slackbot.send_message(Response(text="Background Process Message",
                          channel=channel))


@slackbot.command('background')
def background_processing():
    '''Command that starts a process to allow a non blocking sleep'''
    p = Process(target=fire_and_forget, args=(command.channel,), daemon=True)
    p.start()
    return "Foreground message"


@slackbot.middleware()
def log_message(message):
    logging.info(message)
    return message


@slackbot.scheduled(Schedule().seconds(30))
def shceduled_function():
    slackbot.send_message(Response(text="Hey! Hey Listen!",
                                   channel=SCHEDULED_CHANNEL))

@slackbot.command('message-with-attachment')
def get_message_with_attachment():
    attachments = [
        MessageAttachment(
            title="Here's a message, it has 2 attachment fields",
            title_link="https://api.slack.com/docs/message-attachments"
            text="This message has some text!",
            fields=[
                MessageAttachmentField(title="Here's the first attachment field", value="And here's it's body", short=True),
                MessageAttachmentField(title="...And here's the second", value="And here's it's body", short=True)
            ]
        )
    ]
    return attachments

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    slackbot.run()
