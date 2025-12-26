#!/usr/bin/env python3
"""
Test script for Zero Seed Analysis API endpoint.

Verifies that:
1. Mock data endpoint works (default behavior)
2. LLM analysis endpoint works when use_llm=true
3. Transformation from FullAnalysisReport to NodeAnalysisResponse is correct

Usage:
    uv run python scripts/test_analysis_endpoint.py
"""

import asyncio
import sys
from pathlib import Path


async def test_mock_analysis():
    """Test mock data endpoint (default behavior)."""
    print("=" * 80)
    print("TEST 1: Mock Analysis (use_llm=false)")
    print("=" * 80)

    from protocols.api.zero_seed import create_zero_seed_router

    router = create_zero_seed_router()
    if router is None:
        print("❌ FAILED: Router creation failed (FastAPI not available?)")
        return False

    # Find the endpoint function
    for route in router.routes:
        if hasattr(route, 'path') and '/analysis' in route.path:
            endpoint = route.endpoint
            break
    else:
        print("❌ FAILED: Could not find analysis endpoint")
        return False

    # Call with mock data (use_llm=False)
    try:
        response = await endpoint(node_id="test-node-001", use_llm=False)
        print(f"✓ Got response for node: {response.node_id}")
        print(f"  Categorical: {response.categorical.status} - {response.categorical.summary[:60]}...")
        print(f"  Epistemic: {response.epistemic.status} - {response.epistemic.summary[:60]}...")
        print(f"  Dialectical: {response.dialectical.status} - {response.dialectical.summary[:60]}...")
        print(f"  Generative: {response.generative.status} - {response.generative.summary[:60]}...")
        print("✓ Mock analysis endpoint works!")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_analysis():
    """Test LLM-backed analysis endpoint."""
    print("\n" + "=" * 80)
    print("TEST 2: LLM Analysis (use_llm=true)")
    print("=" * 80)

    from agents.k.llm import has_llm_credentials

    if not has_llm_credentials():
        print("⚠ SKIPPED: No ANTHROPIC_API_KEY found")
        return True

    from protocols.api.zero_seed import create_zero_seed_router

    router = create_zero_seed_router()
    if router is None:
        print("❌ FAILED: Router creation failed")
        return False

    # Find the endpoint function
    for route in router.routes:
        if hasattr(route, 'path') and '/analysis' in route.path:
            endpoint = route.endpoint
            break
    else:
        print("❌ FAILED: Could not find analysis endpoint")
        return False

    # Test with a real spec file
    spec_path = "spec/protocols/witness"  # Will become spec/protocols/witness.md

    try:
        print(f"Analyzing spec: {spec_path}.md")
        print("(This will make a real LLM call and may take 10-30 seconds...)")

        response = await endpoint(node_id=spec_path, use_llm=True)

        print(f"\n✓ Got LLM analysis for: {response.node_id}")
        print(f"\nCategorical ({response.categorical.status}):")
        print(f"  {response.categorical.summary}")
        print(f"  Items: {len(response.categorical.items)}")
        for item in response.categorical.items[:3]:
            print(f"    - {item.label}: {item.value[:60]}... [{item.status}]")

        print(f"\nEpistemic ({response.epistemic.status}):")
        print(f"  {response.epistemic.summary}")
        print(f"  Items: {len(response.epistemic.items)}")
        for item in response.epistemic.items[:3]:
            print(f"    - {item.label}: {item.value} [{item.status}]")

        print(f"\nDialectical ({response.dialectical.status}):")
        print(f"  {response.dialectical.summary}")
        print(f"  Items: {len(response.dialectical.items)}")

        print(f"\nGenerative ({response.generative.status}):")
        print(f"  {response.generative.summary}")
        print(f"  Items: {len(response.generative.items)}")
        for item in response.generative.items[:3]:
            print(f"    - {item.label}: {item.value} [{item.status}]")

        print("\n✓ LLM analysis endpoint works!")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_transformation():
    """Test that transformation preserves data structure."""
    print("\n" + "=" * 80)
    print("TEST 3: FullAnalysisReport → NodeAnalysisResponse Transformation")
    print("=" * 80)

    from agents.k.llm import has_llm_credentials

    if not has_llm_credentials():
        print("⚠ SKIPPED: No ANTHROPIC_API_KEY found")
        return True

    try:
        from agents.k.llm import create_llm_client
        from protocols.api.zero_seed import _transform_analysis_report
        from services.analysis import AnalysisService

        # Create service
        llm = create_llm_client()
        service = AnalysisService(llm)

        # Use a small spec file for quick test
        spec_path = "spec/agents/poly.md"

        print(f"Running analysis on: {spec_path}")
        report = await service.analyze_full(spec_path)

        print("\n✓ Got FullAnalysisReport:")
        print(f"  Target: {report.target}")
        print(f"  Categorical: {report.categorical.laws_total} laws, {report.categorical.laws_passed} passed")
        print(f"  Epistemic: Layer {report.epistemic.layer}, Grounded={report.epistemic.is_grounded}")
        print(f"  Dialectical: {len(report.dialectical.tensions)} tensions")
        print(f"  Generative: Ratio={report.generative.compression_ratio:.2f}, Regenerable={report.generative.is_regenerable}")

        # Transform
        response = _transform_analysis_report("test-node", report)

        print("\n✓ Transformed to NodeAnalysisResponse:")
        print(f"  Node ID: {response.node_id}")
        print(f"  Categorical: {len(response.categorical.items)} items")
        print(f"  Epistemic: {len(response.epistemic.items)} items")
        print(f"  Dialectical: {len(response.dialectical.items)} items")
        print(f"  Generative: {len(response.generative.items)} items")

        # Verify structure
        assert response.node_id == "test-node"
        assert response.categorical.status in ["pass", "issues", "unknown"]
        assert response.epistemic.status in ["pass", "issues", "unknown"]
        assert response.dialectical.status in ["pass", "issues", "unknown"]
        assert response.generative.status in ["pass", "issues", "unknown"]

        print("\n✓ Transformation preserves data structure!")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("Testing Zero Seed Analysis API Integration")
    print("=" * 80)

    tests = [
        ("Mock Analysis", test_mock_analysis),
        ("LLM Analysis", test_llm_analysis),
        ("Transformation", test_transformation),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = await test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(r for _, r in results)
    print("\n" + ("✓ All tests passed!" if all_passed else "❌ Some tests failed"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
