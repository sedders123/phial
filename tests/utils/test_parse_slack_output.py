"""Test parse_slack_output."""
from typing import Dict, List

from phial.utils import parse_slack_output


def test_parse_slack_output() -> None:
    """Test returns Message correctly."""
    sample_input = [
        {
            "text": "test",
            "channel": "channel",
            "user": "user",
            "ts": "ts",
            "team": "team",
        }
    ]
    output = parse_slack_output(sample_input)
    assert output is not None
    assert output.channel == "channel"
    assert output.team == "team"
    assert output.text == "test"
    assert output.timestamp == "ts"
    assert output.team == "team"
    assert output.bot_id is None


def test_parse_slack_output_bot() -> None:
    """Test returns bot Message correctly."""
    sample_input = [
        {
            "text": "test",
            "channel": "channel",
            "user": "user",
            "ts": "ts",
            "team": "team",
            "bot_id": "bot",
        }
    ]
    output = parse_slack_output(sample_input)
    assert output is not None
    assert output.channel == "channel"
    assert output.team == "team"
    assert output.text == "test"
    assert output.timestamp == "ts"
    assert output.team == "team"
    assert output.bot_id == "bot"


def test_parse_slack_output_returns_none_on_empty_input() -> None:
    """Check returns None when no messages passed in."""
    sample_input: List[Dict[str, str]] = []
    output = parse_slack_output(sample_input)
    assert output is None
