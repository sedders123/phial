"""Test Command class."""

from phial.wrappers import Command, Message


def test_command_repr() -> None:
    """Assert Command repr works."""

    def test() -> None:
        pass

    command = Command("test", test)
    assert repr(command) == "<Command: test>"


def test_command_help_text() -> None:
    """Assert help text found from docstring."""

    def test() -> None:
        """Help text."""

    command = Command("test", test)
    assert command.help_text == "Help text."


def test_command_help_text_override() -> None:
    """Assert help text override works."""

    def test() -> None:
        """Help text."""

    command = Command("test", test, help_text_override="Help text override")
    assert command.help_text == "Help text override"


def test_command_build_patter_regex_no_substitution_ignore_case() -> None:
    """Assert case insensitive regex works correctly."""
    command_template = "test"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match = command_pattern.match("test")
    assert match is not None
    match = command_pattern.match("Test")
    assert match is not None


def test_command_build_patter_regex_single_substitution_ignore_case() -> None:
    """Assert case insensitive regex with param works correctly."""
    command_template = "test <one>"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match_dict = command_pattern.match("test one")
    assert match_dict is not None
    assert match_dict.groupdict()["one"] is not None


def test_command_build_patter_regex_multiple_substitution_ignore_case() -> None:
    """Assert case insensitive regex with multiple param works correctly."""
    command_template = "test <one> <two>"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match_dict = command_pattern.match("test one two")
    assert match_dict is not None
    assert match_dict.groupdict()["one"] is not None
    assert match_dict.groupdict()["two"] is not None


def test_command_build_patter_regex_no_substitution_case_sensitive() -> None:
    """Assert case sensitive regex works correctly."""
    command_template = "tEst"
    command_pattern = Command._build_pattern_regex(  # noqa: SLF001
        command_template,
        case_sensitive=True,
    )
    assert command_pattern.match("tEst") is not None
    assert command_pattern.match("Test") is None


def test_build_patter_regex_single_substitution_case_sensitive() -> None:
    """Assert case sensitive regex with param works correctly."""
    command_template = "tEst <one>"
    command_pattern = Command._build_pattern_regex(  # noqa: SLF001
        command_template,
        case_sensitive=True,
    )

    match_dict = command_pattern.match("tEst one")
    assert match_dict is not None
    assert match_dict.groupdict()["one"] is not None
    assert command_pattern.match("Test one") is None


def test_build_patter_regex_multiple_substitution_case_sensitive() -> None:
    """Assert case sensitive regex with multiple param works correctly."""
    command_template = "tEst <one> <two>"
    command_pattern = Command._build_pattern_regex(  # noqa: SLF001
        command_template,
        case_sensitive=True,
    )
    match_dict = command_pattern.match("tEst one two")
    assert match_dict is not None
    assert match_dict.groupdict()["one"] is not None
    assert match_dict.groupdict()["two"] is not None
    assert command_pattern.match("Test one") is None


def test_build_command_allows_quotation_marks() -> None:
    """Assert regex allows partial quoting."""
    command_template = "test <one> <two>"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match_dict = command_pattern.match('test "one two" three')
    assert match_dict is not None
    assert match_dict.groupdict()["one"] == "one two"
    assert match_dict.groupdict()["two"] == "three"


def test_build_command_allows_all_params_with_quotation_marks() -> None:
    """Assert regex allows full quoting."""
    command_template = "test <one> <two>"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match_dict = command_pattern.match('test "one two" "three"')
    assert match_dict is not None
    assert match_dict.groupdict()["one"] == "one two"
    assert match_dict.groupdict()["two"] == "three"


def test_build_command_allows_multiple_params_with_quotation_marks() -> None:
    """Assert regex allows partial quoting surrounding unquoted."""
    command_template = "test <one> <two> <three>"
    command_pattern = Command._build_pattern_regex(command_template)  # noqa: SLF001
    match_dict = command_pattern.match('test "one two" three "four"')
    assert match_dict is not None
    assert match_dict.groupdict()["one"] == "one two"
    assert match_dict.groupdict()["two"] == "three"
    assert match_dict.groupdict()["three"] == "four"


def test_command_pattern_matches() -> None:
    """Assert pattern_matches matches correctly."""

    def test() -> None:
        pass

    command = Command("test", test)
    message = Message("test", "channel", "user", "ts", "team")

    assert command.pattern_matches(message) is not None
    assert command.pattern_matches(message) == {}


def test_command_pattern_matches_aliases() -> None:
    """Assert pattern_matches matches aliases correctly."""

    def test() -> None:
        pass

    command = Command("test", test)
    command.alias_patterns = [
        Command._build_pattern_regex("test <one>"),  # noqa: SLF001
    ]
    message = Message("test one", "channel", "user", "ts", "team")

    assert command.pattern_matches(message) is not None
    assert command.pattern_matches(message) == {"one": "one"}


def test_command_pattern_matches_returns_values() -> None:
    """Assert pattern_matches matches returns values correctly."""

    def test(val: str) -> None:
        pass

    command = Command("test <val>", test)
    message = Message("test value", "channel", "user", "ts", "team")

    assert command.pattern_matches(message) is not None
    assert command.pattern_matches(message) == {"val": "value"}


def test_command_pattern_matches_returns_none() -> None:
    """Assert pattern_matches does not incorrectly match."""

    def test() -> None:
        pass

    command = Command("test-no-match", test)
    message = Message("test", "channel", "user", "ts", "team")

    assert command.pattern_matches(message) is None
