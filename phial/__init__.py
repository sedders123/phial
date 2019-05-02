"""phial Slack Bot."""
from phial.bot import Phial
from phial.globals import command
from phial.scheduler import Schedule
from phial.wrappers import Attachment, Message, Response

__version__ = "0.8.3"
__all__ = ['Phial', 'command', 'Response', 'Attachment', 'Schedule', 'Message']
