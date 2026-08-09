"""Read world-file georeferencing and create canonical GeoTIFF rasters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorldFileTransform:
    """Affine map transform stored by a six-line ESRI world file."""

    pixel_width: float
    row_rotation: float
    column_rotation: float
    pixel_height: float
    upper_left_x_center: float
    upper_left_y_center: float


def read_world_file(path: Path) -> WorldFileTransform:
    """Parse a JPEG world file without requiring a GIS library."""
    values = [float(line.strip()) for line in path.read_text().splitlines() if line.strip()]
    if len(values) != 6:
        raise ValueError(f"Expected six numeric lines in world file {path}, found {len(values)}.")
    return WorldFileTransform(*values)


def world_file_to_affine(world_file: WorldFileTransform):
    """Return Rasterio's corner-based affine transform from a centre-based world file."""
    from affine import Affine

    # The final two world-file values refer to the centre of pixel (0, 0),
    # whereas Rasterio's affine transform refers to its upper-left corner.
    return Affine(
        world_file.pixel_width,
        world_file.column_rotation,
        world_file.upper_left_x_center
        - (world_file.pixel_width + world_file.column_rotation) / 2,
        world_file.row_rotation,
        world_file.pixel_height,
        world_file.upper_left_y_center
        - (world_file.row_rotation + world_file.pixel_height) / 2,
    )


def write_geotiff(
    image_path: Path,
    world_file_path: Path,
    crs: str,
    output_path: Path,
) -> dict[str, object]:
    """Embed an image, world transform, and CRS into a compressed GeoTIFF.

    The source is copied in 1024-pixel windows to avoid loading the complete
    16k-by-16k orthophoto into memory.
    """
    import rasterio
    from rasterio.windows import Window

    transform = world_file_to_affine(read_world_file(world_file_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(image_path) as source:
        profile = source.profile.copy()
        # JPEG carries a YCbCr photometric setting, which only applies when a
        # GeoTIFF also uses JPEG compression. Let GDAL select RGB for Deflate.
        profile.pop("photometric", None)
        profile.update(
            driver="GTiff",
            crs=crs,
            transform=transform,
            compress="deflate",
            predictor=2,
            tiled=True,
            blockxsize=512,
            blockysize=512,
            BIGTIFF="IF_SAFER",
        )
        with rasterio.open(output_path, "w", **profile) as destination:
            for row_offset in range(0, source.height, 1024):
                for column_offset in range(0, source.width, 1024):
                    window = Window(
                        column_offset,
                        row_offset,
                        min(1024, source.width - column_offset),
                        min(1024, source.height - row_offset),
                    )
                    destination.write(source.read(window=window), window=window)

    with rasterio.open(output_path) as dataset:
        bounds = dataset.bounds
        return {
            "path": str(output_path),
            "crs": str(dataset.crs),
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "pixel_size_m": [dataset.transform.a, abs(dataset.transform.e)],
            "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
        }
