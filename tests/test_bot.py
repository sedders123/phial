import unittest
from unittest.mock import MagicMock
from phial import Phial, command, Message
import phial.wrappers
import re
from .helpers import captured_output, MockTrueFunc


class TestPhialBot(unittest.TestCase):

    def setUp(self):
        self.bot = Phial('test-token')
        self.bot.is_running = MockTrueFunc()

    def tearDown(self):
        self.bot = None


class TestCommandDecarator(TestPhialBot):
    '''Tests for phial's command decorator'''

    def test_command_decorator_functionality(self):
        @self.bot.command('test')
        def command_function():
            return 'test'

        self.assertTrue('test' in self.bot.command_functions)
        self.assertTrue(command_function in self.bot.command_functions
                        .values())

    def test_command_decorator_calls_add_command(self):
        self.bot.add_command = MagicMock()

        @self.bot.command('test_add_called')
        def test_command_function():
            return 'test'
        self.bot.add_command.assert_called_with('test_add_called',
                                                test_command_function)


class TestAddCommand(TestPhialBot):
    '''Tests for phial's add_command function'''

    def test_add_command_functionality(self):
        def command_function():
            return 'test'
        self.bot.add_command('test', command_function)

        self.assertTrue('test' in self.bot.command_functions)
        self.assertTrue(command_function in self.bot.command_functions
                        .values())

    def test_add_command_errors_on_duplicate_name(self):
        def command_function():
            return 'test'

        self.bot.add_command('duplicate', command_function)

        with self.assertRaises(ValueError) as context:
            self.bot.add_command('duplicate', command_function)

        self.assertTrue('duplicate' in str(context.exception))


class TestBuildCommandPattern(TestPhialBot):
    '''Test phial's build_command_pattern function'''

    def test_build_command_pattern_no_substition(self):
        command_template = 'test'
        command_pattern = self.bot._build_command_pattern(command_template)
        expected_result = re.compile('^test$')
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_single_substition(self):
        command_template = 'test <one>'
        command_pattern = self.bot._build_command_pattern(command_template)
        expected_result = re.compile('^test (?P<one>.+)$')
        self.assertTrue(command_pattern == expected_result)

    def test_build_command_pattern_multiple_substition(self):
        command_template = 'test <one> <two>'
        command_pattern = self.bot._build_command_pattern(command_template)
        expected_result = re.compile('^test (?P<one>.+) (?P<two>.+)$')
        self.assertTrue(command_pattern == expected_result)


class TestGetBaseCommand(TestPhialBot):
    '''Test phial's get_base_command function'''

    def test_get_base_command_functionality(self):
        base_command = self.bot._get_base_command('test')
        self.assertTrue(base_command == 'test')

    def test_get_base_command_with_args(self):
        base_command = self.bot._get_base_command('test <one>')
        self.assertTrue(base_command == 'test')


class TestGetCommandMatch(TestPhialBot):
    '''Test phial's get_command_match function'''

    def test_basic_functionality(self):
        self.bot.commands = [(re.compile('^test$'), 'test')]
        command_pattern, base_command = self.bot.get_command_match('test')
        self.assertTrue(command_pattern == {})
        self.assertTrue(base_command == 'test')

    def test_single_substition_matching(self):
        self.bot.commands = [(re.compile('^test (?P<one>.+)$'), 'test')]
        args, base_command = self.bot.get_command_match('test first')
        self.assertTrue(args == {'one': 'first'})
        self.assertTrue(base_command == 'test')

    def test_multi_substition_matching(self):
        self.bot.commands = [(re.compile('^test (?P<one>.+) (?P<two>.+)$'),
                             'test')]
        args, base_command = self.bot.get_command_match('test first second')
        self.assertTrue(args == {'one': 'first', 'two': 'second'})
        self.assertTrue(base_command == 'test')

    def test_returns_none_correctly(self):
        command_match = self.bot.get_command_match('test')
        self.assertTrue(command_match is None)


class TestCreateCommand(TestPhialBot):
    '''Test phial's create_command function'''

    def test_basic_functionality(self):
        self.bot.commands = [(re.compile('^test$'), 'test')]
        command = self.bot._create_command('test', 'channel_id')
        self.assertTrue(command.base_command == 'test')
        self.assertTrue(command.channel == 'channel_id')

    def test_basic_functionality_with_args(self):
        self.bot.commands = [(re.compile('^test (?P<one>.+)$'), 'test')]
        command = self.bot._create_command('test first', 'channel_id')
        self.assertTrue(command.base_command == 'test')
        self.assertTrue(command.channel == 'channel_id')
        self.assertTrue(command.args == {'one': 'first'})

    def test_errors_when_no_command_match(self):
        with self.assertRaises(ValueError) as context:
            self.bot._create_command('test', 'channel_id')
        self.assertTrue('Command "test" has not been registered'
                        in str(context.exception))


class TestHandleCommand(TestPhialBot):
    '''Test phial's handle_command function'''

    def test_handle_command_basic_functionality(self):

        test_func = MagicMock()
        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Command('test', 'channel_id', {})
        self.bot._handle_command(command_instance)

        self.assertTrue(test_func.called)

    def test_command_context_works_correctly(self):
        def test_func():
            self.assertTrue(command.base_command == 'test')
            self.assertTrue(command.channel == 'channel_id')
            self.assertTrue(command.args == {})

        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Command('test', 'channel_id', {})
        self.bot._handle_command(command_instance)

    def test_command_context_pops_correctly(self):
        def test_func():
            pass

        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Command('test', 'channel_id', {})
        self.bot._handle_command(command_instance)

        with self.assertRaises(RuntimeError) as context:
            print(command)
        self.assertTrue('Not in a context with a command'
                        in str(context.exception))


class TestParseSlackOutput(TestPhialBot):

    def test_basic_functionality(self):
        sample_slack_output = [{'text': '!test', 'channel': 'channel_id'}]
        command, channel = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(command == 'test')
        self.assertTrue(channel == 'channel_id')

    def test_returns_none_correctly_for_normal_message(self):
        sample_slack_output = [{'text': 'test', 'channel': 'channel_id'}]
        command, channel = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(command is None)
        self.assertTrue(channel is None)

    def test_returns_none_correctly_if_no_messages(self):
        sample_slack_output = []
        command, channel = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(command is None)
        self.assertTrue(channel is None)


class TestSendMessage(TestPhialBot):
    '''Test phial's send_message function'''

    def test_basic_functionality(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock(return_value="test")
        message = Message(text='Hi test', channel='channel_id')
        self.bot.send_message(message)

        self.bot.slack_client.api_call.assert_called_with('chat.postMessage',
                                                          channel='channel_id',
                                                          text='Hi test',
                                                          as_user=True)


class TestExecuteResponse(TestPhialBot):
    '''Test phial's execute_response function'''

    def test_basic_functionality(self):
        self.bot.send_message = MagicMock()
        message = Message(text='Hi test', channel='channel_id')
        self.bot._execute_response(message)
        self.bot.send_message.assert_called_with(message)


class TestRun(TestPhialBot):
    '''Test phial's run function'''

    def test_basic_functionality(self):
        def test_func():
            pass
        self.bot.add_command('test', test_func)

        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        command = 'test'
        channel = 'channel_id'
        self.bot._parse_slack_output = MagicMock(return_value=(command,
                                                               channel))
        test_command = phial.wrappers.Command('test', 'channel_id', {})
        self.bot._create_command = MagicMock(return_value=test_command)
        self.bot._handle_command = MagicMock()

        self.bot.run()
        self.bot.slack_client.rtm_connect.assert_called_once()
        self.bot._parse_slack_output.assert_called_once()
        self.bot._create_command.assert_called_with(command, channel)
        self.bot._handle_command.assert_called_with(test_command)

    def test_errors_with_invalid_token(self):
        with self.assertRaises(ValueError) as context:
            self.bot.run()
        self.assertTrue('Connection failed. Invalid Token or bot ID'
                        in str(context.exception))

    def test_errors_with_invald_error(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        command = 'test'
        channel = 'channel_id'
        self.bot._parse_slack_output = MagicMock(return_value=(command,
                                                               channel))
        with captured_output() as (out, err):
            self.bot.run()

        output = out.getvalue().strip()
        expected_message = 'ValueError: Command "test" has not been registered'
        self.assertTrue(expected_message in output)
