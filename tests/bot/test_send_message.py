import slackclient  # type: ignore
from phial import Phial, Response
from typing import Any
from tests.helpers import wildpatch


def test_send_message(monkeypatch: Any) -> None:
    def mock_api_call(*args: Any, **kwargs: Any) -> None:
        assert args[1] == "chat.postMessage"
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"

    wildpatch(slackclient.SlackClient, 'api_call', mock_api_call)

    response = Response("channel", "message")
    bot = Phial('token')

    bot.send_message(response)


def test_send_full_message(monkeypatch: Any) -> None:
    def mock_api_call(*args: Any, **kwargs: Any) -> None:
        assert args[1] == "chat.postMessage"
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"
        assert kwargs["user"] == "user"
        assert type(kwargs["attachments"]) is str  # Serialised to JSON

        assert "reaction" not in kwargs

    wildpatch(slackclient.SlackClient, 'api_call', mock_api_call)

    response = Response("channel", "message",
                        original_ts='orig_time',
                        reaction='reaction',
                        ephemeral=False,
                        user='user',
                        attachments={"foo": "bar"})
    bot = Phial('token')

    bot.send_message(response)


def test_send_ephemeral_message(monkeypatch: Any) -> None:
    def mock_api_call(*args: Any, **kwargs: Any) -> None:
        assert args[1] == "chat.postEphemeral"
        assert kwargs["channel"] == "channel"
        assert kwargs["text"] == "message"
        assert kwargs["user"] == "user"
        assert type(kwargs["attachments"]) is str  # Serialised to JSON

        assert "reaction" not in kwargs

    wildpatch(slackclient.SlackClient, 'api_call', mock_api_call)

    response = Response("channel", "message",
                        original_ts='orig_time',
                        reaction='reaction',
                        ephemeral=True,
                        user='user',
                        attachments={"foo": "bar"})
    bot = Phial('token')

    bot.send_message(response)
