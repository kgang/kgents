"""
Timezone utilities for kgents.

Principled Approach:
    1. STORAGE: All datetimes stored as UTC (timezone-aware)
    2. API: All timestamps serialized as ISO 8601 with 'Z' suffix or +00:00
    3. DISPLAY: Frontend converts to local timezone for human display

Laws:
    - Law 1 (UTC Primacy): Internal timestamps are always UTC-aware
    - Law 2 (ISO 8601): Serialization uses standard format
    - Law 3 (Comparison Safety): Never compare naive vs aware datetimes

Usage:
    >>> from services.timezone import utc_now, ensure_utc, to_iso, from_iso
    >>> now = utc_now()  # Always use this, not datetime.now()
    >>> ts = ensure_utc(some_datetime)  # Normalize legacy naive timestamps
    >>> s = to_iso(ts)  # "2025-12-25T22:57:11.612000Z"
    >>> dt = from_iso(s)  # Parse back to datetime

Frontend Integration:
    The API sends ISO 8601 timestamps. React components should:

    ```typescript
    // Display in user's local timezone
    function formatLocalTime(isoString: string): string {
        return new Date(isoString).toLocaleString();
    }

    // Display relative time (e.g., "5 minutes ago")
    function formatRelativeTime(isoString: string): string {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        // ... relative time logic
    }
    ```

See: docs/skills/metaphysical-fullstack.md (Layer 0: Persistence)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Constants
# =============================================================================

UTC = timezone.utc


# =============================================================================
# Core Functions
# =============================================================================


def utc_now() -> datetime:
    """
    Get current time as UTC-aware datetime.

    ALWAYS use this instead of datetime.now() to ensure timezone consistency.

    Returns:
        Current time with tzinfo=UTC

    Example:
        >>> from services.timezone import utc_now
        >>> now = utc_now()
        >>> assert now.tzinfo is not None
        >>> assert now.tzinfo == timezone.utc
    """
    return datetime.now(UTC)


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure a datetime is UTC-aware.

    - If already UTC-aware: return as-is
    - If naive (no tzinfo): assume UTC, add tzinfo
    - If other timezone: convert to UTC

    Args:
        dt: A datetime (naive or aware)

    Returns:
        UTC-aware datetime

    Example:
        >>> from datetime import datetime, timezone
        >>> from services.timezone import ensure_utc
        >>> naive = datetime(2025, 12, 25, 12, 0, 0)
        >>> aware = ensure_utc(naive)
        >>> assert aware.tzinfo == timezone.utc
    """
    if dt.tzinfo is None:
        # Assume naive datetimes are UTC (legacy data pattern)
        return dt.replace(tzinfo=UTC)
    elif dt.tzinfo == UTC:
        return dt
    else:
        # Convert from other timezone to UTC
        return dt.astimezone(UTC)


def to_iso(dt: datetime) -> str:
    """
    Serialize datetime to ISO 8601 format.

    Uses 'Z' suffix for UTC (JavaScript-friendly).

    Args:
        dt: A datetime (will be converted to UTC if needed)

    Returns:
        ISO 8601 string like "2025-12-25T22:57:11.612000Z"

    Example:
        >>> from services.timezone import utc_now, to_iso
        >>> s = to_iso(utc_now())
        >>> assert s.endswith('Z')
    """
    utc_dt = ensure_utc(dt)
    # Use 'Z' suffix instead of '+00:00' for JavaScript compatibility
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def to_iso_full(dt: datetime) -> str:
    """
    Serialize datetime to full-precision ISO 8601 format.

    Includes microseconds. Use to_iso() for most cases.

    Args:
        dt: A datetime (will be converted to UTC if needed)

    Returns:
        ISO 8601 string like "2025-12-25T22:57:11.612345Z"
    """
    utc_dt = ensure_utc(dt)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def from_iso(s: str) -> datetime:
    """
    Parse ISO 8601 string to UTC-aware datetime.

    Handles:
    - 'Z' suffix: "2025-12-25T22:57:11Z"
    - +00:00 suffix: "2025-12-25T22:57:11+00:00"
    - Other timezone offsets (converts to UTC)
    - Naive strings (assumes UTC)

    Args:
        s: ISO 8601 datetime string

    Returns:
        UTC-aware datetime

    Example:
        >>> from services.timezone import from_iso
        >>> dt = from_iso("2025-12-25T22:57:11Z")
        >>> assert dt.tzinfo == timezone.utc
    """
    # Normalize 'Z' to '+00:00' for fromisoformat
    normalized = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        return ensure_utc(dt)
    except ValueError:
        # Fallback: try without timezone, assume UTC
        try:
            dt = datetime.fromisoformat(s.rstrip("Z"))
            return dt.replace(tzinfo=UTC)
        except ValueError:
            raise ValueError(f"Cannot parse datetime: {s}")


# =============================================================================
# Day Boundary Utilities (for "today" filtering)
# =============================================================================


def today_start_utc() -> datetime:
    """
    Get midnight UTC of current day.

    Useful for "today" filters in queries.

    Returns:
        Midnight UTC today (e.g., 2025-12-25T00:00:00Z)

    Example:
        >>> from services.timezone import today_start_utc, utc_now
        >>> start = today_start_utc()
        >>> now = utc_now()
        >>> assert start <= now
        >>> assert start.hour == 0 and start.minute == 0
    """
    now = utc_now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def is_today_utc(dt: datetime) -> bool:
    """
    Check if datetime is within current UTC day.

    Args:
        dt: A datetime (naive or aware)

    Returns:
        True if dt >= midnight UTC today

    Example:
        >>> from services.timezone import utc_now, is_today_utc
        >>> assert is_today_utc(utc_now())
    """
    utc_dt = ensure_utc(dt)
    return utc_dt >= today_start_utc()


# =============================================================================
# Comparison Utilities
# =============================================================================


def safe_compare(dt1: datetime | None, dt2: datetime | None) -> int:
    """
    Safely compare two datetimes, handling None and timezone mismatches.

    Args:
        dt1: First datetime (or None)
        dt2: Second datetime (or None)

    Returns:
        -1 if dt1 < dt2
         0 if dt1 == dt2
         1 if dt1 > dt2
        None values sort last.

    Example:
        >>> from services.timezone import safe_compare, utc_now
        >>> assert safe_compare(None, utc_now()) == 1  # None is "later"
        >>> assert safe_compare(utc_now(), None) == -1
    """
    if dt1 is None and dt2 is None:
        return 0
    if dt1 is None:
        return 1  # None sorts last
    if dt2 is None:
        return -1

    # Ensure both are UTC for safe comparison
    utc1 = ensure_utc(dt1)
    utc2 = ensure_utc(dt2)

    if utc1 < utc2:
        return -1
    elif utc1 > utc2:
        return 1
    return 0


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "UTC",
    "utc_now",
    "ensure_utc",
    "to_iso",
    "to_iso_full",
    "from_iso",
    "today_start_utc",
    "is_today_utc",
    "safe_compare",
]
