"""
Metrics Schema: Data structures for Evergreen metrics.

All metrics are designed to be:
1. JSONL-serializable (one JSON object per line)
2. Immutable (frozen dataclasses)
3. Timestamped (automatic)
4. Tagged (for filtering)

Schema follows OpenTelemetry-inspired patterns for observability.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class MetricType(Enum):
    """Types of metrics emitted."""

    COMPILATION = auto()  # Overall compilation metrics
    SECTION = auto()  # Per-section metrics
    FUSION = auto()  # Fusion operation metrics
    HABIT = auto()  # Habit encoding metrics
    ROLLBACK = auto()  # Rollback operation metrics
    TEXTGRAD = auto()  # TextGRAD improvement metrics


@dataclass(frozen=True)
class BaseMetric:
    """
    Base class for all metrics.

    Provides common fields and serialization.
    """

    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: tuple[str, ...] = ()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = self._to_dict()
        # Convert datetime to ISO format
        data["timestamp"] = data["timestamp"].isoformat()
        # Convert enum to string
        data["metric_type"] = data["metric_type"].name
        return json.dumps(data)

    def _to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (for subclass override)."""
        return asdict(self)


@dataclass(frozen=True)
class CompilationMetric(BaseMetric):
    """
    Metrics for a full compilation run.

    Captures overall statistics about the compilation.
    """

    metric_type: MetricType = field(default=MetricType.COMPILATION)

    # Compilation info
    section_count: int = 0
    total_tokens: int = 0
    total_chars: int = 0
    compilation_time_ms: float = 0.0

    # Source info
    source_file_count: int = 0
    source_paths: tuple[str, ...] = ()

    # Quality metrics
    law_checks_passed: bool = True
    determinism_verified: bool = True

    # Context info
    current_phase: str = ""
    checkpoint_id: str | None = None


@dataclass(frozen=True)
class SectionMetric(BaseMetric):
    """
    Metrics for a single section compilation.

    Tracks provenance and quality per section.
    """

    metric_type: MetricType = field(default=MetricType.SECTION)

    # Section info
    section_name: str = ""
    content_chars: int = 0
    token_cost: int = 0

    # Source info
    source_type: str = ""  # "file", "git", "llm", "template", "fallback"
    source_path: str | None = None
    rigidity: float = 0.5

    # Reasoning
    reasoning_trace_hash: str = ""  # Hash of reasoning trace for deduplication

    # Quality
    required: bool = True
    included: bool = True

    @staticmethod
    def hash_trace(trace: tuple[str, ...]) -> str:
        """Hash a reasoning trace for storage."""
        content = "\n".join(trace)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class FusionMetric(BaseMetric):
    """
    Metrics for a fusion operation.

    Tracks similarity, conflicts, and resolutions.
    """

    metric_type: MetricType = field(default=MetricType.FUSION)

    # Operation info
    section_name: str = ""
    source_count: int = 0

    # Similarity
    similarity_score: float = 0.0
    similarity_strategy: str = ""

    # Conflicts
    conflict_count: int = 0
    conflict_types: tuple[str, ...] = ()
    blocking_conflicts: int = 0

    # Resolutions
    resolution_count: int = 0
    resolution_strategies: tuple[str, ...] = ()
    chosen_sources: tuple[str, ...] = ()

    # Result
    fused_chars: int = 0
    effective_rigidity: float = 0.5


@dataclass(frozen=True)
class HabitMetric(BaseMetric):
    """
    Metrics for habit encoding.

    Tracks pattern analysis and policy derivation.
    """

    metric_type: MetricType = field(default=MetricType.HABIT)

    # Analysis info
    git_patterns_found: int = 0
    session_patterns_found: int = 0
    code_patterns_found: int = 0

    # Policy result
    verbosity: float = 0.5
    formality: float = 0.5
    risk_tolerance: float = 0.5
    confidence: float = 0.5

    # Domain focus
    domain_focus_count: int = 0
    top_domains: tuple[str, ...] = ()

    # Section weights
    section_weight_count: int = 0
    top_sections: tuple[str, ...] = ()


@dataclass(frozen=True)
class RollbackMetric(BaseMetric):
    """
    Metrics for rollback operations.

    Tracks checkpoint usage and restoration.
    """

    metric_type: MetricType = field(default=MetricType.ROLLBACK)

    # Operation info
    operation: str = ""  # "checkpoint", "rollback", "diff"
    checkpoint_id: str = ""

    # Checkpoint info (for checkpoint operation)
    before_chars: int = 0
    after_chars: int = 0
    sections_changed: int = 0
    reason: str = ""

    # Rollback info (for rollback operation)
    restored_to: str = ""
    checkpoints_skipped: int = 0


@dataclass(frozen=True)
class TextGRADMetric(BaseMetric):
    """
    Metrics for TextGRAD improvement operations.

    Tracks feedback parsing and improvement application.
    """

    metric_type: MetricType = field(default=MetricType.TEXTGRAD)

    # Feedback info
    feedback_length: int = 0
    targets_identified: int = 0
    target_sections: tuple[str, ...] = ()

    # Gradient info
    gradient_steps: int = 0
    gradient_directions: tuple[str, ...] = ()

    # Application info
    sections_modified: int = 0
    chars_changed: int = 0
    learning_rate: float = 0.5

    # Result
    improvement_applied: bool = False
    checkpoint_created: bool = False
    checkpoint_id: str | None = None


__all__ = [
    "MetricType",
    "BaseMetric",
    "CompilationMetric",
    "SectionMetric",
    "FusionMetric",
    "HabitMetric",
    "RollbackMetric",
    "TextGRADMetric",
]
