"""
GardenerLogosNode: Unified AGENTESE node for Gardener-Logos.

Routes:
- concept.gardener.manifest → Garden overview
- concept.gardener.tend → Apply tending gesture
- concept.gardener.season.* → Season operations
- concept.gardener.plot.* → Plot management
- concept.gardener.session.* → Session operations (delegated)
- concept.gardener.prompt.* → Prompt operations (delegated to PromptNode)

This node integrates the tending calculus with AGENTESE,
making all garden operations accessible via the Logos system.

Phase 5: Prompt Logos Delegation
- concept.prompt.* paths flow through the garden with garden-aware context
- Season affects TextGRAD learning rate via plasticity
- Watering prompts adjusts learning_rate = tone × season.plasticity

See: spec/protocols/gardener-logos.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ...agentese.node import BaseLogosNode, BasicRendering
from ..garden import GardenSeason, GardenState, create_garden
from ..plots import PlotState, create_crown_jewel_plots, create_plot
from ..projections.ascii import project_garden_to_ascii
from ..projections.json import project_garden_to_json
from ..tending import (
    TendingGesture,
    TendingResult,
    TendingVerb,
    apply_gesture,
    graft,
    observe,
    prune,
    rotate,
    wait,
    water,
)

if TYPE_CHECKING:
    from agents.gardener.session import (
        GardenerSession,
        SessionArtifact,
        SessionIntent,
        SessionPhase,
    )
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.contexts.prompt import PromptContextResolver, PromptNode

# OTEL tracer for observability
_tracer = trace.get_tracer("kgents.gardener_logos")


# =============================================================================
# Role Affordances
# =============================================================================

GARDENER_LOGOS_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "guest": (
        "manifest",
        "season.manifest",
        "plot.list",
        "plot.manifest",
        "session.manifest",
        # Prompt (read-only)
        "prompt.manifest",
        "prompt.history",
    ),
    "developer": (
        "manifest",
        "tend",
        "season.manifest",
        "season.transition",
        "plot.list",
        "plot.create",
        "plot.focus",
        "plot.manifest",
        # Session operations
        "session.create",
        "session.manifest",
        "session.advance",
        "session.sense",
        "session.artifact",
        "session.learn",
        "session.complete",
        # Prompt operations (Phase 5)
        "prompt.manifest",
        "prompt.evolve",
        "prompt.validate",
        "prompt.compile",
        "prompt.history",
        "prompt.rollback",
        "prompt.diff",
    ),
    "meta": (
        "manifest",
        "tend",
        "season.manifest",
        "season.transition",
        "plot.list",
        "plot.create",
        "plot.focus",
        "plot.manifest",
        "plot.delete",
        # Full session control
        "session.create",
        "session.manifest",
        "session.advance",
        "session.sense",
        "session.artifact",
        "session.learn",
        "session.complete",
        "session.abort",
        "session.rollback",
        # Full prompt control (Phase 5)
        "prompt.manifest",
        "prompt.evolve",
        "prompt.validate",
        "prompt.compile",
        "prompt.history",
        "prompt.rollback",
        "prompt.diff",
    ),
    "default": (
        "manifest",
        "season.manifest",
        "plot.list",
        "session.manifest",
        "prompt.manifest",
    ),
}


# =============================================================================
# GardenerLogosNode
# =============================================================================


@dataclass
class GardenerLogosNode(BaseLogosNode):
    """
    Unified AGENTESE node for Gardener-Logos.

    Routes:
    - concept.gardener.manifest → Garden overview
    - concept.gardener.tend → Apply tending gesture
    - concept.gardener.season.manifest → Current season info
    - concept.gardener.season.transition → Change season
    - concept.gardener.plot.list → List all plots
    - concept.gardener.plot.create → Create new plot
    - concept.gardener.plot.focus → Set active plot
    - concept.gardener.plot.manifest → View specific plot
    - concept.gardener.prompt.* → Prompt operations (delegated to PromptNode)

    Phase 5: Prompt Delegation
    - prompt.* aspects are delegated to PromptContextResolver
    - Garden context (season, plasticity) is injected into kwargs
    - TextGRAD learning rate = tone × season.plasticity
    """

    _handle: str = "concept.gardener"
    _garden: GardenState | None = None
    _personality: Any = None  # TendingPersonality (lazy loaded)
    _prompt_resolver: "PromptContextResolver | None" = (
        None  # Phase 5: Prompt delegation
    )

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return self._handle

    def _get_garden(self) -> GardenState:
        """Get or create the garden state."""
        if self._garden is None:
            self._garden = create_garden("kgents")
            # Initialize with crown jewel plots
            self._garden.plots = create_crown_jewel_plots()
            self._garden.metrics.active_plots = len(self._garden.plots)
        return self._garden

    def _get_personality(self) -> Any:
        """Get or create the tending personality."""
        if self._personality is None:
            from ..personality import default_personality

            self._personality = default_personality()
        return self._personality

    def _get_prompt_resolver(self) -> "PromptContextResolver":
        """Get or create the PromptContextResolver for delegation."""
        if self._prompt_resolver is None:
            from protocols.agentese.contexts.prompt import create_prompt_resolver

            self._prompt_resolver = create_prompt_resolver()
        return self._prompt_resolver

    async def _delegate_to_prompt(
        self,
        sub_aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Delegate to PromptContextResolver with garden context.

        Phase 5: Prompt Logos Delegation
        - Routes prompt.* paths to the PromptNode
        - Injects garden_context (season, active_plot, plasticity)
        - Adjusts learning_rate for TextGRAD based on season plasticity

        Args:
            sub_aspect: The aspect after "prompt." (e.g., "evolve", "manifest")
            observer: The Umwelt observer
            **kwargs: Additional parameters

        Returns:
            The result from PromptNode
        """
        with _tracer.start_as_current_span(
            f"gardener_logos.prompt.{sub_aspect}"
        ) as span:
            span.set_attribute("sub_aspect", sub_aspect)

            garden = self._get_garden()
            resolver = self._get_prompt_resolver()

            # Get the PromptNode
            prompt_node = resolver.resolve("prompt", [sub_aspect])

            # Inject garden context
            garden_context = {
                "season": garden.season.name,
                "season_emoji": garden.season.emoji,
                "active_plot": garden.active_plot,
                "plasticity": garden.season.plasticity,
                "entropy_multiplier": garden.season.entropy_multiplier,
            }
            kwargs["garden_context"] = garden_context

            # For evolve aspect, adjust learning_rate based on season plasticity
            if sub_aspect == "evolve":
                # Base learning rate from kwargs or default
                base_learning_rate = kwargs.get("learning_rate", 0.5)
                # Adjust by season plasticity
                # High plasticity (SPROUTING=0.9) → more aggressive changes
                # Low plasticity (DORMANT=0.1) → conservative/stable
                adjusted_rate = base_learning_rate * garden.season.plasticity
                kwargs["learning_rate"] = adjusted_rate
                span.set_attribute("adjusted_learning_rate", adjusted_rate)

            # Route to appropriate aspect
            if sub_aspect == "manifest":
                return await prompt_node.manifest(observer)
            else:
                return await prompt_node._invoke_aspect(sub_aspect, observer, **kwargs)

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-gated affordances."""
        return GARDENER_LOGOS_AFFORDANCES.get(
            archetype, GARDENER_LOGOS_AFFORDANCES["default"]
        )

    # =========================================================================
    # manifest - Garden Overview
    # =========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """
        Return garden overview.

        AGENTESE: concept.gardener.manifest
        """
        with _tracer.start_as_current_span("gardener_logos.manifest"):
            garden = self._get_garden()
            personality = self._get_personality()

            # ASCII projection for CLI
            ascii_view = project_garden_to_ascii(garden, personality)

            # JSON for metadata
            json_view = project_garden_to_json(garden)

            return BasicRendering(
                summary=f"Garden: {garden.name} ({garden.season.emoji} {garden.season.name})",
                content=ascii_view,
                metadata=json_view,
            )

    # =========================================================================
    # Route to aspect handlers
    # =========================================================================

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""
        with _tracer.start_as_current_span(f"gardener_logos.{aspect}") as span:
            span.set_attribute("aspect", aspect)

            match aspect:
                case "manifest":
                    return await self.manifest(observer)
                case "tend":
                    return await self._tend(observer, **kwargs)
                case "season.manifest":
                    return await self._season_manifest(observer, **kwargs)
                case "season.transition":
                    return await self._season_transition(observer, **kwargs)
                case "plot.list":
                    return await self._plot_list(observer, **kwargs)
                case "plot.create":
                    return await self._plot_create(observer, **kwargs)
                case "plot.focus":
                    return await self._plot_focus(observer, **kwargs)
                case "plot.manifest":
                    return await self._plot_manifest(observer, **kwargs)
                # Session operations (Phase 4 Unification)
                case "session.create":
                    return await self._session_create(observer, **kwargs)
                case "session.manifest":
                    return await self._session_manifest(observer, **kwargs)
                case "session.advance":
                    return await self._session_advance(observer, **kwargs)
                case "session.sense":
                    return await self._session_sense(observer, **kwargs)
                case "session.artifact":
                    return await self._session_artifact(observer, **kwargs)
                case "session.learn":
                    return await self._session_learn(observer, **kwargs)
                case "session.complete":
                    return await self._session_complete(observer, **kwargs)
                case "session.abort":
                    return await self._session_abort(observer, **kwargs)
                case "session.rollback":
                    return await self._session_rollback(observer, **kwargs)
                case _:
                    # Phase 5: Prompt Logos Delegation
                    # Handle prompt.* aspects by delegating to PromptNode
                    if aspect.startswith("prompt."):
                        sub_aspect = aspect[7:]  # Remove "prompt." prefix
                        return await self._delegate_to_prompt(
                            sub_aspect, observer, **kwargs
                        )

                    # Unknown aspect
                    return BasicRendering(
                        summary=f"Unknown aspect: {aspect}",
                        content=f"The aspect '{aspect}' is not implemented.",
                        metadata={"error": "unknown_aspect", "aspect": aspect},
                    )

    # =========================================================================
    # tend - Apply Tending Gesture
    # =========================================================================

    async def _tend(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Apply a tending gesture to the garden.

        AGENTESE: concept.gardener.tend

        Args:
            verb: The tending verb (observe, prune, graft, water, rotate, wait)
            target: AGENTESE path to tend
            reasoning: Why this gesture?
            tone: Definitiveness (0.0-1.0, default: 0.5)
        """
        garden = self._get_garden()

        verb_str = kwargs.get("verb", "observe").upper()
        target = kwargs.get("target", "concept.gardener")
        reasoning = kwargs.get("reasoning", "")
        tone = float(kwargs.get("tone", 0.5))

        # Parse verb
        try:
            verb = TendingVerb[verb_str]
        except KeyError:
            return BasicRendering(
                summary="Invalid tending verb",
                content=f"Unknown verb: {verb_str}. Valid verbs: {[v.name for v in TendingVerb]}",
                metadata={"error": "invalid_verb", "verb": verb_str},
            )

        # Build gesture using helpers
        gesture: TendingGesture
        match verb:
            case TendingVerb.OBSERVE:
                gesture = observe(target, reasoning or f"Observing {target}")
            case TendingVerb.PRUNE:
                gesture = prune(target, reasoning or "Pruning", tone)
            case TendingVerb.GRAFT:
                gesture = graft(target, reasoning or "Grafting", tone)
            case TendingVerb.WATER:
                gesture = water(target, reasoning or "Watering", tone)
            case TendingVerb.ROTATE:
                gesture = rotate(target, reasoning or "Rotating")
            case TendingVerb.WAIT:
                gesture = wait(reasoning or "Waiting")
            case _:
                gesture = observe(target, reasoning)

        # Apply gesture
        result: TendingResult = await apply_gesture(garden, gesture)

        # Build response
        lines = [
            f"{gesture.verb.emoji} TENDING RESULT",
            "=" * 40,
            f"Verb: {gesture.verb.name}",
            f"Target: {gesture.target}",
            f"Tone: {gesture.tone:.2f}",
            f"Accepted: {'Yes' if result.accepted else 'No'}",
            f"State Changed: {'Yes' if result.state_changed else 'No'}",
            "",
        ]

        if result.changes:
            lines.append("Changes:")
            for change in result.changes:
                lines.append(f"  - {change}")
            lines.append("")

        if result.reasoning_trace:
            lines.append("Reasoning:")
            for reason in result.reasoning_trace:
                lines.append(f"  - {reason}")
            lines.append("")

        if result.synergies_triggered:
            lines.append("Synergies:")
            for synergy in result.synergies_triggered:
                lines.append(f"  - {synergy}")

        if result.error:
            lines.append(f"Error: {result.error}")

        return BasicRendering(
            summary=f"{gesture.verb.emoji} {gesture.verb.name} {target}",
            content="\n".join(lines),
            metadata={
                "verb": gesture.verb.name,
                "target": gesture.target,
                "tone": gesture.tone,
                "accepted": result.accepted,
                "state_changed": result.state_changed,
                "changes": result.changes,
                "synergies_triggered": result.synergies_triggered,
                "error": result.error,
            },
        )

    # =========================================================================
    # season.manifest - Current Season Info
    # =========================================================================

    async def _season_manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Show current season information.

        AGENTESE: concept.gardener.season.manifest
        """
        garden = self._get_garden()
        season = garden.season

        lines = [
            f"{season.emoji} SEASON: {season.name}",
            "=" * 40,
            f"Plasticity: {season.plasticity:.0%}",
            f"Entropy Multiplier: {season.entropy_multiplier:.1f}x",
            f"Since: {garden.season_since.strftime('%Y-%m-%d %H:%M')}",
            "",
            "Season Meanings:",
            "  DORMANT    - Garden resting. Low entropy cost.",
            "  SPROUTING  - New ideas emerging. High plasticity.",
            "  BLOOMING   - Ideas crystallizing. High visibility.",
            "  HARVEST    - Time to gather and consolidate.",
            "  COMPOSTING - Breaking down old patterns.",
            "",
            "Commands:",
            "  kg concept.gardener.season.transition --to SPROUTING",
        ]

        return BasicRendering(
            summary=f"Season: {season.name}",
            content="\n".join(lines),
            metadata={
                "season": season.name,
                "plasticity": season.plasticity,
                "entropy_multiplier": season.entropy_multiplier,
                "since": garden.season_since.isoformat(),
            },
        )

    # =========================================================================
    # season.transition - Change Season
    # =========================================================================

    async def _season_transition(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Transition to a new season.

        AGENTESE: concept.gardener.season.transition

        Args:
            to: Target season (DORMANT, SPROUTING, BLOOMING, HARVEST, COMPOSTING)
            reason: Why transitioning?
        """
        garden = self._get_garden()

        to_season = kwargs.get("to", "").upper()
        reason = kwargs.get("reason", "Manual transition")

        if not to_season:
            return BasicRendering(
                summary="Season required",
                content="Usage: kg concept.gardener.season.transition --to <SEASON>",
                metadata={"error": "no_season"},
            )

        try:
            new_season = GardenSeason[to_season]
        except KeyError:
            valid = [s.name for s in GardenSeason]
            return BasicRendering(
                summary="Invalid season",
                content=f"Unknown season: {to_season}. Valid: {valid}",
                metadata={"error": "invalid_season", "valid": valid},
            )

        old_season = garden.season
        garden.transition_season(new_season, reason)

        lines = [
            "🔄 SEASON TRANSITION",
            "=" * 40,
            f"From: {old_season.emoji} {old_season.name}",
            f"To:   {new_season.emoji} {new_season.name}",
            f"Reason: {reason}",
            "",
            f"New plasticity: {new_season.plasticity:.0%}",
            f"New entropy multiplier: {new_season.entropy_multiplier:.1f}x",
        ]

        return BasicRendering(
            summary=f"Season: {old_season.name} → {new_season.name}",
            content="\n".join(lines),
            metadata={
                "old_season": old_season.name,
                "new_season": new_season.name,
                "reason": reason,
            },
        )

    # =========================================================================
    # plot.list - List All Plots
    # =========================================================================

    async def _plot_list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        List all plots in the garden.

        AGENTESE: concept.gardener.plot.list
        """
        garden = self._get_garden()
        plots = garden.plots

        if not plots:
            return BasicRendering(
                summary="No plots",
                content="No plots in the garden. Use concept.gardener.plot.create to add one.",
                metadata={"plots": []},
            )

        lines = [
            "📊 GARDEN PLOTS",
            "=" * 40,
            "",
        ]

        for name, plot in plots.items():
            is_active = name == garden.active_plot
            active_marker = " ◀ active" if is_active else ""
            effective_season = plot.get_effective_season(garden.season)

            # Progress bar
            progress = int(plot.progress * 10)
            bar = "█" * progress + "░" * (10 - progress)

            lines.append(
                f"  {plot.display_name:<18} {bar} {plot.progress:.0%}{active_marker}"
            )
            lines.append(f"    Path: {plot.path}")
            if plot.crown_jewel:
                lines.append(f"    Crown Jewel: {plot.crown_jewel}")
            lines.append(f"    Season: {effective_season.emoji}")
            lines.append("")

        lines.append(f"Total: {len(plots)} plots")
        lines.append("")
        lines.append("Commands:")
        lines.append("  kg concept.gardener.plot.focus --name <plot>")
        lines.append("  kg concept.gardener.plot.manifest --name <plot>")

        return BasicRendering(
            summary=f"{len(plots)} plots",
            content="\n".join(lines),
            metadata={
                "plots": [p.to_dict() for p in plots.values()],
                "active_plot": garden.active_plot,
            },
        )

    # =========================================================================
    # plot.create - Create New Plot
    # =========================================================================

    async def _plot_create(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Create a new plot in the garden.

        AGENTESE: concept.gardener.plot.create

        Args:
            name: Plot name
            path: AGENTESE path (e.g., world.project.foo)
            description: Optional description
            plan: Optional plan file path
            rigidity: Resistance to change (0-1, default: 0.5)
        """
        garden = self._get_garden()

        name = kwargs.get("name", "")
        path = kwargs.get("path", "")
        description = kwargs.get("description", "")
        plan_path = kwargs.get("plan")
        rigidity = float(kwargs.get("rigidity", 0.5))

        if not name:
            return BasicRendering(
                summary="Name required",
                content="Usage: kg concept.gardener.plot.create --name <name> --path <path>",
                metadata={"error": "no_name"},
            )

        if not path:
            # Infer path from name
            path = f"concept.project.{name.replace('-', '_')}"

        if name in garden.plots:
            return BasicRendering(
                summary="Plot exists",
                content=f"Plot '{name}' already exists. Use plot.manifest to view it.",
                metadata={"error": "plot_exists", "name": name},
            )

        plot = create_plot(
            name=name,
            path=path,
            description=description,
            plan_path=plan_path,
            rigidity=rigidity,
        )

        garden.plots[name] = plot
        garden.metrics.active_plots = len(garden.plots)

        lines = [
            "✅ PLOT CREATED",
            "=" * 40,
            f"Name: {plot.display_name}",
            f"Path: {plot.path}",
            f"Rigidity: {plot.rigidity:.0%}",
        ]
        if description:
            lines.append(f"Description: {description}")
        if plan_path:
            lines.append(f"Plan: {plan_path}")

        return BasicRendering(
            summary=f"Created: {name}",
            content="\n".join(lines),
            metadata=plot.to_dict(),
        )

    # =========================================================================
    # plot.focus - Set Active Plot
    # =========================================================================

    async def _plot_focus(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Set the active plot.

        AGENTESE: concept.gardener.plot.focus

        Args:
            name: Plot name to focus on
        """
        garden = self._get_garden()

        name = kwargs.get("name", "")

        if not name:
            # Show current focus
            if garden.active_plot:
                return BasicRendering(
                    summary=f"Focus: {garden.active_plot}",
                    content=f"Current focus: {garden.active_plot}",
                    metadata={"active_plot": garden.active_plot},
                )
            return BasicRendering(
                summary="No focus",
                content="No plot is currently focused. Use --name <plot> to focus.",
                metadata={"active_plot": None},
            )

        if name not in garden.plots:
            available = list(garden.plots.keys())
            return BasicRendering(
                summary="Plot not found",
                content=f"Plot '{name}' not found. Available: {available}",
                metadata={"error": "plot_not_found", "available": available},
            )

        old_focus = garden.active_plot
        garden.active_plot = name
        plot = garden.plots[name]

        lines = [
            "🎯 FOCUS CHANGED",
            "=" * 40,
            f"Now focused on: {plot.display_name}",
            f"Path: {plot.path}",
        ]
        if old_focus:
            lines.append(f"Previous focus: {old_focus}")

        return BasicRendering(
            summary=f"Focus: {name}",
            content="\n".join(lines),
            metadata={
                "active_plot": name,
                "old_focus": old_focus,
                "plot": plot.to_dict(),
            },
        )

    # =========================================================================
    # plot.manifest - View Specific Plot
    # =========================================================================

    async def _plot_manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        View details of a specific plot.

        AGENTESE: concept.gardener.plot.manifest

        Args:
            name: Plot name to view
        """
        garden = self._get_garden()

        name = kwargs.get("name", "")

        if not name:
            # Use active plot if no name
            if garden.active_plot:
                name = garden.active_plot
            else:
                return BasicRendering(
                    summary="Name required",
                    content="Usage: kg concept.gardener.plot.manifest --name <plot>",
                    metadata={"error": "no_name"},
                )

        if name not in garden.plots:
            available = list(garden.plots.keys())
            return BasicRendering(
                summary="Plot not found",
                content=f"Plot '{name}' not found. Available: {available}",
                metadata={"error": "plot_not_found", "available": available},
            )

        plot = garden.plots[name]
        from ..projections.ascii import project_plot_to_ascii

        ascii_view = project_plot_to_ascii(plot, garden)

        return BasicRendering(
            summary=f"Plot: {plot.display_name}",
            content=ascii_view,
            metadata=plot.to_dict(),
        )

    # =========================================================================
    # Session Operations (Phase 4 Unification)
    # =========================================================================

    async def _session_create(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Create a new session embedded in the garden.

        AGENTESE: concept.gardener.session.create

        Args:
            name: Session name (optional)
            plan_path: Optional link to forest plan file
            intent: Optional initial intent description
        """
        from agents.gardener.session import SessionIntent, project_session_to_dict

        garden = self._get_garden()

        name = kwargs.get("name")
        plan_path = kwargs.get("plan_path")
        intent_str = kwargs.get("intent")

        # Use garden's get_or_create_session for unified behavior
        session = garden.get_or_create_session(name=name, plan_path=plan_path)

        # Set intent if provided
        if intent_str:
            if isinstance(intent_str, dict):
                intent = SessionIntent.from_dict(intent_str)
            else:
                intent = SessionIntent(description=str(intent_str))
            await session.set_intent(intent)

        session_dict = project_session_to_dict(session)

        lines = [
            "✅ SESSION CREATED",
            "=" * 40,
            f"ID: {session.session_id}",
            f"Name: {session.name}",
            f"Phase: {session.phase.name}",
            f"Garden Season: {garden.season.emoji} {garden.season.name}",
        ]
        if plan_path:
            lines.append(f"Plan: {plan_path}")
        if intent_str:
            lines.append(f"Intent: {intent_str}")

        return BasicRendering(
            summary=f"Session: {session.name}",
            content="\n".join(lines),
            metadata={"status": "created", "session": session_dict},
        )

    async def _session_manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        View current session state.

        AGENTESE: concept.gardener.session.manifest

        Args:
            format: "dict" or "ascii" (default: "dict")
        """
        from agents.gardener.session import (
            project_session_to_ascii,
            project_session_to_dict,
        )

        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session. Use concept.gardener.session.create to start one.",
                metadata={"status": "no_session"},
            )

        fmt = kwargs.get("format", "dict")

        if fmt == "ascii":
            ascii_view = project_session_to_ascii(session)
            return BasicRendering(
                summary=f"Session: {session.name} [{session.phase.name}]",
                content=ascii_view,
                metadata={"status": "manifest", "format": "ascii"},
            )

        session_dict = project_session_to_dict(session)
        lines = [
            f"🌱 SESSION: {session.name}",
            "=" * 40,
            f"ID: {session.session_id}",
            f"Phase: {session.phase.name}",
            f"Artifacts: {len(session.artifacts)}",
            f"Learnings: {len(session.learnings)}",
            f"Cycles: {session.state.reflect_count}",
            "",
            f"Garden Season: {garden.season.emoji} {garden.season.name}",
        ]

        if session.intent:
            lines.append(f"Intent: {session.intent.description}")

        return BasicRendering(
            summary=f"Session: {session.name} [{session.phase.name}]",
            content="\n".join(lines),
            metadata={"status": "manifest", "session": session_dict},
        )

    async def _session_advance(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Advance to the next session phase.

        AGENTESE: concept.gardener.session.advance

        Triggers Phase → Season synergy if appropriate.
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session to advance.",
                metadata={"status": "error", "message": "no_session"},
            )

        old_phase = session.phase
        result = await session.advance()

        # Trigger Phase → Season synergy
        new_season = await garden.on_session_phase_advance(old_phase, session.phase)

        lines = [
            "⏩ PHASE ADVANCED",
            "=" * 40,
            f"From: {old_phase.name}",
            f"To: {session.phase.name}",
        ]

        if new_season:
            lines.append("")
            lines.append(
                f"🔄 Season changed: {garden.season.emoji} {garden.season.name}"
            )

        return BasicRendering(
            summary=f"Phase: {old_phase.name} → {session.phase.name}",
            content="\n".join(lines),
            metadata={
                "status": "advanced",
                "from_phase": old_phase.name,
                "to_phase": session.phase.name,
                "season_changed": new_season is not None,
                "new_season": new_season.name if new_season else None,
                **result,
            },
        )

    async def _session_sense(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Gather context in SENSE phase.

        AGENTESE: concept.gardener.session.sense

        Args:
            context_type: "all", "forest", "codebase", or "memory"
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session.",
                metadata={"status": "error", "message": "no_session"},
            )

        context_type = kwargs.get("context_type", "all")
        result = await session.sense(context_type)

        lines = [
            "👁️ SENSE COMPLETE",
            "=" * 40,
            f"Context gathered: {context_type}",
            f"Phase: {session.phase.name}",
        ]

        return BasicRendering(
            summary=f"Sensed: {context_type}",
            content="\n".join(lines),
            metadata=result,
        )

    async def _session_artifact(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Record an artifact in ACT phase.

        AGENTESE: concept.gardener.session.artifact

        Args:
            artifact_type: "code", "doc", "plan", "learning", "test"
            path: Optional file path
            content: Optional content
            description: Description of the artifact
        """
        from agents.gardener.session import SessionArtifact

        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session.",
                metadata={"status": "error", "message": "no_session"},
            )

        artifact = SessionArtifact(
            artifact_type=kwargs.get("artifact_type", "code"),
            path=kwargs.get("path"),
            content=kwargs.get("content"),
            description=kwargs.get("description", ""),
        )

        result = await session.record_artifact(artifact)

        return BasicRendering(
            summary=f"Artifact: {artifact.artifact_type}",
            content=f"Recorded {artifact.artifact_type} artifact. Total: {len(session.artifacts)}",
            metadata=result,
        )

    async def _session_learn(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Record a learning in REFLECT phase.

        AGENTESE: concept.gardener.session.learn

        Args:
            learning: The learning to record (string or list of strings)
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session.",
                metadata={"status": "error", "message": "no_session"},
            )

        learning = kwargs.get("learning", "")
        if not learning:
            return BasicRendering(
                summary="Learning required",
                content="Provide a learning to record.",
                metadata={"status": "error", "message": "no_learning"},
            )

        result = await session.learn(learning)

        return BasicRendering(
            summary=f"Learned ({len(session.learnings)} total)",
            content=f"Recorded learning. Total: {len(session.learnings)}",
            metadata=result,
        )

    async def _session_complete(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Complete the current session.

        AGENTESE: concept.gardener.session.complete

        Transitions garden to HARVEST season.
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session to complete.",
                metadata={"status": "error", "message": "no_session"},
            )

        result = await session.complete()

        # Trigger garden season transition
        await garden.on_session_complete()

        lines = [
            "✅ SESSION COMPLETE",
            "=" * 40,
            f"Artifacts: {len(session.artifacts)}",
            f"Learnings: {len(session.learnings)}",
            f"Cycles: {session.state.reflect_count}",
            "",
            f"Garden Season: {garden.season.emoji} {garden.season.name}",
        ]

        return BasicRendering(
            summary=f"Session completed: {session.name}",
            content="\n".join(lines),
            metadata={"status": "completed", **result},
        )

    async def _session_abort(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Abort the current session.

        AGENTESE: concept.gardener.session.abort
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session to abort.",
                metadata={"status": "error", "message": "no_session"},
            )

        result = await session.abort()
        garden.clear_session()

        return BasicRendering(
            summary="Session aborted",
            content="Session has been aborted.",
            metadata={"status": "aborted", **result},
        )

    async def _session_rollback(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Rollback from ACT to SENSE phase.

        AGENTESE: concept.gardener.session.rollback
        """
        garden = self._get_garden()
        session = garden.session

        if session is None:
            return BasicRendering(
                summary="No active session",
                content="No active session.",
                metadata={"status": "error", "message": "no_session"},
            )

        result = await session.rollback()

        return BasicRendering(
            summary=f"Rolled back to {session.phase.name}",
            content="Session rolled back from ACT to SENSE.",
            metadata={"status": "rolled_back", **result},
        )


# =============================================================================
# GardenerLogosResolver
# =============================================================================


@dataclass
class GardenerLogosResolver:
    """
    Resolver for concept.gardener.* paths.

    Routes all gardener paths to the singleton GardenerLogosNode.
    """

    _node: GardenerLogosNode | None = None
    _garden: GardenState | None = None

    def resolve(self, holon: str, rest: list[str]) -> GardenerLogosNode:
        """Resolve to GardenerLogosNode singleton."""
        if self._node is None:
            self._node = GardenerLogosNode()
            if self._garden:
                self._node._garden = self._garden
        return self._node

    def set_garden(self, garden: GardenState) -> None:
        """Set the garden state (for testing or persistence)."""
        self._garden = garden
        if self._node:
            self._node._garden = garden


# =============================================================================
# Factory Functions
# =============================================================================


def create_gardener_logos_node(
    garden: GardenState | None = None,
) -> GardenerLogosNode:
    """
    Create a GardenerLogosNode.

    Args:
        garden: Optional pre-existing garden state
    """
    node = GardenerLogosNode()
    if garden:
        node._garden = garden
    return node


def create_gardener_logos_resolver(
    garden: GardenState | None = None,
) -> GardenerLogosResolver:
    """
    Create a GardenerLogosResolver.

    Args:
        garden: Optional pre-existing garden state
    """
    resolver = GardenerLogosResolver()
    if garden:
        resolver.set_garden(garden)
    return resolver


__all__ = [
    "GardenerLogosNode",
    "GardenerLogosResolver",
    "create_gardener_logos_node",
    "create_gardener_logos_resolver",
    "GARDENER_LOGOS_AFFORDANCES",
]
