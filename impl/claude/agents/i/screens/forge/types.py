"""
Type definitions for the Forge.

Defines component types, validation errors, cost estimates, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ComponentType(Enum):
    """Type of component in the pipeline."""

    AGENT = auto()
    PRIMITIVE = auto()
    FUNCTOR = auto()


@dataclass(frozen=True)
class ComponentSpec:
    """
    Specification for a composable component.

    This represents an agent, primitive, or functor that can be
    added to a pipeline.
    """

    id: str
    name: str
    component_type: ComponentType
    display_name: str
    input_type: str  # e.g., "str", "Document", "Any"
    output_type: str  # e.g., "str", "Summary", "Any"
    description: str
    stars: int = 3  # Maturity rating (1-5 stars)
    config_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineComponent:
    """
    A component instance in a pipeline.

    This is a concrete instance of a ComponentSpec with
    specific configuration.
    """

    spec: ComponentSpec
    config: dict[str, Any] = field(default_factory=dict)
    index: int = 0  # Position in pipeline


@dataclass
class ValidationError:
    """A validation error in the pipeline."""

    component_index: int
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class CostEstimate:
    """
    Estimated cost of running the pipeline.

    Tracks entropy, tokens, and latency.
    """

    entropy_per_turn: float = 0.0
    token_budget: int = 0
    estimated_latency_ms: float = 0.0


@dataclass
class SimulationResult:
    """Result of running a simulation."""

    success: bool
    output: Any
    error: str | None = None
    steps: list[StepResult] = field(default_factory=list)
    elapsed_ms: float = 0.0


@dataclass
class StepResult:
    """Result of a single step in simulation."""

    component_index: int
    component_name: str
    input: Any
    output: Any
    elapsed_ms: float = 0.0
    error: str | None = None
