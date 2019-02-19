from slackclient import SlackClient  # type: ignore
from typing import Callable, List, Optional, Pattern, Dict, Union, IO, cast
import re
from phial.scheduler import Scheduler, Schedule, ScheduledJob
from phial.utils import parse_help_text
import logging
from werkzeug.local import LocalStack, LocalProxy
import json

PhialResponse = Union[None, str, 'Response', 'Attachment']


def _find_command() -> 'Message':
    '''Gets the command from the context stack'''
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError('Not in a context with a command')
    return cast('Message', top)


_command_ctx_stack = LocalStack()  # type: ignore
command: 'Message' = cast('Message', LocalProxy(_find_command))


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


def help_command(bot: 'Phial') -> str:
    help_text = cast(str, bot.config.get('baseHelpText', ""))
    if help_text:
        help_text += "\n"
    for command in bot.commands:
        command_doc = command.help_text
        if not command_doc:
            # If no help text default to blank string
            command_doc = ""
        command_help_text = parse_help_text(command_doc)
        # command_name = bot.command_names[command]
        help_text += "*{0}* - {1}\n".format(command.pattern_string,
                                            command_help_text)
    return help_text


class Response():
    def __init__(self,
                 channel: str,
                 text: Optional[str] = None,
                 original_ts: Optional[str] = None,
                 reaction: Optional[str] = None,
                 ephemeral: bool = False,
                 user: Optional[str] = None,
                 attachments: Optional[Dict] = None) -> None:
        self.channel = channel
        self.text = text
        self.original_ts = original_ts
        self.reaction = reaction
        self.ephemeral = ephemeral
        self.user = user
        self.attachments = attachments

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
                 case_sensitive: bool = False,
                 help_text_override: Optional[str] = None):
        self.pattern_string = pattern
        self.pattern = self._build_pattern_regex(pattern, case_sensitive)
        self.alias_patterns = self._get_alias_patterns(func)
        self.func = func
        self.case_sensitive = case_sensitive
        self.help_text_override = help_text_override

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

    @property
    def help_text(self) -> Optional[str]:
        if self.help_text_override is not None:
            return self.help_text_override
        return self.func.__doc__


class Phial:

    #: Default configuration
    default_config = {
        'prefix': "!",
        'registerHelpCommand': True,
        'baseHelpText': "All available commands:",
        'autoReconnect': True
    }

    def __init__(self,
                 token: str,
                 config: Dict = default_config,
                 logger: Optional[logging.Logger] = None) -> None:
        self.slack_client = SlackClient(token)
        self.commands: List[Command] = []
        self.config: Dict = config
        self.middleware_functions: List[Callable
                                        [[Message], Optional[Message]]] = []
        self.scheduler = Scheduler()
        self.fallback_func: Optional[Callable[[], PhialResponse]] = None
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.hasHandlers():
                handler = logging.StreamHandler()
                formatter = logging.Formatter(fmt="%(asctime)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.propagate = False
            logger.setLevel(logging.INFO)
        self.logger = logger
        self._register_standard_commands()

    def add_command(self,
                    pattern: str,
                    func: Callable,
                    case_sensitive: bool = False,
                    help_text_override: Optional[str] = None) -> None:
        pattern = "{0}{1}".format(self.config["prefix"], pattern)

        # Validate command does not already exist
        for existing_command in self.commands:
            if pattern == existing_command.pattern_string:
                raise ValueError('Command {0} already exists'
                                 .format(pattern.split("<")[0]))

        # Create and add command
        command = Command(pattern, func, case_sensitive, help_text_override)
        self.commands.append(command)
        self.logger.debug("Command {0} added"
                          .format(pattern))

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
        self.logger.debug("Middleware {0} added"
                          .format(getattr(func, '__name__', repr(func))))

    def middleware(self) -> Callable:
        def decorator(f: Callable) -> Callable:
            self.add_middleware(f)
            return f
        return decorator

    def add_scheduled(self,
                      schedule: Schedule,
                      func: Callable) -> None:
        job = ScheduledJob(schedule, func)
        self.scheduler.add_job(job)
        self.logger.debug("Schedule {0} added"
                          .format(getattr(func, '__name__', repr(func))))

    def send_message(self, message: Response) -> None:
        api_method = ('chat.postEphemeral' if message.ephemeral
                      else 'chat.postMessage')

        if message.original_ts:
            self.slack_client.api_call(api_method,
                                       channel=message.channel,
                                       text=message.text,
                                       thread_ts=message.original_ts,
                                       attachments=json.dumps(
                                           message.attachments),
                                       user=message.user,
                                       as_user=True)
        else:
            self.slack_client.api_call(api_method,
                                       channel=message.channel,
                                       text=message.text,
                                       attachments=json.dumps(
                                           message.attachments),
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

    def _register_standard_commands(self) -> None:
        if self.config['registerHelpCommand']:
            # The command function has to be a lambda as we wish to delay
            # execution until all commands have been registered.
            self.add_command("help", lambda: help_command(self),
                             help_text_override="List all available commmands")

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

        # If message should have a prefix but doesn't return early
        if (self.config["prefix"] is not None and not
                message.text.startswith(self.config["prefix"])):
            return

        # If message has not been intercepted continue with standard message
        # handling
        for command in self.commands:
            kwargs = command.pattern_matches(message)
            if kwargs is not None:
                try:
                    _command_ctx_stack.push(message)
                    response = command.func(**kwargs)
                    self._send_response(response, message.channel)
                    return
                finally:
                    _command_ctx_stack.pop()

        # If we are here then no commands have matched
        self.logger.warn("Command {0} not found".format(message.text))
        if self.fallback_func is not None:
            try:
                _command_ctx_stack.push(message)
                response = self.fallback_func()
                self._send_response(response, message.channel)
            finally:
                _command_ctx_stack.pop()

    def run(self) -> None:
        auto_reconnect = self.config['autoReconnect']
        if not self.slack_client.rtm_connect(auto_reconnect=auto_reconnect,
                                             with_team_state=False):
            raise ValueError("Connection failed. Invalid Token or bot ID")

        self.logger.info("Phial connected and running!")
        while True:
            try:
                message = parse_slack_output(self.slack_client.rtm_read())
                self._handle_message(message)
                self.scheduler.run_pending()
            except Exception as e:
                self.logger.exception("Error {0}".format(e))


# test = Phial('token')


# @test.command("test")
# @test.alias("foo")
# def command_one() -> str:
#     """
#     From multiline docstring
#     """
#     return ":tada:" + str(command.timestamp)


# def command_two(test: str) -> None:
#     print("Here {0}".format(test))


# @test.fallback()
# def fallback():
#     return "beep"


# test.add_command("test2 <test>", command_two)
# test.run()
