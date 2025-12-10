"""
Flow Engine - The Composition Backbone for kgents CLI.

Flowfiles replace string-based composition ("a >> b >> c") with:
- Version controlled YAML files
- IDE-aware (YAML schema support)
- Testable
- Composable
- Jinja2 templating for variables

From docs/cli-integration-plan.md Part 4.
"""

from .types import (
    FlowStep,
    FlowVariable,
    FlowInput,
    FlowOutput,
    FlowHooks,
    FlowErrorHandling,
    Flowfile,
    FlowResult,
    StepResult,
    FlowStatus,
    StepStatus,
    FlowError,
    FlowValidationError,
    FlowExecutionError,
)
from .parser import (
    parse_flowfile,
    validate_flowfile,
    render_template,
)
from .engine import (
    FlowEngine,
    execute_flow,
)
from .commands import (
    cmd_flow,
)

__all__ = [
    # Types
    "FlowStep",
    "FlowVariable",
    "FlowInput",
    "FlowOutput",
    "FlowHooks",
    "FlowErrorHandling",
    "Flowfile",
    "FlowResult",
    "StepResult",
    "FlowStatus",
    "StepStatus",
    "FlowError",
    "FlowValidationError",
    "FlowExecutionError",
    # Parser
    "parse_flowfile",
    "validate_flowfile",
    "render_template",
    # Engine
    "FlowEngine",
    "execute_flow",
    # Commands
    "cmd_flow",
]
