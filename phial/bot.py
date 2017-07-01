from slackclient import SlackClient
import time
import re
from .globals import _command_ctx_stack
from .wrappers import Command, Message


class Phial():
    '''
    The Phial object acts as the central object. It is gieven a token and an
    optional config file. Once created it hold the core components of the bot,
    including command functions, command patterns and more.
    '''
    DEFAULT_CONFIG = {
        'prefix': '!',
        'read_websocket_delay': 1
    }

    def __init__(self, token, config=DEFAULT_CONFIG):
        self.slack_client = SlackClient(token)
        self.commands = []
        self.config = config

    @staticmethod
    def build_command_pattern(command):
        '''Creates the command pattern reg exs'''
        command_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', command)
        return re.compile("^{}$".format(command_regex))

    def add_command(self, command_str, command_func):
        '''Creates a command pattern and adds a command function to the bot'''
        command_pattern = self.build_command_pattern(command_str)
        self.commands.append((command_pattern, command_func))

    def get_command_match(self, command):
        '''
        Returns a command function for the command pattern that is matched.
        Will returns None if no match
        '''
        for command_pattern, command_function in self.commands:
            m = command_pattern.match(command)
            if m:
                return m.groupdict(), command_function
        return None

    def command(self, command_text):
        '''A decorator for add_command'''
        def decorator(f):
            self.add_command(command_text, f)
        return decorator


    def _handle_command(self, command, channel):
        command_match = self.get_command_match(command)
        try:
            if command_match:
                base_command = command.split(" ")[0]
                kwargs, command_function = command_match
                _command_ctx_stack.push(Command(base_command, channel, kwargs))
                return command_function(**kwargs)
            else:
                raise ValueError('Command "{}" has not been registered'
                                 .format(command))
        except ValueError as err:
            print('ValueError: {}'.format(err))
        finally:
            _command_ctx_stack.pop()

    def _parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if(output and 'text' in output
                   and output['text'].startswith(self.config['prefix'])):
                    return output['text'][1:], output['channel']
        return None, None

    def send_message(self, message):
        self.slack_client.api_call("chat.postMessage",
                                   channel=message.channel,
                                   text=message.text,
                                   as_user=True)

    def execute_response(self, response):
        '''Execute the response of a command function'''
        if isinstance(response, Message):
            self.send_message(response)

    def run(self):
        slack_client = self.slack_client
        if slack_client.rtm_connect():
            print("Phial connected and running!")
            while True:
                command, channel = self._parse_slack_output(slack_client
                                                            .rtm_read())
                if command and channel:
                    response = self._handle_command(command, channel)
                    if response is not None:
                        self.execute_response(response)
                time.sleep(self.config['read_websocket_delay'])
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
