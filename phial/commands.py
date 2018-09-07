from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phial import Phial  # noqa

NEW_LINE_SEPERATOR = "<NEW_LINE_SEPERATOR>"

def help_command(bot: 'Phial') -> str:
    '''List all regsitered commmands'''
    help_text = bot.config.get('baseHelpText', "")
    if help_text:
        help_text += "\n"
    for command in bot.commands:
        # Have to ignore the type of the line below as mypy can not currently
        # deal with 'extending' functions to have extra attributes
        # GitHub Issue: https://github.com/python/mypy/issues/2087
        command_doc = bot.commands[command]._help  # type: ignore
        stripped_command_doc = command_doc.strip()
        escaped_command_doc = stripped_command_doc.replace("\n",NEW_LINE_SEPERATOR) \
            .replace(NEW_LINE_SEPERATOR * 2, "\n").replace(NEW_LINE_SEPERATOR, "")
        command_name = bot.command_names[command]
        help_text += "*{0}* - {1}\n".format(command_name, escaped_command_doc)
    return help_text
