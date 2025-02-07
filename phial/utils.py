"""Helper utilities for phial."""

import re
from collections.abc import Callable
from inspect import Parameter, Signature, signature
from typing import Any, Optional

from phial.errors import ArgumentTypeValidationError, ArgumentValidationError
from phial.wrappers import Message


def validate_kwargs(func: Callable, kwargs: dict[str, str]) -> dict[str, Any]:
    """Validate kwargs match a functions signature."""
    func_params = signature(func).parameters
    validated_kwargs: dict[str, Any] = {}
    # If a function is wrapped additional parameters could be injected
    # which the user should not have to provide.
    # We won't validate params for wrapped functions
    is_func_wrapped = hasattr(func, "__wrapped__")
    for key in func_params.values():
        value = None
        if key.default is not Parameter.empty:
            value = key.default
        if value is None and key.name not in kwargs and not is_func_wrapped:
            raise ArgumentValidationError(
                f"Parameter {key.name} not provided to {func.__name__}",
            )
        if key.name in kwargs:
            value = kwargs[key.name]

        if key.annotation is not Signature.empty and value:
            try:
                value = key.annotation(value)
            except ValueError:
                raise ArgumentTypeValidationError(
                    f"{value} could not be converted to {key.annotation.__name__}",
                )
        if value:
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
    help_text = re.sub(r"(^[ \t]+|[ \t]+)", " ", help_text, flags=re.MULTILINE)

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
