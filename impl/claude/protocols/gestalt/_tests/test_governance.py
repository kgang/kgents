"""
Tests for Gestalt governance (drift detection).

Tests layer rules, ring rules, and violation detection.
"""

import pytest
from protocols.gestalt.analysis import (
    ArchitectureGraph,
    DependencyEdge,
    Module,
    ModuleHealth,
)
from protocols.gestalt.governance import (
    DriftRule,
    DriftViolation,
    GovernanceConfig,
    LayerRule,
    RingRule,
    RuleType,
    check_drift,
    create_kgents_config,
    create_layered_config,
    create_onion_config,
)

# ============================================================================
# Layer Rule Tests
# ============================================================================


class TestLayerRule:
    """Tests for LayerRule."""

    def test_rule_allows_valid_dependency(self) -> None:
        """Rule allows dependency to permitted layer."""
        rule = LayerRule(
            layer="presentation",
            allowed_dependencies=["application", "domain"],
        )
        assert rule.check("presentation", "application") is True
        assert rule.check("presentation", "domain") is True

    def test_rule_blocks_invalid_dependency(self) -> None:
        """Rule blocks dependency to non-permitted layer."""
        rule = LayerRule(
            layer="domain",
            allowed_dependencies=["domain"],  # Domain only depends on itself
        )
        assert rule.check("domain", "infrastructure") is False
        assert rule.check("domain", "presentation") is False

    def test_rule_allows_same_layer(self) -> None:
        """Same-layer dependencies are typically allowed."""
        rule = LayerRule(
            layer="domain",
            allowed_dependencies=["domain"],
        )
        assert rule.check("domain", "domain") is True

    def test_rule_ignores_other_layers(self) -> None:
        """Rule doesn't apply to other source layers."""
        rule = LayerRule(
            layer="domain",
            allowed_dependencies=["domain"],
        )
        # Rule for domain, so presentation source is ignored
        assert rule.check("presentation", "infrastructure") is True

    def test_rule_allows_unknown_target(self) -> None:
        """Unknown target layer is allowed (can't verify)."""
        rule = LayerRule(
            layer="domain",
            allowed_dependencies=["domain"],
        )
        assert rule.check("domain", None) is True


# ============================================================================
# Ring Rule Tests
# ============================================================================


class TestRingRule:
    """Tests for RingRule (onion/clean architecture)."""

    def test_outer_can_depend_on_inner(self) -> None:
        """Outer rings may depend on inner rings."""
        rule = RingRule(ring_order=["core", "domain", "application", "infrastructure"])
        # infrastructure (outer) can depend on core (inner)
        assert rule.check("infrastructure", "core") is True
        assert rule.check("infrastructure", "domain") is True
        assert rule.check("application", "domain") is True

    def test_inner_cannot_depend_on_outer(self) -> None:
        """Inner rings may not depend on outer rings."""
        rule = RingRule(ring_order=["core", "domain", "application", "infrastructure"])
        # core (inner) cannot depend on infrastructure (outer)
        assert rule.check("core", "infrastructure") is False
        assert rule.check("domain", "infrastructure") is False
        assert rule.check("domain", "application") is False

    def test_same_ring_allowed(self) -> None:
        """Same-ring dependencies are allowed."""
        rule = RingRule(ring_order=["core", "domain", "application"])
        assert rule.check("domain", "domain") is True

    def test_unknown_rings_allowed(self) -> None:
        """Unknown rings are allowed (can't verify)."""
        rule = RingRule(ring_order=["core", "domain"])
        assert rule.check("unknown", "core") is True
        assert rule.check("core", "unknown") is True

    def test_ring_index(self) -> None:
        """Test ring index lookup."""
        rule = RingRule(ring_order=["core", "domain", "application"])
        assert rule.get_ring_index("core") == 0
        assert rule.get_ring_index("domain") == 1
        assert rule.get_ring_index("application") == 2
        assert rule.get_ring_index("unknown") == -1


# ============================================================================
# Governance Config Tests
# ============================================================================


class TestGovernanceConfig:
    """Tests for GovernanceConfig."""

    def test_layer_assignment_explicit(self) -> None:
        """Explicit layer assignments work."""
        config = GovernanceConfig(
            layer_assignments={
                "mymodule": "domain",
            }
        )
        graph = ArchitectureGraph()
        graph.modules["mymodule"] = Module(name="mymodule")

        config.assign_layers(graph)
        assert graph.modules["mymodule"].layer == "domain"

    def test_layer_assignment_pattern(self) -> None:
        """Pattern-based layer assignment works."""
        config = GovernanceConfig(
            layer_patterns={
                "domain": ["domain.*", "*.domain"],
                "infrastructure": ["infra.*", "*.infra"],
            }
        )
        graph = ArchitectureGraph()
        graph.modules["domain.user"] = Module(name="domain.user")
        graph.modules["infra.db"] = Module(name="infra.db")

        config.assign_layers(graph)
        assert graph.modules["domain.user"].layer == "domain"
        assert graph.modules["infra.db"].layer == "infrastructure"

    def test_suppression_check(self) -> None:
        """Suppression checking works."""
        config = GovernanceConfig(
            suppressions={
                "a->b": "Known technical debt",
            }
        )
        edge = DependencyEdge(source="a", target="b")
        suppressed, reason = config.is_suppressed(edge)
        assert suppressed is True
        assert "technical debt" in reason

    def test_ring_assignment_from_tags(self) -> None:
        """Ring assignment via tags."""
        config = GovernanceConfig(
            ring_assignments={"core.types": "core"},
        )
        module = Module(name="core.types")
        graph = ArchitectureGraph()
        graph.modules["core.types"] = module

        config.assign_rings(graph)
        assert config.get_module_ring(module) == "core"


# ============================================================================
# Drift Detection Tests
# ============================================================================


class TestDriftDetection:
    """Tests for check_drift function."""

    def test_no_violations_when_compliant(self) -> None:
        """No violations for compliant architecture."""
        config = create_layered_config(["presentation", "application", "domain"])
        config.layer_assignments = {
            "presentation.views": "presentation",
            "application.services": "application",
            "domain.models": "domain",
        }

        graph = ArchitectureGraph()
        graph.modules["presentation.views"] = Module(name="presentation.views")
        graph.modules["application.services"] = Module(name="application.services")
        graph.modules["domain.models"] = Module(name="domain.models")
        graph.edges = [
            # presentation -> application (allowed)
            DependencyEdge(source="presentation.views", target="application.services"),
            # application -> domain (allowed)
            DependencyEdge(source="application.services", target="domain.models"),
        ]

        violations = check_drift(graph, config)
        assert len(violations) == 0

    def test_detects_layer_violation(self) -> None:
        """Detects layer dependency violation."""
        config = create_layered_config(["presentation", "application", "domain"])
        config.layer_assignments = {
            "domain.models": "domain",
            "presentation.views": "presentation",
        }

        graph = ArchitectureGraph()
        graph.modules["domain.models"] = Module(name="domain.models")
        graph.modules["presentation.views"] = Module(name="presentation.views")
        graph.edges = [
            # domain -> presentation (VIOLATION: domain should not depend on presentation)
            DependencyEdge(source="domain.models", target="presentation.views"),
        ]

        violations = check_drift(graph, config)
        assert len(violations) == 1
        assert violations[0].rule_type == RuleType.LAYER
        assert violations[0].source_module == "domain.models"
        assert violations[0].target_module == "presentation.views"

    def test_detects_ring_violation(self) -> None:
        """Detects clean architecture ring violation."""
        config = create_onion_config(["core", "application", "infrastructure"])
        config.ring_assignments = {
            "core.entities": "core",
            "infrastructure.db": "infrastructure",
        }

        graph = ArchitectureGraph()
        graph.modules["core.entities"] = Module(name="core.entities")
        graph.modules["infrastructure.db"] = Module(name="infrastructure.db")
        graph.edges = [
            # core -> infrastructure (VIOLATION: inner cannot depend on outer)
            DependencyEdge(source="core.entities", target="infrastructure.db"),
        ]

        violations = check_drift(graph, config)
        assert len(violations) == 1
        assert violations[0].rule_type == RuleType.RING

    def test_suppressed_violations_marked(self) -> None:
        """Suppressed violations are marked but still returned."""
        # In layered arch: infrastructure depends on domain (allowed)
        # But domain CANNOT depend on infrastructure (violation)
        # We use layers ordered: presentation > domain > infrastructure
        # So infrastructure (bottom) can only depend on itself
        config = create_layered_config(["presentation", "domain", "infrastructure"])
        config.layer_assignments = {
            "infrastructure.db": "infrastructure",
            "domain.models": "domain",
        }
        config.suppressions = {
            "infrastructure.db->domain.models": "Legacy code, will fix later",
        }

        graph = ArchitectureGraph()
        graph.modules["infrastructure.db"] = Module(name="infrastructure.db")
        graph.modules["domain.models"] = Module(name="domain.models")
        graph.edges = [
            # Infrastructure depending on domain is a violation
            # (infrastructure can only depend on itself in layered)
            DependencyEdge(source="infrastructure.db", target="domain.models"),
        ]

        violations = check_drift(graph, config)
        assert len(violations) == 1
        assert violations[0].suppressed is True
        assert "Legacy" in violations[0].suppression_reason

    def test_custom_drift_rule(self) -> None:
        """Custom drift rules work."""
        # Rule: No module may import from 'deprecated' package
        rule = DriftRule(
            name="no-deprecated",
            predicate=lambda e, s, t: not t.name.startswith("deprecated"),
            description="Do not import from deprecated package",
            severity="error",
        )
        config = GovernanceConfig(drift_rules=[rule])

        graph = ArchitectureGraph()
        graph.modules["mymodule"] = Module(name="mymodule")
        graph.modules["deprecated.old"] = Module(name="deprecated.old")
        graph.edges = [
            DependencyEdge(source="mymodule", target="deprecated.old"),
        ]

        violations = check_drift(graph, config)
        assert len(violations) == 1
        assert violations[0].rule_name == "no-deprecated"


# ============================================================================
# Preset Config Tests
# ============================================================================


class TestPresetConfigs:
    """Tests for preset governance configurations."""

    def test_layered_config(self) -> None:
        """Layered config creates proper rules."""
        config = create_layered_config(
            ["presentation", "application", "domain", "infrastructure"]
        )
        assert len(config.layer_rules) == 4
        # Presentation can depend on all layers below
        pres_rule = next(r for r in config.layer_rules if r.layer == "presentation")
        assert "application" in pres_rule.allowed_dependencies
        assert "domain" in pres_rule.allowed_dependencies

    def test_onion_config(self) -> None:
        """Onion config creates proper ring rule."""
        config = create_onion_config(["core", "application", "infrastructure"])
        assert config.ring_rule is not None
        assert config.ring_rule.ring_order == ["core", "application", "infrastructure"]

    def test_kgents_config(self) -> None:
        """kgents-specific config is valid."""
        config = create_kgents_config()
        assert len(config.layer_rules) > 0
        assert config.ring_rule is not None
        assert "core" in config.ring_rule.ring_order


# ============================================================================
# Ring Pattern Regression Tests
# ============================================================================


class TestRingPatternMatching:
    """Regression tests for ring pattern matching against dotted module names."""

    def test_ring_pattern_matches_dotted_module_name(self) -> None:
        """Ring patterns should match dotted module names (not file paths).

        This is a regression test for the bug where ring_patterns used file
        globs like "**/types.py" but fnmatch runs against dotted names like
        "protocols.agentese.types".
        """
        config = create_kgents_config()
        graph = ArchitectureGraph()

        # Add modules with dotted names (as they appear in real scans)
        # Note: protocols.agentese.types matches BOTH "*.types" (core) AND
        # "protocols.agentese.*" (domain). The first matching pattern wins
        # in iteration order. Use modules that unambiguously match one ring.
        graph.modules["protocols.billing.types"] = Module(
            name="protocols.billing.types"
        )
        graph.modules["protocols.cli.handlers.brain"] = Module(
            name="protocols.cli.handlers.brain"
        )
        graph.modules["agents.m.cartographer"] = Module(name="agents.m.cartographer")

        config.assign_rings(graph)

        # protocols.billing.types should match "*.types" -> core
        # (doesn't match agentese.*, cli.*, api.*, terrarium.*, or tenancy.*)
        types_module = graph.modules["protocols.billing.types"]
        assert config.get_module_ring(types_module) == "core", (
            "*.types pattern should match protocols.billing.types"
        )

        # protocols.cli.handlers.brain should match "protocols.cli.*" -> application
        cli_module = graph.modules["protocols.cli.handlers.brain"]
        assert config.get_module_ring(cli_module) == "application", (
            "protocols.cli.* should match protocols.cli.handlers.brain"
        )

        # agents.m.cartographer should match "agents.*" -> domain
        agent_module = graph.modules["agents.m.cartographer"]
        assert config.get_module_ring(agent_module) == "domain", (
            "agents.* should match agents.m.cartographer"
        )

    def test_ring_rule_triggers_violation(self) -> None:
        """Ring rule should detect violations when inner depends on outer.

        Regression test proving ring assignment + rule checking works end-to-end.
        """
        config = create_kgents_config()

        graph = ArchitectureGraph()
        # Core module (inner ring)
        graph.modules["protocols.agentese.types"] = Module(
            name="protocols.agentese.types"
        )
        # Infrastructure module (outer ring)
        graph.modules["protocols.terrarium.client"] = Module(
            name="protocols.terrarium.client"
        )
        # VIOLATION: core (inner) imports infrastructure (outer)
        graph.edges = [
            DependencyEdge(
                source="protocols.agentese.types",
                target="protocols.terrarium.client",
                line_number=10,
            ),
        ]

        violations = check_drift(graph, config)

        # Should detect ring violation
        ring_violations = [v for v in violations if v.rule_type == RuleType.RING]
        assert len(ring_violations) == 1, (
            f"Expected 1 ring violation, got {len(ring_violations)}: {ring_violations}"
        )
        assert ring_violations[0].source_module == "protocols.agentese.types"
        assert ring_violations[0].target_module == "protocols.terrarium.client"
