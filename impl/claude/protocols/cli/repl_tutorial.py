"""
AGENTESE REPL Tutorial: Auto-constructing guided learning.

Wave 6: Tutorial mode teaches the AGENTESE ontology through interactive
exploration. Lessons are auto-generated from REPL introspection.

Design Philosophy:
    - Auto-constructing: Lessons derive from REPL's own structure
    - Hot data: Generated once, cached for fast loading
    - Pedagogical: Learning by doing, not by reading
    - Resumable: Progress persists across sessions

Usage:
    kg -i --tutorial           # Start or resume tutorial
    kg -i --tutorial --reset   # Start fresh (clear progress)
    kg tutorial generate       # Regenerate cached lessons

The generator introspects:
    - CONTEXTS: The five contexts (self, world, concept, void, time)
    - CONTEXT_HOLONS: What's available in each context
    - Navigation: .., /, ?, etc.
    - Composition: >> pipeline operator
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# =============================================================================
# Constants
# =============================================================================

# Where to save tutorial progress
DEFAULT_PROGRESS_FILE = Path.home() / ".kgents_tutorial_progress.json"

# Context descriptions for lesson generation
CONTEXT_DESCRIPTIONS: dict[str, str] = {
    "self": "your agent's internal world (status, memory, soul)",
    "world": "external entities (agents, infrastructure, daemons)",
    "concept": "abstract ideas (laws, principles, dialectics)",
    "void": "entropy and the Accursed Share (serendipity, shadow)",
    "time": "temporal traces (past, future, schedules)",
}

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class TutorialLesson:
    """
    A single tutorial lesson - auto-constructable from REPL structure.

    Each lesson teaches one concept through interaction:
    - prompt: What we're asking the user to do
    - expected: Valid responses (flexible matching)
    - hint: Help if stuck
    - celebration: Success message guiding next steps
    """

    name: str
    context: str  # Which REPL context this lesson targets (or "root")
    prompt: str
    expected: list[str]
    hint: str
    celebration: str

    @classmethod
    def from_context(cls, context: str, description: str) -> "TutorialLesson":
        """
        Auto-generate a lesson for entering a context.

        Introspects the context name to generate appropriate lesson content.
        """
        return cls(
            name=f"discover_{context}",
            context="root",
            prompt=f"Type '{context}' to explore {description}:",
            expected=[context],
            hint=f"Try typing: {context}",
            celebration=f"You've entered the {context} context. Type '?' to see what's here.",
        )

    @classmethod
    def navigation_up(cls) -> "TutorialLesson":
        """Generate lesson for going up one level."""
        return cls(
            name="navigate_up",
            context="any",
            prompt="Type '..' to go back up one level:",
            expected=[".."],
            hint="Two dots (..) moves you up in the hierarchy.",
            celebration="Navigation is simple: enter a context, explore, go back with '..'",
        )

    @classmethod
    def introspection(cls) -> "TutorialLesson":
        """Generate lesson for ? introspection."""
        return cls(
            name="introspection",
            context="any",
            prompt="Type '?' to see available affordances in this context:",
            expected=["?"],
            hint="The question mark (?) shows what you can do here.",
            celebration="Introspection reveals affordances - the actions available to you.",
        )

    @classmethod
    def composition(cls) -> "TutorialLesson":
        """Generate lesson for >> composition."""
        return cls(
            name="composition",
            context="root",
            prompt="Type 'self.status >> concept.count' to compose a pipeline:",
            expected=[
                "self.status >> concept.count",
                "self status >> concept count",
                "self.status>>concept.count",
            ],
            hint="The >> operator composes paths into pipelines.",
            celebration="Pipelines compose actions - the heart of AGENTESE. Composition over construction!",
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON storage."""
        return {
            "name": self.name,
            "context": self.context,
            "prompt": self.prompt,
            "expected": self.expected,
            "hint": self.hint,
            "celebration": self.celebration,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TutorialLesson":
        """Deserialize from dict."""
        return cls(
            name=data["name"],
            context=data["context"],
            prompt=data["prompt"],
            expected=data["expected"],
            hint=data["hint"],
            celebration=data["celebration"],
        )


@dataclass
class TutorialState:
    """
    Tutorial progress state - persists across sessions.

    Tracks which lessons are completed and allows resumption.
    """

    lessons: list[TutorialLesson]
    current_lesson: int = 0
    completed: list[str] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_session: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def is_complete(self) -> bool:
        """Check if all lessons are completed."""
        return self.current_lesson >= len(self.lessons)

    @property
    def progress_percent(self) -> int:
        """Calculate progress percentage."""
        if not self.lessons:
            return 100
        return int((self.current_lesson / len(self.lessons)) * 100)


# =============================================================================
# Lesson Generation (Auto-Constructing)
# =============================================================================


def generate_lessons(
    contexts: frozenset[str] | None = None,
    context_holons: dict[str, list[str]] | None = None,
) -> list[TutorialLesson]:
    """
    Auto-generate lessons by introspecting REPL structure.

    If contexts/holons not provided, imports from repl.py.
    This allows both runtime generation and cached generation.

    Args:
        contexts: Set of context names (default: import from repl)
        context_holons: Mapping of context -> holons (default: import from repl)

    Returns:
        List of TutorialLesson objects in pedagogical order
    """
    # Import from REPL if not provided (for auto-construction)
    if contexts is None or context_holons is None:
        try:
            from protocols.cli.repl import CONTEXT_HOLONS, CONTEXTS

            contexts = contexts or CONTEXTS
            context_holons = context_holons or CONTEXT_HOLONS
        except ImportError:
            # Fallback defaults if REPL not importable
            contexts = frozenset({"self", "world", "concept", "void", "time"})
            context_holons = {
                "self": ["status", "soul"],
                "world": ["agents"],
                "concept": ["laws"],
                "void": ["entropy"],
                "time": ["trace"],
            }

    lessons: list[TutorialLesson] = []

    # Phase 1: Introduce the first context (self - most relatable)
    lessons.append(
        TutorialLesson.from_context("self", CONTEXT_DESCRIPTIONS.get("self", "self"))
    )

    # Phase 2: Teach introspection early
    lessons.append(TutorialLesson.introspection())

    # Phase 3: Teach navigation
    lessons.append(TutorialLesson.navigation_up())

    # Phase 4: Introduce remaining contexts in pedagogical order
    # (world for tangible, concept for abstract, void for advanced, time last)
    context_order = ["world", "concept", "void", "time"]
    for ctx in context_order:
        if ctx in contexts:
            lessons.append(
                TutorialLesson.from_context(ctx, CONTEXT_DESCRIPTIONS.get(ctx, ctx))
            )

    # Phase 5: Teach composition (advanced)
    lessons.append(TutorialLesson.composition())

    return lessons


def generate_lessons_source() -> str:
    """
    Generate Python source code for cached lessons.

    This is used by the hot data build step to pre-generate lessons.

    Returns:
        Python source code defining CACHED_LESSONS
    """
    lessons = generate_lessons()

    # Build Python source
    lines = [
        '"""',
        "Auto-generated tutorial lessons.",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Source: protocols/cli/repl_tutorial.py:generate_lessons()",
        "",
        "DO NOT EDIT - regenerate with: kg tutorial generate",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "# Auto-generated lesson data",
        "CACHED_LESSONS: list[dict] = [",
    ]

    for lesson in lessons:
        lines.append(f"    {lesson.to_dict()!r},")

    lines.append("]")
    lines.append("")

    return "\n".join(lines)


def regenerate_lessons_to_file(output_path: Path | None = None) -> Path:
    """
    Regenerate cached lessons to file (hot data build step).

    Args:
        output_path: Where to write (default: protocols/cli/generated/tutorial_lessons.py)

    Returns:
        Path to the generated file
    """
    if output_path is None:
        output_path = Path(__file__).parent / "generated" / "tutorial_lessons.py"

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate and write
    source = generate_lessons_source()
    output_path.write_text(source)

    return output_path


# =============================================================================
# Lesson Loading (Hot Data Pattern)
# =============================================================================


def load_lessons() -> list[TutorialLesson]:
    """
    Load lessons - prefers cached, falls back to runtime generation.

    Hot data pattern:
    1. Try to load from generated/tutorial_lessons.py (fast)
    2. Fall back to generate_lessons() (slow but always works)
    """
    try:
        from protocols.cli.generated.tutorial_lessons import CACHED_LESSONS

        return [TutorialLesson.from_dict(d) for d in CACHED_LESSONS]
    except ImportError:
        # No cached lessons - generate at runtime
        return generate_lessons()


# =============================================================================
# Progress Persistence
# =============================================================================


def save_progress(
    state: TutorialState,
    progress_file: Path = DEFAULT_PROGRESS_FILE,
) -> bool:
    """
    Save tutorial progress to disk.

    Args:
        state: Current tutorial state
        progress_file: Where to save (default: ~/.kgents_tutorial_progress.json)

    Returns:
        True if saved successfully
    """
    try:
        data = {
            "current_lesson": state.current_lesson,
            "completed": state.completed,
            "started_at": state.started_at,
            "last_session": datetime.now(timezone.utc).isoformat(),
        }
        progress_file.write_text(json.dumps(data, indent=2))
        return True
    except (OSError, PermissionError, TypeError):
        return False


def load_progress(
    progress_file: Path = DEFAULT_PROGRESS_FILE,
) -> dict[str, Any] | None:
    """
    Load tutorial progress from disk.

    Args:
        progress_file: Where to load from

    Returns:
        Progress dict or None if not found/invalid
    """
    try:
        if not progress_file.exists():
            return None
        result: dict[str, Any] = json.loads(progress_file.read_text())
        return result
    except (OSError, PermissionError, json.JSONDecodeError, TypeError):
        return None


def clear_progress(progress_file: Path = DEFAULT_PROGRESS_FILE) -> bool:
    """
    Clear tutorial progress (start fresh).

    Args:
        progress_file: Progress file to remove

    Returns:
        True if cleared successfully
    """
    try:
        if progress_file.exists():
            progress_file.unlink()
        return True
    except (OSError, PermissionError):
        return False


# =============================================================================
# Validation
# =============================================================================


def validate_response(
    response: str,
    lesson: TutorialLesson,
    fuzzy_matcher: Any = None,
) -> bool:
    """
    Validate user response against expected answers.

    Flexible matching:
    1. Exact match (case-insensitive)
    2. Fuzzy match for typos (if fuzzy_matcher provided)

    Args:
        response: User's input
        lesson: Current lesson with expected answers
        fuzzy_matcher: Optional FuzzyMatcher for typo correction

    Returns:
        True if response is valid
    """
    normalized = response.strip().lower()

    # Exact match (case-insensitive)
    for expected in lesson.expected:
        if normalized == expected.lower():
            return True

    # Fuzzy match for typos
    if fuzzy_matcher is not None:
        for expected in lesson.expected:
            try:
                suggestion = fuzzy_matcher.suggest(normalized, [expected.lower()])
                if suggestion == expected.lower():
                    return True
            except Exception:
                pass  # Graceful degradation

    return False


# =============================================================================
# Tutorial Display
# =============================================================================

# ANSI color codes
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

TUTORIAL_WELCOME = f"""\
{CYAN}╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│   {BOLD}AGENTESE REPL Tutorial{RESET}{CYAN}                                        │
│                                                                 │
│   {GRAY}"The noun is a lie. There is only the rate of change."{CYAN}        │
│                                                                 │
│   Learn the five contexts through guided exploration.           │
│   Type what's asked. Progress saves automatically.              │
│                                                                 │
│   {YELLOW}Commands:{RESET}{CYAN}  q = quit   s = skip   h = hint                     │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯{RESET}

"""

TUTORIAL_COMPLETE = f"""\
{CYAN}╭────────────────────────────────────────────────────────────────╮
│                                                                │
│   {GREEN}✓  TUTORIAL COMPLETE!{RESET}{CYAN}                                       │
│                                                                │
│   You've learned the AGENTESE ontology:                        │
│                                                                │
│   {GREEN}✓ self{RESET}{CYAN}    — Your agent's internal world                      │
│   {GREEN}✓ world{RESET}{CYAN}   — External entities and infrastructure             │
│   {GREEN}✓ concept{RESET}{CYAN} — Platonic ideals and definitions                  │
│   {GREEN}✓ void{RESET}{CYAN}    — Entropy, shadow, and serendipity                 │
│   {GREEN}✓ time{RESET}{CYAN}    — Traces, forecasts, and schedules                 │
│                                                                │
│   {GRAY}The forest is now open to you.{RESET}{CYAN}                              │
│                                                                │
│   {YELLOW}Next steps:{RESET}{CYAN}                                                  │
│   - kg -i                    Enter the REPL                    │
│   - kg -i --ambient          Watch the system breathe          │
│   - kg soul challenge        Test your understanding           │
│                                                                │
╰────────────────────────────────────────────────────────────────╯{RESET}
"""


def print_lesson_prompt(lesson: TutorialLesson, lesson_num: int, total: int) -> None:
    """Print the lesson prompt."""
    progress_bar = "█" * lesson_num + "░" * (total - lesson_num)
    print(f"\n{GRAY}[{lesson_num}/{total}] {progress_bar}{RESET}")
    print(f"\n{YELLOW}{lesson.prompt}{RESET}")


def print_celebration(lesson: TutorialLesson) -> None:
    """Print success celebration."""
    print(f"\n{GREEN}✓ {lesson.celebration}{RESET}")


def print_hint(lesson: TutorialLesson) -> None:
    """Print hint for stuck user."""
    print(f"\n{YELLOW}Hint: {lesson.hint}{RESET}")


# =============================================================================
# Tutorial Mode Runner
# =============================================================================


def run_tutorial_mode(
    reset: bool = False,
    progress_file: Path = DEFAULT_PROGRESS_FILE,
) -> int:
    """
    Run the REPL in tutorial mode - guided learning.

    Teaches the AGENTESE ontology through interactive lessons.
    Progress persists across sessions.

    Args:
        reset: If True, clear progress and start fresh
        progress_file: Where to save/load progress

    Returns:
        Exit code (0 for success)
    """
    # Clear progress if requested
    if reset:
        clear_progress(progress_file)

    # Load lessons (prefers cached, falls back to runtime)
    lessons = load_lessons()

    # Create state
    state = TutorialState(lessons=lessons)

    # Restore progress if available
    progress = load_progress(progress_file)
    if progress:
        state.current_lesson = progress.get("current_lesson", 0)
        state.completed = progress.get("completed", [])
        state.started_at = progress.get("started_at", state.started_at)

        # Show resume message
        if state.current_lesson > 0 and not state.is_complete:
            print(f"{GRAY}Resuming from lesson {state.current_lesson + 1}...{RESET}")
            print(f"{GRAY}Progress: {state.progress_percent}% complete{RESET}")

    # Print welcome
    print(TUTORIAL_WELCOME)

    # Get fuzzy matcher if available
    fuzzy = None
    try:
        from protocols.cli.repl_fuzzy import FuzzyMatcher, is_fuzzy_available

        if is_fuzzy_available():
            fuzzy = FuzzyMatcher(threshold=70, limit=3)
    except ImportError:
        pass

    # Main tutorial loop
    while not state.is_complete:
        lesson = state.lessons[state.current_lesson]
        print_lesson_prompt(lesson, state.current_lesson + 1, len(state.lessons))

        try:
            response = input(f"\n{CYAN}» {RESET}").strip()

            # Handle special commands
            if response.lower() == "q":
                save_progress(state, progress_file)
                print(f"\n{GRAY}Progress saved. Resume with: kg -i --tutorial{RESET}")
                return 0

            if response.lower() == "s":
                # Skip to next lesson
                state.current_lesson += 1
                save_progress(state, progress_file)
                print(f"{GRAY}(skipped){RESET}")
                continue

            if response.lower() == "h":
                print_hint(lesson)
                continue

            # Validate response
            if validate_response(response, lesson, fuzzy):
                print_celebration(lesson)
                state.completed.append(lesson.name)
                state.current_lesson += 1
                save_progress(state, progress_file)
            else:
                print(f"\n{GRAY}Not quite. Try again or press 'h' for a hint.{RESET}")

        except (KeyboardInterrupt, EOFError):
            save_progress(state, progress_file)
            print(f"\n\n{GRAY}Progress saved. Resume with: kg -i --tutorial{RESET}")
            return 0

    # Tutorial complete!
    print(TUTORIAL_COMPLETE)

    # Clear progress file (completed)
    clear_progress(progress_file)

    return 0


# =============================================================================
# CLI Command
# =============================================================================


def cmd_tutorial(args: list[str], ctx: Any = None) -> int:
    """
    Tutorial management command.

    Subcommands:
        generate    Regenerate cached lessons (hot data build)
        reset       Clear progress and start fresh
        status      Show tutorial progress

    Usage:
        kg tutorial generate   # Regenerate cached lessons
        kg tutorial reset      # Clear progress
        kg tutorial status     # Show progress
    """
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    subcommand = args[0]

    if subcommand == "generate":
        output = regenerate_lessons_to_file()
        print(f"{GREEN}✓{RESET} Generated {len(load_lessons())} lessons to {output}")
        return 0

    if subcommand == "reset":
        clear_progress()
        print(
            f"{GREEN}✓{RESET} Tutorial progress cleared. Start fresh with: kg -i --tutorial"
        )
        return 0

    if subcommand == "status":
        progress = load_progress()
        if progress:
            lessons = load_lessons()
            current = progress.get("current_lesson", 0)
            percent = int((current / len(lessons)) * 100) if lessons else 100
            print(f"Progress: {current}/{len(lessons)} lessons ({percent}%)")
            print(f"Started: {progress.get('started_at', 'unknown')}")
            print(f"Last session: {progress.get('last_session', 'unknown')}")
        else:
            print("No tutorial progress found. Start with: kg -i --tutorial")
        return 0

    print(f"Unknown subcommand: {subcommand}")
    return 1
