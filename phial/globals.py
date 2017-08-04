from werkzeug.local import LocalStack, LocalProxy


def _find_command():
    '''Gets the command from the context stack'''
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError('Not in a context with a command')
    return top


def _get_global():
    top = _global_ctx_stack.top
    if top is None:
        raise RuntimeError('Working outside the app context')
    return top


_command_ctx_stack = LocalStack()
_global_ctx_stack = LocalStack()
command = LocalProxy(_find_command)
g = LocalProxy(_get_global)
