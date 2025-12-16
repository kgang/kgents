"""
Market Day: An Emergence Scenario.

It's the weekly market day in the town square. Vendors,
performers, and visitors create a dynamic social space
where anything can happen. No fixed plot - just people
and possibilities.

ScenarioType: EMERGENCE
Difficulty: Easy
Duration: ~20 minutes (open-ended)

Design:
- Open-ended: No predetermined outcome
- Emergent: Interactions create unexpected patterns
- Exploratory: Participants discover the space
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
    EXCHANGE,
    EXPLORATION,
    GATHERING,
    HEALING,
    MEMORY,
    Eigenvectors,
)

# =============================================================================
# Citizen Specs
# =============================================================================

BAKER = CitizenSpec(
    name="Emilia Rossi",
    archetype="Builder",
    region="market_square",
    eigenvectors=Eigenvectors(
        warmth=0.9,
        curiosity=0.5,
        trust=0.7,
        creativity=0.6,
        patience=0.7,
        resilience=0.6,
        ambition=0.4,
    ),
    cosmotechnics=GATHERING,
    backstory="Town baker known for her warmth and gossip. "
    "Her stall is where everyone gathers for news.",
    metadata={
        "role": "vendor",
        "specialty": "social_hub",
        "mood": "cheerful",
    },
)

TRAVELER = CitizenSpec(
    name="Sage",
    archetype="Scholar",
    region="market_square",
    eigenvectors=Eigenvectors(
        warmth=0.5,
        curiosity=0.95,
        trust=0.4,
        creativity=0.7,
        patience=0.5,
        resilience=0.7,
        ambition=0.3,
    ),
    cosmotechnics=EXPLORATION,
    backstory="Mysterious traveler from distant lands. "
    "Speaks little but observes everything. Sells curiosities.",
    metadata={
        "role": "visitor",
        "specialty": "knowledge_broker",
        "mood": "enigmatic",
    },
)

PERFORMER = CitizenSpec(
    name="Zephyr the Juggler",
    archetype="Healer",
    region="fountain_plaza",
    eigenvectors=Eigenvectors(
        warmth=0.8,
        curiosity=0.6,
        trust=0.6,
        creativity=0.9,
        patience=0.4,
        resilience=0.5,
        ambition=0.7,
    ),
    cosmotechnics=GATHERING,
    backstory="Street performer who draws crowds. "
    "Uses humor and spectacle to brighten the day.",
    metadata={
        "role": "entertainer",
        "specialty": "crowd_gatherer",
        "mood": "playful",
    },
)

HERBALIST = CitizenSpec(
    name="Old Mira",
    archetype="Healer",
    region="herb_corner",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.6,
        trust=0.5,
        creativity=0.7,
        patience=0.9,
        resilience=0.8,
        ambition=0.2,
    ),
    cosmotechnics=HEALING,
    backstory="Village herbalist who knows everyone's ailments. "
    "People come for remedies but stay for advice.",
    metadata={
        "role": "vendor",
        "specialty": "counselor",
        "mood": "serene",
    },
)

CHILD = CitizenSpec(
    name="Little Pip",
    archetype="Scholar",
    region="market_square",
    eigenvectors=Eigenvectors(
        warmth=0.7,
        curiosity=0.95,
        trust=0.9,
        creativity=0.8,
        patience=0.2,
        resilience=0.4,
        ambition=0.5,
    ),
    cosmotechnics=EXPLORATION,
    backstory="Curious child who runs through the market. "
    "Notices things adults miss. Always asking questions.",
    metadata={
        "role": "wanderer",
        "specialty": "catalyst",
        "mood": "excited",
    },
)

STORYTELLER = CitizenSpec(
    name="Grandmother Oak",
    archetype="Watcher",
    region="shade_tree",
    eigenvectors=Eigenvectors(
        warmth=0.8,
        curiosity=0.5,
        trust=0.7,
        creativity=0.8,
        patience=0.9,
        resilience=0.9,
        ambition=0.1,
    ),
    cosmotechnics=MEMORY,
    backstory="Ancient storyteller who sits under the oak tree. "
    "Tells tales that seem like fiction but aren't.",
    metadata={
        "role": "storyteller",
        "specialty": "memory_keeper",
        "mood": "contemplative",
    },
)


# =============================================================================
# Scenario Template
# =============================================================================

MARKET_DAY = ScenarioTemplate(
    name="Market Day",
    scenario_type=ScenarioType.EMERGENCE,
    description="""
The sun rises on another market day in the town square.
Vendors arrange their wares, performers warm up, and
the aroma of fresh bread fills the air.

There is no mystery to solve, no bridge to build,
no dispute to resolve. Just a living, breathing
market where people meet, trade, laugh, and live.

What happens next is up to you. Follow the child.
Listen to the storyteller. Buy something curious
from the traveler. Or simply sit and watch.

The market creates its own stories.
    """.strip(),
    citizens=[BAKER, TRAVELER, PERFORMER, HERBALIST, CHILD, STORYTELLER],
    regions=[
        "market_square",
        "fountain_plaza",
        "herb_corner",
        "shade_tree",
        "vendor_row",
        "alley_shortcuts",
    ],
    trigger=TriggerCondition.immediate(),
    success_criteria=SuccessCriteria(
        require_all=False,  # Any outcome is valid
        criteria=[
            SuccessCriterion(
                kind="time_elapsed",
                description="Spend time in the market (emergent scenario)",
                params={"min_seconds": 600},  # 10 minutes
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="Have meaningful interactions",
                params={"required_pairs": []},  # Empty - any interactions count
            ),
        ],
    ),
    tags=["emergence", "sandbox", "exploration", "slice-of-life", "social"],
    difficulty="easy",
    estimated_duration_minutes=20,
    polynomial_config={
        "phases": ["morning", "midday", "afternoon", "evening"],
        "valid_transitions": [
            ("morning", "midday"),
            ("midday", "afternoon"),
            ("afternoon", "evening"),
            # Can also jump back for non-linear exploration
            ("midday", "morning"),
            ("afternoon", "midday"),
        ],
    },
)


__all__ = ["MARKET_DAY"]
