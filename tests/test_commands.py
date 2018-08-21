import unittest
from unittest.mock import MagicMock
from phial.commands import help_command


class TestHelpCommand(unittest.TestCase):
    def test_help_command(self):
        bot = MagicMock()
        command = MagicMock()
        command._help = "Test description"
        bot.commands = {"test_pattern": command}
        bot.command_names = {"test_pattern": "test"}

        expected_help_text = "*test* - Test description\n"

        help_text = help_command(bot)
        self.assertEqual(help_text, expected_help_text)
