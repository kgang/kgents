"""
Async LLM Loss Computation Demo.

This demo shows how to use the production-ready async Galois loss computation
with LLM support, caching, and fallback to fast metrics.

Run with:
    uv run python -m services.zero_seed.galois.examples.async_loss_demo
"""

import asyncio

from agents.k.llm import create_llm_client, has_llm_credentials
from services.zero_seed import EdgeKind, ZeroEdge, ZeroNode, generate_node_id
from services.zero_seed.galois.cross_layer import compute_cross_layer_loss_async
from services.zero_seed.galois.galois_loss import (
    LossCache,
    compute_galois_loss_async,
)
from services.witness.mark import Proof


async def demo_basic_loss():
    """Demo 1: Basic async loss computation."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Async Loss Computation")
    print("=" * 70)

    content = """
    The Galois loss measures how much structure is lost when content
    is restructured and then reconstituted. It's a fundamental metric
    for understanding semantic coherence.
    """

    print(f"\nContent to analyze:\n{content.strip()}")

    # Get LLM client if available
    llm = None
    if has_llm_credentials():
        print("\n✓ LLM credentials available, using LLM-based computation")
        llm = create_llm_client()
    else:
        print("\n⚠ No LLM credentials, will fall back to fast metrics")

    # Compute loss
    result = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
    )

    print(f"\nResult:")
    print(f"  Loss: {result.loss:.4f}")
    print(f"  Method: {result.method}")
    print(f"  Metric: {result.metric_name}")
    print(f"  Cached: {result.cached}")

    # Interpret result
    if result.loss < 0.1:
        interpretation = "Excellent - content is highly coherent"
    elif result.loss < 0.3:
        interpretation = "Good - content has moderate coherence"
    elif result.loss < 0.6:
        interpretation = "Fair - content has some structure loss"
    else:
        interpretation = "Poor - significant structure loss detected"

    print(f"  Interpretation: {interpretation}")


async def demo_caching():
    """Demo 2: Caching to avoid redundant LLM calls."""
    print("\n" + "=" * 70)
    print("DEMO 2: Caching Behavior")
    print("=" * 70)

    content = "Caching prevents redundant LLM calls for identical content."

    # Create shared cache
    cache = LossCache()

    # Get LLM if available
    llm = create_llm_client() if has_llm_credentials() else None

    # First computation - will call LLM
    print("\nFirst computation (should compute)...")
    result1 = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
        cache=cache,
    )
    print(f"  Loss: {result1.loss:.4f}, Cached: {result1.cached}")

    # Second computation - should use cache
    print("\nSecond computation (should use cache)...")
    result2 = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
        cache=cache,
    )
    print(f"  Loss: {result2.loss:.4f}, Cached: {result2.cached}")

    # Verify cache hit
    assert result2.cached is True, "Second call should be cached"
    assert result1.loss == result2.loss, "Loss values should match"

    print("\n✓ Cache working correctly!")


async def demo_fallback():
    """Demo 3: Fallback to fast metrics when LLM unavailable."""
    print("\n" + "=" * 70)
    print("DEMO 3: Fallback to Fast Metrics")
    print("=" * 70)

    content = """
    When the LLM is unavailable (network issues, API limits, etc.),
    the system automatically falls back to fast metrics like BERTScore
    or cosine similarity.
    """

    print(f"\nContent:\n{content.strip()}")

    # Force fallback by passing None for LLM
    print("\nComputing loss without LLM (forced fallback)...")
    result = await compute_galois_loss_async(
        content,
        llm_client=None,  # Force fallback
        use_cache=False,
    )

    print(f"\nResult:")
    print(f"  Loss: {result.loss:.4f}")
    print(f"  Method: {result.method}")
    print(f"  Metric: {result.metric_name}")

    # Fallback should still give reasonable results
    assert 0.0 <= result.loss <= 1.0, "Loss should be in valid range"
    print("\n✓ Fallback working correctly!")


async def demo_cross_layer_loss():
    """Demo 4: Cross-layer loss computation with LLM."""
    print("\n" + "=" * 70)
    print("DEMO 4: Cross-Layer Loss Computation")
    print("=" * 70)

    # Create test nodes
    axiom = ZeroNode(
        id=generate_node_id(),
        layer=1,
        path="void.axiom.modularity",
        title="Modularity Axiom",
        content="A system is modular when its components have well-defined interfaces.",
    )

    implementation = ZeroNode(
        id=generate_node_id(),
        layer=5,
        path="world.action.implement",
        title="Implement Modularity",
        content="Use dependency injection to enforce modular boundaries in code.",
        proof=Proof(
            data="Modularity axiom requires well-defined interfaces",
            warrant="Dependency injection enforces interface contracts",
            claim="DI implements modularity",
        ),
    )

    edge = ZeroEdge(
        source=axiom.id,
        target=implementation.id,
        kind=EdgeKind.IMPLEMENTS,
    )

    print(f"\nSource Node (L{axiom.layer}): {axiom.title}")
    print(f"  {axiom.content}")
    print(f"\nTarget Node (L{implementation.layer}): {implementation.title}")
    print(f"  {implementation.content}")
    print(f"\nEdge: {edge.kind.value}")

    # Get LLM if available
    llm = create_llm_client() if has_llm_credentials() else None

    # Compute cross-layer loss
    print("\nComputing cross-layer loss...")
    result = await compute_cross_layer_loss_async(
        axiom,
        implementation,
        edge,
        llm_client=llm,
        use_llm=llm is not None,
    )

    print(f"\nResult:")
    print(f"  Layer Delta: {result.layer_delta}")
    print(f"  Total Loss: {result.total_loss:.4f}")
    print(f"  Explanation: {result.explanation}")
    if result.suggestion:
        print(f"  Suggestion: {result.suggestion}")

    # Interpret result
    if result.total_loss < 0.3:
        print("\n✓ Low loss - edge connection is semantically coherent")
    elif result.total_loss < 0.6:
        print("\n⚠ Moderate loss - consider adding intermediate nodes")
    else:
        print("\n✗ High loss - semantic jump is too large")


async def demo_batch_processing():
    """Demo 5: Batch processing with shared cache."""
    print("\n" + "=" * 70)
    print("DEMO 5: Batch Processing with Shared Cache")
    print("=" * 70)

    contents = [
        "First piece of content to analyze.",
        "Second piece with different structure.",
        "Third piece to test batch processing.",
        "First piece of content to analyze.",  # Duplicate - should hit cache
    ]

    # Shared cache for batch
    cache = LossCache()
    llm = create_llm_client() if has_llm_credentials() else None

    print(f"\nProcessing {len(contents)} items...")

    results = []
    for i, content in enumerate(contents, 1):
        result = await compute_galois_loss_async(
            content,
            llm_client=llm,
            use_cache=True,
            cache=cache,
        )
        results.append(result)
        print(
            f"  {i}. Loss: {result.loss:.4f}, "
            f"Cached: {'✓' if result.cached else '✗'}, "
            f"Method: {result.method}"
        )

    # Verify cache hit for duplicate
    assert results[3].cached is True, "Fourth item should be cached"
    assert results[0].loss == results[3].loss, "Duplicate should have same loss"

    print("\n✓ Batch processing complete!")


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("GALOIS ASYNC LLM LOSS COMPUTATION DEMO")
    print("=" * 70)

    # Check LLM availability
    if has_llm_credentials():
        print("\n✓ LLM credentials detected - using LLM-based computation")
    else:
        print("\n⚠ No LLM credentials - will use fallback metrics")
        print("  (This is expected in CI/CD or when LLM is unavailable)")

    # Run demos
    await demo_basic_loss()
    await demo_caching()
    await demo_fallback()
    await demo_cross_layer_loss()
    await demo_batch_processing()

    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Use compute_galois_loss_async() for production loss computation")
    print("  2. Always provide an LLM client when available for best results")
    print("  3. Enable caching to avoid redundant LLM calls")
    print("  4. System falls back gracefully when LLM is unavailable")
    print("  5. Cross-layer loss helps identify semantic jumps in graphs")
    print()


if __name__ == "__main__":
    asyncio.run(main())
