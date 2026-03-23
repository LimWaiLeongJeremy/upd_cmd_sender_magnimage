"""
CLI entry point. This file has ONE job: parse arguments and call the service.

Usage:
    python main.py <start> <end> <step> <duration> [--groups m ac b e ctrl]

Examples:
    python main.py 0 100 5 0.5
    python main.py 100 0 10 1.0 --groups m ac
    python main.py 75 75 1 0 --groups ctrl     # absolute brightness on ctrl only
"""

import argparse

from constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN, DEFAULT_GROUPS


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Send UDP brightness commands to Magnimage FW16-C LED controllers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "start_brightness",
        type=int,
        help=f"Start brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    parser.add_argument(
        "end_brightness",
        type=int,
        help=f"End brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    parser.add_argument(
        "step",
        type=int,
        help="Brightness step size per increment (must be > 0)",
    )
    parser.add_argument(
        "duration",
        type=float,
        help="Delay in seconds between each brightness step (must be > 0)",
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        default=DEFAULT_GROUPS,
        help="List of controller groups to target (default: all groups)",
    )
    return parser