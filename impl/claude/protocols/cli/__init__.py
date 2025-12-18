"""
CLI Protocol Implementation - The Command Surface for kgents.

This module implements the CLI meta-architecture from spec/protocols/cli.md,
providing the membrane between human intention and agent action.

Key components:
- Core types: Command, Result, OutputFormat, Budget
- Dimensions: 6-dimensional command space (Execution × Statefulness × Backend × Intent × Seriousness × Interactivity)
- Validation: Aspect registration validation
- Membrane commands: sense, trace, map, touch, name, hold, release
- I-gent synergy: Garden views, status whisper, semantic glint

The CLI embodies all seven principles at the surface level.
"""

from .cli_types import (
    BudgetLevel,
    BudgetStatus,
    # Context
    CLIContext,
    # Core types
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
    OutputEnvelope,
    # Enums
    OutputFormat,
    OutputLevel,
    PersonaMode,
)
from .dimensions import (
    # Constants
    DEFAULT_DIMENSIONS,
    PROTECTED_RESOURCES,
    # Dimension enums
    Backend,
    CommandDimensions,
    Execution,
    Intent,
    Interactivity,
    Seriousness,
    Statefulness,
    # Derivation functions
    derive_backend,
    derive_dimensions,
    derive_from_category,
    derive_intent,
    derive_interactivity,
    derive_seriousness,
)
from .membrane_cli import (
    MembraneCLI,
    membrane_observe,
    membrane_sense,
    membrane_trace,
)
from .projection import (
    CLIProjection,
    TerminalOutput,
    project_command,
    route_to_path,
)
from .validation import (
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    format_validation_report,
    validate_all_registrations,
    validate_aspect_registration,
)

__all__ = [
    # Enums
    "OutputFormat",
    "OutputLevel",
    "BudgetLevel",
    "PersonaMode",
    "ErrorSeverity",
    "ErrorRecoverability",
    # Dimension enums
    "Execution",
    "Statefulness",
    "Backend",
    "Intent",
    "Seriousness",
    "Interactivity",
    # Core types
    "CommandResult",
    "OutputEnvelope",
    "ErrorInfo",
    "BudgetStatus",
    "CommandDimensions",
    # Constants
    "DEFAULT_DIMENSIONS",
    "PROTECTED_RESOURCES",
    # Derivation functions
    "derive_from_category",
    "derive_backend",
    "derive_seriousness",
    "derive_intent",
    "derive_interactivity",
    "derive_dimensions",
    # Validation
    "ValidationSeverity",
    "ValidationError",
    "ValidationResult",
    "validate_aspect_registration",
    "validate_all_registrations",
    "format_validation_report",
    # Context
    "CLIContext",
    # Membrane CLI
    "MembraneCLI",
    "membrane_observe",
    "membrane_sense",
    "membrane_trace",
    # Projection
    "CLIProjection",
    "TerminalOutput",
    "project_command",
    "route_to_path",
]
