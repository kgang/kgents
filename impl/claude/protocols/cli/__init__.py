"""
CLI Protocol Implementation - The Command Surface for kgents.

This module implements the CLI meta-architecture from spec/protocols/cli.md,
providing the membrane between human intention and agent action.

Key components:
- Core types: Command, Result, OutputFormat, Budget
- Mirror commands: observe, reflect, integrate, watch
- Membrane commands: sense, trace, map, touch, name, hold, release
- I-gent synergy: Garden views, status whisper, semantic glint

The CLI embodies all seven principles at the surface level.
"""

from .cli_types import (
    # Enums
    OutputFormat,
    OutputLevel,
    BudgetLevel,
    PersonaMode,
    ErrorSeverity,
    ErrorRecoverability,
    # Core types
    CommandResult,
    OutputEnvelope,
    ErrorInfo,
    BudgetStatus,
    # Context
    CLIContext,
)

from .mirror_cli import (
    MirrorCLI,
    mirror_observe,
    mirror_reflect,
    mirror_status,
)

from .membrane_cli import (
    MembraneCLI,
    membrane_observe,
    membrane_sense,
    membrane_trace,
)

from .igent_synergy import (
    StatusWhisper,
    SemanticGlint,
    GardenBridge,
)

__all__ = [
    # Enums
    "OutputFormat",
    "OutputLevel",
    "BudgetLevel",
    "PersonaMode",
    "ErrorSeverity",
    "ErrorRecoverability",
    # Core types
    "CommandResult",
    "OutputEnvelope",
    "ErrorInfo",
    "BudgetStatus",
    # Context
    "CLIContext",
    # Mirror CLI
    "MirrorCLI",
    "mirror_observe",
    "mirror_reflect",
    "mirror_status",
    # Membrane CLI
    "MembraneCLI",
    "membrane_observe",
    "membrane_sense",
    "membrane_trace",
    # I-gent synergy
    "StatusWhisper",
    "SemanticGlint",
    "GardenBridge",
]
