from werkzeug.local import LocalStack, LocalProxy


def _find_command():
    '''Gets the command from the context stack'''
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError('Not in a context with a command')
    return top


_command_ctx_stack = LocalStack()
command = LocalProxy(_find_command)
