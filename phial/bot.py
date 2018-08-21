from slackclient import SlackClient  # type: ignore
import re
from typing import Dict, List, Pattern, Callable, Union, Tuple, Any, Optional
import logging
import json
from phial.commands import help_command
from phial.globals import _command_ctx_stack, command, _global_ctx_stack
from phial.wrappers import Command, Response, Message, Attachment
from phial.scheduler import Scheduler, Schedule, ScheduledJob


class Phial():
    '''
    The Phial object acts as the central object. It is given a token and an
    optional config dictionary. Once created it holds the core components of
    the bot, including command functions, command patterns and more.
    '''

    #: Default configuration
    default_config = {
        'prefix': '!',
        'registerHelpCommand': True
    }

    def __init__(self,
                 token: str,
                 config: dict = default_config,
                 logger: logging.Logger = logging.getLogger(__name__)) -> None:
        self.slack_client = SlackClient(token)
        self.commands = {}  # type: Dict[Pattern[str], Callable]
        self.command_names = {}  # type: Dict[Pattern[str], str]
        self.middleware_functions = []  # type: List[Callable]
        self.config = config
        self.running = False
        self.logger = logger
        self.scheduler = Scheduler()

        _global_ctx_stack.push({})
        self._register_standard_commands()

    def _register_standard_commands(self) -> None:
        '''
        Register any standard commands respecting the configuration provided
        '''
        if self.config['registerHelpCommand']:
            self.add_command("help", lambda: help_command(self),
                             help_text_override="Help command")

    @staticmethod
    def _build_command_pattern(command: str,
                               case_sensitive: bool) -> Pattern[str]:
        '''Creates the command pattern regexs'''
        command_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', command)
        return re.compile("^{}$".format(command_regex),
                          0 if case_sensitive else re.IGNORECASE)

    def add_command(self,
                    command_pattern_template: str,
                    command_func: Callable,
                    case_sensitive: bool = False,
                    help_text_override: Optional[str]=None) -> None:
        '''
        Creates a command pattern and adds a command function to the bot. This
        is the same as :meth:`command`.

        ::

            @bot.command('hello')
            def hello():
                return "world"

        Is the same as ::

            def hello():
                return "world"
            bot.add_command('hello', world)

        Args:
            command_pattern_template(str): A string that will be used to create
                                           a command_pattern regex
            command_func(func): The function to be run when the command pattern
                                is matched
            case_sensitive(bool, optional): Whether or not the command is case
                                            sensitive.
                                            Defaults to False
            help_text_override(str, optional): Text that should be used as a
                                               description of the comand using
                                               the inbuilt !help function
        Raises:
            ValueError
                If command with the same name already registered
        '''
        command_pattern = self._build_command_pattern(command_pattern_template,
                                                      case_sensitive)

        # Have ignore the type of the line below as mypy can not currently deal
        # with 'extending' functions to have extra attributes
        # GitHub Issue: https://github.com/python/mypy/issues/2087
        command_func._help = (help_text_override if  # type: ignore
                              help_text_override is not None
                              else command.__doc__)

        if command_pattern not in self.commands:
            self.command_names[command_pattern] = command_pattern_template
            self.commands[command_pattern] = command_func
            self.logger.debug("Command {0} added"
                              .format(command_pattern_template))
        else:
            raise ValueError('Command {0} already exists'
                             .format(command_pattern.split("<")[0]))

    def get_command_match(self, text: str) -> Optional[Tuple[Dict,
                                                             Pattern[str]]]:
        '''
        Returns a dictionary of args and the command pattern for the command
        pattern that is matched.
        Will returns None if no match

        Args:
            text(str): The string to be matched to a command

        Returns:
            A :obj:`dict` object with kwargs and the command pattern if a match
            is found otherwise :obj:`None`
        '''
        if self.config['prefix']:
            if not text.startswith(self.config['prefix']):
                return None
            text = text[1:]
        for command_pattern in self.commands:
            m = command_pattern.match(text)
            if m:
                return m.groupdict(), command_pattern
        raise ValueError('Command "{}" has not been registered'
                         .format(text))

    def command(self,
                command_pattern_template: str,
                case_sensitive: bool = False) -> Callable:
        '''
        A decorator that is used to register a command function for a given
        command. This does the same as :meth:`add_command` but is used as a
        decorator.

        Args:
            command_pattern_template(str): A string that will be used to create
                                           a command_pattern regex
            case_sensitive(bool, optional): Whether or not the command is case
                                sensitive.
                                Defaults to False

        Example:
            ::

                @bot.command('hello')
                def hello():
                    return "world"

                @bot.command('caseSensitive', case_sensitive=True)
                def case_sensitive():
                    return "You typed caseSensitive"

        '''
        def decorator(f: Callable) -> Callable:
            self.add_command(command_pattern_template, f, case_sensitive)
            return f
        return decorator

    def middleware(self) -> Callable:
        '''
        A decorator that is used to register a middleware function.
        This does the same as :meth:`add_middleware` but is used as a
        decorator. Each middleware function will be passed a `Message`
        , and must return a `Message` for the next middleware function
        to be able to work. To stop processing of a message simply return
        `None`.

        Example:
            ::

                @bot.middleware()
                def intercept_message(message):
                    # Process message from slack before passing it on phial's
                    # default processing
                    ... code here
                    return message

                @bot.middleware()
                def intercept_and_halt_message(message):
                    # Process message from slack without phial's default
                    # processing
                    ... code here
                    return None

        '''
        def decorator(f: Callable) -> Callable:
            self.add_middleware(f)
            return f
        return decorator

    def add_middleware(self, middleware_func: Callable) -> None:
        '''
        Adds a middleware function to the bot. This is the same as
        :meth:`middleware`.

        ::

            @bot.middleware()
            def intercept(messaage):
                return message

        Is the same as ::

            def intercept(messaage):
                return message
            bot.add_middleware(intercept)

        Args:
            middleware_func(func): The function to be added to the middleware
                                   pipeline
        '''
        self.logger.debug("Middleware {0} added"
                          .format(getattr(middleware_func,
                                          '__name__',
                                          repr(middleware_func))))
        self.middleware_functions.append(middleware_func)

    def alias(self,
              command_pattern_template: str,
              case_sensitive: bool =False) -> Callable:
        '''
        A decorator that is used to register an alias for a command.
        Internally this is the same as :meth:`command`.

        Args:
            command_pattern_template(str): A string that will be used to create
                                a command_pattern regex
            case_sensitive(bool, optional): Whether or not the command is case
                                sensitive.
                                Defaults to False

        Example:
            ::

                @bot.command('hello')
                @bot.alias('goodbye')
                def hello():
                    return "world"

            Is the same as ::
                @bot.command('hello')
                @bot.command('goodbye')
                def hello():
                    return "world"
        '''
        return self.command(command_pattern_template, case_sensitive)

    def scheduled(self, schedule: Schedule) -> Callable:
        '''
        A decorator that is used to register a scheduled function.
        This does the same as :meth:`add_scheduled` but is used as a
        decorator.

        Args:
            schedule(Schedule): The schedule used to run the function

        Example:
            ::

                @bot.scheduled(Schedule().every().day())
                def scheduled_beep():
                    bot.send_message(Response(text="Beep",
                                              channel="channel-id">))
        '''
        def decorator(f: Callable) -> Callable:
            self.add_scheduled(schedule, f)
            return f
        return decorator

    def add_scheduled(self, schedule: Schedule,
                      scheduled_func: Callable) -> None:
        '''
        Adds a scheduled function to the bot. This is the same as
        :meth:`scheduled`.

        ::

            @bot.scheduled(Schedule().every().day())
            def scheduled_beep():
                bot.send_message(Response(text="Beep",
                                            channel="channel-id">))

        Is the same as ::

            def scheduled_beep():
                bot.send_message(Response(text="Beep",
                                            channel="channel-id">))
            bot.add_scheduled(Schedule().every().day(), scheduled_beep)

        Args:
            schedule(Schedule): The schedule used to run the function
            scheduled_func(func): The function to be run in accordance to the
                                  schedule
        '''
        self.logger.debug("Schedule {0} added"
                          .format(getattr(scheduled_func,
                                          '__name__',
                                          repr(scheduled_func))))
        job = ScheduledJob(schedule, scheduled_func)
        self.scheduler.add_job(job)

    def _create_command(self,
                        command_message: Message) -> Optional[Command]:
        '''Creates an instance of a command'''
        command_match = self.get_command_match(command_message.text)
        if command_match:
            kwargs, command_pattern = command_match
            return Command(command_pattern,
                           command_message.channel,
                           kwargs,
                           command_message.user,
                           command_message)
        return None

    def _handle_command(self, command: Optional[Command]) -> Any:
        '''Executes a given command'''
        if command is None:
            return  # Do nothing if no command
        _command_ctx_stack.push(command)
        return self.commands[command.command_pattern](_bot=self,
                                                      **command.args)

    def _parse_slack_output(self,
                            slack_rtm_output: List[Dict])-> Optional[Message]:
        """
            The Slack Real Time Messaging API is an events firehose.
            This function parses the JSON form Slack into phial Messages
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if(output and 'text' in output):
                    self.logger.debug("Message recieved from Slack: {0}"
                                      .format(output))
                    bot_id = None
                    if 'bot_id' in output:
                        bot_id = output['bot_id']
                    return Message(output['text'],
                                   output['channel'],
                                   output['user'],
                                   output['ts'],
                                   bot_id)
        return None

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
                                       attachments=json.dumps(
                                           message.attachments,
                                           default=lambda o: o.__dict__),
                                       user=message.user,
                                       as_user=True)
        else:
            self.slack_client.api_call(api_method,
                                       channel=message.channel,
                                       text=message.text,
                                       attachments=json.dumps(
                                           message.attachments,
                                           default=lambda o: o.__dict__),
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

    def _execute_response(self,
                          response: Union[str, Response, Attachment]) -> None:
        '''Execute the response of a command function'''
        if response is None:
            return  # Do nothing if command function returns nothing
        if isinstance(response, str):
            self.send_message(Response(text=response, channel=command.channel))

        elif not isinstance(response, Response) and not isinstance(response,
                                                                   Attachment):
            raise ValueError('Only Response or Attachment objects can be ' +
                             'returned from command functions')
        if isinstance(response, Response):
            if response.original_ts and response.reaction and response.text:
                raise ValueError('Response objects with an original timestamp '
                                 + 'can only have one of the attributes: '
                                 + 'Reaction, Text')
            if response.original_ts and response.reaction:
                self.send_reaction(response)
            elif response.text or response.attachments:
                self.send_message(response)
        if isinstance(response, Attachment):
            if not response.content:
                raise ValueError('The content field of Attachment objects ' +
                                 'must be set')
            self.upload_attachment(response)

    def _is_running(self) -> bool:
        return self.running

    def _handle_message(self, message: Message) -> None:
        '''
         Takes a `Message` object and  run the middleware on the message before
         attempting to create and executes a `Command` if the message has not
         been intercepted.
        '''

        # Run middleware functions
        for func in self.middleware_functions:
            if message:
                message = func(message, _bot=self)

        # If message has been intercepted or is a bot message return early
        if not message or message.bot_id:
            return

        # If message has not been intercepted continue with standard message
        # handling
        try:
            command = self._create_command(message)
            response = self._handle_command(command)
            self._execute_response(response)
        except ValueError as err:
            self.logger.exception('ValueError: {}'.format(err))
        finally:
            _command_ctx_stack.pop()

    def run(self) -> None:
        '''Connects to slack client and handles incoming messages'''
        self.running = True
        slack_client = self.slack_client
        if not slack_client.rtm_connect():
            raise ValueError("Connection failed. Invalid Token or bot ID")

        self.logger.info("Phial connected and running!")
        while self._is_running():
            try:
                message = self._parse_slack_output(slack_client
                                                   .rtm_read())
                if message:
                    self._handle_message(message)
                self.scheduler.run_pending()
            except Exception as e:
                self.logger.exception("Error: {0}".format(e))
