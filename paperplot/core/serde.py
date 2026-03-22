"""Serialization helpers for JSON and YAML-like PaperPlot assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal envs.
    yaml = None


def load_mapping_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".json":
        with file_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    elif suffix in {".yaml", ".yml"}:
        with file_path.open("r", encoding="utf-8") as handle:
            text = handle.read()
        data = _load_yaml_text(text)
    else:
        raise ValueError(f"Unsupported config or asset file type: {file_path.suffix}")

    if not isinstance(data, dict):
        raise TypeError(f"Top-level content must be a mapping: {file_path}")
    return data


def _load_yaml_text(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> Any:
    lines = _preprocess_lines(text)
    if not lines:
        return {}

    root: Any = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    index = 0
    while index < len(lines):
        indent, content = lines[index]
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        container = stack[-1][1]

        if content.startswith("- "):
            if not isinstance(container, list):
                raise TypeError("List item found under non-list container in YAML input.")
            value = content[2:].strip()
            if not value:
                new_value: Any = {}
                container.append(new_value)
                stack.append((indent, new_value))
            elif ":" in value and not value.startswith("{"):
                key, _, raw_value = value.partition(":")
                new_value = {key.strip(): _parse_scalar(raw_value.strip()) if raw_value.strip() else {}}
                container.append(new_value)
                stack.append((indent, new_value))
            else:
                container.append(_parse_scalar(value))
            index += 1
            continue

        key, has_value, raw_value = content.partition(":")
        if not has_value:
            raise ValueError(f"Invalid YAML line: {content!r}")
        key = key.strip()
        value = raw_value.strip()

        next_line = lines[index + 1] if index + 1 < len(lines) else None
        if value == "":
            if next_line and next_line[0] > indent and next_line[1].startswith("- "):
                new_value = []
            else:
                new_value = {}
            if not isinstance(container, dict):
                raise TypeError("Mapping entry found under non-mapping container in YAML input.")
            container[key] = new_value
            stack.append((indent, new_value))
        else:
            if not isinstance(container, dict):
                raise TypeError("Mapping entry found under non-mapping container in YAML input.")
            container[key] = _parse_scalar(value)
        index += 1

    return root


def _preprocess_lines(text: str) -> list[tuple[int, str]]:
    prepared: list[tuple[int, str]] = []
    for raw in text.splitlines():
        without_comment = _strip_comment(raw)
        if not without_comment.strip():
            continue
        indent = len(without_comment) - len(without_comment.lstrip(" "))
        prepared.append((indent, without_comment.strip()))
    return prepared


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _parse_scalar(value: str) -> Any:
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if lower in {"null", "none"}:
        return None

    if value.startswith("[") and value.endswith("]"):
        return _parse_inline_list(value[1:-1])
    if value.startswith("{") and value.endswith("}"):
        return _parse_inline_dict(value[1:-1])
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    return value


def _parse_inline_list(body: str) -> list[Any]:
    if not body.strip():
        return []
    return [_parse_scalar(part.strip()) for part in _split_top_level(body, ",")]


def _parse_inline_dict(body: str) -> dict[str, Any]:
    if not body.strip():
        return {}
    result: dict[str, Any] = {}
    for item in _split_top_level(body, ","):
        key, _, value = item.partition(":")
        if not _:
            raise ValueError(f"Invalid inline mapping item: {item!r}")
        result[key.strip()] = _parse_scalar(value.strip())
    return result


def _split_top_level(text: str, delimiter: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    in_single = False
    in_double = False

    for char in text:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == delimiter and depth == 0:
                items.append("".join(current).strip())
                current = []
                continue
        current.append(char)

    if current:
        items.append("".join(current).strip())
    return items
