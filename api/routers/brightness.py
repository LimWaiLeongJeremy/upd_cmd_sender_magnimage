"""
All brightness-related API endpoints.

THREE ENDPOINTS:
  POST /brightness/absolute      → send_absolute_brightness (single device)
  POST /brightness/ramp/device   → run_brightness_ramp (single device)
  POST /brightness/ramp/groups   → run_brightness_ramp_on_groups (all groups)

DESIGN PATTERN — what a route function should do:
  1. Receive validated request (Pydantic already validated it)
  2. Call the service layer
  3. Catch known exceptions and return appropriate HTTP errors
  4. Return a success response

  Routes are NOT allowed to contain business logic.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    AbsoluteBrightnessRequest,
    DeviceRampRequest,
    GroupRampRequest,
    SuccessResponse,
)
from service.brightness_service import (
    send_absolute_brightness,
    run_brightness_ramp,
    run_brightness_ramp_on_groups,
)

logger = logging.getLogger(__name__)

# prefix="/brightness" means every route here is under /brightness/...
router = APIRouter(prefix="/brightness", tags=["Brightness Control"])

# ---------------------------------------------------------------------------
# POST /brightness/absolute
# ---------------------------------------------------------------------------

@router.post(
    "/absolute",
    response_model=SuccessResponse,
    summary="Set absolute brightness on a single device",
    description=(
        "Immediately sets the brightness of one LED controller to the specified "
        "percentage. No ramping — the change is instantaneous."
    ),  
)
def set_absolute_brightness(request: AbsoluteBrightnessRequest) -> SuccessResponse:
    """
    Send a single absolute brightness command to one controller.

    - **ip**: Target device IP address
    - **brightness**: Target brightness percentage (0-100)
    
    Returns:
        SuccessResponse with a message confirming the change.   
    Raises:
        HTTPException 400 if the brightness value is out of range.
        HTTPException 500 if the UDP send fails.
    """
    logger.info(f"[API] absolute brightness → ip={request.ip} brightness={request.brightness}%")

    try:
        send_absolute_brightness(request.ip, request.brightness)
    except ValueError as ve:
        # This shouldn't happen — Pydantic validates range before we get here.
        # Belt-and-suspenders: if it somehow does, return 422.
        logger.error(f"Value error: {ve}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except OSError as oe:
        # Network failure — device unreachable
        logger.error(f"API Network error for {request.ip}: {oe}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach device {request.ip}: {oe}",
        )
    except Exception as exc:
        # Catch-all for unexpected errors
        logger.critical(f"[API] Unexpected error: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    
    return SuccessResponse(message=f"Brightness set to {request.brightness}% on {request.ip}")  

# ---------------------------------------------------------------------------
# POST /brightness/ramp/device
# ---------------------------------------------------------------------------

@router.post(
    "/ramp/device", 
    response_model=SuccessResponse,
    summary="Run a brightness ramp on a single device", 
    description=(
        "Gradually transitions the brightness of one LED controller from a start "
        "value to an end value. The request blocks until the ramp is complete."
    ),
)
def ramp_device_brightness(request: DeviceRampRequest) -> SuccessResponse:
    """
    Ramp brightness on a single controller.

    - **ip**: Target device IP address
    - **start_brightness**: Starting brightness percentage (0-100)
    - **end_brightness**: Ending brightness percentage (0-100)
    - **step**: Incremental step for each command (positive integer)
    - **interval_seconds**: Time to wait between commands (seconds)

    Returns:
        SuccessResponse with a message confirming the ramp completion.   
    Raises:
        HTTPException 400 if any brightness value is out of range or if step is invalid.
        HTTPException 500 if the UDP send fails during the ramp.
    """
    logger.info(
        f"[API] ramp device brightness → ip={request.ip} "
        f"start={request.start_brightness}% end={request.end_brightness}% "
        f"step={request.step} interval={request.interval_seconds}s"
    )

    try:
        run_brightness_ramp(
            ip=request.ip,
            start_percentage=request.start_brightness,
            end_percentage=request.end_brightness,
            step=request.step,
            interval_seconds=request.interval_seconds,
        )
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except OSError as oe:
        logger.error(f"[API] Network error for {request.ip}: {oe}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach device {request.ip}: {oe}",
        )
    except Exception as exc:
        logger.critical(f"[API] Unexpected error: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return SuccessResponse(
        message=(
            f"Brightness ramp completed on {request.ip}: "
            f"{request.start_brightness}% → {request.end_brightness}%"
        )
    )
    

# ---------------------------------------------------------------------------
# POST /brightness/ramp/groups
# ---------------------------------------------------------------------------

@router.post(
    "/ramp/groups",
    response_model=SuccessResponse,
    summary="Run a brightness ramp on all groups",
    description=(
        "Concurrently ramps brightness across all controllers in the specified groups. "
        "Each controller runs its ramp in parallel. The request blocks until ALL "
        "controllers have completed. If any device fails, a partial failure is reported."
    ),
)
def ramp_groups_brightness(request: GroupRampRequest) -> SuccessResponse:
    """
    Ramp brightness on all controllers in specified groups.

    - **group**: List of group names
    - **start_brightness**: Starting brightness percentage (0-100)
    - **end_brightness**: Ending brightness percentage (0-100)
    - **step**: Incremental step for each command (positive integer)
    - **interval_seconds**: Time to wait between commands (seconds)

    Returns:
        SuccessResponse with a message confirming the ramp completion.
    Raises:
        HTTPException 400 if any brightness value is out of range or if step is invalid.
        HTTPException 500 if the UDP send fails during the ramp.
    """
    logger.info(
        f"[API] ramp groups brightness → groups={request.groups} "
        f"start={request.start_brightness}% end={request.end_brightness}% "
        f"step={request.step} interval={request.interval_seconds}s"
    )

    try:
        run_brightness_ramp_on_groups(
            groups=request.groups,
            start_percentage=request.start_brightness,
            end_percentage=request.end_brightness,
            step=request.step,
            interval_seconds=request.interval_seconds,
        )
    except ValueError as ve:
        logger.error(f"[API] Value error: {ve}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"[API] Partial group/s ramp failure: {re}")
        raise HTTPException(
            status_code=status.HTTP_207_MULTI_STATUS,
            detail=f"One or more devices failed during the ramp: {re}",
        )
    except OSError as oe:
        logger.error(f"[API] Network error: {oe}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach one or more devices: {oe}",
        )
    except Exception as exc:
        logger.critical(f"[API] Unexpected error: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return SuccessResponse(
        message=(
            f"Brightness ramp completed on groups {request.groups}: "
            f"{request.start_brightness}% → {request.end_brightness}%"
        )
    )

