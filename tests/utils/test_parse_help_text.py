from phial.utils import parse_help_text


def test_parse_help_text() -> None:
    help_text = "Help text"
    output = parse_help_text(help_text)
    assert output == help_text


def test_parse_help_text_single_new_line() -> None:
    help_text = "Help text\n same line"
    output = parse_help_text(help_text)
    assert output == "Help text same line"


def test_parse_help_text_double_new_line() -> None:
    help_text = "Help text\n\n new line"
    output = parse_help_text(help_text)
    assert output == "Help text\n new line"


def test_parse_help_text_single_new_line_multline() -> None:
    help_text = """Help text
    same line"""
    output = parse_help_text(help_text)
    assert output == "Help text same line"


def test_parse_help_text_double_new_line_multline() -> None:
    help_text = """Help text

    new line"""
    output = parse_help_text(help_text)
    assert output == "Help text\n new line"
