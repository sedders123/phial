"""Test Response class."""

from phial import Response


def test_response_equality() -> None:
    """Assert Response equality is working."""
    response_one = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        ephemeral=True,
    )
    response_two = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        ephemeral=True,
    )

    assert response_one == response_two


def test_response_equality_attachment() -> None:
    """Assert Response equality is working with attachments."""
    response_one = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        attachments=[{"foo": "bar"}],
        ephemeral=True,
    )
    response_two = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        attachments=[{"foo": "bar"}],
        ephemeral=True,
    )

    assert response_one == response_two


def test_response_equality_attachment_fails() -> None:
    """Assert Response equality fails with attachments."""
    response_one = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        attachments=[{"foo": "bar"}],
        ephemeral=True,
    )
    response_two = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        attachments=[{"foo": "test"}],
        ephemeral=True,
    )

    assert response_one != response_two


def test_response_repr() -> None:
    """Assert Response repr is working."""
    response = Response(
        "channel",
        text="text",
        original_ts="ts",
        reaction="reaction",
        user="user",
        attachments=[{"foo": "bar"}],
        ephemeral=True,
    )

    assert repr(response) == "<Response: text>"
