import logging
from fastapi import APIRouter

from config.ip_groups import VALID_GROUPS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/groups", summary="List all device group names")
def get_groups() -> dict:
    """Return all known group identifiers, sorted."""
    groups = sorted(VALID_GROUPS)
    logger.info(f"[API] GET /devices/groups -> {groups}")
    return {"groups": groups}