from config_parser import parse_config


def test_single_section() -> None:
    text = "[server]\nhost = localhost\nport = 8080\n"
    result = parse_config(text)
    assert result == {"server": {"host": "localhost", "port": 8080}}


def test_multiple_sections() -> None:
    text = "[a]\nx = 1\n[b]\ny = 2\n"
    result = parse_config(text)
    assert result == {"a": {"x": 1}, "b": {"y": 2}}
