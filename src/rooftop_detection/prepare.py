"""Canonicalise configured source imagery into a GeoTIFF."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from rooftop_detection.georeference import write_geotiff


def run_prepare(config_path: Path, output_path: Path | None) -> None:
    """Build and describe a GeoTIFF from one study configuration."""
    config = tomllib.loads(config_path.read_text())
    study_area = config["study_area"]
    imagery = config["imagery"]

    destination = output_path or Path("data/interim") / f"{study_area['id']}.tif"
    result = write_geotiff(
        image_path=Path(imagery["image_path"]),
        world_file_path=Path(imagery["world_file_path"]),
        crs=imagery["source_crs"],
        output_path=destination,
    )
    print(json.dumps(result, indent=2))
