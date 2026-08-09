from shapely.geometry import Polygon, mapping, shape

from rooftop_detection.detect import _clean_polygonal, _quality_metrics


def test_clean_polygonal_preserves_holes_and_serializes_as_geojson() -> None:
    roof = Polygon(
        [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
        holes=[[(3, 3), (7, 3), (7, 7), (3, 7), (3, 3)]],
    )

    cleaned = _clean_polygonal(roof)

    assert cleaned is not None
    serialized = mapping(cleaned)
    assert shape(serialized).equals(cleaned)
    assert len(serialized["coordinates"]) == 2
    assert cleaned.area == 84


def test_quality_metrics_penalize_undersegmentation() -> None:
    footprint = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    complete = footprint.buffer(-0.5)
    partial = Polygon([(0, 0), (5, 0), (5, 10), (0, 10)])

    complete_metrics = _quality_metrics(complete, footprint, sam_score=0.8)
    partial_metrics = _quality_metrics(partial, footprint, sam_score=0.8)

    assert complete_metrics[1] > partial_metrics[1]
    assert complete_metrics[4] > partial_metrics[4]


def test_clean_polygonal_removes_only_small_mask_holes() -> None:
    roof = Polygon(
        [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)],
        holes=[
            [(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)],
            [(5, 5), (10, 5), (10, 10), (5, 10), (5, 5)],
        ],
    )

    cleaned = _clean_polygonal(roof)

    assert cleaned is not None
    assert len(cleaned.interiors) == 1
    assert cleaned.area == 375


def test_clean_polygonal_fills_holes_not_supported_by_footprint() -> None:
    roof = Polygon(
        [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)],
        holes=[[(5, 5), (10, 5), (10, 10), (5, 10), (5, 5)]],
    )
    footprint_without_courtyard = Polygon([(0, 0), (20, 0), (20, 20), (0, 20)])

    cleaned = _clean_polygonal(roof, hole_reference=footprint_without_courtyard)

    assert cleaned is not None
    assert len(cleaned.interiors) == 0
    assert cleaned.area == 400
