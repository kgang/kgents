"""
Lucid Dreamer: Interruptible Maintenance for the Bicameral Engine.

The Lucid Dreamer runs maintenance tasks (re-indexing, compaction, etc.)
while remaining responsive to high-priority signals. It provides:
- Interruptible maintenance (yields to flashbulb signals)
- Morning Briefing queue (ambiguity resolution questions)
- REM cycle scheduling
- Chunked operations that check for interrupts

Design rationale:
- Maintenance at 3 AM blocks if user starts urgent session at 3:05 AM
- The Lucid Dreamer checks for interrupts between chunks
- High-surprise signals wake the system from dreaming

From the implementation plan:
> "The Lucid Dreamer doesn't just maintain—it reflects, questions, and proposes new structures."

Biological analogy:
- REM sleep: Active brain processing, memory consolidation
- Lucid dreaming: Awareness during dreams, ability to direct the experience
- Morning Briefing: Questions accumulated during sleep
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

from .hippocampus import FlushResult, Hippocampus, ICortex
from .synapse import Synapse


class DreamPhase(Enum):
    """Phases of the dream cycle."""

    AWAKE = "awake"
    ENTERING_REM = "entering_rem"
    REM_CONSOLIDATION = "rem_consolidation"
    REM_MAINTENANCE = "rem_maintenance"
    REM_REFLECTION = "rem_reflection"
    WAKING = "waking"
    INTERRUPTED = "interrupted"


class MaintenanceTaskType(Enum):
    """Types of maintenance tasks."""

    INDEX_REBUILD = "index_rebuild"
    VACUUM = "vacuum"
    COMPOST = "compost"
    GHOST_HEALING = "ghost_healing"
    STALENESS_CHECK = "staleness_check"
    SCHEMA_ANALYSIS = "schema_analysis"


@dataclass
class MaintenanceChunk:
    """A single chunk of maintenance work."""

    chunk_id: str
    task_type: MaintenanceTaskType
    progress: float  # 0.0 to 1.0
    items_processed: int
    items_total: int
    started_at: str
    completed_at: str | None = None
    error: str | None = None

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None or self.progress >= 1.0


@dataclass
class Question:
    """A question for the morning briefing."""

    question_id: str
    question_text: str
    context: dict[str, Any]
    priority: int = 0  # Higher = more important
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    answered: bool = False
    answer: str | None = None


@dataclass
class DreamReport:
    """Report of a completed dream cycle."""

    dream_id: str
    started_at: str
    completed_at: str | None
    phase_reached: DreamPhase
    interrupted: bool
    interrupt_reason: str | None
    chunks_processed: int
    total_chunks: int
    flush_result: FlushResult | None
    questions_generated: int
    proposed_migrations: list[dict[str, Any]]
    errors: list[str]

    @property
    def duration_seconds(self) -> float:
        """Duration of the dream cycle in seconds."""
        start = datetime.fromisoformat(self.started_at)
        end_str = self.completed_at or datetime.now().isoformat()
        end = datetime.fromisoformat(end_str)
        return (end - start).total_seconds()

    @property
    def completion_rate(self) -> float:
        """Percentage of maintenance completed."""
        if self.total_chunks == 0:
            return 1.0
        return self.chunks_processed / self.total_chunks


@dataclass
class DreamerConfig:
    """Configuration for the Lucid Dreamer."""

    # Interrupt checking
    interrupt_check_ms: int = 100  # How often to check for interrupts
    flashbulb_wakes: bool = True  # High-surprise signals wake the dreamer

    # REM cycle timing
    rem_interval_hours: float = 24.0  # How often to dream
    rem_start_time_utc: str = "03:00"  # When to start dreaming
    max_rem_duration_minutes: int = 30  # Max dream duration

    # Maintenance settings
    chunk_size: int = 100  # Items per maintenance chunk
    vacuum_threshold_mb: int = 10  # Min DB size for vacuum

    # Morning briefing
    max_questions: int = 10  # Max questions to accumulate
    min_question_priority: int = 0  # Filter low-priority questions

    # Schema analysis
    enable_neurogenesis: bool = True  # Allow schema suggestions

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DreamerConfig":
        """Create from configuration dict."""
        return cls(
            interrupt_check_ms=data.get("interrupt_check_ms", 100),
            flashbulb_wakes=data.get("flashbulb_wakes", True),
            rem_interval_hours=data.get("rem_interval_hours", 24.0),
            rem_start_time_utc=data.get("rem_start_time_utc", "03:00"),
            max_rem_duration_minutes=data.get("max_rem_duration_minutes", 30),
            chunk_size=data.get("chunk_size", 100),
            vacuum_threshold_mb=data.get("vacuum_threshold_mb", 10),
            max_questions=data.get("max_questions", 10),
            min_question_priority=data.get("min_question_priority", 0),
            enable_neurogenesis=data.get("enable_neurogenesis", True),
        )


class NightWatch:
    """
    Scheduler for REM cycles.

    Determines when the next dream should occur based on:
    - Configured interval and start time
    - System activity patterns
    - Manual triggers
    """

    def __init__(self, config: DreamerConfig):
        self._config = config
        self._last_rem: datetime | None = None
        self._next_rem: datetime | None = None
        self._schedule_next()

    def _schedule_next(self) -> None:
        """Schedule the next REM cycle."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Parse target time
        hour, minute = map(int, self._config.rem_start_time_utc.split(":"))

        # Next occurrence of target time
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        self._next_rem = target

    @property
    def next_rem(self) -> datetime | None:
        """When the next REM cycle is scheduled."""
        return self._next_rem

    @property
    def last_rem(self) -> datetime | None:
        """When the last REM cycle occurred."""
        return self._last_rem

    def should_dream(self) -> bool:
        """Check if it's time to dream."""
        if self._next_rem is None:
            return False
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return now >= self._next_rem

    def mark_complete(self) -> None:
        """Mark current REM cycle as complete."""
        self._last_rem = datetime.now(timezone.utc).replace(tzinfo=None)
        self._schedule_next()

    def trigger_now(self) -> None:
        """Trigger immediate REM cycle."""
        self._next_rem = datetime.now(timezone.utc).replace(tzinfo=None)

    def time_until_next(self) -> timedelta:
        """Time until next scheduled REM cycle."""
        if self._next_rem is None:
            return timedelta(hours=self._config.rem_interval_hours)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return max(timedelta(0), self._next_rem - now)


class LucidDreamer:
    """
    Interruptible maintenance with ambiguity resolution.

    The Lucid Dreamer runs maintenance tasks during "sleep" while
    remaining responsive to high-priority signals. It can be
    interrupted at any chunk boundary.

    Usage:
        dreamer = LucidDreamer(synapse, hippocampus)

        # Check if it's time to dream
        if dreamer.should_dream():
            report = await dreamer.rem_cycle()

        # Or trigger manually
        report = await dreamer.rem_cycle()

        # Get morning briefing questions
        questions = dreamer.morning_briefing
    """

    def __init__(
        self,
        synapse: Synapse,
        hippocampus: Hippocampus,
        cortex: ICortex | None = None,
        config: DreamerConfig | None = None,
        maintenance_tasks: list[Callable[..., Any]] | None = None,
    ):
        """
        Initialize the Lucid Dreamer.

        Args:
            synapse: For checking interrupts
            hippocampus: For memory consolidation
            cortex: Optional long-term storage
            config: Configuration options
            maintenance_tasks: Optional custom maintenance task functions
        """
        self._synapse = synapse
        self._hippocampus = hippocampus
        self._cortex = cortex
        self._config = config or DreamerConfig()

        # Night watch scheduler
        self._night_watch = NightWatch(self._config)

        # State
        self._phase = DreamPhase.AWAKE
        self._current_dream_id: str | None = None
        self._dream_history: list[DreamReport] = []

        # Morning briefing
        self._morning_briefing: list[Question] = []

        # Custom maintenance tasks
        self._maintenance_tasks = maintenance_tasks or []

        # Metrics
        self._total_dreams = 0
        self._total_interrupts = 0

    @property
    def phase(self) -> DreamPhase:
        """Current dream phase."""
        return self._phase

    @property
    def is_dreaming(self) -> bool:
        """Whether currently in a dream cycle."""
        return self._phase not in (DreamPhase.AWAKE, DreamPhase.INTERRUPTED)

    @property
    def morning_briefing(self) -> list[Question]:
        """Questions accumulated during dreaming."""
        return [q for q in self._morning_briefing if not q.answered]

    @property
    def night_watch(self) -> NightWatch:
        """Access to the scheduler."""
        return self._night_watch

    @property
    def dream_history(self) -> list[DreamReport]:
        """History of past dream cycles."""
        return self._dream_history.copy()

    def should_dream(self) -> bool:
        """Check if it's time for a REM cycle."""
        return self._night_watch.should_dream()

    def add_question(self, text: str, context: dict[str, Any], priority: int = 0) -> Question:
        """
        Add a question to the morning briefing.

        Args:
            text: The question text
            context: Related context/data
            priority: Question priority (higher = more important)

        Returns:
            The created question
        """
        question = Question(
            question_id=str(uuid4()),
            question_text=text,
            context=context,
            priority=priority,
        )

        # Maintain max questions limit
        self._morning_briefing.append(question)
        if len(self._morning_briefing) > self._config.max_questions:
            # Remove lowest priority
            self._morning_briefing.sort(key=lambda q: q.priority, reverse=True)
            self._morning_briefing = self._morning_briefing[: self._config.max_questions]

        return question

    def answer_question(self, question_id: str, answer: str) -> bool:
        """
        Answer a morning briefing question.

        Args:
            question_id: Question to answer
            answer: The answer

        Returns:
            True if answered, False if not found
        """
        for question in self._morning_briefing:
            if question.question_id == question_id:
                question.answered = True
                question.answer = answer
                return True
        return False

    def clear_answered(self) -> int:
        """Remove answered questions. Returns count removed."""
        before = len(self._morning_briefing)
        self._morning_briefing = [q for q in self._morning_briefing if not q.answered]
        return before - len(self._morning_briefing)

    async def rem_cycle(self) -> DreamReport:
        """
        Execute a REM cycle with interruptible maintenance.

        The cycle proceeds through phases:
        1. ENTERING_REM: Prepare for dreaming
        2. REM_CONSOLIDATION: Flush hippocampus to cortex
        3. REM_MAINTENANCE: Run maintenance tasks (interruptible)
        4. REM_REFLECTION: Analyze patterns, generate questions
        5. WAKING: Complete and report

        Can be interrupted at chunk boundaries by flashbulb signals.

        Returns:
            DreamReport with cycle details
        """
        self._current_dream_id = str(uuid4())
        start_time = datetime.now()

        report = DreamReport(
            dream_id=self._current_dream_id,
            started_at=start_time.isoformat(),
            completed_at=None,
            phase_reached=DreamPhase.AWAKE,
            interrupted=False,
            interrupt_reason=None,
            chunks_processed=0,
            total_chunks=0,
            flush_result=None,
            questions_generated=0,
            proposed_migrations=[],
            errors=[],
        )

        try:
            # Phase 1: Entering REM
            self._phase = DreamPhase.ENTERING_REM
            report.phase_reached = DreamPhase.ENTERING_REM

            if await self._should_interrupt():
                return self._finalize_interrupted(report, "Interrupt during entry")

            # Phase 2: Consolidation (flush hippocampus)
            self._phase = DreamPhase.REM_CONSOLIDATION
            report.phase_reached = DreamPhase.REM_CONSOLIDATION

            try:
                flush_result = await self._hippocampus.flush_to_cortex(self._cortex)
                report.flush_result = flush_result
            except Exception as e:
                report.errors.append(f"Consolidation error: {e}")

            if await self._should_interrupt():
                return self._finalize_interrupted(report, "Interrupt during consolidation")

            # Phase 3: Maintenance (interruptible)
            self._phase = DreamPhase.REM_MAINTENANCE
            report.phase_reached = DreamPhase.REM_MAINTENANCE

            maintenance_result = await self._run_maintenance(report)
            if maintenance_result.interrupted:
                return maintenance_result

            # Phase 4: Reflection
            self._phase = DreamPhase.REM_REFLECTION
            report.phase_reached = DreamPhase.REM_REFLECTION

            reflection_result = await self._run_reflection(report)
            if reflection_result.interrupted:
                return reflection_result

            # Phase 5: Waking
            self._phase = DreamPhase.WAKING
            report.phase_reached = DreamPhase.WAKING
            report.completed_at = datetime.now().isoformat()

            self._total_dreams += 1
            self._night_watch.mark_complete()

        finally:
            self._phase = DreamPhase.AWAKE
            self._dream_history.append(report)
            self._current_dream_id = None

        return report

    async def _should_interrupt(self) -> bool:
        """Check if we should interrupt the dream."""
        if not self._config.flashbulb_wakes:
            return False

        # Check synapse for high-surprise signals
        return self._synapse.has_flashbulb_pending(window_ms=self._config.interrupt_check_ms)

    def _finalize_interrupted(self, report: DreamReport, reason: str) -> DreamReport:
        """Finalize an interrupted dream report."""
        report.interrupted = True
        report.interrupt_reason = reason
        report.phase_reached = DreamPhase.INTERRUPTED
        report.completed_at = datetime.now().isoformat()
        self._total_interrupts += 1
        return report

    async def _run_maintenance(self, report: DreamReport) -> DreamReport:
        """Run maintenance tasks with interrupt checking."""
        # Count total chunks for all tasks
        task_chunks = self._get_maintenance_chunks()
        report.total_chunks = len(task_chunks)

        for chunk in task_chunks:
            # Check for interrupt before each chunk
            if await self._should_interrupt():
                return self._finalize_interrupted(report, "Interrupt during maintenance")

            # Process chunk
            try:
                await self._process_chunk(chunk)
                report.chunks_processed += 1
            except Exception as e:
                report.errors.append(f"Chunk {chunk.chunk_id} error: {e}")

            # Small delay to allow interrupt checking
            await asyncio.sleep(self._config.interrupt_check_ms / 1000.0)

        return report

    def _get_maintenance_chunks(self) -> list[MaintenanceChunk]:
        """Get list of maintenance chunks to process."""
        chunks = []

        # Default maintenance tasks
        default_tasks = [
            (MaintenanceTaskType.GHOST_HEALING, 1),
            (MaintenanceTaskType.STALENESS_CHECK, 1),
        ]

        if self._config.enable_neurogenesis:
            default_tasks.append((MaintenanceTaskType.SCHEMA_ANALYSIS, 1))

        for task_type, count in default_tasks:
            for i in range(count):
                chunks.append(
                    MaintenanceChunk(
                        chunk_id=f"{task_type.value}_{i}",
                        task_type=task_type,
                        progress=0.0,
                        items_processed=0,
                        items_total=self._config.chunk_size,
                        started_at=datetime.now().isoformat(),
                    )
                )

        return chunks

    async def _process_chunk(self, chunk: MaintenanceChunk) -> None:
        """Process a single maintenance chunk."""
        # Simulate work (in production, this would do actual maintenance)
        chunk.progress = 1.0
        chunk.items_processed = chunk.items_total
        chunk.completed_at = datetime.now().isoformat()

        # Run any custom maintenance tasks
        for task in self._maintenance_tasks:
            try:
                if asyncio.iscoroutinefunction(task):
                    await task(chunk)
                else:
                    task(chunk)
            except Exception:
                pass  # Don't fail on custom task errors

    async def _run_reflection(self, report: DreamReport) -> DreamReport:
        """Run reflection phase to generate questions and analyze patterns."""
        # Check for interrupt
        if await self._should_interrupt():
            return self._finalize_interrupted(report, "Interrupt during reflection")

        # Generate questions based on accumulated data
        questions = self._generate_questions()
        for q_text, q_context, q_priority in questions:
            self.add_question(q_text, q_context, q_priority)
            report.questions_generated += 1

        return report

    def _generate_questions(self) -> list[tuple[str, dict[str, Any], int]]:
        """Generate questions for the morning briefing."""
        questions = []

        # Example: Check for anomalies in signal patterns
        stats = self._synapse.surprise_stats()
        if stats.get("surprise_std", 0) > 0.3:
            questions.append(
                (
                    "High variance in signal surprise detected. Should we adjust thresholds?",
                    {"current_stats": stats},
                    1,
                )
            )

        # Example: Check for epoch accumulation
        if len(self._hippocampus.epochs) > 10:
            epoch_context: dict[str, Any] = {"epoch_count": float(len(self._hippocampus.epochs))}
            questions.append(
                (
                    f"You have {len(self._hippocampus.epochs)} memory epochs. Should we consolidate?",
                    epoch_context,
                    2,
                )
            )

        return questions

    def trigger_dream_now(self) -> None:
        """Trigger an immediate REM cycle."""
        self._night_watch.trigger_now()

    def stats(self) -> dict[str, Any]:
        """Get dreamer statistics."""
        return {
            "phase": self._phase.value,
            "is_dreaming": self.is_dreaming,
            "total_dreams": self._total_dreams,
            "total_interrupts": self._total_interrupts,
            "interrupt_rate": (
                self._total_interrupts / self._total_dreams if self._total_dreams > 0 else 0.0
            ),
            "pending_questions": len(self.morning_briefing),
            "next_rem": (
                self._night_watch.next_rem.isoformat() if self._night_watch.next_rem else None
            ),
            "time_until_next": str(self._night_watch.time_until_next()),
        }


# Factory function
def create_lucid_dreamer(
    synapse: Synapse,
    hippocampus: Hippocampus,
    cortex: ICortex | None = None,
    config_dict: dict[str, Any] | None = None,
) -> LucidDreamer:
    """
    Create a Lucid Dreamer with optional configuration.

    Args:
        synapse: For interrupt checking
        hippocampus: For memory consolidation
        cortex: Optional long-term storage
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured LucidDreamer
    """
    config = DreamerConfig.from_dict(config_dict) if config_dict else DreamerConfig()
    return LucidDreamer(
        synapse=synapse,
        hippocampus=hippocampus,
        cortex=cortex,
        config=config,
    )
