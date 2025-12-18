"""
Tests for GestaltUmwelt - Sprint 2: Observer-dependent views.

Tests observer roles, metric weighting, and node filtering.
"""

from __future__ import annotations

import pytest

from protocols.gestalt.umwelt import (
    OBSERVER_TO_UMWELT,
    UMWELT_CONFIGS,
    GestaltUmwelt,
    UmweltConfig,
    compute_node_score,
    filter_node_for_umwelt,
    get_umwelt_config,
)

# =============================================================================
# GestaltUmwelt Enum Tests
# =============================================================================


class TestGestaltUmwelt:
    """Tests for the GestaltUmwelt enum."""

    def test_all_roles_defined(self):
        """All expected roles exist."""
        expected = {"tech_lead", "developer", "reviewer", "product", "security", "performance"}
        actual = {role.value for role in GestaltUmwelt}
        assert expected == actual

    def test_observer_to_umwelt_mapping(self):
        """Frontend observer names map to correct umwelts."""
        assert OBSERVER_TO_UMWELT["architect"] == GestaltUmwelt.TECH_LEAD
        assert OBSERVER_TO_UMWELT["developer"] == GestaltUmwelt.DEVELOPER
        assert OBSERVER_TO_UMWELT["reviewer"] == GestaltUmwelt.REVIEWER
        assert OBSERVER_TO_UMWELT["newcomer"] == GestaltUmwelt.PRODUCT

    def test_direct_role_names_work(self):
        """Backend role names also work."""
        assert OBSERVER_TO_UMWELT["tech_lead"] == GestaltUmwelt.TECH_LEAD
        assert OBSERVER_TO_UMWELT["security"] == GestaltUmwelt.SECURITY
        assert OBSERVER_TO_UMWELT["performance"] == GestaltUmwelt.PERFORMANCE


# =============================================================================
# UmweltConfig Tests
# =============================================================================


class TestUmweltConfig:
    """Tests for UmweltConfig dataclass."""

    def test_default_config(self):
        """Default config has balanced weights."""
        config = UmweltConfig()
        assert config.health_weight == 0.5
        assert config.coupling_weight == 0.5
        assert config.violations_weight == 0.5
        assert config.show_test_modules is True
        assert config.show_external_deps is True

    def test_to_dict(self):
        """Config serializes to dict."""
        config = UmweltConfig(health_weight=0.9, coupling_weight=0.7)
        d = config.to_dict()
        assert d["health_weight"] == 0.9
        assert d["coupling_weight"] == 0.7
        assert "show_test_modules" in d

    def test_all_umwelts_have_configs(self):
        """Every umwelt enum has a config defined."""
        for umwelt in GestaltUmwelt:
            assert umwelt in UMWELT_CONFIGS, f"Missing config for {umwelt}"


# =============================================================================
# get_umwelt_config Tests
# =============================================================================


class TestGetUmweltConfig:
    """Tests for get_umwelt_config function."""

    def test_none_returns_developer(self):
        """None defaults to developer config."""
        config = get_umwelt_config(None)
        assert config == UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER]

    def test_enum_value_works(self):
        """Direct enum value works."""
        config = get_umwelt_config(GestaltUmwelt.TECH_LEAD)
        assert config == UMWELT_CONFIGS[GestaltUmwelt.TECH_LEAD]

    def test_string_role_works(self):
        """String role name works."""
        config = get_umwelt_config("tech_lead")
        assert config == UMWELT_CONFIGS[GestaltUmwelt.TECH_LEAD]

    def test_frontend_observer_works(self):
        """Frontend observer name works."""
        config = get_umwelt_config("architect")
        assert config == UMWELT_CONFIGS[GestaltUmwelt.TECH_LEAD]

    def test_case_insensitive(self):
        """Role lookup is case insensitive."""
        config1 = get_umwelt_config("TECH_LEAD")
        config2 = get_umwelt_config("tech_lead")
        assert config1 == config2

    def test_unknown_role_returns_developer(self):
        """Unknown role defaults to developer."""
        config = get_umwelt_config("unknown_role")
        assert config == UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER]


# =============================================================================
# compute_node_score Tests
# =============================================================================


class TestComputeNodeScore:
    """Tests for compute_node_score function."""

    @pytest.fixture
    def sample_node(self):
        """Sample node with typical metrics."""
        return {
            "health_score": 0.8,
            "coupling": 0.3,
            "has_violations": False,
            "cyclomatic_complexity": 10,
            "lines_of_code": 200,
        }

    def test_balanced_config_gives_midrange_score(self, sample_node):
        """Balanced weights give reasonable score."""
        config = UmweltConfig()
        score = compute_node_score(sample_node, config)
        assert 0 < score < 1

    def test_high_health_weight_emphasizes_health(self):
        """High health weight emphasizes health score."""
        healthy_node = {"health_score": 0.9, "coupling": 0.5, "lines_of_code": 100}
        unhealthy_node = {"health_score": 0.3, "coupling": 0.5, "lines_of_code": 100}

        config = UmweltConfig(health_weight=1.0, coupling_weight=0.0, size_weight=0.0)
        healthy_score = compute_node_score(healthy_node, config)
        unhealthy_score = compute_node_score(unhealthy_node, config)

        assert healthy_score > unhealthy_score

    def test_reviewer_emphasizes_violations(self):
        """Reviewer config emphasizes violations."""
        node_with_violations = {"health_score": 0.5, "has_violations": True, "lines_of_code": 100}
        node_without = {"health_score": 0.5, "has_violations": False, "lines_of_code": 100}

        config = UMWELT_CONFIGS[GestaltUmwelt.REVIEWER]
        score_with = compute_node_score(node_with_violations, config)
        score_without = compute_node_score(node_without, config)

        # Violations should increase importance for reviewer
        assert score_with > score_without

    def test_performance_emphasizes_complexity(self):
        """Performance config emphasizes complexity."""
        complex_node = {"cyclomatic_complexity": 100, "lines_of_code": 1000, "health_score": 0.5}
        simple_node = {"cyclomatic_complexity": 5, "lines_of_code": 50, "health_score": 0.5}

        config = UMWELT_CONFIGS[GestaltUmwelt.PERFORMANCE]
        complex_score = compute_node_score(complex_node, config)
        simple_score = compute_node_score(simple_node, config)

        assert complex_score > simple_score


# =============================================================================
# filter_node_for_umwelt Tests
# =============================================================================


class TestFilterNodeForUmwelt:
    """Tests for filter_node_for_umwelt function."""

    def test_default_config_shows_all(self):
        """Default config shows all nodes."""
        node = {"name": "foo.bar", "health_score": 0.3}
        config = UmweltConfig()
        assert filter_node_for_umwelt(node, config) is True

    def test_min_health_filters_unhealthy(self):
        """Min health filter removes unhealthy nodes."""
        node = {"name": "foo.bar", "health_score": 0.3}
        config = UmweltConfig(min_health_score=0.5)
        assert filter_node_for_umwelt(node, config) is False

    def test_test_modules_filtered(self):
        """Test modules can be filtered out."""
        test_node = {"name": "foo._tests.test_bar", "health_score": 0.8}
        config = UmweltConfig(show_test_modules=False)
        assert filter_node_for_umwelt(test_node, config) is False

    def test_test_modules_shown_when_enabled(self):
        """Test modules shown when enabled."""
        test_node = {"name": "foo._tests.test_bar", "health_score": 0.8}
        config = UmweltConfig(show_test_modules=True)
        assert filter_node_for_umwelt(test_node, config) is True

    def test_external_deps_filtered(self):
        """External dependencies can be filtered."""
        node = {"name": "requests", "is_external": True, "health_score": 0.8}
        config = UmweltConfig(show_external_deps=False)
        assert filter_node_for_umwelt(node, config) is False

    def test_product_config_filters_tests(self):
        """Product config hides test modules."""
        test_node = {"name": "agents._tests.test_agent", "health_score": 0.8}
        config = UMWELT_CONFIGS[GestaltUmwelt.PRODUCT]
        assert filter_node_for_umwelt(test_node, config) is False

    def test_developer_config_shows_tests(self):
        """Developer config shows test modules."""
        test_node = {"name": "agents._tests.test_agent", "health_score": 0.8}
        config = UMWELT_CONFIGS[GestaltUmwelt.DEVELOPER]
        assert filter_node_for_umwelt(test_node, config) is True


# =============================================================================
# Role-Specific Config Tests
# =============================================================================


class TestRoleSpecificConfigs:
    """Tests that each role has appropriate configuration."""

    def test_tech_lead_emphasizes_health(self):
        """Tech lead config emphasizes health and governance."""
        config = UMWELT_CONFIGS[GestaltUmwelt.TECH_LEAD]
        assert config.health_weight >= 0.8
        assert config.violations_weight >= 0.8

    def test_reviewer_maximizes_violations(self):
        """Reviewer config maximizes violation emphasis."""
        config = UMWELT_CONFIGS[GestaltUmwelt.REVIEWER]
        assert config.violations_weight == 1.0

    def test_product_hides_complexity(self):
        """Product config de-emphasizes technical details."""
        config = UMWELT_CONFIGS[GestaltUmwelt.PRODUCT]
        assert config.complexity_weight < 0.5
        assert config.show_test_modules is False

    def test_security_cares_about_coupling(self):
        """Security config emphasizes coupling (attack surface)."""
        config = UMWELT_CONFIGS[GestaltUmwelt.SECURITY]
        assert config.coupling_weight >= 0.8
        assert config.show_external_deps is True

    def test_performance_emphasizes_complexity(self):
        """Performance config emphasizes complexity."""
        config = UMWELT_CONFIGS[GestaltUmwelt.PERFORMANCE]
        assert config.complexity_weight == 1.0
        assert config.size_weight >= 0.7
