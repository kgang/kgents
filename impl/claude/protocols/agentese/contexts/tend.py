"""
AGENTESE Tend Context: Six Tending Gestures.

self.garden.tend.* handles the tending calculus with six primitive gestures:
- self.garden.tend.observe  - Perceive without changing
- self.garden.tend.prune    - Remove what no longer serves
- self.garden.tend.graft    - Add something new
- self.garden.tend.water    - Nurture via TextGRAD
- self.garden.tend.rotate   - Change perspective
- self.garden.tend.wait     - Allow time to pass

These gestures all have entropy costs that vary by season plasticity.

Wave 2.5: Migrated from CLI handler to AGENTESE-native.
Per plans/cli/wave2.5-gardener-migration.md

AGENTESE: self.garden.tend.*

Principle Alignment:
- Tasteful: Six primitive operations
- Ethical: Observer-attributed changes
- Joy-Inducing: Visible entropy costs
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# Tending affordances (six verbs)
TEND_AFFORDANCES: tuple[str, ...] = (
    "observe",
    "prune",
    "graft",
    "water",
    "rotate",
    "wait",
)


@node(
    "self.garden.tend",
    description="Six tending gestures for garden interaction",
    dependencies=(),  # Uses protocols.gardener_logos directly
)
@dataclass
class TendNode(BaseLogosNode):
    """
    self.garden.tend - Six tending gestures.

    The tending calculus provides six primitive gestures for
    gardener-world interaction, each with entropy costs.

    AGENTESE: self.garden.tend.*
    """

    _handle: str = "self.garden.tend"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All tending gestures available to all archetypes."""
        return TEND_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="View available tending gestures",
        examples=["kg tend"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View tending gestures and entropy costs."""
        gestures = [
            ("👁️", "observe", "Perceive without changing", 0.01),
            ("✂️", "prune", "Remove what no longer serves", 0.15),
            ("🌱", "graft", "Add something new", 0.25),
            ("💧", "water", "Nurture via TextGRAD", 0.10),
            ("🔄", "rotate", "Change perspective", 0.05),
            ("⏳", "wait", "Allow time to pass", 0.00),
        ]

        lines = ["Six Tending Gestures:", ""]
        for emoji, verb, desc, cost in gestures:
            lines.append(f"  {emoji} {verb:8} - {desc} (cost: {cost:.2f})")

        return BasicRendering(
            summary="Tending Gestures",
            content="\n".join(lines),
            metadata={
                "gestures": [
                    {"verb": v, "description": d, "entropy_cost": c} for _, v, d, c in gestures
                ]
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle tending gestures."""
        match aspect:
            case "observe":
                return await self._observe(observer, **kwargs)
            case "prune":
                return await self._prune(observer, **kwargs)
            case "graft":
                return await self._graft(observer, **kwargs)
            case "water":
                return await self._water(observer, **kwargs)
            case "rotate":
                return await self._rotate(observer, **kwargs)
            case "wait":
                return await self._wait(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Observe without changing (nearly free)",
        examples=["kg tend observe concept.gardener"],
    )
    async def _observe(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """OBSERVE gesture - perceive without changing."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, observe

        target = kwargs.get("target")
        if not target:
            return {"status": "error", "message": "observe requires target"}

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = observe(target, f"Observing {target}")
        result = await apply_gesture(garden, gesture)

        return {
            "verb": "observe",
            "target": target,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "observations": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
            "success": result.success,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Mark for removal (requires reason)",
        examples=["kg tend prune concept.old --reason 'No longer used'"],
    )
    async def _prune(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """PRUNE gesture - remove what no longer serves."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, prune

        target = kwargs.get("target")
        reason = kwargs.get("reason")
        tone = kwargs.get("tone", 0.5)

        if not target:
            return {"status": "error", "message": "prune requires target"}
        if not reason:
            return {"status": "error", "message": "prune requires reason"}

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = prune(target, reason, float(tone))
        result = await apply_gesture(garden, gesture)

        return {
            "verb": "prune",
            "target": target,
            "reason": reason,
            "tone": tone,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "changes": result.changes,
            "reasoning": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
            "success": result.success,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Add something new (requires reason)",
        examples=["kg tend graft concept.new --reason 'New feature'"],
    )
    async def _graft(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """GRAFT gesture - add something new."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, graft

        target = kwargs.get("target")
        reason = kwargs.get("reason")
        tone = kwargs.get("tone", 0.5)

        if not target:
            return {"status": "error", "message": "graft requires target"}
        if not reason:
            return {"status": "error", "message": "graft requires reason"}

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = graft(target, reason, float(tone))
        result = await apply_gesture(garden, gesture)

        return {
            "verb": "graft",
            "target": target,
            "reason": reason,
            "tone": tone,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "changes": result.changes,
            "reasoning": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
            "success": result.success,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Nurture via TextGRAD (requires feedback)",
        examples=["kg tend water concept.prompt --feedback 'Add more specificity'"],
    )
    async def _water(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """WATER gesture - nurture via TextGRAD."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, water

        target = kwargs.get("target")
        feedback = kwargs.get("feedback")
        tone = kwargs.get("tone", 0.5)

        if not target:
            return {"status": "error", "message": "water requires target"}
        if not feedback:
            return {"status": "error", "message": "water requires feedback"}

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = water(target, feedback, float(tone))
        result = await apply_gesture(garden, gesture)

        # Calculate effective learning rate
        learning_rate = float(tone) * garden.season.plasticity

        return {
            "verb": "water",
            "target": target,
            "feedback": feedback,
            "tone": tone,
            "learning_rate": learning_rate,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "changes": result.changes,
            "synergies_triggered": result.synergies_triggered,
            "reasoning": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
            "success": result.success,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Change perspective (cheap)",
        examples=["kg tend rotate concept.gardener"],
    )
    async def _rotate(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """ROTATE gesture - change perspective."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, rotate

        target = kwargs.get("target")
        reason = kwargs.get("reason", "")

        if not target:
            return {"status": "error", "message": "rotate requires target"}

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = rotate(target, reason or f"Rotating perspective on {target}")
        result = await apply_gesture(garden, gesture)

        return {
            "verb": "rotate",
            "target": target,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "reasoning": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
            "success": result.success,
        }

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[],  # No side effects
        help="Intentional pause (free)",
        examples=["kg tend wait", "kg tend wait --reason 'Allowing ideas to settle'"],
    )
    async def _wait(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """WAIT gesture - allow time to pass."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.tending import apply_gesture, wait

        reason = kwargs.get("reason", "Allowing time to pass")

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        gesture = wait(reason)
        result = await apply_gesture(garden, gesture)

        return {
            "verb": "wait",
            "reason": reason,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "reasoning": list(result.reasoning_trace),
            "entropy_cost": 0.0,  # Waiting is always free
            "success": result.success,
        }


# Factory function
def create_tend_node() -> TendNode:
    """Create a TendNode for self.garden.tend.* paths."""
    return TendNode()


__all__ = [
    "TendNode",
    "TEND_AFFORDANCES",
    "create_tend_node",
]
