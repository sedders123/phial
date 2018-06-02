from typing import Dict, Pattern, IO, Optional


class Message():
    '''
    Used by phial to store data about the message that initiated
    the command.

    Attributes:
        text(str): The message contents
        channel(str): The Slack channel ID the message was sent from
        user(str): The user who sent the message
        timestamp(str): The messages timestamp
        bot_id(str, optional): If the message was sent by a bot
                               the ID of that bot.
                               Defaults to None.
    '''
    def __init__(self,
                 text: str,
                 channel: str,
                 user: str,
                 timestamp: str,
                 bot_id: Optional[str] = None) -> None:
        self.text = text
        self.channel = channel
        self.user = user
        self.timestamp = timestamp
        self.bot_id = bot_id

    def __repr__(self) -> str:
        return "<Message: {0} in {1} at {2}>".format(self.text,
                                                     self.channel,
                                                     self.timestamp)

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__


class Command():
    '''
    The command object used by Phial.

    Attributes:
        command_pattern(str): The regex used for matching the command
        channel(str): The Slack channel ID the command was called from
        args(dict): Any arguments passed to the command
        user(str): The Slack User ID of the user who intiated the command
        message_text(`Message`): The message that initiated the command
    '''
    def __init__(self,
                 command_pattern: Pattern[str],
                 channel: str,
                 args: Dict,
                 user: str,
                 message: Message) -> None:
        self.command_pattern = command_pattern
        self.channel = channel
        self.args = args
        self.user = user
        self.message = message
        self.message_ts = message.timestamp

    def __repr__(self) -> str:
        return "<Command: {0}, {1} in {2}>".format(self.message,
                                                   self.args, self.channel)

    def __eq__(self, other: object) -> bool:
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
    def __init__(self,
                 channel: str,
                 text: Optional[str] = None,
                 original_ts: Optional[str] = None,
                 reaction: Optional[str] = None) -> None:
        self.channel = channel
        self.text = text
        self.original_ts = original_ts
        self.reaction = reaction

    def __repr__(self) -> str:
        return "<Response: {0}>".format(self.text)

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__


class Attachment():
    '''
    When returned in a command function will send an attachment to Slack

    Attributes:
        channel(str): The Slack channel ID the file will be sent to
        filename(str): The filename of the file
        content(`io.BufferedReader`): The file to send to Slack. Open file
                                      using open('<file>', 'rb')

    '''
    def __init__(self,
                 channel: str,
                 filename: Optional[str] = None,
                 content: Optional[IO[bytes]] = None) -> None:
        self.channel = channel
        self.filename = filename
        self.content = content

    def __repr__(self) -> str:
        return "<Attachment in {0} >".format(self.channel)
