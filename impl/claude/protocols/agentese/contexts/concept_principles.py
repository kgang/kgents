"""
concept.principles AGENTESE Node

The queryable knowledge layer for kgents principles.
Exposes the Seven Principles and their derivatives through stance-aware aspects.

The Four Stances:
- Genesis: Becoming - which principles apply?
- Poiesis: Making - how do I build according to principles?
- Krisis: Judgment - does this embody the principles?
- Therapeia: Healing - which principle was violated?

See: spec/principles/node.md for the authoritative specification.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.node import AgentMeta, BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node
from services.principles import (
    PrincipleChecker,
    PrincipleHealer,
    PrincipleLoader,
    PrincipleProjection,
    PrincipleTeacher,
    Stance,
    create_principle_checker,
    create_principle_healer,
    create_principle_loader,
    create_principle_teacher,
    detect_stance,
    get_stance_slices,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer

logger = logging.getLogger(__name__)


# === Node Registration ===


@node(
    "concept.principles",
    description="The kgents design principles - queryable, stance-aware",
    examples=[
        ("manifest", {}, "View principles for your stance"),
        ("constitution", {}, "The Seven Immutable Principles"),
        ("check", {"target": "my_agent"}, "Validate against principles"),
        ("teach", {"principle": 5, "depth": "examples"}, "Learn about Composable"),
    ],
)
@dataclass
class PrinciplesNode(BaseLogosNode):
    """
    AGENTESE node for principle consumption.

    Provides stance-aware access to kgents principles through aspects:
    - manifest: Stance-aware principle projection
    - constitution: The seven immutable principles
    - meta: Meta-principles (Accursed Share, AGENTESE, Personality Space)
    - operational: Tactical implementation guidance
    - ad: Architectural decisions (by ID or category)
    - check: Validate a target against principles (Krisis)
    - teach: Interactive teaching mode
    - heal: Get healing prescription for violations (Therapeia)
    """

    _loader: PrincipleLoader = field(default_factory=create_principle_loader)
    _checker: PrincipleChecker = field(default_factory=create_principle_checker)

    def __post_init__(self) -> None:
        """Initialize healer and teacher with loader."""
        self._healer = create_principle_healer(self._loader)
        self._teacher = create_principle_teacher(self._loader)

    @property
    def handle(self) -> str:
        return "concept.principles"

    # === Archetype Affordances ===

    # Class-level constant (excluded from dataclass fields via ClassVar)
    _ARCHETYPE_AFFORDANCES: ClassVar[dict[str, tuple[str, ...]]] = {
        "developer": ("check", "heal", "ad"),
        "architect": ("check", "heal", "ad", "teach"),
        "reviewer": ("check",),
        "learner": ("teach",),
        "guest": (),
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        return self._ARCHETYPE_AFFORDANCES.get(archetype, ())

    # === Aspect Hints ===

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View principles filtered by your stance (genesis/poiesis/krisis/therapeia)",
        "constitution": "Read the Seven Immutable Principles",
        "meta": "Explore meta-principles (Accursed Share, AGENTESE, Personality Space)",
        "operational": "Get tactical implementation guidance",
        "ad": "Look up architectural decisions by ID or category",
        "check": "Validate a target against the seven principles",
        "teach": "Learn about principles with examples and exercises",
        "heal": "Get a healing prescription for a principle violation",
    }

    # === Core Aspects ===

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Stance-aware principle projection",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        stance: str | None = None,
        task: str | None = None,
    ) -> Renderable:
        """
        Collapse principles to observer's stance.

        Args:
            observer: The observer context
            stance: Optional explicit stance (genesis/poiesis/krisis/therapeia)
            task: Optional task context for stance detection

        Returns:
            PrincipleProjection with stance-appropriate content
        """
        # Detect or parse stance
        if stance:
            try:
                detected_stance = Stance(stance.lower())
            except ValueError:
                detected_stance = Stance.GENESIS
        else:
            detected_stance = detect_stance(observer=observer, task=task)

        # Load slices for this stance
        slices = get_stance_slices(detected_stance)
        content = await self._loader.load_slices(slices)

        projection = PrincipleProjection(
            stance=detected_stance,
            slices=slices,
            content=content,
        )

        return BasicRendering(
            summary=f"Principles ({detected_stance.value})",
            content=projection.to_text(),
            metadata=projection.to_dict(),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="The seven immutable principles",
    )
    async def constitution(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """
        Return the Seven Immutable Principles.

        Law: constitution() returns identical content across all observers.
        """
        rendering = await self._loader.load_constitution()

        return BasicRendering(
            summary="The Seven Principles",
            content=rendering.to_text(),
            metadata=rendering.to_dict(),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Meta-principles (Accursed Share, AGENTESE, Personality Space)",
    )
    async def meta(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        section: str | None = None,
    ) -> Renderable:
        """
        Return meta-principles.

        Args:
            observer: The observer context
            section: Optional specific section to load

        Returns:
            MetaPrincipleRendering
        """
        rendering = await self._loader.load_meta(section=section)

        return BasicRendering(
            summary=f"Meta: {section or 'All'}",
            content=rendering.to_text(),
            metadata=rendering.to_dict(),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Tactical implementation guidance",
    )
    async def operational(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Return operational principles."""
        rendering = await self._loader.load_operational()

        return BasicRendering(
            summary="Operational Principles",
            content=rendering.to_text(),
            metadata=rendering.to_dict(),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Architectural decisions by ID or category",
    )
    async def ad(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        ad_id: int | None = None,
        category: str | None = None,
    ) -> Renderable:
        """
        Load architectural decisions.

        Args:
            observer: The observer context
            ad_id: Specific AD number (1-13)
            category: Category (categorical, design-philosophy, architecture, protocol, ui)

        Returns:
            ADRendering
        """
        if ad_id:
            rendering = await self._loader.load_ad(ad_id)
        elif category:
            rendering = await self._loader.load_ads_by_category(category)
        else:
            rendering = await self._loader.load_ad_index()

        return BasicRendering(
            summary=f"AD-{ad_id:03d}" if ad_id else f"ADs: {category or 'Index'}",
            content=rendering.to_text(),
            metadata=rendering.to_dict(),
        )

    @aspect(
        category=AspectCategory.INTROSPECTION,
        description="Validate a target against the seven principles",
        effects=[Effect.READS("principles")],
    )
    async def check(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        target: str,
        principles: list[int] | None = None,
        context: str | None = None,
    ) -> Renderable:
        """
        Check a target against principles (Krisis stance).

        Law: check() always evaluates all seven principles unless filtered.

        Args:
            observer: The observer context
            target: Target to check (description, code, or identifier)
            principles: Optional list of principle numbers to check
            context: Optional additional context

        Returns:
            CheckResult
        """
        result = await self._checker.check(
            target=target,
            observer=observer,  # type: ignore[arg-type]
            principles=principles,
            context=context,
        )

        return BasicRendering(
            summary=f"Check: {'PASSED' if result.passed else 'FAILED'}",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Interactive teaching mode",
    )
    async def teach(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        principle: int | str | None = None,
        depth: Literal["overview", "examples", "exercises"] = "overview",
    ) -> Renderable:
        """
        Get teaching content for principles.

        Args:
            observer: The observer context
            principle: Principle number/name, or None for all
            depth: Level of detail (overview, examples, exercises)

        Returns:
            TeachingContent
        """
        content = await self._teacher.teach(principle=principle, depth=depth)

        return BasicRendering(
            summary=f"Teach: {content.principle_name or 'All'} ({depth})",
            content=content.to_text(),
            metadata=content.to_dict(),
        )

    @aspect(
        category=AspectCategory.MUTATION,
        description="Get healing prescription for a principle violation",
        effects=[Effect.READS("principles"), Effect.READS("puppets")],
    )
    async def heal(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        violation: int | str,
        context: str | None = None,
    ) -> Renderable:
        """
        Get healing prescription for a violation (Therapeia stance).

        Law: heal(violation) always returns at least one prescription path.

        Args:
            observer: The observer context
            violation: Principle number (1-7) or name
            context: Optional context about what went wrong

        Returns:
            HealingPrescription
        """
        prescription = await self._healer.heal(violation=violation, context=context)

        return BasicRendering(
            summary=f"Heal: {prescription.principle_name}",
            content=prescription.to_text(),
            metadata=prescription.to_dict(),
        )

    # === Invoke Routing ===

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to methods."""
        aspect_map: dict[str, Any] = {
            "constitution": self.constitution,
            "meta": self.meta,
            "operational": self.operational,
            "ad": self.ad,
            "check": self.check,
            "teach": self.teach,
            "heal": self.heal,
        }

        handler = aspect_map.get(aspect)
        if handler is not None:
            return await handler(observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory Function ===


def get_principles_node() -> PrinciplesNode:
    """Get a PrinciplesNode instance."""
    return PrinciplesNode()


# === Exports ===

__all__ = [
    "PrinciplesNode",
    "get_principles_node",
]
