"""
Tests for health probes.
"""

import pytest

from services.probe.health import HealthProbe
from services.probe.types import ProbeStatus, ProbeType


@pytest.mark.asyncio
async def test_health_probe_brain():
    """Test brain health probe."""
    probe = HealthProbe()

    result = await probe.check_brain()

    # Should at least return a result (may pass or fail depending on setup)
    assert result is not None
    assert result.name == "health:brain"
    assert result.probe_type == ProbeType.HEALTH
    assert result.duration_ms >= 0

    # If it passed, details should mention health
    if result.passed:
        assert "healthy" in result.details.lower() or "Brain" in result.details


@pytest.mark.asyncio
async def test_health_probe_witness():
    """Test witness health probe."""
    probe = HealthProbe()

    result = await probe.check_witness()

    assert result is not None
    assert result.name == "health:witness"
    assert result.probe_type == ProbeType.HEALTH
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_health_probe_kblock():
    """Test k-block health probe."""
    probe = HealthProbe()

    result = await probe.check_kblock()

    assert result is not None
    assert result.name == "health:kblock"
    assert result.probe_type == ProbeType.HEALTH
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_health_probe_sovereign():
    """Test sovereign health probe."""
    probe = HealthProbe()

    result = await probe.check_sovereign()

    assert result is not None
    assert result.name == "health:sovereign"
    assert result.probe_type == ProbeType.HEALTH
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_health_probe_all():
    """Test health check for all components."""
    probe = HealthProbe()

    results = await probe.check_all()

    # Should have results for all 5 components (brain, witness, kblock, sovereign, llm)
    assert len(results) == 5

    components = {r.name for r in results}
    assert "health:brain" in components
    assert "health:witness" in components
    assert "health:kblock" in components
    assert "health:sovereign" in components
    assert "health:llm" in components

    # All should have valid probe type
    for result in results:
        assert result.probe_type == ProbeType.HEALTH


@pytest.mark.asyncio
async def test_health_probe_component():
    """Test health check for specific component."""
    probe = HealthProbe()

    # Test valid components
    result = await probe.check_component("brain")
    assert result.name == "health:brain"

    result = await probe.check_component("witness")
    assert result.name == "health:witness"

    result = await probe.check_component("kblock")
    assert result.name == "health:kblock"

    result = await probe.check_component("k-block")  # alias
    assert result.name == "health:kblock"

    result = await probe.check_component("sovereign")
    assert result.name == "health:sovereign"


@pytest.mark.asyncio
async def test_health_probe_unknown_component():
    """Test health check for unknown component."""
    probe = HealthProbe()

    result = await probe.check_component("unknown")

    assert result.status == ProbeStatus.ERROR
    assert "Unknown component" in result.details
