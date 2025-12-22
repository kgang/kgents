"""
Trail File Persistence: XDG-compliant trail storage.

Provides file-based trail persistence for quick save/load without database.

Philosophy:
    "The trail IS the decision. The mark IS the witness."

This is the lightweight alternative to TrailStorageAdapter (Postgres).
Use this for:
    - Quick local saves: `kg portal trail save "auth-bug"`
    - Sharing trails: Export to JSON file
    - Replay: Reconstruct portal tree from saved trail

Use TrailStorageAdapter for:
    - Durable production storage
    - Semantic search across trails
    - Fork/merge operations
    - Evidence in ASHC proofs

Path: ~/.kgents/trails/<trail_id>.json

Teaching:
    gotcha: Trail IDs are sanitized—only alphanumeric, dash, underscore allowed.
            "Auth Bug Investigation" → "auth-bug-investigation"
            (Evidence: test_trail_file_persistence.py::test_sanitize_trail_name)

    gotcha: Trails are immutable once saved. To update, save with a new name
            or use TrailStorageAdapter for versioned updates.
            (Evidence: test_trail_file_persistence.py::test_save_overwrites_existing)

Spec Reference: plans/portal-fullstack-integration.md Phase 3
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.exploration.types import Trail as ExplorationTrail
    from protocols.agentese.contexts.self_context import Trail as ContextTrail

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# XDG-compliant trail directory
TRAIL_DIR = Path.home() / ".kgents" / "trails"


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class TrailSaveResult:
    """Result of a trail save operation."""

    trail_id: str
    name: str
    step_count: int
    file_path: Path
    timestamp: datetime
    mark_id: str | None = None  # Witness mark ID if emitted


@dataclass(frozen=True)
class TrailLoadResult:
    """Result of a trail load operation."""

    trail_id: str
    name: str
    steps: list[dict[str, Any]]
    annotations: dict[int, str]
    created_at: datetime
    created_by: str
    evidence_strength: str


@dataclass(frozen=True)
class TrailListEntry:
    """Entry in trail listing."""

    trail_id: str
    name: str
    step_count: int
    saved_at: datetime
    file_path: Path
    evidence_strength: str


# =============================================================================
# Helpers
# =============================================================================


def sanitize_trail_name(name: str) -> str:
    """
    Convert a trail name to a valid file-safe ID.

    Transformations:
    - Lowercase
    - Replace spaces with dashes
    - Remove non-alphanumeric except dash/underscore
    - Truncate to 64 characters

    Examples:
        "Auth Bug Investigation" → "auth-bug-investigation"
        "Quick Test!!" → "quick-test"
        "a/b/c" → "abc"
    """
    # Lowercase
    result = name.lower()

    # Replace spaces with dashes
    result = result.replace(" ", "-")

    # Keep only alphanumeric, dash, underscore
    result = re.sub(r"[^a-z0-9\-_]", "", result)

    # Collapse multiple dashes
    result = re.sub(r"-+", "-", result)

    # Strip leading/trailing dashes
    result = result.strip("-")

    # Truncate
    if len(result) > 64:
        result = result[:64]

    # Fallback if empty
    if not result:
        result = "unnamed-trail"

    return result


def generate_trail_id(name: str | None = None) -> str:
    """
    Generate a unique trail ID.

    If name provided, uses sanitized name + timestamp.
    Otherwise, uses uuid4.
    """
    if name:
        sanitized = sanitize_trail_name(name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{sanitized}_{timestamp}"

    return f"trail_{uuid.uuid4().hex[:12]}"


# =============================================================================
# Core Functions
# =============================================================================


async def save_trail(
    trail: "ExplorationTrail | ContextTrail | dict[str, Any]",
    name: str | None = None,
    emit_mark: bool = True,
) -> TrailSaveResult:
    """
    Save a trail to file.

    Persists trail data to ~/.kgents/trails/<trail_id>.json
    and optionally emits a witness mark.

    Args:
        trail: Trail to save (ExplorationTrail, ContextTrail, or dict from share())
        name: Optional name override for the trail
        emit_mark: If True, emit witness mark (default True)

    Returns:
        TrailSaveResult with file path and optional mark ID

    Example:
        from protocols.trail.file_persistence import save_trail

        result = await save_trail(portal_tree.to_trail(), "auth-investigation")
        print(f"Saved to {result.file_path}")
    """
    # Ensure directory exists
    TRAIL_DIR.mkdir(parents=True, exist_ok=True)

    # Convert trail to shareable dict
    if hasattr(trail, "share"):
        trail_data = trail.share()  # ContextTrail
    elif hasattr(trail, "to_dict"):
        trail_data = trail.to_dict()  # ExplorationTrail
    elif isinstance(trail, dict):
        trail_data = trail  # Already a dict
    elif hasattr(trail, "__dataclass_fields__"):
        # Handle dataclasses (e.g., protocols.exploration.types.Trail)
        from dataclasses import asdict
        trail_data = asdict(trail)
        # Convert datetime objects to ISO format
        for key, value in trail_data.items():
            if hasattr(value, "isoformat"):
                trail_data[key] = value.isoformat()
            elif isinstance(value, tuple):
                # Convert tuples (like steps) to lists for JSON serialization
                trail_data[key] = [
                    {k: (v.isoformat() if hasattr(v, "isoformat") else v)
                     for k, v in (item if isinstance(item, dict) else asdict(item)).items()}
                    for item in value
                ]
    else:
        raise TypeError(f"Unsupported trail type: {type(trail)}")

    # Use provided name or extract from trail
    trail_name = name or trail_data.get("name", "Unnamed Trail")
    trail_id = trail_data.get("id") or generate_trail_id(trail_name)

    # Add persistence metadata
    now = datetime.now()
    trail_data["saved_at"] = now.isoformat()
    trail_data["name"] = trail_name
    trail_data["id"] = trail_id

    # Ensure step_count is present
    step_count = trail_data.get("step_count", len(trail_data.get("steps", [])))
    trail_data["step_count"] = step_count

    # Write to file
    trail_file = TRAIL_DIR / f"{trail_id}.json"
    trail_file.write_text(json.dumps(trail_data, indent=2, default=str))

    logger.debug(f"Trail saved: {trail_id} ({step_count} steps) → {trail_file}")

    # Emit witness mark if requested
    mark_id: str | None = None
    if emit_mark:
        try:
            from services.witness.portal_marks import mark_trail_save
            from protocols.agentese.contexts.self_context import Trail as ContextTrailType

            # Need a ContextTrail object for mark_trail_save
            if isinstance(trail, ContextTrailType):
                mark_id = await mark_trail_save(trail, name=trail_name)
            else:
                # Reconstruct trail from dict for mark emission
                reconstructed = ContextTrailType.from_dict(trail_data)
                mark_id = await mark_trail_save(reconstructed, name=trail_name)

        except ImportError:
            logger.debug("Witness service not available - skipping mark emission")
        except Exception as e:
            # Fire-and-forget: log error, don't fail the save
            logger.warning(f"Failed to emit trail save mark: {e}")

    return TrailSaveResult(
        trail_id=trail_id,
        name=trail_name,
        step_count=step_count,
        file_path=trail_file,
        timestamp=now,
        mark_id=mark_id,
    )


async def load_trail(trail_id: str) -> TrailLoadResult | None:
    """
    Load a trail from file.

    Args:
        trail_id: Trail ID to load

    Returns:
        TrailLoadResult or None if not found
    """
    trail_file = TRAIL_DIR / f"{trail_id}.json"

    if not trail_file.exists():
        # Try without extension (in case user passed full filename)
        trail_file = TRAIL_DIR / trail_id
        if not trail_file.exists():
            return None

    try:
        trail_data = json.loads(trail_file.read_text())
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse trail file {trail_file}: {e}")
        return None

    # Parse datetime
    created_at_str = trail_data.get("created_at") or trail_data.get("saved_at")
    if created_at_str:
        try:
            created_at = datetime.fromisoformat(created_at_str)
        except (ValueError, TypeError):
            created_at = datetime.now()
    else:
        created_at = datetime.now()

    # Parse annotations
    annotations_raw = trail_data.get("annotations", {})
    annotations = {int(k): v for k, v in annotations_raw.items()}

    return TrailLoadResult(
        trail_id=trail_data.get("id", trail_id),
        name=trail_data.get("name", "Unnamed"),
        steps=trail_data.get("steps", []),
        annotations=annotations,
        created_at=created_at,
        created_by=trail_data.get("created_by", "unknown"),
        evidence_strength=trail_data.get("evidence", {}).get("strength", "weak"),
    )


def list_trails(limit: int = 50) -> list[TrailListEntry]:
    """
    List all saved trails.

    Args:
        limit: Maximum trails to return (default 50)

    Returns:
        List of TrailListEntry, newest first
    """
    if not TRAIL_DIR.exists():
        return []

    entries: list[TrailListEntry] = []

    for trail_file in TRAIL_DIR.glob("*.json"):
        try:
            data = json.loads(trail_file.read_text())

            # Parse saved_at
            saved_at_str = data.get("saved_at")
            if saved_at_str:
                try:
                    saved_at = datetime.fromisoformat(saved_at_str)
                except (ValueError, TypeError):
                    saved_at = datetime.fromtimestamp(trail_file.stat().st_mtime)
            else:
                saved_at = datetime.fromtimestamp(trail_file.stat().st_mtime)

            entries.append(
                TrailListEntry(
                    trail_id=trail_file.stem,
                    name=data.get("name", "Unnamed"),
                    step_count=data.get("step_count", len(data.get("steps", []))),
                    saved_at=saved_at,
                    file_path=trail_file,
                    evidence_strength=data.get("evidence", {}).get("strength", "weak"),
                )
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to read trail {trail_file}: {e}")
            continue

    # Sort by saved_at descending (newest first)
    entries.sort(key=lambda e: e.saved_at, reverse=True)

    return entries[:limit]


async def delete_trail(trail_id: str) -> bool:
    """
    Delete a saved trail.

    Args:
        trail_id: Trail ID to delete

    Returns:
        True if deleted, False if not found
    """
    trail_file = TRAIL_DIR / f"{trail_id}.json"

    if trail_file.exists():
        trail_file.unlink()
        logger.debug(f"Trail deleted: {trail_id}")
        return True

    return False


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TRAIL_DIR",
    "TrailSaveResult",
    "TrailLoadResult",
    "TrailListEntry",
    "sanitize_trail_name",
    "generate_trail_id",
    "save_trail",
    "load_trail",
    "list_trails",
    "delete_trail",
]
