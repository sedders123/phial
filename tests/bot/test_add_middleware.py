"""Test add_middleware."""

from phial import Message, Phial


def test_add_middleware_command() -> None:
    """Test add_middleware commmand works correctly."""

    def test(message: Message) -> None:
        pass

    bot = Phial("app-token", "bot-token", {})
    bot.add_middleware(test)

    assert len(bot.middleware_functions) == 1
    assert bot.middleware_functions[0] is test


def test_add_middleware_decorator() -> None:
    """Test add_middleware decorator works correctly."""
    bot = Phial("app-token", "bot-token", {})

    @bot.middleware()
    def test(message: Message) -> None:
        pass

    assert len(bot.middleware_functions) == 1
    assert bot.middleware_functions[0] is test
