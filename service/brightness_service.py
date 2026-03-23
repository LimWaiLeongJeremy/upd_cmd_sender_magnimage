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

from os import wait

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
        brightness_percentage: Target brightness (0–100).   
    Raises:
        ValueError: If brightness is out of range.
        OSError:    If the UDP send fails.
    """
    # build_brightness_command validates range and raises ValueError if bad
    command = build_brightness_command(brightness_percentage)
    send_udp_packets(ip, command)
    wait(UDP_DUPLICATE_SEND_DELAY)  # Short delay to ensure command is processed before next one
    send_udp_packets(ip, command)
    logger.info(f"[{ip}] Brightness set → {brightness_percentage}%")