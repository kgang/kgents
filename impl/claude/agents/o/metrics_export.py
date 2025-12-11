"""
MetricsExporter: Bridge to Standard Observability Systems.

Exports Cortex metrics to standard observability formats:
- Prometheus: Text-based exposition format
- OpenTelemetry: OTLP for distributed systems
- JSON: Simple export for custom integrations

Design principles:
1. Pull-based for Prometheus (scrape endpoint)
2. Push-based for OpenTelemetry (OTLP)
3. Configurable metric prefixes and labels
4. Non-blocking metric collection

From the implementation plan:
> "Bridge to standard observability systems"
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .cortex_observer import CortexObserver


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """A single metric with labels."""

    name: str
    value: float
    metric_type: MetricType
    help_text: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float | None = None


@dataclass
class MetricsExportConfig:
    """Configuration for metrics export."""

    # Metric naming
    prefix: str = "cortex"
    include_timestamp: bool = True

    # Labels
    default_labels: dict[str, str] = field(default_factory=dict)

    # Export settings
    export_interval_seconds: float = 15.0

    # Prometheus settings
    prometheus_port: int = 9090
    prometheus_path: str = "/metrics"

    # OpenTelemetry settings
    otel_endpoint: str | None = None
    otel_service_name: str = "kgents-cortex"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricsExportConfig":
        """Create from dictionary."""
        return cls(
            prefix=data.get("prefix", "cortex"),
            include_timestamp=data.get("include_timestamp", True),
            default_labels=data.get("default_labels", {}),
            export_interval_seconds=data.get("export_interval_seconds", 15.0),
            prometheus_port=data.get("port", 9090),
            prometheus_path=data.get("path", "/metrics"),
            otel_endpoint=data.get("otel_endpoint"),
            otel_service_name=data.get("otel_service_name", "kgents-cortex"),
        )


class MetricsExporter(ABC):
    """Base class for metrics exporters."""

    def __init__(
        self,
        observer: CortexObserver,
        config: MetricsExportConfig | None = None,
    ):
        """
        Initialize exporter.

        Args:
            observer: CortexObserver to export from
            config: Export configuration
        """
        self._observer = observer
        self._config = config or MetricsExportConfig()

    def collect_metrics(self) -> list[Metric]:
        """
        Collect current metrics from observer.

        Returns:
            List of Metric objects
        """
        health = self._observer.get_health()
        prefix = self._config.prefix
        now = time.time() if self._config.include_timestamp else None
        labels = self._config.default_labels.copy()

        metrics = []

        # Overall health
        metrics.append(
            Metric(
                name=f"{prefix}_health",
                value=self._health_to_value(health.overall.value),
                metric_type=MetricType.GAUGE,
                help_text="Overall cortex health (0=unknown, 1=critical, 2=degraded, 3=healthy)",
                labels=labels,
                timestamp=now,
            )
        )

        # Left Hemisphere metrics
        left = health.left_hemisphere
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_left_hemisphere_available",
                    value=1.0 if left.available else 0.0,
                    metric_type=MetricType.GAUGE,
                    help_text="Left hemisphere availability",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_left_hemisphere_latency_ms",
                    value=left.latency_ms,
                    metric_type=MetricType.GAUGE,
                    help_text="Left hemisphere query latency in milliseconds",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_left_hemisphere_queries_total",
                    value=float(left.queries_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total left hemisphere queries",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_left_hemisphere_errors_total",
                    value=float(left.errors_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total left hemisphere errors",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        # Right Hemisphere metrics
        right = health.right_hemisphere
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_right_hemisphere_available",
                    value=1.0 if right.available else 0.0,
                    metric_type=MetricType.GAUGE,
                    help_text="Right hemisphere availability",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_right_hemisphere_latency_ms",
                    value=right.latency_ms,
                    metric_type=MetricType.GAUGE,
                    help_text="Right hemisphere search latency in milliseconds",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_right_hemisphere_vectors_count",
                    value=float(right.vectors_count),
                    metric_type=MetricType.GAUGE,
                    help_text="Number of vectors in right hemisphere",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        # Coherency metrics
        coherency = health.coherency
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_coherency_rate",
                    value=coherency.coherency_rate,
                    metric_type=MetricType.GAUGE,
                    help_text="Cross-hemisphere coherency rate (0-1)",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_ghost_count",
                    value=float(coherency.ghost_count),
                    metric_type=MetricType.GAUGE,
                    help_text="Current ghost memory count",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_ghost_healed_total",
                    value=float(coherency.ghosts_healed_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total ghost memories healed",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_stale_count",
                    value=float(coherency.stale_count),
                    metric_type=MetricType.GAUGE,
                    help_text="Current stale embedding count",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_stale_flagged_total",
                    value=float(coherency.stale_flagged_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total stale embeddings flagged",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        # Synapse metrics
        synapse = health.synapse
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_synapse_available",
                    value=1.0 if synapse.available else 0.0,
                    metric_type=MetricType.GAUGE,
                    help_text="Synapse availability",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_synapse_surprise_avg",
                    value=synapse.surprise_avg,
                    metric_type=MetricType.GAUGE,
                    help_text="Average surprise across signal types",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_synapse_flashbulb_rate",
                    value=synapse.flashbulb_rate,
                    metric_type=MetricType.GAUGE,
                    help_text="Rate of flashbulb (high-surprise) signals",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_synapse_signals_total",
                    value=float(synapse.signals_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total signals processed by synapse",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_synapse_batch_pending",
                    value=float(synapse.batch_pending),
                    metric_type=MetricType.GAUGE,
                    help_text="Signals pending in batch queue",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        # Hippocampus metrics
        hippo = health.hippocampus
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_hippocampus_available",
                    value=1.0 if hippo.available else 0.0,
                    metric_type=MetricType.GAUGE,
                    help_text="Hippocampus availability",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_hippocampus_size",
                    value=float(hippo.memory_count),
                    metric_type=MetricType.GAUGE,
                    help_text="Current short-term memory size",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_hippocampus_utilization",
                    value=hippo.utilization,
                    metric_type=MetricType.GAUGE,
                    help_text="Hippocampus utilization (0-1)",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_hippocampus_flush_total",
                    value=float(hippo.flushes_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total hippocampus flushes",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        # Dreamer metrics
        dreamer = health.dreamer
        metrics.extend(
            [
                Metric(
                    name=f"{prefix}_dream_cycles_total",
                    value=float(dreamer.dream_cycles_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total REM cycles completed",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_dream_interrupted_total",
                    value=float(dreamer.interrupted_total),
                    metric_type=MetricType.COUNTER,
                    help_text="Total interrupted dreams",
                    labels=labels,
                    timestamp=now,
                ),
                Metric(
                    name=f"{prefix}_morning_briefing_count",
                    value=float(dreamer.morning_briefing_count),
                    metric_type=MetricType.GAUGE,
                    help_text="Questions in morning briefing",
                    labels=labels,
                    timestamp=now,
                ),
            ]
        )

        return metrics

    def _health_to_value(self, health_str: str) -> float:
        """Convert health string to numeric value."""
        mapping = {
            "unknown": 0.0,
            "critical": 1.0,
            "degraded": 2.0,
            "healthy": 3.0,
        }
        return mapping.get(health_str, 0.0)

    @abstractmethod
    def export(self) -> str:
        """Export metrics to string format."""
        ...

    @abstractmethod
    async def serve(self, port: int | None = None, path: str | None = None) -> None:
        """Start serving metrics endpoint."""
        ...


class PrometheusExporter(MetricsExporter):
    """
    Export metrics in Prometheus exposition format.

    Produces text/plain output suitable for Prometheus scraping.

    Usage:
        exporter = PrometheusExporter(observer)
        metrics_text = exporter.export()
        # → Prometheus-format metrics text

        await exporter.serve(port=9090, path="/metrics")
    """

    def export(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Prometheus exposition format text
        """
        metrics = self.collect_metrics()
        lines = []

        for metric in metrics:
            # Add HELP and TYPE lines
            if metric.help_text:
                lines.append(f"# HELP {metric.name} {metric.help_text}")
            lines.append(f"# TYPE {metric.name} {metric.metric_type.value}")

            # Format labels
            label_str = ""
            if metric.labels:
                label_parts = [f'{k}="{v}"' for k, v in metric.labels.items()]
                label_str = "{" + ",".join(label_parts) + "}"

            # Format value line
            value_str = f"{metric.name}{label_str} {metric.value}"
            if metric.timestamp:
                value_str += f" {int(metric.timestamp * 1000)}"

            lines.append(value_str)
            lines.append("")  # Blank line between metrics

        return "\n".join(lines)

    async def serve(self, port: int | None = None, path: str | None = None) -> None:
        """
        Start serving Prometheus metrics endpoint.

        Note: This is a simple implementation. In production, use a proper
        HTTP server like aiohttp or FastAPI.

        Args:
            port: Port to serve on (default from config)
            path: Path for metrics endpoint (default from config)
        """
        port = port or self._config.prometheus_port
        path = path or self._config.prometheus_path

        # Simple asyncio HTTP server for metrics
        # In production, integrate with your web framework
        async def handle_request(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            try:
                request = await reader.read(4096)
                request_line = request.decode().split("\r\n")[0]

                # Check if request is for metrics path
                if f"GET {path}" in request_line:
                    content = self.export()
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain; version=0.0.4\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        "\r\n"
                        f"{content}"
                    )
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

                writer.write(response.encode())
                await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_server(handle_request, "0.0.0.0", port)

        async with server:
            await server.serve_forever()


class OpenTelemetryExporter(MetricsExporter):
    """
    Export metrics via OpenTelemetry Protocol (OTLP).

    Pushes metrics to an OTLP endpoint for distributed observability.

    Note: This is a simplified implementation. For production use,
    consider the official opentelemetry-python SDK.

    Usage:
        exporter = OpenTelemetryExporter(
            observer=cortex_observer,
            config=MetricsExportConfig(
                otel_endpoint="http://localhost:4317",
                otel_service_name="kgents-cortex",
            ),
        )
        await exporter.start()
    """

    def __init__(
        self,
        observer: CortexObserver,
        config: MetricsExportConfig | None = None,
    ):
        super().__init__(observer, config)
        self._running = False
        self._export_task: asyncio.Task[None] | None = None

    def export(self) -> str:
        """
        Export metrics as JSON (for OTLP-compatible format).

        Returns:
            JSON string of metrics
        """
        metrics = self.collect_metrics()

        # Convert to OTLP-like structure
        resource = {
            "service.name": self._config.otel_service_name,
        }

        metric_data = []
        for metric in metrics:
            data_point = {
                "asDouble": metric.value,
                "timeUnixNano": (
                    int(metric.timestamp * 1e9) if metric.timestamp else None
                ),
                "attributes": [
                    {"key": k, "value": {"stringValue": v}}
                    for k, v in metric.labels.items()
                ],
            }

            metric_data.append(
                {
                    "name": metric.name,
                    "description": metric.help_text,
                    "unit": "",
                    "gauge": {"dataPoints": [data_point]},
                }
            )

        payload = {
            "resourceMetrics": [
                {
                    "resource": {"attributes": resource},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "cortex-observer"},
                            "metrics": metric_data,
                        }
                    ],
                }
            ]
        }

        return json.dumps(payload, indent=2)

    async def _export_loop(self) -> None:
        """Background loop that exports metrics periodically."""
        while self._running:
            try:
                await self._push_metrics()
            except Exception:
                pass  # Log error in production

            await asyncio.sleep(self._config.export_interval_seconds)

    async def _push_metrics(self) -> None:
        """Push metrics to OTLP endpoint."""
        if not self._config.otel_endpoint:
            return

        # Note: In production, use proper HTTP client with error handling
        # This is a placeholder for the integration point
        _payload = self.export()  # noqa: F841 - placeholder for future HTTP push
        # Would send to: POST {otel_endpoint}/v1/metrics
        # with Content-Type: application/json

    async def start(self) -> None:
        """Start automatic metric export."""
        if self._running:
            return

        self._running = True
        self._export_task = asyncio.create_task(self._export_loop())

    async def stop(self) -> None:
        """Stop automatic metric export."""
        self._running = False
        if self._export_task:
            self._export_task.cancel()
            try:
                await self._export_task
            except asyncio.CancelledError:
                pass
            self._export_task = None

    async def serve(self, port: int | None = None, path: str | None = None) -> None:
        """Start OTLP export (push-based, not serve-based)."""
        await self.start()
        # Keep running
        while self._running:
            await asyncio.sleep(1)


class JSONExporter(MetricsExporter):
    """
    Export metrics as JSON for custom integrations.

    Usage:
        exporter = JSONExporter(observer)
        json_str = exporter.export()
    """

    def export(self) -> str:
        """
        Export metrics as JSON.

        Returns:
            JSON string of metrics
        """
        metrics = self.collect_metrics()

        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "type": m.metric_type.value,
                    "help": m.help_text,
                    "labels": m.labels,
                }
                for m in metrics
            ],
        }

        return json.dumps(data, indent=2)

    async def serve(self, port: int | None = None, path: str | None = None) -> None:
        """Serve JSON metrics endpoint."""
        port = port or self._config.prometheus_port
        path = path or "/metrics.json"

        async def handle_request(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            try:
                request = await reader.read(4096)
                request_line = request.decode().split("\r\n")[0]

                if f"GET {path}" in request_line:
                    content = self.export()
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        "\r\n"
                        f"{content}"
                    )
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

                writer.write(response.encode())
                await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_server(handle_request, "0.0.0.0", port)

        async with server:
            await server.serve_forever()


# === Factory Functions ===


def create_metrics_exporter(
    observer: CortexObserver,
    format: str = "prometheus",
    config_dict: dict[str, Any] | None = None,
) -> MetricsExporter:
    """
    Create a metrics exporter.

    Args:
        observer: CortexObserver to export from
        format: Export format ("prometheus", "opentelemetry", "json")
        config_dict: Configuration dictionary

    Returns:
        Configured MetricsExporter
    """
    config = (
        MetricsExportConfig.from_dict(config_dict)
        if config_dict
        else MetricsExportConfig()
    )

    exporters: dict[
        str, type[PrometheusExporter] | type[OpenTelemetryExporter] | type[JSONExporter]
    ] = {
        "prometheus": PrometheusExporter,
        "opentelemetry": OpenTelemetryExporter,
        "otel": OpenTelemetryExporter,
        "json": JSONExporter,
    }

    exporter_cls = exporters.get(format.lower(), PrometheusExporter)
    return exporter_cls(observer=observer, config=config)


def create_otel_exporter(
    observer: CortexObserver,
    service_name: str = "kgents-cortex",
    endpoint: str | None = None,
) -> OpenTelemetryExporter:
    """
    Create an OpenTelemetry exporter.

    Args:
        observer: CortexObserver to export from
        service_name: OTLP service name
        endpoint: OTLP endpoint URL

    Returns:
        Configured OpenTelemetryExporter
    """
    config = MetricsExportConfig(
        otel_service_name=service_name,
        otel_endpoint=endpoint,
    )
    return OpenTelemetryExporter(observer=observer, config=config)
