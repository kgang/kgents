"""
Brain schemas - Versioned data contracts for Brain Crown Jewel.

These schemas define the shape of Brain data stored in D-gent's Crystal system.
They are frozen dataclasses - immutable, typed contracts.

AGENTESE: self.data.table.crystal.*

Spec: spec/protocols/unified-data-crystal.md
"""

from dataclasses import dataclass
from agents.d.crystal.schema import Schema

__all__ = [
    "BrainCrystal",
    "BrainSetting",
    "BRAIN_CRYSTAL_SCHEMA",
    "BRAIN_SETTING_SCHEMA",
]


# =============================================================================
# Brain Crystal Schema (brain.crystal v1)
# =============================================================================


@dataclass(frozen=True)
class BrainCrystal:
    """
    A crystallized piece of knowledge in the Brain.

    Crystals are the atomic units of memory - facts, insights, learnings
    that have been distilled and stored. Each crystal has:
    - Summary: Human-readable description
    - Content: Full crystallized content
    - Content hash: For deduplication
    - Tags: Categorization metadata
    - Source tracking: Where did this come from?
    - Usage tracking: Access patterns for relevance scoring
    - D-gent link: Datum ID for semantic content

    This schema is the immutable contract for brain.crystal data.
    The SQLAlchemy model (models/brain.py::Crystal) provides queryable
    metadata and indexes.

    Attributes:
        summary: Human-readable summary of this crystal
        content: Full crystallized content (can be large)
        content_hash: SHA-256 hash for deduplication
        tags: Categorization tags (immutable tuple)
        source_type: Type of source ("conversation", "mark", "file", etc.)
        source_ref: Reference to original source
        access_count: Number of times accessed
        last_accessed: ISO 8601 timestamp of last access
        datum_id: Link to D-gent datum for semantic content
    """

    summary: str
    content: str
    content_hash: str
    tags: tuple[str, ...] = ()
    source_type: str | None = None
    source_ref: str | None = None
    access_count: int = 0
    last_accessed: str | None = None  # ISO 8601 timestamp
    datum_id: str | None = None  # Link to D-gent datum


BRAIN_CRYSTAL_SCHEMA = Schema(
    name="brain.crystal",
    version=1,
    contract=BrainCrystal,
)
"""
Schema for brain.crystal v1.

The foundational crystal schema for Brain. No migrations yet - this is v1.

Future evolution examples:
- v2: Add embedding_version field
- v3: Add relevance_score computed field
- v4: Add crystal_type enum ("fact", "insight", "procedure")

Migrations would look like:
    BRAIN_CRYSTAL_SCHEMA = Schema(
        name="brain.crystal",
        version=2,
        contract=BrainCrystalV2,
        migrations={
            1: lambda d: {**d, "embedding_version": "default"},
        },
    )
"""


# =============================================================================
# Brain Setting Schema (brain.setting v1)
# =============================================================================


@dataclass(frozen=True)
class BrainSetting:
    """
    User settings for Brain behavior.

    Stores preferences and configuration as key-value pairs.
    Settings can be categorized for organization.

    This is a simple schema for configuration data.
    More complex settings would use nested structures or separate schemas.

    Attributes:
        key: Setting key (e.g., "default_tags", "max_crystals")
        value: Setting value (stored as string, parse on read)
        category: Grouping category (e.g., "general", "retention", "display")
    """

    key: str
    value: str
    category: str = "general"


BRAIN_SETTING_SCHEMA = Schema(
    name="brain.setting",
    version=1,
    contract=BrainSetting,
)
"""
Schema for brain.setting v1.

Simple key-value configuration storage.

Future evolution examples:
- v2: Add value_type enum ("string", "int", "bool", "json")
- v3: Add validation_schema for structured values
- v4: Add user_id for multi-user settings

Migrations would look like:
    BRAIN_SETTING_SCHEMA = Schema(
        name="brain.setting",
        version=2,
        contract=BrainSettingV2,
        migrations={
            1: lambda d: {**d, "value_type": "string"},
        },
    )
"""
