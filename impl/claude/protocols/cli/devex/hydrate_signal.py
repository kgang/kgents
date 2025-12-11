"""
HYDRATE.md signal appending.

HYDRATE.md is the thought_stream.md in disguise. Instead of building
a complex GhostWriter, we append timestamped signals to HYDRATE.md.

This creates a living document that shows both the snapshot (top)
and the delta (bottom) of system state.

Usage:
    from protocols.cli.devex import append_hydrate_signal, HydrateEvent

    # After a significant event
    append_hydrate_signal(HydrateEvent.SESSION_START, "focus: agents/m/")
    append_hydrate_signal(HydrateEvent.TEST_RUN, "6683 passed, 2 failed")
    append_hydrate_signal(HydrateEvent.PRIOR_DRIFT, "readability_weight: 0.7 -> 0.8")
"""

from datetime import datetime
from enum import Enum
from pathlib import Path


class HydrateEvent(Enum):
    """Types of signals that can be appended to HYDRATE.md."""

    SESSION_START = "session"
    SESSION_END = "session_end"
    TEST_RUN = "tests"
    PRIOR_DRIFT = "prior"
    FLINCH_SUMMARY = "flinch"
    CI_RESULT = "ci"
    CUSTOM = "note"


# Find project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent  # -> kgents
_HYDRATE_FILE = _PROJECT_ROOT / "HYDRATE.md"

# Marker for signal section
_SIGNAL_MARKER = "<!-- META-BOOTSTRAP SIGNALS -->"


def append_hydrate_signal(
    event: HydrateEvent,
    detail: str = "",
    *,
    project_root: Path | None = None,
) -> bool:
    """
    Append a timestamped signal to HYDRATE.md.

    Signals appear in a dedicated section at the bottom of the file,
    separated by the META-BOOTSTRAP SIGNALS marker.

    Args:
        event: The type of event
        detail: Optional detail string
        project_root: Override project root for testing

    Returns:
        True if signal was appended, False on error
    """
    hydrate_path = (project_root / "HYDRATE.md") if project_root else _HYDRATE_FILE

    try:
        if not hydrate_path.exists():
            return False

        content = hydrate_path.read_text()

        # Format the signal
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        detail_str = f": {detail}" if detail else ""
        signal_line = f"- `{timestamp}` [{event.value}]{detail_str}\n"

        # Check if signal section exists
        if _SIGNAL_MARKER not in content:
            # Add signal section
            content = content.rstrip() + f"\n\n---\n\n{_SIGNAL_MARKER}\n{signal_line}"
        else:
            # Append to existing section
            content = content.rstrip() + f"\n{signal_line}"

        hydrate_path.write_text(content)
        return True

    except Exception:
        # Never let signal logging break anything
        return False


def get_recent_signals(
    limit: int = 10,
    *,
    project_root: Path | None = None,
) -> list[str]:
    """
    Get recent signals from HYDRATE.md.

    Args:
        limit: Maximum number of signals to return
        project_root: Override project root for testing

    Returns:
        List of signal lines (most recent first)
    """
    hydrate_path = (project_root / "HYDRATE.md") if project_root else _HYDRATE_FILE

    try:
        if not hydrate_path.exists():
            return []

        content = hydrate_path.read_text()

        if _SIGNAL_MARKER not in content:
            return []

        # Extract signals section
        _, signals_section = content.split(_SIGNAL_MARKER, 1)
        lines = [
            line.strip()
            for line in signals_section.strip().split("\n")
            if line.strip().startswith("- `")
        ]

        return list(reversed(lines[-limit:]))

    except Exception:
        return []
