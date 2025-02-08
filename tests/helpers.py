"""Helpers for unit tests."""

from typing import Any

import pytest  # noqa


def wildpatch(
    target: Any,  # noqa: ANN401
    name: str,
    value: Any = None,  # noqa: ANN401
    *,
    raising: bool = True,
) -> None:
    """Monkey patch target."""
    import inspect

    if value is None:
        if not isinstance(target, str):
            raise TypeError(
                "use setattr(target, name, value) or "
                "setattr(target, value) with target being a dotted"
                " import string",
            )
        value = name
        name, target = derive_importpath(target, raising)  # type: ignore # noqa

    oldval = getattr(target, name, None)
    if raising and oldval is None:
        raise AttributeError(f"{target} has no attribute {name}")

    # avoid class descriptors like staticmethod/classmethod
    if inspect.isclass(target):
        oldval = target.__dict__.get(name, None)
    setattr(target, name, value)
