"""
AGENTESE REPL Adaptive Learning Guide.

An intelligent companion that helps you learn AGENTESE at your own pace,
wherever you are in the REPL. Not a linear tutorial - an adaptive guide.

Design Philosophy:
    - Context-Aware: Knows where you are and offers relevant help
    - Intent-Aware: Detects what you're trying to do
    - Progressive: Tracks fluency, reveals more as you grow
    - Non-Blocking: Integrates into normal REPL flow
    - Just-In-Time: Help when needed, not constant interruption

Usage:
    kg -i --learn              # Enable learning mode
    /learn                     # Show what to learn next
    /learn <topic>             # Learn about specific topic
    /fluency                   # See your progress
    /hint                      # Get contextual hint

The guide tracks demonstrated skills and adapts its suggestions.
Absolute beginners get a guided path; intermediates get contextual help.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# =============================================================================
# Constants
# =============================================================================

DEFAULT_FLUENCY_FILE = Path.home() / ".kgents_fluency.json"

# Skill categories and their prerequisites
SKILL_TREE: dict[str, dict[str, Any]] = {
    # Navigation skills
    "nav_context": {
        "name": "Context Navigation",
        "description": "Enter contexts: self, world, concept, void, time",
        "prerequisites": [],
        "demos": [
            "entered_self",
            "entered_world",
            "entered_concept",
            "entered_void",
            "entered_time",
        ],
        "threshold": 3,  # Need 3 of 5 to master
    },
    "nav_up": {
        "name": "Navigate Up",
        "description": "Go up with '..' command",
        "prerequisites": ["nav_context"],
        "demos": ["used_dotdot"],
        "threshold": 1,
    },
    "nav_root": {
        "name": "Navigate to Root",
        "description": "Return to root with '/' command",
        "prerequisites": ["nav_up"],
        "demos": ["used_slash"],
        "threshold": 1,
    },
    # Introspection skills
    "introspect_basic": {
        "name": "Basic Introspection",
        "description": "Use '?' to see affordances",
        "prerequisites": ["nav_context"],
        "demos": ["used_question"],
        "threshold": 1,
    },
    "introspect_deep": {
        "name": "Deep Introspection",
        "description": "Use '??' for detailed help",
        "prerequisites": ["introspect_basic"],
        "demos": ["used_questionquestion"],
        "threshold": 1,
    },
    # Invocation skills
    "invoke_basic": {
        "name": "Basic Invocation",
        "description": "Invoke paths like 'self status' or 'self.status'",
        "prerequisites": ["nav_context"],
        "demos": ["invoked_path"],
        "threshold": 2,
    },
    "invoke_aspect": {
        "name": "Aspect Invocation",
        "description": "Invoke specific aspects like 'soul.reflect'",
        "prerequisites": ["invoke_basic"],
        "demos": ["invoked_aspect"],
        "threshold": 1,
    },
    # Composition skills
    "compose_basic": {
        "name": "Basic Composition",
        "description": "Compose paths with >> operator",
        "prerequisites": ["invoke_basic"],
        "demos": ["used_pipeline"],
        "threshold": 1,
    },
    "compose_chain": {
        "name": "Chain Composition",
        "description": "Chain multiple >> operators",
        "prerequisites": ["compose_basic"],
        "demos": ["used_multi_pipeline"],
        "threshold": 1,
    },
    # Observer skills
    "observer_check": {
        "name": "Observer Awareness",
        "description": "Check current observer with /observer",
        "prerequisites": ["introspect_basic"],
        "demos": ["checked_observer"],
        "threshold": 1,
    },
    "observer_switch": {
        "name": "Observer Switching",
        "description": "Switch observers with /observer <archetype>",
        "prerequisites": ["observer_check"],
        "demos": ["switched_observer"],
        "threshold": 1,
    },
    # Context mastery
    "master_self": {
        "name": "Self Context Mastery",
        "description": "Explore self context deeply",
        "prerequisites": ["nav_context", "introspect_basic"],
        "demos": ["explored_self_status", "explored_self_soul", "explored_self_memory"],
        "threshold": 2,
    },
    "master_void": {
        "name": "Void Context Mastery",
        "description": "Explore void context deeply",
        "prerequisites": ["nav_context", "introspect_basic"],
        "demos": ["explored_void_entropy", "explored_void_shadow", "used_sip"],
        "threshold": 2,
    },
}

# Beginner path - suggested order for absolute beginners
BEGINNER_PATH = [
    "nav_context",
    "introspect_basic",
    "nav_up",
    "invoke_basic",
    "compose_basic",
    "observer_check",
]


# =============================================================================
# Fluency Levels
# =============================================================================


class FluencyLevel(Enum):
    """User's overall fluency level."""

    NOVICE = "novice"  # Just starting, needs guidance
    BEGINNER = "beginner"  # Knows basics, exploring
    INTERMEDIATE = "intermediate"  # Comfortable, learning advanced
    FLUENT = "fluent"  # Knows the system well


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Skill:
    """A learnable skill with progress tracking."""

    id: str
    name: str
    description: str
    prerequisites: list[str]
    demos_required: list[str]
    threshold: int
    demos_completed: set[str] = field(default_factory=set)

    @property
    def progress(self) -> float:
        """Progress toward mastery (0.0 to 1.0)."""
        if not self.demos_required:
            return 1.0
        completed = len(self.demos_completed & set(self.demos_required))
        return min(1.0, completed / self.threshold)

    @property
    def is_mastered(self) -> bool:
        """Whether this skill is mastered."""
        return self.progress >= 1.0

    @property
    def is_available(self) -> bool:
        """Whether prerequisites are met (set by FluencyTracker)."""
        # This is set externally based on prerequisite mastery
        return True  # Default, overridden by tracker


@dataclass
class MicroLesson:
    """
    A self-contained micro-lesson for a specific topic.

    Unlike linear tutorial steps, micro-lessons can be accessed
    in any order based on context and user needs.
    """

    topic: str
    title: str
    context: str  # Where this lesson is relevant ("any", "self", "void", etc.)
    explanation: str
    examples: list[str]
    try_it: str  # Suggested command to try
    next_topics: list[str]  # Related topics to explore

    @classmethod
    def for_context(cls, context: str) -> "MicroLesson":
        """Generate a lesson for entering a specific context."""
        descriptions = {
            "self": ("Your Internal World", "status, memory, soul, capabilities"),
            "world": ("External Entities", "agents, daemons, infrastructure"),
            "concept": ("Abstract Ideas", "laws, principles, dialectics"),
            "void": ("The Accursed Share", "entropy, shadow, serendipity"),
            "time": ("Temporal Dimension", "traces, past, future, schedules"),
        }
        title, contents = descriptions.get(context, (context, "..."))
        return cls(
            topic=f"context_{context}",
            title=f"The {context.title()} Context: {title}",
            context="any",
            explanation=f"The {context} context contains: {contents}. "
            f"Enter it by typing '{context}', then use '?' to explore.",
            examples=[
                context,
                f"{context}.status" if context == "self" else f"{context}",
            ],
            try_it=context,
            next_topics=["introspection", "navigation"],
        )

    @classmethod
    def for_navigation(cls) -> "MicroLesson":
        """Lesson on navigation commands."""
        return cls(
            topic="navigation",
            title="Navigating the REPL",
            context="any",
            explanation="Navigation is simple:\n"
            "  - Type a context name (self, world, etc.) to enter it\n"
            "  - Type '..' to go up one level\n"
            "  - Type '/' to return to root\n"
            "  - Type '.' to see where you are",
            examples=["..", "/", ".", "self", "world"],
            try_it="..",
            next_topics=["introspection", "invocation"],
        )

    @classmethod
    def for_introspection(cls) -> "MicroLesson":
        """Lesson on introspection commands."""
        return cls(
            topic="introspection",
            title="Introspection: Seeing What's Available",
            context="any",
            explanation="Two key commands reveal what you can do:\n"
            "  - '?' shows available affordances (what you can do here)\n"
            "  - '??' shows detailed help for the current location",
            examples=["?", "??"],
            try_it="?",
            next_topics=["invocation", "navigation"],
        )

    @classmethod
    def for_invocation(cls) -> "MicroLesson":
        """Lesson on path invocation."""
        return cls(
            topic="invocation",
            title="Invoking Paths",
            context="any",
            explanation="Invoke paths to execute actions:\n"
            "  - Space-separated: 'self status'\n"
            "  - Dot-separated: 'self.status'\n"
            "  - With aspect: 'self.soul.reflect'\n"
            "Paths are verbs, not queries. You're grasping handles.",
            examples=["self status", "self.status", "self.soul.reflect"],
            try_it="self status",
            next_topics=["composition", "aspects"],
        )

    @classmethod
    def for_composition(cls) -> "MicroLesson":
        """Lesson on path composition."""
        return cls(
            topic="composition",
            title="Composing Paths with >>",
            context="any",
            explanation="The >> operator composes paths into pipelines:\n"
            "  - 'a >> b' runs a, then b with the result\n"
            "  - You can chain multiple: 'a >> b >> c'\n"
            "Composition over construction - this is the heart of AGENTESE.",
            examples=["self.status >> concept.count", "world.agents >> time.trace"],
            try_it="self.status >> concept.count",
            next_topics=["observers", "aspects"],
        )

    @classmethod
    def for_observers(cls) -> "MicroLesson":
        """Lesson on observer/umwelt."""
        return cls(
            topic="observers",
            title="Observer Context (Umwelt)",
            context="any",
            explanation="Your observer archetype affects what you see:\n"
            "  - explorer: Sees pedagogical affordances\n"
            "  - developer: Sees technical affordances\n"
            "  - architect: Sees structural affordances\n"
            "  - admin: Sees all affordances\n"
            "Use /observer to check, /observer <name> to switch.",
            examples=["/observer", "/observer developer", "/observers"],
            try_it="/observer",
            next_topics=["composition", "void_context"],
        )

    @classmethod
    def for_void(cls) -> "MicroLesson":
        """Lesson on the void context (advanced)."""
        return cls(
            topic="void_context",
            title="The Void: Entropy and the Accursed Share",
            context="void",
            explanation="The void is where entropy lives:\n"
            "  - entropy.sip: Draw randomness\n"
            "  - shadow.project: Jungian shadow work\n"
            "  - serendipity: Request tangents\n"
            "  - gratitude (tithe): Return thanks\n"
            "'Everything is slop or comes from slop.'",
            examples=["void", "entropy sip", "void.shadow.project"],
            try_it="void",
            next_topics=["composition", "time_context"],
        )


# =============================================================================
# Fluency Tracker
# =============================================================================


@dataclass
class FluencyTracker:
    """
    Tracks user's demonstrated skills and overall fluency.

    Observes REPL interactions and records skill demonstrations.
    Persists across sessions.
    """

    demos: set[str] = field(default_factory=set)
    skills: dict[str, Skill] = field(default_factory=dict)
    session_count: int = 0
    total_commands: int = 0
    first_session: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_session: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        """Initialize skills from skill tree."""
        if not self.skills:
            for skill_id, skill_data in SKILL_TREE.items():
                self.skills[skill_id] = Skill(
                    id=skill_id,
                    name=skill_data["name"],
                    description=skill_data["description"],
                    prerequisites=skill_data["prerequisites"],
                    demos_required=skill_data["demos"],
                    threshold=skill_data["threshold"],
                )

    def record_demo(self, demo: str) -> list[str]:
        """
        Record a skill demonstration.

        Returns list of newly mastered skills.
        """
        if demo in self.demos:
            return []

        self.demos.add(demo)
        newly_mastered: list[str] = []

        # Update all skills that use this demo
        for skill in self.skills.values():
            if demo in skill.demos_required:
                skill.demos_completed.add(demo)
                if skill.is_mastered and skill.id not in [s for s in newly_mastered]:
                    # Check if just became mastered
                    prev_count = len(skill.demos_completed) - 1
                    if prev_count < skill.threshold:
                        newly_mastered.append(skill.id)

        return newly_mastered

    def record_command(self, command: str, context: list[str]) -> list[str]:
        """
        Record a command and return any newly mastered skills.

        Analyzes the command to determine what skills it demonstrates.
        """
        self.total_commands += 1
        newly_mastered = []

        cmd_lower = command.lower().strip()
        _ = ".".join(context) if context else "root"  # reserved for future use

        # Navigation demos
        if cmd_lower in ("self", "world", "concept", "void", "time"):
            newly_mastered.extend(self.record_demo(f"entered_{cmd_lower}"))

        if cmd_lower == "..":
            newly_mastered.extend(self.record_demo("used_dotdot"))

        if cmd_lower == "/":
            newly_mastered.extend(self.record_demo("used_slash"))

        # Introspection demos
        if cmd_lower == "?":
            newly_mastered.extend(self.record_demo("used_question"))

        if cmd_lower == "??":
            newly_mastered.extend(self.record_demo("used_questionquestion"))

        # Invocation demos
        if " " in cmd_lower or "." in cmd_lower:
            if not cmd_lower.startswith("/") and cmd_lower not in (".", ".."):
                newly_mastered.extend(self.record_demo("invoked_path"))
                if cmd_lower.count(".") >= 2 or cmd_lower.count(" ") >= 2:
                    newly_mastered.extend(self.record_demo("invoked_aspect"))

        # Composition demos
        if ">>" in cmd_lower:
            newly_mastered.extend(self.record_demo("used_pipeline"))
            if cmd_lower.count(">>") >= 2:
                newly_mastered.extend(self.record_demo("used_multi_pipeline"))

        # Observer demos
        if cmd_lower == "/observer":
            newly_mastered.extend(self.record_demo("checked_observer"))

        if cmd_lower.startswith("/observer ") and len(cmd_lower.split()) > 1:
            newly_mastered.extend(self.record_demo("switched_observer"))

        # Context mastery demos
        if context and context[0] == "self":
            if len(context) > 1:
                if context[1] == "status":
                    newly_mastered.extend(self.record_demo("explored_self_status"))
                elif context[1] == "soul":
                    newly_mastered.extend(self.record_demo("explored_self_soul"))
                elif context[1] == "memory":
                    newly_mastered.extend(self.record_demo("explored_self_memory"))

        if context and context[0] == "void":
            if len(context) > 1:
                if context[1] == "entropy":
                    newly_mastered.extend(self.record_demo("explored_void_entropy"))
                elif context[1] == "shadow":
                    newly_mastered.extend(self.record_demo("explored_void_shadow"))
            if "sip" in cmd_lower:
                newly_mastered.extend(self.record_demo("used_sip"))

        return list(set(newly_mastered))

    @property
    def level(self) -> FluencyLevel:
        """Calculate overall fluency level."""
        mastered = sum(1 for s in self.skills.values() if s.is_mastered)
        total = len(self.skills)
        ratio = mastered / total if total > 0 else 0

        if ratio < 0.2:
            return FluencyLevel.NOVICE
        elif ratio < 0.5:
            return FluencyLevel.BEGINNER
        elif ratio < 0.8:
            return FluencyLevel.INTERMEDIATE
        else:
            return FluencyLevel.FLUENT

    @property
    def mastered_skills(self) -> list[str]:
        """List of mastered skill IDs."""
        return [s.id for s in self.skills.values() if s.is_mastered]

    @property
    def available_skills(self) -> list[str]:
        """Skills whose prerequisites are met but not yet mastered."""
        mastered = set(self.mastered_skills)
        available = []
        for skill in self.skills.values():
            if skill.is_mastered:
                continue
            if all(p in mastered for p in skill.prerequisites):
                available.append(skill.id)
        return available

    def next_skill(self) -> str | None:
        """Suggest the next skill to learn (follows beginner path if applicable)."""
        mastered = set(self.mastered_skills)

        # First, try to follow beginner path
        for skill_id in BEGINNER_PATH:
            if skill_id not in mastered:
                skill = self.skills.get(skill_id)
                if skill and all(p in mastered for p in skill.prerequisites):
                    return skill_id

        # Then, any available skill
        available = self.available_skills
        return available[0] if available else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "demos": list(self.demos),
            "session_count": self.session_count,
            "total_commands": self.total_commands,
            "first_session": self.first_session,
            "last_session": self.last_session,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FluencyTracker":
        """Deserialize from persistence."""
        tracker = cls(
            demos=set(data.get("demos", [])),
            session_count=data.get("session_count", 0),
            total_commands=data.get("total_commands", 0),
            first_session=data.get(
                "first_session", datetime.now(timezone.utc).isoformat()
            ),
            last_session=data.get(
                "last_session", datetime.now(timezone.utc).isoformat()
            ),
        )
        # Rebuild skill progress from demos
        for demo in tracker.demos:
            for skill in tracker.skills.values():
                if demo in skill.demos_required:
                    skill.demos_completed.add(demo)
        return tracker


# =============================================================================
# Adaptive Guide
# =============================================================================


@dataclass
class AdaptiveGuide:
    """
    The adaptive learning companion.

    Decides what to show and when based on:
    - User's current location in REPL
    - User's fluency level
    - What they seem to be trying to do
    """

    tracker: FluencyTracker
    enabled: bool = True
    hint_cooldown: int = 0  # Commands since last hint

    # Micro-lessons library (auto-constructed)
    _lessons: dict[str, MicroLesson] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize lesson library."""
        if not self._lessons:
            self._lessons = {
                "navigation": MicroLesson.for_navigation(),
                "introspection": MicroLesson.for_introspection(),
                "invocation": MicroLesson.for_invocation(),
                "composition": MicroLesson.for_composition(),
                "observers": MicroLesson.for_observers(),
                "void_context": MicroLesson.for_void(),
            }
            # Add context lessons
            for ctx in ("self", "world", "concept", "void", "time"):
                self._lessons[f"context_{ctx}"] = MicroLesson.for_context(ctx)

    def get_lesson(self, topic: str) -> MicroLesson | None:
        """Get a micro-lesson by topic, with natural aliasing."""
        # Direct match
        if topic in self._lessons:
            return self._lessons[topic]

        # Natural aliases: "self" → "context_self", "void" → "context_void"
        contexts = ("self", "world", "concept", "void", "time")
        if topic in contexts:
            return self._lessons.get(f"context_{topic}")

        # Common abbreviations and alternatives
        aliases: dict[str, str] = {
            "nav": "navigation",
            "intro": "introspection",
            "invoke": "invocation",
            "compose": "composition",
            "observer": "observers",
            "pipe": "composition",
            "pipeline": "composition",
            "pipelines": "composition",
            ">>": "composition",
        }
        if topic.lower() in aliases:
            return self._lessons.get(aliases[topic.lower()])

        return None

    def list_topics(self) -> list[str]:
        """List all available lesson topics, including natural aliases."""
        # Include both canonical names and natural aliases
        topics = set(self._lessons.keys())
        # Add natural context names
        for ctx in ("self", "world", "concept", "void", "time"):
            topics.add(ctx)
        return sorted(topics)

    def contextual_hint(
        self, context: list[str], last_error: bool = False
    ) -> str | None:
        """
        Generate a contextual hint based on current location and fluency.

        Returns None if no hint is appropriate.
        """
        # Respect cooldown
        if self.hint_cooldown > 0:
            self.hint_cooldown -= 1
            return None

        level = self.tracker.level
        context_str = context[0] if context else "root"

        # Novice: Always offer guidance
        if level == FluencyLevel.NOVICE:
            if not context:
                return (
                    "Hint: Type 'self' to begin exploring, or '?' to see all contexts."
                )
            elif (
                context_str == "self"
                and "introspect_basic" not in self.tracker.mastered_skills
            ):
                return "Hint: Type '?' to see what you can do here."
            elif context_str == "void":
                return "Hint: Try 'entropy sip' to draw from the Accursed Share."

        # Beginner: Occasional hints
        elif level == FluencyLevel.BEGINNER:
            if last_error:
                return (
                    "Hint: Type '?' for available commands, or '/learn' for guidance."
                )
            next_skill = self.tracker.next_skill()
            if next_skill and next_skill == "compose_basic":
                return "Hint: Try composing paths with >>. Example: self.status >> concept.count"

        # Intermediate+: Only hint on errors or request
        elif last_error:
            return "Stuck? Type '/learn' for suggestions or '/hint' for help."

        return None

    def welcome_message(self, context: list[str]) -> str:
        """Generate a personalized welcome based on fluency."""
        level = self.tracker.level

        if level == FluencyLevel.NOVICE:
            return (
                "Learning mode active. Type what feels natural - I'll help along the way.\n"
                "Start with: self, world, concept, void, or time\n"
                "Or type '/learn' for guidance."
            )
        elif level == FluencyLevel.BEGINNER:
            next_skill = self.tracker.next_skill()
            if next_skill:
                skill = self.tracker.skills.get(next_skill)
                if skill:
                    return f"Welcome back. Next up: {skill.name}. Type '/learn {next_skill}' to continue."
            return "Welcome back. Type '/learn' to see what's next."
        elif level == FluencyLevel.INTERMEDIATE:
            mastered = len(self.tracker.mastered_skills)
            total = len(self.tracker.skills)
            return f"Welcome back. {mastered}/{total} skills mastered. Type '/fluency' for details."
        else:
            return "Welcome back. You're fluent in AGENTESE. Learning mode is here if you need it."

    def on_command(
        self, command: str, context: list[str]
    ) -> tuple[list[str], str | None]:
        """
        Process a command and return (newly_mastered_skills, optional_message).
        """
        newly_mastered = self.tracker.record_command(command, context)

        message = None
        if newly_mastered:
            skill_names = [
                self.tracker.skills[s].name
                for s in newly_mastered
                if s in self.tracker.skills
            ]
            if skill_names:
                message = f"Skill unlocked: {', '.join(skill_names)}"

        return newly_mastered, message

    def suggest_next(self) -> str:
        """Suggest what to learn next."""
        level = self.tracker.level
        next_skill_id = self.tracker.next_skill()

        if next_skill_id:
            skill = self.tracker.skills.get(next_skill_id)
            if skill:
                lesson = self._lessons.get(next_skill_id) or self._lessons.get(
                    f"context_{next_skill_id.replace('nav_', '').replace('master_', '')}"
                )

                lines = [f"Next: {skill.name}"]
                lines.append(f"  {skill.description}")
                if lesson:
                    lines.append(f"  Try: {lesson.try_it}")
                lines.append(f"\n  Type '/learn {next_skill_id}' for full lesson.")
                return "\n".join(lines)

        if level == FluencyLevel.FLUENT:
            return (
                "You've mastered AGENTESE! Explore freely or type '/fluency' to review."
            )

        return "Type '?' to explore, or pick a topic: " + ", ".join(
            self.list_topics()[:5]
        )


# =============================================================================
# Persistence
# =============================================================================


def save_fluency(
    tracker: FluencyTracker,
    fluency_file: Path = DEFAULT_FLUENCY_FILE,
) -> bool:
    """Save fluency data to disk."""
    try:
        tracker.last_session = datetime.now(timezone.utc).isoformat()
        fluency_file.write_text(json.dumps(tracker.to_dict(), indent=2))
        return True
    except (OSError, PermissionError, TypeError):
        return False


def load_fluency(
    fluency_file: Path = DEFAULT_FLUENCY_FILE,
) -> FluencyTracker:
    """Load fluency data from disk, or create new tracker."""
    try:
        if fluency_file.exists():
            data = json.loads(fluency_file.read_text())
            tracker = FluencyTracker.from_dict(data)
            tracker.session_count += 1
            return tracker
    except (OSError, PermissionError, json.JSONDecodeError, TypeError, KeyError):
        pass
    return FluencyTracker(session_count=1)


def clear_fluency(fluency_file: Path = DEFAULT_FLUENCY_FILE) -> bool:
    """Clear fluency data (start fresh)."""
    try:
        if fluency_file.exists():
            fluency_file.unlink()
        return True
    except (OSError, PermissionError):
        return False


# =============================================================================
# Command Handlers (for REPL integration)
# =============================================================================

# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def handle_learn_command(guide: AdaptiveGuide, args: list[str]) -> str:
    """
    Handle /learn command.

    /learn          - Suggest what to learn next
    /learn <topic>  - Show lesson for topic
    /learn list     - List all topics
    """
    if not args or args[0] == "":
        return guide.suggest_next()

    if args[0] == "list":
        topics = guide.list_topics()
        lines = [f"{BOLD}Available topics:{RESET}"]
        for topic in topics:
            lesson = guide.get_lesson(topic)
            if lesson:
                lines.append(f"  {YELLOW}{topic:<20}{RESET} {lesson.title}")
        return "\n".join(lines)

    topic = args[0]
    lesson = guide.get_lesson(topic)

    if not lesson:
        # Try fuzzy matching
        topics = guide.list_topics()
        matches = [t for t in topics if topic.lower() in t.lower()]
        if matches:
            return f"Topic '{topic}' not found. Did you mean: {', '.join(matches[:3])}?"
        return f"Topic '{topic}' not found. Type '/learn list' to see all topics."

    # Render the lesson
    lines = [
        f"{BOLD}{lesson.title}{RESET}",
        "",
        lesson.explanation,
        "",
        f"{YELLOW}Examples:{RESET}",
    ]
    for ex in lesson.examples:
        lines.append(f"  {CYAN}{ex}{RESET}")
    lines.append("")
    lines.append(f"{GREEN}Try it:{RESET} {lesson.try_it}")

    if lesson.next_topics:
        lines.append("")
        lines.append(f"{GRAY}Related: {', '.join(lesson.next_topics)}{RESET}")

    return "\n".join(lines)


def handle_fluency_command(guide: AdaptiveGuide) -> str:
    """Handle /fluency command - show progress."""
    tracker = guide.tracker
    level = tracker.level

    lines = [
        f"{BOLD}AGENTESE Fluency{RESET}",
        "",
        f"Level: {YELLOW}{level.value.title()}{RESET}",
        f"Sessions: {tracker.session_count}",
        f"Commands: {tracker.total_commands}",
        "",
        f"{BOLD}Skills:{RESET}",
    ]

    # Group skills by mastery
    mastered = []
    in_progress = []
    locked = []

    mastered_set = set(tracker.mastered_skills)

    for skill_id, skill in tracker.skills.items():
        prereqs_met = all(p in mastered_set for p in skill.prerequisites)

        if skill.is_mastered:
            mastered.append(skill)
        elif prereqs_met:
            in_progress.append(skill)
        else:
            locked.append(skill)

    if mastered:
        lines.append(f"\n  {GREEN}Mastered:{RESET}")
        for s in mastered:
            lines.append(f"    {GREEN}✓{RESET} {s.name}")

    if in_progress:
        lines.append(f"\n  {YELLOW}In Progress:{RESET}")
        for s in in_progress:
            pct = int(s.progress * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            lines.append(f"    {bar} {pct}% {s.name}")

    if locked:
        lines.append(f"\n  {GRAY}Locked:{RESET}")
        for s in locked[:3]:  # Show only first 3 locked
            prereq_names = [
                tracker.skills[p].name for p in s.prerequisites if p in tracker.skills
            ]
            lines.append(
                f"    {GRAY}🔒 {s.name} (needs: {', '.join(prereq_names)}){RESET}"
            )
        if len(locked) > 3:
            lines.append(f"    {GRAY}... and {len(locked) - 3} more{RESET}")

    return "\n".join(lines)


def handle_hint_command(guide: AdaptiveGuide, context: list[str]) -> str:
    """Handle /hint command - get contextual hint."""
    hint = guide.contextual_hint(context, last_error=False)
    if hint:
        return hint

    # Force a hint based on context
    ctx = context[0] if context else "root"

    hints = {
        "root": "From root, enter a context: self, world, concept, void, or time",
        "self": "In self: try 'status', 'soul', or 'memory'. Use '?' to see all.",
        "world": "In world: try 'agents', 'daemon', or 'infra'. Use '?' to see all.",
        "concept": "In concept: try 'laws', 'dialectic', or 'principle'.",
        "void": "In void: try 'entropy sip', 'shadow', or 'serendipity'.",
        "time": "In time: try 'trace', 'past', 'future', or 'schedule'.",
    }

    return hints.get(ctx, "Type '?' to see available commands.")
