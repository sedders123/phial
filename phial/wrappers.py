class Command():
    '''
    The command object used by Phial.

    Attributes:
        base_command(str): The base part of the command
        channel(str): The Slack channel ID the command was called from
        args(dict): Any arguments passed to the command
    '''
    def __init__(self, base_command, channel, args):
        self.base_command = base_command
        self.channel = channel
        self.args = args

    def __repr__(self):
        return "<Command: {0}, {1} in {2}>".format(self.base_command,
                                                   self.args, self.channel)


class Message():
    '''
    The message class object used by Phial.

    Attributes:
        text(str): The message contents
        channel(str): The Slack channel ID the message will be sent to
    '''
    def __init__(self, text, channel):
        self.text = text
        self.channel = channel

    def __repr__(self):
        return "<Message: {0} in {1}>".format(self.text, self.channel)
