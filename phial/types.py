from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from phial.wrappers import Response, Attachment  # noqa

#: A union of all response types phial can use
PhialResponse = Union[None, str, 'Response', 'Attachment']
