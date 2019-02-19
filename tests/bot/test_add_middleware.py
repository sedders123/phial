from phial import Phial, Message


def test_add_middleware_command() -> None:
    def test(message: Message) -> None:
        pass

    bot = Phial('token', {})
    bot.add_middleware(test)

    assert len(bot.middleware_functions) == 1
    assert bot.middleware_functions[0] is test


def test_add_middleware_decorator() -> None:
    bot = Phial('token', {})

    @bot.middleware()
    def test(message: Message) -> None:
        pass

    assert len(bot.middleware_functions) == 1
    assert bot.middleware_functions[0] is test
