"""Test handle_request."""

from typing import Any, cast

from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from phial import Message, Phial


class MockClient:
    """Mock client for testing."""

    def send_socket_mode_response(self, *args: Any, **kwargs: Any) -> None:
        """Mock send_socket_mode_response."""


def build_request(
    text: str,
    channel: str,
    user: str,
    timestamp: str,
    team: str | None,
) -> SocketModeRequest:
    """Build a request for testing."""
    return SocketModeRequest(
        type="events_api",
        envelope_id="envelope_id",
        payload={
            "event": {
                "type": "message",
                "channel": channel,
                "user": user,
                "text": text,
                "ts": timestamp,
                "team": team,
            },
        },
    )


def test_handle_request_handles_none_correctly() -> None:
    """Test handle_request handle None correctly."""

    def command() -> None:
        raise Exception("Should not be called")

    def middleware(message: Message) -> None:
        raise Exception("Should not be called")

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot._handle_request(client, None)  # type: ignore


def test_request_passed_to_middleware() -> None:
    """Test handle_request passes to middleware."""

    def command() -> None:
        raise Exception("Should not be called")

    middleware_calls = [0]

    def middleware(message: Message) -> None:
        middleware_calls[0] += 1

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    request = build_request("text", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert middleware_calls[0] == 1


def test_requests_ignored_if_not_events_api_type() -> None:
    """Test handle_request ignores requests that are not events_api type."""

    def command() -> None:
        raise Exception("Should not be called")

    middleware_calls = [0]

    def middleware(message: Message) -> None:
        middleware_calls[0] += 1

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    request = build_request("text", "channel", "user", "timestamp", "team")
    request.type = "not_events_api"
    bot._handle_request(client, request)
    assert middleware_calls[0] == 0


def test_request_ignored_if_no_prefix() -> None:
    """Test message is ignored if it has no prefix."""
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    request = build_request("text", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 0


def test_request_calls_command_correctly() -> None:
    """Test message invokes a command correctly."""
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    request = build_request("!test", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 1


def test_request_calls_command_correctly_when_no_prefix() -> None:
    """Test message invokes a command correctly with no prefix."""
    middleware_calls = [0]
    command_calls = [0]

    def command() -> None:
        command_calls[0] += 1

    def middleware(message: Message) -> Message:
        middleware_calls[0] += 1
        return message

    bot = Phial("app-token", "bot-token", config={"prefix": ""})
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    request = build_request("test", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 1


def test_request_falls_back_correctly() -> None:
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

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    bot.add_middleware(middleware)
    bot.add_fallback_command(fallback)
    request = build_request("!test-fallback", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert middleware_calls[0] == 1
    assert command_calls[0] == 0
    assert fallback_calls[0] == 1


def test_argument_validation_works_correctly() -> None:
    """Test argument validation works correctly."""
    command_calls = [0]

    def command(name: str) -> None:
        command_calls[0] += 1

    def mock_send_response(response: str, channel: str) -> None:
        assert response == "Parameter name not provided to command"

    bot = Phial("app-token", "bot-token")
    bot._send_response = mock_send_response  # type: ignore
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test", command)
    request = build_request("!test", "channel", "user", "timestamp", "team")
    bot._handle_request_internal(client, request)
    assert command_calls[0] == 0


def test_argument_type_validation_works_correctly() -> None:
    """Test argument type validation works correctly."""
    command_calls = [0]

    def command(age: int) -> None:
        command_calls[0] += 1

    def mock_send_response(response: str, channel: str) -> None:
        assert response == "foo could not be converted to int"

    bot = Phial("app-token", "bot-token")
    bot._send_response = mock_send_response  # type: ignore
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test <age>", command)
    request = build_request("!test foo", "channel", "user", "timestamp", "team")
    bot._handle_request_internal(client, request)
    assert command_calls[0] == 0


def test_type_validation_works_correctly() -> None:
    """Test type validation works correctly."""
    command_calls = [0]

    def command(age: int) -> None:
        command_calls[0] += 1

    bot = Phial("app-token", "bot-token")
    client = cast(SocketModeClient, MockClient())
    bot.add_command("test <age>", command)
    request = build_request("!test string", "channel", "user", "timestamp", "team")
    bot._handle_request(client, request)
    assert command_calls[0] == 0
