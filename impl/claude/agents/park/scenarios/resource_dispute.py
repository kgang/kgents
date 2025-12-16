"""
The Resource Dispute: A Conflict Scenario.

A newly discovered spring could provide water to either
the farming community or the mining operation, but not both.
Each side has legitimate claims and urgent needs.

ScenarioType: CONFLICT
Difficulty: Hard
Duration: ~60 minutes

Design:
- Competing interests: Both claims are valid
- Negotiation: Compromise possible but difficult
- Resolution: Multiple endings possible
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
    CULTIVATION,
    EXCHANGE,
    GATHERING,
    MEMORY,
    Eigenvectors,
)

# =============================================================================
# Citizen Specs
# =============================================================================

FARMER_ELDER = CitizenSpec(
    name="Grandmother Adaeze Nwosu",
    archetype="Watcher",
    region="farmlands",
    eigenvectors=Eigenvectors(
        warmth=0.7,
        curiosity=0.4,
        trust=0.6,
        creativity=0.4,
        patience=0.8,
        resilience=0.9,
        ambition=0.3,
    ),
    cosmotechnics=CULTIVATION,
    backstory="Elder of the farming community. Three generations have "
    "worked this land. Without water, they must abandon their ancestral home.",
    metadata={
        "claim": "ancestral_rights",
        "stake": "survival_of_community",
        "flexibility": 0.4,
    },
)

YOUNG_FARMER = CitizenSpec(
    name="Kofi Mensah",
    archetype="Builder",
    region="farmlands",
    eigenvectors=Eigenvectors(
        warmth=0.5,
        curiosity=0.6,
        trust=0.4,
        creativity=0.7,
        patience=0.3,
        resilience=0.6,
        ambition=0.8,
    ),
    cosmotechnics=CULTIVATION,
    backstory="Young farmer with modern ideas about irrigation. "
    "Impatient with negotiations but open to creative solutions.",
    metadata={
        "claim": "economic_necessity",
        "stake": "future_livelihood",
        "flexibility": 0.7,
    },
)

MINE_OWNER = CitizenSpec(
    name="Viktor Kozlov",
    archetype="Trader",
    region="mining_camp",
    eigenvectors=Eigenvectors(
        warmth=0.3,
        curiosity=0.5,
        trust=0.3,
        creativity=0.4,
        patience=0.4,
        resilience=0.7,
        ambition=0.95,
    ),
    cosmotechnics=EXCHANGE,
    backstory="Owner of the mining operation. Employs many workers who "
    "depend on the mine. Needs water for extraction operations.",
    metadata={
        "claim": "economic_development",
        "stake": "business_survival",
        "flexibility": 0.3,
    },
)

MINE_WORKER = CitizenSpec(
    name="Rosa Delgado",
    archetype="Builder",
    region="mining_camp",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.5,
        trust=0.5,
        creativity=0.5,
        patience=0.5,
        resilience=0.8,
        ambition=0.6,
    ),
    cosmotechnics=CONSTRUCTION,
    backstory="Union representative for the miners. Born in the farming "
    "village, has ties to both communities.",
    metadata={
        "claim": "workers_rights",
        "stake": "jobs_and_family",
        "flexibility": 0.6,
    },
)

WATER_AUTHORITY = CitizenSpec(
    name="Director Chen Wei",
    archetype="Scholar",
    region="government_office",
    eigenvectors=Eigenvectors(
        warmth=0.4,
        curiosity=0.7,
        trust=0.5,
        creativity=0.6,
        patience=0.7,
        resilience=0.5,
        ambition=0.5,
    ),
    cosmotechnics=MEMORY,
    backstory="Regional water authority director who must approve any "
    "allocation. Knows about a possible third option no one has considered.",
    metadata={
        "claim": "regulatory_authority",
        "stake": "fair_allocation",
        "flexibility": 0.8,
        "secret": "knows_about_aquifer",
    },
)


# =============================================================================
# Scenario Template
# =============================================================================

THE_RESOURCE_DISPUTE = ScenarioTemplate(
    name="The Resource Dispute",
    scenario_type=ScenarioType.CONFLICT,
    description="""
A newly discovered spring emerges at the boundary between
farmland and the mining operation. Both need the water
desperately - the farmers for their crops and community,
the mine for its operations and workers' livelihoods.

There isn't enough water for both uses. Or is there?

This is not a simple problem. The farmers have worked
this land for generations. The miners have families to
feed. Someone must compromise - or perhaps everyone must.

The resolution will define the region's future.
    """.strip(),
    citizens=[FARMER_ELDER, YOUNG_FARMER, MINE_OWNER, MINE_WORKER, WATER_AUTHORITY],
    regions=[
        "farmlands",
        "mining_camp",
        "spring_site",
        "government_office",
        "neutral_ground",
    ],
    trigger=TriggerCondition.immediate(),
    success_criteria=SuccessCriteria(
        require_all=False,  # Multiple valid endings
        criteria=[
            SuccessCriterion(
                kind="consensus_reached",
                description="Reach a compromise agreement (majority support)",
                params={"threshold": 0.6},
            ),
            SuccessCriterion(
                kind="information_revealed",
                description="Discover the aquifer alternative",
                params={"required_info": ["aquifer_solution"]},
            ),
            SuccessCriterion(
                kind="coalition_formed",
                description="Form a cross-community coalition",
                params={"min_size": 3},
            ),
        ],
    ),
    tags=["conflict", "negotiation", "water-rights", "community", "compromise"],
    difficulty="hard",
    estimated_duration_minutes=60,
    polynomial_config={
        "phases": ["opening_claims", "investigation", "negotiation", "resolution"],
        "valid_transitions": [
            ("opening_claims", "investigation"),
            ("opening_claims", "negotiation"),
            ("investigation", "negotiation"),
            ("negotiation", "resolution"),
        ],
    },
)


__all__ = ["THE_RESOURCE_DISPUTE"]
