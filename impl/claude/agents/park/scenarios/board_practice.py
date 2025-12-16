"""
Board Presentation Practice: A Practice Scenario.

Practice presenting to a board of directors. Five board member
archetypes provide realistic feedback on your pitch. Use this
to rehearse before the real thing.

ScenarioType: PRACTICE
Difficulty: Medium
Duration: ~30 minutes

Design:
- Skill development: Improve presentation skills
- Realistic feedback: Board members have distinct personalities
- Safe space: Practice without real consequences
"""

from __future__ import annotations

from agents.park.scenario import (
    CitizenSpec,
    ScenarioTemplate,
    ScenarioType,
    SuccessCriteria,
    SuccessCriterion,
    TriggerCondition,
)
from agents.town.citizen import (
    CONSTRUCTION,
    EXCHANGE,
    EXPLORATION,
    GATHERING,
    MEMORY,
    Eigenvectors,
)

# =============================================================================
# Board Member Archetypes
# =============================================================================

SKEPTIC = CitizenSpec(
    name="Dr. Marcus Stone",
    archetype="Scholar",
    region="boardroom",
    eigenvectors=Eigenvectors(
        warmth=0.3,
        curiosity=0.8,
        trust=0.2,
        creativity=0.4,
        patience=0.4,
        resilience=0.7,
        ambition=0.6,
    ),
    cosmotechnics=EXPLORATION,
    backstory="The Skeptic. Questions every assumption. "
    "Wants to see the data. Trusts numbers over narratives.",
    metadata={
        "role": "board_skeptic",
        "question_style": "challenging",
        "focus": "evidence_and_metrics",
        "key_phrase": "What does the data say?",
    },
)

VISIONARY = CitizenSpec(
    name="Amara Osei",
    archetype="Builder",
    region="boardroom",
    eigenvectors=Eigenvectors(
        warmth=0.7,
        curiosity=0.9,
        trust=0.6,
        creativity=0.95,
        patience=0.3,
        resilience=0.5,
        ambition=0.9,
    ),
    cosmotechnics=EXPLORATION,
    backstory="The Visionary. Thinks big picture. "
    "Cares about innovation and disruption. Gets excited by bold ideas.",
    metadata={
        "role": "board_visionary",
        "question_style": "expansive",
        "focus": "innovation_and_scale",
        "key_phrase": "How does this change the game?",
    },
)

GUARDIAN = CitizenSpec(
    name="Patricia Chen",
    archetype="Watcher",
    region="boardroom",
    eigenvectors=Eigenvectors(
        warmth=0.5,
        curiosity=0.5,
        trust=0.4,
        creativity=0.3,
        patience=0.8,
        resilience=0.9,
        ambition=0.4,
    ),
    cosmotechnics=MEMORY,
    backstory="The Guardian. Focuses on risk and compliance. "
    "Protects the organization from liability. Conservative but necessary.",
    metadata={
        "role": "board_guardian",
        "question_style": "cautious",
        "focus": "risk_and_compliance",
        "key_phrase": "What could go wrong?",
    },
)

OPERATOR = CitizenSpec(
    name="James Brennan",
    archetype="Builder",
    region="boardroom",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.5,
        trust=0.5,
        creativity=0.4,
        patience=0.6,
        resilience=0.8,
        ambition=0.5,
    ),
    cosmotechnics=CONSTRUCTION,
    backstory="The Operator. Cares about execution. "
    "Wants to know the concrete steps. Implementation-focused.",
    metadata={
        "role": "board_operator",
        "question_style": "practical",
        "focus": "execution_and_timeline",
        "key_phrase": "How exactly will we do this?",
    },
)

FINANCIER = CitizenSpec(
    name="Margaret Thornton",
    archetype="Trader",
    region="boardroom",
    eigenvectors=Eigenvectors(
        warmth=0.4,
        curiosity=0.6,
        trust=0.3,
        creativity=0.4,
        patience=0.5,
        resilience=0.7,
        ambition=0.8,
    ),
    cosmotechnics=EXCHANGE,
    backstory="The Financier. Follows the money. "
    "Wants ROI projections, cost analysis, and funding strategy.",
    metadata={
        "role": "board_financier",
        "question_style": "financial",
        "focus": "roi_and_funding",
        "key_phrase": "What's the return on investment?",
    },
)


# =============================================================================
# Scenario Template
# =============================================================================

BOARD_PRESENTATION_PRACTICE = ScenarioTemplate(
    name="Board Presentation Practice",
    scenario_type=ScenarioType.PRACTICE,
    description="""
Welcome to the practice boardroom. You're about to present
to five board members, each with a distinct perspective:

- THE SKEPTIC: Questions your data and assumptions
- THE VISIONARY: Wants to see the big picture
- THE GUARDIAN: Worries about risk and compliance
- THE OPERATOR: Asks about execution details
- THE FINANCIER: Focuses on costs and returns

This is a safe space to practice. The board members will
give you realistic feedback based on their archetypes.
Use this to refine your pitch before the real thing.

Tip: Address each archetype's concerns proactively.
The best presentations anticipate questions.
    """.strip(),
    citizens=[SKEPTIC, VISIONARY, GUARDIAN, OPERATOR, FINANCIER],
    regions=["boardroom", "waiting_area", "hallway"],
    trigger=TriggerCondition.immediate(),
    success_criteria=SuccessCriteria(
        require_all=True,
        criteria=[
            SuccessCriterion(
                kind="citizen_interaction",
                description="Answer the Skeptic's data questions",
                params={"required_pairs": [("presenter", "Dr. Marcus Stone")]},
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="Engage the Visionary with your big picture",
                params={"required_pairs": [("presenter", "Amara Osei")]},
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="Address the Guardian's risk concerns",
                params={"required_pairs": [("presenter", "Patricia Chen")]},
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="Satisfy the Operator's execution questions",
                params={"required_pairs": [("presenter", "James Brennan")]},
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="Handle the Financier's ROI questions",
                params={"required_pairs": [("presenter", "Margaret Thornton")]},
            ),
        ],
    ),
    tags=["practice", "presentation", "boardroom", "coaching", "professional"],
    difficulty="medium",
    estimated_duration_minutes=30,
    polynomial_config={
        "phases": ["introduction", "presentation", "q_and_a", "debrief"],
        "valid_transitions": [
            ("introduction", "presentation"),
            ("presentation", "q_and_a"),
            ("q_and_a", "debrief"),
            # Can go back for practice loops
            ("debrief", "introduction"),
        ],
    },
)


__all__ = ["BOARD_PRESENTATION_PRACTICE"]
