"""
Experiment Types: Evidence-Gathering Data Structures.

Defines the core types for running experiments with Bayesian stopping:
- Experiment: Top-level experiment container
- Trial: Individual trial within an experiment
- EvidenceBundle: Compiled evidence from trials
- ExperimentConfig: Configuration for different experiment types

Philosophy:
    "Uncertainty triggers experiments, not guessing."

Teaching:
    gotcha: ExperimentConfig is a base class. Use specific config types
            (GenerateConfig, ParseConfig, LawsConfig) for type safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def generate_experiment_id() -> str:
    """Generate unique experiment ID."""
    return f"exp-{uuid4().hex[:12]}"


# =============================================================================
# Experiment Types
# =============================================================================


class ExperimentType(Enum):
    """
    Types of experiments that can be run.

    Each type gathers evidence about a different aspect of the system:
    - GENERATE: Code generation quality via VoidHarness
    - PARSE: Parser robustness and error handling
    - LAWS: Category law verification (identity, associativity)
    - COMPOSE: Tool composition correctness
    - PRINCIPLE: Principle adherence testing
    """

    GENERATE = "generate"
    PARSE = "parse"
    LAWS = "laws"
    COMPOSE = "compose"
    PRINCIPLE = "principle"


class ExperimentStatus(Enum):
    """Status of an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"  # Stopped early by Bayesian criterion


# =============================================================================
# Trial: Individual Experimental Run
# =============================================================================


@dataclass
class Trial:
    """
    Individual trial within an experiment.

    Captures:
    - Input to the trial
    - Output produced
    - Success status
    - Timing information
    - Confidence score (for Bayesian stopping)
    - Repair log (for transparency)
    """

    index: int
    input: Any
    output: Any
    success: bool
    duration_ms: float
    confidence: float = 1.0  # 1.0 = certain success, 0.0 = certain failure
    repairs: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "index": self.index,
            "input": str(self.input),
            "output": str(self.output) if self.output else None,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "confidence": self.confidence,
            "repairs": self.repairs,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Trial:
        """Create from dictionary."""
        return cls(
            index=data["index"],
            input=data["input"],
            output=data.get("output"),
            success=data["success"],
            duration_ms=data["duration_ms"],
            confidence=data.get("confidence", 1.0),
            repairs=data.get("repairs", []),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


# =============================================================================
# Evidence Bundle: Compiled Results
# =============================================================================


@dataclass
class EvidenceBundle:
    """
    Compiled evidence from a set of trials.

    Provides summary statistics and confidence metrics for decision-making.
    """

    trials_total: int
    trials_success: int
    success_rate: float
    mean_confidence: float
    std_confidence: float
    mean_duration_ms: float
    stopped_early: bool = False
    evidence_tier: str = "EMPIRICAL"  # From Mark.EvidenceTier

    @property
    def trials_failed(self) -> int:
        """Number of failed trials."""
        return self.trials_total - self.trials_success

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trials_total": self.trials_total,
            "trials_success": self.trials_success,
            "success_rate": self.success_rate,
            "mean_confidence": self.mean_confidence,
            "std_confidence": self.std_confidence,
            "mean_duration_ms": self.mean_duration_ms,
            "stopped_early": self.stopped_early,
            "evidence_tier": self.evidence_tier,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceBundle:
        """Create from dictionary."""
        return cls(
            trials_total=data["trials_total"],
            trials_success=data["trials_success"],
            success_rate=data["success_rate"],
            mean_confidence=data["mean_confidence"],
            std_confidence=data["std_confidence"],
            mean_duration_ms=data["mean_duration_ms"],
            stopped_early=data.get("stopped_early", False),
            evidence_tier=data.get("evidence_tier", "EMPIRICAL"),
        )


# =============================================================================
# Experiment Configuration
# =============================================================================


@dataclass
class ExperimentConfig:
    """
    Base configuration for experiments.

    Subclass for specific experiment types (GenerateConfig, ParseConfig, etc).
    """

    type: ExperimentType
    adaptive: bool = False  # Use Bayesian stopping?
    confidence_threshold: float = 0.95  # For adaptive stopping
    max_trials: int = 100  # Hard cap
    n: int = 10  # For fixed-N experiments

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "adaptive": self.adaptive,
            "confidence_threshold": self.confidence_threshold,
            "max_trials": self.max_trials,
            "n": self.n,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExperimentConfig:
        """Create from dictionary."""
        exp_type = ExperimentType(data["type"])

        # Dispatch to specific config type
        if exp_type == ExperimentType.GENERATE:
            return GenerateConfig.from_dict(data)
        elif exp_type == ExperimentType.PARSE:
            return ParseConfig.from_dict(data)
        elif exp_type == ExperimentType.LAWS:
            return LawsConfig.from_dict(data)
        else:
            return cls(
                type=exp_type,
                adaptive=data.get("adaptive", False),
                confidence_threshold=data.get("confidence_threshold", 0.95),
                max_trials=data.get("max_trials", 100),
                n=data.get("n", 10),
            )


@dataclass
class GenerateConfig(ExperimentConfig):
    """Configuration for code generation experiments."""

    spec: str = ""  # Code spec to implement
    model: str = "claude-sonnet-4-20250514"
    budget: int = 100_000  # Token budget

    def __init__(
        self,
        spec: str,
        model: str = "claude-sonnet-4-20250514",
        budget: int = 100_000,
        adaptive: bool = False,
        confidence_threshold: float = 0.95,
        max_trials: int = 100,
        n: int = 10,
    ):
        super().__init__(
            type=ExperimentType.GENERATE,
            adaptive=adaptive,
            confidence_threshold=confidence_threshold,
            max_trials=max_trials,
            n=n,
        )
        self.spec = spec
        self.model = model
        self.budget = budget

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d.update(
            {
                "spec": self.spec,
                "model": self.model,
                "budget": self.budget,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GenerateConfig:
        """Create from dictionary."""
        return cls(
            spec=data["spec"],
            model=data.get("model", "claude-sonnet-4-20250514"),
            budget=data.get("budget", 100_000),
            adaptive=data.get("adaptive", False),
            confidence_threshold=data.get("confidence_threshold", 0.95),
            max_trials=data.get("max_trials", 100),
            n=data.get("n", 10),
        )


@dataclass
class ParseConfig(ExperimentConfig):
    """Configuration for parser robustness experiments."""

    input_text: str = ""  # Input to parse
    strategy: str = "lazy_validation"  # Parsing strategy to test

    def __init__(
        self,
        input_text: str,
        strategy: str = "lazy_validation",
        adaptive: bool = False,
        confidence_threshold: float = 0.95,
        max_trials: int = 100,
        n: int = 10,
    ):
        super().__init__(
            type=ExperimentType.PARSE,
            adaptive=adaptive,
            confidence_threshold=confidence_threshold,
            max_trials=max_trials,
            n=n,
        )
        self.input_text = input_text
        self.strategy = strategy

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d.update(
            {
                "input_text": self.input_text,
                "strategy": self.strategy,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParseConfig:
        """Create from dictionary."""
        return cls(
            input_text=data["input_text"],
            strategy=data.get("strategy", "lazy_validation"),
            adaptive=data.get("adaptive", False),
            confidence_threshold=data.get("confidence_threshold", 0.95),
            max_trials=data.get("max_trials", 100),
            n=data.get("n", 10),
        )


@dataclass
class LawsConfig(ExperimentConfig):
    """Configuration for category law verification experiments."""

    target: str = ""  # Target to test (e.g., "services/tooling/base.py:Tool")
    laws: list[str] = field(default_factory=lambda: ["identity", "associativity"])

    def __init__(
        self,
        target: str,
        laws: list[str] | None = None,
        adaptive: bool = False,
        confidence_threshold: float = 0.95,
        max_trials: int = 100,
        n: int = 10,
    ):
        super().__init__(
            type=ExperimentType.LAWS,
            adaptive=adaptive,
            confidence_threshold=confidence_threshold,
            max_trials=max_trials,
            n=n,
        )
        self.target = target
        self.laws = laws or ["identity", "associativity"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d.update(
            {
                "target": self.target,
                "laws": self.laws,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LawsConfig:
        """Create from dictionary."""
        return cls(
            target=data["target"],
            laws=data.get("laws", ["identity", "associativity"]),
            adaptive=data.get("adaptive", False),
            confidence_threshold=data.get("confidence_threshold", 0.95),
            max_trials=data.get("max_trials", 100),
            n=data.get("n", 10),
        )


# =============================================================================
# Experiment: Top-Level Container
# =============================================================================


@dataclass
class Experiment:
    """
    Top-level experiment container.

    Tracks:
    - Configuration
    - Status
    - Trials
    - Evidence bundle
    - Witness marks
    """

    id: str = field(default_factory=generate_experiment_id)
    config: ExperimentConfig = field(default_factory=lambda: ExperimentConfig(type=ExperimentType.GENERATE))
    status: ExperimentStatus = ExperimentStatus.PENDING
    trials: list[Trial] = field(default_factory=list)
    evidence: EvidenceBundle | None = None
    mark_ids: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def duration_seconds(self) -> float | None:
        """Total experiment duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def trial_count(self) -> int:
        """Number of trials run."""
        return len(self.trials)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "trials": [t.to_dict() for t in self.trials],
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "mark_ids": self.mark_ids,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Experiment:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            config=ExperimentConfig.from_dict(data["config"]),
            status=ExperimentStatus(data["status"]),
            trials=[Trial.from_dict(t) for t in data.get("trials", [])],
            evidence=EvidenceBundle.from_dict(data["evidence"]) if data.get("evidence") else None,
            mark_ids=data.get("mark_ids", []),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
        )


__all__ = [
    # Core types
    "Experiment",
    "ExperimentType",
    "ExperimentStatus",
    "Trial",
    "EvidenceBundle",
    # Config types
    "ExperimentConfig",
    "GenerateConfig",
    "ParseConfig",
    "LawsConfig",
    # Utilities
    "generate_experiment_id",
]
