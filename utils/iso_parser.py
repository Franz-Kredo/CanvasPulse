
from datetime import datetime
from typing import Optional


def _parse_iso(dt: Optional[str]) -> Optional[datetime]:
    """Parse Canvas ISO string into aware datetime, or None."""
    if not dt:
        return None
    # Canvas returns '...Z' -> make it RFC3339-friendly for fromisoformat
    dt = dt.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(dt)
    except ValueError:
        return None
