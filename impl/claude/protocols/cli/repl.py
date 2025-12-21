"""
AGENTESE REPL: Interactive navigation through the five contexts.

The REPL embodies the verb-first ontology: commands are invocations,
not queries. Navigation feels like grasping handles in a living world.

Version: 1.0.0

Wave 6 Tutorial Mode (v1.0):
    - Tutorial mode (--tutorial) - guided learning of AGENTESE ontology
    - Auto-constructing lessons from REPL structure
    - Progress persistence and resume across sessions
    - Hot data caching for fast lesson loading

Wave 3 Intelligence Features:
    - Fuzzy matching for typo correction (rapidfuzz)
    - LLM suggestions for semantic matches (costs entropy)
    - Dynamic completion from live Logos registry
    - Session persistence across restarts
    - Script mode for non-interactive execution
    - Command history search (Ctrl+R behavior)

Wave 2.5 Hardening (73 tests):
    - Edge case handling (unicode, long paths, special chars)
    - Security audit (shell injection prevention, input validation)
    - Performance benchmarks (navigation < 5ms, completion < 5ms)
    - Stress tested (1000+ rapid commands stable)
    - Input length limits (DoS protection)

Wave 2 Features:
    - Async execution via Logos (proper AGENTESE resolution)
    - Pipeline execution (>> composition actually runs)
    - Observer/Umwelt context switching (/observer command)
    - Rich output rendering (tables, panels, colors)
    - Error sympathy (errors suggest next actions)

Usage:
    kgents -i              # Enter interactive mode
    kgents --interactive   # Same as above
    kgents -i --restore    # Restore previous session
    kgents -i --script f   # Run script file non-interactively
    kgents -i --tutorial   # Start guided tutorial

Design Principles Applied:
    - Liturgical: Commands read like invocations
    - Joy-Inducing: Personality and warmth in responses
    - Transparent Infrastructure: Always shows what's happening
    - Graceful Degradation: Works even when subsystems are offline
    - Composable: Supports >> operator for path composition
    - Anticipatory: Fuzzy matching anticipates user intent

Navigation:
    self, world, concept, void, time  # Enter context
    agents, daemon, infra             # Navigate to holon
    ..                                # Go up one level
    .                                 # Show current path
    /                                 # Go to root

Commands:
    <path>                 # Invoke manifest aspect
    <path>.<aspect>        # Invoke specific aspect
    <path> >> <path>       # Compose paths (now executes!)
    ?                      # Show affordances
    ??                     # Detailed help
    /observer <archetype>  # Switch observer context
    /history [query]       # Search command history
    help                   # Show help
    exit, quit, q          # Leave REPL
"""

from __future__ import annotations

import asyncio
import random
import readline  # noqa: F401 - imported for side effects (history, editing)
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Sequence

# Wave 3: Intelligence imports (graceful degradation)
try:
    from .repl_fuzzy import FuzzyMatcher, LLMSuggester, is_fuzzy_available

    FUZZY_AVAILABLE = is_fuzzy_available()
except ImportError:
    FUZZY_AVAILABLE = False
    FuzzyMatcher = None  # type: ignore[assignment,misc]
    LLMSuggester = None  # type: ignore[assignment,misc]

try:
    from .repl_session import (
        clear_session,
        load_session,
        restore_session_to_state,
        save_session,
    )

    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False
    clear_session = None  # type: ignore[assignment]
    load_session = None  # type: ignore[assignment]
    restore_session_to_state = None  # type: ignore[assignment]
    save_session = None  # type: ignore[assignment]

# Rich imports for beautiful output (graceful degradation if unavailable)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore[misc, assignment]
    Panel = None  # type: ignore[misc, assignment]
    Table = None  # type: ignore[misc, assignment]
    Text = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Constants
# =============================================================================

CONTEXTS = frozenset({"self", "world", "concept", "void", "time"})

# Security: Maximum input length to prevent DoS
MAX_INPUT_LENGTH = 10000  # 10KB max
MAX_PATH_DEPTH = 100  # Maximum path segments

# Context -> Holons mapping (lazily populated)
CONTEXT_HOLONS: dict[str, list[str]] = {
    "self": ["status", "memory", "dream", "soul", "capabilities", "dashboard"],
    "world": ["agents", "daemon", "infra", "fixture", "exec", "dev", "town"],
    "concept": ["laws", "dialectic", "principle", "operad"],
    "void": ["entropy", "shadow", "serendipity", "gratitude", "archetype"],
    "time": ["trace", "past", "future", "schedule", "turn"],
}

WELCOME_BANNER = """\
\033[36m╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│   \033[1;37mkgents\033[0;36m  ·  \033[3mThe verb-first ontology\033[0;36m                          │
│                                                                 │
│   \033[33m"The noun is a lie. There is only the rate of change."\033[36m        │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯\033[0m

\033[90mContexts:\033[0m  self · world · concept · void · time
\033[90mCommands:\033[0m  ? (affordances) · ?? (help) · .. (up) · exit
\033[90mPipeline:\033[0m  path >> path  (compose and execute)
\033[90mSwitch:\033[0m    /observer <archetype>  (explorer, developer, architect)

"""

# Observer archetypes with their descriptions
OBSERVER_ARCHETYPES = {
    "explorer": "Curious newcomer, sees pedagogical affordances",
    "developer": "Skilled builder, sees technical affordances",
    "architect": "System designer, sees structural + define affordances",
    "admin": "Full access, sees all affordances including dangerous",
}

# =============================================================================
# Wave 4: Joy-Inducing Constants
# =============================================================================

# J1: Welcome message variations by time of day
WELCOME_VARIANTS = {
    "morning": [
        "Good morning. The forest awaits.",
        "Dawn breaks. What shall we explore?",
        "Morning light. Ready to navigate?",
    ],
    "afternoon": [
        "Good afternoon. Where to?",
        "The day is young. Navigate wisely.",
        "Afternoon. The paths are clear.",
    ],
    "evening": [
        "Good evening. The stars are watching.",
        "Night falls. Perfect time to explore the void.",
        "Evening. The forest grows quiet.",
    ],
    "returning": [
        "Welcome back. You were in {context}.",
        "Resuming from {context}. The river continues.",
        "Back again. {context} awaits.",
    ],
}

# J2: K-gent personality triggers
KGENT_TRIGGERS = frozenset(
    {
        "reflect",
        "advice",
        "feeling",
        "wisdom",
        "meaning",
        "advise",
        "challenge",
        "think",
        "ponder",
    }
)

# J2: Rate limiting interval (seconds between K-gent invocations)
KGENT_RATE_LIMIT_SECONDS = 30

# J3: Easter eggs - hidden delights
EASTER_EGGS = {
    "void.entropy.dance": "_easter_entropy_dance",
    "self.soul.sing": "_easter_soul_sing",
    "concept.zen": "_easter_concept_zen",
    "time.flow": "_easter_time_flow",
    "world.hello": "_easter_world_hello",
    "..........": "_easter_too_far",
}

# J3: Zen principles for concept.zen easter egg
ZEN_PRINCIPLES = [
    "The noun is a lie. There is only the rate of change.",
    "Agents are morphisms, not objects.",
    "Everything is slop or comes from slop.",
    "The observer is the observation.",
    "Compose, don't construct.",
    "Fun is free. Being/having fun is free.",
    "Say no more than yes.",
    "There is no view from nowhere.",
]

# Wave 4: Slash command shortcuts for joy-inducing commands
SLASH_SHORTCUTS = {
    "/oblique": "concept.creativity.oblique",
    "/constrain": "concept.creativity.constrain",
    "/yes-and": "concept.creativity.expand",
    "/expand": "concept.creativity.expand",
    "/surprise": "void.serendipity.prompt",
    "/surprise-me": "void.serendipity.prompt",
    "/project": "void.shadow.project",
    "/sparkline": "world.viz.sparkline",
    "/why": "self.soul.why",
    "/tension": "self.soul.tension",
    "/challenge": "self.soul.challenge",
    "/nphase": "concept.nphase.compile",
    "/nphase-validate": "concept.nphase.validate",
    "/nphase-template": "concept.nphase.template",
    "/nphase-bootstrap": "concept.nphase.bootstrap",
}

HELP_TEXT = """\
\033[1mAGENTESE REPL\033[0m - Navigate the five contexts

\033[1mNavigation:\033[0m
  self, world, concept, void, time   Enter a context
  <holon>                            Navigate to holon
  ..                                 Go up one level
  .                                  Show current path
  /                                  Return to root

\033[1mInvocation:\033[0m
  <path>                   Invoke with manifest aspect
  <path>.<aspect>          Invoke specific aspect (e.g., soul.reflect)
  <path> >> <path>         Compose paths into pipeline (executes!)

\033[1mIntrospection:\033[0m
  ?                        Show affordances for current node
  ??                       Detailed help for current node
  help                     Show this help

\033[1mObserver Control:\033[0m
  /observer                Show current observer archetype
  /observer <archetype>    Switch observer (explorer, developer, architect, admin)
  /observers               List all available archetypes

\033[1mLearning Mode:\033[0m (Wave 6)
  --learn                  Enable adaptive learning guide
  /learn                   See what to learn next
  /learn <topic>           Learn about specific topic
  /learn list              List all available topics
  /fluency                 See your skill progress
  /hint                    Get contextual hint

\033[1mTutorial Mode:\033[0m (Wave 6 - for absolute beginners)
  --tutorial               Linear guided intro to AGENTESE
  --tutorial --reset       Start tutorial from beginning

\033[1mAmbient Mode:\033[0m (Wave 5)
  --ambient                Launch passive dashboard (shows live system status)
  --interval <secs>        Set refresh interval (default: 5s)
  \033[90mKeybindings in ambient:\033[0m q=quit, r=refresh, space=pause, 1-5=focus

\033[1mJoy Features:\033[0m (Waves 4-6)
  - Time-aware welcomes (morning/afternoon/evening)
  - K-gent soul responses for philosophical queries
  - Contextual hints when you're stuck
  - Hidden easter eggs (discover them!)

\033[1mExamples:\033[0m
  \033[33mself\033[0m                       Enter self context
  \033[33msoul reflect\033[0m               Invoke self.soul.reflect
  \033[33mworld agents list\033[0m          List agents
  \033[33mvoid entropy sip\033[0m           Draw from Accursed Share
  \033[33mworld.agents >> count\033[0m      Pipeline: list then count
  \033[33m/observer developer\033[0m        Switch to developer observer
  \033[33m/nphase my.yml\033[0m             Compile ProjectDefinition (defaults to compile)
  \033[33m/nphase-validate my.yml\033[0m    Validate ProjectDefinition only
  \033[33m/nphase-template PLAN\033[0m      Show phase template
  \033[33m..\033[0m                         Go back up

\033[1mMeta:\033[0m
  exit, quit, q            Leave the REPL
  clear                    Clear screen
  history                  Show command history
  /history <query>         Search command history
  /memory                  Show conversation memory (Phase 4)
  /memory toggle           Toggle memory indicator in prompt
  /presence                Show agent presence (Phase 3)
  /presence toggle         Toggle presence display
"""


# =============================================================================
# Rich Console Singleton
# =============================================================================

# Global console for rich output (created once)
_console: Any = None


def get_console() -> Any:
    """Get or create the rich console (lazy initialization)."""
    global _console
    if _console is None and RICH_AVAILABLE:
        _console = Console()
    return _console


# =============================================================================
# Umwelt Wrapper (for cache tracking)
# =============================================================================


class _UmweltWrapper:
    """
    Wrapper around a frozen Umwelt to track observer type for cache invalidation.

    Since LightweightUmwelt is frozen, we can't add fields to it.
    This wrapper provides a mutable container.
    """

    def __init__(self, umwelt: Any, observer_type: str):
        self._umwelt = umwelt
        self._observer_type = observer_type

    @property
    def dna(self) -> Any:
        """Forward DNA access to wrapped umwelt."""
        return self._umwelt.dna

    async def get(self) -> Any:
        """Forward get to wrapped umwelt."""
        return await self._umwelt.get()

    async def set(self, value: Any) -> None:
        """Forward set to wrapped umwelt."""
        await self._umwelt.set(value)

    def is_grounded(self, output: Any) -> bool:
        """Forward is_grounded to wrapped umwelt."""
        result = self._umwelt.is_grounded(output)
        return bool(result)


# =============================================================================
# REPL State
# =============================================================================


@dataclass
class ReplState:
    """
    The REPL's current state.

    Principle: Transparent Infrastructure - state is always visible.

    Wave 5 Enhancements:
    - Ambient mode (passive dashboard)
    - Non-blocking keyboard for ambient keybindings

    Wave 3 Enhancements:
    - Fuzzy matcher for typo correction
    - LLM suggester for semantic matches
    - Entropy budget tracking
    - Session restoration flag

    Wave 2 Enhancements:
    - Observer archetype for affordance filtering
    - Logos integration for proper AGENTESE resolution
    - Rich console for beautiful output
    """

    # Current path (e.g., ["self", "soul"])
    path: list[str] = field(default_factory=list)

    # Command history for this session
    history: list[str] = field(default_factory=list)

    # Observer archetype (affects affordances)
    observer: str = "explorer"

    # Is REPL running?
    running: bool = True

    # Last result (for reference in subsequent commands)
    last_result: Any = None

    # Verbosity level
    verbose: bool = False

    # Wave 3: Entropy budget for LLM suggestions (refills each session)
    entropy_budget: float = 0.10  # 10% entropy per session

    # Wave 3: Session was restored from disk
    restored_session: bool = False

    # Wave 4: Consecutive error tracking for hints
    consecutive_errors: int = 0

    # Wave 4: Last K-gent invocation time for rate limiting
    last_kgent_time: Optional[datetime] = None

    # Wave 5: Ambient mode state
    ambient_paused: bool = False  # Is ambient refresh paused?
    ambient_focus: Optional[int] = None  # Focused panel (1-5, None = all)
    ambient_interval: float = 5.0  # Refresh interval in seconds

    # Logos resolver (lazy-loaded)
    _logos: Any = field(default=None, repr=False)

    # Umwelt for observer (lazy-loaded)
    _umwelt: Any = field(default=None, repr=False)

    # Wave 3: Fuzzy matcher (lazy-loaded)
    _fuzzy: Any = field(default=None, repr=False)

    # Wave 3: LLM suggester (lazy-loaded)
    _llm_suggester: Any = field(default=None, repr=False)

    # Wave 6: Adaptive learning guide (lazy-loaded)
    _guide: Any = field(default=None, repr=False)

    # Wave 6: Learning mode enabled
    learning_mode: bool = False

    # Phase 4 (CLI v7): Conversation window for 10+ turn memory
    _window: Any = field(default=None, repr=False)

    # Phase 4: Show window utilization in prompt
    show_window_utilization: bool = False

    # Phase 3 (CLI v7): Agent presence
    show_presence: bool = True  # Show agent presence status
    _kgent_cursor: Any = field(default=None, repr=False)

    @property
    def current_path(self) -> str:
        """Get the current path as a dotted string."""
        return ".".join(self.path) if self.path else ""

    @property
    def prompt(self) -> str:
        """Generate the prompt string with observer indicator.

        ANSI escape codes are wrapped with \\001 and \\002 markers so
        readline correctly calculates prompt width for cursor positioning.

        Phase 4 (CLI v7): Optionally shows window utilization when active.
        """

        # Helper to wrap ANSI codes for readline
        def rl(code: str) -> str:
            """Wrap ANSI code for readline (marks as non-printing)."""
            return f"\001{code}\002"

        # Observer indicator (abbreviated)
        obs_abbrev = {
            "explorer": "E",
            "developer": "D",
            "architect": "A",
            "admin": "*",
        }
        obs = obs_abbrev.get(self.observer, "?")

        gray = rl("\033[90m")
        reset = rl("\033[0m")
        cyan = rl("\033[36m")
        yellow = rl("\033[33m")

        # Phase 4: Window utilization indicator (when enabled and has turns)
        window_indicator = ""
        if self.show_window_utilization:
            window = self.get_window()
            if window is not None and window.turn_count > 0:
                window_indicator = f"{gray}[{window.turn_count}]{reset} "

        if not self.path:
            return f"{gray}({obs}){reset} {window_indicator}{cyan}[root]{reset} {yellow}»{reset} "

        # Color the context differently
        context = self.path[0]
        rest = ".".join(self.path[1:])

        context_colors = {
            "self": rl("\033[32m"),  # green
            "world": rl("\033[34m"),  # blue
            "concept": rl("\033[35m"),  # magenta
            "void": rl("\033[90m"),  # gray
            "time": rl("\033[33m"),  # yellow
        }

        color = context_colors.get(context, cyan)

        # Special indicator for soul dialogue mode
        magenta = rl("\033[35m")
        if context == "self" and rest == "soul":
            return f"{gray}({obs}){reset} {window_indicator}{color}[{context}{reset}.{rest}{color}]{reset} {magenta}💬{reset} "

        if rest:
            return f"{gray}({obs}){reset} {window_indicator}{color}[{context}{reset}.{rest}{color}]{reset} {yellow}»{reset} "
        else:
            return f"{gray}({obs}){reset} {window_indicator}{color}[{context}]{reset} {yellow}»{reset} "

    def get_logos(self) -> Any:
        """Get or create the Logos resolver (lazy initialization).

        Uses WiredLogos (AGENTESE v3) for path validation and proper integration.
        Falls back to plain Logos if WiredLogos unavailable.
        """
        if self._logos is None:
            try:
                # v3: Use WiredLogos for full integration
                from protocols.agentese import create_minimal_wired_logos

                self._logos = create_minimal_wired_logos()
            except ImportError:
                try:
                    # Fallback: plain Logos
                    from protocols.agentese.logos import create_logos

                    self._logos = create_logos()
                except ImportError:
                    pass  # Logos not available, will use CLI fallback
        return self._logos

    def get_umwelt(self) -> Any:
        """Get or create Umwelt for current observer (lazy initialization).

        v3: Uses Observer class from AGENTESE for proper gradation support.
        Falls back to legacy LightweightUmwelt if v3 Observer unavailable.
        """
        if self._umwelt is None or getattr(self._umwelt, "_observer_type", None) != self.observer:
            try:
                # v3: Use Observer class with from_archetype factory
                from protocols.agentese import Observer as V3Observer

                v3_observer = V3Observer.from_archetype(self.observer)
                # Wrap to track observer type for cache invalidation
                self._umwelt = _UmweltWrapper(v3_observer, self.observer)
            except (ImportError, AttributeError):
                # Fallback: Legacy LightweightUmwelt construction
                try:
                    from agents.d.volatile import VolatileAgent
                    from bootstrap.umwelt import LightweightUmwelt

                    # Create a simple DNA-like object for the observer
                    @dataclass
                    class ObserverDNA:
                        name: str = "repl_user"
                        archetype: str = "explorer"
                        capabilities: tuple[str, ...] = ()

                    dna = ObserverDNA(
                        name="repl_user",
                        archetype=self.observer,
                        capabilities=("manifest", "witness", "affordances")
                        if self.observer == "explorer"
                        else ("manifest", "witness", "affordances", "define")
                        if self.observer in ("developer", "architect", "admin")
                        else (),
                    )

                    # Create lightweight umwelt with volatile storage
                    storage: Any = VolatileAgent(_state={})
                    umwelt = LightweightUmwelt(
                        storage=storage,
                        dna=dna,
                        gravity=(),
                    )
                    # Wrap in a non-frozen container for cache tracking
                    self._umwelt = _UmweltWrapper(umwelt, self.observer)
                except ImportError:
                    pass  # Umwelt not available
        return self._umwelt

    def get_fuzzy(self) -> Any:
        """Get or create the fuzzy matcher (lazy initialization)."""
        if self._fuzzy is None and FuzzyMatcher is not None:
            self._fuzzy = FuzzyMatcher(threshold=80, limit=5)
        return self._fuzzy

    def get_llm_suggester(self) -> Any:
        """Get or create the LLM suggester (lazy initialization)."""
        if self._llm_suggester is None and LLMSuggester is not None:
            self._llm_suggester = LLMSuggester(entropy_cost=0.01)
        return self._llm_suggester

    def get_guide(self) -> Any:
        """Get or create the adaptive learning guide (lazy initialization)."""
        if self._guide is None:
            try:
                from protocols.cli.repl_guide import AdaptiveGuide, load_fluency

                tracker = load_fluency()
                self._guide = AdaptiveGuide(tracker=tracker, enabled=self.learning_mode)
            except ImportError:
                pass  # Guide not available
        return self._guide

    def get_window(self) -> Any:
        """
        Get or create the ConversationWindow (lazy initialization).

        Phase 4 (CLI v7): Deep Conversation
        - Bounded history with configurable max_turns (default 35)
        - Summarization when window fills (requires LLM)
        - 10+ turn memory for context-aware REPL

        The window tracks user inputs and REPL responses as turns,
        enabling the REPL to remember earlier context.
        """
        if self._window is None:
            try:
                from services.conductor.window import ConversationWindow

                self._window = ConversationWindow(
                    max_turns=35,  # Keep last 35 turns in full
                    strategy="hybrid",  # Sliding + summarization
                    context_window_tokens=8000,
                )
            except ImportError:
                pass  # ConversationWindow not available
        return self._window

    def record_turn(self, user_input: str, response: str) -> None:
        """
        Record a conversation turn in the window.

        Phase 4 (CLI v7): This enables 10+ turn memory by tracking
        user inputs and REPL responses as turns.

        Args:
            user_input: What the user typed
            response: The REPL's response (output)
        """
        window = self.get_window()
        if window is not None:
            # Only record non-trivial turns (not navigation, not help)
            if len(user_input) > 2 and len(response) > 10:
                window.add_turn(user_input, response)

    def get_window_status(self) -> str:
        """
        Get a compact status string for the window.

        Returns format: "(7/35)" showing turns used / max turns
        """
        window = self.get_window()
        if window is None:
            return ""
        return f"({window.turn_count}/{window.max_turns})"

    def get_kgent_cursor(self) -> Any:
        """
        Get or create the K-gent cursor (lazy initialization).

        Phase 3 (CLI v7): Agent Cursors
        - K-gent is the primary agent presence
        - Shows activity in the CLI footer
        - Updates as invocations are processed
        """
        if self._kgent_cursor is None:
            try:
                from protocols.agentese.presence import create_kgent_cursor

                self._kgent_cursor = create_kgent_cursor()
            except ImportError:
                pass  # Presence not available
        return self._kgent_cursor

    def update_presence(self, state: str, path: str | None = None, activity: str = "") -> None:
        """
        Update K-gent cursor presence state and broadcast to channel.

        Phase 3 (CLI v7): Updates the cursor and optionally prints status.
        Phase 5 (CLI v7): Now broadcasts to PresenceChannel for web canvas.

        Args:
            state: Cursor state (exploring, working, suggesting, waiting)
            path: AGENTESE path being focused
            activity: Brief description of activity
        """
        cursor = self.get_kgent_cursor()
        if cursor is None:
            return

        try:
            from protocols.agentese.presence import CursorState, get_presence_channel

            state_enum = CursorState(state.lower())
            cursor.transition(state_enum, path, activity)

            # Phase 5: Broadcast to channel for web canvas integration
            channel = get_presence_channel()
            try:
                # Try to get running loop (Python 3.10+ preferred method)
                try:
                    loop = asyncio.get_running_loop()
                    # Create task for broadcast (non-blocking)
                    loop.create_task(channel.broadcast(cursor))
                except RuntimeError:
                    # No running loop - run synchronously
                    asyncio.run(channel.broadcast(cursor))
            except RuntimeError:
                # Fallback: create new loop
                asyncio.run(channel.broadcast(cursor))
        except (ImportError, ValueError):
            pass  # Invalid state or presence not available

    def get_presence_status(self) -> str:
        """
        Get the current presence status text.

        Returns formatted status like "K-gent is exploring self.memory..."
        """
        cursor = self.get_kgent_cursor()
        if cursor is None:
            return ""

        try:
            from protocols.agentese.presence import CursorState

            # Don't show waiting state (too noisy)
            if cursor.state == CursorState.WAITING:
                return ""
            return cursor.format_status_text()
        except ImportError:
            return ""


# =============================================================================
# Command Handlers
# =============================================================================


def _expand_aliases(line: str) -> str:
    """
    Expand aliases in the input line.

    v3: Aliases are prefix expansions (first segment only).
    "me.challenge" → "self.soul.challenge" (if "me" → "self.soul")

    Args:
        line: Raw input line from user

    Returns:
        Line with aliases expanded
    """
    # Don't expand special navigation or slash commands
    if not line or line.startswith("/") or line in (".", "..", "..."):
        return line

    try:
        from protocols.agentese import expand_aliases

        # Get the global alias registry
        registry = get_alias_registry()
        if isinstance(registry, dict) and registry.get("_stub"):
            return line  # No registry available

        return expand_aliases(line, registry)
    except ImportError:
        return line


def _parse_path_input(line: str) -> list[str]:
    """
    Parse input line into path parts, supporting both formats.

    Wave 5.1: Supports dotted paths for fast-forward navigation.
    v3: Also expands aliases before parsing.

    Formats supported:
        "world dev"           → ["world", "dev"]       (space-separated)
        "world.dev"           → ["world", "dev"]       (dotted)
        "self.soul.reflect"   → ["self", "soul", "reflect"]
        "self soul reflect"   → ["self", "soul", "reflect"]
        "self.soul reflect"   → ["self", "soul", "reflect"]  (mixed)
        ".."                  → [".."]                 (special, preserved)
        "."                   → ["."]                  (special, preserved)
        "me.challenge"        → ["self", "soul", "challenge"]  (alias expanded)

    Args:
        line: Raw input line from user

    Returns:
        List of path segments
    """
    # Handle special navigation commands that use dots
    if line in (".", "..", "..."):
        return [line]

    # v3: Expand aliases first
    line = _expand_aliases(line)

    # Split by spaces first
    space_parts = line.split()

    # Then expand any dotted segments
    result = []
    for part in space_parts:
        # Don't split special commands or things starting with /
        if part in (".", "..") or part.startswith("/"):
            result.append(part)
        elif "." in part:
            # Split dotted path: "self.soul" → ["self", "soul"]
            result.extend(part.split("."))
        else:
            result.append(part)

    # Filter out empty strings (from leading/trailing dots)
    return [p for p in result if p]


def handle_navigation(state: ReplState, parts: list[str]) -> str | None:
    """
    Handle navigation commands.

    Returns a message to display, or None for no output.

    Supports:
    - Single-word navigation: `self`, `soul`, `..`, `/`, `.`
    - Fast-forward navigation: `self.soul`, `world.agents` (dotted paths to holons)

    Multi-word inputs with aspects (e.g., "self soul reflect") are invocations, not navigation.
    """
    if not parts:
        return None

    cmd = parts[0].lower()

    # Single-word commands first
    if len(parts) == 1:
        # Root navigation
        if cmd == "/":
            state.path = []
            return "\033[90m→ root\033[0m"

        # Go up
        if cmd == "..":
            if state.path:
                removed = state.path.pop()
                return f"\033[90m← {removed}\033[0m"
            return "\033[90m(already at root)\033[0m"

        # Show current path
        if cmd == ".":
            if state.path:
                return f"\033[36m{state.current_path}\033[0m"
            return "\033[36m(root)\033[0m"

        # Context navigation (single word - can switch from anywhere)
        if cmd in CONTEXTS:
            if not state.path or state.path[0] != cmd:
                state.path = [cmd]
                # Phase 5: Broadcast exploring state
                state.update_presence("exploring", cmd, f"Exploring {cmd}...")
                return f"\033[90m→ {cmd}\033[0m"
            # Already in this context - no-op
            return f"\033[90m(already in {cmd})\033[0m"

        # Holon navigation (when in a context, single word only)
        if len(state.path) == 1:
            context = state.path[0]
            holons = CONTEXT_HOLONS.get(context, [])
            if cmd in holons:
                state.path.append(cmd)
                full_path = f"{context}.{cmd}"
                # Phase 5: Broadcast exploring state
                state.update_presence("exploring", full_path, f"Exploring {full_path}...")
                # Special message for soul dialogue mode
                if context == "self" and cmd == "soul":
                    return (
                        "\033[90m→ soul\033[0m\n"
                        "\033[33mDialogue mode:\033[0m Text you type will be sent to K-gent soul.\n"
                        "\033[90mUse\033[0m ?\033[90m for affordances,\033[0m ..\033[90m to exit,\033[0m "
                        "reflect\033[90m/\033[0madvise\033[90m/\033[0mchallenge\033[90m/\033[0mexplore\033[90m for modes.\033[0m"
                    )
                return f"\033[90m→ {cmd}\033[0m"

        return None  # Not a navigation command

    # Fast-forward navigation: context.holon (exactly 2 parts)
    # e.g., "self.soul", "world.agents", "void.entropy"
    if len(parts) == 2:
        context = parts[0].lower()
        holon = parts[1].lower()

        if context in CONTEXTS:
            holons = CONTEXT_HOLONS.get(context, [])
            if holon in holons:
                # Valid fast-forward path - navigate there
                state.path = [context, holon]
                full_path = f"{context}.{holon}"
                # Phase 5: Broadcast exploring state
                state.update_presence("exploring", full_path, f"Exploring {full_path}...")
                # Special message for soul dialogue mode
                if context == "self" and holon == "soul":
                    return (
                        f"\033[90m→ {context}.{holon}\033[0m\n"
                        "\033[33mDialogue mode:\033[0m Text you type will be sent to K-gent soul.\n"
                        "\033[90mUse\033[0m ?\033[90m for affordances,\033[0m ..\033[90m to exit,\033[0m "
                        "reflect\033[90m/\033[0madvise\033[90m/\033[0mchallenge\033[90m/\033[0mexplore\033[90m for modes.\033[0m"
                    )
                return f"\033[90m→ {context}.{holon}\033[0m"

    # 3+ parts = likely an invocation (e.g., self.soul.reflect)
    return None


def handle_introspection(state: ReplState, cmd: str) -> str | None:
    """Handle ? and ?? commands."""
    if cmd == "?":
        return _show_affordances(state)
    elif cmd == "??":
        return _show_detailed_help(state)
    return None


def _show_affordances(state: ReplState) -> str:
    """Show affordances for current location.

    v3: Uses query API to get live affordances from Logos.
    Falls back to static CONTEXT_HOLONS if query unavailable.
    """
    # v3: Try to use query API for live affordances
    logos = state.get_logos()
    if logos is not None:
        result = _query_affordances(state, logos)
        if result is not None:
            return result

    # Fallback: static affordances
    return _show_static_affordances(state)


def _query_affordances(state: ReplState, logos: Any) -> str | None:
    """Use v3 query API to get live affordances."""
    try:
        from protocols.agentese import query

        current = state.current_path or ""
        observer = state.get_umwelt()

        if not current:
            # At root - query for contexts
            pattern = "?*"
        else:
            # Query children of current path
            pattern = f"?{current}.*"

        result = query(logos, pattern, limit=50, observer=observer)

        if not result:
            return None

        lines = ["\033[1mAffordances:\033[0m", ""]

        if not current:
            # Show contexts with descriptions
            context_descs = {
                "self": "Internal state, memory, soul",
                "world": "Agents, infrastructure, resources",
                "concept": "Laws, principles, dialectics",
                "void": "Entropy, shadow, Accursed Share",
                "time": "Traces, forecasts, schedules",
            }
            for match in result.matches:
                ctx = match.path.split(".")[0] if "." in match.path else match.path
                desc = context_descs.get(ctx, "")
                lines.append(f"  \033[36m{ctx:<10}\033[0m  {desc}")
        else:
            # Show child paths
            for match in result.matches:
                # Strip current path prefix for cleaner display
                child = match.path[len(current) + 1 :] if current else match.path
                if match.affordances:
                    affs = ", ".join(match.affordances[:3])
                    lines.append(f"  \033[33m{child}\033[0m  ({affs})")
                else:
                    lines.append(f"  \033[33m{child}\033[0m")

        if result.has_more:
            lines.append(f"  \033[90m... and {result.total_count - len(result)} more\033[0m")

        return "\n".join(lines)

    except (ImportError, Exception):
        return None  # Fall back to static


def _show_static_affordances(state: ReplState) -> str:
    """Show static affordances (fallback when query unavailable)."""
    lines = ["\033[1mAffordances:\033[0m"]

    if not state.path:
        # At root - show contexts
        lines.append("")
        for ctx in sorted(CONTEXTS):
            desc = {
                "self": "Internal state, memory, soul",
                "world": "Agents, infrastructure, resources",
                "concept": "Laws, principles, dialectics",
                "void": "Entropy, shadow, Accursed Share",
                "time": "Traces, forecasts, schedules",
            }.get(ctx, "")
            lines.append(f"  \033[36m{ctx:<10}\033[0m  {desc}")

    elif len(state.path) == 1:
        # In a context - show holons
        context = state.path[0]
        holons = CONTEXT_HOLONS.get(context, [])
        lines.append("")
        for holon in holons:
            lines.append(f"  \033[33m{holon}\033[0m")
        lines.append("")
        lines.append("\033[90mUse '<holon>' to navigate or '<holon> <aspect>' to invoke\033[0m")

    else:
        # In a holon - show aspects
        lines.append("")
        aspects = ["manifest", "witness", "affordances", "help", "refine"]
        for aspect in aspects:
            lines.append(f"  \033[33m{aspect}\033[0m")
        lines.append("")
        lines.append("\033[90mUse '<aspect>' to invoke\033[0m")

    return "\n".join(lines)


def _show_detailed_help(state: ReplState) -> str:
    """Show detailed help for current location.

    v3: When at a specific path, invokes the `help` aspect via Logos.
    Falls back to static help when Logos unavailable.
    """
    if not state.path:
        return HELP_TEXT

    # v3: Try to invoke help aspect via Logos
    logos = state.get_logos()
    observer = state.get_umwelt()
    if logos is not None and observer is not None and len(state.path) >= 2:
        # At a holon or deeper - try help aspect
        help_result = _invoke_help_aspect(state, logos, observer)
        if help_result is not None:
            return help_result

    # Fallback: static context help
    return _show_static_detailed_help(state)


def _invoke_help_aspect(state: ReplState, logos: Any, observer: Any) -> str | None:
    """Invoke the help aspect via Logos."""
    try:
        import asyncio

        path = state.current_path
        if not path:
            return None

        # Invoke help aspect
        full_path = f"{path}.help"
        result = asyncio.run(logos.invoke(full_path, observer))

        if result:
            return str(result)
        return None

    except (ImportError, Exception):
        return None  # Fall back to static


def _show_static_detailed_help(state: ReplState) -> str:
    """Show static detailed help (fallback when Logos unavailable)."""
    context = state.path[0]

    context_help = {
        "self": """\
\033[1mself.*\033[0m - The Internal

The self context handles all internal agent operations:
  status       System health at a glance
  memory       Four Pillars memory health
  dream        LucidDreamer morning briefing
  soul         K-gent soul dialogue
  dashboard    Real-time TUI dashboard
  capabilities What can I do? (affordances)

\033[90mPrinciple: Ethical (boundaries of agency)\033[0m
""",
        "world": """\
\033[1mworld.*\033[0m - The External

The world context handles all external operations:
  agents       Agent operations (list, run, inspect)
  daemon       Cortex daemon lifecycle
  infra        K8s infrastructure operations
  fixture      HotData fixtures
  exec         Q-gent execution
  dev          Live reload development mode
  town         Agent Town civilizational simulation

\033[90mPrinciple: Heterarchical (resources in flux)\033[0m
""",
        "concept": """\
\033[1mconcept.*\033[0m - The Abstract

The concept context handles abstract operations:
  laws         Category laws (identity, associativity)
  dialectic    Challenge and refine concepts
  principle    Design principles
  operad       Composition grammar

\033[90mPrinciple: Generative (compressed wisdom)\033[0m
""",
        "void": """\
\033[1mvoid.*\033[0m - The Accursed Share

The void context handles entropy operations:
  entropy      Draw/return randomness
  shadow       Jungian shadow analysis
  serendipity  Request tangents
  gratitude    Express thanks (tithe)
  archetype    Archetypal patterns

\033[90mMeta-Principle: Everything is slop or comes from slop\033[0m
""",
        "time": """\
\033[1mtime.*\033[0m - The Temporal

The time context handles temporal operations:
  trace        View temporal traces
  past         View past state
  future       Forecast (probabilistic)
  schedule     Schedule future actions
  turn         Turn management

\033[90mPrinciple: Heterarchical (temporal composition)\033[0m
""",
    }

    return context_help.get(context, f"No detailed help for {context}")


def _stream_result(async_iter: Any, state: ReplState) -> str:
    """
    Stream tokens to stdout in real-time.

    Consumes an async iterator from a streaming AGENTESE path
    (e.g., self.chat.stream) and prints tokens as they arrive.

    Args:
        async_iter: Async iterator yielding tokens (dict or str)
        state: REPL state for context

    Returns:
        Full accumulated response as string
    """
    import sys

    async def _consume() -> str:
        full_response = ""
        async for chunk in async_iter:
            if isinstance(chunk, dict):
                # ChatNode.stream returns dicts with 'content' key
                content = chunk.get("content", "")
                if content:
                    sys.stdout.write(content)
                    sys.stdout.flush()
                    full_response += content
            else:
                # Plain string tokens
                token = str(chunk)
                sys.stdout.write(token)
                sys.stdout.flush()
                full_response += token
        return full_response

    result = asyncio.run(_consume())
    print()  # Newline after streaming
    return result


def handle_invocation(state: ReplState, parts: list[str]) -> str:
    """
    Handle path invocation.

    Phase 3 (CLI v7): Updates K-gent presence during invocation.
    Wave 3: Adds fuzzy matching for typo correction.
    Wave 2: Tries async Logos first, falls back to CLI routing.
    """
    # Handle empty input
    if not parts:
        return _error_with_sympathy(
            "No path specified",
            suggestion="Navigate to a context first: self, world, concept, void, time",
        )

    # Phase 3 (CLI v7): Update K-gent cursor to "working" state
    state.update_presence("working", ".".join(parts), "Processing...")

    # Wave 3: Try fuzzy correction for context typos
    first_part = parts[0].lower()
    if first_part not in CONTEXTS and state.path == []:
        fuzzy = state.get_fuzzy()
        if fuzzy is not None:
            corrected = fuzzy.suggest(first_part, list(CONTEXTS))
            if corrected:
                # Auto-correct and notify user
                parts = [corrected] + parts[1:]
                print(f"\033[90m(corrected: {first_part} → {corrected})\033[0m")

    # Build full path
    if parts[0] in CONTEXTS:
        full_path = parts
    else:
        full_path = state.path + parts

    if not full_path:
        return _error_with_sympathy(
            "No path specified",
            suggestion="Navigate to a context first: self, world, concept, void, time",
        )

    # Convert to dotted path for Logos
    path_str = ".".join(full_path)

    # First, try Logos (Wave 2: async execution)
    logos = state.get_logos()
    umwelt = state.get_umwelt()

    def _complete_invocation(output: str) -> str:
        """Wrapper to reset presence to waiting after invocation."""
        state.update_presence("waiting", None, "Ready")
        return output

    if logos is not None and umwelt is not None:
        # Check if path has an aspect (3+ parts) or needs .manifest
        if len(full_path) >= 3:
            # Has explicit aspect
            try:
                result = asyncio.run(logos.invoke(path_str, umwelt))
                # Handle streaming results (e.g., self.chat.stream)
                if hasattr(result, "__aiter__"):
                    output = _stream_result(result, state)
                    state.last_result = output
                    return _complete_invocation(output)
                state.last_result = result
                return _complete_invocation(_render_result(result, state))
            except Exception:
                # Fall back to CLI on any Logos error
                pass
        elif len(full_path) == 2:
            # Holon without aspect - try .manifest
            try:
                result = asyncio.run(logos.invoke(f"{path_str}.manifest", umwelt))
                # Handle streaming results (unlikely for .manifest but be consistent)
                if hasattr(result, "__aiter__"):
                    output = _stream_result(result, state)
                    state.last_result = output
                    return _complete_invocation(output)
                state.last_result = result
                return _complete_invocation(_render_result(result, state))
            except Exception:
                # Fall back to CLI
                pass

    # Fall back to CLI routing
    try:
        result = _invoke_path(full_path)
        state.last_result = result
        return _complete_invocation(result)
    except Exception as e:
        return _complete_invocation(
            _error_with_sympathy(
                str(e),
                suggestion=_suggest_for_path(full_path, state),
            )
        )


def _suggest_for_path(path: list[str], state: ReplState | None = None) -> str | None:
    """
    Generate a helpful suggestion for a failed path.

    Wave 3 Enhancement: Uses fuzzy matching for typo correction.
    """
    if not path:
        return "Try: self, world, concept, void, time"

    context = path[0]
    if context not in CONTEXTS:
        # Wave 3: Try fuzzy matching for context typos
        if state is not None:
            fuzzy = state.get_fuzzy()
            if fuzzy is not None:
                ctx_suggestion: str | None = fuzzy.did_you_mean(context, list(CONTEXTS))
                if ctx_suggestion:
                    return ctx_suggestion

        return f"'{context}' is not a valid context. Try: self, world, concept, void, time"

    if len(path) == 1:
        holons = CONTEXT_HOLONS.get(context, [])
        if holons:
            return f"Available in {context}: {', '.join(holons[:5])}"

    if len(path) >= 2:
        # Wave 3: Try fuzzy matching for holon typos
        if state is not None and len(path) >= 2:
            fuzzy = state.get_fuzzy()
            holons = CONTEXT_HOLONS.get(context, [])
            if fuzzy is not None and holons:
                suggestion: str | None = fuzzy.did_you_mean(path[1], holons)
                if suggestion:
                    return suggestion

        return f"Use ? to see affordances at {'.'.join(path[:2])}"

    return None


# =============================================================================
# Error Sympathy & Rich Rendering (Wave 2)
# =============================================================================


def _error_with_sympathy(message: str, suggestion: str | None = None) -> str:
    """
    Format an error message with sympathy (helpful suggestions).

    Principle: Errors should guide, not just fail.
    """
    lines = [f"\033[31mError:\033[0m {message}"]
    if suggestion:
        lines.append(f"\033[33mTry:\033[0m {suggestion}")
    return "\n".join(lines)


def _render_result(result: Any, state: ReplState) -> str:
    """
    Render a result with rich formatting if available.

    Adapts rendering to the type of result:
    - BasicRendering -> Panel with summary/content
    - dict -> Table
    - list -> Numbered list or table
    - str -> Direct output
    - Other -> repr
    """
    console = get_console()

    # Handle BasicRendering from Logos
    if hasattr(result, "summary") and hasattr(result, "content"):
        if RICH_AVAILABLE and console:
            panel = Panel(
                result.content or "(no content)",
                title=result.summary,
                border_style="cyan",
            )
            # Capture to string
            import io as string_io

            from rich.console import Console as RichConsole

            buffer = string_io.StringIO()
            str_console = RichConsole(file=buffer, force_terminal=True)
            str_console.print(panel)
            return buffer.getvalue().rstrip()
        else:
            return f"\033[1m{result.summary}\033[0m\n{result.content or '(no content)'}"

    # Handle dicts
    if isinstance(result, dict):
        if RICH_AVAILABLE and console:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Key", style="yellow")
            table.add_column("Value")
            for k, v in result.items():
                table.add_row(str(k), str(v))
            import io as string_io

            from rich.console import Console as RichConsole

            buffer = string_io.StringIO()
            str_console = RichConsole(file=buffer, force_terminal=True)
            str_console.print(table)
            return buffer.getvalue().rstrip()
        else:
            lines = []
            for k, v in result.items():
                lines.append(f"  \033[33m{k}:\033[0m {v}")
            return "\n".join(lines)

    # Handle lists
    if isinstance(result, list):
        if len(result) == 0:
            return "\033[90m(empty list)\033[0m"

        if RICH_AVAILABLE and console and len(result) <= 20:
            # For short lists, use a table
            if result and isinstance(result[0], dict):
                # List of dicts -> table with columns
                keys = list(result[0].keys())
                table = Table(show_header=True, header_style="bold cyan")
                for key in keys[:5]:  # Limit columns
                    table.add_column(str(key))
                for item in result[:20]:  # Limit rows
                    table.add_row(*[str(item.get(k, "")) for k in keys[:5]])
                import io as string_io

                from rich.console import Console as RichConsole

                buffer = string_io.StringIO()
                str_console = RichConsole(file=buffer, force_terminal=True)
                str_console.print(table)
                return buffer.getvalue().rstrip()

        # Fall back to numbered list
        lines = []
        for i, item in enumerate(result[:20], 1):
            lines.append(f"  {i:3}. {item}")
        if len(result) > 20:
            lines.append(f"  ... and {len(result) - 20} more")
        return "\n".join(lines)

    # Handle strings
    if isinstance(result, str):
        return result

    # Handle None
    if result is None:
        return "\033[90m(ok)\033[0m"

    # Fallback: repr
    return repr(result)


def _invoke_path(path: list[str]) -> str:
    """
    Invoke an AGENTESE path through the CLI routing.

    Maps paths to actual CLI commands.
    """
    if not path:
        return "\033[90m(no path)\033[0m"

    context = path[0]
    rest = path[1:]

    # Route through existing CLI infrastructure
    try:
        if context == "self":
            # Capture output
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.self_ import cmd_self

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_self(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "world":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.world import cmd_world

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_world(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "concept":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.concept import cmd_concept

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_concept(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "void":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.void import cmd_void

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_void(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "time":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.time_ import cmd_time

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_time(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        else:
            return f"\033[31mUnknown context: {context}\033[0m"

    except ImportError as e:
        return f"\033[33mContext not implemented:\033[0m {e}"
    except Exception as e:
        return f"\033[31mInvocation error:\033[0m {e}"


def handle_composition(state: ReplState, line: str) -> str:
    """
    Handle >> composition operator.

    Wave 2: Actually executes the pipeline through Logos!

    Example: world.agents.list >> concept.count
    """
    parts = [p.strip() for p in line.split(">>")]

    if len(parts) < 2:
        return _error_with_sympathy(
            "Composition requires at least two paths",
            suggestion="Try: self.status >> time.trace",
        )

    # Build full paths by prepending current context if needed
    full_paths = []
    for part in parts:
        if part.split(".")[0] in CONTEXTS or part.split()[0] in CONTEXTS:
            full_paths.append(part)
        else:
            # Prepend current path
            if state.path:
                full_paths.append(f"{state.current_path}.{part}")
            else:
                full_paths.append(part)

    # Try to execute through Logos
    logos = state.get_logos()
    umwelt = state.get_umwelt()

    if logos is not None and umwelt is not None:
        try:
            # Execute pipeline
            composed = logos.compose(*full_paths)
            result = asyncio.run(composed.invoke(umwelt))

            # Render result
            return _render_result(result, state)
        except Exception as e:
            # Fall back to CLI execution with sympathy
            return _execute_pipeline_cli(state, full_paths, e)
    else:
        # No Logos available, use CLI fallback
        return _execute_pipeline_cli(state, full_paths, None)


def _execute_pipeline_cli(state: ReplState, paths: list[str], logos_error: Exception | None) -> str:
    """Execute pipeline via CLI routing (fallback when Logos unavailable)."""
    lines = []

    if logos_error:
        lines.append(f"\033[33mLogos unavailable:\033[0m {logos_error}")
        lines.append("\033[90mFalling back to CLI routing...\033[0m")
        lines.append("")

    # Execute each path sequentially
    current_input = None
    for i, path in enumerate(paths):
        lines.append(f"\033[90m[{i + 1}/{len(paths)}]\033[0m \033[36m{path}\033[0m")

        # Parse and execute through CLI
        parts = path.replace(".", " ").split()
        result = _invoke_path(parts)
        lines.append(result)

        if i < len(paths) - 1:
            lines.append("")  # Separator between steps
            # Pass result forward (for future use when CLI supports it)
            current_input = result

    state.last_result = current_input
    return "\n".join(lines)


def handle_history_search(state: ReplState, line: str) -> str:
    """
    Handle /history command for searching command history.

    Wave 3 Intelligence: Fuzzy search through command history.

    Commands:
        /history           - Show recent history
        /history <query>   - Search history for query
    """
    parts = line.strip().split(maxsplit=1)
    query = parts[1] if len(parts) > 1 else ""

    if not state.history:
        return "\033[90m(no history yet)\033[0m"

    if not query:
        # Show last 10 commands
        lines = ["\033[1mRecent history:\033[0m", ""]
        for i, cmd in enumerate(state.history[-10:], 1):
            lines.append(f"  {i:3}  {cmd}")
        return "\n".join(lines)

    # Wave 3: Fuzzy search if available
    fuzzy = state.get_fuzzy()
    if fuzzy is not None:
        matches = fuzzy.match(query, state.history)
        if matches:
            lines = [f"\033[1mHistory matching '{query}':\033[0m", ""]
            for cmd, score in matches[:10]:
                # Highlight the match
                highlighted = cmd.replace(query, f"\033[33m{query}\033[0m")
                lines.append(f"  \033[90m({score}%)\033[0m {highlighted}")
            return "\n".join(lines)
    else:
        # Simple substring search
        matching = [h for h in state.history if query.lower() in h.lower()]
        if matching:
            lines = [f"\033[1mHistory containing '{query}':\033[0m", ""]
            for cmd in matching[-10:]:
                highlighted = cmd.replace(query, f"\033[33m{query}\033[0m")
                lines.append(f"  {highlighted}")
            return "\n".join(lines)

    return f"\033[90mNo history matching '{query}'\033[0m"


def handle_memory_command(state: ReplState, line: str) -> str:
    """
    Handle /memory command for viewing ConversationWindow state.

    Phase 4 (CLI v7): Deep Conversation

    Commands:
        /memory           - Show window status and recent turns
        /memory status    - Show window utilization
        /memory toggle    - Toggle window indicator in prompt
        /memory clear     - Clear conversation memory
    """
    parts = line.strip().split()
    subcommand = parts[1].lower() if len(parts) > 1 else ""

    window = state.get_window()

    if window is None:
        return "\033[90m(ConversationWindow not available)\033[0m"

    if subcommand == "status":
        # Show detailed window status
        lines = [
            "\033[1mConversation Memory:\033[0m",
            "",
            f"  Turns:       {window.turn_count} / {window.max_turns}",
            f"  Strategy:    {window.strategy}",
            f"  Utilization: {window.utilization:.1%}",
            f"  Has Summary: {window.has_summary}",
        ]
        return "\n".join(lines)

    if subcommand == "toggle":
        # Toggle window indicator in prompt
        state.show_window_utilization = not state.show_window_utilization
        status = "enabled" if state.show_window_utilization else "disabled"
        return f"\033[90mWindow indicator in prompt: {status}\033[0m"

    if subcommand == "clear":
        # Clear the window
        window.reset()
        return "\033[90mConversation memory cleared.\033[0m"

    # Default: show recent turns summary
    if window.turn_count == 0:
        return "\033[90m(no conversation memory yet)\033[0m"

    lines = [
        "\033[1mConversation Memory:\033[0m",
        f"\033[90m{window.turn_count} turns recorded, {window.utilization:.0%} capacity\033[0m",
        "",
    ]

    # Show last few turns (truncated)
    messages = window.get_context_messages()
    recent = messages[-6:]  # Last 3 exchanges
    for msg in recent:
        role = msg.role
        content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        if role == "user":
            lines.append(f"  \033[33m»\033[0m {content}")
        else:
            lines.append(f"  \033[36m←\033[0m {content}")

    lines.append("")
    lines.append("\033[90mCommands: /memory status, /memory toggle, /memory clear\033[0m")
    return "\n".join(lines)


def handle_presence_command(state: ReplState, line: str) -> str:
    """
    Handle /presence command for viewing agent cursor state.

    Phase 3 (CLI v7): Agent Cursors

    Commands:
        /presence           - Show all active cursors
        /presence toggle    - Toggle presence display
        /presence kgent     - Show K-gent cursor state
    """
    parts = line.strip().split()
    subcommand = parts[1].lower() if len(parts) > 1 else ""

    cursor = state.get_kgent_cursor()

    if cursor is None:
        return "\033[90m(Agent presence not available)\033[0m"

    if subcommand == "toggle":
        state.show_presence = not state.show_presence
        status = "enabled" if state.show_presence else "disabled"
        return f"\033[90mAgent presence display: {status}\033[0m"

    if subcommand == "kgent":
        # Show K-gent cursor details
        lines = [
            "\033[1mK-gent Cursor:\033[0m",
            "",
            f"  State:       {cursor.state.value}",
            f"  Behavior:    {cursor.behavior.value}",
            f"  Focus:       {cursor.focus_path or '(none)'}",
            f"  Activity:    {cursor.activity or '(idle)'}",
            f"  Last Update: {cursor.last_updated.strftime('%H:%M:%S')}",
        ]
        return "\n".join(lines)

    # Default: show current presence status
    status_text = cursor.format_status_text()
    lines = [
        "\033[1mAgent Presence:\033[0m",
        f"  \033[90m│\033[0m {status_text}",
        "",
        "\033[90mCommands: /presence toggle, /presence kgent\033[0m",
    ]
    return "\n".join(lines)


def handle_observer_command(state: ReplState, line: str) -> str:
    """
    Handle /observer commands for switching observer context.

    Commands:
        /observer            - Show current observer
        /observer <arch>     - Switch to archetype
        /observers           - List all archetypes
    """
    parts = line.strip().split()
    cmd = parts[0].lower()

    if cmd == "/observers":
        # List all archetypes
        lines = ["\033[1mObserver Archetypes:\033[0m", ""]
        for arch, desc in OBSERVER_ARCHETYPES.items():
            marker = " \033[32m←\033[0m" if arch == state.observer else ""
            lines.append(f"  \033[33m{arch:<12}\033[0m {desc}{marker}")
        return "\n".join(lines)

    if cmd == "/observer":
        if len(parts) == 1:
            # Show current
            desc = OBSERVER_ARCHETYPES.get(state.observer, "Unknown")
            return f"\033[1mCurrent observer:\033[0m \033[33m{state.observer}\033[0m\n{desc}"

        # Switch to new archetype
        new_arch = parts[1].lower()
        if new_arch not in OBSERVER_ARCHETYPES:
            return _error_with_sympathy(
                f"Unknown archetype: {new_arch}",
                suggestion=f"Available: {', '.join(OBSERVER_ARCHETYPES.keys())}",
            )

        old_arch = state.observer
        state.observer = new_arch
        # Invalidate umwelt cache so it gets recreated with new archetype
        state._umwelt = None

        # Show what changed
        return (
            f"\033[90mObserver changed:\033[0m {old_arch} → \033[33m{new_arch}\033[0m\n"
            f"\033[90m{OBSERVER_ARCHETYPES[new_arch]}\033[0m"
        )

    return _error_with_sympathy(
        f"Unknown command: {cmd}",
        suggestion="Try: /observer, /observer developer, /observers",
    )


# =============================================================================
# v3: Alias Management
# =============================================================================


# Global alias registry (lazy-initialized)
_alias_registry: Any | None = None


def get_alias_registry() -> Any:
    """Get or create the global alias registry."""
    global _alias_registry
    if _alias_registry is None:
        try:
            from protocols.agentese import (
                create_alias_registry,
                get_default_aliases_path,
            )

            _alias_registry = create_alias_registry(
                persistence_path=get_default_aliases_path(),
                include_standard=True,
                load_from_disk=True,
            )
        except ImportError:
            # Stub registry if agentese not available
            _alias_registry = {"_stub": True}
    return _alias_registry


def handle_alias_command(state: ReplState, line: str) -> str:
    """
    Handle alias management commands.

    Commands:
        /alias                 - List all aliases
        /aliases               - List all aliases (synonym)
        /alias <name> <path>   - Create alias
        /unalias <name>        - Remove alias
    """
    parts = line.strip().split()
    cmd = parts[0].lower()

    registry = get_alias_registry()

    # Check if registry is just a stub
    if isinstance(registry, dict) and registry.get("_stub"):
        return "\033[31mAlias system not available\033[0m (agentese module not found)"

    try:
        from protocols.agentese import (
            AliasError,
            AliasNotFoundError,
            AliasShadowError,
        )
    except ImportError:
        return "\033[31mAlias system not available\033[0m"

    if cmd in ("/alias", "/aliases"):
        if len(parts) == 1:
            # List all aliases
            aliases = registry.list_aliases()
            if not aliases:
                return "\033[90mNo aliases defined.\033[0m\nUse: /alias <name> <path>"

            lines = ["\033[1mAliases:\033[0m", ""]

            # Show standard aliases
            from protocols.agentese import create_standard_aliases

            standard = create_standard_aliases()
            custom = {k: v for k, v in aliases.items() if k not in standard}
            builtin = {k: v for k, v in aliases.items() if k in standard}

            if builtin:
                lines.append("  \033[90mStandard:\033[0m")
                for name, target in sorted(builtin.items()):
                    lines.append(f"    \033[33m{name:<15}\033[0m → {target}")

            if custom:
                if builtin:
                    lines.append("")
                lines.append("  \033[90mUser-defined:\033[0m")
                for name, target in sorted(custom.items()):
                    lines.append(f"    \033[33m{name:<15}\033[0m → {target}")

            lines.append("")
            lines.append("\033[90mUsage: /alias <name> <path> or /unalias <name>\033[0m")
            return "\n".join(lines)

        if len(parts) == 2:
            # Show specific alias
            name = parts[1]
            target = registry.get(name)
            if target:
                return f"\033[33m{name}\033[0m → {target}"
            return f"\033[90mAlias '{name}' not found\033[0m"

        if len(parts) >= 3:
            # Create alias: /alias name path
            name = parts[1]
            target = parts[2]

            try:
                registry.register(name, target)
                registry.save()
                return f"\033[32mAlias created:\033[0m {name} → {target}"
            except AliasShadowError as e:
                return f"\033[31mError:\033[0m {e}"
            except AliasError as e:
                return f"\033[31mError:\033[0m {e}"

    if cmd == "/unalias":
        if len(parts) < 2:
            return "\033[90mUsage:\033[0m /unalias <name>"

        name = parts[1]

        try:
            registry.unregister(name)
            registry.save()
            return f"\033[32mAlias removed:\033[0m {name}"
        except AliasNotFoundError:
            return f"\033[31mAlias not found:\033[0m {name}"
        except AliasError as e:
            return f"\033[31mError:\033[0m {e}"

    return _error_with_sympathy(
        f"Unknown alias command: {cmd}",
        suggestion="Try: /alias, /aliases, /alias me self.soul, /unalias me",
    )


# =============================================================================
# Wave 4: Joy-Inducing Functions
# =============================================================================


def handle_slash_shortcut(state: ReplState, line: str) -> str | None:
    """
    Handle /shortcut commands for Wave 4 joy-inducing commands.

    Directly invokes handlers for slash shortcuts.

    Returns:
        Result string or None if not a shortcut
    """
    import io
    import sys

    parts = line.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd not in SLASH_SHORTCUTS:
        return None

    # Parse args
    args = parts[1].split() if len(parts) > 1 else []

    # Direct handler mapping
    try:
        if cmd in ("/oblique",):
            from protocols.cli.handlers.oblique import cmd_oblique

            handler = cmd_oblique
        elif cmd in ("/constrain",):
            from protocols.cli.handlers.constrain import cmd_constrain

            handler = cmd_constrain
        elif cmd in ("/yes-and", "/expand"):
            from protocols.cli.handlers.yes_and import cmd_yes_and

            handler = cmd_yes_and
        elif cmd in ("/surprise", "/surprise-me"):
            from protocols.cli.handlers.surprise_me import cmd_surprise_me

            handler = cmd_surprise_me
        elif cmd in ("/project",):
            from protocols.cli.handlers.project import cmd_project

            handler = cmd_project
        elif cmd in ("/sparkline",):
            from protocols.cli.handlers.sparkline import cmd_sparkline

            handler = cmd_sparkline
        elif cmd in ("/why",):
            from protocols.cli.handlers.why import cmd_why

            handler = cmd_why
        elif cmd in ("/tension",):
            from protocols.cli.handlers.tension import cmd_tension

            handler = cmd_tension
        elif cmd in ("/challenge",):
            from protocols.cli.handlers.challenge import cmd_challenge

            handler = cmd_challenge
        elif cmd in (
            "/nphase",
            "/nphase-validate",
            "/nphase-template",
            "/nphase-bootstrap",
        ):
            from protocols.cli.handlers.nphase import cmd_nphase

            def _build_nphase_args(base_cmd: str, extra_args: list[str]) -> list[str]:
                """Construct args for nphase CLI wrapper."""
                cli_args = []
                if base_cmd == "/nphase-validate":
                    cli_args.append("validate")
                elif base_cmd == "/nphase-template":
                    cli_args.append("template")
                elif base_cmd == "/nphase-bootstrap":
                    cli_args.append("bootstrap")

                # Default /nphase to compile if the user passed a path directly
                if base_cmd == "/nphase" and extra_args:
                    if extra_args[0] not in {
                        "compile",
                        "validate",
                        "bootstrap",
                        "template",
                    }:
                        cli_args.append("compile")

                cli_args.extend(extra_args)
                return cli_args

            cli_args = _build_nphase_args(cmd, args)

            def nphase_handler(args: list[str], ctx: InvocationContext | None = None) -> int:
                """Thin wrapper to match handler signature used below."""
                del args, ctx  # Unused, using cli_args from closure
                return cmd_nphase(cli_args)

            handler = nphase_handler
        else:
            return None

        # Capture stdout to return as string
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()

        try:
            handler(args, None)
            return captured.getvalue().rstrip()
        finally:
            sys.stdout = old_stdout

    except Exception as e:
        return f"\033[31mError:\033[0m {e}"


def _get_hour() -> int:
    """Get current hour (0-23). Separated for testing."""
    return datetime.now().hour


def get_welcome_message(state: ReplState) -> str:
    """
    Generate a context-aware welcome message.

    J1: Varies by:
    - Time of day (morning/afternoon/evening)
    - Session restoration status (returning user)

    Args:
        state: Current REPL state

    Returns:
        A personalized welcome message
    """
    # Returning user takes priority
    if state.restored_session and state.path:
        context = ".".join(state.path)
        template = random.choice(WELCOME_VARIANTS["returning"])
        return template.format(context=context)

    # Time-based welcome
    hour = _get_hour()
    if 5 <= hour < 12:
        return random.choice(WELCOME_VARIANTS["morning"])
    elif 12 <= hour < 18:
        return random.choice(WELCOME_VARIANTS["afternoon"])
    else:
        return random.choice(WELCOME_VARIANTS["evening"])


async def maybe_invoke_kgent(cmd: str, state: ReplState) -> str | None:
    """
    Route philosophical queries to K-gent soul.

    J2: Checks for trigger words and invokes K-gent with rate limiting.

    Args:
        cmd: The user's command
        state: Current REPL state

    Returns:
        K-gent response (purple colored) or None if not triggered
    """
    # Check for trigger words
    cmd_lower = cmd.lower()
    if not any(trigger in cmd_lower for trigger in KGENT_TRIGGERS):
        return None

    # Rate limiting
    now = datetime.now()
    if state.last_kgent_time is not None:
        elapsed = (now - state.last_kgent_time).total_seconds()
        if elapsed < KGENT_RATE_LIMIT_SECONDS:
            return None  # Rate limited, silently skip

    # Try to invoke K-gent
    try:
        from agents.k.soul import BudgetTier, KgentSoul

        soul = KgentSoul(auto_llm=True)
        if not soul.has_llm:
            # No LLM available, use template
            return None

        response = await soul.dialogue(
            cmd,
            budget=BudgetTier.WHISPER,  # Conservative budget
        )

        # Update rate limit tracker
        state.last_kgent_time = now

        # Return in purple (K-gent's color)
        return f"\033[35m{response.response}\033[0m"

    except ImportError:
        return None
    except Exception:
        return None


def handle_easter_egg(path: str, state: ReplState) -> str | None:
    """
    Handle easter egg commands.

    J3: Hidden delights discovered naturally by curious users.

    Args:
        path: The command path to check
        state: Current REPL state

    Returns:
        Easter egg output or None if not an easter egg
    """
    # Normalize path
    normalized = path.replace(" ", ".").lower()

    # Check for excessive dots
    if normalized.count(".") >= 9 or normalized == "..........":
        return _easter_too_far()

    # Check known easter eggs
    handler_name = EASTER_EGGS.get(normalized)
    if handler_name is None:
        return None

    # Dispatch to handler
    handlers = {
        "_easter_entropy_dance": _easter_entropy_dance,
        "_easter_soul_sing": _easter_soul_sing,
        "_easter_concept_zen": _easter_concept_zen,
        "_easter_time_flow": _easter_time_flow,
        "_easter_world_hello": _easter_world_hello,
        "_easter_too_far": _easter_too_far,
    }

    handler = handlers.get(handler_name)
    if handler:
        return handler()
    return None


def _easter_entropy_dance() -> str:
    """ASCII animation of spinning entropy gauge."""
    frames = [
        "  ◐  \n░▒█▒░\n  ◓  ",
        "  ◑  \n░▓█▓░\n  ◒  ",
        "  ◒  \n░█▓█░\n  ◐  ",
        "  ◓  \n▒█░█▒\n  ◑  ",
    ]
    # Return a random frame with some flair
    frame = random.choice(frames)
    return f"\033[36m{frame}\033[0m\n\n\033[90mEntropy dances. The void watches.\033[0m"


def _easter_soul_sing() -> str:
    """Generate a haiku about the current moment."""
    haikus = [
        "Agents compose paths\nMorphisms flow through the forest\nThe void exhales slop",
        "Dawn breaks on the code\nFunctors lift the weary soul\nComposition wins",
        "Entropy whispers\nGratitude returns to void\nThe river flows on",
        "Handles yield insight\nObservers become observed\nNo view from nowhere",
    ]
    haiku = random.choice(haikus)
    return f"\033[35m{haiku}\033[0m"


def _easter_concept_zen() -> str:
    """Return a random principle from spec/principles.md."""
    principle = random.choice(ZEN_PRINCIPLES)
    return f"\033[33m✧ {principle}\033[0m"


def _easter_time_flow() -> str:
    """Animated time visualization."""
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    # Time bar
    progress = (hour * 60 + minute) / (24 * 60)
    bar_width = 20
    filled = int(progress * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)

    return (
        f"\033[33m╭─ time.flow ─╮\033[0m\n"
        f"\033[33m│\033[0m {bar} \033[33m│\033[0m\n"
        f"\033[33m│\033[0m   {hour:02d}:{minute:02d}       \033[33m│\033[0m\n"
        f"\033[33m╰─────────────╯\033[0m\n"
        f"\033[90mThe river flows. Time is just a handle.\033[0m"
    )


def _easter_world_hello() -> str:
    """The classic."""
    return "\033[32mHello, World!\033[0m\n\n\033[90m(Some traditions are worth keeping.)\033[0m"


def _easter_too_far() -> str:
    """You've gone too far."""
    return "\033[31m⚠\033[0m You've gone too far.\n\033[90mHere there be dragons.\033[0m\n\n    🐉"


def get_contextual_hint(state: ReplState) -> str | None:
    """
    Generate proactive hints based on user behavior.

    J5: Contextual hints guide stuck users.

    Args:
        state: Current REPL state

    Returns:
        A hint string or None if no hint needed
    """
    # Hint for repeated errors
    if state.consecutive_errors >= 3:
        return "\033[33mHint:\033[0m Try '?' to see available affordances"

    # Hint for long session at root
    if len(state.history) > 20 and not state.path:
        return "\033[33mHint:\033[0m Try 'self status' for a system overview"

    # Hint in void context
    if state.path == ["void"]:
        return "\033[33mHint:\033[0m 'entropy sip' draws from the Accursed Share"

    # No hint needed
    return None


# =============================================================================
# Wave 5: Ambient Mode Functions
# =============================================================================


def _get_key_nonblocking() -> str | None:
    """
    Get a single keypress without blocking.

    Returns None if no key pressed, or the key character.
    Only works on Unix-like systems (uses select + termios).
    On Windows, returns None (ambient mode keybindings not supported).

    Wave 5: Non-blocking keyboard for ambient mode.
    """
    try:
        import select

        # Check if stdin has data ready
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None
    except Exception:
        # On Windows or if stdin not available, return None
        return None


def _handle_ambient_key(key: str, state: ReplState) -> bool:
    """
    Handle a keypress in ambient mode.

    Args:
        key: The pressed key
        state: Current REPL state

    Returns:
        True if a refresh should be triggered, False otherwise.

    Wave 5: Keybindings for ambient mode.
    """
    if key == "q":
        # Quit
        state.running = False
        return False

    elif key == "r":
        # Force refresh
        return True

    elif key == " ":
        # Toggle pause
        state.ambient_paused = not state.ambient_paused
        return True  # Refresh to show pause indicator

    elif key in "12345":
        # Focus panel
        state.ambient_focus = int(key)
        return True  # Refresh to show focus

    elif key == "0":
        # Clear focus (show all panels)
        state.ambient_focus = None
        return True

    return False


def _render_ambient_screen(metrics: Any, paused: bool, focus: int | None = None) -> str:
    """
    Render the ambient mode display.

    Args:
        metrics: DashboardMetrics from collectors
        paused: Whether refresh is paused
        focus: Focused panel number (1-5) or None for all

    Returns:
        The rendered screen as a string.

    Wave 5: Passive dashboard rendering.
    """
    lines = []

    # Header
    pause_indicator = " \033[33m[PAUSED]\033[0m" if paused else ""
    lines.append(f"\033[36m╭─── kgents ambient{pause_indicator} ───╮\033[0m")
    lines.append("\033[36m│\033[0m [q]uit [r]efresh [space]pause [1-5]focus  \033[36m│\033[0m")
    lines.append("\033[36m├───────────────────────────────────────────╯\033[0m")
    lines.append("")

    # K-gent Panel (1)
    if focus is None or focus == 1:
        lines.append("\033[32m K-GENT SOUL \033[0m")
        if metrics.kgent.is_online:
            lines.append(f"  Mode: {metrics.kgent.mode.upper()}")
            lines.append(
                f"  Garden: {metrics.kgent.garden_patterns} patterns "
                f"({metrics.kgent.garden_trees} trees)"
            )
            lines.append(f"  Dream: {metrics.kgent.dream_age_str}")
        else:
            lines.append("  \033[90m[offline]\033[0m")
        lines.append("")

    # Metabolism Panel (2)
    if focus is None or focus == 2:
        lines.append("\033[33m METABOLISM \033[0m")
        if metrics.metabolism.is_online:
            pct = int(metrics.metabolism.pressure * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            lines.append(f"  Pressure: {bar} {pct}%")
            lines.append(f"  Status: {metrics.metabolism.status_text}")
            fever_str = "\033[31mYES\033[0m" if metrics.metabolism.in_fever else "No"
            lines.append(f"  Fever: {fever_str}")
        else:
            lines.append("  \033[90m[offline]\033[0m")
        lines.append("")

    # Flux Panel (3)
    if focus is None or focus == 3:
        lines.append("\033[34m FLUX \033[0m")
        if metrics.flux.is_online:
            lines.append(f"  Events/sec: {metrics.flux.events_per_second:.1f}")
            lines.append(f"  Queue: {metrics.flux.queue_depth} pending")
            lines.append(f"  Agents: {metrics.flux.active_agents} active")
        else:
            lines.append("  \033[90m[offline]\033[0m")
        lines.append("")

    # Triad Panel (4)
    if focus is None or focus == 4:
        lines.append("\033[35m TRIAD \033[0m")
        if metrics.triad.is_online:

            def _bar(val: float) -> str:
                filled = int(val * 10)
                return "█" * filled + "░" * (10 - filled)

            lines.append(f"  D {_bar(metrics.triad.durability)} PG")
            lines.append(f"  R {_bar(metrics.triad.resonance)} Qd")
            lines.append(f"  F {_bar(metrics.triad.reflex)} Rd")
        else:
            lines.append("  \033[90m[offline]\033[0m")
        lines.append("")

    # Traces Panel (5)
    if focus is None or focus == 5:
        lines.append("\033[90m RECENT TRACES \033[0m")
        if metrics.traces:
            for trace in metrics.traces[:5]:
                line = trace.render(show_timestamp=True)
                lines.append(f"  {line[:50]}")
        else:
            lines.append("  \033[90m(no traces)\033[0m")
        lines.append("")

    # Entropy gauge
    entropy_val = metrics.metabolism.pressure if metrics.metabolism.is_online else 0.0
    entropy_pct = int(entropy_val * 100)
    entropy_bar = "█" * (entropy_pct // 5) + "░" * (20 - entropy_pct // 5)
    lines.append(f"\033[90m Entropy: {entropy_bar} {entropy_pct}%\033[0m")

    # Footer
    lines.append("")
    collected = (
        metrics.collected_at.strftime("%H:%M:%S")
        if hasattr(metrics, "collected_at")
        else "--:--:--"
    )
    lines.append(f"\033[90m Last refresh: {collected}\033[0m")

    # In raw terminal mode, \n doesn't include carriage return
    # Use \r\n for proper line breaks
    return "\r\n".join(lines)


def run_ambient_mode(state: ReplState) -> int:
    """
    Run REPL in ambient mode - passive dashboard.

    Shows live system status without interactive prompt.
    Refreshes at configurable interval (default 5s).

    Wave 5: Ambient mode for passive monitoring.

    Args:
        state: ReplState with ambient_interval set

    Returns:
        Exit code (0 for success)
    """
    import asyncio
    import time

    # Import collectors
    try:
        from agents.i.data.dashboard_collectors import (
            collect_metrics,
            create_demo_metrics,
        )
    except ImportError:
        print("\033[31mError:\033[0m Dashboard collectors not available")
        return 1

    # Check if we have a terminal
    if not sys.stdin.isatty():
        print("\033[33mWarning:\033[0m Ambient mode requires a terminal. Using single snapshot.")
        # Single snapshot mode
        try:
            metrics = asyncio.run(collect_metrics())
        except Exception:
            metrics = create_demo_metrics()
        print(_render_ambient_screen(metrics, paused=False, focus=state.ambient_focus))
        return 0

    # Set up raw mode for non-blocking keyboard
    try:
        import termios
        import tty

        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        have_raw_mode = True
    except (ImportError, termios.error):
        have_raw_mode = False
        old_settings = None

    # Hide cursor
    print("\033[?25l", end="", flush=True)

    try:
        last_refresh = 0.0
        while state.running:
            current_time = time.time()

            # Check for keypress
            key = _get_key_nonblocking()
            if key:
                should_refresh = _handle_ambient_key(key, state)
                if should_refresh:
                    last_refresh = 0.0  # Force refresh

            # Refresh if not paused and interval elapsed
            if not state.ambient_paused and (current_time - last_refresh) >= state.ambient_interval:
                # Clear screen
                print("\033[2J\033[H", end="", flush=True)

                # Collect and render metrics
                try:
                    metrics = asyncio.run(collect_metrics())
                except Exception:
                    metrics = create_demo_metrics()

                screen = _render_ambient_screen(
                    metrics,
                    paused=state.ambient_paused,
                    focus=state.ambient_focus,
                )
                print(screen, end="", flush=True)
                last_refresh = current_time

            # Small sleep to prevent CPU spin
            time.sleep(0.05)

    finally:
        # Show cursor
        print("\033[?25h", end="", flush=True)

        # Restore terminal settings
        if have_raw_mode and old_settings is not None:
            import termios

            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        # Clear screen one more time
        print("\033[2J\033[H", end="")
        print("\033[90mAmbient mode ended. The forest rests.\033[0m")

    return 0


# =============================================================================
# Tab Completion
# =============================================================================


def _display_matches(substitution: str, matches: Sequence[str], longest_match_length: int) -> None:
    """
    Custom display hook for showing completion matches.

    Called by readline when there are multiple matches to display.
    Renders completions in a compact format.

    Args:
        substitution: The text being completed
        matches: List of possible completions
        longest_match_length: Length of the longest match
    """
    # Print newline to separate from prompt
    print()

    # Group by type for better organization
    contexts_list = [m for m in matches if m in CONTEXTS]
    commands = [
        m
        for m in matches
        if m.startswith("/") or m in ("help", "exit", "quit", "clear", "?", "??", "..", ".", "/")
    ]
    others = [m for m in matches if m not in contexts_list and m not in commands]

    # Display contexts first (compact)
    if contexts_list:
        print(f"\033[36m{' '.join(sorted(contexts_list))}\033[0m")

    # Display other completions (holons, aspects) - compact
    if others:
        print(f"\033[33m{' '.join(sorted(others))}\033[0m")

    # Display commands last (compact, dimmed)
    if commands:
        print(f"\033[90m{' '.join(sorted(commands))}\033[0m")

    # Redisplay the prompt with current input
    print()
    sys.stdout.flush()

    # Force readline to redisplay the prompt
    try:
        readline.redisplay()
    except Exception:
        pass  # Some readline implementations don't support this


class Completer:
    """
    Tab completion for AGENTESE paths.

    Wave 5: Enhanced completion with display hook for showing available options.
    Wave 5.1: Dotted path completion (fast-forward with '.')

    Features:
    - Press TAB to see all available options
    - Type partial text + TAB to autocomplete
    - Context-aware: shows holons in context, aspects in holon
    - Dynamic completions from Logos registry (Wave 3)
    - Dotted paths: type "self." to see self's children (Wave 5.1)
    """

    def __init__(self, state: ReplState):
        self.state = state
        self.matches: list[str] = []

    def complete(self, text: str, state_idx: int) -> str | None:
        """Return the state_idx'th completion for text."""
        if state_idx == 0:
            self.matches = self._get_matches(text)

        if state_idx < len(self.matches):
            return self.matches[state_idx]
        return None

    def _get_matches(self, text: str) -> list[str]:
        """
        Get all completions matching text.

        Wave 3 Enhancement: Dynamic completion from Logos registry.
        Wave 5 Enhancement: Better organization for display.
        Wave 5.1 Enhancement: Dotted path completion (fast-forward).

        Dotted path examples:
            "self."      → ["self.status", "self.memory", "self.soul", ...]
            "self.so"    → ["self.soul"]
            "self.soul." → ["self.soul.manifest", "self.soul.witness", ...]
        """
        # Wave 5.1: Handle dotted paths for fast-forward completion
        if "." in text and not text.startswith("."):
            return self._get_dotted_matches(text)

        matches = []

        # Handle empty input at root - show contexts
        if not self.state.path and not text:
            matches = list(CONTEXTS)

        # At root with input, complete contexts
        elif not self.state.path:
            matches = [c for c in CONTEXTS if c.startswith(text.lower())]

        # In context, complete holons
        elif len(self.state.path) == 1:
            context = self.state.path[0]
            holons = CONTEXT_HOLONS.get(context, [])

            if not text:
                # No input - show all holons for this context
                matches = list(holons)
            else:
                matches = [h for h in holons if h.startswith(text.lower())]

            # Wave 3 + Phase 4: Add dynamic completions from registry
            # Try logos first, then fall back to direct registry access
            registry_handles: list[str] = []
            logos = self.state.get_logos()
            if logos is not None:
                try:
                    registry_handles = logos.list_handles(context)
                except Exception:
                    pass  # Fall through to registry fallback

            # Phase 4: Direct registry fallback for robustness
            if not registry_handles:
                try:
                    from protocols.agentese.registry import get_registry

                    registry = get_registry()
                    registry_handles = registry.list_by_context(context)
                except Exception:
                    pass  # Graceful degradation

            for handle in registry_handles:
                # Extract just the holon part (e.g., "self.soul" -> "soul")
                parts = handle.split(".")
                if len(parts) >= 2:
                    holon = parts[1]
                    if (not text or holon.startswith(text.lower())) and holon not in matches:
                        matches.append(holon)

        # In holon, complete aspects
        else:
            aspects = [
                "manifest",
                "witness",
                "affordances",
                "refine",
                "lens",
                "define",
                "sip",
                "tithe",
            ]
            if not text:
                matches = list(aspects)
            else:
                matches = [a for a in aspects if a.startswith(text.lower())]

        # Add special commands (always available)
        special = [
            "..",
            ".",
            "/",
            "?",
            "??",
            "help",
            "exit",
            "quit",
            "clear",
            "/observer",
            "/observers",
            "/history",  # Wave 3
            "/memory",  # Phase 4
            # Wave 4: Joy-inducing shortcuts
            "/oblique",
            "/constrain",
            "/yes-and",
            "/expand",
            "/surprise",
            "/surprise-me",
            "/project",
            "/sparkline",
            "/why",
            "/tension",
            "/challenge",
        ]
        if not text:
            matches.extend(special)
        else:
            matches.extend([s for s in special if s.startswith(text)])

        # Complete archetype names after /observer
        if text.startswith("/observer "):
            prefix = text[len("/observer ") :]
            matches = [f"/observer {a}" for a in OBSERVER_ARCHETYPES if a.startswith(prefix)]

        return sorted(set(matches))

    def _get_dotted_matches(self, text: str) -> list[str]:
        """
        Handle dotted path completion (Wave 5.1 fast-forward).

        Parses dotted paths and returns completions with full prefix.
        Supports both absolute paths (self.soul.) and relative paths (soul. when in [self]).

        Args:
            text: Input like "self.", "soul." (relative), "self.soul.ref"

        Returns:
            List of completions with dotted prefix, e.g.:
            - At root, "self." → ["self.status", "self.soul", ...]
            - At [self], "soul." → ["soul.manifest", "soul.witness", ...]
            - At [self], "self.soul." → ["self.soul.manifest", ...] (absolute)
        """
        # Split on dots: "soul.ref" → ["soul", "ref"]
        parts = text.split(".")

        # If ends with dot, completing is empty: "soul." → parts=["soul", ""]
        # Otherwise, last part is what we're completing: "soul.re" → parts=["soul", "re"]
        completing = parts[-1].lower()
        input_path_parts = parts[:-1]  # The typed path prefix

        # Build the prefix for completions (preserves user's input format)
        prefix = ".".join(input_path_parts) + "." if input_path_parts else ""

        # Resolve the full path by combining current state path with input
        # Check if input starts with a context (absolute path) or is relative
        if input_path_parts and input_path_parts[0].lower() in CONTEXTS:
            # Absolute path: "self.soul." - use as-is
            full_path_parts = [p.lower() for p in input_path_parts]
        else:
            # Relative path: "soul." at [self] → full path is ["self", "soul"]
            full_path_parts = self.state.path + [p.lower() for p in input_path_parts]

        # Determine what to complete based on resolved path depth
        if len(full_path_parts) == 0:
            # Just "." at root - shouldn't happen due to guard, but handle it
            return []

        elif len(full_path_parts) == 1:
            # Completing holons for a context
            context = full_path_parts[0]
            if context not in CONTEXTS:
                return []

            holons = CONTEXT_HOLONS.get(context, [])
            candidates = list(holons)

            # Wave 3 + Phase 4: Add dynamic completions from registry
            registry_handles: list[str] = []
            logos = self.state.get_logos()
            if logos is not None:
                try:
                    registry_handles = logos.list_handles(context)
                except Exception:
                    pass  # Fall through to registry fallback

            # Phase 4: Direct registry fallback for robustness
            if not registry_handles:
                try:
                    from protocols.agentese.registry import get_registry

                    registry = get_registry()
                    registry_handles = registry.list_by_context(context)
                except Exception:
                    pass  # Graceful degradation

            for handle in registry_handles:
                handle_parts = handle.split(".")
                if len(handle_parts) >= 2:
                    holon = handle_parts[1]
                    if holon not in candidates:
                        candidates.append(holon)

            # Filter by completing prefix and add input prefix
            matches = [f"{prefix}{h}" for h in candidates if h.lower().startswith(completing)]

        elif len(full_path_parts) == 2:
            # Completing aspects for a holon
            aspects = [
                "manifest",
                "witness",
                "affordances",
                "refine",
                "lens",
                "define",
                "sip",
                "tithe",
            ]
            matches = [f"{prefix}{a}" for a in aspects if a.lower().startswith(completing)]

        else:
            # Deeper paths - no standard completions
            matches = []

        return sorted(set(matches))


# =============================================================================
# Main REPL Loop
# =============================================================================


def run_script(script_path: Path, verbose: bool = False) -> int:
    """
    Run REPL commands from a script file (non-interactive).

    Wave 3 Intelligence: Script mode for automation.

    Script syntax:
        - One command per line
        - Lines starting with # are comments
        - Empty lines are ignored
        - exit/quit terminates early

    Args:
        script_path: Path to the .repl script file
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success)
    """
    if not script_path.exists():
        print(f"\033[31mError:\033[0m Script not found: {script_path}")
        return 1

    state = ReplState(verbose=verbose)

    try:
        lines = script_path.read_text().splitlines()
    except (OSError, PermissionError) as e:
        print(f"\033[31mError:\033[0m Cannot read script: {e}")
        return 1

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Early exit
        if line.lower() in ("exit", "quit", "q"):
            break

        # Print command being executed (with line number)
        if verbose:
            print(f"\033[90m[{line_num}]\033[0m {line}")
        else:
            print(f"\033[36m»\033[0m {line}")

        # Process the command
        result = _process_script_command(state, line)
        if result:
            print(result)
            print()  # Blank line between results

    return 0


def _process_script_command(state: ReplState, line: str) -> str | None:
    """Process a single script command and return the result."""
    # Handle special commands
    if line.lower() == "help":
        return HELP_TEXT

    # Check for /observer commands
    if line.startswith("/observer") or line == "/observers":
        return handle_observer_command(state, line)

    # Check for /history commands
    if line.startswith("/history"):
        return handle_history_search(state, line)

    # Check for introspection
    intro_result = handle_introspection(state, line)
    if intro_result is not None:
        return intro_result

    # Check for composition
    if ">>" in line:
        return handle_composition(state, line)

    # Parse command - support both space-separated and dotted paths (Wave 5.1)
    parts = _parse_path_input(line)

    # Check for navigation
    nav_result = handle_navigation(state, parts)
    if nav_result is not None:
        return nav_result

    # Otherwise, treat as invocation
    return handle_invocation(state, parts)


def run_repl(
    ctx: "InvocationContext | None" = None,
    verbose: bool = False,
    restore: bool = False,
    learning: bool = False,
) -> int:
    """
    Run the AGENTESE REPL.

    This is a synchronous function that blocks until the user exits.

    Wave 6 Learning Mode:
    - Adaptive guide tracks fluency (/fluency)
    - Contextual hints based on skill level
    - On-demand lessons (/learn <topic>)

    Wave 3 Intelligence:
    - Session restoration (--restore flag)
    - History search (/history command)
    - Fuzzy matching for typo correction

    Wave 4 Joy-Inducing:
    - Time-aware welcome messages (J1)
    - K-gent personality integration (J2)
    - Easter eggs (J3)
    - Contextual hints (J5)

    Principle: Joy-Inducing - the REPL should feel warm and responsive.
    """
    state = ReplState(verbose=verbose, learning_mode=learning)

    # Wave 3: Restore previous session if requested
    if restore and SESSION_AVAILABLE and restore_session_to_state is not None:
        if restore_session_to_state(state):
            state.restored_session = True

    # Set up tab completion
    # Wave 5: Changed to 'complete' for showing all options on ambiguous input
    completer = Completer(state)
    readline.set_completer(completer.complete)

    # Detect libedit (macOS) vs GNU readline - they use different binding syntax
    is_libedit = "libedit" in (readline.__doc__ or "").lower()
    if is_libedit:
        # libedit (macOS) binding syntax
        readline.parse_and_bind("bind ^I rl_complete")
        # Show all completions immediately when ambiguous (single TAB press)
        readline.parse_and_bind("set show-all-if-ambiguous on")
    else:
        # GNU readline binding syntax
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set show-all-if-ambiguous on")

    # Set up custom display hook for pretty-printing completions
    try:
        readline.set_completion_display_matches_hook(_display_matches)
    except AttributeError:
        pass  # Not all readline implementations support this

    # Configure completer delimiters - keep space as delimiter for multi-word commands
    # but preserve dots for AGENTESE path completion
    readline.set_completer_delims(" \t\n")

    # Set up history file
    history_file = Path.home() / ".kgents_repl_history"
    try:
        readline.read_history_file(history_file)
    except (FileNotFoundError, PermissionError, OSError):
        pass  # History unavailable, continue without

    # Print welcome banner
    print(WELCOME_BANNER)

    # Wave 4: Personalized welcome message (J1)
    welcome_msg = get_welcome_message(state)
    print(f"\033[36m{welcome_msg}\033[0m\n")

    # Wave 6: Learning mode welcome
    if state.learning_mode:
        guide = state.get_guide()
        if guide:
            learning_welcome = guide.welcome_message(state.path)
            print(f"\033[33m{learning_welcome}\033[0m\n")

    # Main loop
    while state.running:
        try:
            line = input(state.prompt).strip()

            if not line:
                continue

            # Security: Input length limit
            if len(line) > MAX_INPUT_LENGTH:
                print(
                    f"\033[31mError:\033[0m Input too long ({len(line)} chars, max {MAX_INPUT_LENGTH})"
                )
                continue

            # Add to history
            state.history.append(line)

            # Handle special commands
            if line.lower() in ("exit", "quit", "q"):
                # Wave 3: Save session on exit
                if SESSION_AVAILABLE and save_session is not None:
                    save_session(state.path, state.observer)
                # Wave 6: Save fluency on exit
                if state.learning_mode:
                    guide = state.get_guide()
                    if guide:
                        try:
                            from protocols.cli.repl_guide import save_fluency

                            save_fluency(guide.tracker)
                        except ImportError:
                            pass
                print("\033[90mFarewell. The river flows.\033[0m")
                break

            if line.lower() == "help":
                print(HELP_TEXT)
                continue

            if line.lower() == "clear":
                print("\033[2J\033[H", end="")
                continue

            if line.lower() == "history":
                for i, cmd in enumerate(state.history[-20:], 1):
                    print(f"  {i:3}  {cmd}")
                continue

            # Wave 3: Check for /history commands
            if line.startswith("/history"):
                history_result = handle_history_search(state, line)
                print(history_result)
                continue

            # Phase 4: Check for /memory commands (conversation window)
            if line.startswith("/memory"):
                memory_result = handle_memory_command(state, line)
                print(memory_result)
                continue

            # Phase 3 (CLI v7): Check for /presence commands (agent cursors)
            if line.startswith("/presence"):
                presence_result = handle_presence_command(state, line)
                print(presence_result)
                continue

            # Check for /observer commands (Wave 2)
            if line.startswith("/observer") or line == "/observers":
                observer_result = handle_observer_command(state, line)
                print(observer_result)
                continue

            # Wave 6: Learning guide commands
            if line.startswith("/learn"):
                guide = state.get_guide()
                if guide:
                    from protocols.cli.repl_guide import handle_learn_command

                    args = line.split()[1:] if len(line.split()) > 1 else [""]
                    learn_result = handle_learn_command(guide, args)
                    print(learn_result)
                else:
                    print("\033[33mLearning mode not available.\033[0m Enable with: kg -i --learn")
                continue

            if line == "/fluency":
                guide = state.get_guide()
                if guide:
                    from protocols.cli.repl_guide import handle_fluency_command

                    fluency_result = handle_fluency_command(guide)
                    print(fluency_result)
                else:
                    print("\033[33mLearning mode not available.\033[0m Enable with: kg -i --learn")
                continue

            if line == "/hint":
                guide = state.get_guide()
                if guide:
                    from protocols.cli.repl_guide import handle_hint_command

                    hint_result = handle_hint_command(guide, state.path)
                    print(hint_result)
                else:
                    hint = get_contextual_hint(state)
                    print(hint if hint else "Type '?' for available commands.")
                continue

            # v3: Alias management commands
            if line.startswith("/alias") or line == "/aliases" or line.startswith("/unalias"):
                alias_result = handle_alias_command(state, line)
                print(alias_result)
                continue

            # Wave 4: Check for slash shortcuts (joy-inducing commands)
            if line.startswith("/") and line.split()[0].lower() in SLASH_SHORTCUTS:
                shortcut_result = handle_slash_shortcut(state, line)
                if shortcut_result is not None:
                    print(shortcut_result)
                    state.consecutive_errors = 0
                continue

            # Check for introspection
            intro_result = handle_introspection(state, line)
            if intro_result is not None:
                print(intro_result)
                state.consecutive_errors = 0  # Reset on success
                continue

            # Wave 4: Check for easter eggs (J3)
            easter_result = handle_easter_egg(line, state)
            if easter_result is not None:
                print(easter_result)
                state.consecutive_errors = 0
                continue

            # Check for composition
            if ">>" in line:
                comp_result = handle_composition(state, line)
                print(comp_result)
                state.consecutive_errors = 0
                continue

            # Parse command - support both space-separated and dotted paths
            # Wave 5.1: "world.dev" → ["world", "dev"], "self.soul.reflect" → ["self", "soul", "reflect"]
            parts = _parse_path_input(line)

            # Check for navigation
            nav_result = handle_navigation(state, parts)
            if nav_result is not None:
                print(nav_result)
                state.consecutive_errors = 0
                # Wave 6: Track for learning guide
                guide = state.get_guide()
                if guide and state.learning_mode:
                    newly_mastered, msg = guide.on_command(line, state.path)
                    if msg:
                        print(f"\033[32m{msg}\033[0m")
                continue

            # Otherwise, treat as invocation
            result = handle_invocation(state, parts)
            if result:
                print(result)
                # Track consecutive errors
                if "Error" in result or "error" in result.lower():
                    state.consecutive_errors += 1
                    # Wave 6: Guide hint in learning mode
                    guide = state.get_guide()
                    if guide and state.learning_mode:
                        hint = guide.contextual_hint(state.path, last_error=True)
                        if hint:
                            print(hint)
                    else:
                        # Wave 4: Show contextual hint (J5)
                        hint = get_contextual_hint(state)
                        if hint:
                            print(hint)
                else:
                    state.consecutive_errors = 0
                    # Wave 6: Track for learning guide
                    guide = state.get_guide()
                    if guide and state.learning_mode:
                        newly_mastered, msg = guide.on_command(line, state.path)
                        if msg:
                            print(f"\033[32m{msg}\033[0m")
                    # Phase 4 (CLI v7): Record turn for 10+ message memory
                    state.record_turn(line, result)
                    # Phase 4 (CLI v7): Show presence footer if enabled
                    if state.show_presence:
                        presence_status = state.get_presence_status()
                        if presence_status:
                            print(f"\n\033[90m{presence_status}\033[0m")

        except KeyboardInterrupt:
            print("\n\033[90m(use 'exit' to leave)\033[0m")
            continue

        except EOFError:
            # Wave 3: Save session on EOF
            if SESSION_AVAILABLE and save_session is not None:
                save_session(state.path, state.observer)
            # Wave 6: Save fluency on EOF
            if state.learning_mode:
                guide = state.get_guide()
                if guide:
                    try:
                        from protocols.cli.repl_guide import save_fluency

                        save_fluency(guide.tracker)
                    except ImportError:
                        pass
            print("\n\033[90mFarewell. The river flows.\033[0m")
            break

        except Exception as e:
            print(f"\033[31mError:\033[0m {e}")
            state.consecutive_errors += 1
            # Wave 4: Show contextual hint (J5)
            hint = get_contextual_hint(state)
            if hint:
                print(hint)
            if verbose:
                import traceback

                traceback.print_exc()

    # Save history
    try:
        readline.write_history_file(history_file)
    except Exception:
        pass

    return 0


# =============================================================================
# Entry Point
# =============================================================================


def cmd_interactive(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Enter the AGENTESE REPL.

    Wave 6 Features:
    - Learning mode (--learn) - adaptive guide tracks fluency, offers hints
    - Tutorial mode (--tutorial) - linear guided intro (for absolute beginners)

    Wave 5 Features:
    - Ambient mode (--ambient) - passive dashboard
    - Configurable refresh interval (--interval <secs>)

    Wave 3 Features:
    - Session restoration (--restore)
    - Script mode (--script <file>)
    - Fuzzy matching for typo correction
    - History search (/history command)

    The REPL provides interactive navigation through the five contexts,
    with tab completion, history, and path composition.
    """
    verbose = "--verbose" in args or "-v" in args
    restore = "--restore" in args or "-r" in args
    learning = "--learn" in args or "-l" in args

    # Wave 3: Script mode
    if "--script" in args:
        idx = args.index("--script")
        if idx + 1 < len(args):
            script_path = Path(args[idx + 1])
            return run_script(script_path, verbose=verbose)
        else:
            print("\033[31mError:\033[0m --script requires a file path")
            return 1

    # Wave 5: Ambient mode
    if "--ambient" in args:
        state = ReplState(verbose=verbose)

        # Parse interval flag
        if "--interval" in args:
            idx = args.index("--interval")
            if idx + 1 < len(args):
                try:
                    state.ambient_interval = float(args[idx + 1])
                except ValueError:
                    print(f"\033[31mError:\033[0m Invalid interval: {args[idx + 1]}")
                    return 1

        return run_ambient_mode(state)

    # Wave 6: Tutorial mode (linear, for absolute beginners)
    if "--tutorial" in args:
        try:
            from protocols.cli.repl_tutorial import run_tutorial_mode

            reset = "--reset" in args
            return run_tutorial_mode(reset=reset)
        except ImportError as e:
            print(f"\033[31mError:\033[0m Tutorial module not available: {e}")
            return 1

    return run_repl(ctx=ctx, verbose=verbose, restore=restore, learning=learning)


if __name__ == "__main__":
    sys.exit(cmd_interactive(sys.argv[1:]))
