"""Test send_message."""

from typing import Any

import pytest
import slack_sdk

from phial import Phial, Response
from tests.helpers import wildpatch


def test_send_message() -> None:
    """Test send_message works correctly."""

    def mock_api_call(*_: Any, **kwargs: Any) -> None:
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"
        assert kwargs["attachments"] == "null"
        assert kwargs["thread_ts"] is None

    wildpatch(slack_sdk.WebClient, "chat_postMessage", mock_api_call)

    response = Response("channel", text="message")
    bot = Phial("app-token", "bot-token")

    bot.send_message(response)


def test_send_full_message() -> None:
    """Test send message works correctly when all properties populated."""

    def mock_api_call(*_: Any, **kwargs: Any) -> None:
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"
        assert kwargs["thread_ts"] == "orig_time"
        assert type(kwargs["attachments"]) is str  # Serialised to JSON

        assert "reaction" not in kwargs

    wildpatch(slack_sdk.WebClient, "chat_postMessage", mock_api_call)

    response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        reaction="reaction",
        ephemeral=False,
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")

    bot.send_message(response)


def test_send_ephemeral_message() -> None:
    """Test sending ephemeral messages works."""

    def mock_api_call(*_: Any, **kwargs: Any) -> None:
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"
        assert kwargs["user"] == "user"
        assert type(kwargs["attachments"]) is str  # Serialised to JSON

        assert "reaction" not in kwargs

    wildpatch(slack_sdk.WebClient, "chat_postEphemeral", mock_api_call)

    response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        reaction="reaction",
        ephemeral=True,
        user="user",
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")

    bot.send_message(response)


def test_send_ephemeral_message_throws_with_no_user() -> None:
    """Test sending ephemeral throws when no user is specified."""
    response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        reaction="reaction",
        ephemeral=True,
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")
    with pytest.raises(ValueError):
        bot.send_message(response)
