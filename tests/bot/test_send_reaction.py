"""Test send_reaction."""
from typing import Any

import slackclient  # type: ignore

from phial import Phial, Response
from tests.helpers import wildpatch


def test_send_reaction(monkeypatch: Any) -> None:
    """Test send_reaction."""

    def mock_api_call(*args: Any, **kwargs: Any) -> None:
        assert args[1] == "reactions.add"
        assert kwargs["channel"] == "channel"
        assert kwargs["name"] == "reaction"
        assert kwargs["timestamp"] == "orig_time"

        assert "text" not in kwargs
        assert "user" not in kwargs
        assert "attachments" not in kwargs

    wildpatch(slackclient.SlackClient, "api_call", mock_api_call)

    response = Response(
        "channel",
        "message",
        original_ts="orig_time",
        reaction="reaction",
        ephemeral=False,
        user="user",
        attachments=[{"foo": "bar"}],
    )
    bot = Phial("token")

    bot.send_reaction(response)
