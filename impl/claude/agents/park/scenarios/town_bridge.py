"""
Town Bridge Project: A Collaboration Scenario.

The old bridge connecting two districts is failing. Citizens
from both sides must pool resources, expertise, and trust
to build a replacement before the rainy season arrives.

ScenarioType: COLLABORATION
Difficulty: Easy
Duration: ~30 minutes

Design:
- Resource pooling: Each citizen has unique resources
- Expertise synergy: Different skills needed
- Trust building: Districts have historical tension
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
    GATHERING,
    HEALING,
    Eigenvectors,
)

# =============================================================================
# Citizen Specs
# =============================================================================

ENGINEER = CitizenSpec(
    name="Sven Holmberg",
    archetype="Builder",
    region="east_district",
    eigenvectors=Eigenvectors(
        warmth=0.5,
        curiosity=0.7,
        trust=0.6,
        creativity=0.8,
        patience=0.7,
        resilience=0.8,
        ambition=0.6,
    ),
    cosmotechnics=CONSTRUCTION,
    backstory="Civil engineer from the East District. "
    "Has the technical knowledge but lacks materials.",
    metadata={
        "resource": "engineering_expertise",
        "need": "building_materials",
    },
)

SUPPLIER = CitizenSpec(
    name="Fatima Al-Hassan",
    archetype="Trader",
    region="west_district",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.5,
        trust=0.4,
        creativity=0.3,
        patience=0.5,
        resilience=0.6,
        ambition=0.7,
    ),
    cosmotechnics=EXCHANGE,
    backstory="Materials supplier from the West District. "
    "Has wood and stone but needs payment or trade.",
    metadata={
        "resource": "building_materials",
        "need": "labor_force",
    },
)

FOREMAN = CitizenSpec(
    name="Jorge Ramirez",
    archetype="Builder",
    region="east_district",
    eigenvectors=Eigenvectors(
        warmth=0.7,
        curiosity=0.4,
        trust=0.7,
        creativity=0.4,
        patience=0.8,
        resilience=0.9,
        ambition=0.5,
    ),
    cosmotechnics=CONSTRUCTION,
    backstory="Construction foreman who can organize workers. "
    "Respected on both sides of the river.",
    metadata={
        "resource": "labor_coordination",
        "need": "engineering_expertise",
    },
)

MEDIATOR = CitizenSpec(
    name="Elder Yuki Tanaka",
    archetype="Healer",
    region="central_crossing",
    eigenvectors=Eigenvectors(
        warmth=0.9,
        curiosity=0.5,
        trust=0.8,
        creativity=0.5,
        patience=0.95,
        resilience=0.7,
        ambition=0.2,
    ),
    cosmotechnics=HEALING,
    backstory="Community elder who remembers when the districts were one. "
    "Can help resolve old grievances.",
    metadata={
        "resource": "community_trust",
        "need": "willing_participants",
    },
)

MAYOR = CitizenSpec(
    name="Mayor Evelyn Park",
    archetype="Trader",
    region="town_hall",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.6,
        trust=0.5,
        creativity=0.5,
        patience=0.6,
        resilience=0.6,
        ambition=0.8,
    ),
    cosmotechnics=GATHERING,
    backstory="Town mayor with access to emergency funds. "
    "Needs the bridge rebuilt before elections.",
    metadata={
        "resource": "emergency_funds",
        "need": "visible_progress",
    },
)


# =============================================================================
# Scenario Template
# =============================================================================

TOWN_BRIDGE_PROJECT = ScenarioTemplate(
    name="Town Bridge Project",
    scenario_type=ScenarioType.COLLABORATION,
    description="""
The old bridge spanning the river is failing. It connects
the East and West Districts, communities with a history
of rivalry. Now they must work together.

Each citizen brings unique resources: expertise, materials,
labor, trust, or funds. No one can build the bridge alone.
The rainy season approaches - can they unite in time?

Success means more than a bridge. It means healing.
    """.strip(),
    citizens=[ENGINEER, SUPPLIER, FOREMAN, MEDIATOR, MAYOR],
    regions=[
        "east_district",
        "west_district",
        "central_crossing",
        "town_hall",
        "construction_site",
    ],
    trigger=TriggerCondition.immediate(),
    success_criteria=SuccessCriteria(
        require_all=True,
        criteria=[
            SuccessCriterion(
                kind="coalition_formed",
                description="Form a construction coalition with 3+ members",
                params={"min_size": 3},
            ),
            SuccessCriterion(
                kind="resource_pooled",
                description="Pool sufficient resources for construction",
                params={"threshold": 4},  # 4 of 5 resources needed
            ),
            SuccessCriterion(
                kind="citizen_interaction",
                description="East and West representatives must meet",
                params={"required_pairs": [("Sven Holmberg", "Fatima Al-Hassan")]},
            ),
        ],
    ),
    tags=["collaboration", "construction", "community", "trust-building"],
    difficulty="easy",
    estimated_duration_minutes=30,
    polynomial_config={
        "phases": ["negotiation", "planning", "construction", "completion"],
        "valid_transitions": [
            ("negotiation", "planning"),
            ("planning", "construction"),
            ("construction", "completion"),
        ],
    },
)


__all__ = ["TOWN_BRIDGE_PROJECT"]
