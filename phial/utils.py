"""Helper utilities for phial."""

import re
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Optional

from phial.errors import ArgumentTypeValidationError, ArgumentValidationError
from phial.wrappers import Message


def validate_kwargs(func: Callable, kwargs: dict[str, str]) -> dict[str, Any]:
    """Validate kwargs match a functions signature."""
    func_params = signature(func).parameters
    validated_kwargs: dict[str, Any] = {}
    for key in func_params.values():
        value = None
        if key.default is not Parameter.empty:
            value = key.default
        if value is None and key.name not in kwargs:
            raise ArgumentValidationError(
                "Parameter {0} not provided to {1}".format(key.name, func.__name__)
            )
        elif key.name in kwargs:
            value = kwargs[key.name]

        if key.annotation is not Signature.empty:
            try:
                value = key.annotation(value)
            except ValueError:
                raise ArgumentTypeValidationError(
                    "{0} could not be converted to {1}".format(
                        value, key.annotation.__name__
                    )
                )
        validated_kwargs[key.name] = value
    return validated_kwargs


def parse_help_text(help_text: str) -> str:
    """Parse help text."""
    NEW_LINE_SEPERATOR = "<__NEW_LINE_SEPERATOR__>"

    # Strip excess whitespace
    help_text = help_text.strip()

    # Remove single new lines
    help_text = help_text.replace("\n", NEW_LINE_SEPERATOR)
    help_text = help_text.replace(NEW_LINE_SEPERATOR * 2, "\n")
    help_text = help_text.replace(NEW_LINE_SEPERATOR, "")

    # Remove extra spaces
    help_text = re.sub(r"(^[ \t]+|[ \t]+)", " ", help_text, flags=re.M)

    return help_text


def parse_slack_event(slack_event: dict) -> Optional["Message"]:
    """Parse Slack output."""
    event = slack_event.get("event", {})
    if "text" in event:
        bot_id = None
        team = None
        if "team" in event:
            team = event["team"]
        if "bot_id" in event:
            bot_id = event["bot_id"]

        msg = Message(
            event["text"],
            event["channel"],
            event["user"],
            event["ts"],
            team,
            bot_id,
        )
        return msg
    return None
