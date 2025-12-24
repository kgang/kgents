"""
Composition Service: Chain kg operations with unified witnessing.

"Every step leaves a mark. Every composition tells a story."

The Composition service enables:
- Sequential execution of kg subcommands
- Unified trace linking all step marks
- Dependency-aware execution
- Named compositions for reuse
- Early exit on failure (unless --continue)

Philosophy:
    A single kg command is atomic. A composition is molecular.
    The composition trace provides the causal narrative connecting
    all steps from stimulus to outcome.

Pattern: Container-Owns-Workflow (Pattern 1 from crown-jewel-patterns.md)
    CompositionExecutor orchestrates the steps, manages the trace,
    and coordinates with MarkStore for witnessing.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 5)
"""

from .executor import CompositionExecutor, execute_composition
from .store import CompositionStore, get_composition_store
from .trace import CompositionTrace, start_composition_trace
from .types import (
    Composition,
    CompositionStatus,
    CompositionStep,
    StepResult,
)

__all__ = [
    # Types
    "Composition",
    "CompositionStep",
    "StepResult",
    "CompositionStatus",
    # Executor
    "CompositionExecutor",
    "execute_composition",
    # Store
    "CompositionStore",
    "get_composition_store",
    # Trace
    "CompositionTrace",
    "start_composition_trace",
]
