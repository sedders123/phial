"""The core of phial."""

import json
import logging
from concurrent.futures import Future, ThreadPoolExecutor
from time import sleep
from typing import Callable, Optional, cast

from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

from phial.commands import help_command
from phial.errors import ArgumentTypeValidationError
from phial.globals import _command_ctx_stack
from phial.scheduler import Schedule, ScheduledJob, Scheduler
from phial.utils import parse_slack_event, validate_kwargs
from phial.wrappers import (  # fmt: off
    Attachment,
    Command,
    Message,
    PhialResponse,
    Response,
)


class Phial:
    """
    The Phial class acts as the main interface to Slack.

    It handles registration and execution of user defined commands,
    as well as providing a wrapper around :obj:`slackclient.SlackClient`
    to make sending messages to Slack simpler.
    """

    #: Default configuration
    default_config = {
        "prefix": "!",
        "registerHelpCommand": True,
        "baseHelpText": "All available commands:",
        "autoReconnect": True,
        "loopDelay": 0.001,
        "hotReload": False,
        "maxThreads": 4,
    }

    def __init__(
        self, app_token: str, bot_token: str, config: dict = default_config
    ) -> None:
        self.config = dict(self.default_config)
        self.config.update(config)
        self.slack_client = SocketModeClient(
            app_token=app_token,
            web_client=WebClient(token=bot_token),
            auto_reconnect_enabled=cast(bool, self.config["autoReconnect"]),
        )
        self.commands: list[Command] = []
        self.middleware_functions: list[Callable[[Message], Optional[Message]]] = []
        self.scheduler = Scheduler()
        self.fallback_func: Optional[Callable[[Message], PhialResponse]] = None
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():  # pragma: nocover
            handler = logging.StreamHandler()
            formatter = logging.Formatter(fmt="%(asctime)s [%(name)s] - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False
            self.logger.setLevel(logging.INFO)
        self._register_standard_commands()

    def add_command(
        self,
        pattern: str,
        func: Callable[..., PhialResponse],
        case_sensitive: bool = False,
        help_text_override: Optional[str] = None,
        hide_from_help_command: Optional[bool] = False,
    ) -> None:
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
        :param hide_from_help_command: A flag to specify whether or not
                                       the inbuilt help command should
                                       hide this command from the list
                                       it generates.

                                       Defaults to False

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
        pattern = "{0}{1}".format(
            self.config["prefix"] if "prefix" in self.config else "", pattern
        )
        # Validate command does not already exist
        for existing_command in self.commands:
            if pattern == existing_command.pattern_string:
                raise ValueError(
                    "Command {0} already exists".format(pattern.split("<")[0])
                )

        # Create and add command
        command = Command(
            pattern,
            func,
            case_sensitive,
            help_text_override=help_text_override,
            hide_from_help_command=hide_from_help_command,
        )
        self.commands.append(command)
        self.logger.debug("Command {0} added".format(pattern))

    def command(
        self,
        pattern: str,
        case_sensitive: bool = False,
        help_text_override: Optional[str] = None,
        hide_from_help_command: Optional[bool] = False,
    ) -> Callable:
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
        :param hide_from_help_command: A flag to specify whether or not
                                       the inbuilt help command should
                                       hide this command from the list
                                       it generates.

                                       Defaults to False

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
            self.add_command(
                pattern,
                f,
                case_sensitive,
                help_text_override=help_text_override,
                hide_from_help_command=hide_from_help_command,
            )
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
        pattern = "{0}{1}".format(
            self.config["prefix"] if "prefix" in self.config else "", pattern
        )

        def decorator(f: Callable) -> Callable:
            if not hasattr(f, "alias_patterns"):
                f.alias_patterns = []  # type: ignore
            f.alias_patterns.append(pattern)  # type: ignore
            return f

        return decorator

    def add_fallback_command(self, func: Callable[[Message], PhialResponse]) -> None:
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

    def add_middleware(self, func: Callable[[Message], Optional[Message]]) -> None:
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
        self.logger.debug(
            "Middleware {0} added".format(getattr(func, "__name__", repr(func)))
        )

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

    def add_scheduled(self, schedule: Schedule, func: Callable) -> None:
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
        self.logger.debug(
            "Schedule {0} added".format(getattr(func, "__name__", repr(func)))
        )

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

        if message.ephemeral:
            if message.user is None:
                raise ValueError("User not provided for ephemeral message")
            self.slack_client.web_client.chat_postEphemeral(
                channel=message.channel,
                text=message.text,
                thread_ts=message.original_ts,
                attachments=json.dumps(message.attachments),
                user=message.user,
                as_user=True,
            )
        else:
            self.slack_client.web_client.chat_postMessage(
                channel=message.channel,
                text=message.text,
                thread_ts=message.original_ts,
                attachments=json.dumps(message.attachments),
                as_user=True,
            )

    def send_reaction(self, response: Response) -> None:
        """
        Sends a reaction to a Slack Message.

        :param response: Response containing the reaction to be
                         sent to Slack
        """
        if response.original_ts is None or response.reaction is None:
            raise ValueError(
                "Original timestamp and reaction must be provided for reaction"
            )
        self.slack_client.web_client.reactions_add(
            channel=response.channel,
            timestamp=response.original_ts,
            name=response.reaction,
        )

    def upload_attachment(self, attachment: Attachment) -> None:
        """
        Upload a file to Slack.

        :param attachment: The attachment to be uploaded to Slack
        """
        self.slack_client.web_client.files_upload_v2(
            channels=attachment.channel,
            filename=attachment.filename,
            file=attachment.content,  # type: ignore
            title=attachment.filename,
        )

    def _register_standard_commands(self) -> None:
        if "registerHelpCommand" in self.config and self.config["registerHelpCommand"]:
            # The command function has to be a lambda as we wish to delay
            # execution until all commands have been registered.
            self.add_command(
                "help",
                lambda: help_command(self),
                help_text_override="List all available commmands",
            )

    def _send_response(self, response: PhialResponse, original_channel: str) -> None:
        if response is None:
            return  # Do nothing if command function returns nothing

        if isinstance(response, str):
            self.send_message(Response(text=response, channel=original_channel))

        elif not isinstance(response, Response) and not isinstance(
            response, Attachment
        ):
            raise ValueError(
                "Only Response or Attachment objects can be "
                "returned from command functions"
            )

        if isinstance(response, Response):
            if response.original_ts and response.reaction and response.text:
                raise ValueError(
                    "Response objects with an original timestamp "
                    "can only have one of the attributes: "
                    "Reaction, Text"
                )
            if response.original_ts and response.reaction:
                self.send_reaction(response)
            elif response.text or response.attachments:
                self.send_message(response)

        if isinstance(response, Attachment):
            self.upload_attachment(response)

    def _handle_message(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        try:
            self._handle_message_internal(client, req)
        except Exception as e:
            self.logger.error(e)

    def _handle_message_internal(
        self, client: SocketModeClient, req: SocketModeRequest
    ) -> None:
        # Acknowledge the request so it is not resent
        ack_response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(ack_response)

        if req.type != "events_api":
            return
        message = parse_slack_event(req.payload)

        # Run middleware functions
        for func in self.middleware_functions:
            if message:
                self.logger.debug(
                    "Ran middleware: {0} on {1}".format(func.__name__, message)
                )
                message = func(message)

        # If message has been intercepted or is a bot message return early
        if not message or message.bot_id:
            return

        # If message should have a prefix but doesn't return early
        if (
            "prefix" in self.config
            and self.config["prefix"] is not None
            and self.config["prefix"] != ""
            and isinstance(self.config["prefix"], str)
            and not message.text.startswith(self.config["prefix"])
        ):
            return

        # If message has not been intercepted continue with standard message
        # handling
        for command in self.commands:
            command_name = command.func.__name__
            kwargs = command.pattern_matches(message)
            if kwargs is not None:
                try:
                    kwargs = validate_kwargs(command.func, kwargs)
                    _command_ctx_stack.push(message)
                    response = command.func(**kwargs)
                    self._send_response(response, message.channel)
                    return
                except ArgumentTypeValidationError as e:
                    self._send_response(str(e), message.channel)
                    return
                finally:
                    self.logger.debug(
                        "Ran command: {0} on {1}".format(command_name, message)
                    )
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

    def _start(self) -> None:  # pragma: no cover
        """
        Starts the bot.

        When called will start the bot listening to messages from Slack
        """
        self.slack_client.socket_mode_request_listeners.append(self._handle_message)  # type: ignore
        self.slack_client.connect()

        self.logger.info("Phial connected and running!")

        thread_pool_size = int(cast(str, self.config["maxThreads"]))
        thread_pool = ThreadPoolExecutor(thread_pool_size)
        run_pending_tasks: Optional[Future] = None

        while True:
            try:
                if run_pending_tasks is None or run_pending_tasks.done():
                    run_pending_tasks = thread_pool.submit(self.scheduler.run_pending)
            except Exception as e:
                self.logger.error(e)
            sleep(cast(float, self.config["loopDelay"]))  # Help prevent high CPU usage.

    def run(self) -> None:  # pragma: no cover
        """Run the bot."""
        if self.config["hotReload"]:
            # TODO: Implement hot reload
            self._start()
        else:
            self._start()
