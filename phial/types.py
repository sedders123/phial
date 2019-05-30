"""Shared types for phial."""
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: nocover
    from phial.wrappers import Response, Attachment  # noqa

#: A union of all response types phial can use
PhialResponse = Union[None, str, 'Response', 'Attachment']
