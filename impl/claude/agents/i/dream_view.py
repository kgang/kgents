"""
DreamReportRenderer: I-gent Rendering of Dream Reports and Morning Briefings.

Provides ASCII visualization of:
- REM cycle phases and progress
- Dream reports with timing and statistics
- Morning briefing (questions accumulated during dreaming)
- Schema neurogenesis proposals

Design principles:
1. Human-readable ASCII output
2. Progressive disclosure (compact to detailed)
3. Actionable morning briefing format
4. Clear phase transitions

From the implementation plan:
> "I-gent rendering of dream reports and morning briefings"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class DreamPhase(Enum):
    """Phases of the dream cycle."""

    AWAKE = "awake"
    ENTERING_REM = "entering_rem"
    REM_CONSOLIDATION = "rem_consolidation"
    REM_MAINTENANCE = "rem_maintenance"
    REM_REFLECTION = "rem_reflection"
    WAKING = "waking"
    INTERRUPTED = "interrupted"


@dataclass
class Question:
    """A question for the morning briefing."""

    question_id: str
    question_text: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_at: str = ""
    answered: bool = False
    answer: str | None = None


@dataclass
class MaintenanceChunk:
    """A chunk of maintenance work."""

    chunk_id: str
    task_type: str
    progress: float
    items_processed: int
    items_total: int
    started_at: str
    completed_at: str | None = None
    error: str | None = None


@dataclass
class MigrationProposal:
    """A schema migration proposal."""

    proposal_id: str
    table: str
    action: str
    column_name: str
    column_type: str
    confidence: float
    approved: bool = False
    rejected: bool = False
    reason: str | None = None


@runtime_checkable
class IDreamReport(Protocol):
    """Protocol for dream reports."""

    @property
    def dream_id(self) -> str: ...

    @property
    def started_at(self) -> str: ...

    @property
    def completed_at(self) -> str | None: ...

    @property
    def phase_reached(self) -> Any: ...

    @property
    def interrupted(self) -> bool: ...

    @property
    def interrupt_reason(self) -> str | None: ...

    @property
    def chunks_completed(self) -> int: ...

    @property
    def chunks_total(self) -> int: ...

    @property
    def questions_generated(self) -> int: ...


@dataclass
class SimpleDreamReport:
    """Simple dream report for testing."""

    dream_id: str
    started_at: str
    completed_at: str | None
    phase_reached: DreamPhase
    interrupted: bool = False
    interrupt_reason: str | None = None
    chunks_completed: int = 0
    chunks_total: int = 0
    questions_generated: int = 0
    duration_ms: float = 0.0
    maintenance_tasks: list[MaintenanceChunk] = field(default_factory=list)


# === Phase Rendering ===


def render_phase_indicator(phase: DreamPhase | str) -> str:
    """
    Render a phase indicator symbol.

    Args:
        phase: Current dream phase

    Returns:
        Single-char indicator
    """
    if isinstance(phase, str):
        phase_str = phase
    else:
        phase_str = phase.value

    indicators = {
        "awake": "○",  # Empty circle
        "entering_rem": "◐",  # Half circle
        "rem_consolidation": "●",  # Full circle
        "rem_maintenance": "◉",  # Circle with dot
        "rem_reflection": "◎",  # Double circle
        "waking": "◑",  # Half circle other way
        "interrupted": "⊗",  # Crossed circle
    }
    return indicators.get(phase_str, "?")


def render_phase_bar(phase: DreamPhase | str) -> str:
    """
    Render a phase progress bar.

    Args:
        phase: Current dream phase

    Returns:
        ASCII progress bar showing phase progression
    """
    if isinstance(phase, str):
        phase_str = phase
    else:
        phase_str = phase.value

    phases = [
        "awake",
        "entering_rem",
        "rem_consolidation",
        "rem_maintenance",
        "rem_reflection",
        "waking",
    ]

    if phase_str == "interrupted":
        # Find where we were interrupted (default to consolidation)
        return "[○──◐──!INTERRUPTED──────────────]"

    try:
        idx = phases.index(phase_str)
    except ValueError:
        idx = 0

    bar_parts = []
    for i, p in enumerate(phases):
        if i < idx:
            bar_parts.append("●")
        elif i == idx:
            bar_parts.append(render_phase_indicator(p))
        else:
            bar_parts.append("○")

    return "[" + "──".join(bar_parts) + "]"


# === Dream Report Rendering ===


def render_dream_report(
    report: IDreamReport | SimpleDreamReport | dict[str, Any],
) -> str:
    """
    Render a dream report as ASCII.

    Args:
        report: Dream report to render

    Returns:
        Multi-line ASCII visualization
    """
    # Handle dict input
    if isinstance(report, dict):
        dream_id = report.get("dream_id", "unknown")
        started_at = report.get("started_at", "")
        completed_at = report.get("completed_at")
        phase = report.get("phase_reached", "awake")
        interrupted = report.get("interrupted", False)
        interrupt_reason = report.get("interrupt_reason")
        chunks_completed = report.get("chunks_completed", 0)
        chunks_total = report.get("chunks_total", 0)
        questions = report.get("questions_generated", 0)
        duration_ms = report.get("duration_ms", 0.0)
    else:
        dream_id = report.dream_id
        started_at = report.started_at
        completed_at = report.completed_at
        phase = report.phase_reached
        interrupted = report.interrupted
        interrupt_reason = report.interrupt_reason if hasattr(report, "interrupt_reason") else None
        chunks_completed = report.chunks_completed
        chunks_total = report.chunks_total
        questions = report.questions_generated
        duration_ms = report.duration_ms if hasattr(report, "duration_ms") else 0.0

    lines = []

    # Header
    status = "INTERRUPTED" if interrupted else ("COMPLETE" if completed_at else "ACTIVE")
    lines.append(f"╔{'═' * 58}╗")
    lines.append(f"║ DREAM REPORT: {dream_id[:30]:<30} [{status:^10}] ║")
    lines.append(f"╠{'═' * 58}╣")

    # Phase progress
    phase_bar = render_phase_bar(phase)
    lines.append(f"║ Phase: {phase_bar:<50} ║")

    # Timing
    lines.append(f"║ Started: {started_at[:25]:<48} ║")
    if completed_at:
        lines.append(f"║ Completed: {completed_at[:25]:<46} ║")
    if duration_ms > 0:
        duration_str = f"{duration_ms:.1f}ms"
        if duration_ms > 1000:
            duration_str = f"{duration_ms / 1000:.2f}s"
        lines.append(f"║ Duration: {duration_str:<47} ║")

    # Progress
    if chunks_total > 0:
        progress = chunks_completed / chunks_total
        bar_width = 30
        filled = int(progress * bar_width)
        progress_bar = "█" * filled + "░" * (bar_width - filled)
        lines.append(f"║ Progress: [{progress_bar}] {progress:.0%}{'':>10} ║")
        lines.append(f"║ Chunks: {chunks_completed}/{chunks_total:<46} ║")

    # Questions generated
    if questions > 0:
        lines.append(f"║ Questions Generated: {questions:<36} ║")

    # Interruption
    if interrupted and interrupt_reason:
        lines.append(f"╟{'─' * 58}╢")
        lines.append(f"║ ⚠ INTERRUPTED: {interrupt_reason[:41]:<41} ║")

    lines.append(f"╚{'═' * 58}╝")

    return "\n".join(lines)


def render_dream_report_compact(
    report: IDreamReport | SimpleDreamReport | dict[str, Any],
) -> str:
    """
    Render a compact single-line dream report.

    Args:
        report: Dream report to render

    Returns:
        Single-line summary
    """
    # Handle dict input
    if isinstance(report, dict):
        phase = report.get("phase_reached", "awake")
        interrupted = report.get("interrupted", False)
        chunks_completed = report.get("chunks_completed", 0)
        chunks_total = report.get("chunks_total", 0)
        questions = report.get("questions_generated", 0)
    else:
        phase = report.phase_reached
        interrupted = report.interrupted
        chunks_completed = report.chunks_completed
        chunks_total = report.chunks_total
        questions = report.questions_generated

    phase_str = phase.value if hasattr(phase, "value") else str(phase)
    indicator = render_phase_indicator(phase)

    status = "!" if interrupted else "✓"
    progress = f"{chunks_completed}/{chunks_total}" if chunks_total > 0 else "-"

    return f"[{status}] {indicator} {phase_str} | Chunks: {progress} | Q: {questions}"


# === Morning Briefing Rendering ===


def render_morning_briefing(
    questions: list[Question] | list[dict[str, Any]],
    title: str = "MORNING BRIEFING",
) -> str:
    """
    Render morning briefing as interactive question list.

    Args:
        questions: List of questions
        title: Briefing title

    Returns:
        Multi-line ASCII briefing
    """
    if not questions:
        return f"╔{'═' * 50}╗\n║ {title:^48} ║\n╟{'─' * 50}╢\n║ No questions pending.{' ' * 27}║\n╚{'═' * 50}╝"

    lines = []
    lines.append(f"╔{'═' * 50}╗")
    lines.append(f"║ {title:^48} ║")
    lines.append(f"║ {len(questions)} question(s) to review{' ' * 24}║")
    lines.append(f"╠{'═' * 50}╣")

    for i, q in enumerate(questions, 1):
        # Handle dict input
        if isinstance(q, dict):
            text = q.get("question_text", "")
            priority = q.get("priority", 0)
            answered = q.get("answered", False)
            answer = q.get("answer")
        elif isinstance(q, Question):
            text = q.question_text
            priority = q.priority
            answered = q.answered
            answer = q.answer
        else:
            # Should not happen with proper types, but handle gracefully
            text = ""
            priority = 0
            answered = False
            answer = None

        # Priority indicator
        priority_str = "!" * min(3, max(1, priority)) if priority > 0 else " "

        # Status
        status = "✓" if answered else "○"

        # Question text (truncated)
        text_short = text[:40] + "..." if len(text) > 40 else text

        lines.append(f"║ {status} [{i}] {priority_str} {text_short:<41} ║")

        # Show answer if available
        if answered and answer:
            answer_short = answer[:38] + "..." if len(answer) > 38 else answer
            lines.append(f"║      → {answer_short:<43} ║")

    lines.append(f"╚{'═' * 50}╝")

    return "\n".join(lines)


def render_briefing_question(
    question: Question | dict[str, Any],
    number: int = 1,
) -> str:
    """
    Render a single question for interactive answering.

    Args:
        question: Question to render
        number: Question number

    Returns:
        Formatted question prompt
    """
    if isinstance(question, dict):
        text = question.get("question_text", "")
        context = question.get("context", {})
        priority = question.get("priority", 0)
    else:
        text = question.question_text
        context = question.context
        priority = question.priority

    lines = []

    # Priority banner
    if priority >= 3:
        lines.append("⚠️  HIGH PRIORITY QUESTION")
    elif priority >= 2:
        lines.append("📋 Medium Priority")

    # Question
    lines.append(f"\n  Question {number}:")
    lines.append(f"  {text}\n")

    # Context
    if context:
        lines.append("  Context:")
        for key, value in context.items():
            value_str = str(value)[:50]
            lines.append(f"    • {key}: {value_str}")

    lines.append("\n  Your answer: ")

    return "\n".join(lines)


# === Neurogenesis Rendering ===


def render_migration_proposals(
    proposals: list[MigrationProposal] | list[dict[str, Any]],
) -> str:
    """
    Render schema migration proposals.

    Args:
        proposals: List of migration proposals

    Returns:
        Multi-line ASCII proposal list
    """
    if not proposals:
        return "No pending migration proposals."

    lines = []
    lines.append(f"╔{'═' * 60}╗")
    lines.append(f"║ {'SCHEMA NEUROGENESIS PROPOSALS':^58} ║")
    lines.append(f"║ {len(proposals)} proposal(s) awaiting review{' ' * 26}║")
    lines.append(f"╠{'═' * 60}╣")

    for i, p in enumerate(proposals, 1):
        if isinstance(p, dict):
            pid = p.get("proposal_id", "?")[:8]
            table = p.get("table", "?")
            action = p.get("action", "?")
            column = p.get("column_name", "?")
            col_type = p.get("column_type", "?")
            confidence = p.get("confidence", 0.0)
            approved = p.get("approved", False)
            rejected = p.get("rejected", False)
        elif isinstance(p, MigrationProposal):
            pid = p.proposal_id[:8]
            table = p.table
            action = p.action
            column = p.column_name
            col_type = p.column_type
            confidence = p.confidence
            approved = p.approved
            rejected = p.rejected
        else:
            # Should not happen with proper types, but handle gracefully
            pid = "?"
            table = "?"
            action = "?"
            column = "?"
            col_type = "?"
            confidence = 0.0
            approved = False
            rejected = False

        # Status
        if approved:
            status = "✓"
        elif rejected:
            status = "✗"
        else:
            status = "○"

        # Confidence bar
        bar_width = 10
        filled = int(confidence * bar_width)
        conf_bar = "█" * filled + "░" * (bar_width - filled)

        lines.append(f"║ {status} [{i}] {pid}...{' ' * 44}║")
        lines.append(f"║      Table: {table:<46}║")
        lines.append(f"║      Action: {action} {column} ({col_type}){' ' * 20}║")
        lines.append(f"║      Confidence: [{conf_bar}] {confidence:.0%}{' ' * 21}║")

        if i < len(proposals):
            lines.append(f"╟{'─' * 60}╢")

    lines.append(f"╚{'═' * 60}╝")

    return "\n".join(lines)


def render_migration_sql(proposal: MigrationProposal | dict[str, Any]) -> str:
    """
    Render the SQL for a migration proposal.

    Args:
        proposal: Migration proposal

    Returns:
        SQL statement string
    """
    if isinstance(proposal, dict):
        table = proposal.get("table", "?")
        action = proposal.get("action", "?")
        column = proposal.get("column_name", "?")
        col_type = proposal.get("column_type", "TEXT")
    else:
        table = proposal.table
        action = proposal.action
        column = proposal.column_name
        col_type = proposal.column_type

    if action == "add_column":
        return f"ALTER TABLE {table} ADD COLUMN {column} {col_type};"
    elif action == "drop_column":
        return f"ALTER TABLE {table} DROP COLUMN {column};"
    elif action == "create_index":
        return f"CREATE INDEX idx_{table}_{column} ON {table}({column});"
    else:
        return f"-- Unknown action: {action}"


# === Factory Functions ===


def create_mock_dream_report(
    phase: DreamPhase = DreamPhase.REM_CONSOLIDATION,
    interrupted: bool = False,
    chunks_completed: int = 50,
    chunks_total: int = 100,
) -> SimpleDreamReport:
    """
    Create a mock dream report for testing.

    Args:
        phase: Dream phase
        interrupted: Whether interrupted
        chunks_completed: Chunks completed
        chunks_total: Total chunks

    Returns:
        SimpleDreamReport for testing
    """
    return SimpleDreamReport(
        dream_id=f"dream-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        started_at=datetime.now().isoformat(),
        completed_at=None if interrupted else datetime.now().isoformat(),
        phase_reached=phase,
        interrupted=interrupted,
        interrupt_reason="High-surprise signal detected" if interrupted else None,
        chunks_completed=chunks_completed,
        chunks_total=chunks_total,
        questions_generated=3,
        duration_ms=1500.0,
    )


def create_mock_questions(count: int = 3) -> list[Question]:
    """
    Create mock questions for testing.

    Args:
        count: Number of questions

    Returns:
        List of mock Questions
    """
    questions = [
        Question(
            question_id="q-001",
            question_text="What category should this memory cluster be assigned to?",
            context={"cluster_id": "cluster-42", "memories": 15},
            priority=2,
            created_at=datetime.now().isoformat(),
        ),
        Question(
            question_id="q-002",
            question_text="Is this pattern intentional or should it be normalized?",
            context={"pattern": "user_*.json", "occurrences": 234},
            priority=1,
            created_at=datetime.now().isoformat(),
        ),
        Question(
            question_id="q-003",
            question_text="Should these duplicate memories be merged or kept separate?",
            context={"memory_a": "mem-001", "memory_b": "mem-002", "similarity": 0.95},
            priority=3,
            created_at=datetime.now().isoformat(),
        ),
    ]
    return questions[:count]
