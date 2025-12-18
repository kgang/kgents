"""
Garden Protocol Plan Node: AGENTESE interface for individual plans.

This module implements the Plan Node from spec/protocols/garden-protocol.md Part V.

Registered paths:
- self.forest.plan.{name}.manifest - Return plan state for observer
- self.forest.plan.{name}.letter - Return the letter (conversation with future self)
- self.forest.plan.{name}.tend - Update plan with a tending gesture
- self.forest.plan.{name}.dream - Generate void.* connections (dormant only)

Key insight from spec:
> "Plans are first-class AGENTESE entities."
> "The same input produces different outputs depending on season."

The PlanNode uses GardenPolynomial for season-dependent behavior:
- SPROUTING: exploration welcome
- BLOOMING: focused work expected
- COMPOSTING: reflection and extraction
- DORMANT: may dream (void.* connections)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .types import (
    GardenInput,
    GardenPlanHeader,
    GardenPolynomial,
    Gesture,
    GestureType,
    Mood,
    Season,
    Trajectory,
    parse_garden_header,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Plan Affordances
# =============================================================================

PLAN_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "letter",
    "tend",
    "dream",
)


# =============================================================================
# Project Root Detection
# =============================================================================

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_plans_dir() -> Path:
    """Get the plans directory."""
    return _PROJECT_ROOT / "plans"


# =============================================================================
# Plan Loading and Saving
# =============================================================================


async def load_plan(plan_name: str) -> GardenPlanHeader | None:
    """
    Load a plan by name from the plans directory.

    Looks for plans/{name}.md and parses the Garden Protocol header.
    Falls back to creating a default header if parsing fails.

    Args:
        plan_name: The plan name (e.g., "coalition-forge")

    Returns:
        GardenPlanHeader if found, None otherwise
    """
    plans_dir = _get_plans_dir()

    # Try direct match first
    plan_file = plans_dir / f"{plan_name}.md"
    if not plan_file.exists():
        # Try with dashes/underscores swapped
        alt_name = (
            plan_name.replace("-", "_")
            if "-" in plan_name
            else plan_name.replace("_", "-")
        )
        plan_file = plans_dir / f"{alt_name}.md"

    if not plan_file.exists():
        return None

    # Parse Garden Protocol header
    header = parse_garden_header(plan_file)
    if header:
        return header

    # Fall back to minimal header from file existence
    return GardenPlanHeader(
        path=f"self.forest.plan.{plan_name}",
        mood=Mood.CURIOUS,
        momentum=0.0,
        trajectory=Trajectory.PARKED,
        season=Season.DORMANT,
        last_gardened=date.today(),
        gardener="unknown",
        letter="",
        resonates_with=[],
    )


async def save_plan(header: GardenPlanHeader) -> bool:
    """
    Save a plan header to disk.

    Args:
        header: The GardenPlanHeader to save

    Returns:
        True if saved successfully, False otherwise
    """
    plans_dir = _get_plans_dir()
    plan_file = plans_dir / f"{header.name}.md"

    if not plan_file.exists():
        return False

    # Read existing content
    content = plan_file.read_text()

    # Replace YAML frontmatter
    if content.startswith("---"):
        # Find end of frontmatter
        end_idx = content.find("\n---\n", 3)
        if end_idx > 0:
            body = content[end_idx + 5 :]  # After second ---
        else:
            body = ""
    else:
        body = content

    # Write new header + body
    new_content = f"---\n{header.to_yaml()}---\n{body}"
    plan_file.write_text(new_content)
    return True


# =============================================================================
# Connection Discovery (for dream aspect)
# =============================================================================


async def find_resonances(
    plan: GardenPlanHeader,
    entropy_amount: float,
) -> list[dict[str, Any]]:
    """
    Find potential resonances (connections) with other plans.

    This is the void.* operation that discovers unexpected connections.
    Uses entropy budget to explore semantic connections.

    Args:
        plan: The plan to find resonances for
        entropy_amount: Amount of entropy to spend on exploration

    Returns:
        List of connection dicts with plan_name and reason
    """
    # Simple implementation: look for plans with similar names or themes
    connections: list[dict[str, Any]] = []
    plans_dir = _get_plans_dir()

    if not plans_dir.exists():
        return connections

    # Scan other plans
    for plan_file in plans_dir.glob("*.md"):
        if plan_file.stem.startswith("_"):
            continue

        other_name = plan_file.stem
        if other_name == plan.name:
            continue

        # Simple heuristic: shared word fragments
        plan_words = set(plan.name.lower().replace("-", " ").split())
        other_words = set(other_name.lower().replace("-", " ").split())

        if plan_words & other_words:
            connections.append(
                {
                    "plan_name": other_name,
                    "reason": f"Shared concepts: {plan_words & other_words}",
                    "entropy_cost": 0.01,
                }
            )

        # Also check if in resonates_with
        if other_name in plan.resonates_with:
            connections.append(
                {
                    "plan_name": other_name,
                    "reason": "Already resonates",
                    "entropy_cost": 0.0,
                }
            )

    # Limit based on entropy budget
    max_connections = int(entropy_amount / 0.01)
    return connections[:max_connections]


# =============================================================================
# Plan Node
# =============================================================================


@node("self.forest.plan", description="Garden Protocol - Individual plan operations")
@dataclass
class PlanNode(BaseLogosNode):
    """
    AGENTESE node for individual plan operations.

    Handles paths like:
    - self.forest.plan.coalition-forge.manifest
    - self.forest.plan.coalition-forge.letter
    - self.forest.plan.coalition-forge.tend
    - self.forest.plan.coalition-forge.dream

    The plan name is extracted from the path dynamically.

    Uses GardenPolynomial for season-dependent behavior:
    - SPROUTING: exploration welcome, high plasticity
    - BLOOMING: focused work expected, productive
    - FRUITING: harvesting results, documentation
    - COMPOSTING: extracting learnings, winding down
    - DORMANT: resting, may dream (void.* connections)
    """

    _handle: str = "self.forest.plan"

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-gated affordances for plan operations."""
        # All roles can manifest and read letters
        base = ("manifest", "letter")

        if archetype in ("meta", "ops"):
            return base + ("tend", "dream")

        return base

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Collapse to observer-appropriate representation.

        This is the required abstract method from BaseLogosNode.
        Returns a summary of the PlanNode's capabilities.
        """
        return BasicRendering(
            summary="Garden Protocol Plan Node",
            content="Plan operations via self.forest.plan.{name}.{aspect}\n\n"
            "Aspects:\n"
            "- manifest: View plan state\n"
            "- letter: Read letter to future self\n"
            "- tend: Update plan with gesture\n"
            "- dream: Generate void connections (dormant only)",
            metadata={
                "handle": self.handle,
                "affordances": list(PLAN_AFFORDANCES),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""
        # Extract plan name from kwargs (passed by gateway)
        plan_name = kwargs.pop("plan_name", "")

        match aspect:
            case "manifest":
                return await self._manifest_impl(observer, plan_name, **kwargs)
            case "letter":
                return await self._letter(observer, plan_name, **kwargs)
            case "tend":
                return await self._tend(observer, plan_name, **kwargs)
            case "dream":
                return await self._dream(observer, plan_name, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # Aspects
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("plans")],
        help="View plan state",
        long_help="Return plan state appropriate for this observer.",
        examples=["kg plan coalition-forge", "kg plan coalition-forge --json"],
        see_also=["letter", "tend"],
    )
    async def _manifest_impl(
        self,
        observer: "Umwelt[Any, Any]",
        plan_name: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Return plan state appropriate for this observer.

        AGENTESE: self.forest.plan.{name}.manifest

        The manifest shows the plan's current state including:
        - Mood and momentum
        - Season and trajectory
        - Last gardened date
        - Resonances with other plans
        - Entropy budget status
        """
        plan = await load_plan(plan_name)

        if plan is None:
            return BasicRendering(
                summary=f"Plan Not Found: {plan_name}",
                content=f"No plan found with name '{plan_name}'",
                metadata={"status": "not_found", "plan_name": plan_name},
            )

        # Get valid inputs for current season
        valid_inputs = GardenPolynomial.directions(plan.season)
        input_names = [i.value for i in valid_inputs]

        # Build human-readable output
        lines = [
            f"# {plan.name}",
            "",
            f"**Mood**: {plan.mood.value}",
            f"**Momentum**: {plan.momentum:.0%}",
            f"**Trajectory**: {plan.trajectory.value}",
            f"**Season**: {plan.season.value.upper()}",
            "",
            f"**Last Gardened**: {plan.last_gardened.isoformat()}",
            f"**Gardener**: {plan.gardener}",
            "",
            "## Valid Inputs",
            "",
        ]
        for name in input_names:
            lines.append(f"- {name}")

        if plan.resonates_with:
            lines.extend(
                [
                    "",
                    "## Resonates With",
                    "",
                ]
            )
            for r in plan.resonates_with:
                lines.append(f"- {r}")

        lines.extend(
            [
                "",
                "## Entropy Budget",
                "",
                f"- Available: {plan.entropy.available:.2f}",
                f"- Spent: {plan.entropy.spent:.2f}",
                f"- Remaining: {plan.entropy.remaining:.2f}",
                f"- Exhausted: {plan.entropy.exhausted}",
            ]
        )

        if plan.entropy.sips:
            lines.extend(
                [
                    "",
                    "### Recent Sips",
                    "",
                ]
            )
            for sip in plan.entropy.sips[-5:]:  # Last 5 sips
                lines.append(f"- {sip}")

        content = "\n".join(lines)

        return BasicRendering(
            summary=f"Plan: {plan.name} ({plan.season.value})",
            content=content,
            metadata={
                "status": "live",
                "plan_name": plan.name,
                "mood": plan.mood.value,
                "momentum": plan.momentum,
                "trajectory": plan.trajectory.value,
                "season": plan.season.value,
                "valid_inputs": input_names,
                "entropy_remaining": plan.entropy.remaining,
                "entropy_exhausted": plan.entropy.exhausted,
                "resonates_with": plan.resonates_with,
                # Backwards compatibility
                "progress": plan.progress_equivalent,
                "status_equivalent": plan.status_equivalent,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("plans")],
        help="Read letter to future self",
        long_help="Return the letter (conversation with future self) from this plan.",
        examples=["kg plan coalition-forge letter"],
        see_also=["manifest", "tend"],
    )
    async def _letter(
        self,
        observer: "Umwelt[Any, Any]",
        plan_name: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Return the letter (conversation with future self).

        AGENTESE: self.forest.plan.{name}.letter

        The letter replaces session_notes from Forest Protocol.
        It's a reflection, not a changelog.

        Anti-pattern from spec:
        > Letter as log: "2025-12-18: Did X. Did Y." (BAD)
        > Letter is reflection, not changelog. (GOOD)
        """
        plan = await load_plan(plan_name)

        if plan is None:
            return BasicRendering(
                summary=f"Plan Not Found: {plan_name}",
                content=f"No plan found with name '{plan_name}'",
                metadata={"status": "not_found", "plan_name": plan_name},
            )

        if not plan.letter:
            return BasicRendering(
                summary=f"No Letter: {plan.name}",
                content=f"Plan '{plan.name}' has no letter yet.\n\nWrite one via `tend` with a letter gesture.",
                metadata={
                    "status": "empty",
                    "plan_name": plan.name,
                    "season": plan.season.value,
                },
            )

        # Format letter with context
        lines = [
            f"# Letter from {plan.name}",
            "",
            f"*Season: {plan.season.value.upper()} | Mood: {plan.mood.value} | {plan.last_gardened.isoformat()}*",
            "",
            "---",
            "",
            plan.letter,
        ]

        content = "\n".join(lines)

        return BasicRendering(
            summary=f"Letter: {plan.name}",
            content=content,
            metadata={
                "status": "live",
                "plan_name": plan.name,
                "letter_length": len(plan.letter),
                "season": plan.season.value,
                "mood": plan.mood.value,
                "last_gardened": plan.last_gardened.isoformat(),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("plans")],
        help="Update plan with gesture",
        long_help="Update plan state with a tending gesture (code, insight, decision, etc.).",
        examples=[
            "kg plan coalition-forge tend --gesture code --summary 'Added events'"
        ],
        see_also=["manifest", "letter"],
    )
    async def _tend(
        self,
        observer: "Umwelt[Any, Any]",
        plan_name: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Update plan state with a tending gesture.

        AGENTESE: self.forest.plan.{name}.tend

        Tending is the primary way to update a plan. It accepts:
        - gesture_type: code, insight, decision, void_sip, void_tithe, connect, prune
        - summary: Description of what was done
        - files: Optional list of files affected
        - letter: Optional letter update
        - mood: Optional mood change
        - momentum_delta: Optional momentum adjustment

        The input is validated against the current season using GardenPolynomial.
        """
        plan = await load_plan(plan_name)

        if plan is None:
            return BasicRendering(
                summary=f"Plan Not Found: {plan_name}",
                content=f"No plan found with name '{plan_name}'",
                metadata={"status": "not_found", "plan_name": plan_name},
            )

        # Extract gesture parameters
        gesture_type_str = kwargs.get("gesture_type", "code")
        summary = kwargs.get("summary", "")
        files = kwargs.get("files", [])
        letter_update = kwargs.get("letter")
        mood_str = kwargs.get("mood")
        momentum_delta = kwargs.get("momentum_delta", 0.0)

        # Parse gesture type
        try:
            gesture_type = GestureType(gesture_type_str)
        except ValueError:
            return BasicRendering(
                summary="Invalid Gesture Type",
                content=f"Unknown gesture type: {gesture_type_str}\n\nValid types: {[t.value for t in GestureType]}",
                metadata={"status": "error", "error": "invalid_gesture_type"},
            )

        # Map gesture type to GardenInput for polynomial validation
        gesture_to_input = {
            GestureType.CODE: GardenInput.BUILD,
            GestureType.INSIGHT: GardenInput.EXPLORE,
            GestureType.DECISION: GardenInput.DEFINE,
            GestureType.VOID_SIP: GardenInput.DREAM,
            GestureType.VOID_TITHE: GardenInput.TITHE,
            GestureType.CONNECT: GardenInput.CONNECT,
            GestureType.PRUNE: GardenInput.ARCHIVE,
        }

        garden_input = gesture_to_input.get(gesture_type)
        if garden_input:
            valid_inputs = GardenPolynomial.directions(plan.season)
            if garden_input not in valid_inputs:
                # Warn but don't block - transitions are suggestions, not enforced
                warning = f"Warning: '{gesture_type.value}' is unusual for {plan.season.value} season"
            else:
                warning = None
        else:
            warning = None

        # Create gesture (for future session integration)
        _gesture = Gesture(
            type=gesture_type,
            plan=plan_name,
            summary=summary,
            files=files if files else [],
        )

        # Update plan
        plan.last_gardened = date.today()
        plan.gardener = getattr(observer, "name", "unknown")

        # Apply momentum delta
        new_momentum = max(0.0, min(1.0, plan.momentum + momentum_delta))

        # Apply mood change
        new_mood = plan.mood
        if mood_str:
            try:
                new_mood = Mood(mood_str)
            except ValueError:
                pass  # Keep existing mood

        # Apply letter update (for future save_plan integration)
        _new_letter = plan.letter
        if letter_update:
            _new_letter = letter_update

        # Handle entropy for void gestures
        entropy_spent = 0.0
        if gesture_type == GestureType.VOID_SIP:
            if plan.entropy.sip(summary):
                entropy_spent = 0.02
            else:
                return BasicRendering(
                    summary="Entropy Exhausted",
                    content=f"Cannot sip: entropy budget exhausted.\n\nSpent: {plan.entropy.spent:.2f} / {plan.entropy.available:.2f}\n\nConsider transitioning to COMPOSTING and tithing.",
                    metadata={
                        "status": "error",
                        "error": "entropy_exhausted",
                        "entropy_spent": plan.entropy.spent,
                        "entropy_available": plan.entropy.available,
                    },
                )
        elif gesture_type == GestureType.VOID_TITHE:
            plan.entropy.tithe()

        # Check for season transition (invoke polynomial if input is valid)
        new_season = plan.season
        if garden_input and garden_input in GardenPolynomial.directions(plan.season):
            new_season, _ = GardenPolynomial.invoke(plan.season, garden_input)

        # Build result summary
        changes = []
        if new_momentum != plan.momentum:
            changes.append(f"momentum: {plan.momentum:.0%} -> {new_momentum:.0%}")
        if new_mood != plan.mood:
            changes.append(f"mood: {plan.mood.value} -> {new_mood.value}")
        if new_season != plan.season:
            changes.append(f"season: {plan.season.value} -> {new_season.value}")
        if letter_update:
            changes.append("letter updated")
        if entropy_spent:
            changes.append(f"entropy: -{entropy_spent:.2f}")

        # NOTE: Not actually saving to disk in this implementation
        # Real implementation would call save_plan() here

        result_lines = [
            f"# Tended: {plan_name}",
            "",
            f"**Gesture**: {gesture_type.value}",
            f"**Summary**: {summary}",
            "",
        ]

        if files:
            result_lines.append("**Files**:")
            for f in files:
                result_lines.append(f"- {f}")
            result_lines.append("")

        if changes:
            result_lines.append("**Changes**:")
            for c in changes:
                result_lines.append(f"- {c}")
        else:
            result_lines.append("*No state changes*")

        if warning:
            result_lines.extend(["", f"*{warning}*"])

        content = "\n".join(result_lines)

        return BasicRendering(
            summary=f"Tended: {plan_name} ({gesture_type.value})",
            content=content,
            metadata={
                "status": "ok",
                "plan_name": plan_name,
                "gesture_type": gesture_type.value,
                "summary": summary,
                "files": files,
                "changes": changes,
                "new_season": new_season.value,
                "new_momentum": new_momentum,
                "new_mood": new_mood.value,
                "entropy_spent": entropy_spent,
                "warning": warning,
            },
        )

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("plans")],
        help="Generate void connections",
        long_help="Generate speculative connections from void.* for dormant plans.",
        examples=["kg plan old-plan dream"],
        see_also=["manifest", "tend"],
    )
    async def _dream(
        self,
        observer: "Umwelt[Any, Any]",
        plan_name: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Generate speculative connections from void.*.

        AGENTESE: self.forest.plan.{name}.dream

        Dreams are only available for DORMANT plans. They draw from void.*
        to discover unexpected connections between plans.

        From spec:
        > "Only dormant plans dream."
        > "Draw from void, generate semantic connections."
        """
        plan = await load_plan(plan_name)

        if plan is None:
            return BasicRendering(
                summary=f"Plan Not Found: {plan_name}",
                content=f"No plan found with name '{plan_name}'",
                metadata={"status": "not_found", "plan_name": plan_name},
            )

        # Check if dormant
        if plan.season != Season.DORMANT:
            return BasicRendering(
                summary=f"Not Dormant: {plan_name}",
                content=f"Only dormant plans can dream.\n\nCurrent season: {plan.season.value.upper()}\n\nTo dream, transition to DORMANT via COMPOSTING -> ARCHIVE.",
                metadata={
                    "status": "error",
                    "error": "not_dormant",
                    "current_season": plan.season.value,
                },
            )

        # Find resonances
        entropy_amount = kwargs.get("entropy_amount", 0.05)
        connections = await find_resonances(plan, entropy_amount)

        if not connections:
            return BasicRendering(
                summary=f"No Dreams: {plan_name}",
                content=f"The plan '{plan_name}' dreams of connections not yet made...\n\nNo resonances discovered this time.",
                metadata={
                    "status": "empty",
                    "plan_name": plan_name,
                    "connections": [],
                },
            )

        # Build output
        lines = [
            f"# Dreams of {plan_name}",
            "",
            f"*{plan.mood.value.title()} dreams while resting...*",
            "",
            "## Discovered Resonances",
            "",
        ]

        total_entropy = 0.0
        for conn in connections:
            lines.append(f"### {conn['plan_name']}")
            lines.append(f"- **Reason**: {conn['reason']}")
            lines.append(f"- **Entropy cost**: {conn['entropy_cost']:.2f}")
            lines.append("")
            total_entropy += conn["entropy_cost"]

        lines.extend(
            [
                "---",
                "",
                f"*Total entropy spent: {total_entropy:.2f}*",
            ]
        )

        content = "\n".join(lines)

        return BasicRendering(
            summary=f"Dreams: {plan_name} ({len(connections)} connections)",
            content=content,
            metadata={
                "status": "live",
                "plan_name": plan_name,
                "connections": connections,
                "entropy_spent": total_entropy,
            },
        )


# =============================================================================
# Factory Functions
# =============================================================================

_plan_node: PlanNode | None = None


def get_plan_node() -> PlanNode:
    """Get the singleton PlanNode instance."""
    global _plan_node
    if _plan_node is None:
        _plan_node = PlanNode()
    return _plan_node


__all__ = [
    "PLAN_AFFORDANCES",
    "PlanNode",
    "get_plan_node",
    "load_plan",
    "save_plan",
    "find_resonances",
]
