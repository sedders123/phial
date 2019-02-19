from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from phial.wrappers import Response, Attachment  # noqa

PhialResponse = Union[None, str, 'Response', 'Attachment']
