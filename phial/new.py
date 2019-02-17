from slackclient import SlackClient  # type: ignore
from typing import Callable, List, Optional, Pattern, Dict, Union, IO
import re

PhialResponse = Union[None, str, 'Response', 'Attachment']


def parse_slack_output(slack_rtm_output: List[Dict]) -> Optional['Message']:
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if(output and 'text' in output):
                    bot_id = None
                    if 'bot_id' in output:
                        bot_id = output['bot_id']
                    return Message(output['text'],
                                   output['channel'],
                                   output['user'],
                                   output['ts'],
                                   output['team'],
                                   bot_id)
        return None


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
        attachments(Union[List[MessageAttachment],
                          List[Dict[str, Dict[str, str]]]]):
                          A list of MessageAttachment objects to be attached
                          to the message
        ephemeral(bool): Whether to send the message as an ephemeral message
        user(str): The user id to display the ephemeral message to

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
                 reaction: Optional[str] = None,
                 ephemeral: bool = False,
                 user: Optional[str] = None) -> None:
        # TODO: Readd message attachments
        self.channel = channel
        self.text = text
        self.original_ts = original_ts
        self.reaction = reaction
        self.ephemeral = ephemeral
        self.user = user

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


class Message():
    """Slack message"""
    def __init__(self,
                 text: str,
                 channel: str,
                 user: str,
                 timestamp: str,
                 team: str,
                 bot_id: Optional[str] = None) -> None:
        self.text = text
        self.channel = channel
        self.user = user
        self.timestamp = timestamp
        self.team = team
        self.bot_id = bot_id

    def __repr__(self) -> str:
        return "<Message: {0} in {1}:{2} at {3}>".format(self.text,
                                                         self.channel,
                                                         self.team,
                                                         self.timestamp)

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__


class Command:
    """A command that a user can execute"""
    def __init__(self, pattern: str, func: Callable[..., PhialResponse]):
        self.pattern = self._build_pattern_regex(pattern)
        self.func = func

    def _build_pattern_regex(self,
                             pattern: str,
                             case_sensitive: bool = False) -> Pattern[str]:
        '''Creates the command pattern regexs'''
        command = re.sub(r'(<\w+>)', r'(\"?\1\"?)', pattern)
        command_regex = re.sub(r'(<\w+>)', r'(?P\1[^"]*)', command)
        return re.compile("^{}$".format(command_regex),
                          0 if case_sensitive else re.IGNORECASE)

    def pattern_matches(self,
                        message: Message) -> Optional[Dict]:
        match = self.pattern.match(message.text)
        if match:
            return match.groupdict()
        return None


class Phial:

    #: Default configuration
    default_config = {
        'prefix': "!",
        'registerHelpCommand': True,
        'baseHelpText': "All available commands:",
        'autoReconnect': True
    }

    def __init__(self, token: str, config: Dict = default_config) -> None:
        self.slack_client = SlackClient(token)
        self.commands: List[Command] = []
        self.config: Dict = config

    def add_command(self, pattern: str, func: Callable) -> None:
        pattern = "{0}{1}".format(self.config["prefix"], pattern)
        command = Command(pattern, func)
        self.commands.append(command)

    def send_message(self, message: Response) -> None:
        '''
        Takes a response object and then sends the message to Slack

        Args:
            message(Response): message object to be sent to Slack

        '''

        api_method = ('chat.postEphemeral' if message.ephemeral
                      else 'chat.postMessage')

        if message.original_ts:
            self.slack_client.api_call(api_method,
                                       channel=message.channel,
                                       text=message.text,
                                       thread_ts=message.original_ts,
                                       user=message.user,
                                       as_user=True)
        else:
            self.slack_client.api_call(api_method,
                                       channel=message.channel,
                                       text=message.text,
                                       user=message.user,
                                       as_user=True)

    def send_reaction(self, response: Response) -> None:
        '''
        Takes a `Response` object and then sends the reaction to Slack

        Args:
            response(Response): response object containing the reaction to be
                                sent to Slack

        '''
        self.slack_client.api_call("reactions.add",
                                   channel=response.channel,
                                   timestamp=response.original_ts,
                                   name=response.reaction,
                                   as_user=True)

    def upload_attachment(self, attachment: Attachment) -> None:
        '''
        Takes an `Attachment` object and then uploads the contents to Slack

        Args:
            attachment(Attachment): attachment object containing the file to be
                                    uploaded to Slack

        '''
        self.slack_client.api_call('files.upload',
                                   channels=attachment.channel,
                                   filename=attachment.filename,
                                   file=attachment.content)

    def _send_response(self,
                       response: PhialResponse,
                       original_channel: str) -> None:
        if response is None:
            return  # Do nothing if command function returns nothing

        if isinstance(response, str):
            self.send_message(Response(text=response,
                                       channel=original_channel))

        elif not isinstance(response, Response) and not \
                isinstance(response, Attachment):
            raise ValueError('Only Response or Attachment objects can be ' +
                             'returned from command functions')

        if isinstance(response, Response):
            if response.original_ts and response.reaction and response.text:
                raise ValueError('Response objects with an original timestamp '
                                 + 'can only have one of the attributes: '
                                 + 'Reaction, Text')
            if response.original_ts and response.reaction:
                self.send_reaction(response)
            elif response.text:
                self.send_message(response)

        if isinstance(response, Attachment):
            if not response.content:
                raise ValueError('The content field of Attachment objects ' +
                                 'must be set')
            self.upload_attachment(response)

    def _handle_message(self, message: Optional[Message]) -> None:
        if not message:
            return
        # TODO: Pass through middleware

        for command in self.commands:
            kwargs = command.pattern_matches(message)
            if kwargs is not None:
                response = command.func(**kwargs)
                self._send_response(response, message.channel)
                return

    def run(self) -> None:
        auto_reconnect = self.config['autoReconnect']
        if not self.slack_client.rtm_connect(auto_reconnect=auto_reconnect,
                                             with_team_state=False):
            raise ValueError("Connection failed. Invalid Token or bot ID")
        while True:
            try:
                message = parse_slack_output(self.slack_client.rtm_read())
                self._handle_message(message)
            except Exception as e:
                print("Error {0}".format(e))


def command_one() -> str:
    return ":tada:"


def command_two(test: str) -> None:
    print("Here {0}".format(test))


test = Phial('token')
test.add_command("test", command_one)
test.add_command("test2 <test>", command_two)
test.run()
