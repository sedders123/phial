"""Advanced examples."""

import logging
import os
from multiprocessing import Process
from time import sleep
from functools import wraps
from typing import Any, Callable

from phial import Message, Phial, Response, Schedule, command

slackbot = Phial(
    os.getenv("SLACK_APP_TOKEN", "NONE"), os.getenv("SLACK_BOT_TOKEN", "NONE")
)
SCHEDULED_CHANNEL = "channel-id"


def foo_injector(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        return func(*args, foo="bar", **kwargs)

    return decorator


@slackbot.command("foo")
@foo_injector
def foo(foo: str) -> str:
    """A command which replies with a message."""
    return foo


@slackbot.command("cent(er|re)")
def regex_in_command() -> Response:
    """Command that uses regex to define structure."""
    base_command = command.text.split(" ")[0]
    if slackbot.config["prefix"]:
        base_command = base_command[1:]
    if base_command == "center":
        return Response(text="Yeehaw! You're a Yank", channel=command.channel)
    if base_command == "centre":
        return Response(text="I say! You appear to be a Brit", channel=command.channel)
    return Response(
        text="Well this is awkward... this isn't meant to \
                    happen",
        channel=command.channel,
    )


@slackbot.command("colo[u]?r <arg>")
def regex_in_command_with_arg(arg: str) -> Response:
    """Command that uses regex to define structure with an arg."""
    base_command = command.text.split(" ")[0]
    return Response(
        text=f"My favourite {base_command} is {arg}",
        channel=command.channel,
    )


def fire_and_forget(channel: str) -> None:
    """
    Example function used by background_processing().

    Sends a message outside of a command context.
    """
    sleep(3)
    slackbot.send_message(Response(text="Background Process Message", channel=channel))


@slackbot.command("background")
def background_processing() -> str:
    """Command that starts a process to allow a non blocking sleep."""
    p = Process(target=fire_and_forget, args=(command.channel,), daemon=True)
    p.start()
    return "Foreground message"


@slackbot.middleware()
def log_message(message: Message) -> Message:
    """Middleware that logs a message."""
    logging.info(message)
    return message


@slackbot.scheduled(Schedule().seconds(30))
def shceduled_function() -> None:
    """Sends a message on a schedule."""
    slackbot.send_message(Response(text="Hey! Hey Listen!", channel=SCHEDULED_CHANNEL))


@slackbot.command("messageWithAttachment")
def get_message_with_attachment() -> Response:
    """A command that posts a message with a Slack attachment."""
    return Response(
        channel=command.channel,
        attachments=[
            {
                "title": "Here's a message, it has 2 attachment fields",
                "title_link": "https://api.slack.com/docs/message-attachments",
                "text": "This message has some text!",
                "fields": [
                    {
                        "title": "Here's the first attachment field",
                        "value": "And here's it's body",
                        "short": True,
                    },
                    {
                        "title": "...And here's the second",
                        "value": "And here's it's body",
                        "short": True,
                    },
                ],
            },
        ],
    )


if __name__ == "__main__":
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    slackbot.run()
