from slackclient import SlackClient  # type: ignore
from typing import Callable, List, Optional, Pattern, Dict, Union, IO
import re
from phial.scheduler import Scheduler, Schedule, ScheduledJob

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
    def __init__(self,
                 pattern: str,
                 func: Callable[..., PhialResponse],
                 case_sensitive: bool = False):
        self.pattern = self._build_pattern_regex(pattern, case_sensitive)
        self.alias_patterns = self._get_alias_patterns(func)
        self.func = func
        self.case_sensitive = case_sensitive

    def _get_alias_patterns(self, func: Callable) -> List[Pattern]:
        patterns: List[Pattern] = []
        if hasattr(func, 'alias_patterns'):
            for pattern in func.alias_patterns:  # type: ignore
                patterns.append(self._build_pattern_regex(pattern))
        return patterns

    @staticmethod
    def _build_pattern_regex(pattern: str,
                             case_sensitive: bool = False) -> Pattern[str]:
        command = re.sub(r'(<\w+>)', r'(\"?\1\"?)', pattern)
        command_regex = re.sub(r'(<\w+>)', r'(?P\1[^"]*)', command)
        return re.compile("^{}$".format(command_regex),
                          0 if case_sensitive else re.IGNORECASE)

    def pattern_matches(self,
                        message: Message) -> Optional[Dict]:
        match = self.pattern.match(message.text)
        if match:
            return match.groupdict()
        # Only check aliases if main pattern does not match
        for alias in self.alias_patterns:
            match = alias.match(message.text)
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
        self.middleware_functions: List[Callable
                                        [[Message], Optional[Message]]] = []
        self.scheduler = Scheduler()
        self.fallback_func: Optional[Callable[[], PhialResponse]] = None

    def add_command(self,
                    pattern: str,
                    func: Callable,
                    case_sensitive: bool = False) -> None:
        pattern = "{0}{1}".format(self.config["prefix"], pattern)
        command = Command(pattern, func, case_sensitive)
        self.commands.append(command)

    def command(self,
                pattern: str,
                case_sensitive: bool = False) -> Callable:
        def decorator(f: Callable) -> Callable:
            self.add_command(pattern, f, case_sensitive)
            return f
        return decorator

    def alias(self, pattern: str) -> Callable:
        pattern = "{0}{1}".format(self.config["prefix"], pattern)

        def decorator(f: Callable) -> Callable:
            if not hasattr(f, 'alias_patterns'):
                f.alias_patterns = []  # type: ignore
            f.alias_patterns.append(pattern)  # type: ignore
            return f
        return decorator

    def add_fallback(self, func: Callable) -> None:
        self.fallback_func = func

    def fallback(self) -> Callable:
        def decorator(f: Callable) -> Callable:
            self.add_fallback(f)
            return f
        return decorator

    def add_middleware(self,
                       func: Callable[[Message], Optional[Message]]) -> None:
        self.middleware_functions.append(func)

    def middleware(self) -> Callable:
        def decorator(f: Callable) -> Callable:
            self.add_middleware(f)
            return f
        return decorator

    def add_scheduled(self,
                      schedule: Schedule,
                      scheduled_func: Callable) -> None:
        job = ScheduledJob(schedule, scheduled_func)
        self.scheduler.add_job(job)

    def send_message(self, message: Response) -> None:
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

        self.slack_client.api_call("reactions.add",
                                   channel=response.channel,
                                   timestamp=response.original_ts,
                                   name=response.reaction,
                                   as_user=True)

    def upload_attachment(self, attachment: Attachment) -> None:
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

        # Run middleware functions
        for func in self.middleware_functions:
            if message:
                message = func(message)

        # If message has been intercepted or is a bot message return early
        if not message or message.bot_id:
            return

        # If message has not been intercepted continue with standard message
        # handling
        for command in self.commands:
            kwargs = command.pattern_matches(message)
            if kwargs is not None:
                response = command.func(**kwargs)
                self._send_response(response, message.channel)
                return
        # If we are here then no commands have matched
        if self.fallback_func is not None:
            response = self.fallback_func()
            self._send_response(response, message.channel)

    def run(self) -> None:
        auto_reconnect = self.config['autoReconnect']
        if not self.slack_client.rtm_connect(auto_reconnect=auto_reconnect,
                                             with_team_state=False):
            raise ValueError("Connection failed. Invalid Token or bot ID")
        while True:
            try:
                message = parse_slack_output(self.slack_client.rtm_read())
                self._handle_message(message)
                self.scheduler.run_pending()
            except Exception as e:
                print("Error {0}".format(e))


# test = Phial('token')


# @test.command("test")
# @test.alias("foo")
# def command_one() -> str:
#     return ":tada:"


# def command_two(test: str) -> None:
#     print("Here {0}".format(test))


# test.add_command("test2 <test>", command_two)
# test.run()
