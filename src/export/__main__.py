"""CLI entry point for the export module."""

import argparse
import sys

from .client import ExportClient

FORMATS = ("png", "jpg", "svg", "pptx")


def main() -> int:
    parser = argparse.ArgumentParser(description="FigureLabs.ai export client")
    parser.add_argument("token", help="Access token")
    parser.add_argument("message_id", help="Message ID of a completed generation")
    parser.add_argument(
        "--format", "-f",
        nargs="+",
        default=["png"],
        choices=FORMATS,
        metavar="FMT",
        help=f"Format(s) to download: {', '.join(FORMATS)} (default: png)",
    )
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--filename", "-n", help="Filename stem (no extension)")
    args = parser.parse_args()

    client = ExportClient(args.token)
    results = client.download_all(
        args.message_id,
        fmts=args.format,
        output_dir=args.output,
        filename=args.filename,
    )

    failed = [fmt for fmt, path in results.items() if path is None]
    if failed:
        print(f"Failed: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
