class Command():
    '''
    The command object used by Phial.

    Attributes:
        base_command(str): The base part of the command
        channel(str): The Slack channel ID the command was called from
        args(dict): Any arguments passed to the command
        user(str): The Slack User ID of the user who intiated the command
        message_ts(str): The timestamp of the message that initiated the
                         command
    '''
    def __init__(self, base_command, channel, args, user, message_ts):
        self.base_command = base_command
        self.channel = channel
        self.args = args
        self.user = user
        self.message_ts = message_ts

    def __repr__(self):
        return "<Command: {0}, {1} in {2}>".format(self.base_command,
                                                   self.args, self.channel)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class CommandMessage():
    '''
    Internal class used by phial to sotre data about the message that initiated
    the command.

    Attributes:
        text(str): The message contents
        channel(str): The Slack channel ID the message was sent from
        user(str): The user who sent the message
        timestamp(str): The messages timestamp
    '''
    def __init__(self, text, channel, user, timestamp):
        self.text = text
        self.channel = channel
        self.user = user
        self.timestamp = timestamp

    def __repr__(self):
        return "<CommandMessage: {0} in {1} at {3}>".format(self.text,
                                                            self.channel,
                                                            self.timestamp)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
