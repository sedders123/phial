from werkzeug.local import LocalStack, LocalProxy
from typing import cast, Dict
from .wrappers import Command


def _find_command() -> Command:
    '''Gets the command from the context stack'''
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError('Not in a context with a command')
    return cast(Command, top)


def _get_global() -> Dict:
    top = _global_ctx_stack.top
    if top is None:
        raise RuntimeError('Working outside the app context')
    return cast(Dict, top)


_command_ctx_stack = LocalStack()  # type: ignore
_global_ctx_stack = LocalStack()  # type: ignore
command = cast(Command, LocalProxy(_find_command))  # type: Command
g = cast(Dict, LocalProxy(_get_global))  # type: Dict
