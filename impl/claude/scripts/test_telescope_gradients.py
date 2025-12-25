#!/usr/bin/env python
"""
Quick test to verify telescope endpoint returns comprehensive gradient data.

Run with:
    uv run python scripts/test_telescope_gradients.py
"""

import asyncio
import sys
from pathlib import Path

# Add impl/claude to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_telescope_gradients():
    """Test that telescope endpoint generates gradients for all visible nodes."""
    from protocols.api.zero_seed import create_zero_seed_router

    router = create_zero_seed_router()
    if not router:
        print("❌ Zero Seed router not available (FastAPI not installed)")
        return False

    # Find the get_telescope_state endpoint
    telescope_endpoint = None
    for route in router.routes:
        # Route path includes the prefix, so check for ending
        if route.path.endswith("/telescope"):
            if hasattr(route, 'methods') and "GET" in route.methods:
                telescope_endpoint = route.endpoint
                break
            elif hasattr(route, 'endpoint'):
                telescope_endpoint = route.endpoint
                break

    if not telescope_endpoint:
        print("❌ Telescope endpoint not found")
        print(f"Available routes: {[r.path for r in router.routes]}")
        return False

    # Call the endpoint directly
    response = await telescope_endpoint(focal_point=None, focal_distance=None)

    # Verify response structure
    print(f"\n✅ Telescope State:")
    print(f"   - Focal distance: {response.state.focal_distance}")
    print(f"   - Show gradient: {response.state.show_gradient}")
    print(f"   - Visible layers: {response.state.visible_layers}")

    print(f"\n✅ Visible Nodes: {len(response.visible_nodes)} total")
    layer_counts = {}
    for node in response.visible_nodes:
        layer_counts[node.layer] = layer_counts.get(node.layer, 0) + 1

    for layer in sorted(layer_counts.keys()):
        print(f"   - Layer {layer}: {layer_counts[layer]} nodes")

    print(f"\n✅ Gradients: {len(response.gradients)} total")

    # Analyze gradients
    zero_magnitude = 0
    nonzero_magnitude = 0
    max_magnitude = 0.0

    for node_id, gradient in response.gradients.items():
        if gradient.magnitude == 0:
            zero_magnitude += 1
        else:
            nonzero_magnitude += 1
            max_magnitude = max(max_magnitude, gradient.magnitude)

    print(f"   - Zero magnitude (fixed points): {zero_magnitude}")
    print(f"   - Non-zero magnitude: {nonzero_magnitude}")
    print(f"   - Max magnitude: {max_magnitude:.3f}")

    # Show sample gradients
    print(f"\n✅ Sample Gradients:")
    sample_count = 0
    for node_id, gradient in list(response.gradients.items())[:5]:
        node = next(n for n in response.visible_nodes if n.id == node_id)
        print(
            f"   - {node_id} (L{node.layer}): "
            f"mag={gradient.magnitude:.3f}, "
            f"vec=({gradient.x:.3f}, {gradient.y:.3f}), "
            f"target={gradient.target_node}"
        )
        sample_count += 1

    print(f"\n✅ Navigation Suggestions: {len(response.suggestions)}")
    for i, suggestion in enumerate(response.suggestions, 1):
        print(
            f"   {i}. {suggestion.action} → {suggestion.target} "
            f"(value={suggestion.value_score:.2f})"
        )
        print(f"      {suggestion.reasoning}")

    # Verify all nodes have gradients
    node_ids = {n.id for n in response.visible_nodes}
    gradient_ids = set(response.gradients.keys())

    if node_ids == gradient_ids:
        print(f"\n✅ All {len(node_ids)} nodes have gradient vectors")
    else:
        missing = node_ids - gradient_ids
        extra = gradient_ids - node_ids
        print(f"\n❌ Gradient mismatch:")
        if missing:
            print(f"   - Missing gradients for: {missing}")
        if extra:
            print(f"   - Extra gradients for: {extra}")
        return False

    print("\n✅ All checks passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_telescope_gradients())
    sys.exit(0 if success else 1)
