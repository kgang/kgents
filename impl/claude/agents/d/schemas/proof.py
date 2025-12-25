"""
GaloisWitnessedProof - Toulmin proof extended with Galois loss quantification.

The proof IS the decision. Coherence = 1 - galois_loss.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any


@dataclass(frozen=True)
class GaloisWitnessedProof:
    """
    Toulmin proof extended with Galois loss quantification.

    Every decision carries its own justification via:
    - data: Evidence supporting the claim
    - warrant: Reasoning connecting data to claim
    - claim: The conclusion/decision
    - backing: Support for the warrant
    - qualifier: Certainty level
    - rebuttals: Potential defeaters

    Plus Galois extensions:
    - galois_loss: L(proof) in [0, 1]
    - loss_decomposition: Loss per component
    - tier: Evidence tier (CATEGORICAL, EMPIRICAL, etc.)
    """

    # Toulmin fields
    data: str
    warrant: str
    claim: str
    backing: str
    qualifier: str = "probably"
    rebuttals: tuple[str, ...] = field(default_factory=tuple)

    # Evidence metadata
    tier: str = "EMPIRICAL"  # CATEGORICAL, EMPIRICAL, AESTHETIC, SOMATIC, CHAOTIC
    principles: tuple[str, ...] = field(default_factory=tuple)  # Constitutional principles

    # Galois extensions
    galois_loss: float = 0.0
    loss_decomposition: dict[str, float] = field(default_factory=dict)

    # Provenance
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss. Core insight of Galois upgrade."""
        return 1.0 - self.galois_loss

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "warrant": self.warrant,
            "claim": self.claim,
            "backing": self.backing,
            "qualifier": self.qualifier,
            "rebuttals": list(self.rebuttals),
            "tier": self.tier,
            "principles": list(self.principles),
            "galois_loss": self.galois_loss,
            "loss_decomposition": self.loss_decomposition,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GaloisWitnessedProof":
        return cls(
            data=d["data"],
            warrant=d["warrant"],
            claim=d["claim"],
            backing=d["backing"],
            qualifier=d.get("qualifier", "probably"),
            rebuttals=tuple(d.get("rebuttals", [])),
            tier=d.get("tier", "EMPIRICAL"),
            principles=tuple(d.get("principles", [])),
            galois_loss=d.get("galois_loss", 0.0),
            loss_decomposition=d.get("loss_decomposition", {}),
            created_at=datetime.fromisoformat(d["created_at"]) if "created_at" in d else datetime.now(UTC),
        )


# Schema for Universe registration
from agents.d.universe import DataclassSchema

PROOF_SCHEMA = DataclassSchema(name="galois.proof", type_cls=GaloisWitnessedProof)
