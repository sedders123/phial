from phial import Attachment


def test_attachment_repr() -> None:
    attachment = Attachment('channel', 'file_name')

    assert repr(attachment) == "<Attachment in channel>"
