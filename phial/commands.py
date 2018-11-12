from typing import TYPE_CHECKING, cast
from phial.utils import parse_help_text

if TYPE_CHECKING:
    from phial import Phial  # noqa


def help_command(bot: 'Phial') -> str:
    '''List all regsitered commmands'''
    help_text = cast(str, bot.config.get('baseHelpText', ""))
    if help_text:
        help_text += "\n"
    for command in bot.commands:
        # Have to ignore the type of the line below as mypy can not currently
        # deal with 'extending' functions to have extra attributes
        # GitHub Issue: https://github.com/python/mypy/issues/2087
        command_doc = bot.commands[command]._help  # type: ignore
        if not command_doc:
            # If no help text default to blank string
            command_doc = ""
        commnad_help_text = parse_help_text(command_doc)
        command_name = bot.command_names[command]
        help_text += "*{0}* - {1}\n".format(command_name, commnad_help_text)
    return help_text
