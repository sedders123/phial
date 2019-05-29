"""The core of phial."""
import json
import logging
from time import sleep
from typing import Callable, Dict, List, NoReturn, Optional

from slackclient import SlackClient  # type: ignore

from phial.commands import help_command
from phial.globals import _command_ctx_stack
from phial.scheduler import Schedule, ScheduledJob, Scheduler
from phial.types import PhialResponse
from phial.utils import parse_slack_output
from phial.wrappers import Attachment, Command, Message, Response


class Phial:
    """
    The Phial class acts as the main interface to Slack.

    It handles registraion and execution of user defined commands,
    as well as providing a wrapper around :obj:`slackclient.SlackClient`
    to make sending messages to Slack simpler.
    """

    #: Default configuration
    default_config = {
        'prefix': "!",
        'registerHelpCommand': True,
        'baseHelpText': "All available commands:",
        'autoReconnect': True,
        'loopDelay': 0.001,
    }

    def __init__(self,
                 token: str,
                 config: Dict = default_config) -> None:
        self.slack_client = SlackClient(token)
        self.commands = []  # type: List[Command]
        self.config = dict(self.default_config)  # type: Dict
        self.config.update(config)
        self.middleware_functions = []  # type: List[Callable[[Message], Optional[Message]]] # noqa: E501
        self.scheduler = Scheduler()
        self.fallback_func = None  # type: Optional[Callable[[Message], PhialResponse]] # noqa: E501
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(name)s] - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False
            self.logger.setLevel(logging.DEBUG)
        self._register_standard_commands()

    def add_command(self,
                    pattern: str,
                    func: Callable[..., PhialResponse],
                    case_sensitive: bool = False,
                    help_text_override: Optional[str] = None) -> None:
        """
        Registers a command with the bot.

        This method can be used as a decorator via :meth:`command`

        :param pattern: The pattern that a :obj:`Message`'s text must
                        match for the command to be invoked.
        :param func: The fucntion to be executed when the command is
                     invoked
        :param case_sensitive: Whether the :code:`pattern` should
                               respect case sensitivity.

                               Defaults to False
        :param help_text_override: Text that should be used as a
                                   description of the command using
                                   the inbuilt help function.

                                   If not overriden the command's
                                   docstring will be used as the
                                   help text.

                                   Defaults to None

        :raises ValueError: If command with the same pattern is already
                            registered

        .. rubric:: Example

        ::

            def hello():
                return "world"
            bot.add_command('hello', world)


        Is the same as
        ::

            @bot.command('hello')
            def hello():
                return "world"

        """
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
                case_sensitive: bool = False,
                help_text_override: Optional[str] = None) -> Callable:
        """
        Registers a command with the bot.

        This command is a decorator version of :meth:`add_command`

        :param pattern: The pattern that a :obj:`Message`'s text must
                        match for the command to be invoked.
        :param case_sensitive: Whether the :code:`pattern` should
                               respect case sensitivity.

                               Defaults to False
        :param help_text_override: Text that should be used as a
                                   description of the command using
                                   the inbuilt help function.

                                   If not overriden the command's
                                   docstring will be used as the
                                   help text.

                                   Defaults to None

        .. rubric:: Example

        ::

                @bot.command('hello')
                def hello():
                    return "world"

                @bot.command('caseSensitive', case_sensitive=True)
                def case_sensitive():
                    return "You typed caseSensitive"

        """
        def decorator(f: Callable) -> Callable:
            self.add_command(pattern, f, case_sensitive, help_text_override)
            return f
        return decorator

    def alias(self, pattern: str) -> Callable:
        """
        A decorator that is used to register an alias for a command.

        :param pattern: The pattern that a :obj:`Message`'s text must
                        match for the command to be invoked.

        .. rubric:: Example

        ::

            @bot.command('hello')
            @bot.alias('goodbye')
            def hello():
                return "world"
        """
        pattern = "{0}{1}".format(self.config["prefix"] if "prefix"
                                  in self.config else "", pattern)

        def decorator(f: Callable) -> Callable:
            if not hasattr(f, 'alias_patterns'):
                f.alias_patterns = []  # type: ignore
            f.alias_patterns.append(pattern)  # type: ignore
            return f
        return decorator

    def add_fallback_command(self,
                             func: Callable[[Message], PhialResponse]) -> None:
        """
        Add a fallback command.

        Registers a 'fallback' function to run when a user tries to execute a
        command that doesn't exist.

        This method can be used as a decorator via :meth:`fallback_command`

        :param func: The function to be executed when the user tries
                     to execute a command that doesn't exist

        .. rubric:: Example

        ::

            def error_handler(message: Message) -> str:
                return "Oops that command doesn't seem to exist"

            bot.add_fallback_command(error_handler)

        Is the same as
        ::

            @bot.fallback_command()
            def error_handler(message: Message) -> str:
                return "Oops that command doesn't seem to exist"

        """
        self.fallback_func = func

    def fallback_command(self) -> Callable:
        """
        A decorator to add a fallback command.

        See :meth:`add_fallback_command` for more information on
        fallback commands

        .. rubric:: Example

        ::

            @bot.fallback_command()
            def error_handler(message: Message) -> str:
                return "Oops that command doesn't seem to exist"
        """
        def decorator(f: Callable) -> Callable:
            self.add_fallback_command(f)
            return f
        return decorator

    def add_middleware(self,
                       func: Callable[[Message], Optional[Message]]) -> None:
        """
        Adds a middleware function to the bot.

        Middleware functions get passed every message the bot recieves from
        slack before the bot process the message itself. Returning :obj:`None`
        from a middleware function will prevent the bot from processing it.

        This method can be used as a decorator via :meth:`middleware`.

        :param middleware_func: The function to be added to the middleware
                                pipeline

        .. rubric :: Example

        ::

            def intercept(messaage):
                return message
            bot.add_middleware(intercept)

        Is the same as
        ::

            @bot.middleware()
            def intercept(messaage):
                return message

        """
        self.middleware_functions.append(func)
        self.logger.debug("Middleware {0} added"
                          .format(getattr(func, '__name__', repr(func))))

    def middleware(self) -> Callable:
        """
        A decorator to add a middleware function to the bot.

        See :meth:`add_middleware` for more information about middleware

        .. rubric:: Example

        ::

            @bot.middleware()
            def intercept(messaage):
                return message
        """
        def decorator(f: Callable) -> Callable:
            self.add_middleware(f)
            return f
        return decorator

    def add_scheduled(self,
                      schedule: Schedule,
                      func: Callable) -> None:
        """
        Adds a scheduled function to the bot.

        This method can be used as a decorator via :meth:`scheduled`.

        :param schedule: The schedule used to run the function
        :param scheduled_func: The function to be run in accordance to the
                               schedule

        .. rubric:: Example

        ::

            def scheduled_beep():
                bot.send_message(Response(text="Beep",
                                          channel="channel-id">))
            bot.add_scheduled(Schedule().every().day(), scheduled_beep)

        Is the same as

        ::

            @bot.scheduled(Schedule().every().day())
            def scheduled_beep():
                bot.send_message(Response(text="Beep",
                                          channel="channel-id">))
        """
        job = ScheduledJob(schedule, func)
        self.scheduler.add_job(job)
        self.logger.debug("Schedule {0} added"
                          .format(getattr(func, '__name__', repr(func))))

    def scheduled(self, schedule: Schedule) -> Callable:
        """
        A decorator that is used to register a scheduled function.

        See :meth:`add_scheduled` for more information on scheduled
        jobs.

        :param schedule: The schedule used to determine when the function
                         should be run

        .. rubric:: Example

        ::

            @bot.scheduled(Schedule().every().day())
            def scheduled_beep():
                bot.send_message(Response(text="Beep",
                                          channel="channel-id">))
        """
        def decorator(f: Callable) -> Callable:
            self.add_scheduled(schedule, f)
            return f
        return decorator

    def send_message(self, message: Response) -> None:
        """
        Sends a message to Slack.

        :param message: The message to be sent to Slack
        """
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
        """
        Sends a reaction to a Slack Message.

        :param response: Response containing the reaction to be
                         sent to Slack
        """
        self.slack_client.api_call("reactions.add",
                                   channel=response.channel,
                                   timestamp=response.original_ts,
                                   name=response.reaction,
                                   as_user=True)

    def upload_attachment(self, attachment: Attachment) -> None:
        """
        Upload a file to Slack.

        :param attachment: The attachment to be uploaded to Slack
        """
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
            raise ValueError('Only Response or Attachment objects can be '
                             'returned from command functions')

        if isinstance(response, Response):
            if response.original_ts and response.reaction and response.text:
                raise ValueError('Response objects with an original timestamp '
                                 'can only have one of the attributes: '
                                 'Reaction, Text')
            if response.original_ts and response.reaction:
                self.send_reaction(response)
            elif response.text or response.attachments:
                self.send_message(response)

        if isinstance(response, Attachment):
            self.upload_attachment(response)

    def _handle_message(self, message: Optional[Message]) -> None:
        if not message:
            return

        # Run middleware functions
        for func in self.middleware_functions:
            if message:
                self.logger.debug(f"Ran middleware: {func.__name__} on"
                                  " {message}")
                message = func(message)

        # If message has been intercepted or is a bot message return early
        if not message or message.bot_id:
            return

        # If message should have a prefix but doesn't return early
        if "prefix" in self.config and self.config["prefix"] is not None \
                and not message.text.startswith(self.config["prefix"]):
            return

        # If message has not been intercepted continue with standard message
        # handling
        for command in self.commands:
            command_name = command.func.__name__
            kwargs = command.pattern_matches(message)
            if kwargs is not None:
                try:
                    _command_ctx_stack.push(message)
                    response = command.func(**kwargs)
                    self._send_response(response, message.channel)
                    return
                finally:
                    self.logger.debug(f"Ran command: {command_name} on"
                                      " {message}")
                    _command_ctx_stack.pop()

        # If we are here then no commands have matched
        self.logger.warning("Command {0} not found".format(message.text))
        if self.fallback_func is not None:
            try:
                _command_ctx_stack.push(message)
                response = self.fallback_func(message)
                self._send_response(response, message.channel)
            finally:
                _command_ctx_stack.pop()

    def run(self) -> NoReturn:
        """
        Starts the bot.

        When called will start the bot listening to messages from Slack
        """
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
                self.logger.error(e, exec_info=True)
            sleep(self.config['loopDelay'])  # Help prevent high CPU usage.
