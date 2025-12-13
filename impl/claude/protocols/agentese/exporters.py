"""
AGENTESE Exporters: OpenTelemetry Exporter Configuration.

Configures and manages OpenTelemetry exporters for traces and metrics,
supporting multiple backends:
- OTLP (gRPC/HTTP) for Tempo, Jaeger, or any OTLP-compatible collector
- Jaeger native protocol
- Local JSON files for development
- Console output for debugging

Usage:
    from protocols.agentese.exporters import configure_telemetry, TelemetryConfig

    # Production: Export to OTLP collector
    configure_telemetry(TelemetryConfig(
        otlp_endpoint="http://tempo:4317",
        service_name="kgents-production",
    ))

    # Development: Export to local JSON files
    configure_telemetry(TelemetryConfig(
        local_json_path="~/.kgents/traces/",
        console_export=True,
    ))
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricExporter,
    MetricExportResult,
    MetricsData,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
    SpanExportResult,
)

# === Configuration ===


@dataclass
class TelemetryConfig:
    """
    Configuration for OpenTelemetry exporters.

    Supports multiple export targets simultaneously.
    At least one export method should be configured.
    """

    # Service identification
    service_name: str = "kgents"
    service_version: str = "0.1.0"
    deployment_environment: str = "development"

    # OTLP export (Tempo, Jaeger, generic collectors)
    otlp_endpoint: str | None = None
    otlp_insecure: bool = True  # Use insecure channel for local dev
    otlp_headers: dict[str, str] = field(default_factory=dict)

    # Jaeger native export
    jaeger_host: str | None = None
    jaeger_port: int = 6831

    # Local JSON export (development)
    local_json_path: str | None = None

    # Console export (debugging)
    console_export: bool = False

    # Sampling
    sampling_rate: float = 1.0  # 1.0 = sample all, 0.1 = 10%

    # Metrics
    metrics_export_interval_ms: int = 15000

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        """Create config from environment variables."""
        return cls(
            service_name=os.getenv("KGENTS_SERVICE_NAME", "kgents"),
            service_version=os.getenv("KGENTS_SERVICE_VERSION", "0.1.0"),
            deployment_environment=os.getenv("KGENTS_ENVIRONMENT", "development"),
            otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            otlp_insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower()
            == "true",
            jaeger_host=os.getenv("JAEGER_AGENT_HOST"),
            jaeger_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
            local_json_path=os.getenv("KGENTS_TRACE_JSON_PATH"),
            console_export=os.getenv("KGENTS_TRACE_CONSOLE", "false").lower() == "true",
            sampling_rate=float(os.getenv("OTEL_TRACES_SAMPLER_ARG", "1.0")),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TelemetryConfig":
        """Load config from YAML file."""
        import yaml

        config_path = Path(path).expanduser()
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        traces = data.get("traces", {})
        metrics_conf = data.get("metrics", {})
        sampling = data.get("sampling", {})

        return cls(
            service_name=data.get("service_name", "kgents"),
            service_version=data.get("service_version", "0.1.0"),
            deployment_environment=data.get("environment", "development"),
            otlp_endpoint=traces.get("otlp_endpoint"),
            otlp_insecure=traces.get("otlp_insecure", True),
            jaeger_host=traces.get("jaeger_host"),
            jaeger_port=traces.get("jaeger_port", 6831),
            local_json_path=traces.get("json_path"),
            console_export=traces.get("console", False),
            sampling_rate=sampling.get("rate", 1.0),
            metrics_export_interval_ms=metrics_conf.get("export_interval_ms", 15000),
        )


# === JSON File Exporter ===


class JsonFileSpanExporter(SpanExporter):
    """
    Export spans to JSON files for local development.

    Each trace gets its own file with all spans included.
    Files are named by trace ID and timestamp.
    """

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to JSON files."""
        if not spans:
            return SpanExportResult.SUCCESS

        # Group by trace ID
        traces: dict[str, list[dict[str, Any]]] = {}
        for span in spans:
            ctx = span.get_span_context()  # type: ignore[no-untyped-call]
            trace_id = format(ctx.trace_id, "032x")

            if trace_id not in traces:
                traces[trace_id] = []

            traces[trace_id].append(self._span_to_dict(span))

        # Write each trace to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for trace_id, span_list in traces.items():
            filename = f"{timestamp}_{trace_id[:8]}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w") as f:
                json.dump(
                    {
                        "trace_id": trace_id,
                        "timestamp": datetime.now().isoformat(),
                        "spans": span_list,
                    },
                    f,
                    indent=2,
                    default=str,
                )

        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """No cleanup needed."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Immediate write, always succeeds."""
        return True

    def _span_to_dict(self, span: ReadableSpan) -> dict[str, Any]:
        """Convert span to JSON-serializable dict."""
        ctx = span.get_span_context()  # type: ignore[no-untyped-call]
        parent = span.parent

        return {
            "name": span.name,
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
            "parent_span_id": format(parent.span_id, "016x") if parent else None,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "duration_ns": (span.end_time or 0) - (span.start_time or 0),
            "attributes": dict(span.attributes) if span.attributes else {},
            "status": {
                "code": span.status.status_code.name,
                "description": span.status.description,
            },
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes) if event.attributes else {},
                }
                for event in span.events
            ],
        }


class JsonFileMetricExporter(MetricExporter):
    """
    Export metrics to JSON files for local development.
    """

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        metrics_data: MetricsData,
        timeout_millis: float = 10000,
        **kwargs: Any,
    ) -> MetricExportResult:
        """Export metrics to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"metrics_{timestamp}.json"
        filepath = self.output_dir / filename

        data: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "resource_metrics": [],
        }

        for resource_metrics in metrics_data.resource_metrics:
            rm_data: dict[str, Any] = {
                "resource": dict(resource_metrics.resource.attributes),
                "scope_metrics": [],
            }

            for scope_metrics in resource_metrics.scope_metrics:
                sm_data: dict[str, Any] = {
                    "scope": scope_metrics.scope.name,
                    "metrics": [],
                }

                for metric in scope_metrics.metrics:
                    sm_data["metrics"].append(
                        {
                            "name": metric.name,
                            "description": metric.description,
                            "unit": metric.unit,
                            "data": str(metric.data),
                        }
                    )

                rm_data["scope_metrics"].append(sm_data)

            data["resource_metrics"].append(rm_data)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis: float = 30000, **kwargs: Any) -> None:
        """No cleanup needed."""
        pass

    def force_flush(self, timeout_millis: float = 10000) -> bool:
        """Immediate write, always succeeds."""
        return True


# === Configuration Function ===

_configured = False


def configure_telemetry(config: TelemetryConfig | None = None) -> None:
    """
    Configure OpenTelemetry with the specified exporters.

    This should be called once at application startup.
    Subsequent calls will be ignored.

    Args:
        config: Telemetry configuration. If None, loads from environment.
    """
    global _configured
    if _configured:
        return

    if config is None:
        config = TelemetryConfig.from_env()

    # Create resource
    resource = Resource.create(
        {
            SERVICE_NAME: config.service_name,
            SERVICE_VERSION: config.service_version,
            "deployment.environment": config.deployment_environment,
        }
    )

    # Configure trace provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    if config.otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            otlp_exporter = OTLPSpanExporter(
                endpoint=config.otlp_endpoint,
                insecure=config.otlp_insecure,
                headers=config.otlp_headers or None,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except ImportError:
            # Fall back to HTTP if gRPC not available
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter as OTLPHttpExporter,
            )

            otlp_exporter = OTLPHttpExporter(  # type: ignore[assignment]
                endpoint=f"{config.otlp_endpoint}/v1/traces",
                headers=config.otlp_headers or None,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Add Jaeger exporter (if configured)
    if config.jaeger_host:
        try:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter

            jaeger_exporter = JaegerExporter(
                agent_host_name=config.jaeger_host,
                agent_port=config.jaeger_port,
            )
            provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        except ImportError:
            pass  # Jaeger exporter not installed

    # Add JSON file exporter
    if config.local_json_path:
        json_exporter = JsonFileSpanExporter(config.local_json_path)
        provider.add_span_processor(BatchSpanProcessor(json_exporter))

    # Add console exporter
    if config.console_export:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Set as global provider
    trace.set_tracer_provider(provider)

    # Configure metrics provider
    _configure_metrics(config, resource)

    _configured = True


def _configure_metrics(config: TelemetryConfig, resource: Resource) -> None:
    """Configure OpenTelemetry metrics provider."""
    readers = []

    # OTLP metrics exporter
    if config.otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )

            otlp_metric_exporter = OTLPMetricExporter(
                endpoint=config.otlp_endpoint,
                insecure=config.otlp_insecure,
            )
            readers.append(
                PeriodicExportingMetricReader(
                    otlp_metric_exporter,
                    export_interval_millis=config.metrics_export_interval_ms,
                )
            )
        except ImportError:
            pass

    # JSON file metrics exporter
    if config.local_json_path:
        json_metric_exporter = JsonFileMetricExporter(config.local_json_path)
        readers.append(
            PeriodicExportingMetricReader(
                json_metric_exporter,
                export_interval_millis=config.metrics_export_interval_ms,
            )
        )

    # Console metrics exporter
    if config.console_export:
        readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=config.metrics_export_interval_ms,
            )
        )

    if readers:
        meter_provider = MeterProvider(resource=resource, metric_readers=readers)
        metrics.set_meter_provider(meter_provider)


def shutdown_telemetry() -> None:
    """
    Shutdown OpenTelemetry providers, flushing any pending data.

    Call this before application exit to ensure all traces are exported.
    """
    # Flush trace provider
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()
    if hasattr(provider, "shutdown"):
        provider.shutdown()

    # Flush metrics provider
    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, "force_flush"):
        meter_provider.force_flush()
    if hasattr(meter_provider, "shutdown"):
        meter_provider.shutdown()


def is_telemetry_configured() -> bool:
    """Check if telemetry has been configured."""
    return _configured


# === Convenience Functions ===


def configure_for_development(trace_dir: str = "~/.kgents/traces/") -> None:
    """
    Configure telemetry for local development.

    Enables JSON file export and console output.

    Args:
        trace_dir: Directory for JSON trace files
    """
    configure_telemetry(
        TelemetryConfig(
            local_json_path=trace_dir,
            console_export=True,
            deployment_environment="development",
        )
    )


def configure_for_production(
    otlp_endpoint: str,
    service_name: str = "kgents",
    sampling_rate: float = 0.1,
) -> None:
    """
    Configure telemetry for production.

    Enables OTLP export with sampling.

    Args:
        otlp_endpoint: OTLP collector endpoint (e.g., "tempo:4317")
        service_name: Service name for traces
        sampling_rate: Fraction of traces to sample (0.1 = 10%)
    """
    configure_telemetry(
        TelemetryConfig(
            otlp_endpoint=otlp_endpoint,
            service_name=service_name,
            sampling_rate=sampling_rate,
            deployment_environment="production",
        )
    )
