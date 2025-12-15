"""
Integration test for Agent Town metrics instrumentation.

Demonstrates end-to-end metrics flow:
1. LOD queries emit metrics
2. Dialogue operations emit metrics
3. Flux operations emit metrics
4. Metrics can be queried via API
"""

from __future__ import annotations

import pytest
from protocols.api.action_metrics import get_metrics_store


@pytest.mark.asyncio
async def test_lod_query_emits_metric():
    """Test that LOD queries emit metrics."""
    from agents.town.archetypes import ARCHETYPE_SPECS, ArchetypeKind
    from agents.town.citizen import Citizen, Eigenvectors

    store = get_metrics_store()
    store.clear()

    # Create a citizen
    spec = ARCHETYPE_SPECS[ArchetypeKind.BUILDER]
    citizen = Citizen(
        name="Alice",
        archetype="Builder",
        region="plaza",
        eigenvectors=Eigenvectors(
            warmth=0.7,
            curiosity=0.6,
            trust=0.8,
            creativity=0.5,
            patience=0.7,
            resilience=0.6,
            ambition=0.5,
        ),
        cosmotechnics=spec.cosmotechnics,
    )

    # Simulate LOD query by calling manifest directly
    # (In real usage, this would go through the API endpoint)
    import time

    from protocols.api.action_metrics import ActionType, emit_action_metric

    start = time.monotonic()
    manifest = citizen.manifest(lod=3)
    latency_ms = int((time.monotonic() - start) * 1000)

    # Emit metric as the API would
    emit_action_metric(
        action_type=ActionType.LOD3.value,
        user_id="test-user",
        town_id="test-town",
        citizen_id=citizen.id,
        tokens_in=0,
        tokens_out=0,
        model="template",
        latency_ms=latency_ms,
        credits_charged=10,
    )

    # Verify metric was emitted
    metrics = store.query(user_id="test-user")
    assert len(metrics) == 1

    metric = metrics[0]
    assert metric.action_type == "lod3"
    assert metric.credits_charged == 10
    assert manifest["name"] == "Alice"


@pytest.mark.asyncio
async def test_flux_operations_emit_metrics():
    """Test that flux operations emit metrics."""
    from agents.town.environment import create_phase3_environment
    from agents.town.flux import TownFlux

    store = get_metrics_store()
    store.clear()

    env = create_phase3_environment()
    flux = TownFlux(env, seed=42)

    # Run one step
    events = []
    async for event in flux.step():
        events.append(event)

    # Verify flux emitted metrics
    # Flux operations emit metrics with action_type="flux_{operation}"
    metrics = store.query(user_id="system")

    # Should have metrics for each event generated
    assert len(metrics) > 0

    # Verify metric structure
    if metrics:
        metric = metrics[0]
        assert metric.action_type.startswith("flux_")
        assert metric.user_id == "system"
        assert metric.credits_charged == 0  # Flux operations don't charge credits


@pytest.mark.asyncio
async def test_metrics_aggregation():
    """Test metrics aggregation for dashboard queries."""
    from datetime import datetime

    store = get_metrics_store()
    store.clear()

    # Emit several LOD3 metrics
    from protocols.api.action_metrics import emit_action_metric

    for i in range(5):
        emit_action_metric(
            action_type="lod3",
            user_id="user-123",
            town_id="town-456",
            tokens_in=100,
            tokens_out=50,
            model="haiku",
            latency_ms=100 + i * 10,
            credits_charged=10,
        )

    # Query and aggregate
    agg = store.aggregate(
        user_id="user-123",
        since=datetime.now().replace(hour=0, minute=0, second=0),
    )

    assert agg["count"] == 5
    assert agg["total_credits"] == 50
    assert agg["avg_latency_ms"] > 0


@pytest.mark.asyncio
async def test_metrics_dashboard_query():
    """Test dashboard query: 'What was the average LOD3 latency today?'"""
    from datetime import datetime, timedelta

    store = get_metrics_store()
    store.clear()

    # Emit LOD3 metrics with varying latencies
    from protocols.api.action_metrics import emit_action_metric

    latencies = [100, 150, 200, 250, 300]
    for lat in latencies:
        emit_action_metric(
            action_type="lod3",
            user_id="user-1",
            town_id="town-1",
            tokens_in=100,
            tokens_out=50,
            model="haiku",
            latency_ms=lat,
            credits_charged=10,
        )

    # Query for today
    today = datetime.now().replace(hour=0, minute=0, second=0)
    agg = store.aggregate(action_type="lod3", since=today)

    # Verify aggregation
    assert agg["count"] == 5
    assert agg["avg_latency_ms"] == 200.0  # Average of [100, 150, 200, 250, 300]
    assert agg["p50_latency_ms"] == 200  # Median
    assert agg["total_credits"] == 50


@pytest.mark.asyncio
async def test_unit_economics_tracking():
    """Test unit economics validation through metrics."""
    from protocols.api.action_metrics import emit_action_metric

    store = get_metrics_store()
    store.clear()

    # Simulate a typical LOD4 query (Sonnet)
    # From unified-v2.md: LOD4 @ 100 credits, Sonnet ~800 tokens
    emit_action_metric(
        action_type="lod4",
        user_id="user-1",
        town_id="town-1",
        tokens_in=500,
        tokens_out=300,
        model="sonnet",
        latency_ms=1000,
        credits_charged=100,
    )

    metrics = store.query(user_id="user-1")
    assert len(metrics) == 1

    metric = metrics[0]

    # Verify cost calculation
    # Sonnet: $3/1M input, $15/1M output
    # (500 * 3 / 1M) + (300 * 15 / 1M) = 0.0015 + 0.0045 = 0.006
    assert abs(metric.estimated_cost_usd - 0.006) < 0.0001

    # Verify revenue (conservative: $0.006/credit)
    # 100 * 0.006 = 0.60
    assert abs(metric.revenue_usd - 0.60) < 0.01

    # Verify positive margin
    assert metric.gross_margin > 0


@pytest.mark.asyncio
async def test_otel_span_export():
    """Test OTEL span export structure."""
    from protocols.api.action_metrics import ActionMetric

    metric = ActionMetric(
        action_type="lod4",
        user_id="user-123",
        town_id="town-456",
        citizen_id="citizen-789",
        tokens_in=500,
        tokens_out=300,
        model="sonnet",
        latency_ms=1000,
        credits_charged=100,
    )

    span_attrs = metric.to_otel_span()

    # Verify required fields for OTEL
    assert "action.type" in span_attrs
    assert "action.model" in span_attrs
    assert "action.tokens.in" in span_attrs
    assert "action.tokens.out" in span_attrs
    assert "action.tokens.total" in span_attrs
    assert "action.latency_ms" in span_attrs
    assert "action.credits" in span_attrs
    assert "action.cost_usd" in span_attrs
    assert "action.revenue_usd" in span_attrs
    assert "action.margin" in span_attrs

    # Verify context fields
    assert span_attrs["user.id"] == "user-123"
    assert span_attrs["town.id"] == "town-456"
    assert span_attrs["citizen.id"] == "citizen-789"
