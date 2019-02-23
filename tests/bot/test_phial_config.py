from phial import Phial


def test_uses_default_config_when_specified():
    bot = Phial('test-token')
    assert bot.config == Phial.default_config


def test_config_override():
    bot = Phial('test-token', config={
        'prefix': "/",
        'registerHelpCommand': False,
        'baseHelpText': "All commands:",
        'autoReconnect': False
    })

    assert bot.config == {
        'prefix': "/",
        'registerHelpCommand': False,
        'baseHelpText': "All commands:",
        'autoReconnect': False
    }


def test_partial_config_override():
    bot = Phial('test-token', config={
        'prefix': "/",
    })

    assert bot.config['prefix'] == '/'
    assert bot.config['baseHelpText'] == "All available commands:"
