"""
self.grow Telemetry

OpenTelemetry-compatible spans and metrics for growth operations.

AGENTESE: self.grow observability contract
"""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Iterator

# === Metrics Schema ===

GROWTH_METRICS = {
    # Counters
    "growth.recognize.invocations": "Total recognition invocations",
    "growth.recognize.gaps_found": "Total gaps found",
    "growth.propose.invocations": "Total proposal invocations",
    "growth.validate.invocations": "Total validation invocations",
    "growth.validate.passed": "Validations that passed",
    "growth.validate.failed": "Validations that failed",
    "growth.germinate.invocations": "Total germination invocations",
    "growth.promote.invocations": "Total promotion invocations",
    "growth.promote.approved": "Promotions approved",
    "growth.promote.rejected": "Promotions rejected",
    "growth.rollback.invocations": "Total rollback invocations",
    "growth.prune.invocations": "Total prune invocations",
    # Gauges
    "growth.nursery.count": "Current germinating holons",
    "growth.nursery.capacity_pct": "Nursery capacity percentage",
    "growth.budget.remaining": "Remaining entropy budget",
    "growth.budget.spent": "Entropy spent this run",
    # Histograms
    "growth.recognize.latency_ms": "Recognition latency",
    "growth.validate.score.tasteful": "Tasteful scores distribution",
    "growth.validate.score.curated": "Curated scores distribution",
    "growth.germinate.time_to_promote_days": "Days from germination to promotion",
}


# === Span Schema ===

GROWTH_TRACE_SCHEMA = {
    "name": "agentese.growth",
    "attributes": {
        # Recognition phase
        "growth.phase": "string",
        "growth.gap.pattern": "string",
        "growth.gap.confidence": "float",
        "growth.gap.evidence_count": "int",
        # Proposal phase
        "growth.proposal.handle": "string",
        "growth.proposal.hash": "string",
        "growth.proposal.context": "string",
        "growth.proposal.entity": "string",
        # Validation phase
        "growth.validation.passed": "bool",
        "growth.validation.score.tasteful": "float",
        "growth.validation.score.curated": "float",
        "growth.validation.score.ethical": "float",
        "growth.validation.score.joy": "float",
        "growth.validation.score.composable": "float",
        "growth.validation.score.heterarchical": "float",
        "growth.validation.score.generative": "float",
        "growth.validation.blockers": "string[]",
        "growth.validation.law_check.identity": "bool",
        "growth.validation.law_check.associativity": "bool",
        "growth.validation.abuse_check.passed": "bool",
        # Germination phase
        "growth.germination.usage_count": "int",
        "growth.germination.success_count": "int",
        "growth.germination.failure_patterns": "string[]",
        # Promotion phase
        "growth.promotion.stage": "string",
        "growth.promotion.approver": "string",
        "growth.promotion.rollback_token": "string",
        # Resource tracking
        "growth.entropy.spent": "float",
        "growth.entropy.remaining": "float",
        "growth.nursery.count": "int",
        "growth.nursery.capacity": "int",
    },
}


# === Lightweight Tracer (no OpenTelemetry dependency) ===


@dataclass
class GrowthSpan:
    """
    A lightweight span for growth operations.

    Compatible with OpenTelemetry but doesn't require the dependency.
    Can be exported to OTLP when infrastructure is available.
    """

    name: str
    trace_id: str = ""
    span_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: str = "UNSET"
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        import uuid

        if not self.trace_id:
            self.trace_id = str(uuid.uuid4()).replace("-", "")
        if not self.span_id:
            self.span_id = str(uuid.uuid4()).replace("-", "")[:16]

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span."""
        self.events.append(
            {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "attributes": attributes or {},
            }
        )

    def set_status(self, status: str, description: str = "") -> None:
        """Set span status (OK, ERROR, UNSET)."""
        self.status = status
        if description:
            self.attributes["status.description"] = description

    def end(self) -> None:
        """End the span."""
        self.end_time = datetime.now()
        if self.status == "UNSET":
            self.status = "OK"

    def to_dict(self) -> dict[str, Any]:
        """Export span as dictionary (OTLP-compatible)."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


@dataclass
class GrowthTracer:
    """
    Lightweight tracer for growth operations.

    Collects spans and can export to various backends.
    """

    service_name: str = "agentese.growth"
    spans: list[GrowthSpan] = field(default_factory=list)
    _current_span: GrowthSpan | None = None

    @contextmanager
    def start_span(self, name: str) -> Iterator[GrowthSpan]:
        """Start a new span."""
        span = GrowthSpan(name=name)
        old_span = self._current_span
        self._current_span = span
        try:
            yield span
        except Exception as e:
            span.set_status("ERROR", str(e))
            raise
        finally:
            span.end()
            self.spans.append(span)
            self._current_span = old_span

    @asynccontextmanager
    async def start_span_async(self, name: str) -> AsyncIterator[GrowthSpan]:
        """Start a new span (async version)."""
        span = GrowthSpan(name=name)
        old_span = self._current_span
        self._current_span = span
        try:
            yield span
        except Exception as e:
            span.set_status("ERROR", str(e))
            raise
        finally:
            span.end()
            self.spans.append(span)
            self._current_span = old_span

    @property
    def current_span(self) -> GrowthSpan | None:
        """Get the current active span."""
        return self._current_span

    def export(self) -> list[dict[str, Any]]:
        """Export all spans as dictionaries."""
        return [span.to_dict() for span in self.spans]

    def clear(self) -> None:
        """Clear collected spans."""
        self.spans.clear()


# === Lightweight Metrics (no OpenTelemetry dependency) ===


@dataclass
class Counter:
    """A simple counter metric."""

    name: str
    description: str = ""
    value: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def add(self, amount: int = 1) -> None:
        """Increment the counter."""
        self.value += amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "counter",
            "value": self.value,
            "labels": self.labels,
        }


@dataclass
class Gauge:
    """A simple gauge metric."""

    name: str
    description: str = ""
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)

    def set(self, value: float) -> None:
        """Set the gauge value."""
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "gauge",
            "value": self.value,
            "labels": self.labels,
        }


@dataclass
class Histogram:
    """A simple histogram metric."""

    name: str
    description: str = ""
    values: list[float] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    buckets: tuple[float, ...] = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def record(self, value: float) -> None:
        """Record a value."""
        self.values.append(value)

    @property
    def count(self) -> int:
        return len(self.values)

    @property
    def sum(self) -> float:
        return sum(self.values)

    @property
    def mean(self) -> float:
        if not self.values:
            return 0.0
        return self.sum / self.count

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "histogram",
            "count": self.count,
            "sum": self.sum,
            "mean": self.mean,
            "labels": self.labels,
        }


@dataclass
class GrowthMetrics:
    """
    Metrics collector for growth operations.

    Provides counters, gauges, and histograms without
    requiring OpenTelemetry infrastructure.
    """

    _counters: dict[str, Counter] = field(default_factory=dict)
    _gauges: dict[str, Gauge] = field(default_factory=dict)
    _histograms: dict[str, Histogram] = field(default_factory=dict)

    def counter(self, name: str, description: str = "") -> Counter:
        """Get or create a counter."""
        if name not in self._counters:
            desc = description or GROWTH_METRICS.get(name, "")
            self._counters[name] = Counter(name=name, description=desc)
        return self._counters[name]

    def gauge(self, name: str, description: str = "") -> Gauge:
        """Get or create a gauge."""
        if name not in self._gauges:
            desc = description or GROWTH_METRICS.get(name, "")
            self._gauges[name] = Gauge(name=name, description=desc)
        return self._gauges[name]

    def histogram(self, name: str, description: str = "") -> Histogram:
        """Get or create a histogram."""
        if name not in self._histograms:
            desc = description or GROWTH_METRICS.get(name, "")
            self._histograms[name] = Histogram(name=name, description=desc)
        return self._histograms[name]

    def export(self) -> dict[str, list[dict[str, Any]]]:
        """Export all metrics as dictionaries."""
        return {
            "counters": [c.to_dict() for c in self._counters.values()],
            "gauges": [g.to_dict() for g in self._gauges.values()],
            "histograms": [h.to_dict() for h in self._histograms.values()],
        }

    def clear(self) -> None:
        """Clear all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


# === Global Instances ===

# Default tracer instance
tracer = GrowthTracer()

# Default metrics instance
metrics = GrowthMetrics()
