"""
Core types and configuration for stability analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Import risk scores (0.0 = safe, 1.0 = dangerous)
IMPORT_RISK: dict[str, float] = {
    # Safe (0.0)
    "typing": 0.0,
    "dataclasses": 0.0,
    "abc": 0.0,
    "enum": 0.0,
    "types": 0.0,
    # Low risk (0.1)
    "re": 0.1,
    "json": 0.1,
    "functools": 0.1,
    "collections": 0.1,
    "itertools": 0.1,
    "operator": 0.1,
    "math": 0.1,
    # Medium risk (0.2-0.4)
    "asyncio": 0.2,
    "logging": 0.2,
    "pathlib": 0.3,
    "datetime": 0.1,
    "hashlib": 0.2,
    # Medium-high risk (0.5-0.7)
    "requests": 0.6,
    "urllib": 0.6,
    "http": 0.6,
    "os": 0.7,
    # High risk (0.8+)
    "subprocess": 0.9,
    "sys": 0.8,
    "shutil": 0.8,
    "socket": 0.9,
    "multiprocessing": 0.7,
    "threading": 0.6,
}

# Default unknown import risk
DEFAULT_IMPORT_RISK = 0.5


@dataclass
class StabilityConfig:
    """Configuration for stability analysis."""

    # Thresholds (scaled by entropy budget)
    max_cyclomatic_complexity: int = 20
    max_branching_factor: int = 5
    max_import_risk: float = 0.5

    # Absolute limits (not scaled)
    chaos_threshold: float = 0.1
    max_depth: int = 3

    # Import control
    allowed_imports: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "typing",
            "dataclasses",
            "abc",
            "enum",
            "re",
            "json",
            "asyncio",
            "functools",
            "collections",
            "itertools",
            "operator",
            "math",
            "datetime",
        })
    )

    forbidden_imports: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "os",
            "subprocess",
            "sys",
            "shutil",
            "socket",
            "requests",
            "urllib",
            "http",
            "multiprocessing",
        })
    )


# Singleton default config
DEFAULT_CONFIG = StabilityConfig()


@dataclass(frozen=True)
class StabilityMetrics:
    """Quantitative stability measurements."""

    cyclomatic_complexity: int
    branching_factor: int
    import_risk: float
    has_unbounded_recursion: bool
    estimated_runtime: str  # "O(1)", "O(n)", "O(n^2)", "unbounded"
    import_count: int
    function_count: int
    max_nesting_depth: int


@dataclass(frozen=True)
class StabilityInput:
    """Input to the Chaosmonger agent."""

    source_code: str  # Python source to analyze
    entropy_budget: float  # Available budget (0.0-1.0)
    config: StabilityConfig = field(default_factory=lambda: DEFAULT_CONFIG)


@dataclass(frozen=True)
class StabilityResult:
    """Output from the Chaosmonger agent."""

    is_stable: bool
    metrics: StabilityMetrics
    violations: tuple[str, ...]  # Why unstable (if any)
