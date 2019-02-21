import re
from typing import Dict, Pattern, IO, Optional, List, Callable
from phial.types import PhialResponse


class Response():
    """
    A response to be sent ot Slack.

    When returned in a command function will send a message, or reaction to
    Slack depending on contents.

    :param channel: The Slack channel ID the response will be sent to
    :param text: The response contents
    :param original_ts: The timestamp of the original message. If populated
                        will put the text response in a thread
    :param reation: A valid slack emoji name. NOTE: will only work when
                    :paramref:`original_ts` is populated
    :param attachments: Any Slack Message Attachments (TODO: Link)
    :param ephemeral: Whether to send the message as an ephemeral message
    :param user: The user id to display the ephemeral message to

    Examples:
        The following would send a message to a slack channel when executed ::

            @slackbot.command('ping')
            def ping():
                return Response(text="Pong", channel='channel_id')

        The following would send a reply to a message in a thread ::

            @slackbot.command('hello')
            def hello():
                return Response(text="hi",
                                channel='channel_id',
                                original_ts='original_ts')

        The following would send a reaction to a message ::

            @slackbot.command('react')
            def react():
                return Response(reaction="x",
                                channel='channel_id',
                                original_ts='original_ts')
    """

    def __init__(self,
                 channel: str,
                 text: Optional[str] = None,
                 original_ts: Optional[str] = None,
                 reaction: Optional[str] = None,
                 ephemeral: bool = False,
                 user: Optional[str] = None,
                 attachments: Optional[Dict] = None) -> None:
        self.channel = channel
        self.text = text
        self.original_ts = original_ts
        self.reaction = reaction
        self.ephemeral = ephemeral
        self.user = user
        self.attachments = attachments

    def __repr__(self) -> str:
        return "<Response: {0}>".format(self.text)

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__


class Attachment():
    def __init__(self,
                 channel: str,
                 filename: Optional[str] = None,
                 content: Optional[IO] = None) -> None:
        self.channel = channel
        self.filename = filename
        self.content = content

    def __repr__(self) -> str:
        return "<Attachment in {0}>".format(self.channel)


class Message():
    """
    A representation of a Slack message.

    :param text: The message contents
    :param channel: The Slack channel ID the message was sent from
    :param user: The user who sent the message
    :param timestamp: The message's timestamp
    :param team: The Team ID of the Slack workspace the message was
                 sent from
    :param bot_id: If the message was sent by a bot
                   the ID of that bot. Defaults to None.
    """

    def __init__(self,
                 text: str,
                 channel: str,
                 user: str,
                 timestamp: str,
                 team: str,
                 bot_id: Optional[str] = None) -> None:
        self.text = text
        self.channel = channel
        self.user = user
        self.timestamp = timestamp
        self.team = team
        self.bot_id = bot_id

    def __repr__(self) -> str:
        return "<Message: {0} in {1}:{2} at {3}>".format(self.text,
                                                         self.channel,
                                                         self.team,
                                                         self.timestamp)

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__


class Command:
    def __init__(self,
                 pattern: str,
                 func: Callable[..., PhialResponse],
                 case_sensitive: bool = False,
                 help_text_override: Optional[str] = None):
        self.pattern_string = pattern
        self.pattern = self._build_pattern_regex(pattern, case_sensitive)
        self.alias_patterns = self._get_alias_patterns(func)
        self.func = func
        self.case_sensitive = case_sensitive
        self.help_text_override = help_text_override

    def __repr__(self) -> str:
        return "<Command: {0}>".format(self.pattern_string)

    def _get_alias_patterns(self, func: Callable) -> List[Pattern]:
        patterns: List[Pattern] = []
        if hasattr(func, 'alias_patterns'):
            for pattern in func.alias_patterns:  # type: ignore
                patterns.append(self._build_pattern_regex(pattern))
        return patterns

    @staticmethod
    def _build_pattern_regex(pattern: str,
                             case_sensitive: bool = False) -> Pattern[str]:
        command = re.sub(r'(<\w+>)', r'(\"?\1\"?)', pattern)
        command_regex = re.sub(r'(<\w+>)', r'(?P\1[^"]*)', command)
        return re.compile("^{}$".format(command_regex),
                          0 if case_sensitive else re.IGNORECASE)

    def pattern_matches(self,
                        message: Message) -> Optional[Dict]:
        match = self.pattern.match(message.text)
        if match:
            return match.groupdict()

        # Only check aliases if main pattern does not match
        for alias in self.alias_patterns:
            match = alias.match(message.text)
            if match:
                return match.groupdict()

        return None

    @property
    def help_text(self) -> Optional[str]:
        if self.help_text_override is not None:
            return self.help_text_override
        return self.func.__doc__
