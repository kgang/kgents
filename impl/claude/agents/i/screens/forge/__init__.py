"""
Forge subsystem - Agent creation and composition.

The Forge is where agents are built, simulated, refined, and exported.
It's a visual composition environment with JOY at its core.

Components:
- screen.py: Main ForgeScreen
- palette.py: Agent and primitive selection
- pipeline.py: Visual pipeline builder
- simulator.py: Test harness for composed pipelines
- exporter.py: Code generation for export
"""

from __future__ import annotations

from .exporter import CodeExporter
from .palette import AGENT_CATALOG, PRIMITIVE_CATALOG, AgentPalette
from .pipeline import PipelineBuilder
from .screen import ForgeScreen
from .simulator import SimulationRunner
from .types import (
    ComponentSpec,
    ComponentType,
    CostEstimate,
    PipelineComponent,
    SimulationResult,
    StepResult,
    ValidationError,
)

__all__ = [
    "AgentPalette",
    "AGENT_CATALOG",
    "CodeExporter",
    "ComponentSpec",
    "ComponentType",
    "CostEstimate",
    "ForgeScreen",
    "PipelineBuilder",
    "PipelineComponent",
    "PRIMITIVE_CATALOG",
    "SimulationResult",
    "SimulationRunner",
    "StepResult",
    "ValidationError",
]
