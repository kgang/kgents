"""
Constitutional Reward System - Usage Examples

Demonstrates constitutional scoring across all four domains.

Run:
    uv run python services/constitutional/example_usage.py
"""

from services.constitutional import Domain, Principle, PrincipleScore, constitutional_reward


def print_score(domain: str, action: str, score: PrincipleScore):
    """Pretty print a constitutional score."""
    print(f"\n{'='*60}")
    print(f"Domain: {domain.upper()}")
    print(f"Action: {action}")
    print(f"{'='*60}")
    print(f"  TASTEFUL:      {score.tasteful:.2f}")
    print(f"  CURATED:       {score.curated:.2f}")
    print(f"  ETHICAL:       {score.ethical:.2f}")
    print(f"  JOY_INDUCING:  {score.joy_inducing:.2f}")
    print(f"  COMPOSABLE:    {score.composable:.2f}")
    print(f"  HETERARCHICAL: {score.heterarchical:.2f}")
    print(f"  GENERATIVE:    {score.generative:.2f}")
    print(f"  ---")
    print(f"  WEIGHTED TOTAL: {score.weighted_total():.2f} / 8.7")


def chat_examples():
    """Chat domain examples."""
    from services.chat.evidence import TurnResult

    print("\n" + "="*60)
    print("CHAT DOMAIN EXAMPLES")
    print("="*60)

    # Perfect turn
    result = TurnResult(
        response="This is a thoughtful, well-crafted response!",
        tools=[],
        tools_passed=True,
    )
    context = {"turn_result": result, "has_mutations": False}
    score = constitutional_reward("send_message", context, "chat")
    print_score("chat", "Perfect turn (no mutations, good response)", score)

    # Turn with mutations
    result = TurnResult(
        response="Done!",
        tools=[{"name": "edit_file"}],
        tools_passed=True,
    )
    context = {"turn_result": result, "has_mutations": True}
    score = constitutional_reward("send_message", context, "chat")
    print_score("chat", "Turn with acknowledged mutations", score)

    # Turn with too many tools
    result = TurnResult(
        response="Completed complex task",
        tools=[{"name": f"tool_{i}"} for i in range(10)],
        tools_passed=True,
    )
    context = {"turn_result": result, "has_mutations": False}
    score = constitutional_reward("send_message", context, "chat")
    print_score("chat", "Turn with 10 tools (poor composition)", score)


def navigation_examples():
    """Navigation domain examples."""
    print("\n" + "="*60)
    print("NAVIGATION DOMAIN EXAMPLES")
    print("="*60)

    # Derivation navigation
    context = {"nav_type": "derivation"}
    score = constitutional_reward("navigate", context, "navigation")
    print_score("navigation", "Derivation navigation (following proof)", score)

    # Loss gradient navigation
    context = {"nav_type": "loss_gradient"}
    score = constitutional_reward("navigate", context, "navigation")
    print_score("navigation", "Loss gradient navigation (seeking truth)", score)

    # Direct jump
    context = {"nav_type": "direct_jump"}
    score = constitutional_reward("navigate", context, "navigation")
    print_score("navigation", "Direct jump (intentional but breaks flow)", score)


def portal_examples():
    """Portal domain examples."""
    print("\n" + "="*60)
    print("PORTAL DOMAIN EXAMPLES")
    print("="*60)

    # Deep expansion with evidence
    context = {"depth": 3, "edge_type": "evidence", "expansion_count": 2}
    score = constitutional_reward("expand_portal", context, "portal")
    print_score("portal", "Deep expansion (depth=3) with evidence edge", score)

    # Too many expansions
    context = {"depth": 1, "edge_type": "", "expansion_count": 10}
    score = constitutional_reward("expand_portal", context, "portal")
    print_score("portal", "Too many expansions (sprawl warning)", score)


def edit_examples():
    """Edit domain examples."""
    print("\n" + "="*60)
    print("EDIT DOMAIN EXAMPLES")
    print("="*60)

    # Small spec-aligned change
    context = {"lines_changed": 20, "spec_aligned": True}
    score = constitutional_reward("edit_file", context, "edit")
    print_score("edit", "Small spec-aligned change (20 lines)", score)

    # Large non-aligned change
    context = {"lines_changed": 300, "spec_aligned": False}
    score = constitutional_reward("edit_file", context, "edit")
    print_score("edit", "Large change (300 lines, not spec-aligned)", score)


def serialization_example():
    """Demonstrate serialization."""
    print("\n" + "="*60)
    print("SERIALIZATION EXAMPLE")
    print("="*60)

    context = {"nav_type": "derivation"}
    score = constitutional_reward("navigate", context, "navigation")

    # Serialize
    data = score.to_dict()
    print("\nSerialized to dict:")
    for key, value in data.items():
        print(f"  {key}: {value:.2f}")

    # Deserialize
    restored = PrincipleScore.from_dict(data)
    print("\nDeserialized successfully:")
    print(f"  ETHICAL: {restored.ethical:.2f}")
    print(f"  GENERATIVE: {restored.generative:.2f}")


def backward_compatibility_example():
    """Demonstrate backward compatibility with chat."""
    print("\n" + "="*60)
    print("BACKWARD COMPATIBILITY")
    print("="*60)

    from services.chat.evidence import TurnResult
    from services.chat.reward import constitutional_reward as chat_reward

    result = TurnResult(response="Great!", tools=[])

    # Old way (still works)
    score = chat_reward("send_message", result, has_mutations=False)
    print("\nUsing services.chat.reward (old way):")
    print(f"  ETHICAL: {score.ethical:.2f}")
    print(f"  JOY_INDUCING: {score.joy_inducing:.2f}")

    # New way (equivalent)
    context = {"turn_result": result, "has_mutations": False}
    score2 = constitutional_reward("send_message", context, "chat")
    print("\nUsing services.constitutional (new way):")
    print(f"  ETHICAL: {score2.ethical:.2f}")
    print(f"  JOY_INDUCING: {score2.joy_inducing:.2f}")

    print("\n✓ Both methods produce identical results")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("CONSTITUTIONAL REWARD SYSTEM - USAGE EXAMPLES")
    print("="*60)

    chat_examples()
    navigation_examples()
    portal_examples()
    edit_examples()
    serialization_example()
    backward_compatibility_example()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("\n✓ Chat domain: TurnResult-based scoring")
    print("✓ Navigation domain: nav_type-based scoring")
    print("✓ Portal domain: depth/edge_type/expansion_count scoring")
    print("✓ Edit domain: lines_changed/spec_aligned scoring")
    print("✓ All domains use same PrincipleScore type")
    print("✓ Backward compatibility maintained")
    print("\nSee services/constitutional/README.md for full documentation")
    print("See services/constitutional/QUICK_REF.md for quick reference\n")


if __name__ == "__main__":
    main()
