"""
Reflector - The Unified Runtime Surface.

The Reflector is the observer between Runtime and User.
It manages the "Space Between" - mediating how runtime events
reach different surfaces (CLI, TUI, web).

Public API:
    # Core types
    Reflector           - Protocol for all reflector implementations
    InvocationContext   - Rich context for command invocation
    PromptInfo          - Information for rendering the prompt
    PromptState         - Current state of the prompt

    # Events
    RuntimeEvent        - Base event class
    EventType           - Event type enumeration
    Invoker             - Who invoked a command
    command_start       - Factory for CommandStartEvent
    command_end         - Factory for CommandEndEvent
    agent_health        - Factory for AgentHealthEvent
    proposal_added      - Factory for ProposalAddedEvent

    # Implementations
    TerminalReflector   - CLI stdout + FD3 output
    HeadlessReflector   - Test-friendly in-memory capture

    # Factory functions
    create_terminal_reflector  - Create CLI reflector
    create_test_reflector      - Create test reflector
    create_invocation_context  - Create command context

Example:
    # CLI usage
    from protocols.cli.reflector import (
        TerminalReflector,
        create_invocation_context,
        command_start,
        command_end,
    )

    reflector = TerminalReflector()
    ctx = create_invocation_context("status", reflector=reflector)

    # Emit start event
    reflector.on_event(command_start("status"))

    # Handler does work...
    ctx.output(
        human="[CORTEX] OK HEALTHY",
        semantic={"health": "healthy"}
    )

    # Emit end event
    reflector.on_event(command_end("status", exit_code=0))

    # Testing usage
    from protocols.cli.reflector import (
        HeadlessReflector,
        create_invocation_context,
    )

    reflector = HeadlessReflector()
    ctx = create_invocation_context("status", reflector=reflector)

    # Run handler...
    ctx.output(human="test", semantic={"key": "value"})

    # Assert
    reflector.assert_human_contains("test")
    reflector.assert_semantic_has("key", "value")
"""

from .events import (
    AgentHealthEvent,
    AgentRegisteredEvent,
    AgentUnregisteredEvent,
    CommandEndEvent,
    CommandStartEvent,
    ErrorEvent,
    EventType,
    Invoker,
    PheromoneEvent,
    ProposalAddedEvent,
    ProposalResolvedEvent,
    RuntimeEvent,
    agent_health,
    agent_registered,
    command_end,
    command_start,
    error_event,
    proposal_added,
)
from .headless import HeadlessReflector, create_test_reflector
from .protocol import (
    BaseReflector,
    InvocationContext,
    PromptInfo,
    PromptState,
    Reflector,
    close_invocation_context,
    create_invocation_context,
)
from .terminal import (
    TerminalReflector,
    create_terminal_reflector,
    get_default_reflector,
)

__all__ = [
    # Protocol and base
    "Reflector",
    "BaseReflector",
    "InvocationContext",
    "PromptInfo",
    "PromptState",
    # Events
    "RuntimeEvent",
    "EventType",
    "Invoker",
    "CommandStartEvent",
    "CommandEndEvent",
    "AgentHealthEvent",
    "AgentRegisteredEvent",
    "AgentUnregisteredEvent",
    "ProposalAddedEvent",
    "ProposalResolvedEvent",
    "PheromoneEvent",
    "ErrorEvent",
    # Event factories
    "command_start",
    "command_end",
    "agent_health",
    "agent_registered",
    "proposal_added",
    "error_event",
    # Implementations
    "TerminalReflector",
    "HeadlessReflector",
    # Factory functions
    "create_terminal_reflector",
    "create_test_reflector",
    "create_invocation_context",
    "close_invocation_context",
    "get_default_reflector",
]
