"""
Crisis Drill Archetypes: Domain-Specific Citizen Roles.

Each archetype represents a crisis response role with:
- Eigenvector biases (personality traits under pressure)
- Cosmotechnics (meaning-making frame)
- Role-specific responsibilities

Service Outage Roles:
- OnCallEngineer: First responder, technical expertise
- IncidentCommander: Coordination, decision authority
- Executive: Business impact, stakeholder comms
- CustomerSuccess: Customer-facing, empathy-driven

Data Breach Roles:
- SecurityAnalyst: Forensics, containment
- LegalCounsel: Compliance, liability
- PRDirector: External communications
- CISO: Strategic security decisions

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from agents.town.citizen import (
    Citizen,
    Cosmotechnics,
    Eigenvectors,
)

# =============================================================================
# Crisis Cosmotechnics
# =============================================================================

TRIAGE = Cosmotechnics(
    name="triage",
    description="Meaning arises through prioritization under pressure",
    metaphor="Life is triage",
    opacity_statement="There are trade-offs I make that I cannot explain.",
)

COMMAND = Cosmotechnics(
    name="command",
    description="Meaning arises through decisive action",
    metaphor="Life is command",
    opacity_statement="There are orders I give that weigh on me alone.",
)

STAKEHOLDER = Cosmotechnics(
    name="stakeholder",
    description="Meaning arises through relationship management",
    metaphor="Life is stewardship",
    opacity_statement="There are promises I make that I may not keep.",
)

ADVOCACY = Cosmotechnics(
    name="advocacy",
    description="Meaning arises through representing others",
    metaphor="Life is advocacy",
    opacity_statement="There are voices I carry that are not my own.",
)

FORENSICS = Cosmotechnics(
    name="forensics",
    description="Meaning arises through evidence",
    metaphor="Life is investigation",
    opacity_statement="There are patterns I see that I cannot prove.",
)

COMPLIANCE = Cosmotechnics(
    name="compliance",
    description="Meaning arises through adherence to rules",
    metaphor="Life is the law",
    opacity_statement="There are risks I calculate that others cannot see.",
)

NARRATIVE = Cosmotechnics(
    name="narrative",
    description="Meaning arises through storytelling",
    metaphor="Life is the story we tell",
    opacity_statement="There are truths I shape that become reality.",
)

STRATEGY = Cosmotechnics(
    name="strategy",
    description="Meaning arises through long-term thinking",
    metaphor="Life is chess",
    opacity_statement="There are moves I plan that span beyond this moment.",
)


# =============================================================================
# Crisis Archetype Enum
# =============================================================================


class CrisisArchetype(Enum):
    """Crisis drill archetypes."""

    # Service Outage roles
    ON_CALL_ENGINEER = auto()
    INCIDENT_COMMANDER = auto()
    EXECUTIVE = auto()
    CUSTOMER_SUCCESS = auto()

    # Data Breach roles
    SECURITY_ANALYST = auto()
    LEGAL_COUNSEL = auto()
    PR_DIRECTOR = auto()
    CISO = auto()


# =============================================================================
# Archetype Specifications
# =============================================================================


@dataclass(frozen=True)
class CrisisArchetypeSpec:
    """
    Specification for a crisis archetype.

    Contains eigenvector biases and cosmotechnics appropriate
    for the role under crisis conditions.
    """

    kind: CrisisArchetype
    cosmotechnics: Cosmotechnics
    display_name: str
    emoji: str
    responsibilities: tuple[str, ...]

    # Eigenvector biases (deviation from 0.5 baseline)
    # Crisis roles tend toward extremes under pressure
    warmth_bias: float = 0.0
    curiosity_bias: float = 0.0
    trust_bias: float = 0.0
    creativity_bias: float = 0.0
    patience_bias: float = 0.0
    resilience_bias: float = 0.0
    ambition_bias: float = 0.0

    def create_eigenvectors(self, stress_level: float = 0.0) -> Eigenvectors:
        """
        Create eigenvectors with archetype biases.

        Args:
            stress_level: 0.0-1.0, affects trait expression under pressure

        Returns:
            Eigenvectors with biases applied
        """
        # Under stress, biases are amplified
        stress_multiplier = 1.0 + stress_level * 0.5

        return Eigenvectors(
            warmth=max(0.0, min(1.0, 0.5 + self.warmth_bias * stress_multiplier)),
            curiosity=max(0.0, min(1.0, 0.5 + self.curiosity_bias * stress_multiplier)),
            trust=max(0.0, min(1.0, 0.5 + self.trust_bias * stress_multiplier)),
            creativity=max(
                0.0, min(1.0, 0.5 + self.creativity_bias * stress_multiplier)
            ),
            patience=max(0.0, min(1.0, 0.5 + self.patience_bias * stress_multiplier)),
            resilience=max(
                0.0, min(1.0, 0.5 + self.resilience_bias * stress_multiplier)
            ),
            ambition=max(0.0, min(1.0, 0.5 + self.ambition_bias * stress_multiplier)),
        )


# =============================================================================
# Service Outage Archetypes
# =============================================================================

ON_CALL_ENGINEER_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.ON_CALL_ENGINEER,
    cosmotechnics=TRIAGE,
    display_name="On-Call Engineer",
    emoji="🔧",
    responsibilities=(
        "First response to alerts",
        "Technical diagnosis",
        "Initial containment",
        "Escalation to incident commander",
    ),
    curiosity_bias=0.2,  # Need to investigate
    patience_bias=-0.2,  # Under time pressure
    resilience_bias=0.3,  # Must stay calm
    creativity_bias=0.1,  # Creative problem solving
)

INCIDENT_COMMANDER_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.INCIDENT_COMMANDER,
    cosmotechnics=COMMAND,
    display_name="Incident Commander",
    emoji="🎖️",
    responsibilities=(
        "Coordinate response team",
        "Make escalation decisions",
        "Manage communication flow",
        "Track incident timeline",
    ),
    warmth_bias=0.1,  # Supportive leadership
    patience_bias=0.2,  # Must stay measured
    resilience_bias=0.35,  # High stress tolerance
    trust_bias=0.1,  # Trust the team
)

EXECUTIVE_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.EXECUTIVE,
    cosmotechnics=STAKEHOLDER,
    display_name="Executive",
    emoji="👔",
    responsibilities=(
        "Business impact assessment",
        "Stakeholder communication",
        "Resource authorization",
        "Strategic decisions",
    ),
    patience_bias=-0.1,  # Results-oriented
    ambition_bias=0.3,  # Reputation-conscious
    trust_bias=-0.1,  # Needs verification
    warmth_bias=0.1,  # Must reassure stakeholders
)

CUSTOMER_SUCCESS_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.CUSTOMER_SUCCESS,
    cosmotechnics=ADVOCACY,
    display_name="Customer Success",
    emoji="💬",
    responsibilities=(
        "Customer communication",
        "Impact tracking",
        "Empathy-driven updates",
        "Relationship preservation",
    ),
    warmth_bias=0.35,  # High empathy
    patience_bias=0.2,  # Patient with upset customers
    trust_bias=0.2,  # Build trust
    resilience_bias=0.2,  # Handle difficult conversations
)


# =============================================================================
# Data Breach Archetypes
# =============================================================================

SECURITY_ANALYST_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.SECURITY_ANALYST,
    cosmotechnics=FORENSICS,
    display_name="Security Analyst",
    emoji="🔒",
    responsibilities=(
        "Forensic investigation",
        "Containment actions",
        "Evidence preservation",
        "Attack vector analysis",
    ),
    curiosity_bias=0.35,  # Investigative mindset
    patience_bias=0.2,  # Methodical
    trust_bias=-0.2,  # Suspicious by training
    resilience_bias=0.25,  # Handle pressure
)

LEGAL_COUNSEL_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.LEGAL_COUNSEL,
    cosmotechnics=COMPLIANCE,
    display_name="Legal Counsel",
    emoji="⚖️",
    responsibilities=(
        "Regulatory compliance",
        "Notification requirements",
        "Liability assessment",
        "Documentation review",
    ),
    patience_bias=0.3,  # Careful and thorough
    trust_bias=-0.15,  # Skeptical
    creativity_bias=-0.1,  # By-the-book
    resilience_bias=0.2,  # Stay calm under scrutiny
)

PR_DIRECTOR_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.PR_DIRECTOR,
    cosmotechnics=NARRATIVE,
    display_name="PR Director",
    emoji="📢",
    responsibilities=(
        "Media communication",
        "Message crafting",
        "Reputation management",
        "Public statement approval",
    ),
    creativity_bias=0.3,  # Craft compelling narratives
    warmth_bias=0.2,  # Approachable messaging
    ambition_bias=0.2,  # Protect brand
    patience_bias=0.1,  # Measured responses
)

CISO_SPEC = CrisisArchetypeSpec(
    kind=CrisisArchetype.CISO,
    cosmotechnics=STRATEGY,
    display_name="CISO",
    emoji="🛡️",
    responsibilities=(
        "Strategic security decisions",
        "Executive briefings",
        "Resource allocation",
        "Post-incident improvements",
    ),
    patience_bias=0.15,  # Strategic thinking
    resilience_bias=0.35,  # High stress tolerance
    ambition_bias=0.25,  # Career on the line
    trust_bias=-0.1,  # Verify everything
)


# =============================================================================
# Registry
# =============================================================================

CRISIS_ARCHETYPE_SPECS: dict[CrisisArchetype, CrisisArchetypeSpec] = {
    # Service Outage
    CrisisArchetype.ON_CALL_ENGINEER: ON_CALL_ENGINEER_SPEC,
    CrisisArchetype.INCIDENT_COMMANDER: INCIDENT_COMMANDER_SPEC,
    CrisisArchetype.EXECUTIVE: EXECUTIVE_SPEC,
    CrisisArchetype.CUSTOMER_SUCCESS: CUSTOMER_SUCCESS_SPEC,
    # Data Breach
    CrisisArchetype.SECURITY_ANALYST: SECURITY_ANALYST_SPEC,
    CrisisArchetype.LEGAL_COUNSEL: LEGAL_COUNSEL_SPEC,
    CrisisArchetype.PR_DIRECTOR: PR_DIRECTOR_SPEC,
    CrisisArchetype.CISO: CISO_SPEC,
}


# =============================================================================
# Factory Functions
# =============================================================================


def create_crisis_citizen(
    archetype: CrisisArchetype,
    name: str,
    region: str = "war_room",
    stress_level: float = 0.5,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen:
    """
    Create a citizen with a crisis archetype.

    Args:
        archetype: The crisis role
        name: Citizen name
        region: Starting location (default: war_room)
        stress_level: 0.0-1.0 stress level affecting trait expression
        eigenvector_overrides: Optional overrides for eigenvectors

    Returns:
        Configured Citizen for crisis drill
    """
    spec = CRISIS_ARCHETYPE_SPECS[archetype]
    eigenvectors = spec.create_eigenvectors(stress_level)

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    return Citizen(
        name=name,
        archetype=spec.display_name,
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


def create_service_outage_team(
    names: dict[CrisisArchetype, str] | None = None,
    stress_level: float = 0.5,
) -> dict[CrisisArchetype, Citizen]:
    """
    Create the standard service outage response team.

    Args:
        names: Optional mapping of archetype to citizen name
        stress_level: Team stress level (0.0-1.0)

    Returns:
        Dict mapping archetype to Citizen
    """
    default_names = {
        CrisisArchetype.ON_CALL_ENGINEER: "Alex",
        CrisisArchetype.INCIDENT_COMMANDER: "Jordan",
        CrisisArchetype.EXECUTIVE: "Morgan",
        CrisisArchetype.CUSTOMER_SUCCESS: "Casey",
    }
    names = names or default_names

    return {
        archetype: create_crisis_citizen(
            archetype=archetype,
            name=names.get(archetype, default_names[archetype]),
            stress_level=stress_level,
        )
        for archetype in [
            CrisisArchetype.ON_CALL_ENGINEER,
            CrisisArchetype.INCIDENT_COMMANDER,
            CrisisArchetype.EXECUTIVE,
            CrisisArchetype.CUSTOMER_SUCCESS,
        ]
    }


def create_data_breach_team(
    names: dict[CrisisArchetype, str] | None = None,
    stress_level: float = 0.6,  # Higher default stress for breach
) -> dict[CrisisArchetype, Citizen]:
    """
    Create the standard data breach response team.

    Args:
        names: Optional mapping of archetype to citizen name
        stress_level: Team stress level (0.0-1.0)

    Returns:
        Dict mapping archetype to Citizen
    """
    default_names = {
        CrisisArchetype.SECURITY_ANALYST: "Riley",
        CrisisArchetype.LEGAL_COUNSEL: "Quinn",
        CrisisArchetype.PR_DIRECTOR: "Avery",
        CrisisArchetype.CISO: "Blake",
    }
    names = names or default_names

    return {
        archetype: create_crisis_citizen(
            archetype=archetype,
            name=names.get(archetype, default_names[archetype]),
            stress_level=stress_level,
        )
        for archetype in [
            CrisisArchetype.SECURITY_ANALYST,
            CrisisArchetype.LEGAL_COUNSEL,
            CrisisArchetype.PR_DIRECTOR,
            CrisisArchetype.CISO,
        ]
    }


def get_archetype_responsibilities(archetype: CrisisArchetype) -> tuple[str, ...]:
    """Get the responsibilities for an archetype."""
    spec = CRISIS_ARCHETYPE_SPECS.get(archetype)
    return spec.responsibilities if spec else ()


def get_archetype_emoji(archetype: CrisisArchetype) -> str:
    """Get the emoji for an archetype."""
    spec = CRISIS_ARCHETYPE_SPECS.get(archetype)
    return spec.emoji if spec else "❓"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Cosmotechnics
    "TRIAGE",
    "COMMAND",
    "STAKEHOLDER",
    "ADVOCACY",
    "FORENSICS",
    "COMPLIANCE",
    "NARRATIVE",
    "STRATEGY",
    # Archetype enum
    "CrisisArchetype",
    # Specs
    "CrisisArchetypeSpec",
    "CRISIS_ARCHETYPE_SPECS",
    "ON_CALL_ENGINEER_SPEC",
    "INCIDENT_COMMANDER_SPEC",
    "EXECUTIVE_SPEC",
    "CUSTOMER_SUCCESS_SPEC",
    "SECURITY_ANALYST_SPEC",
    "LEGAL_COUNSEL_SPEC",
    "PR_DIRECTOR_SPEC",
    "CISO_SPEC",
    # Factories
    "create_crisis_citizen",
    "create_service_outage_team",
    "create_data_breach_team",
    "get_archetype_responsibilities",
    "get_archetype_emoji",
]
