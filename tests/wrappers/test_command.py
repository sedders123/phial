from phial.wrappers import Command, Message


def test_command_repr() -> None:
    def test() -> None:
        pass

    command = Command('test', test, False, None)
    assert repr(command) == "<Command: test>"


def test_command_help_text() -> None:
    def test() -> None:
        """Help text"""
        pass

    command = Command('test', test, False, None)
    assert command.help_text == "Help text"


def test_command_help_text_override() -> None:
    def test() -> None:
        """Help text"""
        pass

    command = Command('test', test, False, "Help text override")
    assert command.help_text == "Help text override"


def test_command_build_patter_regex_no_substition_ignore_case():
    command_template = 'test'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match = command_pattern.match("test")
    assert match is not None


def test_command_build_patter_regex_single_substition_ignore_case():
    command_template = 'test <one>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match_dict = command_pattern.match("test one").groupdict()
    assert match_dict['one'] is not None


def test_command_build_patter_regex_multiple_substition_ignore_case():
    command_template = 'test <one> <two>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match_dict = command_pattern.match("test one two").groupdict()
    assert match_dict['one'] is not None
    assert match_dict['two'] is not None


def test_command_build_patter_regex_no_substition_case_sensitive():
    command_template = 'tEst'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   True)
    assert command_pattern.match("tEst") is not None
    assert command_pattern.match("Test") is None


def test_command_build_patter_regex_single_substition_case_sensitive():
    command_template = 'tEst <one>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   True)

    match_dict = command_pattern.match("tEst one").groupdict()
    assert match_dict['one'] is not None
    assert command_pattern.match("Test one") is None


def test_command_build_patter_regex_multiple_substition_case_sensitive():
    command_template = 'tEst <one> <two>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   True)
    match_dict = command_pattern.match("tEst one two").groupdict()
    assert match_dict['one'] is not None
    assert match_dict['two'] is not None
    assert command_pattern.match("Test one") is None


def test_build_command_allows_quotation_marks():
    command_template = 'test <one> <two>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match_dict = command_pattern.match("test \"one two\" three") \
        .groupdict()
    print(match_dict)
    assert match_dict['one'] == "one two"
    assert match_dict['two'] == "three"


def test_build_command_allows_all_params_with_quotation_marks():
    command_template = 'test <one> <two>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match_dict = command_pattern.match("test \"one two\" \"three\"") \
        .groupdict()
    print(match_dict)
    assert match_dict['one'] == "one two"
    assert match_dict['two'] == "three"


def test_build_command_allows_multiple_params_with_quotation_marks():
    command_template = 'test <one> <two> <three>'
    command_pattern = Command._build_pattern_regex(command_template,
                                                   False)
    match_dict = command_pattern.match("test \"one two\" three \"four\"") \
        .groupdict()
    print(match_dict)
    assert match_dict['one'] == "one two"
    assert match_dict['two'] == "three"
    assert match_dict['three'] == "four"


def test_command_pattern_matches() -> None:
    def test() -> None:
        pass

    command = Command('test', test, False, None)
    message = Message('test', 'channel', 'user', 'ts', 'team')

    assert command.pattern_matches(message) is not None
    assert command.pattern_matches(message) == {}


def test_command_pattern_matches_returns_none() -> None:
    def test() -> None:
        pass

    command = Command('test-no-match', test, False, None)
    message = Message('test', 'channel', 'user', 'ts', 'team')

    assert command.pattern_matches(message) is None
