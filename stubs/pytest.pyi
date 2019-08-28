"""Partial type stubs for pytest."""
from typing import ContextManager, Optional, Type

from _pytest._code import ExceptionInfo  # type: ignore


def raises(exc_type: Type[BaseException],
           match: Optional[str] = None) -> ContextManager[ExceptionInfo]:  # noqa
    ...
