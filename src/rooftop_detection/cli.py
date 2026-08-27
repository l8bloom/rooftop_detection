"""Main CLI entry point for the rooftop-detection pipeline.

This command group exposes three subcommands:

* ``prepare`` – Create a self‑contained GeoTIFF from imagery and its world file.
* ``detect`` – Run local SAM2 roof segmentation and write geospatial results.
* ``run`` – Prepare the GeoTIFF when needed, then detect every configured roof.

The ``--help`` option prints this description followed by a list of the subcommands and the options they accept. This verbose help is intended to aid users who want a quick reference to all commands and flags.
"""

from __future__ import annotations

from pathlib import Path

import click

from rooftop_detection import __version__


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Detect and describe roofs from georeferenced aerial imagery."""


@cli.command()
@click.option("--config", type=click.Path(path_type=Path), required=True, help="Study-area TOML.")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Destination GeoTIFF (defaults to data/interim/<study-area-id>.tif).",
)
def prepare(config: Path, output: Path | None) -> None:
    """Create a self-contained GeoTIFF from imagery and its world file."""
    from rooftop_detection.prepare import run_prepare

    run_prepare(config, output)


@cli.command()
@click.option("--config", type=click.Path(path_type=Path), required=True, help="Study-area TOML.")
@click.option(
    "--buildings",
    type=click.Path(path_type=Path),
    default=Path("data/input/buildings.geojson"),
    show_default=True,
    help="Input building targets.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=Path("outputs/roof_attributes.json"),
    show_default=True,
    help="Results JSON.",
)
@click.option(
    "--overlays-dir",
    type=click.Path(path_type=Path),
    default=Path("outputs/overlays"),
    show_default=True,
    help="Review PNG directory.",
)
def detect(config: Path, buildings: Path, output: Path, overlays_dir: Path) -> None:
    """Run local SAM2 roof segmentation and write geospatial results."""
    from rooftop_detection.detect import run_detect

    run_detect(config, buildings, output, overlays_dir)


@cli.command()
@click.option("--config", type=click.Path(path_type=Path), required=True, help="Study-area TOML.")
@click.option(
    "--buildings",
    type=click.Path(path_type=Path),
    default=Path("data/input/buildings.geojson"),
    show_default=True,
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=Path("outputs/roof_attributes.json"),
    show_default=True,
)
@click.option(
    "--overlays-dir",
    type=click.Path(path_type=Path),
    default=Path("outputs/overlays"),
    show_default=True,
)
def run(config: Path, buildings: Path, output: Path, overlays_dir: Path) -> None:
    """Prepare the GeoTIFF when needed, then detect every configured roof."""
    import tomllib

    from rooftop_detection.detect import run_detect
    from rooftop_detection.prepare import run_prepare

    configuration = tomllib.loads(config.read_text())
    study_area = configuration["study_area"]
    imagery = configuration["imagery"]
    prepared_path = Path(imagery.get("prepared_path", f"data/interim/{study_area['id']}.tif"))
    if not prepared_path.exists():
        run_prepare(config, prepared_path)
    run_detect(config, buildings, output, overlays_dir)


def main() -> None:
    """Run the Click command group."""
    cli()


if __name__ == "__main__":
    main()
