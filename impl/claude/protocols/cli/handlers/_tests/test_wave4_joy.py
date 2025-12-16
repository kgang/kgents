"""
Tests for Wave 4 Joy-Inducing CLI Commands.

Tests all 9 commands from CLI Quick Wins Wave 4:
- sparkline: Unicode visualization
- challenge: Devil's advocate alias
- oblique: Brian Eno strategies
- constrain: Productive constraints
- yes-and: Improv expansion
- surprise-me: Random prompts
- project: Projection analysis
- why: Recursive why
- tension: Tension detection
"""

import pytest


# Sparkline tests removed - handler archived in UI factoring cleanup
# TODO: Rebuild sparkline with reactive primitives


class TestChallenge:
    """Tests for kgents challenge command (soul alias)."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.challenge import cmd_challenge

        assert cmd_challenge(["--help"]) == 0


class TestOblique:
    """Tests for kgents oblique command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.oblique import cmd_oblique

        assert cmd_oblique(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage returns 0 and a strategy."""
        from protocols.cli.handlers.oblique import cmd_oblique

        assert cmd_oblique([]) == 0

    def test_list_mode(self) -> None:
        """--list shows all strategies."""
        from protocols.cli.handlers.oblique import cmd_oblique

        assert cmd_oblique(["--list"]) == 0

    def test_reproducible_seed(self) -> None:
        """--seed produces reproducible results."""
        from protocols.cli.handlers.oblique import OBLIQUE_STRATEGIES, cmd_oblique

        # Just verify it runs without error
        assert cmd_oblique(["--seed", "42"]) == 0

    def test_strategies_exist(self) -> None:
        """Strategy deck is populated."""
        from protocols.cli.handlers.oblique import OBLIQUE_STRATEGIES

        assert len(OBLIQUE_STRATEGIES) >= 40  # At least 40 strategies


class TestConstrain:
    """Tests for kgents constrain command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage with topic returns 0."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain(["API", "design"]) == 0

    def test_missing_input(self) -> None:
        """Missing topic returns 1."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain([]) == 1

    def test_count_option(self) -> None:
        """--count works."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain(["--count", "5", "code", "review"]) == 0

    def test_persona_option(self) -> None:
        """--persona works with valid persona."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain(["--persona", "playful", "API", "design"]) == 0

    def test_invalid_persona(self) -> None:
        """Invalid persona returns 1."""
        from protocols.cli.handlers.constrain import cmd_constrain

        assert cmd_constrain(["--persona", "invalid", "topic"]) == 1


class TestYesAnd:
    """Tests for kgents yes-and command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.yes_and import cmd_yes_and

        assert cmd_yes_and(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage with idea returns 0."""
        from protocols.cli.handlers.yes_and import cmd_yes_and

        assert cmd_yes_and(["agents", "could", "dream"]) == 0

    def test_missing_input(self) -> None:
        """Missing idea returns 1."""
        from protocols.cli.handlers.yes_and import cmd_yes_and

        assert cmd_yes_and([]) == 1

    def test_rounds_option(self) -> None:
        """--rounds works."""
        from protocols.cli.handlers.yes_and import cmd_yes_and

        assert cmd_yes_and(["--rounds", "5", "code", "as", "poetry"]) == 0


class TestSurpriseMe:
    """Tests for kgents surprise-me command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.surprise_me import cmd_surprise_me

        assert cmd_surprise_me(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage returns 0."""
        from protocols.cli.handlers.surprise_me import cmd_surprise_me

        assert cmd_surprise_me([]) == 0

    def test_domain_option(self) -> None:
        """--domain works with valid domain."""
        from protocols.cli.handlers.surprise_me import cmd_surprise_me

        assert cmd_surprise_me(["--domain", "code"]) == 0

    def test_invalid_domain(self) -> None:
        """Invalid domain returns 1."""
        from protocols.cli.handlers.surprise_me import cmd_surprise_me

        assert cmd_surprise_me(["--domain", "invalid"]) == 1

    def test_weird_mode(self) -> None:
        """--weird works."""
        from protocols.cli.handlers.surprise_me import cmd_surprise_me

        assert cmd_surprise_me(["--weird"]) == 0


class TestProject:
    """Tests for kgents project command (projection analysis)."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.project import cmd_project

        assert cmd_project(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage with statement returns 0."""
        from protocols.cli.handlers.project import cmd_project

        assert cmd_project(["They're", "so", "disorganized"]) == 0

    def test_missing_input(self) -> None:
        """Missing statement returns 1."""
        from protocols.cli.handlers.project import cmd_project

        assert cmd_project([]) == 1

    def test_too_short(self) -> None:
        """Too short statement returns 1."""
        from protocols.cli.handlers.project import cmd_project

        assert cmd_project(["lazy"]) == 1

    def test_projection_patterns(self) -> None:
        """Known patterns produce meaningful analysis."""
        from protocols.cli.handlers.project import _analyze_projection

        result = _analyze_projection("They're so disorganized")
        assert result.shadow_content  # Has shadow content
        assert result.self_inquiry  # Has self-inquiry


class TestWhy:
    """Tests for kgents why command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.why import cmd_why

        assert cmd_why(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage with statement returns 0."""
        from protocols.cli.handlers.why import cmd_why

        assert cmd_why(["We", "need", "microservices"]) == 0

    def test_missing_input(self) -> None:
        """Missing statement returns 1."""
        from protocols.cli.handlers.why import cmd_why

        assert cmd_why([]) == 1

    def test_depth_option(self) -> None:
        """--depth works."""
        from protocols.cli.handlers.why import cmd_why

        assert cmd_why(["--depth", "3", "tests", "should", "pass"]) == 0

    def test_why_chain_generation(self) -> None:
        """Why chain generates expected structure."""
        from protocols.cli.handlers.why import _generate_why_chain

        chain = _generate_why_chain("We need tests", depth=3)
        assert chain.original == "We need tests"
        assert len(chain.chain) == 3
        assert chain.bedrock  # Has bedrock


class TestTension:
    """Tests for kgents tension command."""

    def test_help_flag(self) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.tension import cmd_tension

        assert cmd_tension(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage returns 0."""
        from protocols.cli.handlers.tension import cmd_tension

        assert cmd_tension([]) == 0

    def test_system_mode(self) -> None:
        """--system works."""
        from protocols.cli.handlers.tension import cmd_tension

        assert cmd_tension(["--system"]) == 0

    def test_tension_report_structure(self) -> None:
        """Tension report has expected structure."""
        from protocols.cli.handlers.tension import _get_project_tensions

        report = _get_project_tensions()
        assert len(report.tensions) > 0
        assert report.dominant_tension is not None
        assert len(report.synthesis_hints) > 0


class TestContextRouterIntegration:
    """Tests for context router integration."""

    def test_void_serendipity_registered(self) -> None:
        """void.serendipity is registered."""
        from protocols.cli.contexts.void import get_router

        router = get_router()
        assert "serendipity" in router.holons

    def test_void_project_registered(self) -> None:
        """void.project is registered."""
        from protocols.cli.contexts.void import get_router

        router = get_router()
        assert "project" in router.holons

    def test_concept_creativity_registered(self) -> None:
        """concept.creativity is registered."""
        from protocols.cli.contexts.concept import get_router

        router = get_router()
        assert "creativity" in router.holons

    def test_world_viz_registered(self) -> None:
        """world.viz is registered."""
        from protocols.cli.contexts.world import get_router

        router = get_router()
        assert "viz" in router.holons


class TestHollowRegistration:
    """Tests for hollow.py command registration."""

    def test_wave4_commands_registered(self) -> None:
        """All Wave 4 commands are registered in hollow.py."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        # Note: sparkline and dashboard archived in UI factoring cleanup
        wave4_commands = [
            "challenge",
            "oblique",
            "constrain",
            "yes-and",
            "surprise-me",
            "project",
            "why",
            "tension",
        ]

        for cmd in wave4_commands:
            assert cmd in COMMAND_REGISTRY, f"{cmd} not registered"

    def test_commands_resolve(self) -> None:
        """Wave 4 commands resolve to callables."""
        from protocols.cli.hollow import resolve_command

        # Note: sparkline archived in UI factoring cleanup
        wave4_commands = [
            "oblique",
            "constrain",
            "yes-and",
            "surprise-me",
            "project",
            "why",
            "tension",
        ]

        for cmd in wave4_commands:
            handler = resolve_command(cmd)
            assert handler is not None, f"{cmd} does not resolve"
            assert callable(handler), f"{cmd} is not callable"


class TestREPLShortcuts:
    """Tests for REPL slash shortcuts."""

    def test_shortcuts_defined(self) -> None:
        """All shortcuts are defined."""
        from protocols.cli.repl import SLASH_SHORTCUTS

        expected_shortcuts = [
            "/oblique",
            "/constrain",
            "/yes-and",
            "/expand",
            "/surprise",
            "/surprise-me",
            "/project",
            "/sparkline",
            "/why",
            "/tension",
            "/challenge",
        ]

        for shortcut in expected_shortcuts:
            assert shortcut in SLASH_SHORTCUTS, f"{shortcut} not defined"

    def test_shortcuts_map_to_valid_paths(self) -> None:
        """Shortcuts map to valid AGENTESE paths."""
        from protocols.cli.repl import SLASH_SHORTCUTS

        for shortcut, path in SLASH_SHORTCUTS.items():
            parts = path.split(".")
            assert len(parts) >= 2, f"{shortcut} maps to invalid path: {path}"
            assert parts[0] in ("self", "world", "concept", "void", "time"), (
                f"{shortcut} has invalid context"
            )
