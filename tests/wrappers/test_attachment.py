from phial import Attachment
import io


def test_attachment_repr() -> None:
    attachment = Attachment('channel', 'file_name', io.StringIO())

    assert repr(attachment) == "<Attachment file_name in channel>"
