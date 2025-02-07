"""Test Attachment class."""

import io

from phial import Attachment


def test_attachment_repr() -> None:
    """Test attachment repr."""
    attachment = Attachment("channel", "file_name", io.StringIO())

    assert repr(attachment) == "<Attachment file_name in channel>"
