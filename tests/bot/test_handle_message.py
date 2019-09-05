"""Test handle_message."""
import pytest

from phial import Message, Phial
from phial.errors import ArgumentValidationError


def test_handle_message_handles_none_correctly() -> None:
    """Test handle_message handle None correctly."""
    def command() -> None:
        raise Exception("Should not be called")

    def middleware(message: Message) -> None:
        raise Exception("Should not be called")

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot._handle_message(None)


def test_message_passed_to_middleware() -> None:
    """Test handle_message passes to middleware."""
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
    """Test message is ignored if it has no prefix."""
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
    """Test message invokes a command correctly."""
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
    """Test message invokes a command correctly with no prefix."""
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial('token', {'prefix': ''})
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    message = Message('test', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 1


def test_message_falls_back_correctly() -> None:
    """Test message hits fallback command correctly."""
    middleware_calls = [0]
    command_calls = [0]
    fallback_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    def fallback(message: Message) -> None:
        fallback_calls[0] += 1

    bot = Phial('token')
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot.add_fallback_command(fallback)
    message = Message('!test-fallback', 'channel', 'user', 'timestamp', 'team')
    bot._handle_message(message)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 0
    assert fallback_calls[0] == 1


def test_type_validation_works_correctly() -> None:
    """Test type validation works correctly."""
    command_calls = [0]

    def command(name: str) -> None:
        command_calls[0] += 1

    bot = Phial('token')
    bot.add_command("test", command)
    message = Message('!test', 'channel', 'user', 'timestamp', 'team')
    with pytest.raises(ArgumentValidationError):
        bot._handle_message(message)
    assert command_calls[0] == 0
