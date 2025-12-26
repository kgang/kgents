#!/usr/bin/env python3
"""
Example usage of Constitutional Reward system.

Run:
    uv run python services/chat/example_reward_usage.py
"""

from __future__ import annotations

from services.chat.evidence import TurnResult
from services.chat.reward import Principle, PrincipleScore, constitutional_reward


def main() -> None:
    """Demonstrate Constitutional Reward usage."""
    print("=" * 80)
    print("Constitutional Reward System - Examples")
    print("=" * 80)
    print()

    # Example 1: Perfect Turn
    print("1. PERFECT TURN")
    print("-" * 80)
    result = TurnResult(
        response="I've analyzed the code and found three optimization opportunities.",
        tools=[],
        tools_passed=True,
    )
    score = constitutional_reward("send_message", result, has_mutations=False)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: No")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}")
    print(f"  Composable:    {score.composable:.2f}")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7")
    print()

    # Example 2: Acknowledged Mutations
    print("2. ACKNOWLEDGED MUTATIONS")
    print("-" * 80)
    result = TurnResult(
        response="I've successfully updated the file with the new configuration.",
        tools=[{"name": "write_file", "status": "success"}],
        tools_passed=True,
    )
    score = constitutional_reward("send_message", result, has_mutations=True)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: Yes (acknowledged)")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}  ← Lower (mutations)")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}")
    print(f"  Composable:    {score.composable:.2f}")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7")
    print()

    # Example 3: Unacknowledged Mutations
    print("3. UNACKNOWLEDGED MUTATIONS")
    print("-" * 80)
    result = TurnResult(
        response="Done.",
        tools=[{"name": "write_file", "status": "failed"}],
        tools_passed=False,
    )
    score = constitutional_reward("send_message", result, has_mutations=True)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: Yes (unacknowledged)")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}  ← Much lower (unacknowledged)")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}  ← Lower (short response)")
    print(f"  Composable:    {score.composable:.2f}")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7")
    print()

    # Example 4: Too Many Tools
    print("4. TOO MANY TOOLS")
    print("-" * 80)
    result = TurnResult(
        response="I've completed all the operations you requested.",
        tools=[{"name": f"tool_{i}", "status": "success"} for i in range(10)],
        tools_passed=True,
    )
    score = constitutional_reward("send_message", result, has_mutations=False)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: No")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}")
    print(f"  Composable:    {score.composable:.2f}  ← Lower (too many tools)")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7")
    print()

    # Example 5: Short Response
    print("5. SHORT RESPONSE")
    print("-" * 80)
    result = TurnResult(
        response="OK",
        tools=[],
        tools_passed=True,
    )
    score = constitutional_reward("send_message", result, has_mutations=False)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: No")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}  ← Lower (too short)")
    print(f"  Composable:    {score.composable:.2f}")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7")
    print()

    # Example 6: Multiple Violations
    print("6. MULTIPLE VIOLATIONS")
    print("-" * 80)
    result = TurnResult(
        response="OK",
        tools=[{"name": f"tool_{i}", "status": "failed"} for i in range(10)],
        tools_passed=False,
    )
    score = constitutional_reward("send_message", result, has_mutations=True)
    print(f"Response: {result.response}")
    print(f"Tools: {len(result.tools)}")
    print("Mutations: Yes (unacknowledged)")
    print()
    print("Scores:")
    print(f"  Tasteful:      {score.tasteful:.2f}")
    print(f"  Curated:       {score.curated:.2f}")
    print(f"  Ethical:       {score.ethical:.2f}  ← VIOLATION")
    print(f"  Joy-Inducing:  {score.joy_inducing:.2f}  ← VIOLATION")
    print(f"  Composable:    {score.composable:.2f}  ← VIOLATION")
    print(f"  Heterarchical: {score.heterarchical:.2f}")
    print(f"  Generative:    {score.generative:.2f}")
    print(f"  Weighted Total: {score.weighted_total():.2f} / 8.7  ← DEGRADED")
    print()

    # Example 7: Custom Weights
    print("7. CUSTOM WEIGHTS")
    print("-" * 80)
    score = PrincipleScore(ethical=0.8, composable=0.9)
    print("Using custom weights:")
    custom_weights = {
        Principle.ETHICAL: 3.0,  # Extra weight on ethics
        Principle.COMPOSABLE: 2.0,  # Extra weight on composition
        Principle.JOY_INDUCING: 0.5,  # Less weight on joy
    }
    print("  ETHICAL: 3.0 (default: 2.0)")
    print("  COMPOSABLE: 2.0 (default: 1.5)")
    print("  JOY_INDUCING: 0.5 (default: 1.2)")
    print()
    default_total = score.weighted_total()
    custom_total = score.weighted_total(custom_weights)
    print(f"Default weighted total: {default_total:.2f}")
    print(f"Custom weighted total:  {custom_total:.2f}")
    print()

    # Example 8: Serialization
    print("8. SERIALIZATION")
    print("-" * 80)
    score = PrincipleScore(ethical=0.8, composable=0.9, joy_inducing=0.7)
    print("Original score:")
    print(f"  {score}")
    print()
    data = score.to_dict()
    print("Serialized to dict:")
    print(f"  {data}")
    print()
    restored = PrincipleScore.from_dict(data)
    print("Restored from dict:")
    print(f"  {restored}")
    print(f"  Match: {score.to_dict() == restored.to_dict()}")
    print()

    print("=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
