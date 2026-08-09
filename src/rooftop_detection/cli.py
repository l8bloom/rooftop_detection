"""Command-line entry point for the rooftop-detection pipeline."""

from __future__ import annotations

import argparse

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
    commands.add_parser("prepare", help="Create georeferenced model chips from imagery and footprints.")
    commands.add_parser("detect", help="Run roof segmentation and write geospatial results.")
    commands.add_parser("run", help="Run the configured end-to-end pipeline.")
    return parser


def main() -> None:
    """Run the CLI.

    Pipeline commands are registered now and will be wired to their implementation
    modules as each stage is added.
    """
    parser = build_parser()
    args = parser.parse_args()
    parser.error(f"The '{args.command}' command has not been implemented yet.")


if __name__ == "__main__":
    main()
