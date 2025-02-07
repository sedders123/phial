"""Test Response class."""

from phial import Response


def test_response_equality() -> None:
    """Assert Response equality is working."""
    response_one = Response("channel", "text", "ts", "reaction", True, "user")
    response_two = Response("channel", "text", "ts", "reaction", True, "user")

    assert response_one == response_two


def test_response_equality_attachment() -> None:
    """Assert Response equality is working with attachments."""
    response_one = Response(
        "channel", "text", "ts", "reaction", True, "user", [{"foo": "bar"}]
    )
    response_two = Response(
        "channel", "text", "ts", "reaction", True, "user", [{"foo": "bar"}]
    )

    assert response_one == response_two


def test_response_equality_attachment_fails() -> None:
    """Assert Response equality fails with attachments."""
    response_one = Response(
        "channel", "text", "ts", "reaction", True, "user", [{"foo": "bar"}]
    )
    response_two = Response(
        "channel", "text", "ts", "reaction", True, "user", [{"foo": "test"}]
    )

    assert response_one != response_two


def test_response_repr() -> None:
    """Assert Response repr is working."""
    response = Response(
        "channel", "text", "ts", "reaction", True, "user", [{"foo": "bar"}]
    )

    assert repr(response) == "<Response: text>"
