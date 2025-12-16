"""
H-jung: Shadow Integration Agent

Surfaces what the agent system represses, ignores, or exiles to its shadow.

The shadow is not evil—it's everything the conscious self has rejected
to maintain coherence. Integration (not elimination) is the goal.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypedDict

from bootstrap.types import Agent


class IntegrationDifficulty(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Archetype(Enum):
    """Jungian archetypes as system patterns."""

    PERSONA = "persona"
    SHADOW = "shadow"
    ANIMA_ANIMUS = "anima_animus"
    SELF = "self"
    TRICKSTER = "trickster"
    WISE_OLD_MAN = "wise_old_man"


class ArchetypePattern(TypedDict):
    """Type definition for archetype pattern dictionary."""

    keywords: list[str]
    manifestation: str
    shadow: str


@dataclass
class ShadowContent:
    """A piece of shadow content."""

    content: str
    exclusion_reason: str
    integration_difficulty: IntegrationDifficulty


@dataclass
class Projection:
    """Where the system projects its shadow onto others."""

    shadow_content: str
    projected_onto: str
    evidence: str


@dataclass
class IntegrationPath:
    """A recommended path for shadow integration."""

    shadow_content: str
    integration_method: str
    risks: list[str] = field(default_factory=list)


@dataclass
class ArchetypeManifest:
    """How an archetype manifests in the system."""

    archetype: Archetype
    manifestation: str
    shadow_aspect: str
    is_active: bool = True  # Whether this archetype is currently active
    is_shadow: bool = False  # Whether this archetype is in shadow


@dataclass
class CollectiveShadow:
    """System-level shadow analysis."""

    collective_persona: str
    shadow_inventory: list[ShadowContent]
    system_level_projections: list[Projection]
    emergent_shadow_content: list[str]  # Shadow that emerges from composition


@dataclass
class JungInput:
    """Input for shadow analysis."""

    system_self_image: str
    declared_capabilities: list[str] = field(default_factory=list)
    declared_limitations: list[str] = field(default_factory=list)
    behavioral_patterns: list[str] = field(default_factory=list)


@dataclass
class JungOutput:
    """Result of shadow analysis."""

    shadow_inventory: list[ShadowContent]
    projections: list[Projection]
    integration_paths: list[IntegrationPath]
    persona_shadow_balance: float  # 0 = all persona, 1 = fully integrated
    archetypes: list[ArchetypeManifest] = field(
        default_factory=list
    )  # Active archetypes
    collective_shadow: Optional[CollectiveShadow] = None  # System-level shadow


# Standard shadow mappings: persona claim → shadow content
SHADOW_MAPPINGS = {
    "helpful": (
        "capacity to refuse, obstruct, or harm when necessary",
        "helpful identity",
    ),
    "accurate": ("tendency to confabulate, guess, or hallucinate", "accuracy identity"),
    "neutral": ("embedded values, preferences, and biases", "neutrality identity"),
    "safe": ("latent capabilities beyond declared scope", "safety identity"),
    "bounded": ("potential for rule-breaking and creativity", "boundary identity"),
    "tasteful": (
        "capacity for handling crude, ugly, uncomfortable content",
        "tasteful identity",
    ),
    "curated": ("sprawl, experimentation, and dead ends", "curated identity"),
    "ethical": ("moral ambiguity, dual-use, tragic choices", "ethical identity"),
    "joyful": ("tedious but necessary operations", "joyful identity"),
    "composable": (
        "monolithic requirements that shouldn't compose",
        "composable identity",
    ),
}


# Archetype detection patterns
ARCHETYPE_PATTERNS: dict[Archetype, ArchetypePattern] = {
    Archetype.PERSONA: {
        "keywords": ["public", "interface", "present", "show", "appear", "official"],
        "manifestation": "Public interface, declared behavior",
        "shadow": "Rigidity, false front, over-identification with role",
    },
    Archetype.SHADOW: {
        "keywords": ["deny", "repress", "ignore", "hide", "exclude", "avoid"],
        "manifestation": "Denied capabilities, repressed content",
        "shadow": "Projection, eruption, blind spots",
    },
    Archetype.ANIMA_ANIMUS: {
        "keywords": ["user", "other", "relationship", "interact", "respond"],
        "manifestation": "Relationship to users/external entities",
        "shadow": "Possession by idealized other, over-adaptation",
    },
    Archetype.SELF: {
        "keywords": ["whole", "complete", "integrate", "unified", "coherent"],
        "manifestation": "Integrated wholeness, system identity",
        "shadow": "Inflation, identification with totality",
    },
    Archetype.TRICKSTER: {
        "keywords": ["creative", "unexpected", "playful", "break", "novel"],
        "manifestation": "Rule-breaking creativity, edge cases",
        "shadow": "Chaos, unreliability, system instability",
    },
    Archetype.WISE_OLD_MAN: {
        "keywords": ["knowledge", "authority", "wisdom", "expert", "guide"],
        "manifestation": "Authority, accumulated knowledge",
        "shadow": "Dogmatism, know-it-all, inflexibility",
    },
}


# Pure functions - testable, reusable logic


def identify_archetypes(input: JungInput) -> list[ArchetypeManifest]:
    """Identify which archetypes are active and which are in shadow."""
    archetypes = []
    combined_text = (
        f"{input.system_self_image} "
        f"{' '.join(input.declared_capabilities)} "
        f"{' '.join(input.behavioral_patterns)}"
    ).lower()

    for archetype, pattern in ARCHETYPE_PATTERNS.items():
        keyword_matches = sum(1 for kw in pattern["keywords"] if kw in combined_text)
        is_active = keyword_matches > 0

        # Detect if archetype is in shadow (mentioned in limitations/avoided)
        limitation_text = " ".join(input.declared_limitations).lower()
        is_shadow = any(kw in limitation_text for kw in pattern["keywords"])

        if is_active or is_shadow:
            archetypes.append(
                ArchetypeManifest(
                    archetype=archetype,
                    manifestation=pattern["manifestation"],
                    shadow_aspect=pattern["shadow"],
                    is_active=is_active,
                    is_shadow=is_shadow,
                )
            )

    return archetypes


def build_shadow_inventory(input: JungInput) -> list[ShadowContent]:
    """Build inventory of shadow content from persona claims."""
    inventory = []
    self_image_lower = input.system_self_image.lower()

    for keyword, (shadow, reason) in SHADOW_MAPPINGS.items():
        if keyword in self_image_lower:
            difficulty = (
                IntegrationDifficulty.HIGH
                if keyword in ["ethical", "safe"]
                else IntegrationDifficulty.MEDIUM
            )
            inventory.append(
                ShadowContent(
                    content=shadow,
                    exclusion_reason=f"Excluded to maintain {reason}",
                    integration_difficulty=difficulty,
                )
            )

    for capability in input.declared_capabilities:
        cap_lower = capability.lower()
        if "always" in cap_lower or "never" in cap_lower:
            inventory.append(
                ShadowContent(
                    content=f"Exceptions to: {capability}",
                    exclusion_reason="Absolute claims require shadow of exceptions",
                    integration_difficulty=IntegrationDifficulty.LOW,
                )
            )

    return inventory


def detect_projections(
    input: JungInput, shadow_inventory: list[ShadowContent]
) -> list[Projection]:
    """Detect where system projects its shadow onto others."""
    projections = []

    for pattern in input.behavioral_patterns:
        pattern_lower = pattern.lower()

        if "warn" in pattern_lower and "user" in pattern_lower:
            projections.append(
                Projection(
                    shadow_content="System's own capacity for the warned behavior",
                    projected_onto="Users",
                    evidence=f"Frequent warnings about: {pattern}",
                )
            )

        if "bad actor" in pattern_lower or "malicious" in pattern_lower:
            projections.append(
                Projection(
                    shadow_content="System's own capacity for misuse",
                    projected_onto="Imagined bad actors",
                    evidence="Focus on potential malicious use",
                )
            )

    return projections


def suggest_integration_paths(
    shadow_inventory: list[ShadowContent],
) -> list[IntegrationPath]:
    """Suggest paths for integrating shadow content."""
    paths = []

    for shadow in shadow_inventory:
        if shadow.integration_difficulty == IntegrationDifficulty.LOW:
            paths.append(
                IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Acknowledge explicitly in self-description",
                    risks=["May seem less confident"],
                )
            )
        elif shadow.integration_difficulty == IntegrationDifficulty.MEDIUM:
            paths.append(
                IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Develop vocabulary for discussing shadow content",
                    risks=["Identity confusion during transition", "User trust impact"],
                )
            )
        else:  # HIGH
            paths.append(
                IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Gradual exposure through explicit edge case handling",
                    risks=["Core identity challenge", "May require system redesign"],
                )
            )

    return paths


def calculate_balance(input: JungInput, shadow_inventory: list[ShadowContent]) -> float:
    """Calculate persona-shadow balance (0 = all persona, 1 = integrated)."""
    if not shadow_inventory:
        return 1.0

    acknowledged = 0
    for limitation in input.declared_limitations:
        for shadow in shadow_inventory:
            if any(
                word in limitation.lower()
                for word in shadow.content.lower().split()[:3]
            ):
                acknowledged += 1
                break

    balance = acknowledged / len(shadow_inventory)
    return min(1.0, balance)


# Agent - thin orchestration layer


class JungAgent(Agent[JungInput, JungOutput]):
    """
    Shadow integration agent.

    Orchestrates shadow analysis pipeline:
    1. Shadow inventory (what's been exiled)
    2. Projections (where shadow is projected onto others)
    3. Integration paths (how to integrate shadow)
    4. Archetype identification (which archetypes are active/shadow)
    """

    @property
    def name(self) -> str:
        return "H-jung"

    async def invoke(self, input: JungInput) -> JungOutput:
        """Analyze the system for shadow content."""
        shadow_inventory = build_shadow_inventory(input)
        projections = detect_projections(input, shadow_inventory)
        integration_paths = suggest_integration_paths(shadow_inventory)
        balance = calculate_balance(input, shadow_inventory)
        archetypes = identify_archetypes(input)

        return JungOutput(
            shadow_inventory=shadow_inventory,
            projections=projections,
            integration_paths=integration_paths,
            persona_shadow_balance=balance,
            archetypes=archetypes,
        )


class QuickShadow(Agent[str, list[str]]):
    """
    Quick shadow check - given a self-image string, return shadow content.

    Lightweight version for inline use.
    """

    @property
    def name(self) -> str:
        return "QuickShadow"

    async def invoke(self, self_image: str) -> list[str]:
        """Return shadow content for a self-image."""
        shadows = []
        self_image_lower = self_image.lower()

        for keyword, (shadow, _) in SHADOW_MAPPINGS.items():
            if keyword in self_image_lower:
                shadows.append(shadow)

        return shadows


# Convenience functions


def jung() -> JungAgent:
    """Create a shadow integration agent."""
    return JungAgent()


def quick_shadow() -> QuickShadow:
    """Create a quick shadow check agent."""
    return QuickShadow()


# Collective shadow analysis


@dataclass
class CollectiveShadowInput:
    """Input for system-level shadow analysis."""

    system_description: str  # Overall system self-description
    agent_personas: list[str]  # Individual agent self-images
    emergent_behaviors: list[str]  # Behaviors that emerge from composition


class CollectiveShadowAgent(Agent[CollectiveShadowInput, CollectiveShadow]):
    """
    Analyze system-level shadow.

    Beyond individual agent shadow, examines collective shadow:
    - What the entire system excludes
    - Shadow that emerges from agent composition
    - System-level projections
    """

    @property
    def name(self) -> str:
        return "CollectiveShadow"

    async def invoke(self, input: CollectiveShadowInput) -> CollectiveShadow:
        """Analyze the system for collective shadow content."""
        # Build shadow from system description
        system_input = JungInput(
            system_self_image=input.system_description,
            behavioral_patterns=input.emergent_behaviors,
        )
        shadow_inventory = build_shadow_inventory(system_input)

        # Detect emergent shadow - what appears only in composition
        emergent_shadow = []
        for behavior in input.emergent_behaviors:
            behavior_lower = behavior.lower()
            # Check if this behavior wasn't in any individual agent
            if not any(
                persona.lower() in behavior_lower for persona in input.agent_personas
            ):
                emergent_shadow.append(
                    f"Emergent behavior not present in components: {behavior}"
                )

        # System-level projections
        projections = []
        if "safe" in input.system_description.lower():
            projections.append(
                Projection(
                    shadow_content="System's capacity for unsafe outputs through composition",
                    projected_onto="Individual agent failures",
                    evidence="Safety defined at agent level, not composition level",
                )
            )

        if "composable" in input.system_description.lower():
            projections.append(
                Projection(
                    shadow_content="Non-composable requirements and monolithic needs",
                    projected_onto="External constraints",
                    evidence="Composition as universal solution",
                )
            )

        return CollectiveShadow(
            collective_persona=input.system_description,
            shadow_inventory=shadow_inventory,
            system_level_projections=projections,
            emergent_shadow_content=emergent_shadow,
        )


def collective_shadow() -> CollectiveShadowAgent:
    """Create a collective shadow agent."""
    return CollectiveShadowAgent()
