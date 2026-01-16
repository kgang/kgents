"""
CLI Command Dimension System - The 7-Dimensional Product Space.

Every CLI command exists in a 7-dimensional product space:

    CommandSpace = Execution x Statefulness x Backend x Intent x Seriousness x Interactivity x Context

This module implements the dimension types and derivation rules from spec/protocols/cli.md Part II.

The 7th dimension (ExecutionContext) captures WHERE the command is executing:
- CLI_DIRECT: Normal CLI invocation
- DAEMON_WORKER: Inside daemon thread pool
- DAEMON_MAIN: Daemon main thread
- REPL: Interactive mode (-i)

The Core Insight:
    "Just as screen density replaced scattered isMobile checks,
     command dimensions replace scattered behavioral checks."

Instead of:
    if is_async_command(name):
        result = await run_async(handler, args)

We have:
    dimensions = derive_dimensions(path)
    result = await cli_project(path, observer, dimensions)

This is Simplifying Isomorphism (AD-008) applied to CLI architecture.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese.affordances import (
        AspectCategory,
        AspectMetadata,
        DeclaredEffect,
        Effect,
    )


# === Dimension Enums ===


class Execution(Enum):
    """
    Execution dimension: how the command is invoked.

    Derived primarily from AspectCategory, but overridden if
    Effect.CALLS is present (always async for external calls).
    """

    SYNC = auto()  # Blocking call
    ASYNC = auto()  # Non-blocking, awaitable


class Statefulness(Enum):
    """
    Statefulness dimension: whether command accesses state.

    Derived from Effect.READS/WRITES presence.
    Determines whether state context management is needed.
    """

    STATELESS = auto()  # No state context
    STATEFUL = auto()  # Load/save state context


class Backend(Enum):
    """
    Backend dimension: what backs the command execution.

    Derived from Effect.CALLS target.
    Determines budget display and cost warnings.
    """

    PURE = auto()  # No external calls
    LLM = auto()  # LLM call (shows budget)
    EXTERNAL = auto()  # External API call


class Intent(Enum):
    """
    Intent dimension: the purpose of the command.

    Derived from AspectCategory:
    - INTROSPECTION -> instructional (explains, helps)
    - Everything else -> functional (does work)
    """

    FUNCTIONAL = auto()  # Does work
    INSTRUCTIONAL = auto()  # Explains, documents


class Seriousness(Enum):
    """
    Seriousness dimension: the gravity of the command.

    Derived from:
    - void.* context -> PLAYFUL (errors gentle, serendipity welcome)
    - Effect.FORCES present -> SENSITIVE (requires consent)
    - Protected resource writes -> SENSITIVE
    - Otherwise -> NEUTRAL
    """

    SENSITIVE = auto()  # Errors loud, confirmation required
    PLAYFUL = auto()  # Errors gentle, serendipity welcome
    NEUTRAL = auto()  # Standard behavior


class Interactivity(Enum):
    """
    Interactivity dimension: the interaction mode.

    Derived from aspect metadata flags:
    - streaming=True -> STREAMING
    - interactive=True -> INTERACTIVE
    - Otherwise -> ONESHOT
    """

    ONESHOT = auto()  # Single invocation
    STREAMING = auto()  # Continuous output
    INTERACTIVE = auto()  # REPL mode


class ExecutionContext(Enum):
    """
    Execution context dimension: WHERE the command is executing.

    This replaces scattered event loop and daemon detection checks
    with a single source of truth.

    Derived from environment variables and Python flags:
    - KGENTS_DAEMON_WORKER env -> DAEMON_WORKER
    - KGENTS_DAEMON_MAIN env -> DAEMON_MAIN
    - sys.flags.interactive or KGENTS_REPL env -> REPL
    - Otherwise -> CLI_DIRECT
    """

    CLI_DIRECT = auto()  # Normal CLI invocation
    DAEMON_WORKER = auto()  # Inside daemon thread pool
    DAEMON_MAIN = auto()  # Daemon main thread
    REPL = auto()  # Interactive mode (-i)


def derive_context() -> ExecutionContext:
    """
    Derive execution context from environment.

    Priority order:
    1. KGENTS_DAEMON_WORKER env -> DAEMON_WORKER
    2. KGENTS_DAEMON_MAIN env -> DAEMON_MAIN
    3. sys.flags.interactive or KGENTS_REPL env -> REPL
    4. Default -> CLI_DIRECT

    Returns:
        ExecutionContext enum value
    """
    if os.environ.get("KGENTS_DAEMON_WORKER"):
        return ExecutionContext.DAEMON_WORKER
    if os.environ.get("KGENTS_DAEMON_MAIN"):
        return ExecutionContext.DAEMON_MAIN
    if sys.flags.interactive or os.environ.get("KGENTS_REPL"):
        return ExecutionContext.REPL
    return ExecutionContext.CLI_DIRECT


# === The Composite Type ===


@dataclass
class CommandDimensions:
    """
    The 7-dimensional command space.

    This is the SINGLE SOURCE OF TRUTH for CLI behavior.
    No scattered conditionals should exist outside dimension derivation.

    The 7 dimensions:
    1. execution: SYNC or ASYNC
    2. statefulness: STATELESS or STATEFUL
    3. backend: PURE, LLM, or EXTERNAL
    4. intent: FUNCTIONAL or INSTRUCTIONAL
    5. seriousness: SENSITIVE, PLAYFUL, or NEUTRAL
    6. interactivity: ONESHOT, STREAMING, or INTERACTIVE
    7. context: CLI_DIRECT, DAEMON_WORKER, DAEMON_MAIN, or REPL

    Example:
        dimensions = derive_dimensions(path, meta)

        match dimensions.execution:
            case Execution.SYNC: result = logos.invoke_sync(...)
            case Execution.ASYNC: result = await logos.invoke(...)

        match dimensions.seriousness:
            case Seriousness.SENSITIVE: await request_consent(...)
            case Seriousness.PLAYFUL: error_style = ErrorStyle.GENTLE
            case Seriousness.NEUTRAL: pass

        if dimensions.in_daemon:
            # Handle daemon-specific behavior
            ...
    """

    execution: Execution
    statefulness: Statefulness
    backend: Backend
    intent: Intent
    seriousness: Seriousness
    interactivity: Interactivity
    context: ExecutionContext = field(default_factory=derive_context)

    def __str__(self) -> str:
        """Compact representation for tracing."""
        return "/".join(
            [
                self.execution.name,
                self.statefulness.name,
                self.backend.name,
                self.intent.name,
                self.seriousness.name,
                self.interactivity.name,
                self.context.name,
            ]
        )

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(
            (
                self.execution,
                self.statefulness,
                self.backend,
                self.intent,
                self.seriousness,
                self.interactivity,
                self.context,
            )
        )

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, CommandDimensions):
            return NotImplemented
        return (
            self.execution == other.execution
            and self.statefulness == other.statefulness
            and self.backend == other.backend
            and self.intent == other.intent
            and self.seriousness == other.seriousness
            and self.interactivity == other.interactivity
            and self.context == other.context
        )

    @property
    def is_async(self) -> bool:
        """Convenience: does this need async execution?"""
        return self.execution == Execution.ASYNC

    @property
    def needs_state(self) -> bool:
        """Convenience: does this need state context?"""
        return self.statefulness == Statefulness.STATEFUL

    @property
    def needs_budget_display(self) -> bool:
        """Convenience: should we show budget/cost?"""
        return self.backend == Backend.LLM

    @property
    def needs_confirmation(self) -> bool:
        """Convenience: should we request confirmation?"""
        return self.seriousness == Seriousness.SENSITIVE

    @property
    def is_streaming(self) -> bool:
        """Convenience: is this streaming output?"""
        return self.interactivity == Interactivity.STREAMING

    @property
    def is_repl_interactive(self) -> bool:
        """Convenience: does this enter REPL mode (Interactivity dimension)?"""
        return self.interactivity == Interactivity.INTERACTIVE

    @property
    def in_daemon(self) -> bool:
        """Convenience: is this running in a daemon context?"""
        return self.context in (ExecutionContext.DAEMON_WORKER, ExecutionContext.DAEMON_MAIN)

    @property
    def is_interactive(self) -> bool:
        """Convenience: is this running in interactive/REPL context?"""
        return self.context == ExecutionContext.REPL


# === Protected Resources ===

# Resources that trigger SENSITIVE seriousness when written
PROTECTED_RESOURCES: frozenset[str] = frozenset(
    {
        "soul",
        "memory",
        "forest",
        "config",
        "credentials",
        "garden",
        "crystal",
    }
)


# === Derivation Rules ===


def derive_from_category(
    category: "AspectCategory",
) -> tuple[Execution, Statefulness]:
    """
    Derive execution and statefulness from aspect category.

    From spec Part II, §2.2:
    | Category       | Execution | Statefulness | Typical Backend |
    |----------------|-----------|--------------|-----------------|
    | PERCEPTION     | sync      | stateless    | pure            |
    | MUTATION       | async     | stateful     | varies          |
    | GENERATION     | async     | stateful     | llm             |
    | COMPOSITION    | sync      | stateless    | pure            |
    | INTROSPECTION  | sync      | stateless    | pure            |
    | ENTROPY        | sync      | stateless    | pure            |

    Args:
        category: The AspectCategory from the aspect decorator

    Returns:
        Tuple of (Execution, Statefulness) base values
    """
    from protocols.agentese.affordances import AspectCategory

    CATEGORY_RULES: dict[AspectCategory, tuple[Execution, Statefulness]] = {
        AspectCategory.PERCEPTION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.MUTATION: (Execution.ASYNC, Statefulness.STATEFUL),
        AspectCategory.GENERATION: (Execution.ASYNC, Statefulness.STATEFUL),
        AspectCategory.COMPOSITION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.INTROSPECTION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.ENTROPY: (Execution.SYNC, Statefulness.STATELESS),
    }
    return CATEGORY_RULES.get(category, (Execution.SYNC, Statefulness.STATELESS))


def derive_backend(effects: list["DeclaredEffect | Effect"]) -> Backend:
    """
    Derive backend from declared effects.

    Rules:
    - Effect.CALLS("llm") or similar -> LLM
    - Effect.CALLS(<other>) -> EXTERNAL
    - No CALLS -> PURE

    Args:
        effects: List of declared effects from aspect metadata

    Returns:
        Backend dimension value
    """
    from protocols.agentese.affordances import DeclaredEffect, Effect

    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.CALLS:
                resource_lower = effect.resource.lower()
                if "llm" in resource_lower or "model" in resource_lower:
                    return Backend.LLM
                return Backend.EXTERNAL
    return Backend.PURE


def derive_seriousness(
    path: str,
    effects: list["DeclaredEffect | Effect"],
) -> Seriousness:
    """
    Derive seriousness from path context and effects.

    Rules (in priority order):
    1. void.* context -> PLAYFUL (errors gentle, serendipity welcome)
    2. FORCES effect present -> SENSITIVE (requires consent)
    3. WRITES to protected resource -> SENSITIVE
    4. Otherwise -> NEUTRAL

    Args:
        path: The AGENTESE path (e.g., "void.entropy.sip")
        effects: List of declared effects from aspect metadata

    Returns:
        Seriousness dimension value
    """
    from protocols.agentese.affordances import DeclaredEffect, Effect

    # Rule 1: void.* is playful
    if path.startswith("void."):
        return Seriousness.PLAYFUL

    # Rule 2: FORCES effect requires consent
    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.FORCES:
                return Seriousness.SENSITIVE

    # Rule 3: Writes to protected resources
    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.WRITES:
                if effect.resource.lower() in PROTECTED_RESOURCES:
                    return Seriousness.SENSITIVE

    return Seriousness.NEUTRAL


def derive_intent(
    category: "AspectCategory",
) -> Intent:
    """
    Derive intent from aspect category.

    Rules:
    - INTROSPECTION -> INSTRUCTIONAL (explains, documents)
    - Everything else -> FUNCTIONAL (does work)

    Args:
        category: The AspectCategory from the aspect decorator

    Returns:
        Intent dimension value
    """
    from protocols.agentese.affordances import AspectCategory

    if category == AspectCategory.INTROSPECTION:
        return Intent.INSTRUCTIONAL
    return Intent.FUNCTIONAL


def derive_interactivity(
    streaming: bool = False,
    interactive: bool = False,
) -> Interactivity:
    """
    Derive interactivity from aspect metadata flags.

    Rules:
    - interactive=True -> INTERACTIVE (REPL mode)
    - streaming=True -> STREAMING (continuous output)
    - Otherwise -> ONESHOT (single invocation)

    Args:
        streaming: Whether the aspect produces streaming output
        interactive: Whether the aspect runs in REPL mode

    Returns:
        Interactivity dimension value
    """
    if interactive:
        return Interactivity.INTERACTIVE
    if streaming:
        return Interactivity.STREAMING
    return Interactivity.ONESHOT


def derive_dimensions(
    path: str,
    meta: "AspectMetadata",
    context: ExecutionContext | None = None,
) -> CommandDimensions:
    """
    Derive complete dimensions from path and aspect metadata.

    This is the SINGLE SOURCE OF TRUTH for CLI behavior.
    No scattered conditionals should exist outside this derivation.

    The derivation process:
    1. Get base execution/statefulness from AspectCategory
    2. Override execution if CALLS effect present (always async)
    3. Override statefulness if READS/WRITES effects present
    4. Derive backend from CALLS effect target
    5. Derive intent from category
    6. Derive seriousness from path and effects
    7. Derive interactivity from metadata flags
    8. Derive context from environment (or use provided value)

    Args:
        path: The AGENTESE path (e.g., "self.memory.capture")
        meta: AspectMetadata from the @aspect decorator
        context: Optional override for execution context (defaults to derive_context())

    Returns:
        Complete CommandDimensions for the path

    Example:
        >>> from protocols.agentese.affordances import AspectMetadata, AspectCategory, Effect
        >>> meta = AspectMetadata(
        ...     category=AspectCategory.GENERATION,
        ...     effects=[Effect.WRITES("memory"), Effect.CALLS("llm")],
        ...     requires_archetype=(),
        ...     idempotent=False,
        ...     description="Capture a memory",
        ... )
        >>> dims = derive_dimensions("self.memory.capture", meta)
        >>> dims.execution == Execution.ASYNC
        True
        >>> dims.backend == Backend.LLM
        True
        >>> dims.context == ExecutionContext.CLI_DIRECT  # Default
        True
    """
    from protocols.agentese.affordances import DeclaredEffect, Effect

    # Step 1: Base from category
    execution, statefulness = derive_from_category(meta.category)

    # Step 2: Override execution if CALLS effect present
    has_calls = any(
        isinstance(e, DeclaredEffect) and e.effect == Effect.CALLS for e in meta.effects
    )
    if has_calls:
        execution = Execution.ASYNC

    # Step 3: Override statefulness if state effects present
    has_state_effect = any(
        isinstance(e, DeclaredEffect) and e.effect in (Effect.READS, Effect.WRITES)
        for e in meta.effects
    )
    if has_state_effect:
        statefulness = Statefulness.STATEFUL

    # Step 4-7: Derive remaining dimensions
    backend = derive_backend(meta.effects)
    intent = derive_intent(meta.category)
    seriousness = derive_seriousness(path, meta.effects)

    # Get interactivity from extended metadata (v3.2 fields)
    streaming = getattr(meta, "streaming", False)
    interactive_flag = getattr(meta, "interactive", False)
    interactivity = derive_interactivity(streaming, interactive_flag)

    # Step 8: Use provided context or derive from environment
    resolved_context = context if context is not None else derive_context()

    return CommandDimensions(
        execution=execution,
        statefulness=statefulness,
        backend=backend,
        intent=intent,
        seriousness=seriousness,
        interactivity=interactivity,
        context=resolved_context,
    )


# === Default Dimensions ===

# Default for undecorated paths (safest defaults)
DEFAULT_DIMENSIONS = CommandDimensions(
    execution=Execution.SYNC,
    statefulness=Statefulness.STATELESS,
    backend=Backend.PURE,
    intent=Intent.FUNCTIONAL,
    seriousness=Seriousness.NEUTRAL,
    interactivity=Interactivity.ONESHOT,
    context=ExecutionContext.CLI_DIRECT,
)


__all__ = [
    # Dimension enums
    "Execution",
    "Statefulness",
    "Backend",
    "Intent",
    "Seriousness",
    "Interactivity",
    "ExecutionContext",
    # Composite type
    "CommandDimensions",
    # Constants
    "PROTECTED_RESOURCES",
    "DEFAULT_DIMENSIONS",
    # Derivation functions
    "derive_from_category",
    "derive_backend",
    "derive_seriousness",
    "derive_intent",
    "derive_interactivity",
    "derive_context",
    "derive_dimensions",
]
