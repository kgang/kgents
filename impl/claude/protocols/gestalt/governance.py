"""
Gestalt Architecture Governance.

Layer and ring rules for drift detection.
Validates that dependencies follow architectural constraints.

Key Concepts:
- Layer: Horizontal slice (e.g., presentation, domain, infrastructure)
- Ring: Concentric ring (e.g., core, application, adapters)
- Drift: Violation of layer/ring dependency rules

Rules are defined as:
- LayerRule: "layer A may only depend on layers B, C"
- RingRule: "ring A may only depend on inner rings"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .analysis import ArchitectureGraph, DependencyEdge, Module

# ============================================================================
# Rule Types
# ============================================================================


class RuleType(Enum):
    """Type of architecture rule."""

    LAYER = "layer"  # Layered architecture
    RING = "ring"  # Onion/clean architecture
    ALLOW = "allow"  # Explicit allow rule
    DENY = "deny"  # Explicit deny rule
    TAG = "tag"  # Tag-based rule


@dataclass
class LayerRule:
    """
    Layered architecture rule.

    Defines which layers a given layer may depend on.
    """

    layer: str  # The layer this rule applies to
    allowed_dependencies: list[str]  # Layers this layer may depend on
    description: str = ""

    def check(self, source_layer: str | None, target_layer: str | None) -> bool:
        """
        Check if a dependency is allowed.

        Returns True if allowed, False if violation.
        """
        if source_layer != self.layer:
            return True  # Rule doesn't apply
        if target_layer is None:
            return True  # Can't check unknown layer
        return target_layer in self.allowed_dependencies


@dataclass
class RingRule:
    """
    Onion/clean architecture rule.

    Defines ring ordering where outer rings may depend on inner rings.
    """

    ring_order: list[str]  # Innermost to outermost
    description: str = ""

    def get_ring_index(self, ring: str) -> int:
        """Get index of ring (-1 if not found)."""
        try:
            return self.ring_order.index(ring)
        except ValueError:
            return -1

    def check(self, source_ring: str | None, target_ring: str | None) -> bool:
        """
        Check if dependency is allowed.

        Outer rings (higher index) may depend on inner rings (lower index).
        Same-ring dependencies are allowed.
        """
        if source_ring is None or target_ring is None:
            return True

        source_idx = self.get_ring_index(source_ring)
        target_idx = self.get_ring_index(target_ring)

        if source_idx == -1 or target_idx == -1:
            return True  # Unknown ring, can't check

        # source may depend on target if target is same or inner (lower index)
        return target_idx <= source_idx


@dataclass
class DriftRule:
    """
    Generic drift rule using predicate.

    Allows custom rules beyond simple layer/ring checks.
    """

    name: str
    predicate: Callable[[DependencyEdge, Module, Module], bool]
    description: str = ""
    severity: str = "warning"  # warning, error

    def check(
        self,
        edge: DependencyEdge,
        source_module: Module,
        target_module: Module,
    ) -> bool:
        """Check if dependency is allowed. True = allowed."""
        return self.predicate(edge, source_module, target_module)


# ============================================================================
# Violations
# ============================================================================


@dataclass
class DriftViolation:
    """A detected architectural drift violation."""

    edge: DependencyEdge
    rule_name: str
    rule_type: RuleType
    source_module: str
    target_module: str
    source_layer: str | None = None
    target_layer: str | None = None
    severity: str = "warning"
    description: str = ""
    suggested_fix: str = ""
    suppressed: bool = False
    suppression_reason: str = ""

    def __str__(self) -> str:
        return (
            f"[{self.severity.upper()}] {self.rule_name}: "
            f"{self.source_module} -> {self.target_module} "
            f"(line {self.edge.line_number})"
        )


# ============================================================================
# Governance Configuration
# ============================================================================


@dataclass
class GovernanceConfig:
    """
    Architecture governance configuration.

    Combines layer rules, ring rules, and custom drift rules.
    """

    layer_rules: list[LayerRule] = field(default_factory=list)
    ring_rule: RingRule | None = None
    drift_rules: list[DriftRule] = field(default_factory=list)
    suppressions: dict[str, str] = field(default_factory=dict)  # edge_key -> reason

    # Module -> layer mapping
    layer_assignments: dict[str, str] = field(default_factory=dict)
    # Module -> ring mapping
    ring_assignments: dict[str, str] = field(default_factory=dict)

    # Patterns for auto-assignment
    layer_patterns: dict[str, list[str]] = field(
        default_factory=dict
    )  # layer -> patterns
    ring_patterns: dict[str, list[str]] = field(
        default_factory=dict
    )  # ring -> patterns

    def assign_layers(self, graph: ArchitectureGraph) -> None:
        """Auto-assign layers to modules based on patterns."""
        import fnmatch

        for name, module in graph.modules.items():
            # Check explicit assignments first
            if name in self.layer_assignments:
                module.layer = self.layer_assignments[name]
                continue

            # Check patterns
            for layer, patterns in self.layer_patterns.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(name, pattern):
                        module.layer = layer
                        break
                if module.layer:
                    break

    def assign_rings(self, graph: ArchitectureGraph) -> None:
        """Auto-assign rings to modules based on patterns."""
        import fnmatch

        for name, module in graph.modules.items():
            # Check explicit assignments first
            if name in self.ring_assignments:
                module.tags.add(f"ring:{self.ring_assignments[name]}")
                continue

            # Check patterns
            for ring, patterns in self.ring_patterns.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(name, pattern):
                        module.tags.add(f"ring:{ring}")
                        break

    def get_module_ring(self, module: Module) -> str | None:
        """Get ring assignment for a module."""
        for tag in module.tags:
            if tag.startswith("ring:"):
                return tag[5:]
        return None

    def is_suppressed(self, edge: DependencyEdge) -> tuple[bool, str]:
        """Check if a violation is suppressed."""
        key = f"{edge.source}->{edge.target}"
        if key in self.suppressions:
            return True, self.suppressions[key]
        return False, ""


# ============================================================================
# Drift Detection
# ============================================================================


def check_drift(
    graph: ArchitectureGraph,
    config: GovernanceConfig,
) -> list[DriftViolation]:
    """
    Check for architectural drift violations.

    Applies all configured rules and returns violations.
    """
    violations: list[DriftViolation] = []

    # Auto-assign layers and rings
    config.assign_layers(graph)
    config.assign_rings(graph)

    for edge in graph.edges:
        source_module = graph.modules.get(edge.source)
        target_module = graph.modules.get(edge.target)

        if source_module is None:
            continue

        # Check layer rules
        for rule in config.layer_rules:
            if not rule.check(
                source_module.layer,
                target_module.layer if target_module else None,
            ):
                suppressed, reason = config.is_suppressed(edge)
                violations.append(
                    DriftViolation(
                        edge=edge,
                        rule_name=f"layer:{rule.layer}",
                        rule_type=RuleType.LAYER,
                        source_module=edge.source,
                        target_module=edge.target,
                        source_layer=source_module.layer,
                        target_layer=target_module.layer if target_module else None,
                        severity="error",
                        description=rule.description
                        or f"Layer '{source_module.layer}' may not depend on '{target_module.layer if target_module else 'unknown'}'",
                        suppressed=suppressed,
                        suppression_reason=reason,
                    )
                )

        # Check ring rule
        if config.ring_rule and target_module:
            source_ring = config.get_module_ring(source_module)
            target_ring = config.get_module_ring(target_module)

            if not config.ring_rule.check(source_ring, target_ring):
                suppressed, reason = config.is_suppressed(edge)
                violations.append(
                    DriftViolation(
                        edge=edge,
                        rule_name="ring",
                        rule_type=RuleType.RING,
                        source_module=edge.source,
                        target_module=edge.target,
                        source_layer=source_ring,
                        target_layer=target_ring,
                        severity="error",
                        description=config.ring_rule.description
                        or f"Ring '{source_ring}' may not depend on outer ring '{target_ring}'",
                        suppressed=suppressed,
                        suppression_reason=reason,
                    )
                )

        # Check custom drift rules
        for drift_rule in config.drift_rules:
            if target_module and not drift_rule.check(
                edge, source_module, target_module
            ):
                suppressed, reason = config.is_suppressed(edge)
                violations.append(
                    DriftViolation(
                        edge=edge,
                        rule_name=drift_rule.name,
                        rule_type=RuleType.DENY,
                        source_module=edge.source,
                        target_module=edge.target,
                        severity=drift_rule.severity,
                        description=drift_rule.description,
                        suppressed=suppressed,
                        suppression_reason=reason,
                    )
                )

    return violations


# ============================================================================
# Common Governance Presets
# ============================================================================


def create_layered_config(layers: list[str]) -> GovernanceConfig:
    """
    Create a standard layered architecture config.

    Each layer may only depend on the layer directly below it.
    E.g., ["presentation", "application", "domain", "infrastructure"]
    """
    rules = []
    for i, layer in enumerate(layers):
        # Allow dependencies on same layer and layers below
        allowed = layers[i:]
        rules.append(
            LayerRule(
                layer=layer,
                allowed_dependencies=allowed,
                description=f"Layer '{layer}' may depend on {allowed}",
            )
        )

    return GovernanceConfig(layer_rules=rules)


def create_onion_config(rings: list[str]) -> GovernanceConfig:
    """
    Create a clean/onion architecture config.

    Rings are ordered from innermost to outermost.
    Outer rings may depend on inner rings.
    E.g., ["domain", "application", "infrastructure", "presentation"]
    """
    return GovernanceConfig(
        ring_rule=RingRule(
            ring_order=rings,
            description="Outer rings may only depend on inner rings",
        )
    )


def create_kgents_config() -> GovernanceConfig:
    """
    Create governance config for the kgents codebase.

    Layers: spec > agents > protocols > impl
    """
    config = GovernanceConfig(
        layer_patterns={
            "spec": ["spec.*"],
            "agents": ["agents.*"],
            "protocols": ["protocols.*"],
        },
        ring_rule=RingRule(
            ring_order=["core", "domain", "application", "infrastructure"],
            description="Clean architecture: inner rings must not depend on outer",
        ),
        ring_patterns={
            "core": ["**/types.py", "**/base.py", "**/protocols.py"],
            "domain": ["agents.*", "protocols.agentese.*"],
            "application": ["protocols.cli.*", "protocols.api.*"],
            "infrastructure": ["protocols.terrarium.*", "protocols.tenancy.*"],
        },
    )

    # Add layer rules
    config.layer_rules = [
        LayerRule(
            layer="spec",
            allowed_dependencies=["spec"],
            description="Spec has no implementation dependencies",
        ),
        LayerRule(
            layer="agents",
            allowed_dependencies=["agents", "protocols"],
            description="Agents may depend on protocols",
        ),
        LayerRule(
            layer="protocols",
            allowed_dependencies=["protocols", "agents"],
            description="Protocols may depend on agents and other protocols",
        ),
    ]

    return config
