"""Partial type stubs for Werkzeug."""

from typing import Callable, Generic, TypeVar

T = TypeVar("T")

class LocalStack(Generic[T]):
    @property
    def top(self) -> T: ...
    def push(self, item: T) -> None: ...
    def pop(self) -> None: ...

def LocalProxy(func: Callable[..., T]) -> T:
    """
    This is actually a class.

    It's a function here because it is easier to stub
    """
    ...
