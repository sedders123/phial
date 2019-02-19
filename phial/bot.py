from slackclient import SlackClient  # type: ignore
from typing import Dict, List, Callable, Optional
import logging
import json
from phial.commands import help_command
from phial.globals import _command_ctx_stack
from phial.scheduler import Scheduler, Schedule, ScheduledJob
from phial.wrappers import Command, Response, Message, Attachment
from phial.utils import parse_slack_output
from phial.types import PhialResponse


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
        pattern = "{0}{1}".format(self.config["prefix"] if "prefix"
                                  in self.config else "", pattern)
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
        pattern = "{0}{1}".format(self.config["prefix"] if "prefix"
                                  in self.config else "", pattern)

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
        if ("registerHelpCommand" in self.config and self.
                config['registerHelpCommand']):
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
