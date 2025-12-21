"""
Tests for Interactive Text core contracts and types.

Tests the foundational types for the Meaning Token Frontend Architecture:
- TokenPattern, Affordance, Observer, TokenDefinition
- MeaningToken abstract base class
- InteractionResult

Feature: meaning-token-frontend
Requirements: 1.1, 1.6
"""

from __future__ import annotations

import re

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    DocumentState,
    InteractionResult,
    Observer,
    ObserverDensity,
    ObserverRole,
    TokenDefinition,
    TokenPattern,
)

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def token_pattern_strategy(draw: st.DrawFn) -> TokenPattern:
    """Generate valid token patterns."""
    name = draw(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz_",
            min_size=1,
            max_size=20,
        )
    )
    # Use simple patterns that are always valid
    pattern_text = draw(
        st.sampled_from(
            [
                r"\w+",
                r"\d+",
                r"[a-z]+",
                r"`[^`]+`",
                r"\[.+?\]",
            ]
        )
    )
    priority = draw(st.integers(min_value=0, max_value=100))

    return TokenPattern(
        name=name,
        regex=re.compile(pattern_text),
        priority=priority,
    )


@st.composite
def affordance_strategy(draw: st.DrawFn) -> Affordance:
    """Generate valid affordances."""
    name = draw(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz_",
            min_size=1,
            max_size=20,
        )
    )
    action = draw(st.sampled_from(list(AffordanceAction)))
    handler = draw(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz._",
            min_size=5,
            max_size=50,
        )
    )
    enabled = draw(st.booleans())

    return Affordance(
        name=name,
        action=action,
        handler=handler,
        enabled=enabled,
    )


@st.composite
def observer_strategy(draw: st.DrawFn) -> Observer:
    """Generate valid observers."""
    capabilities = draw(
        st.frozensets(
            st.sampled_from(["llm", "verification", "network", "storage"]),
            min_size=0,
            max_size=4,
        )
    )
    density = draw(st.sampled_from(list(ObserverDensity)))
    role = draw(st.sampled_from(list(ObserverRole)))

    return Observer.create(
        capabilities=capabilities,
        density=density,
        role=role,
    )


# =============================================================================
# TokenPattern Tests
# =============================================================================


class TestTokenPattern:
    """Tests for TokenPattern dataclass."""

    def test_create_valid_pattern(self) -> None:
        """TokenPattern can be created with valid inputs."""
        pattern = TokenPattern(
            name="test_pattern",
            regex=re.compile(r"\w+"),
            priority=5,
        )
        assert pattern.name == "test_pattern"
        assert pattern.priority == 5

    def test_pattern_matching(self) -> None:
        """TokenPattern regex can match text."""
        pattern = TokenPattern(
            name="word",
            regex=re.compile(r"\b\w+\b"),
        )
        matches = list(pattern.regex.finditer("hello world"))
        assert len(matches) == 2
        assert matches[0].group() == "hello"
        assert matches[1].group() == "world"

    def test_empty_name_raises(self) -> None:
        """TokenPattern with empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            TokenPattern(name="", regex=re.compile(r"\w+"))

    @given(pattern=token_pattern_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_pattern_is_frozen(self, pattern: TokenPattern) -> None:
        """TokenPattern is immutable (frozen dataclass)."""
        with pytest.raises(AttributeError):
            pattern.name = "new_name"  # type: ignore


# =============================================================================
# Affordance Tests
# =============================================================================


class TestAffordance:
    """Tests for Affordance dataclass."""

    def test_create_affordance(self) -> None:
        """Affordance can be created with valid inputs."""
        affordance = Affordance(
            name="click_action",
            action=AffordanceAction.CLICK,
            handler="self.document.token.click",
        )
        assert affordance.name == "click_action"
        assert affordance.action == AffordanceAction.CLICK
        assert affordance.enabled is True  # Default

    def test_affordance_to_dict(self) -> None:
        """Affordance can be serialized to dict."""
        affordance = Affordance(
            name="hover",
            action=AffordanceAction.HOVER,
            handler="self.document.token.hover",
            enabled=True,
            description="Show tooltip",
        )
        result = affordance.to_dict()

        assert result["name"] == "hover"
        assert result["action"] == "hover"
        assert result["handler"] == "self.document.token.hover"
        assert result["enabled"] is True
        assert result["description"] == "Show tooltip"

    @given(affordance=affordance_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_affordance_roundtrip(self, affordance: Affordance) -> None:
        """Affordance to_dict contains all fields."""
        result = affordance.to_dict()
        assert "name" in result
        assert "action" in result
        assert "handler" in result
        assert "enabled" in result


# =============================================================================
# Observer Tests
# =============================================================================


class TestObserver:
    """Tests for Observer dataclass."""

    def test_create_observer(self) -> None:
        """Observer can be created with factory method."""
        observer = Observer.create(
            capabilities=frozenset(["llm", "network"]),
            density=ObserverDensity.COMPACT,
            role=ObserverRole.EDITOR,
        )
        assert observer.id  # Has generated ID
        assert "llm" in observer.capabilities
        assert observer.density == ObserverDensity.COMPACT
        assert observer.role == ObserverRole.EDITOR

    def test_observer_has_capability(self) -> None:
        """Observer.has_capability checks capabilities correctly."""
        observer = Observer.create(capabilities=frozenset(["llm", "network"]))

        assert observer.has_capability("llm") is True
        assert observer.has_capability("network") is True
        assert observer.has_capability("verification") is False

    def test_observer_to_dict(self) -> None:
        """Observer can be serialized to dict."""
        observer = Observer.create(
            capabilities=frozenset(["llm"]),
            density=ObserverDensity.SPACIOUS,
            role=ObserverRole.ADMIN,
        )
        result = observer.to_dict()

        assert result["id"] == observer.id
        assert "llm" in result["capabilities"]
        assert result["density"] == "spacious"
        assert result["role"] == "admin"

    @given(observer=observer_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_observer_unique_ids(self, observer: Observer) -> None:
        """Each Observer.create() generates unique ID."""
        observer2 = Observer.create()
        assert observer.id != observer2.id


# =============================================================================
# TokenDefinition Tests
# =============================================================================


class TestTokenDefinition:
    """Tests for TokenDefinition dataclass."""

    def test_create_token_definition(self) -> None:
        """TokenDefinition can be created with valid inputs."""
        pattern = TokenPattern(name="test", regex=re.compile(r"\w+"))
        affordance = Affordance(
            name="click",
            action=AffordanceAction.CLICK,
            handler="test.handler",
        )
        defn = TokenDefinition(
            name="test_token",
            pattern=pattern,
            affordances=(affordance,),
        )

        assert defn.name == "test_token"
        assert defn.pattern == pattern
        assert len(defn.affordances) == 1

    def test_get_affordance_by_action(self) -> None:
        """TokenDefinition.get_affordance finds affordance by action."""
        click = Affordance(name="click", action=AffordanceAction.CLICK, handler="h1")
        hover = Affordance(name="hover", action=AffordanceAction.HOVER, handler="h2")

        defn = TokenDefinition(
            name="test",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(click, hover),
        )

        assert defn.get_affordance(AffordanceAction.CLICK) == click
        assert defn.get_affordance(AffordanceAction.HOVER) == hover
        assert defn.get_affordance(AffordanceAction.DRAG) is None

    def test_empty_name_raises(self) -> None:
        """TokenDefinition with empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            TokenDefinition(
                name="",
                pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
                affordances=(),
            )


# =============================================================================
# DocumentState Tests
# =============================================================================


class TestDocumentState:
    """Tests for DocumentState enum."""

    def test_all_states_defined(self) -> None:
        """All four document states are defined."""
        states = list(DocumentState)
        assert len(states) == 4
        assert DocumentState.VIEWING in states
        assert DocumentState.EDITING in states
        assert DocumentState.SYNCING in states
        assert DocumentState.CONFLICTING in states

    def test_state_values(self) -> None:
        """Document states have correct string values."""
        assert DocumentState.VIEWING.value == "VIEWING"
        assert DocumentState.EDITING.value == "EDITING"
        assert DocumentState.SYNCING.value == "SYNCING"
        assert DocumentState.CONFLICTING.value == "CONFLICTING"


# =============================================================================
# InteractionResult Tests
# =============================================================================


class TestInteractionResult:
    """Tests for InteractionResult dataclass."""

    def test_success_result(self) -> None:
        """InteractionResult.success_result creates successful result."""
        result = InteractionResult.success_result(data={"key": "value"}, witness_id="w123")

        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.witness_id == "w123"
        assert result.error is None

    def test_not_available_result(self) -> None:
        """InteractionResult.not_available creates unavailable result."""
        result = InteractionResult.not_available("drag")

        assert result.success is False
        assert "drag" in result.error
        assert result.data is None

    def test_failure_result(self) -> None:
        """InteractionResult.failure creates failed result."""
        result = InteractionResult.failure("Something went wrong")

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None

    def test_result_has_timestamp(self) -> None:
        """InteractionResult has timestamp."""
        result = InteractionResult.success_result(data=None)
        assert result.timestamp is not None
