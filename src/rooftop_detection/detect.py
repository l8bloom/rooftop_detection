"""Prompt SAM2 with official building footprints and export roof polygons."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import rasterio
import torch
from affine import Affine
from PIL import Image
from pyproj import Transformer
from rasterio.features import rasterize, shapes
from rasterio.windows import Window
from shapely import make_valid
from shapely.geometry import Point, Polygon, mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform, unary_union
from transformers import Sam2Model, Sam2Processor


@dataclass(frozen=True)
class Candidate:
    """One vectorised SAM mask and its image/footprint quality signals."""

    mask: np.ndarray
    geometry: BaseGeometry
    sam_score: float
    precision: float
    coverage: float
    iou: float
    area_ratio: float
    selection_score: float
    prompt_strategy: str


def _polygon_parts(geometry: BaseGeometry) -> list[Polygon]:
    """Flatten all polygonal parts from a possibly mixed valid geometry."""
    if geometry.is_empty:
        return []
    if geometry.geom_type == "Polygon":
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [part for child in geometry.geoms for part in _polygon_parts(child)]
    return []


def _clean_polygonal(
    geometry: BaseGeometry,
    minimum_area_m2: float = 3.0,
    hole_reference: BaseGeometry | None = None,
) -> BaseGeometry | None:
    """Repair, filter and lightly simplify a polygonal mask geometry."""
    parts = [part for part in _polygon_parts(make_valid(geometry)) if part.area >= minimum_area_m2]
    if not parts:
        return None
    cleaned = make_valid(unary_union(parts).simplify(0.3, preserve_topology=True))
    reference_holes = (
        [Polygon(ring) for part in _polygon_parts(hole_reference) for ring in part.interiors]
        if hole_reference is not None
        else None
    )
    cleaned_parts = []
    for part in _polygon_parts(cleaned):
        if part.area < minimum_area_m2:
            continue
        meaningful_holes = []
        for ring in part.interiors:
            hole = Polygon(ring)
            large_enough = hole.area >= 10.0
            reference_supported = reference_holes is None or any(
                hole.intersection(reference.buffer(1.0)).area / hole.area >= 0.5
                for reference in reference_holes
            )
            if large_enough and reference_supported:
                meaningful_holes.append(ring.coords)
        cleaned_parts.append(Polygon(part.exterior.coords, meaningful_holes))
    return make_valid(unary_union(cleaned_parts)) if cleaned_parts else None


def _mask_geometry(
    mask: np.ndarray, crop_transform: Affine, footprint: BaseGeometry
) -> BaseGeometry | None:
    """Vectorise all meaningful connected SAM mask components in map coordinates."""
    polygons = [
        shape(geometry)
        for geometry, value in shapes(mask, mask=mask.astype(bool), transform=crop_transform)
        if value
    ]
    return _clean_polygonal(unary_union(polygons), hole_reference=footprint) if polygons else None


def _quality_metrics(
    roof: BaseGeometry, footprint: BaseGeometry, sam_score: float, tolerance_m: float = 1.0
) -> tuple[float, float, float, float, float]:
    """Return precision, coverage, IoU, area ratio and composite selection score."""
    footprint = make_valid(footprint)
    buffered_footprint = footprint.buffer(tolerance_m)
    precision = roof.intersection(buffered_footprint).area / roof.area
    coverage = roof.buffer(tolerance_m).intersection(footprint).area / footprint.area
    intersection = roof.intersection(footprint).area
    union = roof.union(footprint).area
    iou = intersection / union
    area_ratio = roof.area / footprint.area
    selection_score = 0.55 * sam_score + 0.15 * precision + 0.20 * coverage + 0.10 * iou
    return precision, coverage, iou, area_ratio, selection_score


def _crop_for_building(source, geometry: BaseGeometry, padding_m: float):
    """Read a padded RGB crop and return its pixel-space prompt box and transform."""
    inverse = ~source.transform
    min_x, min_y, max_x, max_y = geometry.bounds
    left, top = inverse * (min_x - padding_m, max_y + padding_m)
    right, bottom = inverse * (max_x + padding_m, min_y - padding_m)
    left, top = max(0, int(np.floor(left))), max(0, int(np.floor(top)))
    right, bottom = min(source.width, int(np.ceil(right))), min(source.height, int(np.ceil(bottom)))
    window = Window(left, top, right - left, bottom - top)
    pixels = source.read(indexes=(1, 2, 3), window=window)
    image = Image.fromarray(pixels.transpose(1, 2, 0), mode="RGB")
    crop_transform = source.transform * Affine.translation(left, top)
    to_crop = ~crop_transform
    box_left, box_top = to_crop * (min_x, max_y)
    box_right, box_bottom = to_crop * (max_x, min_y)
    box = [[[float(box_left), float(box_top), float(box_right), float(box_bottom)]]]
    return image, box, crop_transform


def _spaced_points(
    points: list[Point], scores: list[float], maximum: int, separation_m: float
) -> list[Point]:
    """Select high-value points while keeping prompts spatially distributed."""
    selected: list[Point] = []
    for _, point in sorted(
        zip(scores, points, strict=True), reverse=True, key=lambda item: item[0]
    ):
        if all(point.distance(other) >= separation_m for other in selected):
            selected.append(point)
        if len(selected) == maximum:
            break
    return selected


def _point_prompts(
    geometry: BaseGeometry,
    crop_transform: Affine,
    refinement_geometry: BaseGeometry | None = None,
) -> tuple[list, list]:
    """Create positive interior and negative concavity/context prompts from a footprint."""
    geometry = make_valid(geometry)
    min_x, min_y, max_x, max_y = geometry.bounds
    xs = np.linspace(min_x, max_x, 9)
    ys = np.linspace(min_y, max_y, 9)
    grid = [Point(float(x), float(y)) for x in xs for y in ys]

    positive_pool = [point for point in grid if geometry.contains(point)]
    positive_scores = [point.distance(geometry.boundary) for point in positive_pool]
    positives = _spaced_points(positive_pool, positive_scores, 5, 4.0)
    if not positives:
        positives = [geometry.representative_point()]

    safe_exterior = geometry.buffer(1.0)
    negative_pool = [point for point in grid if not safe_exterior.contains(point)]
    negative_scores = [-point.distance(geometry) for point in negative_pool]
    negatives = _spaced_points(negative_pool, negative_scores, 8, 3.0)

    if refinement_geometry is not None:
        missing = make_valid(geometry.difference(refinement_geometry.buffer(0.5)))
        missing_parts = sorted(_polygon_parts(missing), key=lambda part: part.area, reverse=True)
        positives = [part.representative_point() for part in missing_parts if part.area >= 5.0][
            :4
        ] + positives

        leakage = make_valid(refinement_geometry.difference(geometry.buffer(1.0)))
        leakage_parts = sorted(_polygon_parts(leakage), key=lambda part: part.area, reverse=True)
        negatives = [part.representative_point() for part in leakage_parts if part.area >= 5.0][
            :4
        ] + negatives

    to_crop = ~crop_transform
    all_points = positives + negatives
    coordinates = [
        [
            [
                [float((to_crop * point.coords[0])[0]), float((to_crop * point.coords[0])[1])]
                for point in all_points
            ]
        ]
    ]
    labels = [[[1] * len(positives) + [0] * len(negatives)]]
    return coordinates, labels


def _infer_candidates(
    model,
    processor,
    image: Image.Image,
    box: list,
    crop_transform: Affine,
    footprint: BaseGeometry,
    device: str,
    prompt_strategy: str,
    refinement_geometry: BaseGeometry | None = None,
) -> list[Candidate]:
    """Run one prompt strategy and score each returned SAM candidate."""
    processor_arguments = {"images": image, "input_boxes": box, "return_tensors": "pt"}
    if prompt_strategy == "box_and_points":
        points, labels = _point_prompts(footprint, crop_transform, refinement_geometry)
        processor_arguments.update(input_points=points, input_labels=labels)
    inputs = processor(**processor_arguments).to(device)
    with torch.inference_mode():
        outputs = model(**inputs, multimask_output=True)
    scores = outputs.iou_scores[0, 0].detach().float().cpu().numpy()
    masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu())[
        0
    ][0]
    candidates = []
    for index, tensor in enumerate(masks):
        mask = tensor.numpy().astype(np.uint8)
        geometry = _mask_geometry(mask, crop_transform, footprint)
        if geometry is None or geometry.area == 0:
            continue
        metrics = _quality_metrics(geometry, footprint, float(scores[index]))
        candidates.append(
            Candidate(mask, geometry, float(scores[index]), *metrics, prompt_strategy)
        )
    return candidates


def _needs_retry(candidate: Candidate) -> bool:
    """Identify candidates that need footprint-derived refinement prompts."""
    return (
        candidate.sam_score < 0.80
        or candidate.precision < 0.85
        or candidate.coverage < 0.85
        or not 0.75 <= candidate.area_ratio <= 1.30
    )


def _write_overlay(
    image: Image.Image, geometry: BaseGeometry, crop_transform: Affine, output_path: Path
) -> None:
    """Render the exact cleaned/exported native-CRS geometry for human review."""
    base = np.asarray(image).copy()
    mask = rasterize(
        [(geometry, 1)],
        out_shape=(image.height, image.width),
        transform=crop_transform,
        dtype=np.uint8,
    )
    tint = base.copy()
    tint[mask.astype(bool)] = (255, 30, 30)
    rendered = cv2.addWeighted(base, 0.68, tint, 0.32, 0)
    to_pixel = ~crop_transform
    for polygon in _polygon_parts(geometry):
        rings = [polygon.exterior, *polygon.interiors]
        for ring in rings:
            pixels = np.asarray(
                [to_pixel * coordinate for coordinate in ring.coords], dtype=np.int32
            )
            cv2.polylines(rendered, [pixels.reshape(-1, 1, 2)], True, (255, 255, 0), 2)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), cv2.cvtColor(rendered, cv2.COLOR_RGB2BGR))


def run_detect(
    config_path: Path, buildings_path: Path, output_path: Path, overlays_dir: Path
) -> None:
    """Run local SAM2 once per configured building and write valid WGS84 geometries."""
    config = tomllib.loads(config_path.read_text())
    study_area = config["study_area"]
    imagery = config["imagery"]
    raster_path = Path(imagery.get("prepared_path", f"data/interim/{study_area['id']}.tif"))
    if not raster_path.exists():
        raise FileNotFoundError(f"Prepared GeoTIFF not found: {raster_path}. Run 'prepare' first.")

    buildings = gpd.read_file(buildings_path)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    processor = Sam2Processor.from_pretrained("facebook/sam2.1-hiera-large")
    model = Sam2Model.from_pretrained("facebook/sam2.1-hiera-large").to(device).eval()
    records = []

    with rasterio.open(raster_path) as source:
        if source.crs is None:
            raise ValueError(f"Prepared raster has no CRS: {raster_path}")
        if buildings.crs is None:
            raise ValueError(f"Building input has no CRS: {buildings_path}")
        buildings = buildings.to_crs(source.crs)
        to_wgs84 = Transformer.from_crs(source.crs, "EPSG:4326", always_xy=True).transform

        for _, building in buildings.iterrows():
            footprint = make_valid(building.geometry)
            image, box, crop_transform = _crop_for_building(source, footprint, 8.0)
            candidates = _infer_candidates(
                model, processor, image, box, crop_transform, footprint, device, "box"
            )
            if not candidates:
                raise RuntimeError(f"SAM returned no polygon for {building['building_id']}")
            best = max(candidates, key=lambda candidate: candidate.selection_score)
            retried = _needs_retry(best)
            if retried:
                candidates.extend(
                    _infer_candidates(
                        model,
                        processor,
                        image,
                        box,
                        crop_transform,
                        footprint,
                        device,
                        "box_and_points",
                        best.geometry,
                    )
                )
                best = max(candidates, key=lambda candidate: candidate.selection_score)

            review_required = _needs_retry(best)
            wgs84_geometry = transform(to_wgs84, best.geometry)
            building_id = building["building_id"]
            _write_overlay(
                image, best.geometry, crop_transform, overlays_dir / f"{building_id}.png"
            )
            records.append(
                {
                    "building_id": building_id,
                    "source_used": {
                        "imagery": "City of Vienna Orthofoto 2024 (15 cm, CC BY 4.0)",
                        "building_prompt": "City of Vienna LOD0.4 building-part footprint",
                        "model": "facebook/sam2.1-hiera-large",
                    },
                    "roof": {
                        "geometry": mapping(wgs84_geometry),
                        "area_m2": round(best.geometry.area, 2),
                        "type": "unknown_from_top_down_rgb",
                        "material": "unknown_from_top_down_rgb",
                    },
                    "confidence": {
                        "outline": round(best.selection_score, 3),
                        "area": round(best.selection_score * 0.95, 3),
                        "type": 0.0,
                        "material": 0.0,
                        "sam_predicted_iou": round(best.sam_score, 3),
                        "footprint_precision": round(best.precision, 3),
                        "footprint_coverage": round(best.coverage, 3),
                        "footprint_iou": round(best.iou, 3),
                    },
                    "quality": {
                        "area_ratio_to_footprint": round(best.area_ratio, 3),
                        "prompt_strategy": best.prompt_strategy,
                        "retry_attempted": retried,
                        "review_required": review_required,
                    },
                    "notes": (
                        "Manual review recommended: prompt/mask quality thresholds were not all met."
                        if review_required
                        else "Automatic quality checks passed."
                    ),
                }
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"schema_version": "1.1", "crs": "EPSG:4326", "buildings": records}, indent=2)
        + "\n"
    )
    print(
        json.dumps(
            {"buildings": len(records), "output": str(output_path), "overlays": str(overlays_dir)},
            indent=2,
        )
    )
