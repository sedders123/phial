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


class Message():
    '''
    Used by phial to store data about the message that initiated
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
        return "<Message: {0} in {1} at {3}>".format(self.text,
                                                     self.channel,
                                                     self.timestamp)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Response():
    '''
    When returned in a command function will send a message, or reaction to
    slack depending on contents.

    Attributes:
        channel(str): The Slack channel ID the response will be sent to
        text(str): The response contents
        original_ts(str): The timestamp of the original message. If populated
                          will put the text response in a thread
        reation(str): A valid slack emoji name. NOTE: will only work when
                      original_ts is populated

    Examples:
        The following would send a message to a slack channel when executed ::

            @slackbot.command('ping')
            def ping():
                return Response(text="Pong", channel='channel_id')

        The following would send a reply to a message in a thread ::

            @slackbot.command('hello')
            def hello():
                return Response(text="hi",
                                channel='channel_id',
                                original_ts='original_ts')

        The following would send a reaction to a message ::

            @slackbot.command('react')
            def react():
                return Response(reaction="x",
                                channel='channel_id',
                                original_ts='original_ts')

    '''
    def __init__(self, channel, text=None, original_ts=None, reaction=None):
        self.channel = channel
        self.text = text
        self.original_ts = original_ts
        self.reaction = reaction

    def __repr__(self):
        return "<Response to {1}>".format(self.text, self.channel)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
