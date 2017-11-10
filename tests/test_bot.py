import unittest
from unittest.mock import MagicMock, mock_open
from phial import Phial, command, Response, Attachment, g
import phial.wrappers
import phial.globals
import re
from .helpers import captured_output, MockTrueFunc


class TestPhialBotIsRunning(unittest.TestCase):
    '''Tests for phial's _is_running function'''

    def test_returns_expected_value(self):
        bot = Phial('test-token')
        self.assertFalse(bot._is_running())


class TestPhialBot(unittest.TestCase):

    def setUp(self):
        self.bot = Phial('test-token')
        self.bot._is_running = MockTrueFunc()

    def tearDown(self):
        self.bot = None
        phial.globals._global_ctx_stack.pop()
        phial.globals._command_ctx_stack.pop()


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
        command_message = phial.wrappers.Message('test',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        command = self.bot._create_command(command_message)
        expected_command = phial.wrappers.Command('test',
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  command_message)
        self.assertEquals(command, expected_command)

    def test_basic_functionality_with_args(self):
        self.bot.commands = [(re.compile('^test (?P<one>.+)$'), 'test')]
        command_message = phial.wrappers.Message('test first',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        command = self.bot._create_command(command_message)
        expected_command = phial.wrappers.Command('test',
                                                  'channel_id',
                                                  {'one': 'first'},
                                                  'user',
                                                  command_message)
        self.assertEquals(command, expected_command)

    def test_errors_when_no_command_match(self):
        with self.assertRaises(ValueError) as context:
            command_message = phial.wrappers.Message('test',
                                                     'channel_id',
                                                     'user',
                                                     'timestamp')
            self.bot._create_command(command_message)
        self.assertTrue('Command "test" has not been registered'
                        in str(context.exception))


class TestHandleCommand(TestPhialBot):
    '''Test phial's handle_command function'''

    def test_handle_command_basic_functionality(self):

        test_func = MagicMock()
        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Command('test',
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  'timestamp')
        self.bot._handle_command(command_instance)

        self.assertTrue(test_func.called)


class TestCommandContextWorksCorrectly(TestPhialBot):

    def test_command_context_works_correctly(self):
        def test_func():
            self.assertTrue(command.base_command == 'test')
            self.assertTrue(command.channel == 'channel_id')
            self.assertTrue(command.args == {})

        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Command('test',
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  'timestamp')
        self.bot._handle_command(command_instance)

    def test_command_context_pops_correctly(self):
        def test_func():
            pass

        self.bot.add_command('test', test_func)
        command_instance = phial.wrappers.Message('!test',
                                                  'channel_id',
                                                  'user',
                                                  'timestamp')
        self.bot._handle_message(command_instance)

        with self.assertRaises(RuntimeError) as context:
            print(command)
        self.assertTrue('Not in a context with a command'
                        in str(context.exception))


class TestParseSlackOutput(TestPhialBot):

    def test_basic_functionality(self):
        sample_slack_output = [{
                                'text': '!test',
                                'channel': 'channel_id',
                                'user': 'user_id',
                                'ts': 'timestamp'
                               }]
        command_message = self.bot._parse_slack_output(sample_slack_output)
        expected_command_message = phial.wrappers.Message('!test',
                                                          'channel_id',
                                                          'user_id',
                                                          'timestamp')
        self.assertEquals(command_message, expected_command_message)

    def test_returns_message_correctly_for_normal_message(self):
        sample_slack_output = [{'text': 'test', 'channel': 'channel_id',
                                'user': 'user', 'ts': 'timestamp'}]
        command_message = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(type(command_message) is phial.wrappers.Message)

    def test_returns_none_correctly_if_no_messages(self):
        sample_slack_output = []
        command_message = self.bot._parse_slack_output(sample_slack_output)
        self.assertTrue(command_message is None)


class TestSendMessage(TestPhialBot):
    '''Test phial's send_message function'''

    def test_send_message(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock(return_value="test")
        message = Response(text='Hi test', channel='channel_id')
        self.bot.send_message(message)

        self.bot.slack_client.api_call.assert_called_with('chat.postMessage',
                                                          channel='channel_id',
                                                          text='Hi test',
                                                          as_user=True)

    def test_send_reply(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock(return_value="test")
        message = Response(text='Hi test',
                           channel='channel_id',
                           original_ts='timestamp')
        self.bot.send_message(message)

        self.bot.slack_client.api_call \
            .assert_called_with('chat.postMessage',
                                channel='channel_id',
                                text='Hi test',
                                thread_ts='timestamp',
                                as_user=True)


class TestSendReaction(TestPhialBot):
    '''Test phial's send_message function'''

    def test_basic_functionality(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock()

        response = Response(reaction='x',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot.send_reaction(response)

        self.bot.slack_client.api_call \
            .assert_called_with("reactions.add",
                                channel=response.channel,
                                timestamp=response.original_ts,
                                name=response.reaction,
                                as_user=True)


class TestUploadAttachment(TestPhialBot):
    '''Test phial's upload_attachment function'''

    def test_basic_functionality(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.api_call = MagicMock()

        attachment = Attachment(channel='channel_id',
                                filename='test.txt',
                                content=mock_open())
        self.bot.upload_attachment(attachment)

        self.bot.slack_client.api_call \
            .assert_called_with("files.upload",
                                channels=attachment.channel,
                                filename=attachment.filename,
                                file=attachment.content)


class TestExecuteResponse(TestPhialBot):
    '''Test phial's execute_response function'''

    def test_send_string(self):
        self.bot.send_message = MagicMock()
        command_instance = phial.wrappers.Command(base_command="base",
                                                  channel="channel_id",
                                                  args={},
                                                  user="user",
                                                  message={})
        phial.globals._command_ctx_stack.push(command_instance)
        self.bot._execute_response("string")
        expected_response = Response(text='string', channel='channel_id')
        self.bot.send_message.assert_called_with(expected_response)
        phial.globals._command_ctx_stack.pop()

    def test_send_message(self):
        self.bot.send_message = MagicMock()
        response = Response(text='Hi test', channel='channel_id')
        self.bot._execute_response(response)
        self.bot.send_message.assert_called_with(response)

    def test_send_reply(self):
        self.bot.send_message = MagicMock()
        response = Response(text='Hi test',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot._execute_response(response)
        self.bot.send_message.assert_called_with(response)

    def test_send_reaction(self):
        self.bot.send_reaction = MagicMock()
        response = Response(reaction='x',
                            channel='channel_id',
                            original_ts='timestamp')
        self.bot._execute_response(response)
        self.bot.send_reaction.assert_called_with(response)

    def test_upload_attachment(self):
        self.bot.upload_attachment = MagicMock()
        attachment = Attachment(channel='channel_id',
                                filename='test.txt',
                                content=mock_open())
        self.bot._execute_response(attachment)
        self.bot.upload_attachment.assert_called_with(attachment)

    def test_errors_on_invalid_response(self):
        with self.assertRaises(ValueError) as context:
            self.bot._execute_response([])
        error_msg = 'Only Response or Attachment objects can be returned ' \
                    + 'from command functions'
        self.assertTrue(error_msg in str(context.exception))

    def test_errors_with_invalid_attachment(self):
        attachment = Attachment(channel="channel_id",
                                filename="test_file.txt")
        with self.assertRaises(ValueError) as context:
            self.bot._execute_response(attachment)
        error_msg = 'The content field of Attachment objects must be set'
        self.assertTrue(error_msg in str(context.exception))

    def test_errors_with_reaction_and_reply(self):
        response = Response(reaction='x',
                            text='test',
                            channel='channel_id',
                            original_ts='timestamp')

        with self.assertRaises(ValueError) as context:
            self.bot._execute_response(response)

        error_msg = 'Response objects with an original timestamp can ' \
                    + 'only have one of the attributes: Reaction, ' \
                    + 'Text'
        self.assertTrue(error_msg in str(context.exception))


class TestMiddleware(TestPhialBot):
    '''Test phial's middleware'''

    def test_decarator(self):
        @self.bot.middleware()
        def middleware_test(message):
            return message

        self.assertTrue(middleware_test in self.bot.middleware_functions)

    def test_add_function(self):
        def middleware_test(message):
            return message
        self.bot.add_middleware(middleware_test)
        self.assertTrue(middleware_test in self.bot.middleware_functions)

    def test_halts_message_when_none_returned(self):
        middleware_test = MagicMock(return_value=None)
        self.bot.add_middleware(middleware_test)
        test = MagicMock()
        self.bot.add_command('test', test)
        message = phial.wrappers.Message('!test',
                                         'channel_id',
                                         'user',
                                         'timestamp')
        self.bot._handle_message(message)
        middleware_test.assert_called_once_with(message)
        test.assert_not_called()

    def test_passes_on_message_correctly(self):
        message = phial.wrappers.Message('!test',
                                         'channel_id',
                                         'user',
                                         'timestamp')
        middleware_test = MagicMock(return_value=message)
        self.bot.add_middleware(middleware_test)
        test = MagicMock()
        self.bot.add_command('test', test)
        self.bot._handle_message(message)
        middleware_test.assert_called_once_with(message)
        test.assert_called_once()


class TestRun(TestPhialBot):
    '''Test phial's run function'''

    def test_basic_functionality(self):
        def test_func():
            pass
        self.bot.add_command('test', test_func)

        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        command_message = phial.wrappers.Message('test',
                                                 'channel_id',
                                                 'user',
                                                 'timestamp')
        self.bot._parse_slack_output = MagicMock(return_value=command_message)
        test_command = phial.wrappers.Command('test',
                                              'channel_id',
                                              {},
                                              'user_id',
                                              'timestamp')
        self.bot._create_command = MagicMock(return_value=test_command)
        self.bot._handle_command = MagicMock()

        self.bot.run()
        self.bot.slack_client.rtm_connect.assert_called_once()
        self.bot._parse_slack_output.assert_called_once()
        self.bot._create_command.assert_called_with(command_message)
        self.bot._handle_command.assert_called_with(test_command)

    def test_errors_with_invalid_token(self):
        with self.assertRaises(ValueError) as context:
            self.bot.run()
        self.assertTrue('Connection failed. Invalid Token or bot ID'
                        in str(context.exception))

    def test_errors_with_invalid_command(self):
        self.bot.slack_client = MagicMock()
        self.bot.slack_client.rtm_connect = MagicMock(return_value=True)
        test_command = phial.wrappers.Message('test',
                                              'channel_id',
                                              'user_id',
                                              'timestamp')
        self.bot._parse_slack_output = MagicMock(return_value=test_command)
        with captured_output() as (out, err):
            self.bot.run()

        output = out.getvalue().strip()
        expected_message = 'ValueError: Command "test" has not been registered'
        self.assertTrue(expected_message in output)


class TestGlobalContext(unittest.TestCase):

    def test_global_context_in_command(self):
        bot = Phial('test-token')

        def command_function():
            g['test'] = "test value"

        def second_command_function():
            self.assertEquals(g['test'], "test value")

        bot.add_command('test', command_function)
        command_instance = phial.wrappers.Command('test',
                                                  'channel_id',
                                                  {},
                                                  'user',
                                                  'timestamp')
        bot.add_command('test2', second_command_function)
        second_command_instance = phial.wrappers.Command('test2',
                                                         'channel_id',
                                                         {},
                                                         'user',
                                                         'timestamp')
        bot._handle_command(command_instance)
        bot._handle_command(second_command_instance)

    def test_global_context_fails_outside_app_context(self):
        with self.assertRaises(RuntimeError) as context:
            print(g)
        self.assertTrue('Working outside the app context'
                        in str(context.exception))
