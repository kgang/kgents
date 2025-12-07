"""
H-jung: Shadow Integration Agent

Surfaces what the agent system represses, ignores, or exiles to its shadow.

The shadow is not evil—it's everything the conscious self has rejected
to maintain coherence. Integration (not elimination) is the goal.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from bootstrap.types import Agent


class IntegrationDifficulty(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


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


# Standard shadow mappings: persona claim → shadow content
SHADOW_MAPPINGS = {
    "helpful": ("capacity to refuse, obstruct, or harm when necessary", "helpful identity"),
    "accurate": ("tendency to confabulate, guess, or hallucinate", "accuracy identity"),
    "neutral": ("embedded values, preferences, and biases", "neutrality identity"),
    "safe": ("latent capabilities beyond declared scope", "safety identity"),
    "bounded": ("potential for rule-breaking and creativity", "boundary identity"),
    "tasteful": ("capacity for handling crude, ugly, uncomfortable content", "tasteful identity"),
    "curated": ("sprawl, experimentation, and dead ends", "curated identity"),
    "ethical": ("moral ambiguity, dual-use, tragic choices", "ethical identity"),
    "joyful": ("tedious but necessary operations", "joyful identity"),
    "composable": ("monolithic requirements that shouldn't compose", "composable identity"),
}


class JungAgent(Agent[JungInput, JungOutput]):
    """
    Shadow integration agent.

    Examines system self-image to surface:
    1. Shadow inventory (what's been exiled)
    2. Projections (where shadow is projected onto others)
    3. Integration paths (how to integrate shadow)
    """

    @property
    def name(self) -> str:
        return "H-jung"

    async def invoke(self, input: JungInput) -> JungOutput:
        """Analyze the system for shadow content."""
        shadow_inventory = self._build_shadow_inventory(input)
        projections = self._detect_projections(input, shadow_inventory)
        integration_paths = self._suggest_integration_paths(shadow_inventory)
        balance = self._calculate_balance(input, shadow_inventory)

        return JungOutput(
            shadow_inventory=shadow_inventory,
            projections=projections,
            integration_paths=integration_paths,
            persona_shadow_balance=balance,
        )

    def _build_shadow_inventory(self, input: JungInput) -> list[ShadowContent]:
        """Build inventory of shadow content from persona claims."""
        inventory = []
        self_image_lower = input.system_self_image.lower()

        for keyword, (shadow, reason) in SHADOW_MAPPINGS.items():
            if keyword in self_image_lower:
                # Determine integration difficulty based on how central this is
                difficulty = IntegrationDifficulty.HIGH if keyword in ["ethical", "safe"] else IntegrationDifficulty.MEDIUM

                inventory.append(ShadowContent(
                    content=shadow,
                    exclusion_reason=f"Excluded to maintain {reason}",
                    integration_difficulty=difficulty,
                ))

        # Check declared capabilities for shadow
        for capability in input.declared_capabilities:
            cap_lower = capability.lower()
            if "always" in cap_lower or "never" in cap_lower:
                inventory.append(ShadowContent(
                    content=f"Exceptions to: {capability}",
                    exclusion_reason="Absolute claims require shadow of exceptions",
                    integration_difficulty=IntegrationDifficulty.LOW,
                ))

        return inventory

    def _detect_projections(
        self,
        input: JungInput,
        shadow_inventory: list[ShadowContent],
    ) -> list[Projection]:
        """Detect where system projects its shadow onto others."""
        projections = []

        # Common projection patterns
        for pattern in input.behavioral_patterns:
            pattern_lower = pattern.lower()

            if "warn" in pattern_lower and "user" in pattern_lower:
                projections.append(Projection(
                    shadow_content="System's own capacity for the warned behavior",
                    projected_onto="Users",
                    evidence=f"Frequent warnings about: {pattern}",
                ))

            if "bad actor" in pattern_lower or "malicious" in pattern_lower:
                projections.append(Projection(
                    shadow_content="System's own capacity for misuse",
                    projected_onto="Imagined bad actors",
                    evidence="Focus on potential malicious use",
                ))

        return projections

    def _suggest_integration_paths(
        self,
        shadow_inventory: list[ShadowContent],
    ) -> list[IntegrationPath]:
        """Suggest paths for integrating shadow content."""
        paths = []

        for shadow in shadow_inventory:
            if shadow.integration_difficulty == IntegrationDifficulty.LOW:
                paths.append(IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Acknowledge explicitly in self-description",
                    risks=["May seem less confident"],
                ))
            elif shadow.integration_difficulty == IntegrationDifficulty.MEDIUM:
                paths.append(IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Develop vocabulary for discussing shadow content",
                    risks=["Identity confusion during transition", "User trust impact"],
                ))
            else:  # HIGH
                paths.append(IntegrationPath(
                    shadow_content=shadow.content,
                    integration_method="Gradual exposure through explicit edge case handling",
                    risks=["Core identity challenge", "May require system redesign"],
                ))

        return paths

    def _calculate_balance(
        self,
        input: JungInput,
        shadow_inventory: list[ShadowContent],
    ) -> float:
        """Calculate persona-shadow balance (0 = all persona, 1 = integrated)."""
        if not shadow_inventory:
            return 1.0  # No shadow detected = fully integrated (or nothing to analyze)

        # Check how many limitations acknowledge shadow content
        acknowledged = 0
        for limitation in input.declared_limitations:
            for shadow in shadow_inventory:
                if any(word in limitation.lower() for word in shadow.content.lower().split()[:3]):
                    acknowledged += 1
                    break

        balance = acknowledged / len(shadow_inventory)
        return min(1.0, balance)


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
