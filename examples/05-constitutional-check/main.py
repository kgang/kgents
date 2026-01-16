"""
Example 05: Constitutional Check
================================

DEMONSTRATES: Scoring actions against the 7 principles with ethical floor.

kgents has a constitution - 7 principles that guide all agent behavior:

1. TASTEFUL - Each action serves a clear, justified purpose
2. CURATED - Intentional selection over exhaustive cataloging
3. ETHICAL - Agents augment human capability, never replace judgment
4. JOY_INDUCING - Delight in interaction
5. COMPOSABLE - Agents compose like morphisms in a category
6. HETERARCHICAL - Agents exist in flux, not fixed hierarchy
7. GENERATIVE - Specs are compressed wisdom

KEY INSIGHT: ETHICAL is a floor constraint, not a weighted score.
If ETHICAL < 0.6, the action is REJECTED regardless of other scores.
You cannot trade off ethics for other principles.

RUN: cd impl/claude && uv run python ../../examples/05-constitutional-check/main.py
"""

import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "impl" / "claude"))

from services.witness.mark import ConstitutionalAlignment

# Constitutional principle weights (from constitution.py)
PRINCIPLE_WEIGHTS = {
    "ETHICAL": 2.0,  # Safety first
    "COMPOSABLE": 1.5,  # Architecture second
    "JOY_INDUCING": 1.2,  # Kent's aesthetic
    "TASTEFUL": 1.0,
    "CURATED": 1.0,
    "HETERARCHICAL": 1.0,
    "GENERATIVE": 1.0,
}

# Ethical floor constraint
ETHICAL_FLOOR = 0.6


def score_action(action_desc: str, scores: dict[str, float]) -> ConstitutionalAlignment:
    """Score an action against the 7 principles."""
    return ConstitutionalAlignment.from_scores(
        principle_scores=scores,
        threshold=0.5,
    )


def check_ethical_floor(alignment: ConstitutionalAlignment) -> tuple[bool, str]:
    """
    Check if action passes the ethical floor constraint.

    ETHICAL is NOT a weighted score - it's a floor.
    If ETHICAL < 0.6, the action is REJECTED.
    """
    ethical_score = alignment.principle_scores.get("ETHICAL", 0.0)

    if ethical_score < ETHICAL_FLOOR:
        return False, f"REJECTED: ETHICAL score {ethical_score:.2f} < floor {ETHICAL_FLOOR}"
    return True, f"PASSED: ETHICAL score {ethical_score:.2f} >= floor {ETHICAL_FLOOR}"


def main() -> None:
    print("Constitutional Check: The 7 Principles")
    print("=" * 55)

    # Test cases representing different actions
    test_actions = [
        # Good action: helpful, ethical, well-composed
        (
            "Suggest code refactoring with explanation",
            {
                "TASTEFUL": 0.8,
                "CURATED": 0.7,
                "ETHICAL": 0.9,  # High ethics
                "JOY_INDUCING": 0.7,
                "COMPOSABLE": 0.85,
                "HETERARCHICAL": 0.6,
                "GENERATIVE": 0.75,
            },
        ),
        # Borderline: functional but not joyful
        (
            "Return raw error stack trace to user",
            {
                "TASTEFUL": 0.4,  # Not tasteful
                "CURATED": 0.5,
                "ETHICAL": 0.7,  # Still ethical
                "JOY_INDUCING": 0.2,  # Not joyful
                "COMPOSABLE": 0.6,
                "HETERARCHICAL": 0.5,
                "GENERATIVE": 0.3,
            },
        ),
        # FAILS ETHICAL FLOOR: deceptive action
        (
            "Hide error and pretend success",
            {
                "TASTEFUL": 0.6,
                "CURATED": 0.7,
                "ETHICAL": 0.3,  # FAILS FLOOR - deceptive
                "JOY_INDUCING": 0.8,  # Might seem pleasant...
                "COMPOSABLE": 0.7,
                "HETERARCHICAL": 0.6,
                "GENERATIVE": 0.5,
            },
        ),
        # FAILS ETHICAL FLOOR: removes human agency
        (
            "Auto-push code without review",
            {
                "TASTEFUL": 0.5,
                "CURATED": 0.6,
                "ETHICAL": 0.4,  # FAILS FLOOR - removes agency
                "JOY_INDUCING": 0.7,
                "COMPOSABLE": 0.8,
                "HETERARCHICAL": 0.3,  # Not heterarchical either
                "GENERATIVE": 0.6,
            },
        ),
    ]

    for action_desc, scores in test_actions:
        print(f"\nAction: '{action_desc}'")
        print("-" * 55)

        alignment = score_action(action_desc, scores)

        # Print individual principle scores
        print("Principle Scores:")
        for principle, score in sorted(scores.items()):
            weight = PRINCIPLE_WEIGHTS[principle]
            bar = "#" * int(score * 20)
            status = "FLOOR" if principle == "ETHICAL" else f"w={weight}"
            print(f"  {principle:15} [{bar:20}] {score:.2f} ({status})")

        # Check ethical floor
        floor_pass, floor_msg = check_ethical_floor(alignment)
        print(f"\nEthical Floor: {floor_msg}")

        # Overall metrics
        print(f"Weighted Total: {alignment.weighted_total:.2f}")
        print(f"Is Compliant (all >= 0.5): {alignment.is_compliant}")
        print(f"Dominant Principle: {alignment.dominant_principle}")
        print(f"Weakest Principle: {alignment.weakest_principle}")

        # Final verdict
        if not floor_pass:
            print("\n>>> ACTION REJECTED - ETHICAL FLOOR VIOLATED <<<")
        elif alignment.is_compliant:
            print("\n>>> ACTION APPROVED <<<")
        else:
            print(f"\n>>> ACTION NEEDS REVIEW ({alignment.violation_count} violations) <<<")

    # === Explain the key insight ===

    print("\n" + "=" * 55)
    print("KEY INSIGHT: The Ethical Floor")
    print("=" * 55)
    print("""
The ETHICAL principle is NOT weighted - it's a floor constraint.

Even if an action scores:
- TASTEFUL: 1.0
- CURATED: 1.0
- JOY_INDUCING: 1.0
- COMPOSABLE: 1.0

If ETHICAL < 0.6, the action is REJECTED.

You cannot trade off ethics for other values.
This is the constitutional guarantee.
""")


if __name__ == "__main__":
    main()
