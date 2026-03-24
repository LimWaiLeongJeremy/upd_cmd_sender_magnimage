"""
Pydantic models that define the shape of every API request and response.

This is an API contract — what callers must send, and what they will receive.

Reason:
  FastAPI uses these models to automatically:
  - Validate incoming JSON (wrong type = 422 error before your code runs)
  - Generate the /docs interactive API page
  - Serialize your response objects to JSON

  You never write manual validation like `if duration <= 0` in a route.
  The schema enforces it declaratively.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from constants import BRIGHTNESS_MAX, BRIGHTNESS_MIN, DEFAULT_GROUPS

# ---------------------------------------------------------------------------
# Shared validators
# ---------------------------------------------------------------------------


def _validate_brightness(value: int) -> int:
    if not (BRIGHTNESS_MIN <= value <= BRIGHTNESS_MAX):
        raise ValueError(
            f"Brightness must be between {BRIGHTNESS_MIN} and {BRIGHTNESS_MAX}, got {value}"
        )
    return value
  
  
# ---------------------------------------------------------------------------
# Request models  
# ---------------------------------------------------------------------------

class AbsoluteBrightnessRequest(BaseModel):
    """
    Request body for setting a single absolute brightness level on one device.

    Example JSON:
        {
            "ip": "127.0.0.1",
            "brightness": 75
        }
    """
    ip: str = Field(
        ...,
        description="Target controller IP address",
        examples=["127.0.0.1"],
    )
    brightness: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f"Target brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    
class DeviceRampRequest(BaseModel):
    """
    Request body for ramping brightness on a single device.

    Example JSON:
        {
            "ip": "127.0.0.1",
            "start_brightness": 0,
            "end_brightness": 100,
            "step": 10,
            "interval_second": 0.5
        }
    """
    ip: str = Field(
        ...,
        description="Target controller IP address",
        examples=["127.0.0.1"],
    )
    start_brightness: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f"Start brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    end_brightness: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f"End brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    step: int = Field(
        ...,
        ge=1,
        description="Brightness step size per increment (must be > 1)",
    )
    interval_seconds: float = Field(
        ...,
        gt=0.0,
        description="Interval between brightness updates (seconds (> 0))",
    )
    
    
    
class GroupRampRequest(BaseModel):
    """
    Request body for ramping brightness across one or more device groups.

    Example JSON:
        {
            "groups": ["m", "ac"],
            "start_brightness": 0,
            "end_brightness": 100,
            "step": 10,
            "interval_second": 0.5
        }
    """
    groups: list[str] = Field(
        default=DEFAULT_GROUPS,
        description="List of controller groups to target (e.g. ['m', 'ac'])",
        examples=[["m", "ac"], ["b"], ["ctrl"]],
    )
    start_brightness: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f"Start brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    end_brightness: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f"End brightness percentage ({BRIGHTNESS_MIN}-{BRIGHTNESS_MAX})",
    )
    step: int = Field(
        ...,
        ge=1,
        description="Brightness step size per increment (must be >= 1)",
    )
    interval_seconds: float = Field(
        ...,
        gt=0.0,
        description="Interval between brightness updates (seconds (> 0))",
    )
    
    
class SuccessResponse(BaseModel):
    """Standard response model for successful operations."""
    success: bool = True
    message: str
    
    
class ErrorResponse(BaseModel):
    """Standard error envelope. Frontend always knows what failure looks like."""
    success: bool = False
    error: str
    detail: Optional[str] = None