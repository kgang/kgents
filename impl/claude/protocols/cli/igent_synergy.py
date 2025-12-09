"""
I-gent Synergy - Bridge between CLI and I-gent visualization.

Implements the cross-cutting concerns from spec/protocols/cli.md and
spec/i-gents/README.md:

1. Status Whisper: Minimal persistent presence at edge of attention
   - Shows integrity score + trend in prompt
   - Pulses on significant changes

2. Semantic Glint: Context-aware completion suggestions
   - Not autocomplete - empathic perception
   - Appears grey and patient, dissolves if ignored

3. Garden Bridge: CLI ↔ Garden view coordination
   - `kgents garden` opens live garden
   - `--garden` flag on commands shows progress
   - Session state synchronization

This module enables the "batteries included" I-gent integration
described in the spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Any


# =============================================================================
# Status Whisper
# =============================================================================


class WhisperState(Enum):
    """Status whisper visual states."""

    NORMAL = "normal"  # Standard display
    PULSE = "pulse"  # Brief highlight on change
    DREAMING = "dreaming"  # System is consolidating (◇)
    ALERT = "alert"  # Attention needed


@dataclass
class StatusWhisper:
    """
    A persistent, minimal presence at the edge of attention.

    From membrane.md: The whisper shows integrity score and trend,
    pulsing gently on significant changes.

    Visual format:
        ~/project $ ▌                              ◉ 0.82 ▵

    Integration points:
    - Shell prompt (PS1 integration)
    - Editor status bar (VS Code, vim)
    - Terminal title
    """

    integrity_score: float = 1.0
    trend: str = "stable"  # "improving", "stable", "declining"
    state: WhisperState = WhisperState.NORMAL
    last_updated: datetime = field(default_factory=datetime.now)
    _callbacks: list[Callable[[float, str], None]] = field(default_factory=list)

    def render(self) -> str:
        """
        Render the whisper as a compact string.

        Format: ◉ 0.82 ▵
        """
        trend_symbol = {
            "improving": "▵",
            "stable": "",
            "declining": "▿",
        }.get(self.trend, "")

        state_symbol = {
            WhisperState.NORMAL: "◉",
            WhisperState.PULSE: "●",
            WhisperState.DREAMING: "◇",
            WhisperState.ALERT: "◈",
        }.get(self.state, "◉")

        return f"{state_symbol} {self.integrity_score:.2f} {trend_symbol}".strip()

    def render_prompt_segment(self) -> str:
        """Render as shell prompt segment (for PS1)."""
        return f"[{self.render()}]"

    def update(self, integrity_score: float, trend: str = "stable") -> None:
        """
        Update whisper state.

        Triggers pulse if significant change detected.
        """
        old_score = self.integrity_score
        self.integrity_score = integrity_score
        self.trend = trend
        self.last_updated = datetime.now()

        # Pulse on significant change
        if abs(integrity_score - old_score) > 0.1:
            self.state = WhisperState.PULSE
            # Reset to normal after brief delay (in async context)

        # Notify callbacks
        for callback in self._callbacks:
            callback(integrity_score, trend)

    def on_change(self, callback: Callable[[float, str], None]) -> None:
        """Register callback for changes."""
        self._callbacks.append(callback)

    def enter_dreaming(self) -> None:
        """Signal that system is dreaming (consolidating)."""
        self.state = WhisperState.DREAMING

    def wake(self) -> None:
        """Signal that system has awakened from dreaming."""
        self.state = WhisperState.PULSE

    @classmethod
    def get_ps1_command(cls) -> str:
        r"""
        Get shell command for PS1 integration.

        Usage in .bashrc/.zshrc:
            export PS1="$(kgents whisper) \$ "
        """
        return "kgents whisper --format=prompt"


# =============================================================================
# Semantic Glint
# =============================================================================


@dataclass
class GlintSuggestion:
    """A single glint suggestion."""

    text: str
    confidence: float  # 0.0-1.0
    context: str  # Why this suggestion
    source: str  # What context triggered it ("git", "tension", "pattern")


@dataclass
class SemanticGlint:
    """
    Context-aware completion suggestions.

    From membrane.md: The shell perceives the shape of emerging intention
    and offers resonance. Not autocomplete - empathic perception.

    The Glint:
    - Appears grey and patient
    - Dissolves if ignored
    - Materializes if approached
    - Never interrupts

    Integration points:
    - Git hooks (commit message suggestions)
    - Editor inline suggestions
    - CLI completion
    """

    confidence_threshold: float = 0.7
    respect_focus: bool = True  # Disappear in focus mode
    _suggestions: list[GlintSuggestion] = field(default_factory=list)
    _active: bool = True

    def generate(
        self,
        input_buffer: str,
        context: dict[str, Any] | None = None,
    ) -> GlintSuggestion | None:
        """
        Generate a glint suggestion based on context.

        Returns None if confidence below threshold or no suggestion.
        """
        if not self._active:
            return None

        context = context or {}

        # Context sources:
        # - staged_files: Git staged files
        # - active_tensions: Current tensions from membrane
        # - recent_commands: Command history
        # - current_dir: Working directory

        suggestion = self._analyze_context(input_buffer, context)

        if suggestion and suggestion.confidence >= self.confidence_threshold:
            self._suggestions.append(suggestion)
            return suggestion

        return None

    def _analyze_context(
        self,
        input_buffer: str,
        context: dict[str, Any],
    ) -> GlintSuggestion | None:
        """
        Analyze context and generate suggestion.

        Full implementation would use:
        - Recent command history
        - Active tensions
        - Staged files (for git)
        - Current working directory patterns
        """
        # Git commit message suggestion
        if "git commit" in input_buffer and "staged_files" in context:
            staged = context["staged_files"]
            if staged:
                # Infer commit type from file patterns
                commit_type = self._infer_commit_type(staged)
                files_desc = self._describe_files(staged)

                return GlintSuggestion(
                    text=f'-m "{commit_type}: {files_desc}"',
                    confidence=0.75,
                    context=f"Based on staged files: {', '.join(staged[:3])}",
                    source="git",
                )

        # Tension-aware suggestion
        if "active_tensions" in context and context["active_tensions"]:
            tensions = context["active_tensions"]
            if tensions and any(
                t.get("shape_id", "").endswith("-curve") for t in tensions
            ):
                curve = next(
                    t for t in tensions if t.get("shape_id", "").endswith("-curve")
                )
                return GlintSuggestion(
                    text=f"# Note: working within {curve.get('topic', 'high tension')} area",
                    confidence=0.6,
                    context=f"Active tension: {curve.get('shape_id')}",
                    source="tension",
                )

        return None

    def _infer_commit_type(self, files: list[str]) -> str:
        """Infer conventional commit type from files."""
        file_str = " ".join(files).lower()

        if "test" in file_str:
            return "test"
        elif "readme" in file_str or "doc" in file_str:
            return "docs"
        elif "fix" in file_str:
            return "fix"
        elif any(f.endswith(".md") for f in files):
            return "docs"
        else:
            return "feat"

    def _describe_files(self, files: list[str]) -> str:
        """Generate brief description of file changes."""
        if len(files) == 1:
            name = Path(files[0]).stem
            return f"update {name}"
        elif len(files) <= 3:
            names = [Path(f).stem for f in files]
            return f"update {', '.join(names)}"
        else:
            return f"update {len(files)} files"

    def render(self, suggestion: GlintSuggestion | None) -> str:
        """
        Render glint as grey, patient text.

        The glint appears inline, grey (not bright), ready to dissolve.
        """
        if not suggestion:
            return ""

        # ANSI grey: \033[90m ... \033[0m
        return f"\033[90m{suggestion.text}\033[0m"

    def disable(self) -> None:
        """Disable glint suggestions (e.g., in focus mode)."""
        self._active = False

    def enable(self) -> None:
        """Re-enable glint suggestions."""
        self._active = True


# =============================================================================
# Garden Bridge
# =============================================================================


class GardenPhase(Enum):
    """Moon phases from I-gent spec."""

    DORMANT = "○"  # Defined but not instantiated
    WAKING = "◐"  # Partially active
    ACTIVE = "●"  # Fully alive
    WANING = "◑"  # Cooling down
    EMPTY = "◌"  # Error state


@dataclass
class AgentState:
    """State of an agent in the garden."""

    agent_id: str
    genus: str
    phase: GardenPhase
    birth_time: datetime
    joy: float = 1.0  # 0.0-1.0
    ethics: float = 1.0  # 0.0-1.0
    composes_with: tuple[str, ...] = ()
    margin_notes: list[dict] = field(default_factory=list)


@dataclass
class GardenState:
    """
    State of the I-gent garden view.

    Synchronized between CLI operations and garden visualization.
    """

    name: str
    session_start: datetime = field(default_factory=datetime.now)
    agents: dict[str, AgentState] = field(default_factory=dict)
    breath_phase: str = "exhale"  # "inhale", "exhale"
    focus_agent: str | None = None
    global_notes: list[dict] = field(default_factory=list)

    def add_agent(self, state: AgentState) -> None:
        """Add or update agent in garden."""
        self.agents[state.agent_id] = state

    def get_agent(self, agent_id: str) -> AgentState | None:
        """Get agent state by ID."""
        return self.agents.get(agent_id)

    def add_note(self, content: str, source: str = "system") -> None:
        """Add global margin note."""
        self.global_notes.append(
            {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "content": content,
            }
        )


@dataclass
class GardenBridge:
    """
    Bridge between CLI and Garden visualization.

    Enables:
    - `kgents garden` command to open live garden
    - `--garden` flag to show progress during operations
    - Session state synchronization via D-gent
    """

    state: GardenState | None = None
    whisper: StatusWhisper = field(default_factory=StatusWhisper)
    glint: SemanticGlint = field(default_factory=SemanticGlint)
    _render_callback: Callable[[GardenState], None] | None = None

    def initialize(self, name: str = "kgents") -> GardenState:
        """Initialize a new garden session."""
        self.state = GardenState(name=name)

        # Add bootstrap agents
        self.state.add_agent(
            AgentState(
                agent_id="Ground",
                genus="bootstrap",
                phase=GardenPhase.ACTIVE,
                birth_time=datetime.now(),
            )
        )

        return self.state

    def on_render(self, callback: Callable[[GardenState], None]) -> None:
        """Register callback for garden rendering."""
        self._render_callback = callback

    def update_agent(
        self,
        agent_id: str,
        phase: GardenPhase | None = None,
        joy: float | None = None,
        ethics: float | None = None,
    ) -> None:
        """Update agent state and trigger render."""
        if not self.state:
            return

        agent = self.state.get_agent(agent_id)
        if not agent:
            return

        # Create updated state (AgentState is not frozen, so we can mutate)
        if phase is not None:
            agent.phase = phase
        if joy is not None:
            agent.joy = joy
        if ethics is not None:
            agent.ethics = ethics

        # Trigger render
        if self._render_callback:
            self._render_callback(self.state)

    def add_margin_note(
        self,
        agent_id: str | None,
        content: str,
        source: str = "system",
    ) -> None:
        """Add margin note to agent or global."""
        if not self.state:
            return

        note = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "content": content,
        }

        if agent_id:
            agent = self.state.get_agent(agent_id)
            if agent:
                agent.margin_notes.append(note)
        else:
            self.state.global_notes.append(note)

    def render_glyphs(self) -> str:
        """
        Render all agents as glyphs.

        Format: ●A  ○B  ◐C  ●K
        """
        if not self.state:
            return ""

        glyphs = []
        for agent_id, agent in self.state.agents.items():
            symbol = agent.phase.value
            letter = agent.genus[0].upper() if agent.genus else agent_id[0].upper()
            glyphs.append(f"{symbol}{letter}")

        return "  ".join(glyphs)

    def render_garden_ascii(self) -> str:
        """
        Render garden as ASCII art.

        From I-gent spec: The garden view shows agents in spatial relationship.
        """
        if not self.state:
            return "No garden initialized. Run 'kgents garden' to start."

        lines = [
            f"--- {self.state.name} garden --- t: {_format_elapsed(self.state.session_start)} ---",
            "",
        ]

        # Render agents
        for agent_id, agent in self.state.agents.items():
            phase_str = {
                GardenPhase.DORMANT: "dormant",
                GardenPhase.WAKING: "waking",
                GardenPhase.ACTIVE: "active",
                GardenPhase.WANING: "waning",
                GardenPhase.EMPTY: "error",
            }.get(agent.phase, "unknown")

            lines.append(f"  {agent.phase.value} {agent_id:<15} [{phase_str}]")

            # Show composition relationships
            if agent.composes_with:
                for comp in agent.composes_with:
                    lines.append(f"       └─> {comp}")

        lines.append("")

        # Breath cycle
        breath = (
            "░░░░████░░░░" if self.state.breath_phase == "exhale" else "████░░░░████"
        )
        lines.append(f"breath: {breath}  ({self.state.breath_phase})")

        # Focus
        if self.state.focus_agent:
            lines.append(f"focus: [{self.state.focus_agent}]")

        lines.append("")

        return "\n".join(lines)

    def to_session_json(self) -> dict:
        """Export garden state for session persistence."""
        if not self.state:
            return {}

        return {
            "name": self.state.name,
            "session_start": self.state.session_start.isoformat(),
            "agents": {
                aid: {
                    "agent_id": a.agent_id,
                    "genus": a.genus,
                    "phase": a.phase.name,
                    "birth_time": a.birth_time.isoformat(),
                    "joy": a.joy,
                    "ethics": a.ethics,
                    "composes_with": list(a.composes_with),
                    "margin_notes": a.margin_notes,
                }
                for aid, a in self.state.agents.items()
            },
            "global_notes": self.state.global_notes,
        }


# =============================================================================
# Helpers
# =============================================================================


def _format_elapsed(start: datetime) -> str:
    """Format elapsed time as HH:MM:SS."""
    elapsed = datetime.now() - start
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# =============================================================================
# CLI Integration Functions
# =============================================================================


def get_whisper_for_prompt() -> str:
    """Get whisper string for shell prompt integration."""
    whisper = StatusWhisper()
    # TODO: Load actual state from D-gent persistence
    return whisper.render_prompt_segment()


def get_glint_for_input(input_buffer: str, context: dict | None = None) -> str:
    """Get glint suggestion for current input."""
    glint = SemanticGlint()
    suggestion = glint.generate(input_buffer, context)
    return glint.render(suggestion)


async def run_garden_tui() -> None:
    """
    Launch interactive garden TUI.

    This is the entry point for `kgents garden` command.
    Full implementation would use Textual for rich terminal UI.
    """
    bridge = GardenBridge()
    state = bridge.initialize("interactive")

    print(bridge.render_garden_ascii())
    print("\nGarden TUI requires 'textual' package for full experience.")
    print("Install with: pip install textual")
    print("\nFor now, use:")
    print("  kgents membrane observe  - Full topological observation")
    print("  kgents membrane sense    - Quick shape intuition")
    print("  kgents mirror status     - Check integrity score")
