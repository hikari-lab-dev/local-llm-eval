"""簡易設定ファイルパーサー。"""

from __future__ import annotations

_TRUE_VALUES = {"true"}
_FALSE_VALUES = {"false"}


def parse_config(text: str) -> dict[str, dict[str, object]]:
    """簡易INI風の設定テキストをパースする。

    Args:
        text: 設定ファイルの内容全体。

    Returns:
        セクション名をキーとし、値は key: 変換後の値 の辞書を持つ辞書。
    """
    sections: dict[str, dict[str, object]] = {}
    current_section = ""
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        section_name = _match_section_header(line)
        if section_name is not None:
            current_section = section_name
            sections.setdefault(current_section, {})
            continue
        key, value = _parse_key_value(line)
        sections.setdefault(current_section, {})[key] = _convert_value(value)
    return sections


def _strip_comment(line: str) -> str:
    """行内コメント（# 以降）を取り除く。"""
    index = line.find("#")
    if index == -1:
        return line
    return line[:index]


def _match_section_header(line: str) -> str | None:
    """`[section]` 形式ならセクション名を返す。"""
    if not (line.startswith("[") and line.endswith("]")):
        return None
    return line[1:-1].strip()


def _parse_key_value(line: str) -> tuple[str, str]:
    """`key = value` を key と value に分割する。"""
    key, _, value = line.partition("=")
    return key.strip(), value.strip()


def _convert_value(value: str) -> object:
    """文字列値を bool / int / float / str のいずれかへ変換する。"""
    lowered = value.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    if _is_int(value):
        return int(value)
    if _is_float(value):
        return float(value)
    return value


def _is_int(value: str) -> bool:
    """文字列が整数として解釈できるかを判定する。"""
    try:
        int(value)
        return True
    except ValueError:
        return False


def _is_float(value: str) -> bool:
    """文字列が浮動小数点として解釈できるかを判定する。"""
    try:
        float(value)
        return True
    except ValueError:
        return False
