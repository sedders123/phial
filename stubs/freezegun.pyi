"""Partial type stubs for freezegun."""

from collections.abc import Callable
from datetime import date, datetime
from types import TracebackType
from typing import TypeVar

_F = TypeVar("_F", bound=Callable[..., object])

class FrozenDateTimeFactory:
    def move_to(self, target_datetime: str | date | datetime) -> None: ...

class _freeze_time:
    def __call__(self, func: _F) -> _F: ...
    def __enter__(self) -> FrozenDateTimeFactory: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

def freeze_time(time: str) -> _freeze_time: ...
