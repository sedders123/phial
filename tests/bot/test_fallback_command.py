from phial import Phial


def test_add_fallback_command() -> None:
    def test() -> None:
        pass

    bot = Phial('token', {})
    bot.add_fallback_command(test)

    assert bot.fallback_func is not None
    assert bot.fallback_func is test


def test_add_fallback_decorator() -> None:
    bot = Phial('token', {})

    @bot.fallback_command()
    def test() -> None:
        pass

    assert bot.fallback_func is not None
    assert bot.fallback_func is test
