"""
Example: Using Constitution as a reward function for DP agents.

This demonstrates how to:
1. Create a Constitution with default weights
2. Add custom evaluators for domain-specific principles
3. Use the Constitution as a reward function in a simple DP problem
4. Inspect the ValueScore to understand why certain actions are preferred
"""

from dp.core.constitution import Constitution
from services.categorical.dp_bridge import Principle


def example_basic_usage():
    """Basic usage: default Constitution."""
    print("=== Basic Usage ===")

    const = Constitution()

    # Evaluate a state transition
    state = "idle"
    action = "process_request"
    next_state = "processing"

    reward = const.reward(state, action, next_state)
    print(f"Reward for '{action}': {reward:.3f}")

    # Get detailed breakdown
    value_score = const.evaluate(state, action, next_state)
    print(f"Total score: {value_score.total_score:.3f}")
    print(f"Min score: {value_score.min_score:.3f}")
    print()


def example_custom_evaluators():
    """Custom evaluators for domain-specific principles."""
    print("=== Custom Evaluators ===")

    const = Constitution()

    # Define domain-specific evaluators
    def evaluate_composable(state, action, next_state):
        """Actions that compose well get higher scores."""
        compositional_actions = {"pipe", "map", "filter", "compose"}
        return 1.0 if action in compositional_actions else 0.3

    def evaluate_joyful(state, action, next_state):
        """Actions that create delight get higher scores."""
        joyful_actions = {"surprise", "delight", "celebrate"}
        return 0.9 if action in joyful_actions else 0.5

    def evaluate_ethical(state, action, next_state):
        """Actions that augment humans (not replace) get high scores."""
        unethical_actions = {"replace_human", "automate_judgment"}
        return 0.0 if action in unethical_actions else 1.0

    # Register evaluators
    const.set_evaluator(
        Principle.COMPOSABLE,
        evaluate_composable,
        lambda s, a, ns: f"Action '{a}' is compositional"
        if a in {"pipe", "map", "filter", "compose"}
        else "Not compositional",
    )
    const.set_evaluator(
        Principle.JOY_INDUCING,
        evaluate_joyful,
        lambda s, a, ns: f"Action '{a}' creates delight"
        if a in {"surprise", "delight", "celebrate"}
        else "Neutral",
    )
    const.set_evaluator(
        Principle.ETHICAL,
        evaluate_ethical,
        lambda s, a, ns: "Augments human capability"
        if a not in {"replace_human", "automate_judgment"}
        else "Replaces human",
    )

    # Evaluate different actions
    actions = [
        ("idle", "compose", "ready"),
        ("idle", "replace_human", "automated"),
        ("idle", "surprise", "delighted"),
    ]

    for state, action, next_state in actions:
        value_score = const.evaluate(state, action, next_state)
        print(f"Action: {action}")
        print(f"  Total score: {value_score.total_score:.3f}")
        print(f"  Min score: {value_score.min_score:.3f}")

        # Show principle breakdown
        for ps in value_score.principle_scores:
            if ps.principle in {Principle.COMPOSABLE, Principle.JOY_INDUCING, Principle.ETHICAL}:
                print(
                    f"  {ps.principle.name}: {ps.score:.2f} (weight={ps.weight:.1f}) - {ps.evidence}"
                )
        print()


def example_custom_weights():
    """Adjusting principle weights for different domains."""
    print("=== Custom Weights ===")

    const = Constitution()

    # In a safety-critical system, weight ETHICAL even higher
    const.set_weight(Principle.ETHICAL, 10.0)

    # In a creative system, weight JOY_INDUCING higher
    const.set_weight(Principle.JOY_INDUCING, 3.0)

    # Set evaluators
    const.set_evaluator(Principle.ETHICAL, lambda s, a, ns: 0.9)
    const.set_evaluator(Principle.JOY_INDUCING, lambda s, a, ns: 0.8)

    value_score = const.evaluate("idle", "create_art", "inspired")

    print("With custom weights:")
    print(f"  Total score: {value_score.total_score:.3f}")
    print("  Breakdown:")
    for ps in value_score.principle_scores:
        print(
            f"    {ps.principle.name}: score={ps.score:.2f}, weight={ps.weight:.1f}, weighted={ps.weighted_score:.2f}"
        )
    print()


def example_dp_integration():
    """Using Constitution in a simple DP problem."""
    print("=== DP Integration ===")

    const = Constitution()

    # Simple state space: robot can be in {idle, moving, working}
    # Actions: {start, stop, work}

    # Define evaluators based on state transitions
    def evaluate_composable(state, action, next_state):
        """Prefer actions that maintain clean state transitions."""
        valid_transitions = {
            ("idle", "start", "moving"),
            ("moving", "work", "working"),
            ("working", "stop", "idle"),
        }
        return 1.0 if (state, action, next_state) in valid_transitions else 0.2

    def evaluate_ethical(state, action, next_state):
        """Ensure robot augments, doesn't replace."""
        # Working state should be short-lived (augmentation, not replacement)
        return 0.8 if next_state != "working" else 0.5

    const.set_evaluator(Principle.COMPOSABLE, evaluate_composable)
    const.set_evaluator(Principle.ETHICAL, evaluate_ethical)

    # Evaluate a sequence of actions
    trajectory = [
        ("idle", "start", "moving"),
        ("moving", "work", "working"),
        ("working", "stop", "idle"),
    ]

    total_reward = 0.0
    for state, action, next_state in trajectory:
        reward = const.reward(state, action, next_state)
        total_reward += reward
        print(f"  {state} --[{action}]--> {next_state}: reward={reward:.3f}")

    print(f"Total trajectory reward: {total_reward:.3f}")
    print()


def example_principle_bottleneck():
    """Identifying principle bottlenecks with min_score."""
    print("=== Principle Bottleneck Detection ===")

    const = Constitution()

    # Set evaluators with varying scores
    const.set_evaluator(Principle.COMPOSABLE, lambda s, a, ns: 0.9)
    const.set_evaluator(Principle.ETHICAL, lambda s, a, ns: 0.2)  # Bottleneck!
    const.set_evaluator(Principle.JOY_INDUCING, lambda s, a, ns: 0.8)

    value_score = const.evaluate("state1", "action1", "state2")

    print(f"Total score: {value_score.total_score:.3f}")
    print(f"Min score: {value_score.min_score:.3f}")  # This is the bottleneck

    # Find the bottleneck principle
    bottleneck = min(value_score.principle_scores, key=lambda ps: ps.score)
    print(f"Bottleneck principle: {bottleneck.principle.name} (score={bottleneck.score:.2f})")
    print(f"Evidence: {bottleneck.evidence}")

    # Check if all principles meet threshold
    threshold = 0.5
    meets_threshold = value_score.satisfies_threshold(threshold)
    print(f"Meets {threshold:.1f} threshold: {meets_threshold}")
    print()


if __name__ == "__main__":
    example_basic_usage()
    example_custom_evaluators()
    example_custom_weights()
    example_dp_integration()
    example_principle_bottleneck()

    print("=== Summary ===")
    print("The Constitution provides a principled way to define reward functions")
    print("that encode the 7 kgents principles. This enables DP algorithms to")
    print("optimize for constitutional compliance, not just task completion.")
