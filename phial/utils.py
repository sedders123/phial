import re


def parse_help_text(help_text: str) -> str:
    NEW_LINE_SEPERATOR = "<__NEW_LINE_SEPERATOR__>"

    # Strip excess whitespace
    help_text = help_text.strip()

    # Remove single new lines
    help_text = help_text.replace("\n", NEW_LINE_SEPERATOR)
    help_text = help_text.replace(NEW_LINE_SEPERATOR * 2, "\n")
    help_text = help_text.replace(NEW_LINE_SEPERATOR, "")

    # Remove extra spaces
    help_text = re.sub(r'(^[ \t]+|[ \t]+)', ' ', help_text, flags=re.M)

    return help_text
