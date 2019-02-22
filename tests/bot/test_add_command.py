from phial import Phial
import pytest  # type: ignore


def test_add_command() -> None:
    def test() -> None:
        pass

    bot = Phial('token', {'registerHelpCommand': False})
    bot.add_command("test", test)

    assert len(bot.commands) == 1
    assert bot.commands[0].func is test


def test_add_same_command_throws() -> None:
    def test() -> None:
        pass

    bot = Phial('token', {'registerHelpCommand': False})
    bot.add_command("test", test)

    with pytest.raises(ValueError):
        bot.add_command("test", test)


def test_add_command_decorator() -> None:
    bot = Phial('token', {'registerHelpCommand': False})

    @bot.command("test")
    def test() -> None:
        pass

    assert len(bot.commands) == 1
    assert bot.commands[0].func is test


def test_alias_decorator() -> None:
    bot = Phial('token', {'registerHelpCommand': False})

    @bot.command("test")
    @bot.alias("test2")
    def test() -> None:
        pass

    assert len(bot.commands) == 1
    assert len(bot.commands[0].alias_patterns) == 1
