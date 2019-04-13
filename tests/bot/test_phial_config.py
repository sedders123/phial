"""Test phial config."""
from phial import Phial


def test_uses_default_config_when_not_specified() -> None:
    """Test phial using default config."""
    bot = Phial('test-token')
    assert bot.config == Phial.default_config


def test_config_override() -> None:
    """Test config can be overriden."""
    bot = Phial('test-token', config={
        'prefix': "/",
        'registerHelpCommand': False,
        'baseHelpText': "All commands:",
        'autoReconnect': False,
        'loopDelay': 0.5,
        'hotReload': True,
    })

    assert bot.config == {
        'prefix': "/",
        'registerHelpCommand': False,
        'baseHelpText': "All commands:",
        'autoReconnect': False,
        'loopDelay': 0.5,
    }


def test_partial_config_override() -> None:
    """Test config can be partially oerriden."""
    bot = Phial('test-token', config={
        'prefix': "/",
    })

    assert bot.config['prefix'] == '/'
    assert bot.config['baseHelpText'] == "All available commands:"
