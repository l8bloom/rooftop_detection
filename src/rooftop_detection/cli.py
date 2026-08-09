"""Command-line entry point for the rooftop-detection pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from rooftop_detection import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without importing heavyweight geospatial or ML dependencies."""
    parser = argparse.ArgumentParser(
        prog="rooftop-detection",
        description="Detect and describe roofs from georeferenced aerial imagery.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("acquire", help="Download or register a configured imagery source.")
    prepare = commands.add_parser(
        "prepare", help="Create a self-contained GeoTIFF from source imagery and georeferencing."
    )
    prepare.add_argument("--config", required=True, type=Path, help="Study-area TOML configuration.")
    prepare.add_argument(
        "--output",
        type=Path,
        help="Destination GeoTIFF (defaults to data/interim/<study-area-id>.tif).",
    )
    commands.add_parser("detect", help="Run roof segmentation and write geospatial results.")
    commands.add_parser("run", help="Run the configured end-to-end pipeline.")
    return parser


def main() -> None:
    """Run the CLI.

    Heavy geospatial and ML dependencies are imported only by the command that
    needs them, so basic CLI help remains fast and dependency-light.
    """
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "prepare":
        from rooftop_detection.prepare import run_prepare

        run_prepare(args.config, args.output)
        return
    parser.error(f"The '{args.command}' command has not been implemented yet.")


if __name__ == "__main__":
    main()
