"""
Tool Base Types: Categorical Morphisms for Tool Infrastructure.

Tools are agents with contracts. This module defines the base protocol
that all tools must implement, along with supporting types.

The Categorical Insight:
    Tool[A, B] is a morphism from A to B in the Agent category.
    Tools compose via >>:
        pipeline = read >> grep >> summarize
        result = await pipeline.invoke(input)

Category Laws (verified via BootstrapWitness):
    Identity: Id >> tool == tool == tool >> Id
    Associativity: (f >> g) >> h == f >> (g >> h)

See: spec/services/tooling.md §3.1
See: docs/skills/crown-jewel-patterns.md (Pattern 1: Container Owns Workflow)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from services.witness import TrustLevel

# Type variables for Tool[A, B]
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


# =============================================================================
# Tool Categories (from spec §3)
# =============================================================================


class ToolCategory(Enum):
    """
    Categories of tools in the U-gent infrastructure.

    Type I: Core Tools - File and search operations
    Type II: Wrappers - Functorial lifting (Traced, Cached, Retry)
    Type III: System - External system interaction (bash, web)
    Type IV: Orchestration - Workflow and task management
    """

    CORE = auto()  # ReadTool, WriteTool, EditTool, GlobTool, GrepTool
    WRAPPER = auto()  # TracedTool, CachedTool, RetryTool, SandboxedTool
    SYSTEM = auto()  # BashTool, WebFetchTool, WebSearchTool
    ORCHESTRATION = auto()  # TodoTool, ModeTool, PipelineTool


class ToolEffect(Enum):
    """
    Declared side-effects for tools.

    Every tool declares its effects for capability checking
    and trust gating.
    """

    READS = "reads"  # Reads from filesystem/external
    WRITES = "writes"  # Writes to filesystem/external
    DELETES = "deletes"  # Deletes files/resources
    CALLS = "calls"  # Calls external service (shell, network)
    SPAWNS = "spawns"  # Spawns processes
    BLOCKS = "blocks"  # Blocks waiting for input
    STREAMS = "streams"  # Produces streaming output

    @classmethod
    def reads(cls, resource: str) -> tuple["ToolEffect", str]:
        """Helper: READS(resource)."""
        return (cls.READS, resource)

    @classmethod
    def writes(cls, resource: str) -> tuple["ToolEffect", str]:
        """Helper: WRITES(resource)."""
        return (cls.WRITES, resource)

    @classmethod
    def calls(cls, service: str) -> tuple["ToolEffect", str]:
        """Helper: CALLS(service)."""
        return (cls.CALLS, service)

    @classmethod
    def spawns(cls, process: str) -> tuple["ToolEffect", str]:
        """Helper: SPAWNS(process)."""
        return (cls.SPAWNS, process)


# =============================================================================
# Tool Result and Error Types
# =============================================================================


@dataclass(frozen=True)
class ToolResult(Generic[B]):
    """
    Result of a tool invocation.

    Wraps the actual result with metadata about execution.
    """

    value: B
    duration_ms: float
    tool_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ToolError(Exception):
    """Base exception for tool errors."""

    def __init__(self, message: str, tool_name: str | None = None) -> None:
        super().__init__(message)
        self.tool_name = tool_name


class ToolTimeoutError(ToolError):
    """Tool execution timed out."""

    def __init__(self, message: str, tool_name: str | None = None, timeout_ms: int = 0) -> None:
        super().__init__(message, tool_name)
        self.timeout_ms = timeout_ms


class CausalityViolation(ToolError):
    """Tool invoked without required prerequisite (e.g., write without read)."""

    pass


class SafetyViolation(ToolError):
    """Tool invoked with unsafe parameters (e.g., dangerous bash command)."""

    pass


# =============================================================================
# Tool Protocol (Abstract Base)
# =============================================================================


class Tool(ABC, Generic[A, B]):
    """
    Abstract base for all tools.

    Tools are morphisms in the Agent category:
        Tool[A, B]: A → B

    Each tool has:
    - name: Unique identifier (e.g., "file.read")
    - category: Classification (CORE, WRAPPER, SYSTEM, ORCHESTRATION)
    - effects: Declared side-effects for trust gating
    - trust_required: Minimum trust level to invoke

    Tools compose via >>:
        pipeline = read_tool >> grep_tool >> summarize_tool

    Category Laws:
        Id >> f == f == f >> Id (Identity)
        (f >> g) >> h == f >> (g >> h) (Associativity)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier (e.g., 'file.read')."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        return ""

    @property
    def category(self) -> ToolCategory:
        """Tool category for classification."""
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        """Declared side-effects as (effect, resource) pairs."""
        return []

    @property
    def trust_required(self) -> int:
        """Minimum trust level (0-3) to invoke this tool."""
        return 0  # READ_ONLY by default

    @property
    def timeout_default_ms(self) -> int:
        """Default timeout in milliseconds."""
        return 120_000  # 2 minutes

    @property
    def cacheable(self) -> bool:
        """Whether results can be cached."""
        return False

    @property
    def streaming(self) -> bool:
        """Whether tool supports streaming output."""
        return False

    @abstractmethod
    async def invoke(self, request: A) -> B:
        """
        Execute the tool with the given request.

        Args:
            request: Input of type A

        Returns:
            Output of type B

        Raises:
            ToolError: On execution failure
            ToolTimeoutError: If execution exceeds timeout
            CausalityViolation: If causal prerequisites not met
            SafetyViolation: If request violates safety constraints
        """
        ...

    def __rshift__(self, other: "Tool[B, Any]") -> "ToolPipeline[A, Any]":
        """
        Compose tools via >> operator.

        Example:
            pipeline = read >> grep >> summarize
        """
        return ToolPipeline(steps=[self, other])

    def __repr__(self) -> str:
        return f"Tool({self.name})"


# =============================================================================
# Identity Tool (Category Law)
# =============================================================================


class IdentityTool(Tool[A, A]):
    """
    Identity morphism: Id[A] → A.

    Category Law:
        Id >> f == f == f >> Id

    Used in composition tests and as pipeline identity.
    """

    def __init__(self, name: str = "identity") -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Identity morphism (passthrough)"

    async def invoke(self, request: A) -> A:
        return request


# =============================================================================
# Tool Pipeline (Composition)
# =============================================================================


@dataclass
class ToolPipeline(Tool[A, B]):
    """
    Composed pipeline of tools.

    Implements the >> operator for tool composition:
        pipeline = read >> grep >> summarize

    Category Laws:
        - Associativity: (f >> g) >> h == f >> (g >> h)
        - Identity: Id >> f == f == f >> Id
    """

    steps: list[Tool[Any, Any]]

    @property
    def name(self) -> str:
        """Pipeline name is composition of step names."""
        return " >> ".join(t.name for t in self.steps)

    @property
    def description(self) -> str:
        return f"Pipeline of {len(self.steps)} steps"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        """Union of all step effects."""
        all_effects: list[tuple[ToolEffect, str]] = []
        for step in self.steps:
            all_effects.extend(step.effects)
        return all_effects

    @property
    def trust_required(self) -> int:
        """Maximum trust required across steps."""
        return max((step.trust_required for step in self.steps), default=0)

    async def invoke(self, request: A) -> B:
        """Execute pipeline sequentially."""
        result: Any = request
        for step in self.steps:
            result = await step.invoke(result)
        return cast(B, result)  # Safe: pipeline composition guarantees type flow

    def __rshift__(self, other: Tool[B, Any]) -> "ToolPipeline[A, Any]":
        """Extend pipeline with another tool."""
        return ToolPipeline(steps=[*self.steps, other])


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Tool",
    "ToolCategory",
    "ToolEffect",
    "ToolResult",
    "ToolError",
    "ToolTimeoutError",
    "CausalityViolation",
    "SafetyViolation",
    "IdentityTool",
    "ToolPipeline",
]
