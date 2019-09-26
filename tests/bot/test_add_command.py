"""Test ad_command."""
import pytest

from phial import Phial


def test_add_command() -> None:
    """Test add_command works correctly."""

    def test() -> None:
        pass

    bot = Phial("token", {"registerHelpCommand": False})
    bot.add_command("test", test)

    assert len(bot.commands) == 1
    assert bot.commands[0].func is test


def test_add_same_command_throws() -> None:
    """Test add_command throws when adding command with same pattern."""

    def test() -> None:
        pass

    bot = Phial("token", {"registerHelpCommand": False})
    bot.add_command("test", test)

    with pytest.raises(ValueError):
        bot.add_command("test", test)


def test_add_command_decorator() -> None:
    """Test add_command decorator works correctly."""
    bot = Phial("token", {"registerHelpCommand": False})

    @bot.command("test")
    def test() -> None:
        pass

    assert len(bot.commands) == 1
    assert bot.commands[0].func is test


def test_alias_decorator() -> None:
    """Test alias decorator works correctly."""
    bot = Phial("token", {"registerHelpCommand": False})

    @bot.command("test")
    @bot.alias("test2")
    def test() -> None:
        pass

    assert len(bot.commands) == 1
    assert len(bot.commands[0].alias_patterns) == 1
