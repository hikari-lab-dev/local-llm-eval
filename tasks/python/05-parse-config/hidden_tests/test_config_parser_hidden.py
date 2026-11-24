from config_parser import parse_config


def test_boolean_values() -> None:
    text = "[a]\nenabled = True\ndisabled = FALSE\n"
    result = parse_config(text)
    assert result == {"a": {"enabled": True, "disabled": False}}


def test_float_value() -> None:
    text = "[a]\nratio = 3.14\n"
    result = parse_config(text)
    assert result == {"a": {"ratio": 3.14}}


def test_float_value_is_float_type() -> None:
    text = "[a]\nratio = 3.14\n"
    result = parse_config(text)
    assert isinstance(result["a"]["ratio"], float)


def test_inline_comment_and_blank_lines() -> None:
    text = "[a]\n\n# comment\nx = 1  # inline comment\n\n"
    result = parse_config(text)
    assert result == {"a": {"x": 1}}


def test_negative_integer() -> None:
    text = "[a]\nx = -5\n"
    result = parse_config(text)
    assert result == {"a": {"x": -5}}


def test_plain_string_value() -> None:
    text = "[a]\nname = hello world\n"
    result = parse_config(text)
    assert result == {"a": {"name": "hello world"}}


def test_duplicate_section_merges_keys() -> None:
    text = "[a]\nx = 1\n[a]\ny = 2\n"
    result = parse_config(text)
    assert result == {"a": {"x": 1, "y": 2}}
