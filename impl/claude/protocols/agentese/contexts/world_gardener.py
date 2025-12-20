"""
AGENTESE Gardener Context: Cultivation Practice for Ideas.

The concept.gardener context provides access to:
- concept.gardener.session.* - Session lifecycle (SENSE → ACT → REFLECT)
- self.garden.* - Idea planting, nurturing, harvesting
- void.garden.sip - Serendipity from the void

This module defines GardenerNode which handles gardener-level operations.

AGENTESE: concept.gardener.*, self.garden.*, void.garden.*

Principle Alignment:
- Joy-Inducing: Gardening metaphor brings delight to development
- Composable: Sessions are polynomial state machines
- Generative: Ideas grow through evidence and time
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from agents.gardener.handlers import GardenerContext
    from agents.k.garden import GardenEntry, PersonaGarden
    from bootstrap.umwelt import Umwelt


# Gardener affordances available at concept.gardener.*
GARDENER_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "session",
    "start",
    "advance",
    "cycle",
    "polynomial",
    "sessions",
    "intent",
    "chat",
)

# Garden affordances available at self.garden.*
GARDEN_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "plant",
    "harvest",
    "nurture",
    "status",
    "harvest_to_brain",
)

# Void affordances at void.garden.*
VOID_GARDEN_AFFORDANCES: tuple[str, ...] = ("sip",)


# =============================================================================
# PHASE_CONFIG - Session polynomial phases
# =============================================================================

PHASE_CONFIG = {
    "SENSE": {
        "emoji": "👁️",
        "label": "Sensing",
        "color": "cyan",
        "desc": "Gather context",
    },
    "ACT": {
        "emoji": "⚡",
        "label": "Acting",
        "color": "yellow",
        "desc": "Execute intent",
    },
    "REFLECT": {
        "emoji": "💭",
        "label": "Reflecting",
        "color": "purple",
        "desc": "Consolidate learnings",
    },
}


# =============================================================================
# GardenerNode - concept.gardener.*
# =============================================================================


@dataclass
class GardenerNode(BaseLogosNode):
    """
    concept.gardener - Development Session Management.

    The Gardener Crown Jewel provides:
    - Session lifecycle with SENSE → ACT → REFLECT polynomial
    - Visible state machine for development cycles
    - Garden access for idea lifecycle management

    Storage:
    - services/gardener/persistence.py for database persistence
    - D-gent datums for session notes and idea content
    """

    _handle: str = "concept.gardener"

    # Session context (lazy-loaded)
    _context: "GardenerContext | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Gardener affordances - available to all archetypes."""
        return GARDENER_AFFORDANCES

    async def _get_context(self) -> "GardenerContext":
        """Get or create GardenerContext."""
        if self._context is None:
            from agents.gardener.handlers import GardenerContext
            from agents.gardener.persistence import create_session_store

            store = create_session_store()
            self._context = GardenerContext(store=store)
            await self._context.init()
        return self._context

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("gardener_session"), Effect.READS("garden_state")],
        help="Show current session status and garden overview",
        examples=["kg gardener", "kg gardener status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show session status and garden overview."""
        ctx = await self._get_context()
        garden = await _get_garden()
        stats = await garden.stats()

        if not ctx.active_session:
            return BasicRendering(
                summary="The Gardener: No Active Session",
                content=(
                    "No active gardener session.\n\n"
                    "Start one with: kg gardener start\n\n"
                    f"Garden Status:\n{_format_garden_stats(stats)}"
                ),
                metadata={
                    "status": "no_session",
                    "garden": stats.__dict__ if hasattr(stats, "__dict__") else {},
                },
            )

        session = ctx.active_session
        state = session.state
        phase_cfg = PHASE_CONFIG[session.phase.name]

        lines = [
            f"Session: {state.name}",
            f"ID: {session.session_id}",
            "",
            f"State Machine: {_render_polynomial(session.phase.name)}",
            "",
            f"Current Phase: {phase_cfg['emoji']} {phase_cfg['label']}",
            f"  {phase_cfg['desc']}",
        ]

        if state.intent:
            intent_dict = state.intent.to_dict() if hasattr(state.intent, "to_dict") else {}
            lines.extend(
                [
                    "",
                    f"Intent: {intent_dict.get('description', 'No description')}",
                    f"  Priority: {intent_dict.get('priority', 'normal')}",
                ]
            )

        if state.plan_path:
            lines.append(f"\nPlan: {state.plan_path}")

        lines.extend(
            [
                "",
                "Counts:",
                f"  Sense: {state.sense_count} | Act: {state.act_count} | Reflect: {state.reflect_count}",
            ]
        )

        valid_next = {
            "SENSE": "advance",
            "ACT": "advance or rollback",
            "REFLECT": "cycle",
        }
        lines.append(f"\nNext: kg gardener {valid_next.get(session.phase.name, 'advance')}")
        lines.append("")
        lines.append(_format_garden_stats(stats))

        return BasicRendering(
            summary=f"Session: {state.name} ({session.phase.name})",
            content="\n".join(lines),
            metadata={
                "status": "active",
                "session_id": session.session_id,
                "name": state.name,
                "phase": session.phase.name,
                "intent": state.intent.to_dict() if state.intent else None,
                "counts": {
                    "sense": state.sense_count,
                    "act": state.act_count,
                    "reflect": state.reflect_count,
                },
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("gardener_session")],
        help="Start a new development session",
        examples=[
            "kg gardener start",
            "kg gardener start 'Crown Jewels Implementation'",
        ],
    )
    async def start(
        self,
        observer: "Umwelt[Any, Any]",
        name: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Start a new gardener session."""
        from protocols.agentese.node import Observer

        ctx = await self._get_context()

        from agents.gardener.handlers import handle_session_create

        # Observer is a dataclass, convert to dict manually
        obs = Observer.guest()
        obs_dict = {
            "archetype": obs.archetype,
            "capabilities": list(obs.capabilities),
        }

        create_kwargs: dict[str, Any] = {}
        if name:
            create_kwargs["name"] = name

        result = await handle_session_create(ctx, obs_dict, **create_kwargs)

        if result.get("status") == "error":
            return BasicRendering(
                summary="Session Start Failed",
                content=f"Error: {result.get('message')}",
                metadata={"error": result.get("message")},
            )

        session_data = result.get("session", {})
        return BasicRendering(
            summary=f"Session Started: {session_data.get('name', 'Unnamed')}",
            content=(
                f"Session Started!\n\n"
                f"Name: {session_data.get('name', 'Unnamed')}\n"
                f"ID: {session_data.get('session_id', 'unknown')[:8]}...\n"
                f"Phase: SENSE (Gather context)\n\n"
                "The session begins in SENSE phase. Read plans, explore codebase, gather context."
            ),
            metadata=session_data,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("gardener_session")],
        help="Advance to the next phase",
        examples=["kg gardener advance"],
    )
    async def advance(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Advance to the next phase."""
        from protocols.agentese.node import Observer

        ctx = await self._get_context()

        if not ctx.active_session:
            return BasicRendering(
                summary="No Active Session",
                content="No active session. Start one with: kg gardener start",
                metadata={"error": "no_session"},
            )

        from agents.gardener.handlers import handle_session_advance

        # Observer is a dataclass, convert to dict manually
        obs = Observer.guest()
        obs_dict = {
            "archetype": obs.archetype,
            "capabilities": list(obs.capabilities),
        }
        result = await handle_session_advance(ctx, obs_dict)

        if result.get("status") == "error":
            return BasicRendering(
                summary="Advance Failed",
                content=f"Error: {result.get('message')}",
                metadata={"error": result.get("message")},
            )

        new_phase = ctx.active_session.phase.name
        phase_cfg = PHASE_CONFIG[new_phase]

        return BasicRendering(
            summary=f"Advanced to {new_phase}",
            content=(
                f"Advanced!\n\n"
                f"New phase: {phase_cfg['emoji']} {phase_cfg['label']}\n"
                f"{phase_cfg['desc']}\n\n"
                f"{_render_polynomial(new_phase)}"
            ),
            metadata={"phase": new_phase},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("gardener_session")],
        help="Start a new cycle (from REFLECT)",
        examples=["kg gardener cycle"],
    )
    async def cycle(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Start a new cycle (from REFLECT)."""
        return await self.advance(observer, **kwargs)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("gardener_session")],
        help="Show polynomial visualization in detail",
        examples=["kg gardener polynomial", "kg gardener poly"],
    )
    async def polynomial(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show polynomial state machine visualization."""
        ctx = await self._get_context()

        if not ctx.active_session:
            return BasicRendering(
                summary="No Active Session",
                content="No active session.",
                metadata={"error": "no_session"},
            )

        state = ctx.active_session.state
        current = ctx.active_session.phase.name

        diagram = """
    ┌─────────┐     advance     ┌─────────┐     advance    ┌───────────┐
    │  SENSE  │────────────────▶│   ACT   │───────────────▶│  REFLECT  │
    │   👁️   │                  │   ⚡    │                 │    💭     │
    └─────────┘                  └─────────┘                 └───────────┘
         ▲                            │                           │
         │                            │ rollback                  │
         │                            ▼                           │
         │                       ┌─────────┐                      │
         └───────────────────────│ SENSE ◀─┼──────────────────────┘
                   cycle         └─────────┘     cycle
"""

        valid = {
            "SENSE": ["ACT"],
            "ACT": ["REFLECT", "SENSE (rollback)"],
            "REFLECT": ["SENSE (cycle)"],
        }

        lines = [
            "Polynomial State Machine:",
            diagram,
            f"Current: {current}",
            f"Valid transitions: {', '.join(valid.get(current, []))}",
            "",
            "Session History:",
            f"  SENSE entered: {state.sense_count}x",
            f"  ACT entered: {state.act_count}x",
            f"  REFLECT completed: {state.reflect_count}x",
        ]

        return BasicRendering(
            summary=f"Polynomial: {current}",
            content="\n".join(lines),
            metadata={"phase": current, "valid_transitions": valid.get(current, [])},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("gardener_session")],
        help="List recent sessions",
        examples=["kg gardener sessions"],
    )
    async def sessions(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """List recent sessions."""
        ctx = await self._get_context()
        recent = await ctx.store.list_recent(limit=10)

        if not recent:
            return BasicRendering(
                summary="No Sessions Found",
                content="No sessions found.",
                metadata={"sessions": []},
            )

        active_id = ctx.active_session.session_id if ctx.active_session else None

        lines = ["Recent Sessions:", "=" * 50]
        for s in recent:
            is_active = s.id == active_id
            active_mark = " [ACTIVE]" if is_active else ""
            lines.append(f"  {s.id[:8]}... {s.name} ({s.phase}){active_mark}")

        return BasicRendering(
            summary=f"Sessions: {len(recent)} found",
            content="\n".join(lines),
            metadata={"sessions": [{"id": s.id, "name": s.name, "phase": s.phase} for s in recent]},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("gardener_session")],
        help="Set session intent",
        examples=["kg gardener intent 'Implement Park migration'"],
    )
    async def intent(
        self,
        observer: "Umwelt[Any, Any]",
        description: str,
        priority: str = "normal",
        **kwargs: Any,
    ) -> Renderable:
        """Set session intent."""
        ctx = await self._get_context()

        if not ctx.active_session:
            return BasicRendering(
                summary="No Active Session",
                content="No active session. Start one with: kg gardener start",
                metadata={"error": "no_session"},
            )

        from agents.gardener.session import SessionIntent

        ctx.active_session.state.intent = SessionIntent(
            description=description,
            priority=priority,
        )

        return BasicRendering(
            summary=f"Intent Set: {description[:40]}...",
            content=f"Intent set:\n  {description}\n  Priority: {priority}",
            metadata={"intent": {"description": description, "priority": priority}},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to gardener-specific aspects."""
        match aspect:
            case "start":
                return await self.start(observer, **kwargs)
            case "advance":
                return await self.advance(observer, **kwargs)
            case "cycle":
                return await self.cycle(observer, **kwargs)
            case "polynomial":
                return await self.polynomial(observer, **kwargs)
            case "sessions":
                return await self.sessions(observer, **kwargs)
            case "intent":
                return await self.intent(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on GardenerNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# GardenNode - self.garden.*
# =============================================================================


@dataclass
class GardenNode(BaseLogosNode):
    """
    self.garden - Idea Lifecycle Management.

    The Garden provides:
    - Plant ideas as seeds
    - Nurture ideas with evidence
    - Harvest mature ideas (flowers) to Brain
    - Serendipity from the void

    Lifecycle: seed → sapling → tree → flower → compost
    """

    _handle: str = "self.garden"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Garden affordances - available to all archetypes."""
        return GARDEN_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Show garden status with lifecycle distribution",
        examples=["kg gardener garden"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show garden lifecycle distribution."""
        garden = await _get_garden()
        stats = await garden.stats()

        lines = [
            "Garden Status",
            "=" * 40,
            "",
        ]

        lifecycle_icons = {
            "seed": "🌱",
            "sapling": "🌿",
            "tree": "🌳",
            "flower": "🌸",
            "compost": "🍂",
        }

        for lc in ["seed", "sapling", "tree", "flower", "compost"]:
            count = stats.by_lifecycle.get(lc, 0)
            icon = lifecycle_icons.get(lc, " ")
            label = lc.capitalize()
            extra = ""
            if lc == "flower" and count > 0:
                extra = " (ready to harvest!)"
            lines.append(f"  {icon} {label}: {count}{extra}")

        lines.extend(
            [
                "",
                f"  Season: {stats.current_season.value.upper()}",
                f"  Total entries: {stats.total_entries}",
            ]
        )

        if stats.total_entries == 0:
            lines.extend(
                [
                    "",
                    "Garden is empty. Plant an idea:",
                    '  kg gardener plant "your insight here"',
                ]
            )
        else:
            # Show top ideas
            from agents.k.garden import GardenLifecycle

            entries = list(garden.entries.values())
            non_compost = [e for e in entries if e.lifecycle != GardenLifecycle.COMPOST]
            by_confidence = sorted(non_compost, key=lambda e: -e.confidence)[:5]

            if by_confidence:
                lines.append("")
                lines.append("Top ideas (by confidence):")
                for entry in by_confidence:
                    icon = lifecycle_icons.get(entry.lifecycle.value, " ")
                    short_id = entry.id[:16] if len(entry.id) > 16 else entry.id
                    lines.append(f"  {icon} {entry.content[:40]} ({entry.confidence:.0%})")
                    lines.append(f"     ID: {short_id}")

        return BasicRendering(
            summary=f"Garden: {stats.total_entries} entries",
            content="\n".join(lines),
            metadata={
                "total": stats.total_entries,
                "by_lifecycle": stats.by_lifecycle,
                "season": stats.current_season.value,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Plant a new idea in the garden",
        examples=["kg gardener plant 'Polynomial agents capture state'"],
    )
    async def plant(
        self,
        observer: "Umwelt[Any, Any]",
        content: str,
        **kwargs: Any,
    ) -> Renderable:
        """Plant a new idea."""
        from agents.k.garden import EntryType

        garden = await _get_garden()

        entry = await garden.plant(
            content=content,
            entry_type=EntryType.INSIGHT,
            source="manual",
            confidence=0.4,
        )

        lifecycle_icons = {
            "seed": "🌱",
            "sapling": "🌿",
            "tree": "🌳",
            "flower": "🌸",
            "compost": "🍂",
        }
        icon = lifecycle_icons.get(entry.lifecycle.value, "🌱")

        return BasicRendering(
            summary=f"Idea Planted: {content[:30]}...",
            content=(
                f"Idea Planted!\n\n"
                f"{icon} {content}\n\n"
                f"Lifecycle: {entry.lifecycle.value.upper()}\n"
                f"Confidence: {entry.confidence:.0%}\n"
                f"ID: {entry.id[:12]}...\n\n"
                "Nurture it with evidence, or wait for it to bloom."
            ),
            metadata={
                "entry_id": entry.id,
                "lifecycle": entry.lifecycle.value,
                "confidence": entry.confidence,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Show ideas ready to harvest (FLOWER stage)",
        examples=["kg gardener harvest"],
    )
    async def harvest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show ideas ready to harvest."""
        garden = await _get_garden()
        flowers = await garden.flowers()

        if not flowers:
            trees = await garden.trees()
            lines = [
                "No flowers ready for harvest yet.",
                "",
                "Ideas need to reach high confidence (90%+) to bloom.",
                "Nurture them with evidence or wait for time to work.",
            ]
            if trees:
                lines.append("")
                lines.append("Closest to bloom (trees):")
                for tree in sorted(trees, key=lambda t: -t.confidence)[:3]:
                    lines.append(f"  🌳 {tree.content[:50]} ({tree.confidence:.0%})")

            return BasicRendering(
                summary="No Flowers Ready",
                content="\n".join(lines),
                metadata={"flowers": []},
            )

        lines = ["🌸 Ready to Harvest", ""]
        for flower in flowers:
            lines.extend(
                [
                    f"  🌸 {flower.content}",
                    f"     Confidence: {flower.confidence:.0%} | Age: {flower.age_days:.0f} days",
                ]
            )
            if flower.evidence:
                lines.append(f"     Evidence: {len(flower.evidence)} items")
            lines.append("")

        lines.append(f"{len(flowers)} idea(s) ready for harvest.")
        lines.append("Harvested ideas can become Brain crystals.")

        return BasicRendering(
            summary=f"Flowers: {len(flowers)} ready",
            content="\n".join(lines),
            metadata={"flowers": [{"id": f.id, "content": f.content} for f in flowers]},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Water/nurture an idea to boost its confidence",
        examples=["kg gardener water <idea-id> 'evidence'"],
    )
    async def nurture(
        self,
        observer: "Umwelt[Any, Any]",
        idea_ref: str,
        evidence: str = "Manual nurturing",
        **kwargs: Any,
    ) -> Renderable:
        """Nurture an idea with evidence."""
        from agents.k.garden import GardenLifecycle

        garden = await _get_garden()

        # Find the idea by ID or partial ID
        target_entry = None
        for entry_id, entry in garden.entries.items():
            if entry_id == idea_ref or entry_id.startswith(idea_ref):
                target_entry = entry
                break

        if target_entry is None:
            # Try matching by content substring
            for entry in garden.entries.values():
                if idea_ref.lower() in entry.content.lower():
                    target_entry = entry
                    break

        if target_entry is None:
            return BasicRendering(
                summary="Idea Not Found",
                content=f"No idea found matching '{idea_ref}'",
                metadata={"error": "not_found"},
            )

        if target_entry.lifecycle == GardenLifecycle.COMPOST:
            return BasicRendering(
                summary="Cannot Water Composted Ideas",
                content=f"Cannot water composted ideas.\n'{target_entry.content[:40]}...' is in compost.",
                metadata={"error": "composted"},
            )

        old_confidence = target_entry.confidence
        old_lifecycle = target_entry.lifecycle
        updated = await garden.nurture(target_entry.id, evidence)

        if updated is None:
            return BasicRendering(
                summary="Nurture Failed",
                content="Error: Failed to nurture idea.",
                metadata={"error": "nurture_failed"},
            )

        lifecycle_icons = {
            "seed": "🌱",
            "sapling": "🌿",
            "tree": "🌳",
            "flower": "🌸",
            "compost": "🍂",
        }
        icon = lifecycle_icons.get(updated.lifecycle.value, "💧")

        lines = [
            "💧 Idea Watered!",
            "",
            f"  {icon} {updated.content}",
            "",
            f'  Evidence added: "{evidence}"',
            f"  Confidence: {old_confidence:.0%} → {updated.confidence:.0%}",
        ]

        if updated.lifecycle != old_lifecycle:
            old_icon = lifecycle_icons.get(old_lifecycle.value, " ")
            new_icon = lifecycle_icons.get(updated.lifecycle.value, " ")
            lines.append(
                f"  Lifecycle: {old_icon} {old_lifecycle.value} → {new_icon} {updated.lifecycle.value}"
            )

        if updated.lifecycle == GardenLifecycle.FLOWER:
            lines.append("")
            lines.append("  🌸 This idea has bloomed! Ready for harvest.")

        return BasicRendering(
            summary=f"Watered: {updated.content[:30]}...",
            content="\n".join(lines),
            metadata={
                "entry_id": updated.id,
                "old_confidence": old_confidence,
                "new_confidence": updated.confidence,
                "lifecycle": updated.lifecycle.value,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("garden_state"),
            Effect.WRITES("brain_crystals"),
        ],
        help="Harvest flower ideas and capture them as Brain crystals",
        examples=["kg gardener harvest-to-brain", "kg gardener reap"],
    )
    async def harvest_to_brain(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Harvest flowers to Brain crystals."""
        garden = await _get_garden()
        flowers = await garden.flowers()

        if not flowers:
            return BasicRendering(
                summary="No Flowers to Harvest",
                content="No flowers ready for harvest yet.\nIdeas need to reach 90%+ confidence to bloom.",
                metadata={"harvested": []},
            )

        try:
            from agents.brain import get_brain_crystal

            brain = await get_brain_crystal()
        except ImportError:
            return BasicRendering(
                summary="Brain Unavailable",
                content="Error: Brain module not available.",
                metadata={"error": "brain_unavailable"},
            )

        harvested = []
        for flower in flowers:
            content = f"[Harvested Idea] {flower.content}"
            metadata = {
                "source": "gardener_harvest",
                "garden_entry_id": flower.id,
                "evidence_count": len(flower.evidence),
                "age_days": flower.age_days,
                "entry_type": flower.entry_type.value,
            }

            capture_result = await brain.capture(content, metadata=metadata)
            crystal_id = (
                capture_result.concept_id
                if hasattr(capture_result, "concept_id")
                else str(capture_result)
            )
            harvested.append((flower, crystal_id))

            await garden.compost(flower.id)

        lines = [
            "🌾 Harvest Complete!",
            "",
            f"  Harvested {len(harvested)} idea(s) to Brain:",
            "",
        ]

        for flower, crystal_id in harvested:
            lines.extend(
                [
                    f"  🌸 → 💎 {flower.content[:50]}",
                    f"       Crystal ID: {crystal_id[:12]}...",
                ]
            )

        lines.extend(
            [
                "",
                "  Harvested ideas have been composted in the garden.",
                "  Use 'kg brain search' to find them in memory.",
            ]
        )

        return BasicRendering(
            summary=f"Harvested: {len(harvested)} ideas",
            content="\n".join(lines),
            metadata={"harvested": [{"flower_id": f.id, "crystal_id": c} for f, c in harvested]},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to garden-specific aspects."""
        match aspect:
            case "plant":
                return await self.plant(observer, **kwargs)
            case "harvest":
                return await self.harvest(observer, **kwargs)
            case "nurture":
                return await self.nurture(observer, **kwargs)
            case "harvest_to_brain":
                return await self.harvest_to_brain(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on GardenNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# VoidGardenNode - void.garden.*
# =============================================================================


@dataclass
class VoidGardenNode(BaseLogosNode):
    """
    void.garden - Serendipity from the Accursed Share.

    The void.garden context provides entropy-based discovery
    to surface unexpected connections.
    """

    _handle: str = "void.garden"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Void garden affordances."""
        return VOID_GARDEN_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show void garden status."""
        return BasicRendering(
            summary="Void Garden: Serendipity",
            content=(
                "The void.garden provides entropy-based discovery.\n\n"
                "Available aspects:\n"
                "  sip - Surface unexpected connections\n"
            ),
            metadata={"status": "available"},
        )

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("garden_state")],
        help="Surface unexpected connections from the void",
        examples=["kg gardener surprise"],
    )
    async def sip(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Serendipity from the void."""
        import random

        from agents.k.garden import GardenLifecycle

        garden = await _get_garden()
        stats = await garden.stats()

        if stats.total_entries == 0:
            return BasicRendering(
                summary="Empty Garden",
                content=(
                    "The void echoes... the garden is empty.\n"
                    'Plant some ideas first: kg gardener plant "idea"'
                ),
                metadata={"error": "empty"},
            )

        entries = [e for e in garden.entries.values() if e.lifecycle != GardenLifecycle.COMPOST]

        if not entries:
            return BasicRendering(
                summary="No Active Entries",
                content="No active entries to surface.",
                metadata={"error": "no_entries"},
            )

        surprise = random.choice(entries)

        lifecycle_icons = {
            "seed": "🌱",
            "sapling": "🌿",
            "tree": "🌳",
            "flower": "🌸",
            "compost": "🍂",
        }
        icon = lifecycle_icons.get(surprise.lifecycle.value, "✨")

        # Find related entries
        surprise_words = set(surprise.content.lower().split())
        related = []
        for e in entries:
            if e.id == surprise.id:
                continue
            e_words = set(e.content.lower().split())
            overlap = len(surprise_words & e_words)
            if overlap >= 2:
                related.append((e, overlap))
        related.sort(key=lambda x: -x[1])

        void_whispers = [
            "What patterns emerge when you hold these together?",
            "The garden dreams of connections not yet seen.",
            "Cross-pollination awaits the curious mind.",
            "Seeds planted apart may grow toward each other.",
            "The void offers; you decide the meaning.",
        ]

        lines = [
            "✨ From the Void",
            "",
            f"  {icon} {surprise.content}",
            f"     {surprise.lifecycle.value} | {surprise.confidence:.0%} confidence",
        ]

        if related:
            lines.append("")
            lines.append("  Perhaps connected to:")
            for r, overlap in related[:2]:
                r_icon = lifecycle_icons.get(r.lifecycle.value, "·")
                lines.append(f"    {r_icon} {r.content[:40]}...")

        lines.append("")
        lines.append(f"  {random.choice(void_whispers)}")

        return BasicRendering(
            summary=f"Serendipity: {surprise.content[:30]}...",
            content="\n".join(lines),
            metadata={
                "surfaced_id": surprise.id,
                "related": [r[0].id for r in related[:2]],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to void-garden-specific aspects."""
        match aspect:
            case "sip":
                return await self.sip(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on VoidGardenNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# Helpers
# =============================================================================


async def _get_garden() -> "PersonaGarden":
    """Get the PersonaGarden singleton."""
    from agents.k.garden import get_garden

    return get_garden()


def _render_polynomial(phase: str) -> str:
    """Render ASCII polynomial state machine."""
    states = ["SENSE", "ACT", "REFLECT"]
    parts = []

    for i, s in enumerate(states):
        is_current = s == phase
        emoji = PHASE_CONFIG[s]["emoji"]
        label = PHASE_CONFIG[s]["label"]

        if is_current:
            parts.append(f"◀ {emoji} {label} ▶")
        else:
            parts.append(f"  {emoji} {label}  ")

        if i < len(states) - 1:
            parts.append(" → ")

    return "".join(parts)


def _format_garden_stats(stats: Any) -> str:
    """Format garden stats for display."""
    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }

    parts = []
    for lc in ["seed", "sapling", "tree", "flower"]:
        count = stats.by_lifecycle.get(lc, 0)
        if count > 0:
            icon = lifecycle_icons.get(lc, " ")
            parts.append(f"{icon}{count}")

    if parts:
        return f"Garden: {' '.join(parts)}"
    return "Garden: Empty - plant an idea!"


# =============================================================================
# Factory Functions
# =============================================================================

_gardener_node: GardenerNode | None = None
_garden_node: GardenNode | None = None
_void_garden_node: VoidGardenNode | None = None


def get_gardener_node() -> GardenerNode:
    """Get the global GardenerNode singleton."""
    global _gardener_node
    if _gardener_node is None:
        _gardener_node = GardenerNode()
    return _gardener_node


def get_garden_node() -> GardenNode:
    """Get the global GardenNode singleton."""
    global _garden_node
    if _garden_node is None:
        _garden_node = GardenNode()
    return _garden_node


def get_void_garden_node() -> VoidGardenNode:
    """Get the global VoidGardenNode singleton."""
    global _void_garden_node
    if _void_garden_node is None:
        _void_garden_node = VoidGardenNode()
    return _void_garden_node


__all__ = [
    # Constants
    "GARDENER_AFFORDANCES",
    "GARDEN_AFFORDANCES",
    "VOID_GARDEN_AFFORDANCES",
    # Nodes
    "GardenerNode",
    "GardenNode",
    "VoidGardenNode",
    # Factory
    "get_gardener_node",
    "get_garden_node",
    "get_void_garden_node",
]
