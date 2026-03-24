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

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List

from tqdm import tqdm

from config.ip_groups import resolve_ips, validate_groups
from constants import LOG_FILE, LOG_NAME, UDP_DUPLICATE_SEND_DELAY
from utils import logger
from utils.command_utils import build_brightness_command
from utils.network_utils import send_udp_packets

logger = logger.setup_logger(LOG_NAME, LOG_FILE)

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
    
    
    # ---------------------------------------------------------------------------
# Group ramp: multiple IPs, concurrent execution
# ---------------------------------------------------------------------------

def run_brightness_ramp_on_groups(
    groups: List[str],
    start_percentage: int,
    end_percentage: int,
    step: int,
    interval_seconds: float,
) -> None:
    """
    Run a brightness ramp concurrently across all controllers in specified groups.

    Resolves group names to IPs, then fans out using a thread pool.
    Each controller runs its ramp independently — one failure does NOT
    abort the others. Errors are logged per-IP and re-raised at the end
    as a summary so the caller knows something went wrong.

    Args:
        groups:           List of group names to target.
        start_percentage: Starting brightness (0-100).
        end_percentage:   Target brightness (0-100).
        step:             Increment size per step.
        interval_seconds: Delay between steps in seconds.

    Raises:
        ValueError: If any group name is invalid.
        RuntimeError: If one or more IPs failed to complete the ramp.
    """
    invalid = validate_groups(groups)
    if invalid:
        raise ValueError(f"Unknown group(s): {invalid}. Valid groups: m, ac, b, e, ctrl")

    target_ips = resolve_ips(groups)
    if not target_ips:
        logger.warning(f"No IPs resolved for groups {groups} — nothing to send.")
        return

    logger.info(
        f"Targeting {len(target_ips)} controller(s) across groups {groups}"
    )

    failures: list[str] = []

    with ThreadPoolExecutor() as executor:
        future_to_ip = {
            executor.submit(
                run_brightness_ramp,
                ip, start_percentage, end_percentage, step, interval_seconds,
            ): ip
            for ip in target_ips
        }

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                future.result()
            except Exception as exc:
                logger.error(f"[{ip}] Ramp failed: {exc}")
                failures.append(ip)

    if failures:
        raise RuntimeError(
            f"Brightness ramp failed for {len(failures)} controller(s): {failures}"
        )

    logger.info("All controllers completed brightness ramp successfully.")
