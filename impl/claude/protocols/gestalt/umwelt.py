"""
GestaltUmwelt: Observer-dependent perception for architecture analysis.

Sprint 2 Feature: Same codebase, different views based on observer role.

Each observer role emphasizes different aspects of the architecture:
- TECH_LEAD: Health, drift, governance focus
- SECURITY: Vulnerable deps, access paths, sensitive data flow
- PERFORMANCE: Bottlenecks, complexity hotspots, coupling
- PRODUCT: Features, integration points, API surface

"There is no view from nowhere. Every perception is observer-dependent."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GestaltUmwelt(Enum):
    """
    Observer roles for Gestalt analysis.

    Maps to frontend observers in components/path/ObserverSwitcher.tsx:
    - architect → TECH_LEAD
    - developer → DEVELOPER (default)
    - reviewer → REVIEWER
    - newcomer → PRODUCT

    Extended with SECURITY and PERFORMANCE for backend-only roles.
    """

    # Core roles (matching frontend)
    TECH_LEAD = "tech_lead"      # architect → High-level patterns, health, governance
    DEVELOPER = "developer"      # developer → Implementation, dependencies
    REVIEWER = "reviewer"        # reviewer → Code review, issues, violations
    PRODUCT = "product"          # newcomer → Features, overview, entry points

    # Extended roles (backend-only, API param)
    SECURITY = "security"        # Vulnerable deps, access paths
    PERFORMANCE = "performance"  # Bottlenecks, complexity hotspots


# Frontend observer → Backend umwelt mapping
OBSERVER_TO_UMWELT: dict[str, GestaltUmwelt] = {
    "architect": GestaltUmwelt.TECH_LEAD,
    "developer": GestaltUmwelt.DEVELOPER,
    "reviewer": GestaltUmwelt.REVIEWER,
    "newcomer": GestaltUmwelt.PRODUCT,
    "tech_lead": GestaltUmwelt.TECH_LEAD,
    "security": GestaltUmwelt.SECURITY,
    "performance": GestaltUmwelt.PERFORMANCE,
    "product": GestaltUmwelt.PRODUCT,
}


@dataclass
class UmweltConfig:
    """
    Configuration for how an observer sees the architecture.

    Each config specifies:
    - Health weight modifiers (what to emphasize)
    - Node visibility rules (what to show/hide)
    - Link visibility rules
    - Metric reweighting factors
    """

    # Display weights (0-1, default 0.5)
    health_weight: float = 0.5       # Emphasize health grades
    coupling_weight: float = 0.5     # Emphasize coupling metrics
    violations_weight: float = 0.5   # Emphasize drift violations
    complexity_weight: float = 0.5   # Emphasize cyclomatic complexity
    size_weight: float = 0.5         # Emphasize lines of code

    # Visibility filters
    min_health_score: float = 0.0    # Hide nodes below this health
    min_importance: float = 0.0      # Hide nodes below this importance
    show_external_deps: bool = True  # Show external dependencies
    show_test_modules: bool = True   # Show test modules
    show_internal_only: bool = False # Only show internal modules

    # Layer emphasis (layers to highlight)
    emphasized_layers: list[str] = field(default_factory=list)

    # Link visibility
    show_all_edges: bool = True
    show_violation_edges: bool = True
    highlight_violation_edges: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "health_weight": self.health_weight,
            "coupling_weight": self.coupling_weight,
            "violations_weight": self.violations_weight,
            "complexity_weight": self.complexity_weight,
            "size_weight": self.size_weight,
            "min_health_score": self.min_health_score,
            "min_importance": self.min_importance,
            "show_external_deps": self.show_external_deps,
            "show_test_modules": self.show_test_modules,
            "show_internal_only": self.show_internal_only,
            "emphasized_layers": self.emphasized_layers,
            "show_all_edges": self.show_all_edges,
            "show_violation_edges": self.show_violation_edges,
            "highlight_violation_edges": self.highlight_violation_edges,
        }


# Preconfigured umwelt settings
UMWELT_CONFIGS: dict[GestaltUmwelt, UmweltConfig] = {
    GestaltUmwelt.TECH_LEAD: UmweltConfig(
        health_weight=0.9,
        coupling_weight=0.7,
        violations_weight=0.9,
        complexity_weight=0.6,
        size_weight=0.3,
        min_health_score=0.0,
        show_test_modules=False,
        emphasized_layers=["protocols", "agents"],
        highlight_violation_edges=True,
    ),
    GestaltUmwelt.DEVELOPER: UmweltConfig(
        health_weight=0.5,
        coupling_weight=0.8,
        violations_weight=0.4,
        complexity_weight=0.5,
        size_weight=0.5,
        show_test_modules=True,
        show_external_deps=True,
        emphasized_layers=[],
    ),
    GestaltUmwelt.REVIEWER: UmweltConfig(
        health_weight=0.7,
        coupling_weight=0.6,
        violations_weight=1.0,  # Maximum emphasis on violations
        complexity_weight=0.8,
        size_weight=0.4,
        min_health_score=0.0,  # Show all, even unhealthy
        show_test_modules=True,
        highlight_violation_edges=True,
        emphasized_layers=["agents", "protocols"],
    ),
    GestaltUmwelt.PRODUCT: UmweltConfig(
        health_weight=0.3,
        coupling_weight=0.2,
        violations_weight=0.2,
        complexity_weight=0.2,
        size_weight=0.7,  # Emphasize module size (feature scope)
        min_health_score=0.4,  # Hide unhealthy modules
        show_test_modules=False,
        show_external_deps=False,  # Simplified view
        show_internal_only=True,
        emphasized_layers=["protocols.api", "web"],
    ),
    GestaltUmwelt.SECURITY: UmweltConfig(
        health_weight=0.6,
        coupling_weight=0.9,  # High coupling = risk
        violations_weight=0.8,
        complexity_weight=0.7,
        size_weight=0.2,
        show_external_deps=True,  # Security cares about external deps
        show_test_modules=False,
        emphasized_layers=["protocols.api", "infra", "agents.d"],
        highlight_violation_edges=True,
    ),
    GestaltUmwelt.PERFORMANCE: UmweltConfig(
        health_weight=0.4,
        coupling_weight=0.9,  # Coupling affects performance
        violations_weight=0.3,
        complexity_weight=1.0,  # Maximum emphasis on complexity
        size_weight=0.8,  # Large modules = potential bottlenecks
        show_test_modules=False,
        emphasized_layers=["agents.d", "agents.m", "protocols.agentese"],
    ),
}


def get_umwelt_config(role: str | GestaltUmwelt | None = None) -> UmweltConfig:
    """
    Get the umwelt configuration for a given role.

    Args:
        role: Observer role (string or enum). Defaults to DEVELOPER.

    Returns:
        UmweltConfig for the specified role.
    """
    if role is None:
        return UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER]

    if isinstance(role, GestaltUmwelt):
        return UMWELT_CONFIGS.get(role, UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER])

    # Map string to umwelt
    umwelt = OBSERVER_TO_UMWELT.get(role.lower())
    if umwelt is None:
        return UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER]

    return UMWELT_CONFIGS[umwelt]


def compute_node_score(
    node: dict[str, Any],
    config: UmweltConfig,
) -> float:
    """
    Compute a weighted importance score for a node based on umwelt.

    Higher scores = more important for this observer's perspective.
    Used for:
    - Sorting (show most important first)
    - Sizing (larger nodes for more important modules)
    - Label visibility (show labels on important nodes)

    Args:
        node: Module node with health_score, coupling, etc.
        config: Umwelt configuration

    Returns:
        Importance score (0-1)
    """
    # Extract metrics with defaults
    health = node.get("health_score", 0.5)
    coupling = node.get("coupling", 0.5)
    violations = 1.0 if node.get("has_violations", False) else 0.0
    complexity = min(node.get("cyclomatic_complexity", 0) / 50, 1.0)  # Normalize
    size = min(node.get("lines_of_code", 0) / 1000, 1.0)  # Normalize

    # Apply weights
    score = (
        health * config.health_weight +
        coupling * config.coupling_weight +
        violations * config.violations_weight +
        complexity * config.complexity_weight +
        size * config.size_weight
    )

    # Normalize to 0-1
    total_weight = (
        config.health_weight +
        config.coupling_weight +
        config.violations_weight +
        config.complexity_weight +
        config.size_weight
    )

    return score / total_weight if total_weight > 0 else 0.5


def filter_node_for_umwelt(
    node: dict[str, Any],
    config: UmweltConfig,
) -> bool:
    """
    Determine if a node should be visible for this umwelt.

    Args:
        node: Module node dict
        config: Umwelt configuration

    Returns:
        True if node should be shown, False to hide
    """
    # Health threshold
    health = node.get("health_score", 0.5)
    if health < config.min_health_score:
        return False

    # Test modules
    name = node.get("name", "") or node.get("id", "")
    is_test = "_tests" in name or "test_" in name or "/tests/" in name
    if is_test and not config.show_test_modules:
        return False

    # External dependencies
    is_external = node.get("is_external", False)
    if is_external and not config.show_external_deps:
        return False

    # Internal only mode
    if config.show_internal_only and is_external:
        return False

    return True


__all__ = [
    "GestaltUmwelt",
    "OBSERVER_TO_UMWELT",
    "UmweltConfig",
    "UMWELT_CONFIGS",
    "get_umwelt_config",
    "compute_node_score",
    "filter_node_for_umwelt",
]
