"""
Simple Async LLM Loss Computation Demo.

A minimal demo showing async Galois loss computation without
importing heavyweight services.

Run with:
    cd impl/claude
    uv run python services/zero_seed/galois/examples/simple_async_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parents[4]))

from services.zero_seed.galois.galois_loss import (
    GaloisLoss,
    LossCache,
    SimpleLLMClient,
    compute_galois_loss_async,
)


async def demo_basic():
    """Basic async loss computation demo."""
    print("\n" + "=" * 60)
    print("DEMO: Basic Async Galois Loss Computation")
    print("=" * 60)

    content = """
    The Galois loss measures how much structure is lost when content
    is restructured and then reconstituted. It's a fundamental metric
    for understanding semantic coherence.
    """

    print(f"\nContent to analyze:\n{content.strip()}")

    # Create LLM client (will use kgents LLM abstraction)
    try:
        llm = SimpleLLMClient()
        print("\n✓ Using SimpleLLMClient (kgents LLM abstraction)")
    except Exception as e:
        print(f"\n⚠ Could not create LLM client: {e}")
        llm = None

    # Compute loss
    print("\nComputing Galois loss...")
    result = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
    )

    print("\nResult:")
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
    """Caching demo."""
    print("\n" + "=" * 60)
    print("DEMO: Caching Behavior")
    print("=" * 60)

    content = "Caching prevents redundant LLM calls for identical content."

    # Create shared cache
    cache = LossCache()

    # Try to get LLM
    try:
        llm = SimpleLLMClient()
    except Exception:
        llm = None

    # First computation
    print("\nFirst computation (will compute)...")
    result1 = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
        cache=cache,
    )
    print(f"  Loss: {result1.loss:.4f}, Cached: {result1.cached}")

    # Second computation
    print("\nSecond computation (should use cache)...")
    result2 = await compute_galois_loss_async(
        content,
        llm_client=llm,
        use_cache=True,
        cache=cache,
    )
    print(f"  Loss: {result2.loss:.4f}, Cached: {result2.cached}")

    # Verify
    if result2.cached:
        print("\n✓ Cache working correctly!")
    else:
        print("\n⚠ Cache miss (may be expected if LLM unavailable)")


async def demo_fallback():
    """Fallback demo."""
    print("\n" + "=" * 60)
    print("DEMO: Fallback to Fast Metrics")
    print("=" * 60)

    content = """
    When the LLM is unavailable, the system automatically falls back
    to fast metrics like BERTScore or cosine similarity.
    """

    print(f"\nContent:\n{content.strip()}")

    # Force fallback by passing None
    print("\nComputing loss without LLM (forced fallback)...")
    result = await compute_galois_loss_async(
        content,
        llm_client=None,
        use_cache=False,
    )

    print("\nResult:")
    print(f"  Loss: {result.loss:.4f}")
    print(f"  Method: {result.method}")
    print(f"  Metric: {result.metric_name}")

    assert 0.0 <= result.loss <= 1.0
    print("\n✓ Fallback working correctly!")


async def demo_batch():
    """Batch processing demo."""
    print("\n" + "=" * 60)
    print("DEMO: Batch Processing")
    print("=" * 60)

    contents = [
        "First piece of content.",
        "Second piece with different structure.",
        "Third piece to test batching.",
        "First piece of content.",  # Duplicate
    ]

    cache = LossCache()

    try:
        llm = SimpleLLMClient()
    except Exception:
        llm = None

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
        cached_marker = "✓" if result.cached else "✗"
        print(
            f"  {i}. Loss: {result.loss:.4f}, "
            f"Cached: {cached_marker}, "
            f"Method: {result.method}"
        )

    # Check duplicate was cached
    if results[3].cached:
        print("\n✓ Batch processing complete - duplicate was cached!")
    else:
        print("\n⚠ Duplicate not cached (may be expected)")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("GALOIS ASYNC LLM LOSS COMPUTATION - SIMPLE DEMO")
    print("=" * 60)

    try:
        await demo_basic()
        await demo_caching()
        await demo_fallback()
        await demo_batch()

        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETE")
        print("=" * 60)
        print("\nKey Features:")
        print("  ✓ Async LLM-based loss computation")
        print("  ✓ Caching to avoid redundant calls")
        print("  ✓ Graceful fallback to fast metrics")
        print("  ✓ Batch processing support")
        print()

    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
