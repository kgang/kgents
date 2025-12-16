"""
The Missing Artifact: A Mystery Scenario.

A valuable artifact has gone missing from the Town Museum.
Five citizens each hold a piece of the puzzle. Through dialogue
and deduction, participants uncover who took it, where it is,
and why.

ScenarioType: MYSTERY
Difficulty: Medium
Duration: ~45 minutes

Design:
- Information asymmetry: Each citizen knows something
- Deduction: Combine clues to solve
- Revelation: The "why" matters as much as "who"
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
    EXPLORATION,
    GATHERING,
    MEMORY,
    Eigenvectors,
)

# =============================================================================
# Citizen Specs
# =============================================================================

CURATOR = CitizenSpec(
    name="Dr. Helena Vance",
    archetype="Watcher",
    region="museum",
    eigenvectors=Eigenvectors(
        warmth=0.4,
        curiosity=0.8,
        trust=0.3,
        creativity=0.5,
        patience=0.9,
        resilience=0.6,
        ambition=0.4,
    ),
    cosmotechnics=MEMORY,
    backstory="The museum curator who discovered the artifact missing. "
    "She knows the artifact's history and value.",
    metadata={
        "has_clue": "artifact_history",
        "secret": "Was working late the night it vanished",
    },
)

GUARD = CitizenSpec(
    name="Marcus Chen",
    archetype="Builder",
    region="museum_entrance",
    eigenvectors=Eigenvectors(
        warmth=0.6,
        curiosity=0.3,
        trust=0.7,
        creativity=0.2,
        patience=0.7,
        resilience=0.8,
        ambition=0.3,
    ),
    cosmotechnics=GATHERING,
    backstory="Night guard who was on duty. "
    "He saw something unusual but isn't sure what.",
    metadata={
        "has_clue": "saw_figure",
        "secret": "Took a break he wasn't supposed to",
    },
)

SCHOLAR = CitizenSpec(
    name="Professor Kira Okonkwo",
    archetype="Scholar",
    region="library",
    eigenvectors=Eigenvectors(
        warmth=0.5,
        curiosity=0.95,
        trust=0.5,
        creativity=0.7,
        patience=0.6,
        resilience=0.5,
        ambition=0.8,
    ),
    cosmotechnics=EXPLORATION,
    backstory="Expert on the artifact's origin culture. "
    "She believes it should be returned to its homeland.",
    metadata={
        "has_clue": "origin_knowledge",
        "secret": "Has been advocating for repatriation",
    },
)

COLLECTOR = CitizenSpec(
    name="Victor Ashworth",
    archetype="Trader",
    region="gallery",
    eigenvectors=Eigenvectors(
        warmth=0.3,
        curiosity=0.6,
        trust=0.2,
        creativity=0.4,
        patience=0.3,
        resilience=0.7,
        ambition=0.9,
    ),
    cosmotechnics=GATHERING,
    backstory="Wealthy collector who offered to buy the artifact. "
    "His offer was refused.",
    metadata={
        "has_clue": "financial_motive",
        "secret": "His business is in trouble",
    },
)

INTERN = CitizenSpec(
    name="Mira Torres",
    archetype="Healer",
    region="archives",
    eigenvectors=Eigenvectors(
        warmth=0.8,
        curiosity=0.7,
        trust=0.8,
        creativity=0.6,
        patience=0.5,
        resilience=0.4,
        ambition=0.5,
    ),
    cosmotechnics=GATHERING,
    backstory="Museum intern with access to the vault. Young and idealistic.",
    metadata={
        "has_clue": "vault_access",
        "secret": "Helped Professor Okonkwo with research",
    },
)


# =============================================================================
# Scenario Template
# =============================================================================

THE_MISSING_ARTIFACT = ScenarioTemplate(
    name="The Missing Artifact",
    scenario_type=ScenarioType.MYSTERY,
    description="""
A priceless artifact has vanished from the Town Museum.
The theft occurred during the night, and five people had
access or motive. Through careful questioning and deduction,
uncover the truth: Who took it? Where is it? And most
importantly - why?

The answer may surprise you. Sometimes theft is not theft
but liberation.
    """.strip(),
    citizens=[CURATOR, GUARD, SCHOLAR, COLLECTOR, INTERN],
    regions=["museum", "museum_entrance", "library", "gallery", "archives", "vault"],
    trigger=TriggerCondition.immediate(),
    success_criteria=SuccessCriteria(
        require_all=True,
        criteria=[
            SuccessCriterion(
                kind="information_revealed",
                description="Discover who took the artifact",
                params={"required_info": ["culprit_identity"]},
            ),
            SuccessCriterion(
                kind="information_revealed",
                description="Find where the artifact is",
                params={"required_info": ["artifact_location"]},
            ),
            SuccessCriterion(
                kind="information_revealed",
                description="Understand the motive",
                params={"required_info": ["true_motive"]},
            ),
        ],
    ),
    tags=["mystery", "deduction", "museum", "ethics", "repatriation"],
    difficulty="medium",
    estimated_duration_minutes=45,
    polynomial_config={
        "phases": ["investigation", "accusation", "resolution"],
        "valid_transitions": [
            ("investigation", "accusation"),
            ("accusation", "resolution"),
        ],
    },
)


__all__ = ["THE_MISSING_ARTIFACT"]
