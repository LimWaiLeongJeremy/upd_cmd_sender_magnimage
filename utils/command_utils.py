"""
All logic related to building the UDP command frame for the
Magnimage FW16-C LED Video Controller.

Frame structure (39 bytes total):
  [0]    0xED  — Header byte 1
  [1]    0xCB  — Header byte 2
  [2]    0x28  — Header byte 3
  [3]    0x38  — Header byte 4
  [4]    0x07  — Header byte 5
  [5]    0x01  — Header byte 6
  [6]    BVAL  — Brightness value (0x00–0xFF)
  [7]    0x00  — Padding
  [8-37] 0x55  — 30 footer bytes
  [38]   CSUM  — Checksum (sum of bytes 0–37, lower 8 bits)
"""

from constants import (
    BRIGHTNESS_MIN,     
    BRIGHTNESS_MAX,
    BRIGHTNESS_BYTE_MAX,
    COMMAND_HEADER,
    COMMAND_FOOTER_BYTE,
    COMMAND_FOOTER_COUNT,
    COMMAND_PADDING_BYTE,
)

def brightness_percent_to_byte(percentage: int) -> int:
    """
    Convert a brightness percentage (0-100) to a controller byte value (0-255).

    Uses integer arithmetic — no floating point rounding surprises.
    Result is clamped to [0, 255] as a safety net even if input is validated upstream.

    Args:
        percentage: Brightness level as a percentage.
    
    Returns:
        Corresponding byte value for the command frame.
    """
    raw = (percentage * BRIGHTNESS_BYTE_MAX) // BRIGHTNESS_MAX
    return max(0, min(BRIGHTNESS_BYTE_MAX, raw))

def calculate_checksum(frame: list[int]) -> int:
    """
    Calculate the command frame checksum.

    Algorithm: sum all bytes in the frame, return the lower 8 bits.
    This is a simple additive checksum — used by the FW16-C protocol.

    Args:
        frame: List of integer byte values (0-255 each).
    Returns:
        Single byte checksum (0-255).
    """
    return sum(frame) % 256

def build_brightness_command(brghtness_percentage: int) -> bytes:
    """
    Build the complete 39-byte UDP command for a given brightness percentage.

    Combines header, brightness byte, padding, footer, and checksum into a single bytes object.
    This is the PRIMARY public function of this module.
    All other functions are helpers called by this one.

    Args:
        brightness_percentage: Target brightness percentage (0-100).
    Returns:
        Byte object representing the full command frame to send over UDP.    
    Raises:
        ValueError: If the input percentage is out of valid range.
    """
    
    if not BRIGHTNESS_MIN <= brghtness_percentage <= BRIGHTNESS_MAX:
        raise ValueError(
            f"Brightness percentage must be between {BRIGHTNESS_MIN} and {BRIGHTNESS_MAX}, "
            f"but got {brghtness_percentage}")

    brightness_byte = brightness_percent_to_byte(brghtness_percentage)

    frame: list[int] = (
        COMMAND_HEADER +
        [brightness_byte] +
        [COMMAND_PADDING_BYTE] +
        [COMMAND_FOOTER_BYTE] 
        * COMMAND_FOOTER_COUNT
    )
    checksum = calculate_checksum(frame)
    frame.append(checksum)

    return bytes(frame)