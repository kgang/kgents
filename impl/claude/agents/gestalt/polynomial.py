"""
GestaltPolynomial: Architecture Analysis as State Machine.

The gestalt polynomial models codebase architecture analysis as a dynamical system:
- IDLE: Ready for analysis operations
- SCANNING: Full codebase scan in progress
- WATCHING: Live file watching mode (incremental updates)
- ANALYZING: Deep analysis on specific module or region
- HEALING: Architecture drift repair/suggestion generation

The Insight (from Gestalt Psychology):
    The whole is more than the sum of its parts.
    Architecture emerges from the relationships between modules,
    not from the modules themselves.

The C4 Model Integration:
    Like semantic zoom (System → Container → Component → Code),
    Gestalt's phases enable different levels of observation.

Example:
    >>> poly = GESTALT_POLYNOMIAL
    >>> state, output = poly.invoke(GestaltPhase.IDLE, ScanInput(language="python"))
    >>> print(state, output)
    GestaltPhase.SCANNING ScanOutput(...)

See: plans/core-apps/gestalt-architecture-visualizer.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Gestalt Phase (Positions in the Polynomial)
# =============================================================================


class GestaltPhase(Enum):
    """
    Positions in the gestalt polynomial.

    These are operational modes, not internal states.
    The phase determines which operations are valid (directions).

    The Metaphor: Architecture as Living Garden
    - IDLE: Dormant, ready to observe
    - SCANNING: Full garden survey
    - WATCHING: Continuous observation (live mode)
    - ANALYZING: Deep inspection of a specific plant
    - HEALING: Pruning suggestions for unhealthy growth
    """

    IDLE = auto()
    SCANNING = auto()
    WATCHING = auto()
    ANALYZING = auto()
    HEALING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class ScanInput:
    """Input for full codebase scan."""

    root: Path | None = None
    language: str = "python"
    max_modules: int | None = None


@dataclass(frozen=True)
class WatchInput:
    """Input for starting/stopping file watching."""

    enable: bool = True
    debounce_seconds: float = 0.3
    patterns: tuple[str, ...] = ("**/*.py",)


@dataclass(frozen=True)
class AnalyzeInput:
    """Input for deep module analysis."""

    module_name: str
    include_dependents: bool = True
    include_dependencies: bool = True
    depth: int = 2  # How many layers of deps to include


@dataclass(frozen=True)
class HealInput:
    """Input for drift repair suggestions."""

    module_name: str | None = None  # None = all modules
    severity_threshold: str = "warning"  # "info", "warning", "error"
    max_suggestions: int = 10


@dataclass(frozen=True)
class IdleInput:
    """Input for returning to idle state."""

    pass


class GestaltInput:
    """Factory for gestalt inputs."""

    @staticmethod
    def scan(
        root: Path | None = None,
        language: str = "python",
        max_modules: int | None = None,
    ) -> ScanInput:
        """Create a scan input."""
        return ScanInput(root=root, language=language, max_modules=max_modules)

    @staticmethod
    def watch(
        enable: bool = True,
        debounce_seconds: float = 0.3,
        patterns: tuple[str, ...] = ("**/*.py",),
    ) -> WatchInput:
        """Create a watch input."""
        return WatchInput(
            enable=enable, debounce_seconds=debounce_seconds, patterns=patterns
        )

    @staticmethod
    def analyze(
        module_name: str,
        include_dependents: bool = True,
        include_dependencies: bool = True,
        depth: int = 2,
    ) -> AnalyzeInput:
        """Create an analyze input for deep module inspection."""
        return AnalyzeInput(
            module_name=module_name,
            include_dependents=include_dependents,
            include_dependencies=include_dependencies,
            depth=depth,
        )

    @staticmethod
    def heal(
        module_name: str | None = None,
        severity_threshold: str = "warning",
        max_suggestions: int = 10,
    ) -> HealInput:
        """Create a heal input for drift repair suggestions."""
        return HealInput(
            module_name=module_name,
            severity_threshold=severity_threshold,
            max_suggestions=max_suggestions,
        )

    @staticmethod
    def idle() -> IdleInput:
        """Create an idle input (return to ready state)."""
        return IdleInput()


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class GestaltOutput:
    """Output from gestalt transitions."""

    phase: GestaltPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanOutput(GestaltOutput):
    """Output from a scan operation."""

    module_count: int = 0
    edge_count: int = 0
    overall_grade: str = "?"
    duration_ms: float = 0.0


@dataclass
class WatchOutput(GestaltOutput):
    """Output from watch mode transition."""

    watching: bool = False
    patterns: tuple[str, ...] = ()


@dataclass
class AnalyzeOutput(GestaltOutput):
    """Output from deep analysis."""

    module_name: str = ""
    health_grade: str = "?"
    dependency_count: int = 0
    dependent_count: int = 0
    drift_violations: int = 0


@dataclass
class HealOutput(GestaltOutput):
    """Output from heal operation."""

    suggestion_count: int = 0
    modules_analyzed: int = 0


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def gestalt_directions(phase: GestaltPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each gestalt phase.

    This encodes the mode-dependent behavior:
    - IDLE: Can start any operation (scan, watch, analyze, heal)
    - SCANNING: Can only cancel (idle) - full scan in progress
    - WATCHING: Can stop watching (idle), or request analysis (analyze)
    - ANALYZING: Can only return to idle
    - HEALING: Can only return to idle
    """
    match phase:
        case GestaltPhase.IDLE:
            return frozenset(
                {ScanInput, WatchInput, AnalyzeInput, HealInput, type, Any}
            )
        case GestaltPhase.SCANNING:
            return frozenset({IdleInput, type, Any})  # Can cancel
        case GestaltPhase.WATCHING:
            # While watching, can stop or request analysis
            return frozenset({IdleInput, AnalyzeInput, WatchInput, type, Any})
        case GestaltPhase.ANALYZING:
            return frozenset({IdleInput, type, Any})
        case GestaltPhase.HEALING:
            return frozenset({IdleInput, type, Any})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def gestalt_transition(
    phase: GestaltPhase, input: Any
) -> tuple[GestaltPhase, GestaltOutput]:
    """
    Gestalt state transition function.

    This is the polynomial core:
    transition: Phase × Input → (NewPhase, Output)

    The Gestalt Principle:
        Observation changes the observed.
        Each scan doesn't just read the codebase—
        it reconstitutes the architecture's gestalt.
    """
    match phase:
        case GestaltPhase.IDLE:
            if isinstance(input, ScanInput):
                return GestaltPhase.SCANNING, ScanOutput(
                    phase=GestaltPhase.SCANNING,
                    success=True,
                    message=f"Scanning codebase ({input.language})",
                    metadata={
                        "root": str(input.root) if input.root else None,
                        "language": input.language,
                        "max_modules": input.max_modules,
                    },
                )
            elif isinstance(input, WatchInput):
                if input.enable:
                    return GestaltPhase.WATCHING, WatchOutput(
                        phase=GestaltPhase.WATCHING,
                        success=True,
                        message="Starting file watcher",
                        watching=True,
                        patterns=input.patterns,
                        metadata={
                            "debounce_seconds": input.debounce_seconds,
                            "patterns": list(input.patterns),
                        },
                    )
                else:
                    # Disable while idle is a no-op
                    return GestaltPhase.IDLE, GestaltOutput(
                        phase=GestaltPhase.IDLE,
                        success=True,
                        message="Watcher not running",
                    )
            elif isinstance(input, AnalyzeInput):
                return GestaltPhase.ANALYZING, AnalyzeOutput(
                    phase=GestaltPhase.ANALYZING,
                    success=True,
                    message=f"Analyzing module: {input.module_name}",
                    module_name=input.module_name,
                    metadata={
                        "include_dependents": input.include_dependents,
                        "include_dependencies": input.include_dependencies,
                        "depth": input.depth,
                    },
                )
            elif isinstance(input, HealInput):
                return GestaltPhase.HEALING, HealOutput(
                    phase=GestaltPhase.HEALING,
                    success=True,
                    message="Generating drift repair suggestions",
                    metadata={
                        "module_name": input.module_name,
                        "severity_threshold": input.severity_threshold,
                        "max_suggestions": input.max_suggestions,
                    },
                )
            else:
                return GestaltPhase.IDLE, GestaltOutput(
                    phase=GestaltPhase.IDLE,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case GestaltPhase.SCANNING:
            if isinstance(input, IdleInput):
                return GestaltPhase.IDLE, GestaltOutput(
                    phase=GestaltPhase.IDLE,
                    success=True,
                    message="Scan complete, returning to idle",
                )
            else:
                return GestaltPhase.SCANNING, GestaltOutput(
                    phase=GestaltPhase.SCANNING,
                    success=False,
                    message="Scan in progress, wait or send idle to cancel",
                )

        case GestaltPhase.WATCHING:
            if isinstance(input, IdleInput):
                return GestaltPhase.IDLE, WatchOutput(
                    phase=GestaltPhase.IDLE,
                    success=True,
                    message="Stopping file watcher",
                    watching=False,
                    patterns=(),
                )
            elif isinstance(input, WatchInput) and not input.enable:
                return GestaltPhase.IDLE, WatchOutput(
                    phase=GestaltPhase.IDLE,
                    success=True,
                    message="File watcher stopped",
                    watching=False,
                    patterns=(),
                )
            elif isinstance(input, AnalyzeInput):
                # Can analyze while watching (stays in WATCHING)
                return GestaltPhase.WATCHING, AnalyzeOutput(
                    phase=GestaltPhase.WATCHING,
                    success=True,
                    message=f"Quick analysis: {input.module_name}",
                    module_name=input.module_name,
                    metadata={
                        "include_dependents": input.include_dependents,
                        "include_dependencies": input.include_dependencies,
                        "depth": input.depth,
                        "mode": "quick",  # Lighter analysis while watching
                    },
                )
            else:
                return GestaltPhase.WATCHING, GestaltOutput(
                    phase=GestaltPhase.WATCHING,
                    success=False,
                    message="Invalid input while watching",
                )

        case GestaltPhase.ANALYZING:
            if isinstance(input, IdleInput):
                return GestaltPhase.IDLE, GestaltOutput(
                    phase=GestaltPhase.IDLE,
                    success=True,
                    message="Analysis complete, returning to idle",
                )
            else:
                return GestaltPhase.ANALYZING, GestaltOutput(
                    phase=GestaltPhase.ANALYZING,
                    success=False,
                    message="Analysis in progress, wait or send idle",
                )

        case GestaltPhase.HEALING:
            if isinstance(input, IdleInput):
                return GestaltPhase.IDLE, GestaltOutput(
                    phase=GestaltPhase.IDLE,
                    success=True,
                    message="Healing complete, returning to idle",
                )
            else:
                return GestaltPhase.HEALING, GestaltOutput(
                    phase=GestaltPhase.HEALING,
                    success=False,
                    message="Healing in progress, wait or send idle",
                )

        case _:
            return GestaltPhase.IDLE, GestaltOutput(
                phase=GestaltPhase.IDLE,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


GESTALT_POLYNOMIAL: PolyAgent[GestaltPhase, Any, GestaltOutput] = PolyAgent(
    name="GestaltPolynomial",
    positions=frozenset(GestaltPhase),
    _directions=gestalt_directions,
    _transition=gestalt_transition,
)
"""
The Gestalt polynomial agent.

This models gestalt behavior as a polynomial state machine:
- positions: 5 phases (IDLE, SCANNING, WATCHING, ANALYZING, HEALING)
- directions: phase-dependent valid inputs
- transition: architecture operation transitions

Key Property (C4-Aligned):
    Different phases correspond to different levels of observation:
    - SCANNING = System Context level (whole codebase)
    - WATCHING = Container level (incremental updates)
    - ANALYZING = Component level (deep module inspection)
    - HEALING = Code level (specific fixes)

Key Property (Live Mode):
    WATCHING phase allows concurrent analysis without leaving watch mode.
    This enables real-time architecture monitoring with on-demand deep dives.
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "GestaltPhase",
    # Inputs
    "ScanInput",
    "WatchInput",
    "AnalyzeInput",
    "HealInput",
    "IdleInput",
    "GestaltInput",
    # Outputs
    "GestaltOutput",
    "ScanOutput",
    "WatchOutput",
    "AnalyzeOutput",
    "HealOutput",
    # Functions
    "gestalt_directions",
    "gestalt_transition",
    # Polynomial
    "GESTALT_POLYNOMIAL",
]
