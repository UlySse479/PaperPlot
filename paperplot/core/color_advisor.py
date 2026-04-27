"""Scientific color recommendation and persistent series-color bindings."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "scientific-color-advisor"
    / "skill"
    / "vendor"
    / "scientific-color-lab-core"
    / "catalog.json"
)

_USAGE_TO_CATALOG = {
    "manuscript": "manuscript",
    "lab-meeting": "lab meeting",
    "poster": "poster",
    "course-slides": "course slides",
    "online-document": "online document",
}

_TONE_TO_CATALOG = {
    "restrained": ["Editorial Minimal", "Publication Clean", "Scientific Neutral"],
    "balanced": ["Publication Clean", "Scientific Neutral", "Nature-like"],
    "strong": ["Presentation Strong", "Nature-like"],
}

_CHART_REQUESTS = {
    "line": {"chart_type": "line-plot", "palette_class": "qualitative"},
    "scatter": {"chart_type": "scatter-plot", "palette_class": "qualitative"},
    "bar": {"chart_type": "bar-chart", "palette_class": "qualitative"},
    "grouped_bar": {"chart_type": "bar-chart", "palette_class": "qualitative"},
    "box": {"chart_type": "bar-chart", "palette_class": "qualitative"},
    "heatmap": {"chart_type": "heatmap", "palette_class": "sequential"},
}

_ROLE_ALIASES = {
    "primary": 0,
    "secondary": 1,
    "tertiary": 2,
    "quaternary": 3,
    "quinary": 4,
}

_DIVERGING_CMAP_NAMES = {
    "coolwarm",
    "bwr",
    "seismic",
    "rdbu",
    "rdbu_r",
    "piyg",
    "brbg",
    "puor",
    "spectral",
}


def apply_color_advisor(spec: Mapping[str, Any], template_spec: Mapping[str, Any]) -> dict[str, Any]:
    """Attach advisor-backed palette recommendations to the resolved spec."""
    resolved = deepcopy(dict(spec))
    policy = resolved.get("color_advisor")
    if not isinstance(policy, Mapping) or not policy.get("enabled"):
        return resolved

    request = _build_request(resolved, resolved.get("template", template_spec), policy)
    chosen = recommend_palette(request)

    palette = deepcopy(dict(resolved.get("palette", {})))
    if request["palette_class"] == "qualitative":
        palette["colors"] = list(chosen["palette"]["hexes"])
    else:
        palette["cmap_colors"] = list(chosen["palette"]["hexes"])
        palette["cmap_class"] = request["palette_class"]
    palette["advisor"] = {
        "request": request,
        "template": chosen["template"],
        "diagnostics": chosen["diagnostics"],
        "why": chosen["why"],
    }
    resolved["palette"] = palette
    return resolved


def resolve_series_color_map(spec: Mapping[str, Any], labels: list[Any]) -> dict[Any, str]:
    """Resolve stable colors for semantic series labels."""
    if not labels:
        return {}

    palette = [str(color) for color in spec.get("palette", {}).get("colors", [])]
    if not palette:
        return {}

    policy = spec.get("color_advisor")
    if not isinstance(policy, Mapping) or not policy.get("enabled"):
        return {label: palette[index % len(palette)] for index, label in enumerate(labels)}

    namespace = str(policy.get("namespace") or "default")
    bindings = policy.get("bindings")
    preferred_order = [str(item) for item in policy.get("preferred_order", []) if item is not None]
    persisted = _load_series_state(policy.get("persist_path"), namespace)
    existing = {key: str(value) for key, value in persisted.items() if isinstance(value, str)}
    existing = {
        key: value
        for key, value in existing.items()
        if value in palette or _is_explicit_hex_binding(bindings, key, value)
    }

    ordered = _sort_labels(labels, preferred_order)
    assigned = set(existing.values())

    for label in ordered:
        label_key = str(label)
        if label_key in existing:
            continue

        bound = _resolve_bound_color(bindings, label_key, palette)
        if bound is not None:
            existing[label_key] = bound
            assigned.add(bound)
            continue

        preferred_index = _preferred_index(label_key, preferred_order)
        if preferred_index is not None and preferred_index < len(palette):
            existing[label_key] = palette[preferred_index]
            assigned.add(palette[preferred_index])
            continue

        next_color = _next_palette_color(palette, assigned, len(existing))
        existing[label_key] = next_color
        assigned.add(next_color)

    _save_series_state(policy.get("persist_path"), namespace, existing)
    return {label: existing[str(label)] for label in labels}


def export_series_color_map(spec: Mapping[str, Any], labels: list[Any]) -> dict[str, Any]:
    """Build a serializable report for advisor-backed series mappings."""
    mapping = resolve_series_color_map(spec, labels)
    policy = spec.get("color_advisor", {})
    advisor = spec.get("palette", {}).get("advisor", {})
    return {
        "enabled": bool(isinstance(policy, Mapping) and policy.get("enabled")),
        "namespace": str(policy.get("namespace") or "default") if isinstance(policy, Mapping) else "default",
        "persist_path": str(policy.get("persist_path")) if isinstance(policy, Mapping) and policy.get("persist_path") else None,
        "series": {str(key): value for key, value in mapping.items()},
        "palette": list(spec.get("palette", {}).get("colors", [])),
        "recommendation": advisor,
    }


def resolve_color_for_label(spec: Mapping[str, Any], label: Any, labels: list[Any] | None = None) -> str | None:
    palette = spec.get("palette", {}).get("colors", [])
    if not palette:
        return None
    if labels is None:
        labels = [label]
    return resolve_series_color_map(spec, labels).get(label)


def build_heatmap_cmap(spec: Mapping[str, Any]):
    """Build a Matplotlib colormap from advisor-selected colors when present."""
    colors = spec.get("palette", {}).get("cmap_colors")
    if not colors:
        return None

    from matplotlib.colors import LinearSegmentedColormap

    cmap_name = spec.get("palette", {}).get("advisor", {}).get("template", {}).get("id", "paperplot-advisor-cmap")
    return LinearSegmentedColormap.from_list(str(cmap_name), list(colors))


def chart_type_request(chart_type: str, template_defaults: Mapping[str, Any] | None = None) -> dict[str, str]:
    request = deepcopy(_CHART_REQUESTS.get(chart_type, {"chart_type": "line-plot", "palette_class": "qualitative"}))
    if chart_type == "heatmap":
        cmap_name = str((template_defaults or {}).get("cmap", "")).lower()
        if cmap_name in _DIVERGING_CMAP_NAMES:
            request["palette_class"] = "diverging"
    return request


def recommend_palette(request: Mapping[str, Any]) -> dict[str, Any]:
    catalog = _load_catalog()
    candidates: list[dict[str, Any]] = []
    for template in catalog:
        if template["chartType"] != request["chart_type"]:
            continue
        if template["paletteClass"] != request["palette_class"]:
            continue
        candidates.append(_score_template(template, request))

    if not candidates:
        raise ValueError(f"No scientific color recommendation found for request: {request}")

    ranked = sorted(
        candidates,
        key=lambda entry: (-entry["score"], -entry["diagnostics"]["score"], entry["template"]["name"]),
    )
    return ranked[0]


def _build_request(
    spec: Mapping[str, Any],
    template_spec: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    chart_request = chart_type_request(template_spec["chart_type"], template_spec.get("defaults"))
    background = str(policy.get("background") or _infer_background(spec)).lower()
    return {
        "target": "scientific-figure",
        "chart_type": str(policy.get("chart_type") or chart_request["chart_type"]),
        "palette_class": str(policy.get("palette_class") or chart_request["palette_class"]),
        "usage": str(policy.get("usage") or "manuscript"),
        "background": background if background in {"light", "dark"} else "light",
        "tone": str(policy.get("tone") or "restrained"),
        "series_count": _normalize_series_count(policy.get("series_count")),
        "priorities": _normalize_flags(policy.get("priorities") or ["colorblind-safe", "grayscale-safe", "avoid-red-green"]),
        "source_colors": [str(item) for item in policy.get("source_colors", []) if item],
    }


@lru_cache(maxsize=1)
def _load_catalog() -> list[dict[str, Any]]:
    with _CATALOG_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise TypeError("Scientific color catalog must be a list.")
    return data


def _infer_background(spec: Mapping[str, Any]) -> str:
    facecolor = str(spec.get("figure", {}).get("facecolor", "white"))
    rgb = _hex_to_rgb(facecolor)
    if rgb is None:
        return "light"
    return "dark" if _relative_luminance(rgb) < 0.35 else "light"


def _normalize_flags(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item) for item in values if item]


def _normalize_series_count(value: Any) -> int | None:
    if value is None:
        return None
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    if count < 1:
        return None
    return count


def _usage_to_catalog(value: str) -> str:
    return _USAGE_TO_CATALOG.get(value, value.replace("-", " "))


def _score_template(template: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    palette = _create_palette(template)
    diagnostics = _check_diagnostics(palette)
    labels = _classify_labels(template, diagnostics)
    usage_match = template.get("academicUsage") == _usage_to_catalog(str(request["usage"]))
    background_match = template.get("backgroundMode") == request["background"]
    score = (
        (30 if template.get("chartType") == request["chart_type"] else 0)
        + (25 if template.get("paletteClass") == request["palette_class"] else 0)
        + (15 if usage_match else 0)
        + (10 if background_match else 0)
        + _template_tone_score(str(request["tone"]), str(template.get("tone")))
        + _priority_score(request, labels, diagnostics)
        + _series_fit_score(request, palette, diagnostics)
        + _source_color_score(request.get("source_colors", []), palette["colors"])
        + round(diagnostics["score"] / 5)
    )
    return {
        "score": score,
        "template": {
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "chart_type": template["chartType"],
            "palette_class": template["paletteClass"],
            "background": template["backgroundMode"],
            "tone": template["tone"],
            "usage": template["academicUsage"],
            "tags": template["tags"],
        },
        "palette": {
            "name": template["name"],
            "hexes": [color["hex"] for color in palette["colors"]],
            "colors": palette["colors"],
        },
        "diagnostics": diagnostics,
        "labels": labels,
        "why": _build_why(template, request, diagnostics),
    }


def _create_palette(template: Mapping[str, Any]) -> dict[str, Any]:
    colors = [_make_color(hex_value, index, str(template["id"])) for index, hex_value in enumerate(template["hexes"])]
    return {
        "id": template["id"],
        "name": template["name"],
        "palette_class": template["paletteClass"],
        "background": template["backgroundMode"],
        "tags": template["tags"],
        "colors": colors,
    }


def _make_color(hex_value: str, index: int, palette_name: str) -> dict[str, Any]:
    rgb = _hex_to_rgb(hex_value) or {"r": 0, "g": 0, "b": 0}
    hsl = _rgb_to_hsl(rgb)
    return {
        "id": f"{palette_name}-{index + 1}",
        "name": f"{palette_name} {index + 1}",
        "hex": _normalize_hex(hex_value),
        "rgb": rgb,
        "hsl": hsl,
        "luminance": _relative_luminance(rgb),
    }


def _check_diagnostics(palette: Mapping[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    background_rgb = {"r": 20, "g": 24, "b": 31} if palette["background"] == "dark" else {"r": 246, "g": 245, "b": 241}

    for color in palette["colors"]:
        contrast = _contrast_ratio(color["rgb"], background_rgb)
        if contrast < 3:
            items.append({"code": "low-interface-contrast", "severity": "warning"})
        if color["hsl"]["s"] > 72:
            items.append({"code": "oversaturation-risk", "severity": "warning"})

    colors = palette["colors"]
    for index, color in enumerate(colors):
        for candidate in colors[index + 1 :]:
            distance = _rgb_distance(color["rgb"], candidate["rgb"])
            if palette["palette_class"] == "qualitative" and distance < 72:
                items.append({"code": "categorical-too-similar", "severity": "warning"})
            if _is_red_green_pair(color, candidate):
                items.append({"code": "red-green-conflict", "severity": "warning"})

    if palette["palette_class"] == "sequential":
        luminances = [color["luminance"] for color in colors]
        if not _is_monotonic(luminances):
            items.append({"code": "sequential-non-monotonic", "severity": "error"})

    if palette["palette_class"] == "diverging":
        midpoint = colors[len(colors) // 2]
        if midpoint["hsl"]["s"] > 20:
            items.append({"code": "diverging-midpoint-chromatic", "severity": "warning"})

    errors = sum(1 for item in items if item["severity"] == "error")
    warnings = sum(1 for item in items if item["severity"] == "warning")
    score = max(25, 100 - (errors * 14) - (warnings * 7))
    status = "healthy"
    if errors > 0 or score < 68:
        status = "high-risk"
    elif warnings > 0 or score < 88:
        status = "needs-attention"
    return {"score": score, "status": status, "items": items}


def _classify_labels(template: Mapping[str, Any], diagnostics: Mapping[str, Any]) -> list[str]:
    labels: set[str] = set()
    codes = {item["code"] for item in diagnostics["items"]}
    if "red-green-conflict" not in codes:
        labels.add("colorblind-safer")
    if (
        "high-contrast" in template.get("tags", [])
        or template.get("structure") == "high-contrast-categorical"
        or template.get("tone") == "Presentation Strong"
    ):
        labels.add("high-contrast")
    if template.get("paletteClass") == "sequential" and "sequential-non-monotonic" not in codes:
        labels.add("ordered-ramp")
    if template.get("paletteClass") == "diverging" and "diverging-midpoint-chromatic" not in codes:
        labels.add("structured-midpoint")
    return sorted(labels)


def _build_why(template: Mapping[str, Any], request: Mapping[str, Any], diagnostics: Mapping[str, Any]) -> list[str]:
    reasons = [
        f"Matches {request['chart_type']} with a {request['palette_class']} palette.",
        f"Fits {str(request['usage']).replace('-', ' ')} usage on a {request['background']} background.",
    ]
    if "high-contrast" in template.get("tags", []):
        reasons.append("Carries strong categorical contrast for figure readability.")
    if not any(item["code"] == "red-green-conflict" for item in diagnostics["items"]):
        reasons.append("Avoids an obvious red/green accessibility conflict.")
    return reasons


def _template_tone_score(request_tone: str, template_tone: str) -> int:
    allowed = _TONE_TO_CATALOG.get(request_tone, [])
    if template_tone not in allowed:
        return 0
    return 12 - (allowed.index(template_tone) * 3)


def _priority_score(request: Mapping[str, Any], labels: list[str], diagnostics: Mapping[str, Any]) -> int:
    diagnostic_codes = {item["code"] for item in diagnostics["items"]}
    score = 0
    for priority in request.get("priorities", []):
        if priority == "high-contrast" and "high-contrast" in labels:
            score += 8
        if priority == "colorblind-safe" and "red-green-conflict" not in diagnostic_codes:
            score += 8
        if priority == "grayscale-safe" and "low-interface-contrast" not in diagnostic_codes:
            score += 6
        if priority == "avoid-red-green" and "red-green-conflict" not in diagnostic_codes:
            score += 8
        if priority == "avoid-rainbow" and "sequential-non-monotonic" not in diagnostic_codes:
            score += 6
    return score


def _source_color_score(source_colors: list[str], colors: list[Mapping[str, Any]]) -> int:
    if not source_colors:
        return 0
    parsed = [_hex_to_rgb(color) for color in source_colors]
    parsed = [color for color in parsed if color is not None]
    if not parsed:
        return 0
    distance = sum(min(_rgb_distance(source, color["rgb"]) for color in colors) for source in parsed) / len(parsed)
    return max(0, 10 - round(distance / 32))


def _series_fit_score(
    request: Mapping[str, Any],
    palette: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
) -> int:
    if request.get("palette_class") != "qualitative":
        return 0

    series_count = _normalize_series_count(request.get("series_count"))
    if series_count is None:
        return 0

    used = palette["colors"][: max(1, min(series_count, len(palette["colors"])))]
    if len(used) <= 1:
        return 0

    pair_distances = [
        _rgb_distance(left["rgb"], right["rgb"])
        for index, left in enumerate(used)
        for right in used[index + 1 :]
    ]
    hue_gaps = [
        _circular_hue_distance(left["hsl"]["h"], right["hsl"]["h"])
        for index, left in enumerate(used)
        for right in used[index + 1 :]
    ]
    luminances = [color["luminance"] for color in used]
    saturations = [color["hsl"]["s"] for color in used]
    background_rgb = {"r": 20, "g": 24, "b": 31} if palette["background"] == "dark" else {"r": 246, "g": 245, "b": 241}
    contrasts = [_contrast_ratio(color["rgb"], background_rgb) for color in used]
    min_distance = min(pair_distances)
    min_hue_gap = min(hue_gaps)
    luminance_span = max(luminances) - min(luminances)
    avg_saturation = sum(saturations) / len(saturations)
    min_contrast = min(contrasts)

    score = 0
    score += _clamp(round((min_distance - 45) / 4), 0, 14)
    score += _clamp(round((min_hue_gap - 18) / 9), 0, 8)
    score += _clamp(round(luminance_span * 20), 0, 4)
    score += _restrained_usage_bonus(request, avg_saturation, min_contrast, min_distance)

    if series_count <= 3:
        score += _clamp(round((min_distance - 55) / 6), 0, 6)

    used_warnings = 0
    if min_distance < 60:
        used_warnings += 1
    if min_hue_gap < 28:
        used_warnings += 1
    if luminance_span < 0.08:
        used_warnings += 1
    if min_contrast < 3:
        used_warnings += 2
    if avg_saturation > 72:
        used_warnings += 2
    if diagnostics["status"] != "healthy" and series_count <= 3:
        used_warnings += 1

    return score - (used_warnings * 3)


def _restrained_usage_bonus(
    request: Mapping[str, Any],
    avg_saturation: float,
    min_contrast: float,
    min_distance: float,
) -> int:
    if request.get("usage") != "manuscript" or request.get("tone") != "restrained":
        return 0

    score = 0
    if 18 <= avg_saturation <= 52:
        score += 10
    elif avg_saturation <= 65:
        score += 4
    else:
        score -= 10

    if min_contrast >= 3.2:
        score += 6
    elif min_contrast < 2.8:
        score -= 8

    if 65 <= min_distance <= 150:
        score += 5
    elif min_distance > 230:
        score -= 4

    return score


def _sort_labels(labels: list[Any], preferred_order: list[str]) -> list[Any]:
    preferred_index = {label: index for index, label in enumerate(preferred_order)}
    return sorted(labels, key=lambda label: (preferred_index.get(str(label), len(preferred_order)), labels.index(label)))


def _preferred_index(label: str, preferred_order: list[str]) -> int | None:
    try:
        return preferred_order.index(label)
    except ValueError:
        return None


def _resolve_bound_color(bindings: Any, label: str, palette: list[str]) -> str | None:
    if not isinstance(bindings, Mapping) or label not in bindings:
        return None
    binding = bindings[label]
    if isinstance(binding, str) and binding.startswith("#"):
        return _normalize_hex(binding)
    if isinstance(binding, str):
        role = binding.strip().lower()
        if role in _ROLE_ALIASES and _ROLE_ALIASES[role] < len(palette):
            return palette[_ROLE_ALIASES[role]]
        if role.startswith("color-"):
            try:
                index = int(role.split("-", 1)[1]) - 1
            except ValueError:
                return None
            if 0 <= index < len(palette):
                return palette[index]
    return None


def _is_explicit_hex_binding(bindings: Any, label: str, color: str) -> bool:
    if not isinstance(bindings, Mapping) or label not in bindings:
        return False
    binding = bindings[label]
    return isinstance(binding, str) and binding.startswith("#") and _normalize_hex(binding) == _normalize_hex(color)


def _next_palette_color(palette: list[str], assigned: set[str], offset: int) -> str:
    for color in palette:
        if color not in assigned:
            return color
    return palette[offset % len(palette)]


def _load_series_state(path_value: Any, namespace: str) -> dict[str, str]:
    path = _coerce_path(path_value)
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {}
    papers = payload.get("papers", {})
    if not isinstance(papers, dict):
        return {}
    state = papers.get(namespace, {})
    if not isinstance(state, dict):
        return {}
    series = state.get("series", {})
    return dict(series) if isinstance(series, dict) else {}


def _save_series_state(path_value: Any, namespace: str, series: Mapping[str, str]) -> None:
    path = _coerce_path(path_value)
    if path is None:
        return
    payload: dict[str, Any] = {"version": 1, "papers": {}}
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict):
            payload = loaded
            payload.setdefault("version", 1)
            payload.setdefault("papers", {})
    payload["papers"].setdefault(namespace, {})
    payload["papers"][namespace]["series"] = dict(series)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _coerce_path(value: Any) -> Path | None:
    if value in {None, ""}:
        return None
    return Path(str(value))


def _normalize_hex(value: str) -> str:
    raw = value if value.startswith("#") else f"#{value}"
    return raw.upper()


def _hex_to_rgb(value: str) -> dict[str, int] | None:
    normalized = value.strip()
    named = {
        "white": "#FFFFFF",
        "black": "#000000",
    }
    normalized = named.get(normalized.lower(), normalized)
    if not normalized.startswith("#"):
        return None
    body = normalized[1:]
    if len(body) != 6:
        return None
    try:
        return {
            "r": int(body[0:2], 16),
            "g": int(body[2:4], 16),
            "b": int(body[4:6], 16),
        }
    except ValueError:
        return None


def _rgb_distance(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    dr = left["r"] - right["r"]
    dg = left["g"] - right["g"]
    db = left["b"] - right["b"]
    return math.sqrt((dr * dr) + (dg * dg) + (db * db))


def _circular_hue_distance(left: float, right: float) -> float:
    delta = abs(left - right) % 360
    return min(delta, 360 - delta)


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def _relative_luminance(rgb: Mapping[str, int]) -> float:
    def _convert(channel: int) -> float:
        unit = channel / 255.0
        return unit / 12.92 if unit <= 0.03928 else ((unit + 0.055) / 1.055) ** 2.4

    red = _convert(rgb["r"])
    green = _convert(rgb["g"])
    blue = _convert(rgb["b"])
    return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)


def _contrast_ratio(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    luminance_left = _relative_luminance(left)
    luminance_right = _relative_luminance(right)
    lighter = max(luminance_left, luminance_right)
    darker = min(luminance_left, luminance_right)
    return (lighter + 0.05) / (darker + 0.05)


def _rgb_to_hsl(rgb: Mapping[str, int]) -> dict[str, float]:
    red = rgb["r"] / 255.0
    green = rgb["g"] / 255.0
    blue = rgb["b"] / 255.0
    maximum = max(red, green, blue)
    minimum = min(red, green, blue)
    delta = maximum - minimum
    hue = 0.0
    if delta != 0:
        if maximum == red:
            hue = ((green - blue) / delta) % 6
        elif maximum == green:
            hue = ((blue - red) / delta) + 2
        else:
            hue = ((red - green) / delta) + 4
        hue *= 60
    lightness = (maximum + minimum) / 2
    saturation = 0.0 if delta == 0 else delta / (1 - abs((2 * lightness) - 1))
    return {
        "h": round(hue, 1),
        "s": round(saturation * 100, 1),
        "l": round(lightness * 100, 1),
    }


def _is_red_green_pair(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_hue = left["hsl"]["h"]
    right_hue = right["hsl"]["h"]
    red_green = (
        ((left_hue <= 25 or left_hue >= 335) and 95 <= right_hue <= 155)
        or ((right_hue <= 25 or right_hue >= 335) and 95 <= left_hue <= 155)
    )
    return red_green and abs(left["luminance"] - right["luminance"]) < 0.14


def _is_monotonic(values: list[float]) -> bool:
    if len(values) < 2:
        return True
    ascending = values[1] >= values[0]
    for index in range(1, len(values)):
        if ascending and values[index] < values[index - 1]:
            return False
        if not ascending and values[index] > values[index - 1]:
            return False
    return True
