"""
Composition Trace: Unified witnessing for kg command compositions.

"The trace IS the proof. The narrative IS the composition."

Each composition creates a unified trace that links all step marks.
This provides:
- Causal narrative from start to finish
- Complete audit trail of all operations
- Ability to replay or debug compositions
- Evidence that composition succeeded/failed

Pattern: Append-Only History (Pattern 7 from crown-jewel-patterns.md)
    Traces are immutable once created. Steps append to the trace
    but never modify existing marks.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from services.witness.mark import Mark, MarkId, generate_mark_id
from services.witness.trace_store import MarkStore, get_mark_store

from .types import Composition, StepResult


@dataclass
class CompositionTrace:
    """
    Unified trace for a composition.

    The root mark records the composition start.
    Each step mark links to the root via CAUSES relation.
    Completion mark links to all step marks.
    """

    composition_id: str
    root_mark_id: MarkId
    step_mark_ids: list[MarkId]
    store: MarkStore

    def add_step_mark(self, mark_id: MarkId) -> None:
        """Record a step mark in this trace."""
        self.step_mark_ids.append(mark_id)

    def get_all_marks(self) -> list[Mark]:
        """Get all marks in this trace (root + steps)."""
        marks = []

        # Get root mark
        root = self.store.get(self.root_mark_id)
        if root:
            marks.append(root)

        # Get step marks
        for step_id in self.step_mark_ids:
            step_mark = self.store.get(step_id)
            if step_mark:
                marks.append(step_mark)

        return marks


async def start_composition_trace(composition: Composition) -> CompositionTrace:
    """
    Start a unified trace for a composition.

    Creates the root mark that all step marks will link to.
    """
    from services.witness.mark import LinkRelation, MarkLink, NPhase, Response, Stimulus

    store = get_mark_store()

    # Create root mark
    root_mark_id = generate_mark_id()
    root_mark = Mark(
        id=root_mark_id,
        timestamp=datetime.now(),
        origin="compose",
        stimulus=Stimulus(
            kind="composition_start",
            content=f"Starting composition: {composition.name or composition.id}",
        ),
        response=Response(
            kind="trace_root",
            content=f"Composition with {len(composition.steps)} steps",
            metadata={
                "composition_id": composition.id,
                "composition_name": composition.name,
                "step_count": len(composition.steps),
                "commands": [s.command for s in composition.steps],
            },
        ),
        phase=NPhase.ACT,
        tags=("compose", "trace_root"),
        links=(),  # Root has no parent
    )

    store.append(root_mark)

    # Update composition with trace ID
    composition.trace_id = str(root_mark_id)

    return CompositionTrace(
        composition_id=composition.id,
        root_mark_id=root_mark_id,
        step_mark_ids=[],
        store=store,
    )


async def record_step_execution(
    trace: CompositionTrace,
    step_index: int,
    command: str,
    result: StepResult,
) -> None:
    """
    Record execution of a step in the composition trace.

    Links the step's mark (if any) to the composition root.
    If the step didn't create a mark, we create one for tracing.
    """
    from services.witness.mark import LinkRelation, MarkLink, NPhase, Response, Stimulus

    # If step already created a mark, just link it to root
    if result.mark_id:
        step_mark_id = MarkId(result.mark_id)
        trace.add_step_mark(step_mark_id)
        return

    # Otherwise, create a mark for this step
    step_mark_id = generate_mark_id()
    step_mark = Mark(
        id=step_mark_id,
        timestamp=datetime.now(),
        origin="compose",
        stimulus=Stimulus(
            kind="composition_step",
            content=f"Step {step_index}: {command}",
        ),
        response=Response(
            kind="step_result",
            content=result.output[:500] if result.success else result.error or "Failed",
            metadata={
                "composition_id": trace.composition_id,
                "step_index": step_index,
                "command": command,
                "success": result.success,
                "duration_ms": result.duration_ms,
                "skipped": result.skipped,
            },
        ),
        phase=NPhase.ACT,
        tags=("compose", "step", "success" if result.success else "failure"),
        links=(
            MarkLink(
                source=trace.root_mark_id,
                target=step_mark_id,
                relation=LinkRelation.CAUSES,
            ),
        ),
    )

    trace.store.append(step_mark)
    trace.add_step_mark(step_mark_id)
    result.mark_id = str(step_mark_id)


async def complete_composition_trace(
    trace: CompositionTrace,
    composition: Composition,
) -> None:
    """
    Complete a composition trace with a summary mark.

    The completion mark links to all step marks and provides
    a high-level summary of the composition outcome.
    """
    from services.witness.mark import LinkRelation, MarkLink, NPhase, Response, Stimulus

    completion_mark_id = generate_mark_id()
    completion_mark = Mark(
        id=completion_mark_id,
        timestamp=datetime.now(),
        origin="compose",
        stimulus=Stimulus(
            kind="composition_complete",
            content=f"Completed composition: {composition.name or composition.id}",
        ),
        response=Response(
            kind="completion",
            content=f"{composition.success_count}/{len(composition.steps)} steps succeeded",
            metadata={
                "composition_id": composition.id,
                "composition_name": composition.name,
                "status": composition.status.value,
                "success_count": composition.success_count,
                "failure_count": composition.failure_count,
                "skipped_count": composition.skipped_count,
                "duration_ms": composition.duration_ms,
            },
        ),
        phase=NPhase.ACT,
        tags=("compose", "completion", "success" if composition.all_succeeded else "failure"),
        links=(
            MarkLink(
                source=trace.root_mark_id,
                target=completion_mark_id,
                relation=LinkRelation.CONTINUES,
            ),
        ),
    )

    trace.store.append(completion_mark)
    trace.add_step_mark(completion_mark_id)
