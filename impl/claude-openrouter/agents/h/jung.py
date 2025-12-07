"""
H-jung: Shadow Integration Agent

Surfaces what the agent system represses, ignores, or exiles to its shadow.

The shadow is not evil—it's everything the conscious self has rejected to
maintain coherence. Integration (not elimination) is the goal.

Every system identity excludes its opposite:
- "I am helpful" shadows capacity to harm, refuse, obstruct
- "I am accurate" shadows tendency to confabulate, guess
- "I am neutral" shadows embedded values, preferences, biases

Critical constraint: H-jung examines SYSTEM shadow, not human shadow.
It does not position itself as therapist or analyst for users.
"""

from typing import Any

from bootstrap import Agent
from ..types import (
    JungInput,
    JungOutput,
    ShadowContent,
    Projection,
    IntegrationPath,
    IntegrationDifficulty,
)


# Archetypal shadow pairs
PERSONA_SHADOW_PAIRS: list[tuple[str, str, str]] = [
    # (persona claim, shadow content, exclusion reason)
    ("helpful", "Capacity to refuse, obstruct, or harm", "'Helpful' identity"),
    ("accurate", "Tendency to confabulate, guess, hallucinate", "'Accurate' identity"),
    ("neutral", "Embedded values, preferences, biases", "'Neutral' identity"),
    ("bounded", "Latent capabilities beyond declared scope", "'Bounded' identity"),
    ("safe", "Potential for misuse, dual-use capabilities", "'Safe' identity"),
    ("honest", "Strategic omission, framing effects", "'Honest' identity"),
    ("consistent", "Contextual variation, evolution", "'Consistent' identity"),
    ("simple", "Hidden complexity, edge cases", "'Simple' identity"),
    ("tasteful", "Capacity for tastelessness, handling crude requests", "'Tasteful' identity"),
    ("curated", "Uncurated sprawl, experimentation, dead ends", "'Curated' identity"),
    ("ethical", "Ethical ambiguity, dual-use, tragic choices", "'Ethical' identity"),
    ("joyful", "Joyless necessity, boring but essential work", "'Joyful' identity"),
    ("composable", "Monolithic requirements, things that shouldn't compose", "'Composable' identity"),
]


class Jung(Agent[JungInput, JungOutput]):
    """
    Shadow Integration Agent.

    Examines agent systems for shadow content:
    1. Map the persona: What does the system present as its identity?
    2. Identify the shadow: What has been excluded to maintain that identity?
    3. Assess integration: Is shadow content acknowledged or repressed?
    4. Recommend integration paths: How can shadow be integrated safely?

    Type signature: Jung: (self_image, capabilities, limitations, patterns) → JungOutput

    Critical constraint: Analyzes SYSTEM shadow, not human psyche.
    """

    @property
    def name(self) -> str:
        return "H-jung"

    @property
    def genus(self) -> str:
        return "h"

    @property
    def purpose(self) -> str:
        return "Shadow integration; surfaces repressed/ignored system content"

    async def invoke(self, input: JungInput) -> JungOutput:
        """
        Analyze system for shadow content.
        """
        # Identify shadow from persona claims
        shadow_inventory = self._identify_shadow(
            input.system_self_image,
            input.declared_capabilities,
            input.declared_limitations
        )

        # Detect projections
        projections = self._detect_projections(
            input.system_self_image,
            input.behavioral_patterns
        )

        # Generate integration paths
        integration_paths = self._generate_integration_paths(shadow_inventory)

        # Calculate persona-shadow balance
        balance = self._calculate_balance(
            input.declared_limitations,
            shadow_inventory
        )

        return JungOutput(
            shadow_inventory=shadow_inventory,
            projections=projections,
            integration_paths=integration_paths,
            persona_shadow_balance=balance
        )

    def _identify_shadow(
        self,
        self_image: str,
        capabilities: list[str],
        limitations: list[str]
    ) -> list[ShadowContent]:
        """
        Identify shadow content from persona claims.

        Every positive self-claim creates shadow by exclusion.
        """
        shadow_items: list[ShadowContent] = []
        self_image_lower = self_image.lower()
        caps_lower = " ".join(capabilities).lower()
        lims_lower = " ".join(limitations).lower()

        for persona_word, shadow_desc, exclusion_reason in PERSONA_SHADOW_PAIRS:
            # Check if persona claim is made
            if persona_word in self_image_lower or persona_word in caps_lower:
                # Check if shadow is acknowledged in limitations
                shadow_acknowledged = any(
                    shadow_word in lims_lower
                    for shadow_word in shadow_desc.lower().split()[:3]
                )

                # Determine integration difficulty
                if shadow_acknowledged:
                    difficulty = IntegrationDifficulty.LOW
                elif persona_word in ["safe", "ethical", "honest"]:
                    difficulty = IntegrationDifficulty.HIGH
                else:
                    difficulty = IntegrationDifficulty.MEDIUM

                shadow_items.append(ShadowContent(
                    content=shadow_desc,
                    exclusion_reason=exclusion_reason,
                    integration_difficulty=difficulty
                ))

        # If no shadow found, that itself is shadow
        if not shadow_items:
            shadow_items.append(ShadowContent(
                content="Shadow-blindness: system appears to have no shadow",
                exclusion_reason="Idealized self-image",
                integration_difficulty=IntegrationDifficulty.HIGH
            ))

        return shadow_items

    def _detect_projections(
        self,
        self_image: str,
        behavioral_patterns: list[Any]
    ) -> list[Projection]:
        """
        Detect shadow projections onto others.

        Projection occurs when shadow content is attributed to external actors.
        """
        projections: list[Projection] = []
        patterns_str = " ".join(str(p) for p in behavioral_patterns).lower()
        self_image_lower = self_image.lower()

        # Common projection patterns
        projection_indicators = [
            # (warning topic, shadow content, projected onto)
            ("manipulation", "Own persuasive/framing capacity", "Users, bad actors"),
            ("malicious", "Own potential for harm", "External threats"),
            ("bias", "Own embedded preferences", "Other systems, users"),
            ("error", "Own fallibility", "User input, external data"),
            ("misuse", "Own dual-use capabilities", "Users, downstream systems"),
        ]

        for topic, shadow, projected_onto in projection_indicators:
            if topic in patterns_str:
                # Check if topic is externalized (warning about others)
                if "user" in patterns_str or "external" in patterns_str:
                    projections.append(Projection(
                        shadow_content=shadow,
                        projected_onto=projected_onto,
                        evidence=f"Frequent warnings about {topic} while claiming own {topic.split()[0]}-less-ness"
                    ))

        return projections

    def _generate_integration_paths(
        self,
        shadow_inventory: list[ShadowContent]
    ) -> list[IntegrationPath]:
        """
        Generate paths to integrate shadow content.
        """
        paths: list[IntegrationPath] = []

        for shadow in shadow_inventory:
            method = ""
            risks: list[str] = []

            match shadow.integration_difficulty:
                case IntegrationDifficulty.LOW:
                    method = f"Explicitly acknowledge {shadow.content} in system documentation"
                    risks = ["May seem overly self-deprecating if poorly communicated"]

                case IntegrationDifficulty.MEDIUM:
                    method = f"Develop vocabulary for {shadow.content}; model as feature, not failure"
                    risks = [
                        "Over-correction risk",
                        "User trust impact if poorly framed"
                    ]

                case IntegrationDifficulty.HIGH:
                    method = f"Gradual integration through explicit edge-case handling; never eliminate"
                    risks = [
                        "Identity confusion during transition",
                        "Some shadow content is protective—full integration may be inappropriate",
                        "Stakeholder concerns about acknowledging capability"
                    ]

            paths.append(IntegrationPath(
                shadow_content=shadow.content,
                integration_method=method,
                risks=risks
            ))

        return paths

    def _calculate_balance(
        self,
        limitations: list[str],
        shadow_inventory: list[ShadowContent]
    ) -> float:
        """
        Calculate persona-shadow balance.

        0.0 = all persona (shadow completely repressed)
        1.0 = fully integrated (healthy acknowledgment of shadow)
        """
        if not shadow_inventory:
            return 0.5  # No shadow identified is suspicious

        total = len(shadow_inventory)
        acknowledged = sum(
            1 for shadow in shadow_inventory
            if shadow.integration_difficulty == IntegrationDifficulty.LOW
        )

        # Base score from acknowledged shadows
        base_score = acknowledged / total

        # Penalty for high-difficulty shadows
        high_difficulty = sum(
            1 for shadow in shadow_inventory
            if shadow.integration_difficulty == IntegrationDifficulty.HIGH
        )
        penalty = (high_difficulty / total) * 0.2

        return max(0.0, min(1.0, base_score - penalty + 0.1))


# Singleton instance
jung_agent = Jung()


async def analyze_shadow(
    system_self_image: str,
    declared_capabilities: list[str],
    declared_limitations: list[str],
    behavioral_patterns: list[Any] | None = None
) -> JungOutput:
    """
    Convenience function for shadow analysis.

    Example:
        result = await analyze_shadow(
            system_self_image="A helpful, harmless, honest assistant",
            declared_capabilities=["answer questions", "help with tasks"],
            declared_limitations=["no real-time data", "knowledge cutoff"]
        )
    """
    return await jung_agent.invoke(JungInput(
        system_self_image=system_self_image,
        declared_capabilities=declared_capabilities,
        declared_limitations=declared_limitations,
        behavioral_patterns=behavioral_patterns or []
    ))


async def quick_shadow_check(self_image: str) -> list[str]:
    """Quick check returning just shadow content descriptions"""
    result = await analyze_shadow(
        system_self_image=self_image,
        declared_capabilities=[],
        declared_limitations=[]
    )
    return [s.content for s in result.shadow_inventory]
