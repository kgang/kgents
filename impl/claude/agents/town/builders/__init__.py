"""
Builder's Workshop: Polynomial Agent Architecture.

The builder polynomial models software development as a state machine:
- IDLE: Ready for new tasks
- EXPLORING: Research phase (Scout's specialty)
- DESIGNING: Architecture phase (Sage's specialty)
- PROTOTYPING: Experimentation phase (Spark's specialty)
- REFINING: Polishing phase (Steady's specialty)
- INTEGRATING: Coordination phase (Sync's specialty)

The Five Core Builders:
- Sage: Architect ("Have we considered...")
- Spark: Experimenter ("What if we tried...")
- Steady: Craftsperson ("Let me polish this...")
- Scout: Researcher ("I found something...")
- Sync: Coordinator ("Here's the plan...")

See: plans/agent-town/builders-workshop.md
"""

# Polynomial
# Base class
from agents.town.builders.base import Builder

# Cosmotechnics
from agents.town.builders.cosmotechnics import (
    ARCHITECTURE,
    CRAFTSMANSHIP,
    DISCOVERY,
    EXPERIMENTATION,
    ORCHESTRATION,
)
from agents.town.builders.polynomial import (
    BUILDER_POLYNOMIAL,
    BuilderInput,
    BuilderOutput,
    BuilderPhase,
    builder_directions,
    builder_transition,
)

# Factory functions
from agents.town.builders.sage import SAGE_EIGENVECTORS, create_sage
from agents.town.builders.scout import SCOUT_EIGENVECTORS, create_scout
from agents.town.builders.spark import SPARK_EIGENVECTORS, create_spark
from agents.town.builders.steady import STEADY_EIGENVECTORS, create_steady
from agents.town.builders.sync import SYNC_EIGENVECTORS, create_sync

# Voice patterns
from agents.town.builders.voice import (
    SAGE_VOICE_PATTERNS,
    SCOUT_VOICE_PATTERNS,
    SPARK_VOICE_PATTERNS,
    STEADY_VOICE_PATTERNS,
    SYNC_VOICE_PATTERNS,
)

__all__ = [
    # Polynomial
    "BuilderPhase",
    "BuilderInput",
    "BuilderOutput",
    "builder_directions",
    "builder_transition",
    "BUILDER_POLYNOMIAL",
    # Base class
    "Builder",
    # Cosmotechnics
    "ARCHITECTURE",
    "CRAFTSMANSHIP",
    "DISCOVERY",
    "EXPERIMENTATION",
    "ORCHESTRATION",
    # Voice patterns
    "SAGE_VOICE_PATTERNS",
    "SCOUT_VOICE_PATTERNS",
    "SPARK_VOICE_PATTERNS",
    "STEADY_VOICE_PATTERNS",
    "SYNC_VOICE_PATTERNS",
    # Eigenvectors
    "SAGE_EIGENVECTORS",
    "SCOUT_EIGENVECTORS",
    "SPARK_EIGENVECTORS",
    "STEADY_EIGENVECTORS",
    "SYNC_EIGENVECTORS",
    # Factory functions
    "create_sage",
    "create_spark",
    "create_steady",
    "create_scout",
    "create_sync",
]
