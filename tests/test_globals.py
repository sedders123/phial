"""Test globals."""

import pytest

from phial.globals import _command_ctx_stack, _find_command
from phial.wrappers import Message


def test_find_command_throws_when_no_command() -> None:
    """Test find_command errors correctly."""
    with pytest.raises(Exception) as e:
        _find_command()
    assert e is not None


def test_find_command_returns_command() -> None:
    """Test find_command returns correctly."""
    _command_ctx_stack.push(Message("text", "channel", "user", "ts", "team"))
    result = _find_command()
    assert result.text == "text"
    assert result.channel == "channel"
    assert result.user == "user"
    assert result.timestamp == "ts"
    assert result.team == "team"
