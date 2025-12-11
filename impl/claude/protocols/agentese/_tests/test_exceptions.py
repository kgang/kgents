"""
Tests for AGENTESE Sympathetic Errors

All errors must explain WHY and suggest WHAT TO DO.
"""

import pytest

from ..exceptions import (
    AgentesError,
    PathNotFoundError,
    PathSyntaxError,
    AffordanceError,
    ObserverRequiredError,
    TastefulnessError,
    BudgetExhaustedError,
    CompositionViolationError,
    path_not_found,
    affordance_denied,
    invalid_path_syntax,
)


class TestAgentesError:
    """Tests for base error class."""

    def test_basic_message(self):
        """Error should contain basic message."""
        err = AgentesError("Something went wrong")
        assert "Something went wrong" in str(err)

    def test_with_why(self):
        """Error should include why explanation."""
        err = AgentesError("Failed", why="The moon was not aligned")
        assert "Why: The moon was not aligned" in str(err)

    def test_with_suggestion(self):
        """Error should include suggestion."""
        err = AgentesError("Failed", suggestion="Try turning it off and on")
        assert "Try: Try turning it off and on" in str(err)

    def test_with_related(self):
        """Error should include related paths."""
        err = AgentesError("Failed", related=["path.a", "path.b"])
        assert "Related: path.a, path.b" in str(err)

    def test_full_sympathetic_error(self):
        """Full error with all fields."""
        err = AgentesError(
            "Operation failed",
            why="The resource was exhausted",
            suggestion="Wait and retry",
            related=["resource.pool", "resource.status"],
        )
        msg = str(err)
        assert "Operation failed" in msg
        assert "Why:" in msg
        assert "Try:" in msg
        assert "Related:" in msg


class TestPathNotFoundError:
    """Tests for path resolution errors."""

    def test_basic_path_not_found(self):
        """Basic path not found error."""
        err = PathNotFoundError("'world.castle' not found", path="world.castle")
        assert "world.castle" in str(err)

    def test_auto_generates_why(self):
        """Should auto-generate why from path."""
        err = PathNotFoundError("Not found", path="world.castle")
        assert "No implementation in registry" in str(err)
        assert "spec/world/castle.md" in str(err)

    def test_auto_generates_suggestion(self):
        """Should auto-generate suggestion from path."""
        err = PathNotFoundError("Not found", path="world.castle")
        assert "Create spec/world/castle.md" in str(err)
        assert "world.castle.define" in str(err)

    def test_includes_available_paths(self):
        """Should include similar available paths."""
        err = PathNotFoundError(
            "Not found",
            path="world.castle",
            available=["world.house", "world.garden", "world.palace"],
        )
        # Related field shows top 5
        assert "world.house" in str(err)

    def test_convenience_constructor(self):
        """Test path_not_found convenience function."""
        err = path_not_found("world.castle", similar=["world.house"])
        assert "world.castle" in str(err)
        assert "'world.castle' not found" in str(err)


class TestPathSyntaxError:
    """Tests for path syntax errors."""

    def test_basic_syntax_error(self):
        """Basic syntax error message."""
        err = PathSyntaxError("Path 'invalid' is malformed")
        assert "invalid" in str(err)

    def test_auto_generates_why(self):
        """Should explain correct syntax."""
        err = PathSyntaxError("Bad path")
        assert "<context>.<holon>" in str(err)

    def test_auto_generates_suggestion(self):
        """Should suggest valid examples."""
        err = PathSyntaxError("Bad path")
        assert "world, self, concept, void, time" in str(err)
        assert "world.house.manifest" in str(err)

    def test_convenience_constructor(self):
        """Test invalid_path_syntax convenience function."""
        err = invalid_path_syntax("bad")
        assert "bad" in str(err)
        assert "malformed" in str(err)


class TestAffordanceError:
    """Tests for affordance access errors."""

    def test_basic_affordance_error(self):
        """Basic affordance denied message."""
        err = AffordanceError("Cannot renovate")
        assert "Cannot renovate" in str(err)

    def test_with_observer_info(self):
        """Error includes observer archetype."""
        err = AffordanceError(
            "Denied",
            aspect="renovate",
            observer_archetype="poet",
            available=["describe", "metaphorize"],
        )
        assert "poet" in str(err)
        assert "renovate" in str(err)

    def test_lists_available_affordances(self):
        """Should list what the observer CAN do."""
        err = AffordanceError(
            "Denied",
            aspect="demolish",
            observer_archetype="poet",
            available=["manifest", "describe", "metaphorize"],
        )
        assert "manifest" in str(err)
        assert "describe" in str(err)

    def test_convenience_constructor(self):
        """Test affordance_denied convenience function."""
        err = affordance_denied(
            "renovate",
            "poet",
            ["manifest", "describe"],
        )
        assert "renovate" in str(err)
        assert "poet" in str(err)


class TestObserverRequiredError:
    """Tests for missing observer errors."""

    def test_default_message(self):
        """Default message explains the principle."""
        err = ObserverRequiredError()
        assert "no view from nowhere" in str(err)

    def test_custom_message(self):
        """Custom message preserved."""
        err = ObserverRequiredError("Custom: observer needed")
        assert "Custom: observer needed" in str(err)

    def test_includes_why(self):
        """Should explain WHY observer is needed."""
        err = ObserverRequiredError()
        assert "observe is to disturb" in str(err)

    def test_includes_suggestion(self):
        """Should suggest how to provide observer."""
        err = ObserverRequiredError()
        assert "observer=my_umwelt" in str(err)


class TestTastefulnessError:
    """Tests for tasteful principle violations."""

    def test_basic_tasteful_error(self):
        """Basic tasteful violation."""
        err = TastefulnessError("Spec is too complex")
        assert "Spec is too complex" in str(err)

    def test_includes_validation_errors(self):
        """Should include specific validation failures."""
        err = TastefulnessError(
            "Spec invalid",
            validation_errors=["Missing purpose", "Duplicates existing concept"],
        )
        assert "Missing purpose" in str(err)

    def test_includes_guidance(self):
        """Should guide toward better design."""
        err = TastefulnessError("Bad spec")
        assert "need to exist" in str(err)
        assert "unique value" in str(err)


class TestBudgetExhaustedError:
    """Tests for entropy budget exhaustion."""

    def test_basic_budget_error(self):
        """Basic budget exhausted message."""
        err = BudgetExhaustedError()
        assert "depleted" in str(err)

    def test_shows_remaining_vs_requested(self):
        """Should show remaining vs requested amounts."""
        err = BudgetExhaustedError(
            "Out of entropy",
            remaining=0.1,
            requested=0.5,
        )
        assert "0.50" in str(err) or "0.5" in str(err)
        assert "0.10" in str(err) or "0.1" in str(err)

    def test_suggests_recovery(self):
        """Should suggest how to recover budget."""
        err = BudgetExhaustedError()
        assert "void.entropy.pour" in str(err)
        assert "void.gratitude.tithe" in str(err)


class TestCompositionViolationError:
    """Tests for category law violations."""

    def test_basic_composition_error(self):
        """Basic composition violation."""
        err = CompositionViolationError("Array return breaks pipeline")
        assert "Array return" in str(err)

    def test_indicates_law_violated(self):
        """Should indicate which law was violated."""
        err = CompositionViolationError(
            "Pipeline broken",
            law_violated="associativity",
        )
        assert "associativity" in str(err)

    def test_suggests_alternatives(self):
        """Should suggest alternatives to arrays."""
        err = CompositionViolationError("Arrays bad")
        assert "Iterator" in str(err) or "stream" in str(err)


class TestSympatheticErrorPrinciple:
    """
    Meta-tests ensuring all errors follow the Sympathetic Error Principle.

    Every error type should provide context that helps, not just fails.
    """

    @pytest.mark.parametrize(
        "error_class,args",
        [
            (PathNotFoundError, ("Not found", {"path": "world.x"})),
            (PathSyntaxError, ("Bad syntax",)),
            (AffordanceError, ("Denied", {"aspect": "x", "available": ["y"]})),
            (ObserverRequiredError, ()),
            (TastefulnessError, ("Bad spec",)),
            (BudgetExhaustedError, ()),
            (CompositionViolationError, ("Law broken",)),
        ],
    )
    def test_error_is_sympathetic(self, error_class, args):
        """Every error should have helpful content."""
        if len(args) == 2:
            msg, kwargs = args
            err = error_class(msg, **kwargs)
        elif len(args) == 1:
            err = error_class(args[0])
        else:
            err = error_class()

        error_str = str(err)

        # Every error should have SOME guidance
        # (either why, suggestion, or related)
        has_why = "Why:" in error_str
        has_try = "Try:" in error_str
        has_related = "Related:" in error_str

        assert has_why or has_try or has_related, (
            f"{error_class.__name__} is not sympathetic: {error_str}"
        )

    def test_all_errors_are_agentes_errors(self):
        """All custom errors should inherit from AgentesError."""
        error_classes = [
            PathNotFoundError,
            PathSyntaxError,
            AffordanceError,
            ObserverRequiredError,
            TastefulnessError,
            BudgetExhaustedError,
            CompositionViolationError,
        ]

        for cls in error_classes:
            assert issubclass(cls, AgentesError), (
                f"{cls.__name__} should inherit AgentesError"
            )
