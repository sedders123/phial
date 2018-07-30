from phial import Phial


def help_command(_bot: Phial) -> str:
    '''List all regsitered commmands'''
    help_text = ""
    for command in _bot.commands:
        command_doc = _bot.commands[command].__doc__
        command_name = _bot.command_names[command]
        help_text += "*{0}* - {1}\n".format(command_name, command_doc)
    return help_text
