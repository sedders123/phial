from phial import Phial, Message


def test_add_fallback_command() -> None:
    def test(message: Message) -> None:
        pass

    bot = Phial('token', {})
    bot.add_fallback_command(test)

    assert bot.fallback_func is not None
    assert bot.fallback_func is test


def test_add_fallback_decorator() -> None:
    bot = Phial('token', {})

    @bot.fallback_command()
    def test(message: Message) -> None:
        pass

    assert bot.fallback_func is not None
    assert bot.fallback_func is test
