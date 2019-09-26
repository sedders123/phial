"""Test fallback command."""
from phial import Message, Phial


def test_add_fallback_command() -> None:
    """Tes add_fallback_command works."""

    def test(message: Message) -> None:
        pass

    bot = Phial("token", {})
    bot.add_fallback_command(test)

    assert bot.fallback_func is not None
    assert bot.fallback_func is test


def test_add_fallback_decorator() -> None:
    """Tetst fallback_command decorator works."""
    bot = Phial("token", {})

    @bot.fallback_command()
    def test(message: Message) -> None:
        pass

    assert bot.fallback_func is not None
    assert bot.fallback_func is test
