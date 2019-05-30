"""Test help command."""
from phial import Phial
from phial.commands import help_command


def test_returns_help_string_correctly() -> None:
    """Test returns help text correctly."""
    bot = Phial('token')

    @bot.command("test")
    def test() -> None:
        """help."""

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n*!test* - help.\n")

    assert help_text == expected_help_text


def test_returns_help_string_correctly_when_no_help_text() -> None:
    """Test returns help text correctly when none set."""
    bot = Phial('token')

    @bot.command("test")
    def test() -> None:
        pass

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n*!test* - \n")

    assert help_text == expected_help_text


def test_hide_from_help_command_hides_correctly() -> None:
    """Test returns help text correctly when none set."""
    bot = Phial('token')

    @bot.command("test", hide_from_help_command=True)
    def test() -> None:
        pass

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n")

    assert help_text == expected_help_text


def test_help_text_override_overrides_correctly() -> None:
    """Test returns help text correctly when none set."""
    bot = Phial('token')

    @bot.command("test", help_text_override="Override")
    def test() -> None:
        """Not this."""
        pass

    help_text = help_command(bot)
    expected_help_text = ("All available commands:\n*!help* - List all"
                          " available commmands\n*!test* - Override\n")

    assert help_text == expected_help_text


def test_returns_help_string_correctly_when_no_base() -> None:
    """Test returns help text correctly when no base."""
    bot = Phial('token', {'registerHelpCommand': False,
                          'baseHelpText': '', 'prefix': ''})

    @bot.command("test")
    def test() -> None:
        """help."""

    help_text = help_command(bot)
    expected_help_text = "*test* - help.\n"
    assert help_text == expected_help_text
