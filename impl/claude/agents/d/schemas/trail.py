"""
Trail schemas for the Crystal system.

Frozen dataclass contracts for Trail, TrailStep, TrailCommitment, and TrailAnnotation.
These schemas define versioned data contracts independent of database models.

Based on models/trail.py but as pure data schemas for the Crystal system.

AGENTESE: self.trail.*
"""

from dataclasses import dataclass, field
from typing import Any

from ..crystal.schema import Schema


@dataclass(frozen=True)
class Trail:
    """
    First-class knowledge artifact.

    Not ephemeral—persisted.
    Not solo—supports concurrent co-exploration.
    Not linear—supports fork/merge semantics.

    Schema: trail.trail v1
    """

    name: str
    description: str
    created_by_id: str
    is_active: bool = True
    forked_from_id: str | None = None
    parent_step_index: int | None = None


TRAIL_SCHEMA = Schema(
    name="trail.trail",
    version=1,
    contract=Trail,
)


@dataclass(frozen=True)
class TrailStep:
    """
    Single navigation action in a trail.

    Immutable once recorded. Forms the audit trail.
    Each step records: what action, what content, why.

    Schema: trail.step v1
    """

    trail_id: str
    index: int  # Position in trail
    action: str
    content: str
    reasoning: str | None = None
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    tool_output: str | None = None


TRAIL_STEP_SCHEMA = Schema(
    name="trail.step",
    version=1,
    contract=TrailStep,
)


@dataclass(frozen=True)
class TrailCommitment:
    """
    A claim committed based on trail evidence.

    Commitment levels define strength of belief:
    - speculative: Early hypothesis, minimal evidence
    - moderate: Reasonable evidence, medium confidence
    - strong: Substantial evidence, high confidence
    - definitive: Overwhelming evidence, certainty

    Schema: trail.commitment v1
    """

    trail_id: str
    step_index: int
    level: str  # "speculative", "moderate", "strong", "definitive"
    justification: str


TRAIL_COMMITMENT_SCHEMA = Schema(
    name="trail.commitment",
    version=1,
    contract=TrailCommitment,
)


@dataclass(frozen=True)
class TrailAnnotation:
    """
    Comment or annotation on a trail step.

    Annotations are mutable—they can be added, edited, deleted.
    Steps are immutable; annotations provide the flexibility.

    Schema: trail.annotation v1
    """

    trail_id: str
    step_index: int
    content: str
    author_id: str | None = None


TRAIL_ANNOTATION_SCHEMA = Schema(
    name="trail.annotation",
    version=1,
    contract=TrailAnnotation,
)


__all__ = [
    "Trail",
    "TRAIL_SCHEMA",
    "TrailStep",
    "TRAIL_STEP_SCHEMA",
    "TrailCommitment",
    "TRAIL_COMMITMENT_SCHEMA",
    "TrailAnnotation",
    "TRAIL_ANNOTATION_SCHEMA",
]
