"""Test upload_attachment."""
import io
from typing import Any

import slackclient  # type: ignore

from phial import Attachment, Phial
from tests.helpers import wildpatch


def test_send_attachment() -> None:
    """Test send attachments calls correctly."""

    def mock_api_call(*args: Any, **kwargs: Any) -> None:
        assert args[1] == "files.upload"
        assert kwargs["channels"] == "channel"
        assert kwargs["filename"] == "file_name"
        assert kwargs["file"].getvalue() == "content"

    wildpatch(slackclient.SlackClient, "api_call", mock_api_call)
    output = io.StringIO()
    output.write("content")
    attachment = Attachment("channel", "file_name", output)
    bot = Phial("token")

    bot.upload_attachment(attachment)
