"""
Tests for AGENTESE Exporters - OpenTelemetry exporter configuration.

These tests verify:
- TelemetryConfig creation and loading
- JsonFileSpanExporter functionality
- Configuration from environment variables
- Configuration from YAML files
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ..exporters import (
    JsonFileMetricExporter,
    JsonFileSpanExporter,
    TelemetryConfig,
    configure_telemetry,
    is_telemetry_configured,
)

# === Test TelemetryConfig ===


class TestTelemetryConfig:
    """Tests for TelemetryConfig dataclass."""

    def test_default_values(self) -> None:
        """Creates config with sensible defaults."""
        config = TelemetryConfig()

        assert config.service_name == "kgents"
        assert config.service_version == "0.1.0"
        assert config.deployment_environment == "development"
        assert config.sampling_rate == 1.0
        assert config.otlp_endpoint is None
        assert config.console_export is False

    def test_custom_values(self) -> None:
        """Creates config with custom values."""
        config = TelemetryConfig(
            service_name="my-service",
            otlp_endpoint="tempo:4317",
            sampling_rate=0.5,
        )

        assert config.service_name == "my-service"
        assert config.otlp_endpoint == "tempo:4317"
        assert config.sampling_rate == 0.5

    def test_from_env_defaults(self) -> None:
        """Creates config from environment with defaults."""
        with patch.dict("os.environ", {}, clear=True):
            config = TelemetryConfig.from_env()

        assert config.service_name == "kgents"
        assert config.otlp_endpoint is None

    def test_from_env_with_values(self) -> None:
        """Creates config from environment variables."""
        env = {
            "KGENTS_SERVICE_NAME": "test-service",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "tempo:4317",
            "OTEL_EXPORTER_OTLP_INSECURE": "true",
            "KGENTS_TRACE_CONSOLE": "true",
            "OTEL_TRACES_SAMPLER_ARG": "0.1",
        }

        with patch.dict("os.environ", env, clear=True):
            config = TelemetryConfig.from_env()

        assert config.service_name == "test-service"
        assert config.otlp_endpoint == "tempo:4317"
        assert config.otlp_insecure is True
        assert config.console_export is True
        assert config.sampling_rate == 0.1

    def test_from_yaml(self) -> None:
        """Loads config from YAML file."""
        yaml_content = """
service_name: yaml-service
service_version: "1.0.0"
environment: production

traces:
  otlp_endpoint: "jaeger:4317"
  console: true

sampling:
  rate: 0.5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            config = TelemetryConfig.from_yaml(yaml_path)

            assert config.service_name == "yaml-service"
            assert config.service_version == "1.0.0"
            assert config.deployment_environment == "production"
            assert config.otlp_endpoint == "jaeger:4317"
            assert config.console_export is True
            assert config.sampling_rate == 0.5
        finally:
            Path(yaml_path).unlink()

    def test_from_yaml_missing_file(self) -> None:
        """Returns defaults when YAML file doesn't exist."""
        config = TelemetryConfig.from_yaml("/nonexistent/path.yaml")

        assert config.service_name == "kgents"
        assert config.otlp_endpoint is None


# === Test JsonFileSpanExporter ===


class TestJsonFileSpanExporter:
    """Tests for JsonFileSpanExporter."""

    def test_creates_output_directory(self) -> None:
        """Creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "traces" / "nested"
            exporter = JsonFileSpanExporter(output_dir)

            assert output_dir.exists()
            assert output_dir.is_dir()

    def test_exports_spans_to_json(self) -> None:
        """Exports spans to JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            exporter = JsonFileSpanExporter(output_dir)

            # Create mock spans
            mock_span = MagicMock()
            mock_ctx = MagicMock()
            mock_ctx.trace_id = 0x12345678901234567890123456789012
            mock_ctx.span_id = 0x1234567890123456
            mock_span.get_span_context.return_value = mock_ctx
            mock_span.name = "test.span"
            mock_span.parent = None
            mock_span.start_time = 1000000000
            mock_span.end_time = 2000000000
            mock_span.attributes = {"test.attr": "value"}
            mock_span.status = MagicMock()
            mock_span.status.status_code.name = "OK"
            mock_span.status.description = None
            mock_span.events = []

            # Export
            from opentelemetry.sdk.trace.export import SpanExportResult

            result = exporter.export([mock_span])

            assert result == SpanExportResult.SUCCESS

            # Check file was created
            json_files = list(output_dir.glob("*.json"))
            assert len(json_files) == 1

            # Check content
            data = json.loads(json_files[0].read_text())
            assert "trace_id" in data
            assert "spans" in data
            assert len(data["spans"]) == 1
            assert data["spans"][0]["name"] == "test.span"

    def test_exports_empty_spans(self) -> None:
        """Handles empty span list gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JsonFileSpanExporter(tmpdir)

            from opentelemetry.sdk.trace.export import SpanExportResult

            result = exporter.export([])

            assert result == SpanExportResult.SUCCESS

    def test_force_flush_succeeds(self) -> None:
        """Force flush always succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JsonFileSpanExporter(tmpdir)

            assert exporter.force_flush() is True

    def test_shutdown_succeeds(self) -> None:
        """Shutdown is a no-op."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JsonFileSpanExporter(tmpdir)

            # Should not raise
            exporter.shutdown()


# === Test JsonFileMetricExporter ===


class TestJsonFileMetricExporter:
    """Tests for JsonFileMetricExporter."""

    def test_creates_output_directory(self) -> None:
        """Creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "metrics"
            exporter = JsonFileMetricExporter(output_dir)

            assert output_dir.exists()


# === Test Configuration Functions ===


class TestConfigureTelemetry:
    """Tests for configure_telemetry function."""

    @pytest.fixture(autouse=True)
    def reset_state(self) -> Any:
        """Reset _configured state before and after each test."""
        import protocols.agentese.exporters as exp_module

        original = exp_module._configured
        exp_module._configured = False
        yield
        exp_module._configured = original

    def test_configure_with_json_export(self) -> None:
        """Configures telemetry with JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TelemetryConfig(local_json_path=tmpdir)

            # Should not raise
            configure_telemetry(config)

            assert is_telemetry_configured()

    def test_skips_if_already_configured(self) -> None:
        """Skips configuration if already configured."""
        import protocols.agentese.exporters as exp_module

        # Force configured state
        exp_module._configured = True

        # Should not raise or reconfigure
        configure_telemetry(TelemetryConfig())

        # Still configured
        assert is_telemetry_configured()


class TestIsTelemetryConfigured:
    """Tests for is_telemetry_configured function."""

    def test_returns_true_when_configured(self) -> None:
        """Returns true when _configured is True."""
        import protocols.agentese.exporters as exp_module

        # Ensure it's True (configure_telemetry was called in earlier tests)
        exp_module._configured = True
        assert is_telemetry_configured() is True

    def test_function_reads_module_variable(self) -> None:
        """Verify is_telemetry_configured() reads the _configured variable."""
        import protocols.agentese.exporters as exp_module

        # The function should return the value of _configured
        # Since configure_telemetry has been called in the test session,
        # _configured should be True
        result = is_telemetry_configured()
        assert result == exp_module._configured
