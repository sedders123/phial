"""Partial type stubs for pytest."""

from typing import Any, ContextManager, Optional, Type

def raises(
    exc_type: Type[BaseException], match: Optional[str] = None
) -> ContextManager[Any]: ...
