"""Starter examples."""

import os
from time import sleep

from phial import Attachment, Phial, Response, command
from phial.wrappers import Command

slackbot = Phial(
    os.getenv("SLACK_APP_TOKEN", "NONE"), os.getenv("SLACK_BOT_TOKEN", "NONE")
)


@slackbot.command("ping")
def ping() -> str:
    """A command which replies with a message."""
    return "Pong"


@slackbot.command("pong")
def pong() -> str:
    """
    A command which replies with a message.

    It has a mutiline docstring.
    """
    return "Ping"


@slackbot.command("hi <name>")
def hi(name: str) -> Response:
    """A command with an argument which replies to a message."""
    return Response(text=f"Hello {name}", channel=command.channel)


@slackbot.command("add <x> <y>")
@slackbot.alias("add <x>")
def add(x: int, y: int = 5) -> str:
    """Add two numbers."""
    return str(x + y)


@slackbot.command("hello <name> <from_>")
def hello(name: str, from_: str) -> Response:
    """A command with two arguments which replies to a message."""
    return Response(
        text=f"Hi {name}, from {from_}",
        channel=command.channel,
    )


@slackbot.command("react")
def react() -> Response:
    """A command that reacts to the original message."""
    return Response(
        reaction="x",
        channel=command.channel,
        original_ts=command.timestamp,
    )


@slackbot.command("upload")
def upload() -> Attachment:
    """A command that uploads a set file."""
    project_dir = os.path.dirname(__file__)
    file_path = os.path.join(project_dir, "phial.png")
    return Attachment(
        channel=command.channel,
        filename="phial.png",
        content=open(file_path, "rb"),
    )


@slackbot.command("reply")
def reply() -> Response:
    """A command that replies to the original message in a thread."""
    return Response(
        text="this is a thread",
        channel=command.channel,
        original_ts=command.timestamp,
    )


@slackbot.command("caseSensitive", case_sensitive=True)
def case_sensitive() -> str:
    """A command which replies with a message."""
    return "You typed caseSensitive"


@slackbot.command("messageWithAttachment")
def get_message_with_attachment() -> Response:
    """
    A command that posts a message with a Slack attachment.

    Read more: https://api.slack.com/docs/message-attachments
    """
    return Response(
        channel=command.channel,
        attachments=[
            {
                "title": "Here's the title of the attachment",
                "text": "...and here's the text",
                "footer": "Teeny tiny footer text",
            },
        ],
    )


@slackbot.command("long")
def long() -> str:
    """Command that sleeps for 5 seconds."""
    sleep(5)
    return "Well that took a while"


@slackbot.command("hidden", hide_from_help_command=True)
def hidden() -> str:
    """A command that is hidden from the default help command."""
    return "Suprise"


@slackbot.fallback_command()
def fallback_command(command: Command) -> str:
    """A fall back command."""
    return "Thats not a command"


if __name__ == "__main__":
    slackbot.run()
