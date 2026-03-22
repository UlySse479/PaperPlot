"""Command-line interface for PaperPlot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from paperplot import (
    autoload_project_assets,
    list_plotters,
    list_profiles,
    list_styles,
    list_templates,
    plot_from_config,
    render_gallery,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="paperplot")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print structured JSON output.")
    parser.add_argument("--quiet", action="store_true", help="Suppress normal stdout output.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="Render a figure from a config file.")
    render_parser.add_argument("config", help="Path to a PaperPlot config file or directory.")
    render_parser.add_argument("--assets", action="append", default=[], help="Optional asset root to load before rendering. Can be passed multiple times.")
    render_parser.add_argument("--project-root", default=".", help="Root used for automatic project asset discovery. Defaults to the current directory.")
    render_parser.add_argument("--output", help="Override the output path defined in the config.")
    render_parser.add_argument("--glob", default="*.json,*.yaml,*.yml", help="Comma-separated patterns used when rendering a directory of configs.")

    gallery_parser = subparsers.add_parser("gallery", help="Render the built-in example gallery.")
    gallery_parser.add_argument("output_dir", help="Directory to write gallery images into.")

    assets_parser = subparsers.add_parser("assets", help="Load project-local assets and print a summary.")
    assets_parser.add_argument("path", nargs="?", default=".", help="Asset root or project root. Defaults to the current directory.")
    assets_parser.add_argument("--direct", action="store_true", help="Treat the path as a direct asset directory with profiles/styles/templates subdirectories.")

    validate_parser = subparsers.add_parser("validate", help="Backward-compatible validation wrapper. Prefer validate-config or validate-assets.")
    validate_parser.add_argument("target", nargs="?", default=".", help="Config path, config directory, or asset/project directory.")
    validate_parser.add_argument("--assets", action="append", default=[], help="Optional asset root to load before validating configs. Can be passed multiple times.")
    validate_parser.add_argument("--project-root", default=".", help="Root used for automatic project asset discovery. Defaults to the current directory.")
    validate_parser.add_argument("--direct-assets", action="store_true", help="Treat the target as a direct asset directory with profiles/styles/templates subdirectories.")
    validate_parser.add_argument("--glob", default="*.json,*.yaml,*.yml", help="Comma-separated patterns used when validating a directory of configs.")

    validate_config_parser = subparsers.add_parser("validate-config", help="Validate config files without rendering.")
    validate_config_parser.add_argument("target", help="Config file or directory of config files.")
    validate_config_parser.add_argument("--assets", action="append", default=[], help="Optional asset root to load before validating configs. Can be passed multiple times.")
    validate_config_parser.add_argument("--project-root", default=".", help="Root used for automatic project asset discovery. Defaults to the current directory.")
    validate_config_parser.add_argument("--glob", default="*.json,*.yaml,*.yml", help="Comma-separated patterns used when validating a directory of configs.")

    validate_assets_parser = subparsers.add_parser("validate-assets", help="Validate asset directories or project roots without rendering.")
    validate_assets_parser.add_argument("target", nargs="?", default=".", help="Asset root or project root. Defaults to the current directory.")
    validate_assets_parser.add_argument("--direct", action="store_true", help="Treat the target as a direct asset directory with profiles/styles/templates subdirectories.")

    list_parser = subparsers.add_parser("list", help="List registered profiles, styles, templates, or plotters.")
    list_parser.add_argument("kind", nargs="?", choices=("profiles", "styles", "templates", "plotters", "all"), default="all", help="Registry kind to list. Defaults to all.")

    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return _run(args)
    except Exception as exc:
        return _handle_cli_error(exc, args.json_output, args.quiet)


def _run(args: argparse.Namespace) -> int:
    if args.command == "render":
        from paperplot.core.config import load_plot_config

        _autoload_for_command(args.project_root, args.assets)
        targets = _collect_config_targets(Path(args.config), args.glob)
        if not targets:
            raise FileNotFoundError(f"No config files found under {args.config}")
        if args.output and len(targets) > 1:
            raise ValueError("--output can only be used with a single config file.")

        results: list[str] = []
        for target in targets:
            payload = load_plot_config(target)
            if args.output:
                figure = payload.setdefault("figure", {})
                if not isinstance(figure, dict):
                    raise TypeError("'figure' section must be a mapping.")
                figure["output"] = args.output
            plot_from_config(payload)
            results.append(_configured_output_from_payload(payload) or str(target))
        _emit(results if len(results) > 1 else results[0], args.json_output, args.quiet)
        return 0

    if args.command == "gallery":
        written = [str(path) for path in render_gallery(args.output_dir)]
        _emit(written, args.json_output, args.quiet)
        return 0

    if args.command == "assets":
        from paperplot import load_assets_from_dir

        payload = load_assets_from_dir(args.path) if args.direct else autoload_project_assets(args.path)
        _emit(payload, args.json_output, args.quiet)
        return 0

    if args.command == "validate-config":
        payload = _validate_configs(args.target, args.project_root, args.assets, args.glob)
        _emit(payload, True if args.json_output else True, args.quiet)
        return 0

    if args.command == "validate-assets":
        payload = _validate_assets(args.target, args.direct)
        _emit(payload, True if args.json_output else True, args.quiet)
        return 0

    if args.command == "validate":
        target = Path(args.target)
        if args.direct_assets or _looks_like_asset_root(target) or (
            target.is_dir() and any(autoload_project_assets(target).values()) and target.name != "configs"
        ):
            payload = _validate_assets(args.target, args.direct_assets)
        else:
            payload = _validate_configs(args.target, args.project_root, args.assets, args.glob)
        _emit(payload, True if args.json_output else True, args.quiet)
        return 0

    if args.command == "list":
        _emit(_list_payload(args.kind), args.json_output, args.quiet)
        return 0

    raise AssertionError(f"Unhandled CLI command: {args.command}")


def _autoload_for_command(project_root: str, assets: list[str]) -> None:
    autoload_project_assets(project_root)
    for asset_path in assets:
        autoload_project_assets(asset_path)


def _validate_configs(target: str, project_root: str, assets: list[str], glob_text: str) -> dict[str, list[str]]:
    from paperplot.core.config import load_plot_config

    _autoload_for_command(project_root, assets)
    targets = _collect_config_targets(Path(target), glob_text)
    if not targets:
        raise FileNotFoundError(f"No config files found under {target}")

    validated: list[str] = []
    for config_path in targets:
        payload = load_plot_config(config_path)
        spec = _validate_config_payload(payload)
        validated.append(spec["template"]["name"])
    return {"configs": [str(path) for path in targets], "templates": validated}


def _validate_assets(target: str, direct: bool) -> dict[str, Any]:
    from paperplot import load_assets_from_dir

    loaded = load_assets_from_dir(target) if direct else autoload_project_assets(target)
    return {"assets": loaded}


def _configured_output_from_payload(payload: dict[str, Any]) -> str | None:
    figure = payload.get("figure", {})
    if not isinstance(figure, dict):
        return None
    output = figure.get("output")
    return str(output) if output is not None else None


def _collect_config_targets(path: Path, pattern_text: str) -> list[Path]:
    if path.is_file():
        return [path]

    patterns = [pattern.strip() for pattern in pattern_text.split(",") if pattern.strip()]
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(sorted(path.glob(pattern)))

    unique: list[Path] = []
    seen: set[Path] = set()
    for item in matches:
        if item.is_file() and item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


def _looks_like_asset_root(path: Path) -> bool:
    return any((path / name).exists() for name in ("profiles", "styles", "templates"))


def _validate_config_payload(payload: dict[str, Any]) -> dict[str, Any]:
    from paperplot.core.config import resolve_figure_spec

    paper = payload.get("paper", {})
    figure = payload.get("figure", {})
    if not isinstance(paper, dict):
        raise TypeError("'paper' section must be a mapping when present.")
    if not isinstance(figure, dict):
        raise TypeError("'figure' section must be a mapping.")

    template = figure.get("template")
    data = figure.get("data")
    if template is None:
        raise ValueError("Figure config must define 'template'.")
    if data is None:
        raise ValueError("Figure config must define 'data'.")

    return resolve_figure_spec(
        template=template,
        profile=paper.get("profile"),
        visual=paper.get("style"),
        size=figure.get("size"),
        override=figure.get("override"),
    )


def _list_payload(kind: str) -> dict[str, list[str]] | list[str]:
    registry_map = {
        "profiles": list_profiles,
        "styles": list_styles,
        "templates": list_templates,
        "plotters": list_plotters,
    }
    if kind == "all":
        return {name: getter() for name, getter in registry_map.items()}
    return registry_map[kind]()


def _emit(payload: Any, json_output: bool, quiet: bool) -> None:
    if quiet:
        return
    if json_output or isinstance(payload, dict):
        print(json.dumps(payload, sort_keys=True))
        return
    if isinstance(payload, list):
        for item in payload:
            print(item)
        return
    print(payload)


def _handle_cli_error(exc: Exception, json_output: bool, quiet: bool) -> int:
    if quiet:
        return 1
    if json_output:
        print(json.dumps({"error": str(exc), "type": exc.__class__.__name__}, sort_keys=True), file=sys.stderr)
    else:
        print(f"{exc.__class__.__name__}: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
