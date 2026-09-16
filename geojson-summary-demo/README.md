# geojson-summary-demo

A command-line program that reads a GeoJSON FeatureCollection and writes deterministic JSON with the feature count and counts by geometry type. An optional `--group-by PROPERTY` adds counts by the exact JSON value of one property. It uses only the Python standard library at runtime and ships no Dockerfile.

Run every command from `geojson-summary-demo/`.

## Install

```bash
python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
```

## Run

```bash
geojson-summary ../data/input/buildings.geojson
```

```json
{
  "feature_count": 10,
  "geometry_type_counts": {
    "MultiPolygon": 3,
    "Polygon": 7
  }
}
```

### Read from standard input

Pass `-` as the path to read the document from standard input. The first two commands print the same output as the file example; the third shows the malformed case:

```bash
geojson-summary - < ../data/input/buildings.geojson
cat ../data/input/buildings.geojson | geojson-summary -
printf '{' | geojson-summary -; echo "exit $?"
```

```
geojson-summary: <stdin> is not valid JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
exit 3
```

### Group by a property

`--group-by PROPERTY` adds `property_value_counts`: values are grouped by exact JSON type and value, entries are sorted by their canonical JSON text, features without the property are counted in one final `missing` entry, and output is ASCII with non-ASCII characters written as JSON unicode escapes.

```bash
printf '%s' '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":null,"properties":{"kind":"A"}},{"type":"Feature","geometry":null,"properties":{"kind":"B"}},{"type":"Feature","geometry":null,"properties":{"kind":"A"}},{"type":"Feature","geometry":null,"properties":{}}]}' | geojson-summary --group-by kind -
```

```json
{
  "feature_count": 4,
  "geometry_type_counts": {
    "null": 4
  },
  "property_value_counts": [
    {
      "count": 2,
      "value": "A"
    },
    {
      "count": 1,
      "value": "B"
    },
    {
      "count": 1,
      "missing": true
    }
  ]
}
```

## Test

```bash
python -m pytest
```

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Unreadable input |
| 2 | Usage error |
| 3 | Malformed JSON |
| 4 | Not a FeatureCollection, or a feature with invalid `geometry` or `properties` |

Messages name standard input as `<stdin>`.
