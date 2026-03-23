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
import logging
import sys

from constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN, DEFAULT_GROUPS, LOG_FILE, LOG_NAME
from service.brightness_service import run_brightness_ramp_on_groups
from utils.logger import setup_logger


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

def validate_args(args: argparse.Namespace, logger: logging.Logger) -> bool:
    """
    Validate parsed CLI arguments.

    Returns True if all arguments are valid, False otherwise.
    All errors are logged — never silently dropped.
    """
    valid = True

    for field, value in [
        ("start_brightness", args.start_brightness),
        ("end_brightness", args.end_brightness),
    ]:
        if not (BRIGHTNESS_MIN <= value <= BRIGHTNESS_MAX):
            logger.error(
                f"'{field}' must be between {BRIGHTNESS_MIN} and {BRIGHTNESS_MAX}, got {value}"
            )
            valid = False

    if args.step <= 0:
        logger.error(f"'step' must be a positive integer, got {args.step}")
        valid = False

    if args.duration < 0:
        logger.error(f"'duration' must be >= 0, got {args.duration}")
        valid = False

    return valid


def main() -> None:
    """Parse arguments, validate, and dispatch to the brightness service."""
    logger = setup_logger(LOG_NAME, LOG_FILE)

    parser = build_parser()
    args = parser.parse_args()

    if not validate_args(args, logger):
        parser.print_usage()
        sys.exit(1)

    logger.info(
        f"Command received: brightness {args.start_brightness}% → {args.end_brightness}% "
        f"| step={args.step} | duration={args.duration}s | groups={args.groups}"
    )

    try:
        run_brightness_ramp_on_groups(
            groups=args.groups,
            start_percentage=args.start_brightness,
            end_percentage=args.end_brightness,
            step=args.step,
            interval_seconds=args.duration,
        )
    except ValueError as exc:
        logger.error(f"Invalid input: {exc}")
        sys.exit(1)
    except RuntimeError as exc:
        logger.error(f"Partial failure: {exc}")
        sys.exit(2)
    except Exception as exc:
        logger.critical(f"Unexpected error: {exc}", exc_info=True)
        sys.exit(3)