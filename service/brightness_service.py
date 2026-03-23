"""
Business logic for brightness control.

This will help in future FastAPI routes implementation.
Everything above this layer (network, commands, config) is an
implementation detail — the service is the public contract.

Public API of this module:
  - send_absolute_brightness(ip, brightness_percentage)
  - run_brightness_ramp(ip, start, end, step, interval)
  - run_brightness_ramp_on_groups(groups, start, end, step, interval)

Phase 2 usage example (FastAPI):
    from services.brightness_service import send_absolute_brightness
    send_absolute_brightness("10.0.0.101", 75)
"""

from time import time

from tqdm import tqdm

from constants import UDP_DUPLICATE_SEND_DELAY
from utils import logger
from utils.command_utils import build_brightness_command
from utils.network_utils import send_udp_packets


# ---------------------------------------------------------------------------
# Core: single IP, single brightness level
# ---------------------------------------------------------------------------

def send_absolute_brightness(ip: str, brightness_percentage: int) -> None:
    """
    Send a single absolute brightness command to one controller.

    This is the atomic unit of work for Phase 2 API endpoints.
    One call → one brightness level on one device.

    Args:
        ip:                   Target controller IP.
        brightness_percentage: Target brightness (0-100).   
    Raises:
        ValueError: If brightness is out of range.
        OSError:    If the UDP send fails.
    """
    # build_brightness_command validates range and raises ValueError if bad
    command = build_brightness_command(brightness_percentage)
    send_udp_packets(ip, command)
    time.sleep(UDP_DUPLICATE_SEND_DELAY)  # Short delay to ensure command is processed before next one
    send_udp_packets(ip, command)
    logger.info(f"[{ip}] Brightness set → {brightness_percentage}%")
    
    
# ---------------------------------------------------------------------------
# Ramp: single IP, gradual transition
# ---------------------------------------------------------------------------
def run_brightness_ramp(
    ip: str, 
    start_percentage: int, 
    end_percentage: int, 
    step: int, 
    interval_seconds: float
) -> None:
    """
    Run a brightness ramp on a single controller.

    Gradually transition brightness from `start` to `end` in increments or decrements of `step`,
    pausing for `interval` seconds between each command.
    
    Handles both upward (10→80) and downward (80→10) ramps automatically.
    Each step calls send_absolute_brightness, so you get full validation
    and logging at every level.

    Args:
        ip:       Target controller IP.
        start_percentage:    Starting brightness percentage (0-100).
        end_percentage:      Ending brightness percentage (0-100).
        step:     Incremental step for each command (positive integer).
        interval_seconds: Time to wait between commands (seconds).
    Raises:
        ValueError: If brightness values are out of range.
    """
    if step <= 0:
        raise ValueError(f"Step must be a positive integer, got {step}")

    going_up = start_percentage <= end_percentage
    brightness_range = (
        range(start_percentage, end_percentage + 1, step)
        if going_up
        else range(start_percentage, end_percentage - 1, -step)
    )

    logger.info(
        f"[{ip}] Starting ramp: {start_percentage}% → {end_percentage}% "
        f"(step={step}, interval={interval_seconds}s)"
    )

    for brightness in tqdm(brightness_range, desc="Adjusting brightness"):
        send_absolute_brightness(ip, brightness)
        time.sleep(interval_seconds)

    logger.info(f"[{ip}] Ramp complete: {start_percentage}% → {end_percentage}%")