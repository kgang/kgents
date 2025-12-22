"""
AGENTESE Exploration Harness Context.

self.explore.* paths for exploration with safety guarantees.

The exploration harness wraps the typed-hypergraph with:
- Navigation budget (bounded exploration)
- Loop detection (prevent spinning)
- Evidence collection (exploration creates proof)
- Commitment protocol (claims require evidence)

AGENTESE Principle: "The harness doesn't constrain—it witnesses."

Spec: spec/protocols/exploration-harness.md

Teaching:
    gotcha: NavigationBudget is immutable—consume() returns NEW budget.
            Always capture the return value.
            (Evidence: test_self_explore.py::test_budget_immutable)

    gotcha: The harness is stateful—it tracks budget, loops, and evidence
            across navigation steps. Create a new harness for each exploration.
            (Evidence: test_self_explore.py::test_harness_stateful)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.exploration import ExplorationHarness


# === Affordances ===

EXPLORE_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Current exploration state
    "start",  # Start new exploration
    "navigate",  # Navigate via hyperedge
    "expand",  # Expand a portal with safety
    "collapse",  # Collapse a portal
    "budget",  # Budget breakdown
    "evidence",  # Collected evidence
    "trail",  # Navigation trail
    "commit",  # Commit a claim
    "loops",  # Loop detection status
    "reset",  # Reset exploration state
)


# === AGENTESE Node ===


@node(
    "self.explore",
    description="Exploration harness with safety guarantees",
)
@dataclass
class ExploreNode(BaseLogosNode):
    """
    self.explore - Exploration with safety and evidence.

    The harness wraps hypergraph navigation with:
    - Budget: Bounded exploration (steps, depth, nodes, time)
    - Loops: Prevent spinning (exact, semantic, structural)
    - Evidence: Every navigation creates proof
    - Commitment: Claims require trail-based evidence

    The harness doesn't constrain—it witnesses.
    Every trail is evidence. Every exploration creates proof obligations.

    Usage:
        kg explore                     # Current state
        kg explore start world.brain   # Start at path
        kg explore navigate tests      # Follow hyperedge
        kg explore budget              # Budget breakdown
        kg explore evidence            # What we found
        kg explore commit "claim"      # Commit with evidence
        kg explore reset               # Fresh start
    """

    _handle: str = "self.explore"

    # Current harness (session-scoped, lazy-initialized)
    _harness: "ExplorationHarness | None" = field(default=None, repr=False)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return EXPLORE_AFFORDANCES

    def _ensure_harness(
        self, start_path: str | None = None, preset: str = "standard"
    ) -> "ExplorationHarness":
        """
        Ensure we have an initialized exploration harness.

        Lazily imports ExplorationHarness to avoid circular dependencies.
        """
        if self._harness is None or start_path:
            from protocols.exploration import create_harness
            from protocols.exploration.budget import (
                quick_budget,
                standard_budget,
                thorough_budget,
            )
            from protocols.exploration.types import ContextNode

            # Select budget preset
            budget_fn = {
                "quick": quick_budget,
                "standard": standard_budget,
                "thorough": thorough_budget,
            }.get(preset, standard_budget)

            # Create start node
            path = start_path or "root"
            holon = path.split(".")[-1] if "." in path else path
            start_node = ContextNode(path=path, holon=holon)

            self._harness = create_harness(start_node, budget=budget_fn())

        return self._harness

    def _reset_harness(self) -> None:
        """Reset the harness to None."""
        self._harness = None

    def _has_harness(self) -> bool:
        """Check if there's an active exploration."""
        return self._harness is not None

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current exploration state",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Manifest current exploration state."""
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Exploration Active",
                content=f"{DIM}No active exploration.{RESET}\n\n"
                f"Start one with: kg explore start <path>\n"
                f"Example: kg explore start world.brain.core",
                metadata={
                    "status": "no_exploration",
                    "hint": "Use 'start <path>' to begin",
                    "route": "/explore",
                },
            )

        harness = self._ensure_harness()
        state = harness.get_state()

        # Format content
        lines = [f"{BOLD}Exploration State{RESET}\n"]

        # Focus
        focus_paths = [n.path for n in harness.focus]
        focus_str = ", ".join(focus_paths) if focus_paths else "(none)"
        lines.append(f"{BOLD}Focus:{RESET}       {CYAN}{focus_str}{RESET}")

        # Trail
        trail = harness.trail
        trail_str = f"{len(trail.steps)} steps"
        if len(trail.steps) > 1:
            first = trail.steps[0].node
            last = trail.steps[-1].node
            trail_str += f" ({first} -> ... -> {last})"
        lines.append(f"{BOLD}Trail:{RESET}       {trail_str}")

        # Evidence
        ev_str = f"{state.evidence_count} items"
        if state.strong_evidence_count > 0:
            weak = state.evidence_count - state.strong_evidence_count
            ev_str = f"{state.evidence_count} items ({state.strong_evidence_count} strong, {weak} weak)"
        lines.append(f"{BOLD}Evidence:{RESET}    {ev_str}")

        # Budget
        remaining = state.budget_remaining
        budget_pct = 100 - int(remaining.get("used_pct", 0) * 100) if "used_pct" in remaining else 100
        lines.append(f"{BOLD}Budget:{RESET}      ~{budget_pct}% remaining")

        # Loops
        lines.append(f"{BOLD}Loops:{RESET}       {state.loop_warnings} warnings")

        if harness.is_halted:
            lines.append(f"\n{BOLD}[HALTED]{RESET}")

        return BasicRendering(
            summary="Exploration State",
            content="\n".join(lines),
            metadata={
                "focus": focus_paths,
                "trail_steps": len(trail.steps),
                "evidence_count": state.evidence_count,
                "strong_evidence": state.strong_evidence_count,
                "budget_remaining_pct": budget_pct,
                "loop_warnings": state.loop_warnings,
                "halted": harness.is_halted,
                "observer": obs.archetype,
                "route": "/explore",
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exploration_state")],
        help="Start new exploration at given path",
    )
    async def start(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str,
        preset: str = "standard",
    ) -> Renderable:
        """Start a new exploration at the given path."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        # Reset and create new harness
        self._reset_harness()
        harness = self._ensure_harness(path, preset=preset)

        lines = [f"{GREEN}Exploration Started{RESET}\n"]
        lines.append(f"{BOLD}Path:{RESET}    {path}")
        lines.append(f"{BOLD}Preset:{RESET}  {preset}")
        lines.append("")
        lines.append(f"{DIM}Commands:{RESET}")
        lines.append(f"  navigate <edge>   Follow a hyperedge")
        lines.append(f"  budget            Show budget status")
        lines.append(f"  evidence          Show evidence collected")

        return BasicRendering(
            summary=f"Started at {path}",
            content="\n".join(lines),
            metadata={
                "path": path,
                "preset": preset,
                "observer": obs.archetype,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exploration_state")],
        help="Navigate via hyperedge",
    )
    async def navigate(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        edge: str,
    ) -> Renderable:
        """Navigate via a hyperedge."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}\n"
                f"Start one with: kg explore start <path>",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()
        result = await harness.navigate(edge)

        if result.success:
            focus_paths = [n.path for n in harness.focus]
            focus_str = ", ".join(focus_paths) if focus_paths else "(none)"

            lines = [f"{GREEN}Navigated via [{edge}]{RESET}\n"]
            lines.append(f"{BOLD}New focus:{RESET} {focus_str}")

            if result.loop_detected:
                lines.append(f"\n{YELLOW}Loop detected: {result.loop_detected.name}{RESET}")
                if result.error_message:
                    lines.append(f"{DIM}{result.error_message}{RESET}")

            return BasicRendering(
                summary=f"Navigated via [{edge}]",
                content="\n".join(lines),
                metadata={
                    "success": True,
                    "edge": edge,
                    "focus": focus_paths,
                    "loop_detected": result.loop_detected.name if result.loop_detected else None,
                },
            )
        else:
            return BasicRendering(
                summary=f"Navigation failed",
                content=f"{RED}Navigation failed: {result.error_message}{RESET}",
                metadata={
                    "success": False,
                    "edge": edge,
                    "error": result.error_message,
                },
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exploration_state")],
        help="Expand a portal with safety checks",
    )
    async def expand(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        portal_path: str,
    ) -> Renderable:
        """Expand a portal with budget, loop, and evidence safety."""
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}\n"
                f"Start one with: kg explore start <path>",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()

        # Need a PortalTree - check if we have one
        try:
            from protocols.file_operad.portal import PortalNode, PortalTree
            from pathlib import Path

            # Create a minimal tree if needed
            root = PortalNode(path=str(Path.cwd()), depth=0)
            tree = PortalTree(root=root)

            # Parse portal path
            path_segments = [s.strip() for s in portal_path.split("/") if s.strip()]

            result = await harness.expand_portal(path_segments, tree)

            if result.success:
                files_str = ", ".join(result.files_opened) if result.files_opened else "(none)"
                return BasicRendering(
                    summary=f"Expanded [{portal_path}]",
                    content=f"{GREEN}Expanded{RESET} [{portal_path}]\n\n"
                    f"Files opened: {files_str}",
                    metadata={
                        "success": True,
                        "portal_path": portal_path,
                        "files_opened": result.files_opened,
                    },
                )
            else:
                return BasicRendering(
                    summary=f"Expansion failed",
                    content=f"{YELLOW}Failed:{RESET} {result.error_message}",
                    metadata={
                        "success": False,
                        "portal_path": portal_path,
                        "error": result.error_message,
                        "loop_detected": result.loop_detected.name if result.loop_detected else None,
                    },
                )
        except ImportError:
            return BasicRendering(
                summary="Portal system unavailable",
                content=f"{DIM}Portal system not available{RESET}",
                metadata={"error": "portal_unavailable"},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show budget breakdown",
    )
    async def budget(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Show detailed budget breakdown."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()
        budget = harness.budget

        # Progress bar helper
        def progress_bar(current: float, total: float, width: int = 10) -> str:
            pct = current / total if total > 0 else 0
            filled = int(pct * width)
            empty = width - filled
            return "[" + "=" * filled + "-" * empty + "]"

        lines = [f"{BOLD}Navigation Budget{RESET}\n"]

        # Steps
        steps_pct = budget.steps_taken / budget.max_steps if budget.max_steps > 0 else 0
        bar = progress_bar(budget.steps_taken, budget.max_steps)
        lines.append(f"  Steps:   {budget.steps_taken:3d} / {budget.max_steps:3d}  {bar} {int(steps_pct*100):3d}%")

        # Nodes
        nodes_count = len(budget.nodes_visited)
        nodes_pct = nodes_count / budget.max_nodes if budget.max_nodes > 0 else 0
        bar = progress_bar(nodes_count, budget.max_nodes)
        lines.append(f"  Nodes:   {nodes_count:3d} / {budget.max_nodes:3d}  {bar} {int(nodes_pct*100):3d}%")

        # Depth
        depth_pct = budget.current_depth / budget.max_depth if budget.max_depth > 0 else 0
        bar = progress_bar(budget.current_depth, budget.max_depth)
        lines.append(f"  Depth:   {budget.current_depth:3d} / {budget.max_depth:3d}  {bar} {int(depth_pct*100):3d}%")

        # Time
        elapsed = budget._elapsed_ms()
        time_pct = elapsed / budget.time_budget_ms if budget.time_budget_ms > 0 else 0
        bar = progress_bar(elapsed, budget.time_budget_ms)
        lines.append(f"  Time:    {int(elapsed):5d} / {budget.time_budget_ms:5d} ms {bar} {int(time_pct*100):3d}%")

        lines.append("")

        # Status
        if not budget.can_navigate():
            reason = budget.exhaustion_reason()
            lines.append(f"{RED}EXHAUSTED: {reason.value if reason else 'unknown'}{RESET}")
        else:
            max_pct = max(steps_pct, nodes_pct, depth_pct, time_pct)
            if max_pct > 0.8:
                lines.append(f"{YELLOW}Risk: HIGH{RESET}")
            elif max_pct > 0.5:
                lines.append(f"{DIM}Risk: MEDIUM{RESET}")
            else:
                lines.append(f"{GREEN}Risk: LOW{RESET}")

        return BasicRendering(
            summary="Budget Status",
            content="\n".join(lines),
            metadata={
                "steps": {"used": budget.steps_taken, "max": budget.max_steps},
                "nodes": {"visited": nodes_count, "max": budget.max_nodes},
                "depth": {"current": budget.current_depth, "max": budget.max_depth},
                "time_ms": {"elapsed": int(elapsed), "max": budget.time_budget_ms},
                "can_navigate": budget.can_navigate(),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show collected evidence",
    )
    async def evidence(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Show collected evidence."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()
        summary = harness.get_evidence_summary()

        lines = [f"{BOLD}Evidence ({summary.total_count} items){RESET}\n"]

        if summary.total_count == 0:
            lines.append(f"{DIM}No evidence collected yet. Navigate to gather evidence.{RESET}")
        else:
            # Group by strength
            from protocols.exploration.types import EvidenceStrength
            evidence_list = harness.evidence_collector._evidence

            strong = [e for e in evidence_list if e.strength == EvidenceStrength.STRONG]
            moderate = [e for e in evidence_list if e.strength == EvidenceStrength.MODERATE]
            weak = [e for e in evidence_list if e.strength == EvidenceStrength.WEAK]

            if strong:
                lines.append(f"\n{GREEN}STRONG ({len(strong)}):{RESET}")
                for e in strong[:5]:
                    lines.append(f"  + {e.content[:60]}...")
                    node = e.metadata.get("node_path", "unknown")
                    lines.append(f"    {DIM}from {node}{RESET}")

            if moderate:
                lines.append(f"\n{YELLOW}MODERATE ({len(moderate)}):{RESET}")
                for e in moderate[:5]:
                    lines.append(f"  o {e.content[:60]}...")

            if weak:
                lines.append(f"\n{DIM}WEAK ({len(weak)}):{RESET}")
                for e in weak[:3]:
                    lines.append(f"  . {e.content[:50]}...")

            # Commitment potential
            lines.append(f"\n{BOLD}Commitment Potential:{RESET}")
            lines.append(f"  TENTATIVE:  {'YES' if summary.total_count >= 1 else 'NO'} (1+ evidence)")
            lines.append(f"  MODERATE:   {'YES' if summary.total_count >= 3 and summary.strong_count >= 1 else 'NO'} (3+ evidence, 1+ strong)")
            lines.append(f"  STRONG:     {'YES' if summary.total_count >= 5 and summary.strong_count >= 2 else 'NO'} (5+ evidence, 2+ strong)")

        return BasicRendering(
            summary=f"Evidence: {summary.total_count} items",
            content="\n".join(lines),
            metadata={
                "total": summary.total_count,
                "strong": summary.strong_count,
                "moderate": summary.moderate_count,
                "weak": summary.weak_count,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show navigation trail",
    )
    async def trail(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Show navigation trail."""
        BOLD = "\033[1m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()
        trail = harness.trail

        lines = [f"{BOLD}Navigation Trail ({len(trail.steps)} steps){RESET}\n"]

        if not trail.steps:
            lines.append(f"{DIM}No steps yet.{RESET}")
        else:
            for i, step in enumerate(trail.steps):
                edge_str = f" {YELLOW}--[{step.edge_taken}]-->{RESET}" if step.edge_taken else ""
                prefix = "+-" if i == len(trail.steps) - 1 else "|-"
                marker = f" {DIM}(current){RESET}" if i == len(trail.steps) - 1 else ""

                lines.append(f"  {prefix} {step.node}{edge_str}{marker}")

        return BasicRendering(
            summary=f"Trail: {len(trail.steps)} steps",
            content="\n".join(lines),
            metadata={
                "id": trail.id,
                "steps": [
                    {"node": s.node, "edge_taken": s.edge_taken}
                    for s in trail.steps
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exploration_state")],
        help="Commit a claim based on evidence",
    )
    async def commit(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        claim: str,
        level: str = "moderate",
    ) -> Renderable:
        """Attempt to commit a claim based on exploration evidence."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        RED = "\033[31m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}",
                metadata={"error": "no_exploration"},
            )

        from protocols.exploration.types import Claim as ClaimType, CommitmentLevel

        harness = self._ensure_harness()

        # Map level string to enum
        level_map = {
            "tentative": CommitmentLevel.TENTATIVE,
            "moderate": CommitmentLevel.MODERATE,
            "strong": CommitmentLevel.STRONG,
            "definitive": CommitmentLevel.DEFINITIVE,
        }
        commitment_level = level_map.get(level.lower(), CommitmentLevel.MODERATE)

        claim_obj = ClaimType(statement=claim)
        result = await harness.commit_claim(claim_obj, commitment_level)

        if result.approved:
            lines = [f"{GREEN}Claim Committed{RESET}\n"]
            lines.append(f"{BOLD}Claim:{RESET}    \"{claim}\"")
            lines.append(f"{BOLD}Level:{RESET}    {commitment_level.value.upper()}")
            lines.append(f"{BOLD}Evidence:{RESET} {result.evidence_count} items ({result.strong_count} strong)")
            lines.append("")
            lines.append(f"{GREEN}The claim is now recorded with commitment level.{RESET}")

            return BasicRendering(
                summary="Claim Committed",
                content="\n".join(lines),
                metadata={
                    "approved": True,
                    "claim": claim,
                    "level": commitment_level.value,
                    "evidence_count": result.evidence_count,
                    "strong_count": result.strong_count,
                },
            )
        else:
            lines = [f"{RED}Commitment Failed: {result.message}{RESET}\n"]
            lines.append(f"{BOLD}Requested level:{RESET} {commitment_level.value}")
            lines.append(f"{BOLD}Evidence:{RESET}        {result.evidence_count} items ({result.strong_count} strong)")
            lines.append("")
            lines.append(f"{DIM}Gather more evidence or try a lower commitment level.{RESET}")

            return BasicRendering(
                summary="Commitment Failed",
                content="\n".join(lines),
                metadata={
                    "approved": False,
                    "claim": claim,
                    "level": commitment_level.value,
                    "evidence_count": result.evidence_count,
                    "strong_count": result.strong_count,
                    "message": result.message,
                },
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show loop detection status",
    )
    async def loops(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Show loop detection status."""
        BOLD = "\033[1m"
        RED = "\033[31m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not self._has_harness():
            return BasicRendering(
                summary="No Active Exploration",
                content=f"{DIM}No active exploration.{RESET}",
                metadata={"error": "no_exploration"},
            )

        harness = self._ensure_harness()
        detector = harness.loop_detector
        state = harness.get_state()

        lines = [f"{BOLD}Loop Detection Status{RESET}\n"]
        lines.append(f"{BOLD}Warnings:{RESET}        {state.loop_warnings}")
        lines.append(f"{BOLD}Halted:{RESET}          {'Yes' if harness.is_halted else 'No'}")

        if harness.is_halted:
            lines.append(f"{RED}Halt reason:{RESET}    {harness._halt_reason}")

        lines.append(f"{BOLD}Path history:{RESET}    {len(detector._path_history)} entries")
        lines.append(f"{BOLD}Loop counts:{RESET}     {len(detector._loop_counts)} tracked")

        return BasicRendering(
            summary=f"Loops: {state.loop_warnings} warnings",
            content="\n".join(lines),
            metadata={
                "warnings": state.loop_warnings,
                "halted": harness.is_halted,
                "halt_reason": harness._halt_reason,
                "path_history_size": len(detector._path_history),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exploration_state")],
        help="Reset exploration state",
    )
    async def reset(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Reset exploration state."""
        GREEN = "\033[32m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        self._reset_harness()

        return BasicRendering(
            summary="Exploration Reset",
            content=f"{GREEN}Exploration state cleared.{RESET}\n\n"
            f"{DIM}Start a new exploration with: kg explore start <path>{RESET}",
            metadata={"reset": True},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect methods."""
        match aspect:
            case "start":
                path = kwargs.get("path", "")
                preset = kwargs.get("preset", "standard")
                return await self.start(observer, path, preset)
            case "navigate":
                edge = kwargs.get("edge", "")
                return await self.navigate(observer, edge)
            case "expand":
                portal_path = kwargs.get("portal_path", kwargs.get("path", ""))
                return await self.expand(observer, portal_path)
            case "collapse":
                # Collapse is same as expand but collapses - would need portal tree
                portal_path = kwargs.get("portal_path", kwargs.get("path", ""))
                return BasicRendering(
                    summary="Collapse not yet implemented",
                    content="Use kg op collapse instead",
                    metadata={"error": "not_implemented"},
                )
            case "budget":
                return await self.budget(observer)
            case "evidence":
                return await self.evidence(observer)
            case "trail":
                return await self.trail(observer)
            case "commit":
                claim = kwargs.get("claim", "")
                level = kwargs.get("level", "moderate")
                return await self.commit(observer, claim, level)
            case "loops":
                return await self.loops(observer)
            case "reset":
                return await self.reset(observer)
            case _:
                return BasicRendering(
                    summary=f"Unknown aspect: {aspect}",
                    content=f"Available aspects: {', '.join(EXPLORE_AFFORDANCES)}",
                    metadata={"error": "unknown_aspect"},
                )


# === Factory Functions ===

_node: ExploreNode | None = None


def get_explore_node() -> ExploreNode:
    """Get the singleton ExploreNode."""
    global _node
    if _node is None:
        _node = ExploreNode()
    return _node


def set_explore_node(node: ExploreNode | None) -> None:
    """Set the singleton ExploreNode (for testing)."""
    global _node
    _node = node


__all__ = [
    "EXPLORE_AFFORDANCES",
    "ExploreNode",
    "get_explore_node",
    "set_explore_node",
]
