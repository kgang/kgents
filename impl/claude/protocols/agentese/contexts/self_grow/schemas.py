"""
self.grow Schemas

All dataclasses for the autopoietic holon generator.

AGENTESE: self.grow.*
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

# === Affordances by Archetype ===

SELF_GROW_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "gardener": (
        "recognize",
        "propose",
        "validate",
        "germinate",
        "promote",
        "prune",
        "rollback",
        "witness",
        "nursery",
        "budget",
    ),
    "architect": (
        "recognize",
        "propose",
        "validate",
        "witness",
        "nursery",
        "budget",
    ),
    "admin": (
        "promote",
        "rollback",
        "prune",
        "witness",
        "nursery",
        "budget",
    ),
    "scholar": ("witness", "nursery", "budget"),
    "default": ("witness", "budget"),
}


# === Error Schemas ===


@dataclass(frozen=True)
class GrowthRelevantError:
    """Schema for errors that feed gap recognition."""

    # Identity
    error_id: str
    timestamp: datetime
    trace_id: str

    # Classification
    error_type: Literal[
        "PathNotFoundError",
        "AffordanceError",
        "CompositionViolationError",
        "ObserverRequiredError",
    ]

    # Context
    attempted_path: str
    context: str
    holon: str
    aspect: str | None

    # Observer
    observer_archetype: str
    observer_name: str

    # Suggestion (from sympathetic error)
    suggestion: str | None = None

    # Frequency
    occurrence_count: int = 1


# === Recognition Schemas ===


@dataclass
class RecognitionQuery:
    """Query contract for gap recognition."""

    # Time bounds
    lookback_hours: int = 168  # 7 days default
    max_errors: int = 10000

    # Filtering
    error_types: tuple[str, ...] = (
        "PathNotFoundError",
        "AffordanceError",
    )
    min_occurrences: int = 5
    exclude_patterns: tuple[str, ...] = ()

    # Cost caps
    max_entropy_cost: float = 0.25
    max_query_time_seconds: float = 30.0

    # Output limits
    max_gaps_returned: int = 10


@dataclass
class GapRecognition:
    """A recognized gap in the ontology."""

    # Identity
    gap_id: str

    # Location
    context: str
    holon: str
    aspect: str | None = None

    # Evidence
    pattern: str = ""
    evidence: list[GrowthRelevantError] = field(default_factory=list)
    evidence_count: int = 0
    archetype_diversity: int = 0

    # Analogues
    analogues: list[str] = field(default_factory=list)
    similarity_scores: dict[str, float] = field(default_factory=dict)

    # Confidence
    confidence: float = 0.0
    confidence_factors: dict[str, float] = field(default_factory=dict)

    # Classification
    gap_type: Literal[
        "missing_holon",
        "missing_affordance",
        "missing_relation",
        "semantic_gap",
    ] = "missing_holon"

    # Cost tracking
    entropy_cost: float = 0.0

    @classmethod
    def create(
        cls,
        context: str,
        holon: str,
        *,
        aspect: str | None = None,
        gap_type: Literal[
            "missing_holon", "missing_affordance", "missing_relation", "semantic_gap"
        ] = "missing_holon",
    ) -> "GapRecognition":
        """Create a new gap recognition with generated ID."""
        return cls(
            gap_id=str(uuid.uuid4()),
            context=context,
            holon=holon,
            aspect=aspect,
            gap_type=gap_type,
        )


# === Proposal Schemas ===


@dataclass
class HolonProposal:
    """A proposal for a new holon."""

    # Identity
    proposal_id: str
    content_hash: str = ""

    # Source
    gap: GapRecognition | None = None
    proposed_by: str = ""
    proposed_at: datetime = field(default_factory=datetime.now)

    # The proposed holon
    entity: str = ""
    context: str = ""
    version: str = "0.1.0"

    # Justification (Tasteful principle)
    why_exists: str = ""

    # Affordances (Polymorphic principle)
    affordances: dict[str, list[str]] = field(default_factory=dict)

    # Manifest (Observer-dependent perception)
    manifest: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Relations (Compositional principle)
    relations: dict[str, list[str]] = field(default_factory=dict)

    # State schema (for D-gent persistence)
    state: dict[str, str] = field(default_factory=dict)

    # Behaviors (Aspect implementations)
    behaviors: dict[str, str] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute deterministic content hash."""
        canonical = json.dumps(
            {
                "entity": self.entity,
                "context": self.context,
                "why_exists": self.why_exists,
                "affordances": self.affordances,
                "manifest": self.manifest,
                "relations": self.relations,
                "state": self.state,
                "behaviors": self.behaviors,
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()

    def __post_init__(self) -> None:
        """Ensure content hash is set."""
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def to_markdown(self) -> str:
        """Generate spec markdown from proposal."""
        lines = [
            f"# {self.context}.{self.entity}",
            "",
            f"**Version:** {self.version}",
            f"**Proposed by:** {self.proposed_by}",
            f"**Date:** {self.proposed_at.isoformat()}",
            "",
            "## Why This Exists",
            "",
            self.why_exists,
            "",
            "## Affordances",
            "",
        ]

        for archetype, verbs in self.affordances.items():
            lines.append(f"### {archetype}")
            for verb in verbs:
                lines.append(f"- {verb}")
            lines.append("")

        if self.behaviors:
            lines.append("## Behaviors")
            lines.append("")
            for aspect, desc in self.behaviors.items():
                lines.append(f"### {aspect}")
                lines.append(desc)
                lines.append("")

        if self.relations:
            lines.append("## Relations")
            lines.append("")
            for rel_type, targets in self.relations.items():
                lines.append(f"### {rel_type}")
                for target in targets:
                    lines.append(f"- {target}")
                lines.append("")

        return "\n".join(lines)

    @classmethod
    def create(
        cls,
        entity: str,
        context: str,
        why_exists: str,
        proposed_by: str,
        *,
        gap: GapRecognition | None = None,
        affordances: dict[str, list[str]] | None = None,
        behaviors: dict[str, str] | None = None,
    ) -> "HolonProposal":
        """Factory method for creating proposals."""
        return cls(
            proposal_id=str(uuid.uuid4()),
            entity=entity,
            context=context,
            why_exists=why_exists,
            proposed_by=proposed_by,
            gap=gap,
            affordances=affordances or {},
            behaviors=behaviors or {},
        )


# === Validation Schemas ===


@dataclass
class LawCheckResult:
    """Result of checking AGENTESE category laws."""

    identity_holds: bool = True
    associativity_holds: bool = True
    composition_valid: bool = True
    errors: list[str] = field(default_factory=list)


@dataclass
class AbuseCheckResult:
    """Result of red-team abuse detection."""

    passed: bool = True
    risk_level: Literal["low", "medium", "high", "critical"] = "low"
    concerns: list[str] = field(default_factory=list)

    # Specific checks
    manipulation_risk: float = 0.0
    exfiltration_risk: float = 0.0
    privilege_escalation_risk: float = 0.0
    resource_abuse_risk: float = 0.0


@dataclass
class DuplicationCheckResult:
    """Result of checking for existing similar holons."""

    is_duplicate: bool = False
    similar_holons: list[tuple[str, float]] = field(default_factory=list)
    highest_similarity: float = 0.0
    recommendation: Literal["proceed", "merge", "reject"] = "proceed"


@dataclass
class ValidationResult:
    """Result of validating a proposal against all gates."""

    passed: bool

    # Principle scores (0.0-1.0)
    scores: dict[str, float] = field(default_factory=dict)
    reasoning: dict[str, str] = field(default_factory=dict)

    # Law checks
    law_checks: LawCheckResult = field(default_factory=LawCheckResult)

    # Abuse detection
    abuse_check: AbuseCheckResult = field(default_factory=AbuseCheckResult)

    # Duplication check
    duplication_check: DuplicationCheckResult = field(default_factory=DuplicationCheckResult)

    # Summary
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)


# === Germination Schemas ===


@dataclass
class NurseryConfig:
    """Configuration for the germination nursery."""

    # Capacity limits
    max_capacity: int = 20
    max_per_context: int = 5

    # Promotion thresholds
    min_usage_for_promotion: int = 50
    min_success_rate_for_promotion: float = 0.8

    # Pruning thresholds
    max_age_days: int = 30
    min_success_rate_for_survival: float = 0.3

    # Entropy budget (per germination)
    entropy_cost_per_germination: float = 0.1


@dataclass
class GerminatingHolon:
    """A holon in the nursery, not yet fully grown."""

    # Identity
    germination_id: str
    proposal: HolonProposal
    validation: ValidationResult

    # Implementation (JIT compiled)
    jit_source: str = ""
    jit_source_hash: str = ""

    # Usage tracking
    usage_count: int = 0
    success_count: int = 0
    failure_patterns: list[str] = field(default_factory=list)

    # Lifecycle
    germinated_at: datetime = field(default_factory=datetime.now)
    germinated_by: str = ""
    promoted_at: datetime | None = None
    pruned_at: datetime | None = None
    rollback_token: str | None = None

    @property
    def success_rate(self) -> float:
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    @property
    def age_days(self) -> int:
        return (datetime.now() - self.germinated_at).days

    def should_promote(self, config: NurseryConfig) -> bool:
        """Check if ready for promotion."""
        return (
            self.usage_count >= config.min_usage_for_promotion
            and self.success_rate >= config.min_success_rate_for_promotion
        )

    def should_prune(self, config: NurseryConfig) -> bool:
        """Check if should be pruned."""
        # Too old without promotion
        if self.age_days > config.max_age_days and not self.promoted_at:
            return True

        # Too many failures after sufficient usage
        if self.usage_count >= 20 and self.success_rate < config.min_success_rate_for_survival:
            return True

        return False


# === Promotion Schemas ===


class PromotionStage:
    """Stages of holon promotion."""

    STAGED = "staged"
    APPROVED = "approved"
    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"


@dataclass
class RollbackToken:
    """Token for rolling back a promoted holon."""

    token_id: str
    handle: str
    promoted_at: datetime
    spec_path: Path
    impl_path: Path
    spec_content: str
    impl_content: str
    expires_at: datetime

    @classmethod
    def create(
        cls,
        handle: str,
        spec_path: Path,
        impl_path: Path,
        spec_content: str = "",
        impl_content: str = "",
        rollback_window_days: int = 7,
    ) -> "RollbackToken":
        """Create a new rollback token."""
        now = datetime.now()
        return cls(
            token_id=str(uuid.uuid4()),
            handle=handle,
            promoted_at=now,
            spec_path=spec_path,
            impl_path=impl_path,
            spec_content=spec_content,
            impl_content=impl_content,
            expires_at=now + timedelta(days=rollback_window_days),
        )

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


@dataclass
class PromotionResult:
    """Result of promotion attempt."""

    success: bool
    stage: str
    handle: str
    reason: str

    # Artifacts (if successful)
    spec_path: Path | None = None
    impl_path: Path | None = None
    rollback_token: RollbackToken | None = None

    # Hashes for verification
    proposal_hash: str | None = None
    impl_hash: str | None = None


@dataclass
class RollbackResult:
    """Result of rollback attempt."""

    success: bool
    handle: str
    reason: str
    restored_spec: bool = False
    restored_impl: bool = False


# === Budget Schemas ===


@dataclass
class GrowthBudgetConfig:
    """Configuration for growth entropy budget."""

    # Per-run limits
    max_entropy_per_run: float = 1.0
    recognize_cost: float = 0.25
    propose_cost: float = 0.15
    validate_cost: float = 0.10
    germinate_cost: float = 0.10
    promote_cost: float = 0.05
    prune_cost: float = 0.02

    # Regeneration
    regeneration_rate_per_hour: float = 0.1


@dataclass
class GrowthBudget:
    """Tracks entropy budget for growth operations."""

    config: GrowthBudgetConfig = field(default_factory=GrowthBudgetConfig)
    remaining: float = field(default=1.0)
    spent_this_run: float = 0.0
    last_regeneration: datetime = field(default_factory=datetime.now)

    # Breakdown by operation
    spent_by_operation: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.remaining == 1.0:
            self.remaining = self.config.max_entropy_per_run

    def can_afford(self, operation: str) -> bool:
        """Check if budget allows operation."""
        cost = self._cost_for(operation)
        return self.remaining >= cost

    def spend(self, operation: str) -> float:
        """Deduct cost from budget."""
        cost = self._cost_for(operation)
        if cost > self.remaining:
            from .exceptions import BudgetExhaustedError

            raise BudgetExhaustedError(
                f"Growth budget exhausted for '{operation}'",
                remaining=self.remaining,
                requested=cost,
            )

        self.remaining -= cost
        self.spent_this_run += cost
        self.spent_by_operation[operation] = self.spent_by_operation.get(operation, 0.0) + cost
        return cost

    def regenerate(self) -> float:
        """Apply time-based regeneration."""
        now = datetime.now()
        hours_elapsed = (now - self.last_regeneration).total_seconds() / 3600
        regenerated = hours_elapsed * self.config.regeneration_rate_per_hour

        old_remaining = self.remaining
        self.remaining = min(
            self.config.max_entropy_per_run,
            self.remaining + regenerated,
        )
        self.last_regeneration = now

        return self.remaining - old_remaining

    def _cost_for(self, operation: str) -> float:
        """Get cost for operation."""
        return {
            "recognize": self.config.recognize_cost,
            "propose": self.config.propose_cost,
            "validate": self.config.validate_cost,
            "germinate": self.config.germinate_cost,
            "promote": self.config.promote_cost,
            "prune": self.config.prune_cost,
        }.get(operation, 0.1)

    def status(self) -> dict[str, Any]:
        """Get budget status as dict."""
        pct = int(self.remaining / self.config.max_entropy_per_run * 100)
        return {
            "remaining": self.remaining,
            "max": self.config.max_entropy_per_run,
            "percent": pct,
            "spent_this_run": self.spent_this_run,
            "spent_by_operation": dict(self.spent_by_operation),
            "regeneration_rate": self.config.regeneration_rate_per_hour,
        }


# === Telemetry Schemas ===


@dataclass(frozen=True)
class GrowthTelemetryConfig:
    """Configuration for growth data sources."""

    # Error Streams
    error_table: str = "agentese.errors"
    error_retention_days: int = 30
    error_sample_rate: float = 1.0

    # Trace Attributes
    trace_service: str = "agentese.logos"
    trace_attributes: tuple[str, ...] = (
        "agentese.path",
        "agentese.context",
        "agentese.holon",
        "agentese.aspect",
        "agentese.observer.archetype",
        "agentese.error.type",
        "agentese.error.suggestion",
    )

    # Metrics
    metrics_namespace: str = "agentese.growth"
    metrics_retention_days: int = 90

    # Recognition Windows
    recognition_lookback_hours: int = 168
    recognition_min_occurrences: int = 5
    recognition_cost_cap_entropy: float = 0.25
