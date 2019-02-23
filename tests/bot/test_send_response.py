from phial import Phial, Response, Attachment
from tests.helpers import wildpatch
import pytest  # type: ignore
import io


def test_send_response_string() -> None:
    def mock_send_message(instance: Phial, response: Response) -> None:
        assert response.text == "test"
        assert response.channel == "channel"

    bot = Phial('token')
    wildpatch(Phial, 'send_message', mock_send_message)

    bot._send_response("test", "channel")


def test_send_response_with_none() -> None:
    bot = Phial('token')

    bot._send_response(None, "channel")


def test_send_response_fails_with_non_response_object() -> None:
    bot = Phial('token')

    with pytest.raises(ValueError):
        bot._send_response(True, "channel")  # type: ignore


def test_send_response() -> None:
    expected_response = Response("channel", "message",
                                 original_ts='orig_time',
                                 ephemeral=False,
                                 user='user',
                                 attachments={"foo": "bar"})

    def mock_send_message(instance: Phial, response: Response) -> None:
        assert response == expected_response

    bot = Phial('token')
    wildpatch(Phial, 'send_message', mock_send_message)

    bot._send_response(expected_response, "channel")


def test_send_response_fails_with_text_and_reaction() -> None:
    expected_response = Response("channel",
                                 "message",
                                 original_ts='orig_time',
                                 reaction="reaction")

    def mock_send_message(instance: Phial, response: Response) -> None:
        assert response == expected_response

    bot = Phial('token')
    wildpatch(Phial, 'send_message', mock_send_message)
    with pytest.raises(ValueError):
        bot._send_response(expected_response, "channel")


def test_send_response_with_attachment() -> None:
    def mock_send_attachment(instance: Phial, response: Attachment) -> None:
        assert response.channel == "channel"
        assert response.filename == "file_name"
    bot = Phial('token')
    wildpatch(Phial, 'upload_attachment', mock_send_attachment)

    output = io.StringIO()
    output.write('content')

    attachment = Attachment("channel", "file_name", output)
    bot._send_response(attachment, "channel")


def test_send_response_reaction() -> None:
    expected_response = Response("channel",
                                 original_ts='orig_time',
                                 reaction="reaction")

    def mock_send_reaction(instance: Phial, response: Response) -> None:
        assert response == expected_response

    bot = Phial('token')
    wildpatch(Phial, 'send_reaction', mock_send_reaction)

    bot._send_response(expected_response, "channel")
