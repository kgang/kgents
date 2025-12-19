"""
MemoryMapScreen - Visualization of Four Pillars Memory State.

Shows the M-gent memory architecture:
- Memory Crystal: Holographic patterns with resolution levels
- Pheromone Field: Stigmergic traces and gradients
- Language Games: Available moves and game state
- Active Inference: Free energy budgets and beliefs

This screen provides real-time insight into the autopoietic memory system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

if TYPE_CHECKING:
    from agents.m import (
        ActiveInferenceAgent,
        LanguageGame,
        MemoryCrystal,
        PheromoneField,
    )


class MemoryMapScreen(Screen[None]):
    """
    Memory Map - Visualization of Four Pillars state.

    Shows holographic memory, pheromone fields, language games,
    and active inference state in a unified dashboard.
    """

    CSS = """
    MemoryMapScreen {
        background: #1a1a1a;
    }

    MemoryMapScreen #main-container {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
    }

    MemoryMapScreen .panel {
        border: solid #4a4a5c;
        padding: 1;
        background: #252525;
    }

    MemoryMapScreen .panel-title {
        text-style: bold;
        color: #e6a352;
        margin-bottom: 1;
    }

    MemoryMapScreen .header-bar {
        dock: top;
        height: 3;
        background: #252525;
        border-bottom: solid #4a4a5c;
        padding: 1 2;
        color: #f5f0e6;
    }

    MemoryMapScreen .metric-label {
        color: #b3a89a;
    }

    MemoryMapScreen .metric-value {
        color: #f5d08a;
    }

    MemoryMapScreen .hot {
        color: #ff6b6b;
    }

    MemoryMapScreen .warm {
        color: #feca57;
    }

    MemoryMapScreen .cool {
        color: #54a0ff;
    }

    MemoryMapScreen .cold {
        color: #5f6f87;
    }

    MemoryMapScreen .resolution-bar {
        color: #48dbfb;
    }

    MemoryMapScreen .gradient-bar {
        color: #ff9f43;
    }

    MemoryMapScreen .info {
        color: #8b7ba5;
    }

    MemoryMapScreen .warning {
        color: #c97b84;
    }

    MemoryMapScreen .success {
        color: #1dd1a1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "consolidate", "Consolidate", show=True),
        Binding("d", "decay", "Decay", show=True),
        Binding("s", "toggle_simulation", "Toggle Sim", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive state
    crystal_data: reactive[dict[str, Any]] = reactive({})
    field_data: reactive[dict[str, Any]] = reactive({})
    inference_data: reactive[dict[str, Any]] = reactive({})
    simulation_active: reactive[bool] = reactive(True)

    def __init__(
        self,
        crystal: "MemoryCrystal[Any] | None" = None,
        field: "PheromoneField | None" = None,
        inference: "ActiveInferenceAgent[Any] | None" = None,
        games: dict[str, "LanguageGame[Any]"] | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode
        self._crystal = crystal
        self._field = field
        self._inference = inference
        self._games = games or {}

        # In demo mode, create demo data
        if demo_mode:
            self._setup_demo_data()

    def _setup_demo_data(self) -> None:
        """Set up demo data for visualization."""
        try:
            import asyncio

            from agents.m import (
                ActiveInferenceAgent,
                Belief,
                MemoryCrystal,
                PheromoneField,
                create_dialectical_game,
                create_recall_game,
            )

            # Create demo crystal
            self._crystal = MemoryCrystal[str](dimension=64)
            self._crystal.store("python_tips", "Tips for Python coding", [0.9] * 64)
            self._crystal.store("rust_memory", "Rust memory safety", [0.8] * 64)
            self._crystal.store("js_async", "JavaScript async patterns", [0.6] * 64)
            self._crystal.store("old_notes", "Some old notes", [0.3] * 64)
            self._crystal.demote("old_notes", factor=0.3)

            # Create demo pheromone field
            self._field = PheromoneField(decay_rate=0.1)

            # Create demo inference
            belief = Belief(
                distribution={
                    "python": 0.4,
                    "rust": 0.3,
                    "javascript": 0.2,
                    "other": 0.1,
                },
                precision=1.2,
            )
            self._inference = ActiveInferenceAgent(belief)

            # Create demo games
            self._games = {
                "recall": create_recall_game(),
                "dialectical": create_dialectical_game(),
            }

        except ImportError:
            pass

    async def on_mount(self) -> None:
        """Refresh data when mounted."""
        await self._refresh_data()

        # Start simulation timer in demo mode
        if self._demo_mode:
            self.set_interval(0.5, self._simulate_activity)

    async def _refresh_data(self) -> None:
        """Refresh all data from sources."""
        # Crystal data
        if self._crystal:
            stats = self._crystal.stats()
            self.crystal_data = {
                "dimension": stats["dimension"],
                "concept_count": stats["concept_count"],
                "hot_count": stats["hot_count"],
                "avg_resolution": stats["avg_resolution"],
                "min_resolution": stats["min_resolution"],
                "max_resolution": stats["max_resolution"],
                "patterns": list(self._crystal.concepts)[:10],
                "resolutions": dict(
                    sorted(
                        self._crystal.resolution_levels.items(),
                        key=lambda x: -x[1],
                    )[:10]
                ),
                "hot_patterns": list(self._crystal.hot_patterns),
            }

        # Field data
        if self._field:
            gradients = await self._field.sense()
            stats = self._field.stats()
            self.field_data = {
                "concept_count": stats["concept_count"],
                "trace_count": stats["trace_count"],
                "deposit_count": stats["deposit_count"],
                "evaporation_count": stats["evaporation_count"],
                "avg_intensity": stats["avg_intensity"],
                "decay_rate": stats["decay_rate"],
                "top_gradients": [
                    {
                        "concept": g.concept,
                        "intensity": g.total_intensity,
                        "traces": g.trace_count,
                    }
                    for g in gradients[:8]
                ],
            }

        # Inference data
        if self._inference:
            self.inference_data = {
                "precision": self._inference.belief.precision,
                "entropy": self._inference.belief.entropy(),
                "concepts": dict(
                    sorted(
                        self._inference.belief.distribution.items(),
                        key=lambda x: -x[1],
                    )[:8]
                ),
                "budgets": {
                    cid: {
                        "free_energy": b.free_energy,
                        "complexity": b.complexity_cost,
                        "accuracy": b.accuracy_gain,
                    }
                    for cid, b in list(self._inference._memory_budgets.items())[:5]
                },
            }

        self.refresh()

    async def _simulate_activity(self) -> None:
        """
        Simulate agent activity for real-time demo visualization.

        This method probabilistically:
        - Accesses crystal patterns (weighted by resolution)
        - Deposits pheromone traces simulating agent activity
        - Slightly updates belief precision (random drift)
        """
        if not self.simulation_active:
            return

        import random

        # Simulate crystal access (promote/demote patterns)
        if self._crystal:
            concepts = list(self._crystal.concepts)
            if concepts:
                # Weighted selection by resolution
                resolutions = [self._crystal.resolution_levels.get(c, 0.5) for c in concepts]
                total_weight = sum(resolutions)

                if total_weight > 0:
                    # Normalize to probabilities
                    probs = [r / total_weight for r in resolutions]

                    # Select concept based on resolution (higher = more likely)
                    concept = random.choices(concepts, weights=probs, k=1)[0]

                    # 70% chance to promote (simulate access), 30% to demote (simulate decay)
                    if random.random() < 0.7:
                        self._crystal.promote(concept, factor=1.05)  # Small boost
                    else:
                        self._crystal.demote(concept, factor=0.98)  # Small decay

        # Simulate pheromone deposits (agent activity traces)
        if self._field:
            # Generate random concept from existing concepts or demo concepts
            demo_concepts = [
                "python",
                "rust",
                "typescript",
                "functional",
                "docker",
                "testing",
                "memory",
                "inference",
            ]

            concept = random.choice(demo_concepts)
            intensity = random.uniform(0.5, 2.0)
            agent_id = random.choice(["coder", "reviewer", "tester", "analyst"])

            await self._field.deposit(concept, intensity, f"{agent_id}_agent")

        # Simulate belief precision drift
        if self._inference:
            # Small random walk in precision
            drift = random.uniform(-0.02, 0.03)  # Slight upward bias
            new_precision = max(0.5, min(2.0, self._inference.belief.precision + drift))
            self._inference.belief.precision = new_precision

            # Occasionally add/update belief distribution
            if random.random() < 0.2:
                concepts = list(self._inference.belief.distribution.keys())
                if concepts:
                    # Randomly adjust one concept's probability
                    concept = random.choice(concepts)
                    current = self._inference.belief.distribution[concept]
                    adjustment = random.uniform(-0.05, 0.05)
                    new_value = max(0.01, min(0.9, current + adjustment))

                    # Renormalize distribution
                    total = sum(self._inference.belief.distribution.values())
                    if total > 0:
                        self._inference.belief.distribution[concept] = new_value
                        # Renormalize all
                        total = sum(self._inference.belief.distribution.values())
                        for k in self._inference.belief.distribution:
                            self._inference.belief.distribution[k] /= total

        # Refresh the display
        await self._refresh_data()

    def compose(self) -> ComposeResult:
        """Compose the memory map screen."""
        yield Header()

        # Header bar
        with Container(classes="header-bar"):
            yield Static(
                "[bold #f5d08a]MEMORY MAP[/] - Four Pillars Visualization",
                id="header-text",
            )

        # Main grid
        with Container(id="main-container"):
            # Panel 1: Memory Crystal
            with ScrollableContainer(classes="panel"):
                yield Static("[Memory Crystal]", classes="panel-title")
                yield Static("", id="crystal-content")

            # Panel 2: Pheromone Field
            with ScrollableContainer(classes="panel"):
                yield Static("[Pheromone Field]", classes="panel-title")
                yield Static("", id="field-content")

            # Panel 3: Active Inference
            with ScrollableContainer(classes="panel"):
                yield Static("[Active Inference]", classes="panel-title")
                yield Static("", id="inference-content")

            # Panel 4: Language Games
            with ScrollableContainer(classes="panel"):
                yield Static("[Language Games]", classes="panel-title")
                yield Static("", id="games-content")

        yield Footer()

    def watch_crystal_data(self, data: dict[str, Any]) -> None:
        """Update crystal panel when data changes."""
        try:
            content = self.query_one("#crystal-content", Static)
            content.update(self._render_crystal(data))
        except Exception:
            pass

    def watch_field_data(self, data: dict[str, Any]) -> None:
        """Update field panel when data changes."""
        try:
            content = self.query_one("#field-content", Static)
            content.update(self._render_field(data))
        except Exception:
            pass

    def watch_inference_data(self, data: dict[str, Any]) -> None:
        """Update inference panel when data changes."""
        try:
            content = self.query_one("#inference-content", Static)
            content.update(self._render_inference(data))
        except Exception:
            pass

    def watch_simulation_active(self, active: bool) -> None:
        """Update header when simulation state changes."""
        try:
            header = self.query_one("#header-text", Static)
            sim_status = "[#1dd1a1]SIM:ON[/]" if active else "[#8b7ba5]SIM:OFF[/]"
            header.update(f"[bold #f5d08a]MEMORY MAP[/] - Four Pillars Visualization  {sim_status}")
        except Exception:
            pass

    def _render_crystal(self, data: dict[str, Any]) -> str:
        """Render crystal data as formatted string."""
        if not data:
            return "[#8b7ba5]No crystal data available[/]"

        lines = []

        # Stats
        lines.append(
            f"[#b3a89a]Concepts:[/] [#f5d08a]{data.get('concept_count', 0)}[/]  "
            f"[#b3a89a]Dimension:[/] [#f5d08a]{data.get('dimension', 0)}[/]"
        )
        lines.append(
            f"[#b3a89a]Hot:[/] [#ff6b6b]{data.get('hot_count', 0)}[/]  "
            f"[#b3a89a]Avg Resolution:[/] [#f5d08a]{data.get('avg_resolution', 0):.2f}[/]"
        )
        lines.append("")

        # Resolution heat map
        lines.append("[#e6a352]Resolution Distribution:[/]")
        resolutions = data.get("resolutions", {})
        hot_patterns = set(data.get("hot_patterns", []))

        for cid, res in resolutions.items():
            # Create resolution bar
            bar_len = int(res * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)

            # Color based on resolution
            if res >= 0.8:
                color = "#ff6b6b"  # hot
            elif res >= 0.5:
                color = "#feca57"  # warm
            elif res >= 0.3:
                color = "#54a0ff"  # cool
            else:
                color = "#5f6f87"  # cold

            # Hot marker
            hot = "🔥" if cid in hot_patterns else "  "

            # Truncate concept id
            display_cid = cid[:15] if len(cid) > 15 else cid.ljust(15)

            lines.append(f"  {hot} {display_cid} [{color}]{bar}[/] {res:.2f}")

        return "\n".join(lines)

    def _render_field(self, data: dict[str, Any]) -> str:
        """Render pheromone field data as formatted string."""
        if not data:
            return "[#8b7ba5]No field data available[/]"

        lines = []

        # Stats
        lines.append(
            f"[#b3a89a]Concepts:[/] [#f5d08a]{data.get('concept_count', 0)}[/]  "
            f"[#b3a89a]Traces:[/] [#f5d08a]{data.get('trace_count', 0)}[/]"
        )
        lines.append(
            f"[#b3a89a]Deposits:[/] [#f5d08a]{data.get('deposit_count', 0)}[/]  "
            f"[#b3a89a]Evaporated:[/] [#f5d08a]{data.get('evaporation_count', 0)}[/]"
        )
        lines.append(f"[#b3a89a]Decay Rate:[/] [#f5d08a]{data.get('decay_rate', 0):.1%}[/]/hr")
        lines.append("")

        # Gradient visualization
        gradients = data.get("top_gradients", [])
        if gradients:
            lines.append("[#e6a352]Gradient Map:[/]")
            max_intensity = max((g["intensity"] for g in gradients), default=1.0)

            for g in gradients:
                normalized = g["intensity"] / max_intensity if max_intensity > 0 else 0
                bar_len = int(normalized * 20)

                # Use block characters for gradient effect
                blocks = "░▒▓█"
                bar = ""
                for i in range(20):
                    if i < bar_len:
                        block_idx = min(3, int((i / bar_len) * 4)) if bar_len > 0 else 0
                        bar += blocks[block_idx]
                    else:
                        bar += " "

                concept = g["concept"][:15].ljust(15)
                traces = g["traces"]

                lines.append(f"  {concept} [#ff9f43]{bar}[/] {g['intensity']:.1f} ({traces})")
        else:
            lines.append("[#8b7ba5]No traces deposited yet[/]")
            lines.append("")
            lines.append("Deposit traces with:")
            lines.append("  await field.deposit('concept', 1.0)")

        return "\n".join(lines)

    def _render_inference(self, data: dict[str, Any]) -> str:
        """Render active inference data as formatted string."""
        if not data:
            return "[#8b7ba5]No inference data available[/]"

        lines = []

        # Belief stats
        precision = data.get("precision", 1.0)
        entropy = data.get("entropy", 0.0)

        precision_color = "#1dd1a1" if precision >= 1.0 else "#c97b84"
        entropy_color = "#1dd1a1" if entropy < 1.5 else "#c97b84"

        lines.append(
            f"[#b3a89a]Precision:[/] [{precision_color}]{precision:.2f}[/]  "
            f"[#b3a89a]Entropy:[/] [{entropy_color}]{entropy:.2f}[/]"
        )
        lines.append("")

        # Belief distribution
        concepts = data.get("concepts", {})
        if concepts:
            lines.append("[#e6a352]Belief Distribution:[/]")
            for concept, prob in concepts.items():
                bar_len = int(prob * 30)
                bar = "█" * bar_len + "░" * (30 - bar_len)
                concept_disp = concept[:12].ljust(12)
                lines.append(f"  {concept_disp} [#54a0ff]{bar}[/] {prob:.2%}")
            lines.append("")

        # Free energy budgets
        budgets = data.get("budgets", {})
        if budgets:
            lines.append("[#e6a352]Free Energy Budgets:[/]")
            for cid, budget in budgets.items():
                fe = budget["free_energy"]
                fe_color = "#1dd1a1" if fe < 0 else "#c97b84"
                indicator = "✓" if fe < 0 else "⚠"

                cid_disp = cid[:15].ljust(15)
                lines.append(f"  {indicator} {cid_disp} F=[{fe_color}]{fe:+.2f}[/]")

        return "\n".join(lines)

    def compose_games_panel(self) -> str:
        """Compose the language games panel content."""
        if not self._games:
            return "[#8b7ba5]No language games registered[/]"

        lines = []
        lines.append(f"[#b3a89a]Registered Games:[/] [#f5d08a]{len(self._games)}[/]")
        lines.append("")

        for name, game in self._games.items():
            lines.append(f"[#e6a352]{name}[/]")

            # Show sample directions from a test position
            try:
                directions = game.directions("test")
                if directions:
                    dir_list = ", ".join(sorted(directions)[:5])
                    lines.append(f"  [#b3a89a]Directions:[/] {dir_list}")
            except Exception:
                lines.append("  [#8b7ba5]No directions from 'test'[/]")

            lines.append("")

        lines.append("[#8b7ba5]Polynomial functor: P(y) = Σₛ y^{D(s)}[/]")

        return "\n".join(lines)

    async def on_show(self) -> None:
        """Update games panel when shown."""
        try:
            content = self.query_one("#games-content", Static)
            content.update(self.compose_games_panel())
        except Exception:
            pass

    def action_back(self) -> None:
        """Return to previous screen."""
        self.dismiss()

    async def action_refresh(self) -> None:
        """Refresh all data."""
        await self._refresh_data()
        self.notify("Memory map refreshed")

    async def action_consolidate(self) -> None:
        """Trigger memory consolidation."""
        if self._crystal and self._inference:
            try:
                from agents.m import InferenceGuidedCrystal

                guided = InferenceGuidedCrystal(self._crystal, self._inference)
                actions = await guided.consolidate()

                promoted = sum(1 for a in actions.values() if a == "promoted")
                demoted = sum(1 for a in actions.values() if a == "demoted")

                self.notify(f"Consolidated: {promoted} promoted, {demoted} demoted")
                await self._refresh_data()
            except Exception as e:
                self.notify(f"Consolidation error: {e}", severity="error")
        else:
            self.notify("No crystal/inference available", severity="warning")

    async def action_decay(self) -> None:
        """Apply pheromone decay."""
        if self._field:
            try:
                from datetime import timedelta

                evaporated = await self._field.decay(timedelta(hours=1))
                self.notify(f"Decay applied: {evaporated} traces evaporated")
                await self._refresh_data()
            except Exception as e:
                self.notify(f"Decay error: {e}", severity="error")
        else:
            self.notify("No pheromone field available", severity="warning")

    def action_toggle_simulation(self) -> None:
        """Toggle simulation on/off."""
        self.simulation_active = not self.simulation_active
        status = "active" if self.simulation_active else "paused"
        self.notify(f"Simulation {status}")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


# ========== Widget Classes for Embedding ==========


class MemoryCrystalWidget(Static):
    """Widget for displaying memory crystal state."""

    def __init__(
        self,
        crystal: "MemoryCrystal[Any] | None" = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._crystal = crystal

    def compose_view(self) -> str:
        """Compose the crystal view."""
        if not self._crystal:
            return "No crystal"

        stats = self._crystal.stats()
        lines = [
            "╭─ Memory Crystal ─────────────────╮",
            f"│ Concepts: {stats['concept_count']:>4}  Dimension: {stats['dimension']:>4} │",
            f"│ Hot: {stats['hot_count']:>4}  Avg Resolution: {stats['avg_resolution']:.2f}  │",
            "╰───────────────────────────────────╯",
        ]
        return "\n".join(lines)

    def on_mount(self) -> None:
        """Update content on mount."""
        self.update(self.compose_view())


class PheromoneFieldWidget(Static):
    """Widget for displaying pheromone field state."""

    def __init__(
        self,
        field: "PheromoneField | None" = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._field = field

    async def compose_view(self) -> str:
        """Compose the field view."""
        if not self._field:
            return "No field"

        gradients = await self._field.sense()
        stats = self._field.stats()

        lines = [
            "╭─ Pheromone Field ─────────────────╮",
            f"│ Concepts: {stats['concept_count']:>4}  Decay: {stats['decay_rate']:.1%}/hr │",
            "╰───────────────────────────────────╯",
        ]

        max_intensity = max((g.total_intensity for g in gradients), default=1.0)
        for result in gradients[:5]:
            normalized = result.total_intensity / max_intensity if max_intensity else 0
            bar = "░▒▓█"[min(3, int(normalized * 4))] * int(normalized * 15)
            lines.append(f"  {result.concept[:15]:<15} {bar} ({result.trace_count})")

        return "\n".join(lines)


class LanguageGameWidget(Static):
    """Widget for displaying language game state."""

    def __init__(
        self,
        game: "LanguageGame[Any] | None" = None,
        current_position: str = "",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._game = game
        self._position = current_position

    def compose_view(self) -> str:
        """Compose the game view."""
        if not self._game:
            return "No game"

        directions = self._game.directions(self._position)

        lines = [
            f"╭─ {self._game.name} Game ──────────────────╮",
            f"│ Position: {self._position[:20]:<20} │",
            "╰───────────────────────────────────╯",
            "",
            "Available Moves:",
        ]

        for d in sorted(directions):
            move = self._game.play(self._position, d)
            status = "✓" if move.is_grammatical else "✗"
            lines.append(f"  {status} {d} → {move.to_position[:20]}")

        return "\n".join(lines)

    def on_mount(self) -> None:
        """Update content on mount."""
        self.update(self.compose_view())
