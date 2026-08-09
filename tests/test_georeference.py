from pathlib import Path

from rooftop_detection.georeference import read_world_file, world_file_to_affine


def test_world_file_transform_uses_pixel_corners() -> None:
    transform = world_file_to_affine(
        read_world_file(Path("data/raw/orthophoto_2024_35_4/35_4_op_2024.jgw"))
    )

    assert transform * (0, 0) == (2500.0000000000005, 342500.0)
    right, bottom = transform * (16667, 16667)
    assert abs(right - 5000.0) < 1e-9
    assert abs(bottom - 340000.0) < 1e-9
