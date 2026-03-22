"""Annotation helpers for paper-style plots."""

from __future__ import annotations

from typing import Any


def compile_significance_annotations(
    significance: list[dict[str, Any]] | None,
    *,
    within_groups: list[Any] | None = None,
) -> list[dict[str, Any]]:
    if not significance:
        return []

    compiled: list[dict[str, Any]] = []
    for item in significance:
        if not isinstance(item, dict):
            continue

        compare = item.get("compare")
        if isinstance(compare, (list, tuple)) and len(compare) == 2:
            left, right = compare
            compiled_item = dict(item)
            compiled_item.pop("compare", None)
            compiled_item.setdefault("x1", left)
            compiled_item.setdefault("x2", right)
            compiled.append(compiled_item)
            continue

        pairs = item.get("pairs")
        if isinstance(pairs, (list, tuple)):
            compiled.extend(_compile_pair_annotations(item, pairs, within_groups=within_groups))
            continue

        against = item.get("against")
        if against is not None:
            compiled.extend(_compile_against_annotations(item, against, within_groups=within_groups))
    return compiled


def add_significance_annotations(
    *,
    ax: Any,
    annotations: list[dict[str, Any]] | None,
    x_lookup: dict[Any, float],
    default_pad: float = 0.03,
) -> None:
    if not annotations:
        return

    ymin, ymax = ax.get_ylim()
    span = ymax - ymin if ymax > ymin else 1.0
    base_pad = span * default_pad

    for index, annotation in enumerate(annotations):
        left_key = _normalize_lookup_key(annotation.get("x1"))
        right_key = _normalize_lookup_key(annotation.get("x2"))
        left = x_lookup.get(left_key, annotation.get("x1"))
        right = x_lookup.get(right_key, annotation.get("x2"))
        if left is None or right is None:
            continue

        height = annotation.get("y", ymax + base_pad * (index + 1))
        tick = annotation.get("tick", base_pad * 0.4)
        text = annotation.get("text", "*")

        ax.plot([left, left, right, right], [height, height + tick, height + tick, height], color="#222222", linewidth=1.0)
        ax.text((left + right) / 2, height + tick + base_pad * 0.15, str(text), ha="center", va="bottom", fontsize=8)

    ax.set_ylim(ymin, max(ax.get_ylim()[1], ymax + base_pad * (len(annotations) + 2)))


def _normalize_lookup_key(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(value)
    return value


def _compile_pair_annotations(
    item: dict[str, Any],
    pairs: list[Any] | tuple[Any, ...],
    *,
    within_groups: list[Any] | None,
) -> list[dict[str, Any]]:
    compiled: list[dict[str, Any]] = []
    selected_groups = _resolve_within_groups(item.get("within"), within_groups)
    texts = item.get("text")
    ys = item.get("y")
    ticks = item.get("tick")

    for index, pair in enumerate(pairs):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        left, right = pair

        if selected_groups is not None:
            for group in selected_groups:
                compiled.append(
                    _build_annotation(
                        item,
                        x1=[group, left],
                        x2=[group, right],
                        index=index,
                        text=texts,
                        y=ys,
                        tick=ticks,
                    )
                )
            continue

        compiled.append(
            _build_annotation(
                item,
                x1=left,
                x2=right,
                index=index,
                text=texts,
                y=ys,
                tick=ticks,
            )
        )

    return compiled


def _compile_against_annotations(
    item: dict[str, Any],
    against: Any,
    *,
    within_groups: list[Any] | None,
) -> list[dict[str, Any]]:
    selected_groups = _resolve_within_groups(item.get("within"), within_groups)
    if selected_groups is None:
        return []

    exclude = set(_listify(item.get("exclude")))
    pairs: list[list[Any]] = []
    for group in selected_groups:
        if group == against or group in exclude:
            continue
        pairs.append([against, group])

    flattened_item = dict(item)
    flattened_item.pop("within", None)
    return _compile_pair_annotations(flattened_item, pairs, within_groups=None)


def _resolve_within_groups(value: Any, groups: list[Any] | None) -> list[Any] | None:
    if value is None:
        return None
    if groups is None:
        return []
    if value in {"all", "each", True}:
        return list(groups)
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _build_annotation(
    source: dict[str, Any],
    *,
    x1: Any,
    x2: Any,
    index: int,
    text: Any,
    y: Any,
    tick: Any,
) -> dict[str, Any]:
    compiled = dict(source)
    compiled.pop("compare", None)
    compiled.pop("pairs", None)
    compiled.pop("within", None)
    compiled["x1"] = x1
    compiled["x2"] = x2

    resolved_text = _value_for_index(text, index)
    resolved_y = _value_for_index(y, index)
    resolved_tick = _value_for_index(tick, index)

    if resolved_text is not None:
        compiled["text"] = resolved_text
    if resolved_y is not None:
        compiled["y"] = resolved_y
    if resolved_tick is not None:
        compiled["tick"] = resolved_tick
    return compiled


def _value_for_index(value: Any, index: int) -> Any:
    if isinstance(value, (list, tuple)):
        if 0 <= index < len(value):
            return value[index]
        return None
    return value


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]
