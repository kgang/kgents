"""
SelfJustifyingCrystal - A Crystal that carries its own proof.

The culmination of the D-gent Crystal Unification:
- Every Crystal can justify its existence
- L1-L2 are axiomatic (no proof needed)
- L3+ require Toulmin proofs with Galois coherence
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from ..datum import Datum
from ..schemas.proof import GaloisWitnessedProof
from .crystal import Crystal, CrystalMeta

T = TypeVar("T")


@dataclass(frozen=True)
class SelfJustifyingCrystal(Generic[T]):
    """
    A typed Crystal that carries its own proof.

    Philosophy:
    "An agent is a thing that justifies its behavior."

    SelfJustifyingCrystal = Crystal + GaloisWitnessedProof

    For L1-L2 (axioms/values): proof is None (axiomatic)
    For L3+ (specs, actions, etc.): proof is required
    """

    # Core Crystal
    meta: CrystalMeta
    datum: Datum
    value: T

    # Zero Seed layer
    layer: int
    path: str  # AGENTESE path

    # Proof (required for L3+)
    proof: GaloisWitnessedProof | None = None

    @property
    def coherence(self) -> float:
        """Coherence = 1 - galois_loss of proof."""
        if self.proof is None:
            return 1.0  # Axioms have perfect coherence
        return self.proof.coherence

    @property
    def is_grounded(self) -> bool:
        """
        Is this Crystal grounded?

        L1-L2: Always grounded (axiomatic)
        L3+: Grounded if proof coherence > 0.7
        """
        if self.layer <= 2:
            return True
        if self.proof is None:
            return False
        return self.proof.coherence > 0.7

    @property
    def tier(self) -> str:
        """Evidence tier derived from loss."""
        if self.proof is None:
            return "CATEGORICAL"
        return self.proof.tier

    def validate(self, strict: bool = False) -> list[str]:
        """
        Validate Crystal meets requirements.

        Args:
            strict: If True, enforces stricter rules (e.g., coherence threshold)

        Returns list of validation errors (empty if valid).
        """
        errors = []

        if self.layer < 1 or self.layer > 7:
            errors.append(f"Invalid layer: {self.layer} (must be 1-7)")

        if self.layer >= 3 and self.proof is None:
            errors.append(f"Layer {self.layer} requires proof")

        if self.layer <= 2 and self.proof is not None:
            errors.append("L1-L2 (axioms) should not have proofs")

        if strict and self.proof is not None and self.proof.coherence < 0.3:
            errors.append(f"Proof coherence too low: {self.proof.coherence:.2f}")

        return errors

    @classmethod
    def create_axiom(cls, value: T, path: str = "void.axiom") -> "SelfJustifyingCrystal[T]":
        """Create an axiomatic (L1) Crystal - no proof needed."""
        datum = Datum.create({"value": str(value)})  # type: ignore[arg-type]
        meta = CrystalMeta(
            schema_name="axiom",
            schema_version=1,
            created_at=datetime.now(UTC),
            layer=1,
        )
        return cls(
            meta=meta,
            datum=datum,
            value=value,
            layer=1,
            path=path,
            proof=None,
        )

    @classmethod
    def create_with_proof(
        cls,
        value: T,
        proof: GaloisWitnessedProof,
        layer: int,
        path: str,
    ) -> "SelfJustifyingCrystal[T]":
        """Create a Crystal with proof (for L3+)."""
        datum = Datum.create({"value": str(value)})  # type: ignore[arg-type]
        meta = CrystalMeta(
            schema_name="justified",
            schema_version=1,
            created_at=datetime.now(UTC),
            layer=layer,
            galois_loss=proof.galois_loss,
            proof_id=None,  # Will be set when proof is stored
        )
        crystal = cls(
            meta=meta,
            datum=datum,
            value=value,
            layer=layer,
            path=path,
            proof=proof,
        )

        # Validate basic structure (not strict)
        errors = crystal.validate(strict=False)
        if errors:
            raise ValueError(f"Invalid crystal: {errors}")

        return crystal
