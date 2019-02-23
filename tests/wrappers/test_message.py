from phial import Message


def test_message_equality() -> None:
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
    message = Message('text',
                      'channel',
                      'user',
                      'timestamp',
                      'team',
                      'bot_id')

    assert repr(message) == "<Message: text in channel:team at timestamp>"
