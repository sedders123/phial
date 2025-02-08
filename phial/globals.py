"""Provides the globally scoped parts of phial."""

from typing import cast

from werkzeug.local import LocalProxy, LocalStack

from phial.wrappers import Message


def _find_command() -> Message:
    """Get the command from the context stack."""
    top = _command_ctx_stack.top
    if top is None:
        raise RuntimeError("Not in a context with a command")
    return cast(Message, top)


_command_ctx_stack: LocalStack[Message] = LocalStack()
command: Message = LocalProxy(_find_command)
