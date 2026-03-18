from typing import Dict, List

# DATA
MAIN: Dict[str, List[str]] = {
    "m":    [],
    "ac":   [],
    "b":    [],
    "e":    [],
    "ctrl": ["127.0.0.1"]
}

BACKUP: Dict[str, List[str]] = {
    "m":  [],
    "ac": [],
    "b":  [],
    "e":  []
}


# All known group names (union of main + backup keys)
VALID_GROUPS: frozenset[str] = frozenset(MAIN.keys()) | frozenset(BACKUP.keys())


# LOGIC
def resolve_ips(groups: List[str]) -> List[str]:
    """
    Resolve a list of group names into a deduplicated flat list of IP addresses.

    Pulls from both MAIN and BACKUP registries.
    Unknown group names are ignored with no error — caller should validate
    group names before calling this if strict validation is needed.

    Args:
        groups: List of group identifiers e.g. ["m", "ac"]

    Returns:
        Flat list of IP address strings.
    """
    seen: set[str] = set()
    result: List[str] = []

    for group in groups:
        for ip in MAIN.get(group, []) + BACKUP.get(group, []):
            if ip not in seen:
                seen.add(ip)
                result.append(ip)

    return result

def validate_groups(groups: List[str]) -> List[str]:
    """
    Return a list of group names that are NOT in the registry.
    Empty list means all groups are valid.

    Args:
        groups: Group names to check.
        
    Returns:
        List of invalid group names.
    """
    return [g for g in groups if g not in VALID_GROUPS]