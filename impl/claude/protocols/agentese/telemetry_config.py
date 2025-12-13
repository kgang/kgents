"""
Telemetry Configuration Loader.

Loads telemetry configuration from ~/.kgents/telemetry.yaml or environment variables.
Provides a simple interface for configuring OpenTelemetry exporters.

Configuration file format (~/.kgents/telemetry.yaml):
    enabled: true

    traces:
      exporter: otlp  # otlp | jaeger | json | none
      otlp_endpoint: "localhost:4317"
      jaeger_host: "localhost"
      jaeger_port: 6831
      json_path: "~/.kgents/traces/"

    metrics:
      exporter: prometheus  # prometheus | otlp | none
      prometheus_port: 9090

    sampling:
      rate: 1.0  # Sample all traces (development)

Environment variables:
    KGENTS_TELEMETRY_ENABLED=true
    OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
    KGENTS_TRACE_JSON_PATH=~/.kgents/traces/
    KGENTS_TRACE_CONSOLE=true
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exporters import TelemetryConfig, configure_telemetry

# === Configuration Paths ===

DEFAULT_CONFIG_PATH = Path("~/.kgents/telemetry.yaml").expanduser()
DEFAULT_TRACE_PATH = Path("~/.kgents/traces/").expanduser()


# === Loader Functions ===


def load_telemetry_config(
    config_path: str | Path | None = None,
) -> TelemetryConfig:
    """
    Load telemetry configuration from file or environment.

    Priority:
    1. Explicit config_path argument
    2. KGENTS_TELEMETRY_CONFIG environment variable
    3. ~/.kgents/telemetry.yaml
    4. Environment variables (OTEL_*, KGENTS_*)
    5. Defaults

    Args:
        config_path: Optional explicit path to config file

    Returns:
        TelemetryConfig loaded from available sources
    """
    # Determine config file path
    if config_path:
        path = Path(config_path).expanduser()
    elif "KGENTS_TELEMETRY_CONFIG" in os.environ:
        path = Path(os.environ["KGENTS_TELEMETRY_CONFIG"]).expanduser()
    else:
        path = DEFAULT_CONFIG_PATH

    # Try loading from file
    if path.exists():
        return TelemetryConfig.from_yaml(path)

    # Fall back to environment
    return TelemetryConfig.from_env()


def setup_telemetry(
    config_path: str | Path | None = None,
    force: bool = False,
) -> bool:
    """
    Load configuration and set up OpenTelemetry.

    This is the main entry point for configuring telemetry.
    Call once at application startup.

    Args:
        config_path: Optional explicit path to config file
        force: If True, reconfigure even if already configured

    Returns:
        True if telemetry was configured, False if skipped

    Example:
        # In application startup
        from protocols.agentese.telemetry_config import setup_telemetry

        if setup_telemetry():
            print("Telemetry configured")
    """
    from .exporters import is_telemetry_configured

    # Check if already configured
    if is_telemetry_configured() and not force:
        return False

    # Load config
    config = load_telemetry_config(config_path)

    # Check if telemetry is explicitly disabled
    if not _is_telemetry_enabled():
        return False

    # Configure
    configure_telemetry(config)
    return True


def _is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled via environment."""
    env_value = os.environ.get("KGENTS_TELEMETRY_ENABLED", "").lower()
    if env_value in ("0", "false", "no", "off"):
        return False

    # If OTEL endpoint is set, assume telemetry is wanted
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return True

    # If local JSON path is set, assume telemetry is wanted
    if os.environ.get("KGENTS_TRACE_JSON_PATH"):
        return True

    # Default to enabled if any config exists
    return DEFAULT_CONFIG_PATH.exists()


# === Quick Setup Functions ===


def setup_development_telemetry(
    trace_dir: str | Path | None = None,
    console: bool = True,
) -> None:
    """
    Quick setup for development - JSON files + optional console output.

    Args:
        trace_dir: Directory for trace JSON files (default ~/.kgents/traces/)
        console: Also output to console (default True)

    Example:
        from protocols.agentese.telemetry_config import setup_development_telemetry

        setup_development_telemetry()
        # Now traces go to ~/.kgents/traces/ and console
    """
    from .exporters import configure_for_development

    trace_path = str(trace_dir) if trace_dir else str(DEFAULT_TRACE_PATH)
    configure_for_development(trace_path)


def setup_production_telemetry(
    otlp_endpoint: str | None = None,
    service_name: str = "kgents",
    sampling_rate: float = 0.1,
) -> None:
    """
    Quick setup for production - OTLP export with sampling.

    Args:
        otlp_endpoint: OTLP collector endpoint (default from env)
        service_name: Service name for traces
        sampling_rate: Fraction of traces to sample (default 10%)

    Example:
        from protocols.agentese.telemetry_config import setup_production_telemetry

        setup_production_telemetry(
            otlp_endpoint="tempo.monitoring:4317",
            service_name="kgents-production",
        )
    """
    from .exporters import configure_for_production

    endpoint = otlp_endpoint or os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"
    )
    configure_for_production(endpoint, service_name, sampling_rate)


# === Configuration Generator ===


def generate_sample_config(output_path: str | Path | None = None) -> str:
    """
    Generate a sample telemetry configuration file.

    Args:
        output_path: If provided, write config to this file

    Returns:
        Sample YAML configuration as string
    """
    sample = """\
# kgents Telemetry Configuration
# Place at ~/.kgents/telemetry.yaml

# Whether telemetry is enabled
enabled: true

# Service identification
service_name: kgents
service_version: "0.1.0"
environment: development  # development | staging | production

# Trace export settings
traces:
  # Exporter type: otlp, jaeger, json, none
  exporter: otlp

  # OTLP settings (for Tempo, Jaeger OTLP, or generic collector)
  otlp_endpoint: "localhost:4317"
  otlp_insecure: true

  # Jaeger native settings (alternative to OTLP)
  # jaeger_host: "localhost"
  # jaeger_port: 6831

  # Local JSON export (for development)
  # json_path: "~/.kgents/traces/"

  # Console output (for debugging)
  console: false

# Metrics settings
metrics:
  # Export interval in milliseconds
  export_interval_ms: 15000

# Sampling settings
sampling:
  # Sampling rate: 1.0 = all, 0.1 = 10%
  rate: 1.0
"""

    if output_path:
        path = Path(output_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sample)

    return sample


def ensure_config_directory() -> Path:
    """
    Ensure ~/.kgents directory exists.

    Returns:
        Path to ~/.kgents directory
    """
    config_dir = Path("~/.kgents").expanduser()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
