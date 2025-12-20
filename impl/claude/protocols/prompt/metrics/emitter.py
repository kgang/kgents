"""
Metrics Emitter: Write metrics to JSONL files.

Wave 5 of the Evergreen Prompt System.

Emits metrics to `metrics/evergreen/` directory:
- compile_YYYY-MM-DD.jsonl: Compilation metrics
- section_YYYY-MM-DD.jsonl: Per-section metrics
- fusion_YYYY-MM-DD.jsonl: Fusion operation metrics
- habit_YYYY-MM-DD.jsonl: Habit encoding metrics

Each file contains one JSON object per line for easy streaming analysis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .schema import (
    BaseMetric,
    CompilationMetric,
    FusionMetric,
    HabitMetric,
    MetricType,
    SectionMetric,
)

if TYPE_CHECKING:
    from ..compiler import CompilationContext, CompiledPrompt
    from ..section_base import Section

logger = logging.getLogger(__name__)


@dataclass
class MetricsEmitter:
    """
    Emit metrics to JSONL files.

    Handles file creation, rotation, and writing.

    Example:
        >>> emitter = MetricsEmitter(base_dir=Path("metrics/evergreen"))
        >>> emitter.emit(CompilationMetric(...))
    """

    base_dir: Path
    enabled: bool = True
    date_format: str = "%Y-%m-%d"

    def __post_init__(self) -> None:
        """Ensure base directory exists."""
        if self.enabled:
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def emit(self, metric: BaseMetric) -> None:
        """
        Emit a metric to the appropriate file.

        Args:
            metric: The metric to emit
        """
        if not self.enabled:
            return

        try:
            file_path = self._get_file_path(metric)
            json_line = metric.to_json()

            with file_path.open("a") as f:
                f.write(json_line + "\n")

            logger.debug(f"Emitted {metric.metric_type.name} metric to {file_path}")

        except Exception as e:
            logger.warning(f"Failed to emit metric: {e}")

    def emit_all(self, metrics: list[BaseMetric]) -> None:
        """Emit multiple metrics."""
        for metric in metrics:
            self.emit(metric)

    def _get_file_path(self, metric: BaseMetric) -> Path:
        """Get the file path for a metric based on its type and date."""
        date_str = metric.timestamp.strftime(self.date_format)
        type_name = metric.metric_type.name.lower()
        filename = f"{type_name}_{date_str}.jsonl"
        return self.base_dir / filename

    def emit_compilation(
        self,
        prompt: "CompiledPrompt",
        context: "CompilationContext",
        compilation_time_ms: float = 0.0,
        checkpoint_id: str | None = None,
    ) -> CompilationMetric:
        """
        Emit metrics for a compilation run.

        Args:
            prompt: The compiled prompt
            context: Compilation context
            compilation_time_ms: Time taken to compile
            checkpoint_id: Checkpoint ID if created

        Returns:
            The emitted CompilationMetric
        """
        # Gather source paths from all sections
        source_paths: list[str] = []
        for section in prompt.sections:
            if section.source_paths:
                source_paths.extend(str(p) for p in section.source_paths)

        metric = CompilationMetric(
            section_count=len(prompt.sections),
            total_tokens=prompt.total_tokens,
            total_chars=len(prompt.content),
            compilation_time_ms=compilation_time_ms,
            source_file_count=len(set(source_paths)),
            source_paths=tuple(sorted(set(source_paths))),
            law_checks_passed=True,  # TODO: Get from validation
            determinism_verified=True,
            current_phase=context.phase.name if hasattr(context, "phase") else "",
            checkpoint_id=checkpoint_id,
        )

        self.emit(metric)
        return metric

    def emit_section(
        self,
        section: "Section",
        source_type: str = "unknown",
        rigidity: float = 0.5,
        reasoning_trace: tuple[str, ...] = (),
        included: bool = True,
    ) -> SectionMetric:
        """
        Emit metrics for a section compilation.

        Args:
            section: The compiled section
            source_type: Type of source used
            rigidity: Rigidity of the source
            reasoning_trace: Reasoning trace for the section
            included: Whether section was included in final output

        Returns:
            The emitted SectionMetric
        """
        metric = SectionMetric(
            section_name=section.name,
            content_chars=len(section.content),
            token_cost=section.token_cost,
            source_type=source_type,
            source_path=str(section.source_paths[0]) if section.source_paths else None,
            rigidity=rigidity,
            reasoning_trace_hash=SectionMetric.hash_trace(reasoning_trace),
            required=section.required,
            included=included,
        )

        self.emit(metric)
        return metric

    def emit_fusion(
        self,
        section_name: str,
        source_count: int,
        similarity_score: float,
        similarity_strategy: str,
        conflict_count: int,
        conflict_types: list[str],
        resolution_count: int,
        resolution_strategies: list[str],
        chosen_sources: list[str],
        fused_chars: int,
        effective_rigidity: float,
    ) -> FusionMetric:
        """
        Emit metrics for a fusion operation.

        Args:
            section_name: Name of the section being fused
            source_count: Number of sources being fused
            similarity_score: Computed similarity score
            similarity_strategy: Strategy used for similarity
            conflict_count: Number of conflicts detected
            conflict_types: Types of conflicts found
            resolution_count: Number of resolutions applied
            resolution_strategies: Strategies used for resolution
            chosen_sources: Which sources were chosen
            fused_chars: Length of fused content
            effective_rigidity: Rigidity of fused result

        Returns:
            The emitted FusionMetric
        """
        blocking = sum(1 for ct in conflict_types if ct in ("CONTRADICTION", "CRITICAL"))

        metric = FusionMetric(
            section_name=section_name,
            source_count=source_count,
            similarity_score=similarity_score,
            similarity_strategy=similarity_strategy,
            conflict_count=conflict_count,
            conflict_types=tuple(conflict_types),
            blocking_conflicts=blocking,
            resolution_count=resolution_count,
            resolution_strategies=tuple(resolution_strategies),
            chosen_sources=tuple(chosen_sources),
            fused_chars=fused_chars,
            effective_rigidity=effective_rigidity,
        )

        self.emit(metric)
        return metric

    def emit_habit(
        self,
        git_patterns: int,
        session_patterns: int,
        code_patterns: int,
        verbosity: float,
        formality: float,
        risk_tolerance: float,
        confidence: float,
        top_domains: list[str],
        top_sections: list[str],
    ) -> HabitMetric:
        """
        Emit metrics for habit encoding.

        Args:
            git_patterns: Number of git patterns found
            session_patterns: Number of session patterns found
            code_patterns: Number of code patterns found
            verbosity: Derived verbosity preference
            formality: Derived formality preference
            risk_tolerance: Derived risk tolerance
            confidence: Overall confidence in policy
            top_domains: Top domain focus areas
            top_sections: Top section priorities

        Returns:
            The emitted HabitMetric
        """
        metric = HabitMetric(
            git_patterns_found=git_patterns,
            session_patterns_found=session_patterns,
            code_patterns_found=code_patterns,
            verbosity=verbosity,
            formality=formality,
            risk_tolerance=risk_tolerance,
            confidence=confidence,
            domain_focus_count=len(top_domains),
            top_domains=tuple(top_domains[:5]),
            section_weight_count=len(top_sections),
            top_sections=tuple(top_sections[:5]),
        )

        self.emit(metric)
        return metric


# Global emitter instance (can be configured)
_default_emitter: MetricsEmitter | None = None


def get_default_emitter() -> MetricsEmitter:
    """Get or create the default metrics emitter."""
    global _default_emitter
    if _default_emitter is None:
        # Default to metrics/evergreen/ relative to project root
        # In production, this should be configured
        base_dir = Path("metrics/evergreen")
        _default_emitter = MetricsEmitter(base_dir=base_dir, enabled=True)
    return _default_emitter


def set_default_emitter(emitter: MetricsEmitter) -> None:
    """Set the default metrics emitter."""
    global _default_emitter
    _default_emitter = emitter


def emit_metric(metric: BaseMetric) -> None:
    """Emit a metric using the default emitter."""
    emitter = get_default_emitter()
    emitter.emit(metric)


def emit_compilation_metrics(
    prompt: "CompiledPrompt",
    context: "CompilationContext",
    compilation_time_ms: float = 0.0,
    checkpoint_id: str | None = None,
) -> CompilationMetric:
    """Emit compilation metrics using the default emitter."""
    emitter = get_default_emitter()
    return emitter.emit_compilation(prompt, context, compilation_time_ms, checkpoint_id)


__all__ = [
    "MetricsEmitter",
    "get_default_emitter",
    "set_default_emitter",
    "emit_metric",
    "emit_compilation_metrics",
]
