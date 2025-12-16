"""
Metrics Module: Observability for the Evergreen Prompt System.

Wave 5 of the Prompt Monad architecture.

Emits JSONL metrics for:
- Per-section provenance (source, rigidity, reasoning hash)
- Fusion decisions (conflicts, resolutions)
- Compilation statistics (token counts, timing)
- Habit encoding results

Metrics are emitted to `metrics/evergreen/*.jsonl` for analysis.
"""

from .emitter import (
    MetricsEmitter,
    emit_compilation_metrics,
    emit_metric,
)
from .schema import (
    CompilationMetric,
    FusionMetric,
    HabitMetric,
    MetricType,
    SectionMetric,
)

__all__ = [
    # Schema
    "MetricType",
    "CompilationMetric",
    "SectionMetric",
    "FusionMetric",
    "HabitMetric",
    # Emitter
    "MetricsEmitter",
    "emit_metric",
    "emit_compilation_metrics",
]
