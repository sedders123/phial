"""Test parse_help_text."""
from phial.utils import parse_help_text


def test_parse_help_text() -> None:
    """Check it doesn't mess up simple input."""
    help_text = "Help text"
    output = parse_help_text(help_text)
    assert output == help_text


def test_parse_help_text_single_new_line() -> None:
    """Check removes new line."""
    help_text = "Help text\n same line"
    output = parse_help_text(help_text)
    assert output == "Help text same line"


def test_parse_help_text_double_new_line() -> None:
    """Check converts double new line to single."""
    help_text = "Help text\n\n new line"
    output = parse_help_text(help_text)
    assert output == "Help text\n new line"


def test_parse_help_text_single_new_line_multline() -> None:
    """Check handles multine strings correctly."""
    help_text = """Help text
    same line"""
    output = parse_help_text(help_text)
    assert output == "Help text same line"


def test_parse_help_text_double_new_line_multline() -> None:
    """Replaces double new line with single new line in multiline string."""
    help_text = """Help text

    new line"""
    output = parse_help_text(help_text)
    assert output == "Help text\n new line"
