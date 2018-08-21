from phial import Phial


def help_command(bot: Phial) -> str:
    '''List all regsitered commmands'''
    help_text = ""
    for command in bot.commands:
        # Have to ignore the type of the line below as mypy can not currently
        # deal with 'extending' functions to have extra attributes
        # GitHub Issue: https://github.com/python/mypy/issues/2087
        command_doc = bot.commands[command]._help  # type: ignore
        command_name = bot.command_names[command]
        help_text += "*{0}* - {1}\n".format(command_name, command_doc)
    return help_text
