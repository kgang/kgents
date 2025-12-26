"""
Ghost function schemas - Placeholders for implied code.

Ghosts are created when:
- Spec mentions unimplemented function
- Call graph references undefined function
- User marks TODO
- Analysis suggests missing abstraction

Philosophy:
- Ghosts make absence visible
- Every ghost is a hypothesis
- Ghosts guide implementation priority
- Ghosts can be resolved (implemented) or dismissed (not needed)

The ghost crystal is the unit of missing code tracking. When we ask "what's
missing?", we consult ghost crystals. When we ask "what should be implemented
next?", we rank ghosts by importance. When we ask "is this ghost still valid?",
we check if it's been resolved or if the source changed.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .proof import GaloisWitnessedProof


@dataclass(frozen=True)
class GhostFunctionCrystal:
    """
    Ghost function crystal for tracking implied/missing code (v1).

    A ghost function represents code that doesn't exist yet but should.
    It captures:
    - Identity: id, suggested_name, suggested_location
    - Reason: ghost_reason (why we think this should exist)
    - Source: source_id (what implied this ghost)
    - Expectation: expected_signature, expected_behavior
    - Derivation: spec_id (if spec-implied)
    - Resolution: resolved, resolved_to, resolved_at

    Ghost Reasons:
        SPEC_IMPLIES: Spec describes a function that doesn't exist
            Example: spec/protocols/witness.md says "create_mark() creates a mark"
                     but services/witness/store.py has no create_mark()

        CALL_REFERENCES: Code calls a function that doesn't exist
            Example: app.py calls "validate_config()" but no such function exists

        TODO: User marked a TODO/FIXME/HACK comment
            Example: "# TODO: extract this logic into compute_coherence()"

        SUGGESTED: Analysis suggests a missing abstraction
            Example: Three functions have duplicate validation logic
                     → suggest extract_common_validation()

    Resolution:
        resolved: False until the ghost is implemented or dismissed
        resolved_to: Function crystal ID if implemented, None if dismissed
        resolved_at: When the ghost was resolved

    The ghost crystal answers:
    - "What code is missing?" → suggested_name, expected_behavior
    - "Why do we think it's missing?" → ghost_reason, source_id
    - "Where should it go?" → suggested_location
    - "Has it been implemented?" → resolved, resolved_to
    """

    id: str
    """Unique identifier for this ghost."""

    suggested_name: str
    """Suggested function name (e.g., 'create_mark', 'validate_config')."""

    suggested_location: str
    """Suggested file/module path (e.g., 'services/witness/store.py')."""

    ghost_reason: str
    """Why this ghost exists: 'SPEC_IMPLIES', 'CALL_REFERENCES', 'TODO', 'SUGGESTED'."""

    source_id: str
    """ID of the source that implied this ghost (spec ID, function ID, etc.)."""

    expected_signature: str | None = None
    """Expected function signature if known (e.g., 'def create_mark(action: str) -> Mark')."""

    expected_behavior: str = ""
    """Description of what this function should do."""

    spec_id: str | None = None
    """Reference to spec section if spec-implied."""

    resolved: bool = False
    """True if this ghost has been implemented or dismissed."""

    resolved_to: str | None = None
    """Function crystal ID if implemented, None if dismissed or pending."""

    resolved_at: datetime | None = None
    """When this ghost was resolved."""

    proof: GaloisWitnessedProof | None = None
    """Proof for why this ghost should exist (None until implemented)."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this ghost was first detected."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "suggested_name": self.suggested_name,
            "suggested_location": self.suggested_location,
            "ghost_reason": self.ghost_reason,
            "source_id": self.source_id,
            "expected_signature": self.expected_signature,
            "expected_behavior": self.expected_behavior,
            "spec_id": self.spec_id,
            "resolved": self.resolved,
            "resolved_to": self.resolved_to,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "proof": self.proof.to_dict() if self.proof else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GhostFunctionCrystal":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            suggested_name=data["suggested_name"],
            suggested_location=data["suggested_location"],
            ghost_reason=data["ghost_reason"],
            source_id=data["source_id"],
            expected_signature=data.get("expected_signature"),
            expected_behavior=data.get("expected_behavior", ""),
            spec_id=data.get("spec_id"),
            resolved=data.get("resolved", False),
            resolved_to=data.get("resolved_to"),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
            proof=GaloisWitnessedProof.from_dict(data["proof"]) if data.get("proof") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
        )

    @property
    def is_pending(self) -> bool:
        """Check if this ghost is still pending (not resolved)."""
        return not self.resolved

    @property
    def was_implemented(self) -> bool:
        """Check if this ghost was resolved by implementation (not dismissed)."""
        return self.resolved and self.resolved_to is not None

    @property
    def was_dismissed(self) -> bool:
        """Check if this ghost was resolved by dismissal (not needed)."""
        return self.resolved and self.resolved_to is None


# Schema for Universe registration
from agents.d.universe import DataclassSchema

GHOST_FUNCTION_SCHEMA = DataclassSchema(
    name="code.ghost",
    type_cls=GhostFunctionCrystal
)


__all__ = [
    "GhostFunctionCrystal",
    "GHOST_FUNCTION_SCHEMA",
]
