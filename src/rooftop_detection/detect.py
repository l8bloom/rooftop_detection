"""Prompt SAM2 with official building footprints and export roof polygons."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import rasterio
import tomllib
import torch
from affine import Affine
from PIL import Image
from pyproj import Transformer
from rasterio.features import shapes
from rasterio.windows import Window
from shapely import make_valid
from shapely.geometry import shape
from shapely.ops import transform
from transformers import Sam2Model, Sam2Processor

from rooftop_detection.georeference import read_world_file, world_file_to_affine


def _largest_polygon(geometry):
    """Return a valid, lightly simplified largest polygon, or ``None``."""
    geometry = make_valid(geometry)
    polygons = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    polygons = [
        polygon for polygon in polygons if polygon.geom_type == "Polygon" and polygon.area >= 3
    ]
    if not polygons:
        return None
    return max(polygons, key=lambda polygon: polygon.area).simplify(0.3, preserve_topology=True)


def _mask_polygon(mask: np.ndarray, crop_transform: Affine):
    """Vectorise the largest connected SAM mask component in map coordinates."""
    polygons = [
        shape(geometry)
        for geometry, value in shapes(mask, mask=mask.astype(bool), transform=crop_transform)
        if value
    ]
    if not polygons:
        return None
    from shapely.ops import unary_union

    return _largest_polygon(unary_union(polygons))


def _crop_for_building(source, geometry, transform: Affine, padding_m: float):
    """Read a padded RGB crop and return it with its pixel-space prompt box."""
    inverse = ~transform
    min_x, min_y, max_x, max_y = geometry.bounds
    left, top = inverse * (min_x - padding_m, max_y + padding_m)
    right, bottom = inverse * (max_x + padding_m, min_y - padding_m)
    left, top = max(0, int(np.floor(left))), max(0, int(np.floor(top)))
    right, bottom = min(source.width, int(np.ceil(right))), min(source.height, int(np.ceil(bottom)))
    pixels = source.read(window=Window(left, top, right - left, bottom - top))
    image = Image.fromarray(pixels.transpose(1, 2, 0), mode="RGB")
    geometry_bounds = geometry.bounds
    box_left, box_top = inverse * (geometry_bounds[0], geometry_bounds[3])
    box_right, box_bottom = inverse * (geometry_bounds[2], geometry_bounds[1])
    box = [
        [
            [
                float(box_left - left),
                float(box_top - top),
                float(box_right - left),
                float(box_bottom - top),
            ]
        ]
    ]
    return image, box, left, top


def _write_overlay(image: Image.Image, mask: np.ndarray, box, output_path: Path) -> None:
    """Write a review image; colours are debug annotations, never model input."""
    base = np.asarray(image).copy()
    tint = base.copy()
    tint[mask.astype(bool)] = (255, 30, 30)
    rendered = cv2.addWeighted(base, 0.68, tint, 0.32, 0)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(rendered, contours, -1, (255, 255, 0), 2)
    x1, y1, x2, y2 = (round(value) for value in box[0][0])
    cv2.rectangle(rendered, (x1, y1), (x2, y2), (0, 255, 255), 2)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), cv2.cvtColor(rendered, cv2.COLOR_RGB2BGR))


def run_detect(
    config_path: Path, buildings_path: Path, output_path: Path, overlays_dir: Path
) -> None:
    """Run local SAM2 once per configured building and write WGS84 JSON results."""
    config = tomllib.loads(config_path.read_text())
    imagery = config["imagery"]
    crs = imagery["source_crs"]
    world_transform = world_file_to_affine(read_world_file(Path(imagery["world_file_path"])))
    buildings = gpd.read_file(buildings_path)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    processor = Sam2Processor.from_pretrained("facebook/sam2.1-hiera-large", local_files_only=True)
    model = (
        Sam2Model.from_pretrained("facebook/sam2.1-hiera-large", local_files_only=True)
        .to(device)
        .eval()
    )
    to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True).transform
    records = []

    with rasterio.open(imagery["image_path"]) as source:
        for _, building in buildings.iterrows():
            image, box, left, top = _crop_for_building(
                source, building.geometry, world_transform, 8.0
            )
            inputs = processor(images=image, input_boxes=box, return_tensors="pt").to(device)
            with torch.inference_mode():
                outputs = model(**inputs, multimask_output=True)
            scores = outputs.iou_scores[0, 0].detach().float().cpu().numpy()
            masks = processor.post_process_masks(
                outputs.pred_masks.cpu(), inputs["original_sizes"].cpu()
            )[0][0]
            crop_transform = world_transform * Affine.translation(left, top)
            candidates = [
                _mask_polygon(mask.numpy().astype(np.uint8), crop_transform) for mask in masks
            ]
            valid = [
                (index, polygon) for index, polygon in enumerate(candidates) if polygon is not None
            ]
            best_index, polygon = max(valid, key=lambda item: float(scores[item[0]]))
            footprint_overlap = (
                polygon.intersection(building.geometry.buffer(1.0)).area / polygon.area
            )
            outline_confidence = float(scores[best_index]) * (
                0.6 + 0.4 * min(1.0, footprint_overlap)
            )
            wgs84_polygon = transform(to_wgs84, polygon)
            building_id = building["building_id"]
            mask = masks[best_index].numpy().astype(np.uint8)
            _write_overlay(image, mask, box, overlays_dir / f"{building_id}.png")
            records.append(
                {
                    "building_id": building_id,
                    "source_used": {
                        "imagery": "City of Vienna Orthofoto 2024 (15 cm, CC BY 4.0)",
                        "building_prompt": "City of Vienna LOD0.4 building-part footprint",
                        "model": "facebook/sam2.1-hiera-large",
                    },
                    "roof": {
                        "geometry": {
                            "type": wgs84_polygon.geom_type,
                            "coordinates": list(wgs84_polygon.exterior.coords),
                        },
                        "area_m2": round(polygon.area, 2),
                        "type": "unknown_from_top_down_rgb",
                        "material": "unknown_from_top_down_rgb",
                    },
                    "confidence": {
                        "outline": round(outline_confidence, 3),
                        "area": round(outline_confidence, 3),
                        "sam_predicted_iou": round(float(scores[best_index]), 3),
                        "footprint_overlap": round(float(footprint_overlap), 3),
                    },
                    "notes": "Footprint is a prompt and quality signal; final outline follows SAM imagery segmentation.",
                }
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"crs": "EPSG:4326", "buildings": records}, indent=2) + "\n")
    print(
        json.dumps(
            {"buildings": len(records), "output": str(output_path), "overlays": str(overlays_dir)},
            indent=2,
        )
    )
