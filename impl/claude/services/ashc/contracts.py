"""
ASHC Proof-Generation Contracts.

Data classes for the proof-generating ASHC pipeline:
- ProofObligation: A property that needs to be proven
- ProofAttempt: A single attempt to discharge an obligation
- VerifiedLemma: A proven fact in the lemma database
- ProofSearchResult: Result of a proof search session

Heritage: Kleppmann (§12), Polynomial Functors (§10), Stigmergic Cognition (§13)

The Core Insight (spec/protocols/proof-generation.md):
    "LLM hallucinations don't matter for proofs because proof checkers
    reject invalid proofs." — Martin Kleppmann

    The LLM can hallucinate all it wants. The proof checker is the gatekeeper.
    If the proof checks, the theorem holds. If it doesn't, try again.

Teaching:
    gotcha: All contracts are frozen dataclasses. Create new instances
            with updated fields, don't mutate existing ones. This enables
            safe composition and audit trails.

AGENTESE:
    concept.ashc.obligation    → Generate proof obligation from failure
    concept.ashc.prove         → Attempt to discharge obligation
    concept.ashc.lemma         → Query verified lemmas
    concept.ashc.graph         → Visualize lemma dependency graph
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType

# =============================================================================
# Type Aliases
# =============================================================================

ObligationId = NewType("ObligationId", str)
LemmaId = NewType("LemmaId", str)
ProofAttemptId = NewType("ProofAttemptId", str)


# =============================================================================
# Enums
# =============================================================================


class ProofStatus(Enum):
    """
    Status of a proof obligation or attempt.

    Teaching:
        gotcha: Use auto() for status values—we care about the semantic
                meaning, not the underlying integer. Comparison is by
                enum member, not value.
    """

    PENDING = auto()  # Awaiting proof search
    SEARCHING = auto()  # LLM actively searching
    VERIFIED = auto()  # Checker accepted proof
    FAILED = auto()  # All attempts exhausted
    TIMEOUT = auto()  # Budget exceeded


class ObligationSource(Enum):
    """
    Source of a proof obligation.

    Test failures are the most common source, but type signatures (AD-013)
    and spec assertions can also generate obligations.
    """

    TEST = auto()  # From pytest assertion failure
    TYPE = auto()  # From AD-013 typed AGENTESE path
    SPEC = auto()  # From spec document assertions
    COMPOSITION = auto()  # From pipeline composition validation


# =============================================================================
# Core Contracts
# =============================================================================


@dataclass(frozen=True)
class ProofObligation:
    """
    A property that needs to be proven.

    Generated from:
    - Test failures (most common)
    - Type signatures (AD-013)
    - Spec assertions
    - Pipeline composition validation

    The obligation captures the formal statement to prove, its origin,
    and context that may help with proof search.

    Laws:
        1. Immutability: Once created, an obligation never changes
        2. Traceability: source_location links back to origin
        3. Compositionality: context is a tuple (immutable, hashable)

    Teaching:
        gotcha: ProofObligation is immutable. Create new obligations
                with updated context, don't mutate existing ones.

    Example:
        >>> obl = ProofObligation(
        ...     id=ObligationId("obl-001"),
        ...     property="∀ x: int. x + 0 == x",
        ...     source=ObligationSource.TEST,
        ...     source_location="test_math.py:42",
        ... )
        >>> obl.property
        '∀ x: int. x + 0 == x'
    """

    id: ObligationId
    property: str  # Formal statement to prove (Lean/Dafny syntax)
    source: ObligationSource
    source_location: str  # File:line or AGENTESE path
    context: tuple[str, ...] = ()  # Relevant code snippets, hints
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "id": str(self.id),
            "property": self.property,
            "source": self.source.name,
            "source_location": self.source_location,
            "context": list(self.context),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProofObligation:
        """Deserialize from dictionary."""
        return cls(
            id=ObligationId(data["id"]),
            property=data["property"],
            source=ObligationSource[data["source"]],
            source_location=data["source_location"],
            context=tuple(data.get("context", [])),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def with_context(self, *additional: str) -> ProofObligation:
        """
        Return a new obligation with additional context.

        Example:
            >>> obl2 = obl.with_context("Hint: use induction on x")
        """
        return ProofObligation(
            id=self.id,
            property=self.property,
            source=self.source,
            source_location=self.source_location,
            context=self.context + additional,
            created_at=self.created_at,
        )


@dataclass(frozen=True)
class ProofAttempt:
    """
    A single attempt to discharge a proof obligation.

    Teaching:
        gotcha: We store failed attempts too—they inform future searches.
                "What didn't work" is as valuable as "what worked."
                The tactics_that_failed set helps avoid repeating mistakes.

    Laws:
        1. Attempts are immutable records
        2. Failed attempts inform future searches (stigmergic learning)
        3. duration_ms enables performance analysis
    """

    id: ProofAttemptId
    obligation_id: ObligationId
    proof_source: str  # The proof text (Lean/Dafny)
    checker: str  # "lean4", "dafny", "verus"
    result: ProofStatus
    checker_output: str  # Raw output from checker
    tactics_used: tuple[str, ...] = ()
    duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "id": str(self.id),
            "obligation_id": str(self.obligation_id),
            "proof_source": self.proof_source,
            "checker": self.checker,
            "result": self.result.name,
            "checker_output": self.checker_output,
            "tactics_used": list(self.tactics_used),
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProofAttempt:
        """Deserialize from dictionary."""
        return cls(
            id=ProofAttemptId(data["id"]),
            obligation_id=ObligationId(data["obligation_id"]),
            proof_source=data["proof_source"],
            checker=data["checker"],
            result=ProofStatus[data["result"]],
            checker_output=data["checker_output"],
            tactics_used=tuple(data.get("tactics_used", [])),
            duration_ms=data.get("duration_ms", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass(frozen=True)
class VerifiedLemma:
    """
    A proven fact in the lemma database.

    Once verified, lemmas are immutable facts. They can be:
    - Indexed for retrieval
    - Composed with other lemmas
    - Used as hints for future proof searches

    The usage_count enables stigmergic reinforcement (§13):
    more-used lemmas rank higher in future searches.

    Laws:
        1. Monotonicity: lemmas(t+1) ⊇ lemmas(t)
        2. Soundness: verified(lemma) → property_holds(lemma.statement)
        3. Compositionality: compose(lemma_a, lemma_b) → valid_proof

    Teaching:
        gotcha: VerifiedLemma includes the full proof—not just the statement.
                This enables proof reuse and composition.
    """

    id: LemmaId
    statement: str  # The formal theorem statement
    proof: str  # The complete proof
    checker: str  # Which checker verified this
    obligation_id: ObligationId  # Origin obligation
    dependencies: tuple[LemmaId, ...] = ()  # Lemmas this builds on
    usage_count: int = 0  # For stigmergic reinforcement
    verified_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "id": str(self.id),
            "statement": self.statement,
            "proof": self.proof,
            "checker": self.checker,
            "obligation_id": str(self.obligation_id),
            "dependencies": [str(d) for d in self.dependencies],
            "usage_count": self.usage_count,
            "verified_at": self.verified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerifiedLemma:
        """Deserialize from dictionary."""
        return cls(
            id=LemmaId(data["id"]),
            statement=data["statement"],
            proof=data["proof"],
            checker=data["checker"],
            obligation_id=ObligationId(data["obligation_id"]),
            dependencies=tuple(LemmaId(d) for d in data.get("dependencies", [])),
            usage_count=data.get("usage_count", 0),
            verified_at=datetime.fromisoformat(data["verified_at"]),
        )

    def with_incremented_usage(self) -> VerifiedLemma:
        """
        Return a new lemma with incremented usage count.

        Called when this lemma is used as a hint for a successful proof.
        """
        return VerifiedLemma(
            id=self.id,
            statement=self.statement,
            proof=self.proof,
            checker=self.checker,
            obligation_id=self.obligation_id,
            dependencies=self.dependencies,
            usage_count=self.usage_count + 1,
            verified_at=self.verified_at,
        )


@dataclass
class ProofSearchResult:
    """
    Result of a proof search session.

    Contains all attempts (successful and failed) for analysis.
    Unlike the other contracts, this is mutable during search
    (attempts are appended as they occur).

    Teaching:
        gotcha: ProofSearchResult is the ONLY mutable contract.
                It accumulates attempts during search, then becomes
                effectively immutable once search completes.
    """

    obligation: ProofObligation
    attempts: list[ProofAttempt] = field(default_factory=list)
    lemma: VerifiedLemma | None = None  # If successful
    budget_used: int = 0  # Attempts made
    budget_total: int = 0  # Attempts allowed

    @property
    def succeeded(self) -> bool:
        """True if a valid proof was found."""
        return self.lemma is not None

    @property
    def tactics_that_failed(self) -> set[str]:
        """
        Tactics to avoid in future searches.

        Stigmergic anti-pheromone: mark failed paths to avoid repetition.
        """
        failed: set[str] = set()
        for attempt in self.attempts:
            if attempt.result == ProofStatus.FAILED:
                failed.update(attempt.tactics_used)
        return failed

    @property
    def tactics_that_succeeded(self) -> set[str]:
        """Tactics that worked in successful attempts."""
        succeeded: set[str] = set()
        for attempt in self.attempts:
            if attempt.result == ProofStatus.VERIFIED:
                succeeded.update(attempt.tactics_used)
        return succeeded

    @property
    def budget_remaining(self) -> int:
        """Remaining proof attempts in budget."""
        return max(0, self.budget_total - self.budget_used)

    @property
    def avg_attempt_duration_ms(self) -> float:
        """Average duration of proof attempts in milliseconds."""
        if not self.attempts:
            return 0.0
        total = sum(a.duration_ms for a in self.attempts)
        return total / len(self.attempts)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "obligation": self.obligation.to_dict(),
            "attempts": [a.to_dict() for a in self.attempts],
            "lemma": self.lemma.to_dict() if self.lemma else None,
            "budget_used": self.budget_used,
            "budget_total": self.budget_total,
            "succeeded": self.succeeded,
            "tactics_failed": list(self.tactics_that_failed),
        }


# =============================================================================
# Proof Search Configuration
# =============================================================================


@dataclass(frozen=True)
class ProofSearchConfig:
    """
    Configuration for proof search phases.

    Budget Strategy (from Spec):
        | Phase  | Attempts | Tactics                        | Purpose              |
        |--------|----------|--------------------------------|----------------------|
        | Quick  | 10       | simp, auto, trivial            | Catch easy proofs    |
        | Medium | 50       | + linarith, omega, decide      | Most proofs here     |
        | Deep   | 200      | + blast, metis, heritage       | Complex theorems     |

    Teaching:
        gotcha: Tactic progressions are tuples (immutable). Quick phase
                uses simple tactics; deeper phases add more sophisticated ones.
    """

    # Budget per phase
    quick_budget: int = 10
    medium_budget: int = 50
    deep_budget: int = 200

    # Timeout per individual proof attempt
    timeout_per_attempt_ms: int = 30000

    # Tactic progressions (immutable tuples)
    quick_tactics: tuple[str, ...] = ("simp", "auto", "trivial")
    medium_tactics: tuple[str, ...] = (
        "simp",
        "auto",
        "linarith",
        "omega",
        "decide",
    )
    deep_tactics: tuple[str, ...] = (
        "simp",
        "auto",
        "linarith",
        "omega",
        "decide",
        "blast",
        "metis",
    )

    @property
    def total_budget(self) -> int:
        """Total proof attempts across all phases."""
        return self.quick_budget + self.medium_budget + self.deep_budget

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "quick_budget": self.quick_budget,
            "medium_budget": self.medium_budget,
            "deep_budget": self.deep_budget,
            "timeout_per_attempt_ms": self.timeout_per_attempt_ms,
            "quick_tactics": list(self.quick_tactics),
            "medium_tactics": list(self.medium_tactics),
            "deep_tactics": list(self.deep_tactics),
            "total_budget": self.total_budget,
        }


# =============================================================================
# Checker Result (Bridge to external proof checkers)
# =============================================================================


@dataclass(frozen=True)
class CheckerResult:
    """
    Result from a proof checker (Dafny, Lean4, Verus).

    Teaching:
        gotcha: Dafny outputs to stderr even on success. Parse exit code,
                not output presence, to determine success.
    """

    success: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    duration_ms: int = 0

    @property
    def is_timeout(self) -> bool:
        """True if verification timed out."""
        return any("timeout" in e.lower() for e in self.errors)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "duration_ms": self.duration_ms,
            "is_timeout": self.is_timeout,
        }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Type aliases
    "ObligationId",
    "LemmaId",
    "ProofAttemptId",
    # Enums
    "ProofStatus",
    "ObligationSource",
    # Core contracts
    "ProofObligation",
    "ProofAttempt",
    "VerifiedLemma",
    "ProofSearchResult",
    # Configuration
    "ProofSearchConfig",
    # Checker bridge
    "CheckerResult",
]
