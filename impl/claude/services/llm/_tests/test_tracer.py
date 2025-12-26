"""
Tests for LLM Tracer.

Verifies that every LLM call is captured with full causality:
- Request/response captured
- Causal chain tracked
- State changes recorded
- Galois loss computed
- Stored in Universe

Test Categories:
1. Basic trace capture
2. Causal chain tracking
3. State change recording
4. Galois loss computation
5. Error handling
6. Querying and retrieval
"""

from datetime import UTC, datetime

import pytest

from agents.d.galois import GaloisLossComputer
from agents.d.schemas.llm_trace import LLMInvocationMark, StateChange
from agents.d.universe import Backend, Universe
from services.llm.tracer import LLMTraceContext, LLMTracer


@pytest.fixture
async def universe():
    """Create test Universe with memory backend."""
    universe = Universe(namespace="test-llm", preferred_backend=Backend.MEMORY)
    await universe._ensure_initialized()
    return universe


@pytest.fixture
async def tracer(universe):
    """Create LLM tracer with Galois loss computer."""
    galois = GaloisLossComputer(metric="token")
    return LLMTracer(universe=universe, galois=galois)


# =============================================================================
# Test Category 1: Basic Trace Capture
# =============================================================================


@pytest.mark.asyncio
async def test_basic_trace_capture(tracer):
    """Test basic LLM call is captured with all fields."""
    async with tracer.trace(triggered_by="test") as ctx:
        ctx.set_request(
            model="claude-3.5-sonnet",
            prompt="What is 2+2?",
            system="You are a calculator",
            temperature=0.0,
        )
        ctx.set_response("4", tokens=(10, 2))

    # Query traces
    traces = await tracer.query_traces(limit=10)
    assert len(traces) == 1

    trace = traces[0]
    assert trace.model == "claude-3.5-sonnet"
    assert trace.user_prompt == "What is 2+2?"
    assert trace.response == "4"
    assert trace.prompt_tokens == 10
    assert trace.completion_tokens == 2
    assert trace.total_tokens == 12
    assert trace.success is True
    assert trace.error is None
    assert trace.invocation_type == "generation"
    assert trace.triggered_by == "test"


@pytest.mark.asyncio
async def test_trace_without_tokens_estimates(tracer):
    """Test trace without explicit tokens estimates them."""
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Hello" * 100)
        ctx.set_response("Hi" * 50)  # No tokens provided

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    # Should estimate ~4 chars per token
    assert trace.prompt_tokens > 0
    assert trace.completion_tokens > 0
    assert trace.total_tokens == trace.prompt_tokens + trace.completion_tokens


@pytest.mark.asyncio
async def test_trace_with_system_prompt_hash(tracer):
    """Test system prompt is hashed for deduplication."""
    system_prompt = "You are a helpful assistant."

    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Hello", system=system_prompt)
        ctx.set_response("Hi")

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    # Should have hash
    assert trace.system_prompt_hash is not None
    assert trace.system_prompt_hash != "none"
    assert len(trace.system_prompt_hash) == 16  # Truncated SHA-256


# =============================================================================
# Test Category 2: Causal Chain Tracking
# =============================================================================


@pytest.mark.asyncio
async def test_causal_parent_tracking(tracer):
    """Test causal parent is recorded."""
    async with tracer.trace(causal_parent_id="parent-123", triggered_by="cascade") as ctx:
        ctx.set_request("claude-3.5-sonnet", "Child call")
        ctx.set_response("Response")

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    assert trace.causal_parent_id == "parent-123"
    assert trace.triggered_by == "cascade"


@pytest.mark.asyncio
async def test_causal_chain_reconstruction(tracer):
    """Test full causal chain can be reconstructed."""
    # Create chain: root → middle → leaf
    async with tracer.trace(triggered_by="user_input") as ctx:
        ctx.set_request("claude-3.5-sonnet", "Root")
        ctx.set_response("Root response")
        root_id = ctx.id

    async with tracer.trace(causal_parent_id=root_id, triggered_by="cascade") as ctx:
        ctx.set_request("claude-3.5-sonnet", "Middle")
        ctx.set_response("Middle response")
        middle_id = ctx.id

    async with tracer.trace(causal_parent_id=middle_id, triggered_by="cascade") as ctx:
        ctx.set_request("claude-3.5-sonnet", "Leaf")
        ctx.set_response("Leaf response")
        leaf_id = ctx.id

    # Get chain from leaf
    chain = await tracer.get_causal_chain(leaf_id)

    assert len(chain) == 3
    assert chain[0].id == root_id  # Root first
    assert chain[1].id == middle_id  # Middle second
    assert chain[2].id == leaf_id  # Leaf last

    assert chain[0].user_prompt == "Root"
    assert chain[1].user_prompt == "Middle"
    assert chain[2].user_prompt == "Leaf"


@pytest.mark.asyncio
async def test_causal_children_query(tracer):
    """Test querying children of a parent trace."""
    async with tracer.trace(triggered_by="user_input") as ctx:
        ctx.set_request("claude-3.5-sonnet", "Parent")
        ctx.set_response("Parent response")
        parent_id = ctx.id

    # Create multiple children
    for i in range(3):
        async with tracer.trace(causal_parent_id=parent_id, triggered_by="cascade") as ctx:
            ctx.set_request("claude-3.5-sonnet", f"Child {i}")
            ctx.set_response(f"Child {i} response")

    children = await tracer.get_causal_children(parent_id)
    assert len(children) == 3

    prompts = {c.user_prompt for c in children}
    assert prompts == {"Child 0", "Child 1", "Child 2"}


# =============================================================================
# Test Category 3: State Change Recording
# =============================================================================


@pytest.mark.asyncio
async def test_state_change_recording(tracer):
    """Test state changes are captured."""
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Create crystal")
        ctx.set_response("Created")

        # Record state changes
        ctx.add_crystal_created("crystal-123")
        ctx.add_crystal_modified("crystal-456")
        ctx.add_edge_created("edge-789")
        ctx.add_state_change(
            StateChange(
                entity_type="crystal",
                entity_id="crystal-123",
                change_type="created",
                before_hash=None,
                after_hash="abc123",
            )
        )

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    assert "crystal-123" in trace.crystals_created
    assert "crystal-456" in trace.crystals_modified
    assert "edge-789" in trace.edges_created
    assert len(trace.state_changes) == 1

    change = trace.state_changes[0]
    assert change.entity_type == "crystal"
    assert change.entity_id == "crystal-123"
    assert change.change_type == "created"
    assert change.before_hash is None
    assert change.after_hash == "abc123"


@pytest.mark.asyncio
async def test_ripple_effects_query(tracer):
    """Test querying ripple effects across causal chain."""
    # Parent creates crystal-1
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Parent")
        ctx.set_response("Done")
        ctx.add_state_change(
            StateChange(
                entity_type="crystal",
                entity_id="crystal-1",
                change_type="created",
                before_hash=None,
                after_hash="hash1",
            )
        )
        parent_id = ctx.id

    # Child creates crystal-2 (cascaded effect)
    async with tracer.trace(causal_parent_id=parent_id) as ctx:
        ctx.set_request("claude-3.5-sonnet", "Child")
        ctx.set_response("Done")
        ctx.add_state_change(
            StateChange(
                entity_type="crystal",
                entity_id="crystal-2",
                change_type="created",
                before_hash=None,
                after_hash="hash2",
            )
        )

    # Get ripple effects
    effects = await tracer.get_ripple_effects(parent_id)

    # Should include both parent and child effects
    assert len(effects) == 2
    entity_ids = {e.entity_id for e in effects}
    assert entity_ids == {"crystal-1", "crystal-2"}


@pytest.mark.asyncio
async def test_query_traces_by_crystal(tracer):
    """Test finding all traces that touched a crystal."""
    # Multiple traces create/modify same crystal
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Create")
        ctx.set_response("Created")
        ctx.add_crystal_created("crystal-target")

    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Modify")
        ctx.set_response("Modified")
        ctx.add_crystal_modified("crystal-target")

    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Unrelated")
        ctx.set_response("Done")
        ctx.add_crystal_created("crystal-other")

    traces = await tracer.get_traces_by_crystal("crystal-target")
    assert len(traces) == 2

    prompts = {t.user_prompt for t in traces}
    assert prompts == {"Create", "Modify"}


# =============================================================================
# Test Category 4: Galois Loss Computation
# =============================================================================


@pytest.mark.asyncio
async def test_galois_loss_computed(tracer):
    """Test Galois loss is computed for responses."""
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Explain coherence")
        ctx.set_response("Coherence is the quality of forming a unified whole.")

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    # Should have loss computed
    assert 0.0 <= trace.galois_loss <= 1.0
    assert trace.coherence == 1.0 - trace.galois_loss

    # Coherent response should have low loss
    assert trace.galois_loss < 0.5


@pytest.mark.asyncio
async def test_aggregate_loss_computation(tracer):
    """Test computing average loss across traces."""
    # Create multiple traces with different coherence
    for i in range(5):
        async with tracer.trace() as ctx:
            ctx.set_request("claude-3.5-sonnet", f"Question {i}")
            ctx.set_response(f"Answer {i}")

    traces = await tracer.query_traces(limit=10)
    avg_loss = await tracer.compute_aggregate_loss(traces)

    assert 0.0 <= avg_loss <= 1.0


# =============================================================================
# Test Category 5: Error Handling
# =============================================================================


@pytest.mark.asyncio
async def test_error_capture(tracer):
    """Test errors are captured in traces."""
    try:
        async with tracer.trace() as ctx:
            ctx.set_request("claude-3.5-sonnet", "Failing call")
            raise ValueError("LLM API error")
    except ValueError:
        pass  # Expected

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    assert trace.success is False
    assert trace.error == "LLM API error"
    assert trace.response == ""  # No response on error


@pytest.mark.asyncio
async def test_error_with_partial_response(tracer):
    """Test error after partial response is captured."""
    try:
        async with tracer.trace() as ctx:
            ctx.set_request("claude-3.5-sonnet", "Partial")
            ctx.set_response("Partial respo")  # Incomplete
            ctx.set_error("Connection timeout")
            raise Exception("Timeout")
    except Exception:
        pass

    traces = await tracer.query_traces(limit=1)
    trace = traces[0]

    assert trace.success is False
    assert trace.error == "Connection timeout"
    assert trace.response == "Partial respo"  # Preserved


# =============================================================================
# Test Category 6: Querying and Retrieval
# =============================================================================


@pytest.mark.asyncio
async def test_get_trace_by_id(tracer):
    """Test retrieving trace by ID."""
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Test")
        ctx.set_response("Response")
        trace_id = ctx.id

    retrieved = await tracer.get_trace(trace_id)
    assert retrieved is not None
    assert retrieved.id == trace_id
    assert retrieved.user_prompt == "Test"


@pytest.mark.asyncio
async def test_query_traces_with_limit(tracer):
    """Test querying with limit."""
    # Create 10 traces
    for i in range(10):
        async with tracer.trace() as ctx:
            ctx.set_request("claude-3.5-sonnet", f"Call {i}")
            ctx.set_response(f"Response {i}")

    # Query with limit
    traces = await tracer.query_traces(limit=5)
    assert len(traces) == 5


@pytest.mark.asyncio
async def test_get_stats(tracer):
    """Test getting aggregate statistics."""
    # Create some traces
    for i in range(3):
        async with tracer.trace() as ctx:
            ctx.set_request("claude-3.5-sonnet", f"Question {i}")
            ctx.set_response(f"Answer {i}", tokens=(10, 20))

    stats = await tracer.get_stats()

    assert stats["total_traces"] == 3
    assert stats["total_tokens"] == 90  # 3 * 30
    assert stats["average_tokens_per_call"] == 30
    assert stats["success_rate"] == 1.0
    assert stats["average_latency_ms"] >= 0  # Can be 0 for very fast calls
    assert 0.0 <= stats["average_loss"] <= 1.0


@pytest.mark.asyncio
async def test_empty_stats(tracer):
    """Test stats with no traces."""
    stats = await tracer.get_stats()

    assert stats["total_traces"] == 0
    assert stats["total_tokens"] == 0
    assert stats["average_latency_ms"] == 0
    assert stats["average_loss"] == 0.0
    assert stats["success_rate"] == 0.0


# =============================================================================
# Test Category 7: Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_full_trace_lifecycle(tracer):
    """Test complete trace lifecycle from creation to retrieval."""
    # Create trace with all features
    async with tracer.trace(
        causal_parent_id="parent-xyz",
        triggered_by="user_input",
        invocation_type="analysis",
        tags={"session:abc", "agent:k-gent"},
    ) as ctx:
        ctx.set_request(
            model="claude-3.5-sonnet",
            prompt="Analyze kgents architecture",
            system="You are an expert on kgents",
            temperature=0.7,
        )
        ctx.set_response("kgents uses a metaphysical fullstack...", tokens=(50, 100))
        ctx.add_crystal_created("crystal-123")
        ctx.add_state_change(
            StateChange(
                entity_type="crystal",
                entity_id="crystal-123",
                change_type="created",
                before_hash=None,
                after_hash="hash123",
            )
        )
        trace_id = ctx.id

    # Retrieve and verify
    trace = await tracer.get_trace(trace_id)
    assert trace is not None
    assert trace.causal_parent_id == "parent-xyz"
    assert trace.triggered_by == "user_input"
    assert trace.invocation_type == "analysis"
    assert "session:abc" in trace.tags
    assert "agent:k-gent" in trace.tags
    assert trace.model == "claude-3.5-sonnet"
    assert trace.temperature == 0.7
    assert trace.total_tokens == 150
    assert "crystal-123" in trace.crystals_created
    assert len(trace.state_changes) == 1


@pytest.mark.asyncio
async def test_trace_serialization_roundtrip(tracer):
    """Test trace can be serialized and deserialized."""
    async with tracer.trace() as ctx:
        ctx.set_request("claude-3.5-sonnet", "Test serialization")
        ctx.set_response("Response")
        ctx.add_crystal_created("crystal-456")
        trace_id = ctx.id

    # Retrieve trace
    original = await tracer.get_trace(trace_id)
    assert original is not None

    # Serialize to dict
    data = original.to_dict()
    assert isinstance(data, dict)
    assert data["id"] == trace_id

    # Deserialize back
    reconstructed = LLMInvocationMark.from_dict(data)
    assert reconstructed.id == original.id
    assert reconstructed.user_prompt == original.user_prompt
    assert reconstructed.response == original.response
    assert reconstructed.crystals_created == original.crystals_created
