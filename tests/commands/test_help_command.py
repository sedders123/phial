from phial import Phial
from phial.commands import help_command


def test_returns_help_string_correctly() -> None:
    bot = Phial('token')

    @bot.command("test")
    def test() -> None:
        """help"""

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n*!test* - help\n")

    assert help_text == expected_help_text


def test_returns_help_string_correctly_when_no_help_text() -> None:
    bot = Phial('token')

    @bot.command("test")
    def test() -> None:
        pass

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n*!test* - \n")

    assert help_text == expected_help_text


def test_returns_help_string_correctly_when_no_base() -> None:
    bot = Phial('token', {})

    @bot.command("test")
    def test() -> None:
        """help"""

    help_text = help_command(bot)
    expected_help_text = ("*test* - help\n")
    assert help_text == expected_help_text
