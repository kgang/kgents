"""
N-Phase Prompt Compiler.

The meta-meta-prompt: generates N-Phase prompts from project definitions.

AGENTESE handle: concept.nphase.*

Usage:
    from impl.claude.protocols.nphase import compiler

    prompt = compiler.compile_from_yaml_file("project.yaml")
    print(prompt)
"""

from .compiler import NPhasePrompt, NPhasePromptCompiler, compiler
from .schema import (
    COMPRESSED_PHASES,
    PHASE_NAMES,
    Blocker,
    Checkpoint,
    Classification,
    Component,
    Decision,
    Effort,
    EntropyBudget,
    FileRef,
    Invariant,
    PhaseOverride,
    PhaseStatus,
    ProjectDefinition,
    ProjectScope,
    ValidationResult,
    Wave,
)
from .state import (
    CumulativeState,
    Handle,
    NPhaseStateUpdater,
    PhaseOutput,
    state_updater,
)

__all__ = [
    # Enums
    "Classification",
    "Effort",
    "PhaseStatus",
    # Schema types
    "ProjectScope",
    "Decision",
    "FileRef",
    "Invariant",
    "Blocker",
    "Component",
    "Wave",
    "Checkpoint",
    "EntropyBudget",
    "PhaseOverride",
    "ProjectDefinition",
    "ValidationResult",
    # Constants
    "PHASE_NAMES",
    "COMPRESSED_PHASES",
    # Compiler
    "NPhasePromptCompiler",
    "NPhasePrompt",
    "compiler",
    # State
    "NPhaseStateUpdater",
    "CumulativeState",
    "PhaseOutput",
    "Handle",
    "state_updater",
]
