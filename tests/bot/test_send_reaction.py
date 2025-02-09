"""Test send_reaction."""

from typing import Any

import pytest
import slack_sdk

from phial import Phial, Response
from tests.helpers import wildpatch


def test_send_reaction() -> None:
    """Test send_reaction."""

    def mock_api_call(*_: Any, **kwargs: Any) -> None:
        assert kwargs["channel"] == "channel"
        assert kwargs["name"] == "reaction"
        assert kwargs["timestamp"] == "orig_time"

        assert "text" not in kwargs
        assert "user" not in kwargs
        assert "attachments" not in kwargs

    wildpatch(slack_sdk.WebClient, "reactions_add", mock_api_call)

    response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        reaction="reaction",
        ephemeral=False,
        user="user",
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")

    bot.send_reaction(response)


def test_send_reaction_throws_if_no_timestamp() -> Any:
    """Test send_reaction throws if no timestamp."""
    response = Response(
        "channel",
        text="message",
        reaction="reaction",
        ephemeral=False,
        user="user",
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")

    with pytest.raises(ValueError):
        bot.send_reaction(response)


def test_send_reaction_throws_if_no_reaction() -> Any:
    """Test send_reaction throws if no reaction."""
    response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        ephemeral=False,
        user="user",
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("app-token", "bot-token")

    with pytest.raises(ValueError):
        bot.send_reaction(response)
