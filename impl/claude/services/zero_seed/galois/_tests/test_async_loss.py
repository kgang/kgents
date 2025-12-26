"""
Tests for async LLM-based Galois loss computation.

This test suite validates:
1. Async loss computation with LLM
2. Fallback to fast metrics when LLM unavailable
3. Caching behavior
4. Cross-layer loss computation with LLM
"""

import pytest

from services.zero_seed.galois.galois_loss import (
    GaloisLoss,
    LossCache,
    compute_galois_loss_async,
)


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.call_count = 0

    async def restructure(self, content: str):
        """Mock restructure operation."""
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Mock LLM failure")

        from services.zero_seed.galois.galois_loss import (
            ModularComponent,
            ModularPrompt,
        )

        # Simple mock: split into sentences
        sentences = content.split(". ")
        components = [
            ModularComponent(
                name=f"component_{i}",
                content=sent,
                weight=1.0,
                dependencies=(),
            )
            for i, sent in enumerate(sentences)
            if sent.strip()
        ]

        return ModularPrompt(components=components)

    async def reconstitute(self, modular):
        """Mock reconstitute operation."""
        if self.should_fail:
            raise RuntimeError("Mock LLM failure")

        # Simple mock: join components
        return ". ".join(c.content for c in modular.components)


@pytest.mark.asyncio
async def test_compute_galois_loss_basic():
    """Test basic async loss computation."""
    content = "This is a test. It has multiple sentences. Testing loss computation."
    mock_llm = MockLLMClient()

    result = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=False,
    )

    assert isinstance(result, GaloisLoss)
    assert 0.0 <= result.loss <= 1.0
    assert result.method == "llm"
    assert result.cached is False
    assert mock_llm.call_count > 0  # LLM was actually called


@pytest.mark.asyncio
async def test_compute_galois_loss_with_cache():
    """Test caching behavior."""
    content = "This content will be cached."
    cache = LossCache()
    mock_llm = MockLLMClient()

    # First call - should compute
    result1 = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=True,
        cache=cache,
    )

    call_count_after_first = mock_llm.call_count

    # Second call - should use cache
    result2 = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=True,
        cache=cache,
    )

    assert result2.cached is True
    assert result2.loss == result1.loss
    # LLM should not be called again (restructure happens in compute_loss)
    # Note: call count might increase by 1 during computer initialization
    assert mock_llm.call_count <= call_count_after_first + 1


@pytest.mark.asyncio
async def test_compute_galois_loss_fallback():
    """Test fallback to fast metrics when LLM fails."""
    content = "This content will trigger fallback."
    mock_llm = MockLLMClient(should_fail=True)

    result = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=False,
    )

    assert isinstance(result, GaloisLoss)
    assert 0.0 <= result.loss <= 1.0
    assert result.method == "fallback"
    # Should fall back to bertscore or cosine or default
    assert result.metric_name in ("bertscore", "cosine", "default")


@pytest.mark.asyncio
async def test_compute_galois_loss_no_llm():
    """Test behavior when no LLM client provided."""
    content = "Testing without LLM client."

    # Should create SimpleLLMClient and attempt to use it
    # This will likely fail if no real LLM is available, triggering fallback
    result = await compute_galois_loss_async(
        content,
        llm_client=None,
        use_cache=False,
    )

    assert isinstance(result, GaloisLoss)
    assert 0.0 <= result.loss <= 1.0
    # Method could be 'llm' or 'fallback' depending on environment
    assert result.method in ("llm", "fallback")


@pytest.mark.asyncio
async def test_compute_galois_loss_identical_content():
    """Test loss on identical content (should be very low)."""
    content = "Identical content."
    mock_llm = MockLLMClient()

    result = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=False,
    )

    # Loss should be very low for short identical content
    # (mock reconstitution should be nearly identical)
    assert result.loss < 0.3  # Allow some noise from metric


@pytest.mark.asyncio
async def test_compute_galois_loss_diverse_content():
    """Test loss on diverse content (higher expected loss)."""
    # Content that will change more during R o C
    content = """
    This is a complex multi-sentence paragraph with various concepts.
    It includes abstract ideas, concrete examples, and transitions.
    The restructuring and reconstitution process may introduce semantic drift.
    We expect higher Galois loss due to the complexity.
    """

    mock_llm = MockLLMClient()

    result = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=False,
    )

    # For diverse content, we expect measurable loss
    # (though mock might still be low - this is a smoke test)
    assert 0.0 <= result.loss <= 1.0


@pytest.mark.asyncio
async def test_cross_layer_loss_with_llm():
    """Test cross-layer loss computation with LLM."""
    from services.zero_seed import EdgeKind, ZeroEdge, ZeroNode, generate_node_id
    from services.zero_seed.galois.cross_layer import compute_cross_layer_loss_async
    from services.witness.mark import Proof

    source = ZeroNode(
        id=generate_node_id(),
        layer=1,
        path="void.axiom.entity",
        title="Entity Axiom",
        content="An entity is a fundamental unit of existence.",
    )

    # L5 node requires proof
    target = ZeroNode(
        id=generate_node_id(),
        layer=5,
        path="world.action.implement",
        title="Implementation",
        content="Implement entity storage using PostgreSQL.",
        proof=Proof(
            data="Need to store entities",
            warrant="PostgreSQL provides ACID guarantees",
            claim="Use PostgreSQL for entity storage",
        ),
    )

    edge = ZeroEdge(
        source=source.id,
        target=target.id,
        kind=EdgeKind.IMPLEMENTS,
    )

    mock_llm = MockLLMClient()

    # Test with LLM
    result_with_llm = await compute_cross_layer_loss_async(
        source,
        target,
        edge,
        llm_client=mock_llm,
        use_llm=True,
    )

    assert result_with_llm.layer_delta == 4
    assert 0.0 <= result_with_llm.total_loss <= 1.0
    assert "layer(s)" in result_with_llm.explanation

    # Test without LLM (heuristic fallback)
    result_without_llm = await compute_cross_layer_loss_async(
        source,
        target,
        edge,
        llm_client=None,
        use_llm=False,
    )

    assert result_without_llm.layer_delta == 4
    # Heuristic should give predictable loss based on formula
    # loss = min(1.0, 0.1 * 4 * 0.8) = 0.32
    assert abs(result_without_llm.total_loss - 0.32) < 0.01


@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test cache invalidation."""
    content = "Content for cache test."
    cache = LossCache()
    mock_llm = MockLLMClient()

    # Compute and cache
    result1 = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=True,
        cache=cache,
    )

    # Invalidate cache
    cache.invalidate(content)

    # Next call should recompute
    initial_count = mock_llm.call_count
    result2 = await compute_galois_loss_async(
        content,
        llm_client=mock_llm,
        use_cache=True,
        cache=cache,
    )

    assert result2.cached is False  # Should not be cached
    # LLM should be called again
    assert mock_llm.call_count > initial_count


def test_loss_cache_basic():
    """Test basic cache operations."""
    cache = LossCache(max_size=3)

    # Set values
    cache.set("content1", "node_loss", 0.5, "metric1")
    cache.set("content2", "node_loss", 0.3, "metric1")
    cache.set("content3", "node_loss", 0.7, "metric1")

    # Get values
    assert cache.get("content1", "node_loss") == 0.5
    assert cache.get("content2", "node_loss") == 0.3
    assert cache.get("content3", "node_loss") == 0.7

    # Test eviction when exceeding max_size
    cache.set("content4", "node_loss", 0.9, "metric1")
    # content1 should be evicted (oldest)
    assert cache.get("content1", "node_loss") is None
    assert cache.get("content4", "node_loss") == 0.9


def test_loss_cache_clear():
    """Test cache clearing."""
    cache = LossCache()

    cache.set("content1", "loss_type", 0.5, "metric")
    assert cache.get("content1", "loss_type") == 0.5

    cache.clear()
    assert cache.get("content1", "loss_type") is None
