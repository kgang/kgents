"""
Tests for probe types.
"""

import pytest
from services.probe.types import HealthStatus, ProbeResult, ProbeStatus, ProbeType


def test_probe_result_creation():
    """Test ProbeResult creation and properties."""
    result = ProbeResult(
        name="test:probe",
        probe_type=ProbeType.IDENTITY,
        status=ProbeStatus.PASSED,
        details="All good",
        duration_ms=10.5,
    )

    assert result.name == "test:probe"
    assert result.probe_type == ProbeType.IDENTITY
    assert result.status == ProbeStatus.PASSED
    assert result.passed is True
    assert result.failed is False
    assert result.details == "All good"
    assert result.duration_ms == 10.5


def test_probe_result_failed():
    """Test ProbeResult for failed probe."""
    result = ProbeResult(
        name="test:failed",
        probe_type=ProbeType.ASSOCIATIVITY,
        status=ProbeStatus.FAILED,
        details="Law violated",
    )

    assert result.passed is False
    assert result.failed is True


def test_probe_result_to_dict():
    """Test ProbeResult serialization to dict."""
    result = ProbeResult(
        name="test:dict",
        probe_type=ProbeType.HEALTH,
        status=ProbeStatus.PASSED,
        duration_ms=5.2,
    )

    data = result.to_dict()

    assert data["name"] == "test:dict"
    assert data["probe_type"] == "health"
    assert data["status"] == "passed"
    assert data["passed"] is True
    assert data["duration_ms"] == 5.2
    assert "timestamp" in data


def test_health_status_creation():
    """Test HealthStatus creation."""
    status = HealthStatus(
        component="brain",
        healthy=True,
        checks={"import": True, "query": True},
        uptime_ms=1234.5,
    )

    assert status.component == "brain"
    assert status.healthy is True
    assert status.checks == {"import": True, "query": True}
    assert status.uptime_ms == 1234.5


def test_health_status_to_dict():
    """Test HealthStatus serialization."""
    status = HealthStatus(
        component="witness",
        healthy=False,
        checks={"import": True, "query": False},
        last_error="Connection failed",
    )

    data = status.to_dict()

    assert data["component"] == "witness"
    assert data["healthy"] is False
    assert data["checks"]["import"] is True
    assert data["checks"]["query"] is False
    assert data["last_error"] == "Connection failed"
