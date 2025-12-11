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

from .commands import (
    cmd_flow,
)
from .engine import (
    FlowEngine,
    execute_flow,
)
from .parser import (
    parse_flowfile,
    render_template,
    validate_flowfile,
)
from .types import (
    FlowError,
    FlowErrorHandling,
    FlowExecutionError,
    Flowfile,
    FlowHooks,
    FlowInput,
    FlowOutput,
    FlowResult,
    FlowStatus,
    FlowStep,
    FlowValidationError,
    FlowVariable,
    StepResult,
    StepStatus,
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
