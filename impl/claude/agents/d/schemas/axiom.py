"""
Axiom and Value schemas - L1 and L2 of the Zero Seed holarchy.

Axioms are the atomic, unproven foundational truths.
Values are derived from axioms through constitutional reasoning.

L1 (Axiom): NO proof field - axiomatic by definition
L2 (Value): NO proof field - derived from axioms but still foundational

AGENTESE paths:
- concept.axiom.*
- concept.value.*

Spec: spec/protocols/zero-seed.md
"""

from dataclasses import dataclass, field
from typing import Any

from ..universe import DataclassSchema

__all__ = [
    # Contracts
    "AxiomCrystal",
    "ValueCrystal",
    # Schemas
    "AXIOM_SCHEMA",
    "VALUE_SCHEMA",
]


# =============================================================================
# L1: Axiom Crystal (Foundational Truths)
# =============================================================================


@dataclass(frozen=True)
class AxiomCrystal:
    """
    L1: Axiomatic foundation - unproven, self-evident truths.

    Axioms are the bedrock of the Zero Seed holarchy. They:
    - Require NO proof (axiomatic by definition)
    - Define the constitutional ground
    - Are domain-specific (mathematics, ethics, design, etc.)
    - Are immutable once declared

    Examples:
    - Mathematics: "∀x: x = x" (reflexivity)
    - Constitution: "Tasteful > feature-complete"
    - Ethics: "Transparency over convenience"

    Attributes:
        content: The axiom statement itself
        domain: Constitutional domain ("constitution", "mathematics", "ethics", etc.)
        tags: Classification tags (frozenset for immutability)
    """

    content: str
    """The axiom statement (self-evident truth)."""

    domain: str
    """Constitutional domain (e.g., 'constitution', 'mathematics', 'ethics')."""

    tags: frozenset[str] = field(default_factory=frozenset)
    """Classification tags for discovery and composition."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "content": self.content,
            "domain": self.domain,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AxiomCrystal":
        """Deserialize from dict."""
        return cls(
            content=data["content"],
            domain=data["domain"],
            tags=frozenset(data.get("tags", [])),
        )


AXIOM_SCHEMA = DataclassSchema(
    name="concept.axiom",
    type_cls=AxiomCrystal,
)
"""
Schema for concept.axiom v1.

L1 foundational schema. Axioms have NO proof field - they ARE the proof.

AGENTESE path: concept.axiom.*
"""


# =============================================================================
# L2: Value Crystal (Derived Principles)
# =============================================================================


@dataclass(frozen=True)
class ValueCrystal:
    """
    L2: Values derived from axioms through constitutional reasoning.

    Values are principles that emerge from axiom composition. They:
    - Still have NO proof field (foundational tier)
    - Trace back to axioms via axiom_ids
    - Define operational principles
    - Guide higher-layer derivations

    Examples:
    - From "Tasteful > feature-complete" → "Depth over breadth"
    - From "Transparency" + "Joy" → "Tool transparency builds trust"

    Attributes:
        principle: The value statement
        axiom_ids: IDs of axioms this value is derived from
        tags: Classification tags
    """

    principle: str
    """The value/principle statement."""

    axiom_ids: tuple[str, ...]
    """Axiom IDs this value is derived from (constitutional lineage)."""

    tags: frozenset[str] = field(default_factory=frozenset)
    """Classification tags for discovery and composition."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "principle": self.principle,
            "axiom_ids": list(self.axiom_ids),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValueCrystal":
        """Deserialize from dict."""
        return cls(
            principle=data["principle"],
            axiom_ids=tuple(data["axiom_ids"]),
            tags=frozenset(data.get("tags", [])),
        )


VALUE_SCHEMA = DataclassSchema(
    name="concept.value",
    type_cls=ValueCrystal,
)
"""
Schema for concept.value v1.

L2 foundational schema. Values have NO proof field - derived from axioms
but still part of the foundational tier.

AGENTESE path: concept.value.*
"""
