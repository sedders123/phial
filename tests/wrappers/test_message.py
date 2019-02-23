"""Test Message class."""
from phial import Message


def test_message_equality() -> None:
    """Assert Message equality works."""
    message_one = Message('text',
                          'channel',
                          'user',
                          'timestamp',
                          'team',
                          'bot_id')
    message_two = Message('text',
                          'channel',
                          'user',
                          'timestamp',
                          'team',
                          'bot_id')

    assert message_one == message_two


def test_message_equality_fails() -> None:
    """Assert Message equality fails."""
    message_one = Message('text',
                          'channel',
                          'user',
                          'timestamp',
                          'team',
                          'bot_id')
    message_two = Message('text2',
                          'channel',
                          'user',
                          'timestamp',
                          'team',
                          'bot_id')

    assert message_one != message_two


def test_response_repr() -> None:
    """Assert Message repr works."""
    message = Message('text',
                      'channel',
                      'user',
                      'timestamp',
                      'team',
                      'bot_id')

    assert repr(message) == "<Message: text in channel:team at timestamp>"
