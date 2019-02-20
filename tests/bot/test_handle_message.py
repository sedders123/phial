from phial import Phial, Message


def test_handle_message_handles_none_correctly() -> None:
    def command() -> None:
        raise Exception("Should not be called")

    def middleware(message: Message) -> None:
        raise Exception("Should not be called")

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot._handle_message(None)


def test_message_passed_to_middleware() -> None:
    def command() -> None:
        raise Exception("Should not be called")

    middleware_calls = [0]

    def middleware(message: Message) -> None:
        middleware_calls[0] += 1

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    message = Message('text', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1


def test_message_ignored_if_no_prefix() -> None:
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    message = Message('text', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 0


def test_message_calls_command_correctly() -> None:
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    message = Message('!test', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 1


def test_message_calls_command_correctly_when_no_prefix() -> None:
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial('token', {})
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    message = Message('test', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 1


def test_message_falls_back_correctly() -> None:
    middleware_calls = [0]
    command_calls = [0]
    fallback_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    def fallback() -> None:
        fallback_calls[0] += 1

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot.add_fallback(fallback)
    message = Message('!test-fallback', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 0
    assert fallback_calls[0] == 1
