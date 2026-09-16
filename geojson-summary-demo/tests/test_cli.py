import io
import json
import sys
from pathlib import Path

import pytest

from geojson_summary.cli import canonical, main

POINT = {"type": "Point", "coordinates": [0, 0]}
LINE = {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}
POLYGON = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}

MIXED_FEATURES = [
    {"type": "Feature", "geometry": POINT, "properties": {"kind": "A"}},
    {"type": "Feature", "geometry": LINE, "properties": {"kind": "B"}},
    {"type": "Feature", "geometry": POINT, "properties": {"kind": "A"}},
    {"type": "Feature", "geometry": POLYGON, "properties": {}},
    {"type": "Feature", "geometry": None, "properties": {"name": "no geometry"}},
    {"type": "Feature", "properties": {}},
]


def collection(features: list) -> dict:
    return {"type": "FeatureCollection", "features": features}


MIXED = json.dumps(collection(MIXED_FEATURES))
MIXED_EXPECTED = (
    "{\n"
    '  "feature_count": 6,\n'
    '  "geometry_type_counts": {\n'
    '    "LineString": 1,\n'
    '    "Point": 2,\n'
    '    "Polygon": 1,\n'
    '    "null": 2\n'
    "  }\n"
    "}\n"
)
MALFORMED_STDIN_ERROR = (
    "geojson-summary: <stdin> is not valid JSON: "
    "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)\n"
)


def write(tmp_path: Path, name: str, text: str) -> str:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_features(tmp_path: Path, name: str, features: list) -> str:
    return write(tmp_path, name, json.dumps(collection(features)))


def with_props(properties) -> dict:
    return {"type": "Feature", "geometry": POINT, "properties": properties}


def run(argv: list[str], capsys) -> tuple[int, str, str]:
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def gb(key: str, path: str, capsys) -> tuple[int, str, str]:
    return run(["--group-by", key, path], capsys)


def test_counts_mixed_geometries(tmp_path, capsys):
    code, out, err = run([write(tmp_path, "mixed.geojson", MIXED)], capsys)
    assert code == 0
    assert err == ""
    assert json.loads(out) == {
        "feature_count": 6,
        "geometry_type_counts": {"LineString": 1, "Point": 2, "Polygon": 1, "null": 2},
    }


def test_output_bytes_are_deterministic(tmp_path, capsys):
    path = write_features(tmp_path, "reversed.geojson", list(reversed(MIXED_FEATURES)))
    first = run([path], capsys)
    second = run([path], capsys)
    assert first[1] == MIXED_EXPECTED
    assert first == second


def test_empty_feature_collection(tmp_path, capsys):
    code, out, _ = run([write_features(tmp_path, "empty.geojson", [])], capsys)
    assert code == 0
    assert json.loads(out) == {"feature_count": 0, "geometry_type_counts": {}}


def test_stdin_feature_collection(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(MIXED))
    code, out, err = run(["-"], capsys)
    assert code == 0
    assert err == ""
    assert out == MIXED_EXPECTED


def test_stdin_malformed_json(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("{"))
    code, out, err = run(["-"], capsys)
    assert code == 3
    assert out == ""
    assert err == MALFORMED_STDIN_ERROR


def test_missing_file(tmp_path, capsys):
    path = str(tmp_path / "missing.geojson")
    code, out, err = run([path], capsys)
    assert code == 1
    assert out == ""
    assert err.startswith("geojson-summary: cannot read ")
    assert path in err


def test_directory_path(tmp_path, capsys):
    code, out, err = run([str(tmp_path)], capsys)
    assert code == 1
    assert out == ""
    assert err.startswith("geojson-summary: cannot read ")


def test_malformed_json(tmp_path, capsys):
    code, out, err = run([write(tmp_path, "broken.geojson", '{"type": ')], capsys)
    assert code == 3
    assert out == ""
    assert " is not valid JSON: " in err


def test_top_level_not_object(tmp_path, capsys):
    code, _, err = run([write(tmp_path, "array.geojson", "[]")], capsys)
    assert code == 4
    assert err.rstrip("\n").endswith("top-level value is not an object")


def test_wrong_type_value(tmp_path, capsys):
    text = json.dumps({"type": "Feature", "features": []})
    code, _, err = run([write(tmp_path, "feature.geojson", text)], capsys)
    assert code == 4
    assert "type is 'Feature', expected 'FeatureCollection'" in err


def test_features_not_array(tmp_path, capsys):
    text = json.dumps({"type": "FeatureCollection", "features": {}})
    code, _, err = run([write(tmp_path, "object.geojson", text)], capsys)
    assert code == 4
    assert err.rstrip("\n").endswith("features is missing or not an array")


def test_feature_not_object(tmp_path, capsys):
    code, _, err = run([write_features(tmp_path, "number.geojson", [1])], capsys)
    assert code == 4
    assert "features[0] is not an object" in err


def test_geometry_not_object(tmp_path, capsys):
    features = [{"type": "Feature", "geometry": "Point"}]
    code, _, err = run([write_features(tmp_path, "geometry.geojson", features)], capsys)
    assert code == 4
    assert "features[0].geometry is not null or an object with a string type" in err


def test_usage_error_without_path():
    with pytest.raises(SystemExit) as raised:
        main([])
    assert raised.value.code == 2


def test_group_by_repeated_values(tmp_path, capsys):
    features = [with_props({"kind": k}) for k in ("A", "B", "A")]
    path = write_features(tmp_path, "kinds.geojson", features)
    code, out, _ = gb("kind", path, capsys)
    plain = json.loads(run([path], capsys)[1])
    summary = json.loads(out)
    assert code == 0
    assert summary["property_value_counts"] == [
        {"count": 2, "value": "A"},
        {"count": 1, "value": "B"},
    ]
    assert summary["feature_count"] == plain["feature_count"]
    assert summary["geometry_type_counts"] == plain["geometry_type_counts"]


def test_group_by_distinguishes_json_types(tmp_path, capsys):
    features = [with_props({"v": v}) for v in (1, "1", 1.0, True, None)]
    code, out, _ = gb("v", write_features(tmp_path, "types.geojson", features), capsys)
    entries = json.loads(out)["property_value_counts"]
    assert code == 0
    assert [canonical(entry["value"]) for entry in entries] == ['"1"', "1", "1.0", "null", "true"]
    assert all(entry["count"] == 1 for entry in entries)
    assert '"value": 1.0' in out
    assert '"value": true' in out


def test_group_by_missing_values(tmp_path, capsys):
    features = [
        {"type": "Feature", "geometry": POINT},
        with_props(None),
        with_props({}),
        with_props({"v": None}),
    ]
    code, out, _ = gb("v", write_features(tmp_path, "missing.geojson", features), capsys)
    assert code == 0
    assert json.loads(out)["property_value_counts"] == [
        {"count": 1, "value": None},
        {"count": 3, "missing": True},
    ]


def test_group_by_ordering_is_deterministic(tmp_path, capsys):
    features = [with_props({"v": v}) for v in ("b", "10", "B", "9")] + [with_props({})]
    first = write_features(tmp_path, "first.geojson", features)
    second = write_features(tmp_path, "second.geojson", list(reversed(features)))
    out_first = gb("v", first, capsys)[1]
    out_second = gb("v", second, capsys)[1]
    entries = json.loads(out_first)["property_value_counts"]
    assert out_first == out_second
    assert [entry["value"] for entry in entries[:-1]] == ["10", "9", "B", "b"]
    assert entries[-1] == {"count": 1, "missing": True}


def test_group_by_object_values_use_canonical_form(tmp_path, capsys):
    values = [{"a": 1, "b": 2}, {"b": 2, "a": 1}, [1, 2], [2, 1]]
    features = [with_props({"v": v}) for v in values]
    code, out, _ = gb("v", write_features(tmp_path, "objects.geojson", features), capsys)
    assert code == 0
    assert json.loads(out)["property_value_counts"] == [
        {"count": 1, "value": [1, 2]},
        {"count": 1, "value": [2, 1]},
        {"count": 2, "value": {"a": 1, "b": 2}},
    ]


def test_group_by_from_stdin(tmp_path, monkeypatch, capsys):
    features = [with_props({"kind": k}) for k in ("A", "B", "A")]
    text = json.dumps(collection(features))
    from_file = gb("kind", write(tmp_path, "kinds.geojson", text), capsys)
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))
    from_stdin = gb("kind", "-", capsys)
    assert from_stdin[0] == 0
    assert from_stdin[1] == from_file[1]


def test_default_output_unchanged_with_properties(tmp_path, capsys):
    _, out, _ = run([write(tmp_path, "mixed.geojson", MIXED)], capsys)
    assert out == MIXED_EXPECTED
    assert "property_value_counts" not in out


def test_group_by_rejects_non_object_properties(tmp_path, capsys):
    path = write_features(tmp_path, "props.geojson", [with_props([])])
    code, out, err = gb("v", path, capsys)
    assert code == 4
    assert out == ""
    assert "features[0].properties is not null or an object" in err
    assert run([path], capsys)[0] == 0
