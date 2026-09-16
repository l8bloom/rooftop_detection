"""Count the features in a GeoJSON FeatureCollection by geometry type and property value."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

PROG = "geojson-summary"
STDIN_PATH = "-"
MISSING_KEY = "missing"


class SummaryError(Exception):
    """A failure that maps to one stderr line and one exit code."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message


def display_name(path: str) -> str:
    return "<stdin>" if path == STDIN_PATH else path


def read_document(path: str) -> str:
    try:
        if path == STDIN_PATH:
            return sys.stdin.read()
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SummaryError(1, f"cannot read {display_name(path)}: {exc}") from exc


def _not_feature_collection(name: str, reason: str) -> SummaryError:
    return SummaryError(4, f"{name} is not a GeoJSON FeatureCollection: {reason}")


def load_feature_collection(path: str) -> dict[str, Any]:
    name = display_name(path)
    text = read_document(path)
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SummaryError(3, f"{name} is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise _not_feature_collection(name, "top-level value is not an object")
    if document.get("type") != "FeatureCollection":
        found = document.get("type")
        raise _not_feature_collection(name, f"type is {found!r}, expected 'FeatureCollection'")
    if not isinstance(document.get("features"), list):
        raise _not_feature_collection(name, "features is missing or not an array")
    return document


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def group_property_values(
    features: list[Any], property_name: str, name: str
) -> list[dict[str, Any]]:
    groups: dict[str, list[Any]] = {}
    missing = 0
    for index, feature in enumerate(features):
        properties = feature.get("properties")
        if properties is not None and not isinstance(properties, dict):
            raise _not_feature_collection(
                name, f"features[{index}].properties is not null or an object"
            )
        if properties is None or property_name not in properties:
            missing += 1
            continue
        value = properties[property_name]
        group = groups.setdefault(canonical(value), [value, 0])
        group[1] += 1
    entries: list[dict[str, Any]] = [
        {"value": value, "count": count} for _, (value, count) in sorted(groups.items())
    ]
    if missing > 0:
        entries.append({MISSING_KEY: True, "count": missing})
    return entries


def summarize(collection: dict[str, Any], name: str, group_by: str | None = None) -> dict[str, Any]:
    features = collection["features"]
    counter: Counter[str] = Counter()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            raise _not_feature_collection(name, f"features[{index}] is not an object")
        geometry = feature.get("geometry")
        if geometry is None:
            counter["null"] += 1
        elif isinstance(geometry, dict) and isinstance(geometry.get("type"), str):
            counter[geometry["type"]] += 1
        else:
            raise _not_feature_collection(
                name, f"features[{index}].geometry is not null or an object with a string type"
            )
    summary: dict[str, Any] = {
        "feature_count": len(features),
        "geometry_type_counts": dict(counter),
    }
    if group_by is not None:
        summary["property_value_counts"] = group_property_values(features, group_by, name)
    return summary


def render(summary: dict[str, Any]) -> str:
    return json.dumps(summary, sort_keys=True, indent=2) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Count the features in a GeoJSON FeatureCollection by geometry type.",
    )
    parser.add_argument("path", help="file path, or - for standard input")
    parser.add_argument(
        "--group-by",
        metavar="PROPERTY",
        dest="group_by",
        default=None,
        help="count features by the exact JSON value of this property",
    )
    args = parser.parse_args(argv)
    try:
        collection = load_feature_collection(args.path)
        summary = summarize(collection, display_name(args.path), args.group_by)
    except SummaryError as error:
        sys.stderr.write(f"{PROG}: {error.message}\n")
        return error.exit_code
    sys.stdout.write(render(summary))
    return 0
