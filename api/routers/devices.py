import logging
from fastapi import APIRouter

from config.ip_groups import BACKUP, MAIN, VALID_GROUPS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/groups", summary="List all device group names")
def get_groups() -> dict:
    """Return all known group identifiers, sorted."""
    groups = sorted(VALID_GROUPS)
    logger.info(f"[API] GET /devices/groups -> {groups}")
    return {"groups": groups}


@router.get("/ips", summary="List all device IP addresses")
def get_ips() -> dict:
    """
    Return all IPs across main and backup registries, deduplicated.
    Each entry includes the group it belongs to and whether it is main or backup.
    """
    entries = []
    seen = set()

    for group, ips in MAIN.items():
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                entries.append({"ip": ip, "group": group, "role": "main"})

    for group, ips in BACKUP.items():
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                entries.append({"ip": ip, "group": group, "role": "backup"})

    logger.info(f"[API] GET /devices/ips -> {len(entries)} addresses")
    return {"devices": entries}