"""
Tests for MetricsExporter (Instance DB Phase 6).

Tests Prometheus, OpenTelemetry, and JSON metric export.
"""

import json
from unittest.mock import MagicMock

import pytest

from agents.o.cortex_observer import (
    CortexObserver,
    create_mock_cortex_observer,
)
from agents.o.metrics_export import (
    JSONExporter,
    Metric,
    MetricsExportConfig,
    MetricType,
    OpenTelemetryExporter,
    PrometheusExporter,
    create_metrics_exporter,
    create_otel_exporter,
)


class TestMetric:
    """Tests for Metric dataclass."""

    def test_create_metric(self) -> None:
        """Test creating a metric."""
        metric = Metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
            help_text="A test metric",
            labels={"env": "test"},
        )

        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.metric_type == MetricType.GAUGE


class TestMetricsExportConfig:
    """Tests for MetricsExportConfig."""

    def test_defaults(self) -> None:
        """Test default configuration."""
        config = MetricsExportConfig()

        assert config.prefix == "cortex"
        assert config.prometheus_port == 9090
        assert config.prometheus_path == "/metrics"

    def test_from_dict(self) -> None:
        """Test creating config from dict."""
        config = MetricsExportConfig.from_dict(
            {
                "prefix": "kgents",
                "port": 8080,
                "otel_endpoint": "http://localhost:4317",
            }
        )

        assert config.prefix == "kgents"
        assert config.prometheus_port == 8080
        assert config.otel_endpoint == "http://localhost:4317"


class TestPrometheusExporter:
    """Tests for PrometheusExporter."""

    def test_collect_metrics(self) -> None:
        """Test collecting metrics from observer."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        metrics = exporter.collect_metrics()

        assert len(metrics) > 0
        assert all(isinstance(m, Metric) for m in metrics)

    def test_export_prometheus_format(self) -> None:
        """Test Prometheus text format export."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        output = exporter.export()

        # Check Prometheus format elements
        assert "# HELP" in output
        assert "# TYPE" in output
        assert "cortex_health" in output

    def test_metric_names_have_prefix(self) -> None:
        """Test all metrics have configured prefix."""
        observer = create_mock_cortex_observer()
        config = MetricsExportConfig(prefix="test")
        exporter = PrometheusExporter(observer, config)

        metrics = exporter.collect_metrics()

        for metric in metrics:
            assert metric.name.startswith("test_")

    def test_labels_in_output(self) -> None:
        """Test labels are included in output."""
        observer = create_mock_cortex_observer()
        config = MetricsExportConfig(default_labels={"env": "test"})
        exporter = PrometheusExporter(observer, config)

        output = exporter.export()

        assert 'env="test"' in output

    def test_health_metric(self) -> None:
        """Test health metric is present."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        metrics = exporter.collect_metrics()
        health_metric = next((m for m in metrics if m.name == "cortex_health"), None)

        assert health_metric is not None
        assert health_metric.metric_type == MetricType.GAUGE

    def test_coherency_metrics(self) -> None:
        """Test coherency metrics are present."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        metrics = exporter.collect_metrics()
        metric_names = [m.name for m in metrics]

        assert "cortex_coherency_rate" in metric_names
        assert "cortex_ghost_count" in metric_names
        assert "cortex_ghost_healed_total" in metric_names

    def test_synapse_metrics(self) -> None:
        """Test synapse metrics are present."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        metrics = exporter.collect_metrics()
        metric_names = [m.name for m in metrics]

        assert "cortex_synapse_surprise_avg" in metric_names
        assert "cortex_synapse_flashbulb_rate" in metric_names

    def test_dream_metrics(self) -> None:
        """Test dream metrics are present."""
        observer = create_mock_cortex_observer()
        exporter = PrometheusExporter(observer)

        metrics = exporter.collect_metrics()
        metric_names = [m.name for m in metrics]

        assert "cortex_dream_cycles_total" in metric_names


class TestOpenTelemetryExporter:
    """Tests for OpenTelemetryExporter."""

    def test_export_json_format(self) -> None:
        """Test OTLP JSON format export."""
        observer = create_mock_cortex_observer()
        exporter = OpenTelemetryExporter(observer)

        output = exporter.export()
        data = json.loads(output)

        assert "resourceMetrics" in data
        assert len(data["resourceMetrics"]) > 0

    def test_service_name_in_resource(self) -> None:
        """Test service name is included."""
        observer = create_mock_cortex_observer()
        config = MetricsExportConfig(otel_service_name="test-service")
        exporter = OpenTelemetryExporter(observer, config)

        output = exporter.export()
        data = json.loads(output)

        resource = data["resourceMetrics"][0]["resource"]
        # Resource is stored as attributes dict
        assert resource["attributes"]["service.name"] == "test-service"

    def test_metrics_have_data_points(self) -> None:
        """Test metrics have data points."""
        observer = create_mock_cortex_observer()
        exporter = OpenTelemetryExporter(observer)

        output = exporter.export()
        data = json.loads(output)

        metrics = data["resourceMetrics"][0]["scopeMetrics"][0]["metrics"]
        assert len(metrics) > 0

        # Check structure
        for metric in metrics:
            assert "name" in metric
            assert "gauge" in metric
            assert "dataPoints" in metric["gauge"]


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_export_json(self) -> None:
        """Test JSON format export."""
        observer = create_mock_cortex_observer()
        exporter = JSONExporter(observer)

        output = exporter.export()
        data = json.loads(output)

        assert "timestamp" in data
        assert "metrics" in data

    def test_metrics_array(self) -> None:
        """Test metrics array format."""
        observer = create_mock_cortex_observer()
        exporter = JSONExporter(observer)

        output = exporter.export()
        data = json.loads(output)

        metrics = data["metrics"]
        assert isinstance(metrics, list)
        assert len(metrics) > 0

        for metric in metrics:
            assert "name" in metric
            assert "value" in metric
            assert "type" in metric


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_prometheus_exporter(self) -> None:
        """Test creating Prometheus exporter."""
        observer = create_mock_cortex_observer()
        exporter = create_metrics_exporter(observer, format="prometheus")

        assert isinstance(exporter, PrometheusExporter)

    def test_create_otel_exporter(self) -> None:
        """Test creating OpenTelemetry exporter."""
        observer = create_mock_cortex_observer()
        exporter = create_metrics_exporter(observer, format="opentelemetry")

        assert isinstance(exporter, OpenTelemetryExporter)

    def test_create_json_exporter(self) -> None:
        """Test creating JSON exporter."""
        observer = create_mock_cortex_observer()
        exporter = create_metrics_exporter(observer, format="json")

        assert isinstance(exporter, JSONExporter)

    def test_create_otel_exporter_factory(self) -> None:
        """Test dedicated OTEL factory."""
        observer = create_mock_cortex_observer()
        exporter = create_otel_exporter(
            observer,
            service_name="my-service",
            endpoint="http://localhost:4317",
        )

        assert isinstance(exporter, OpenTelemetryExporter)
        assert exporter._config.otel_service_name == "my-service"

    def test_default_format_is_prometheus(self) -> None:
        """Test default format is Prometheus."""
        observer = create_mock_cortex_observer()
        exporter = create_metrics_exporter(observer)

        assert isinstance(exporter, PrometheusExporter)
