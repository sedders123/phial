"""Test upload_attachment."""

import io
from typing import Any

import slack_sdk

from phial import Attachment, Phial
from tests.helpers import wildpatch


def test_send_attachment() -> None:
    """Test send attachments calls correctly."""

    def mock_api_call(*_: Any, **kwargs: Any) -> None:
        assert kwargs["channels"] == "channel"
        assert kwargs["filename"] == "file_name"
        assert kwargs["file"].getvalue() == "content"
        assert kwargs["title"] == "file_name"

    wildpatch(slack_sdk.WebClient, "files_upload_v2", mock_api_call)
    output = io.StringIO()
    output.write("content")
    attachment = Attachment("channel", "file_name", output)
    bot = Phial("app-token", "bot-token")

    bot.upload_attachment(attachment)
