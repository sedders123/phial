from slackclient import SlackClient
import re
from .globals import _command_ctx_stack, command, _global_ctx_stack
from .wrappers import Command, Response, Message, Attachment


class Phial():
    '''
    The Phial object acts as the central object. It is given a token and an
    optional config dictionary. Once created it holds the core components of
    the bot, including command functions, command patterns and more.
    '''

    #: Default configuration
    default_config = {
        'prefix': '!'
    }

    def __init__(self, token, config=default_config):
        self.slack_client = SlackClient(token)
        self.commands = {}
        self.middleware_functions = []
        self.config = config
        self.running = False
        _global_ctx_stack.push({})

    @staticmethod
    def _build_command_pattern(command):
        '''Creates the command pattern regexs'''
        command_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', command)
        return re.compile("^{}$".format(command_regex))

    def add_command(self, command_pattern_template, command_func):
        '''
        Creates a command pattern and adds a command function to the bot. This
        is the same as :meth:`command`.

        ::

            @bot.command('hello')
            def world():
                pass

        Is the same as ::

            def world():
                pass
            bot.add_command('hello', world)

        Args:
            command_pattern_template(str): A string that will be used to create
                                           a command_pattern regex
            command_func(func): The function to be run when the command pattern
                                is matched
        Raises:
            ValueError
                If command with the same name already registered
        '''
        command_pattern = self._build_command_pattern(command_pattern_template)
        if command_pattern not in self.commands:
            self.commands[command_pattern] = command_func
        else:
            raise ValueError('Command {0} already exists'
                             .format(command_pattern.split("<")[0]))

    def get_command_match(self, text):
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

    def command(self, command_pattern_template):
        '''
        A decorator that is used to register a command function for a given
        command. This does the same as :meth:`add_command` but is used as a
        decorator.

        Args:
            command_pattern_template(str): A string that will be used to create
                                           a command_pattern regex

        Example:
            ::

                @bot.command('hello')
                def world():
                    pass

        '''
        def decorator(f):
            self.add_command(command_pattern_template, f)
            return f
        return decorator

    def middleware(self):
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
        def decorator(f):
            self.middleware_functions.append(f)
            return f
        return decorator

    def add_middleware(self, middleware_func):
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
        self.middleware_functions.append(middleware_func)

    def alias(self, command_pattern_template):
        '''
        A decorator that is used to register an alias for a command.
        Internally this is the same as :meth:`command`.

        Args:
            command_pattern_template(str): A string that will be used to create
                                a command_pattern regex

        Example:
            ::

                @bot.command('hello')
                @bot.alias('goodbye')
                def world():
                    pass

            Is the same as ::
                @bot.command('hello')
                @bot.command('goodbye')
                def world():
                    pass
        '''
        return self.command(command_pattern_template)

    def _create_command(self, command_message):
        '''Creates an instance of a command'''
        command_match = self.get_command_match(command_message.text)
        if command_match:
            kwargs, command_pattern = command_match
            return Command(command_pattern,
                           command_message.channel,
                           kwargs,
                           command_message.user,
                           command_message)

    def _handle_command(self, command):
        '''Executes a given command'''
        if command is None:
            return  # Do nothing if no command
        _command_ctx_stack.push(command)
        return self.commands[command.command_pattern](**command
                                                      .args)

    def _parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            This function parses the JSON form Slack into phial Messages
        """
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
                                   bot_id)
        return None

    def send_message(self, message):
        '''
        Takes a response object and then sends the message to Slack

        Args:
            message(Response): message object to be sent to Slack

        '''
        if message.original_ts:
            self.slack_client.api_call("chat.postMessage",
                                       channel=message.channel,
                                       text=message.text,
                                       thread_ts=message.original_ts,
                                       as_user=True)
        else:
            self.slack_client.api_call("chat.postMessage",
                                       channel=message.channel,
                                       text=message.text,
                                       as_user=True)

    def send_reaction(self, response):
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

    def upload_attachment(self, attachment):
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

    def _execute_response(self, response):
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
            elif response.text:
                self.send_message(response)
        if isinstance(response, Attachment):
            if not response.content:
                raise ValueError('The content field of Attachment objects ' +
                                 'must be set')
            self.upload_attachment(response)

    def _is_running(self):
        return self.running

    def _handle_message(self, message: Message):
        '''
         Takes a `Message` object and  run the middleware on the message before
         attempting to create and executes a `Command` if the message has not
         been intercepted.
        '''

        # Run middleware functions
        for func in self.middleware_functions:
            if message:
                message = func(message)

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
            print('ValueError: {}'.format(err))
        finally:
            _command_ctx_stack.pop()

    def run(self):
        '''Connects to slack client and handles incoming messages'''
        self.running = True
        slack_client = self.slack_client
        if not slack_client.rtm_connect():
            raise ValueError("Connection failed. Invalid Token or bot ID")

        print("Phial connected and running!")
        while self._is_running():
            try:
                message = self._parse_slack_output(slack_client
                                                   .rtm_read())
                if message:
                    self._handle_message(message)
            except Exception as e:
                print(f"Error: {e}")
