"""Test send_response."""

import io

import pytest

from phial import Attachment, Phial, Response


def test_send_response_string() -> None:
    """Test send_response works with a string."""

    def mock_send_message(response: Response) -> None:
        assert response.text == "test"
        assert response.channel == "channel"

    bot = Phial("app-token", "bot-token")
    bot.send_message = mock_send_message  # type: ignore

    bot._send_response("test", "channel")


def test_send_response_with_none() -> None:
    """Test send_response works with None."""
    bot = Phial("app-token", "bot-token")

    bot._send_response(None, "channel")


def test_send_response_fails_with_non_response_object() -> None:
    """Test send_response fails with an invalid type."""
    bot = Phial("app-token", "bot-token")

    with pytest.raises(ValueError):
        bot._send_response(True, "channel")  # type: ignore  # noqa: FBT003


def test_send_response() -> None:
    """Test send_response works with response."""
    expected_response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        ephemeral=False,
        user="user",
        attachments=[{"foo": "bar"}],
    )

    def mock_send_message(response: Response) -> None:
        assert response == expected_response

    bot = Phial("app-token", "bot-token")
    bot.send_message = mock_send_message  # type: ignore

    bot._send_response(expected_response, "channel")


def test_send_response_fails_with_text_and_reaction() -> None:
    """Test send_response fails when a response has both text and reaction."""
    expected_response = Response(
        "channel",
        text="message",
        original_ts="orig_time",
        reaction="reaction",
    )

    def mock_send_message(response: Response) -> None:
        assert response == expected_response

    bot = Phial("app-token", "bot-token")
    bot.send_message = mock_send_message  # type: ignore
    with pytest.raises(ValueError):
        bot._send_response(expected_response, "channel")


def test_send_response_with_attachment() -> None:
    """Test send_response works with an Attachment."""

    def mock_send_attachment(response: Attachment) -> None:
        assert response.channel == "channel"
        assert response.filename == "file_name"

    bot = Phial("app-token", "bot-token")
    bot.upload_attachment = mock_send_attachment  # type: ignore

    output = io.StringIO()
    output.write("content")

    attachment = Attachment("channel", "file_name", output)
    bot._send_response(attachment, "channel")


def test_send_response_reaction() -> None:
    """Test send_response works with an reaction."""
    expected_response = Response(
        "channel",
        original_ts="orig_time",
        reaction="reaction",
    )

    def mock_send_reaction(response: Response) -> None:
        assert response == expected_response

    bot = Phial("app-token", "bot-token")
    bot.send_reaction = mock_send_reaction  # type: ignore

    bot._send_response(expected_response, "channel")
