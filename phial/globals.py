from werkzeug.local import LocalStack, LocalProxy
from typing import cast
from phial.wrappers import Message


def _find_command() -> Message:
    '''Gets the command from the context stack'''
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError('Not in a context with a command')
    return cast(Message, top)


_command_ctx_stack = LocalStack()  # type: ignore
command: Message = cast(Message, LocalProxy(_find_command))
