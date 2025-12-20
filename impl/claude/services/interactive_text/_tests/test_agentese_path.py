"""
Tests for AGENTESEPath Token Implementation.

Tests the AGENTESEPathToken class including:
- Token creation and properties
- Affordance generation
- Hover, click, right-click, drag actions
- Ghost token handling

Feature: meaning-token-frontend
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

from __future__ import annotations

import pytest

from services.interactive_text.contracts import (
    AffordanceAction,
    Observer,
    ObserverDensity,
    ObserverRole,
)
from services.interactive_text.tokens.agentese_path import (
    AGENTESEPathToken,
    ContextMenuResult,
    DragResult,
    HoverInfo,
    NavigationResult,
    PolynomialState,
    create_agentese_path_token,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer.create(
        capabilities=frozenset(["llm", "network"]),
        density=ObserverDensity.COMFORTABLE,
        role=ObserverRole.EDITOR,
    )


@pytest.fixture
def admin_observer() -> Observer:
    """Create an admin observer."""
    return Observer.create(
        capabilities=frozenset(["llm", "network", "verification"]),
        density=ObserverDensity.COMFORTABLE,
        role=ObserverRole.ADMIN,
    )


@pytest.fixture
def token() -> AGENTESEPathToken:
    """Create a test AGENTESEPath token."""
    return AGENTESEPathToken(
        source_text="`world.town.citizen`",
        source_position=(0, 20),
        path="world.town.citizen",
        exists=True,
    )


@pytest.fixture
def ghost_token() -> AGENTESEPathToken:
    """Create a ghost AGENTESEPath token."""
    return AGENTESEPathToken(
        source_text="`world.nonexistent.path`",
        source_position=(0, 24),
        path="world.nonexistent.path",
        exists=False,
    )


# =============================================================================
# Token Creation Tests
# =============================================================================


class TestAGENTESEPathTokenCreation:
    """Tests for AGENTESEPathToken creation."""

    def test_create_token(self, token: AGENTESEPathToken) -> None:
        """Token can be created with valid inputs."""
        assert token.token_type == "agentese_path"
        assert token.source_text == "`world.town.citizen`"
        assert token.source_position == (0, 20)
        assert token.path == "world.town.citizen"
        assert token.exists is True
        assert token.is_ghost is False

    def test_token_context_parsing(self, token: AGENTESEPathToken) -> None:
        """Token correctly parses context and segments."""
        assert token.context == "world"
        assert token.segments == ["town", "citizen"]

    def test_token_id(self, token: AGENTESEPathToken) -> None:
        """Token has correct ID format."""
        assert token.token_id == "agentese_path:0:20"

    def test_create_from_match(self) -> None:
        """Token can be created from regex match."""
        import re
        text = "See `self.memory.capture` for details"
        match = AGENTESEPathToken.PATH_PATTERN.search(text)
        assert match is not None

        token = AGENTESEPathToken.from_match(match)
        assert token.path == "self.memory.capture"
        assert token.context == "self"
        assert token.segments == ["memory", "capture"]

    def test_create_ghost_token(self, ghost_token: AGENTESEPathToken) -> None:
        """Ghost token has correct properties."""
        assert ghost_token.exists is False
        assert ghost_token.is_ghost is True

    def test_factory_function(self) -> None:
        """create_agentese_path_token factory works correctly."""
        token = create_agentese_path_token("`concept.agent.compose`")
        assert token is not None
        assert token.path == "concept.agent.compose"
        assert token.context == "concept"

    def test_factory_returns_none_for_invalid(self) -> None:
        """Factory returns None for non-matching text."""
        token = create_agentese_path_token("no path here")
        assert token is None

    def test_all_contexts_recognized(self) -> None:
        """All five contexts are recognized."""
        contexts = ["world", "self", "concept", "void", "time"]
        for ctx in contexts:
            token = create_agentese_path_token(f"`{ctx}.test.path`")
            assert token is not None, f"Failed to recognize context: {ctx}"
            assert token.context == ctx


# =============================================================================
# Affordance Tests
# =============================================================================


class TestAGENTESEPathAffordances:
    """Tests for AGENTESEPath affordances."""

    @pytest.mark.asyncio
    async def test_get_affordances(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Token returns expected affordances."""
        affordances = await token.get_affordances(observer)

        # Should have hover, click, right-click, drag
        actions = {a.action for a in affordances}
        assert AffordanceAction.HOVER in actions
        assert AffordanceAction.CLICK in actions
        assert AffordanceAction.RIGHT_CLICK in actions
        assert AffordanceAction.DRAG in actions

    @pytest.mark.asyncio
    async def test_affordances_enabled_for_existing_path(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """All affordances enabled for existing path."""
        affordances = await token.get_affordances(observer)

        # All should be enabled for existing path
        assert all(a.enabled for a in affordances)

    @pytest.mark.asyncio
    async def test_ghost_token_reduced_affordances(
        self, ghost_token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Ghost token has reduced affordances."""
        affordances = await ghost_token.get_affordances(observer)

        # Only hover and click should be enabled
        enabled_actions = {a.action for a in affordances if a.enabled}
        assert AffordanceAction.HOVER in enabled_actions
        assert AffordanceAction.CLICK in enabled_actions

        # Right-click and drag should be disabled
        disabled_actions = {a.action for a in affordances if not a.enabled}
        assert AffordanceAction.RIGHT_CLICK in disabled_actions
        assert AffordanceAction.DRAG in disabled_actions


# =============================================================================
# Action Tests
# =============================================================================


class TestAGENTESEPathActions:
    """Tests for AGENTESEPath action handling."""

    @pytest.mark.asyncio
    async def test_hover_returns_polynomial_state(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Hover action returns polynomial state.
        
        Requirements: 5.2
        """
        result = await token.on_interact(AffordanceAction.HOVER, observer)

        assert result.success is True
        assert isinstance(result.data, HoverInfo)
        assert result.data.title == "world.town.citizen"
        assert isinstance(result.data.content, PolynomialState)
        assert result.data.is_ghost is False

    @pytest.mark.asyncio
    async def test_hover_ghost_token(
        self, ghost_token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Hover on ghost token returns ghost info.
        
        Requirements: 5.6
        """
        result = await ghost_token.on_interact(AffordanceAction.HOVER, observer)

        assert result.success is True
        assert isinstance(result.data, HoverInfo)
        assert result.data.is_ghost is True
        assert "not yet implemented" in result.data.content.lower()

    @pytest.mark.asyncio
    async def test_click_navigates(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Click action navigates to path's Habitat.
        
        Requirements: 5.3
        """
        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, NavigationResult)
        assert result.data.success is True
        assert result.data.path == "world.town.citizen"
        assert result.data.habitat is not None

    @pytest.mark.asyncio
    async def test_click_ghost_token_fails(
        self, ghost_token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Click on ghost token returns error.
        
        Requirements: 5.6
        """
        result = await ghost_token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True  # Action executed
        assert isinstance(result.data, NavigationResult)
        assert result.data.success is False
        assert "does not exist" in result.data.error.lower()

    @pytest.mark.asyncio
    async def test_right_click_shows_context_menu(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Right-click shows context menu.
        
        Requirements: 5.4
        """
        result = await token.on_interact(AffordanceAction.RIGHT_CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, ContextMenuResult)
        assert result.data.path == "world.town.citizen"

        # Should have copy, invoke, view_source options
        option_actions = {opt["action"] for opt in result.data.options}
        assert "copy" in option_actions
        assert "invoke" in option_actions
        assert "view_source" in option_actions

    @pytest.mark.asyncio
    async def test_right_click_admin_has_edit(
        self, token: AGENTESEPathToken, admin_observer: Observer
    ) -> None:
        """Admin gets edit option in context menu."""
        result = await token.on_interact(AffordanceAction.RIGHT_CLICK, admin_observer)

        assert result.success is True
        option_actions = {opt["action"] for opt in result.data.options}
        assert "edit" in option_actions

    @pytest.mark.asyncio
    async def test_drag_prefills_repl(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Drag action pre-fills REPL with path.
        
        Requirements: 5.5
        """
        result = await token.on_interact(AffordanceAction.DRAG, observer)

        assert result.success is True
        assert isinstance(result.data, DragResult)
        assert result.data.path == "world.town.citizen"
        assert "world.town.citizen" in result.data.template


# =============================================================================
# Projection Tests
# =============================================================================


class TestAGENTESEPathProjection:
    """Tests for AGENTESEPath projection."""

    @pytest.mark.asyncio
    async def test_project_cli(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """CLI projection uses Rich markup."""
        result = await token.project("cli", observer)

        assert "[cyan]" in result
        assert "`world.town.citizen`" in result

    @pytest.mark.asyncio
    async def test_project_cli_ghost(
        self, ghost_token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Ghost token CLI projection uses dim styling."""
        result = await ghost_token.project("cli", observer)

        assert "[dim" in result
        assert "italic" in result

    @pytest.mark.asyncio
    async def test_project_json(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """JSON projection returns structured data."""
        result = await token.project("json", observer)

        assert isinstance(result, dict)
        assert result["type"] == "agentese_path"
        assert result["path"] == "world.town.citizen"
        assert result["context"] == "world"
        assert result["segments"] == ["town", "citizen"]
        assert result["is_ghost"] is False

    @pytest.mark.asyncio
    async def test_project_web(
        self, token: AGENTESEPathToken, observer: Observer
    ) -> None:
        """Web projection returns source text."""
        result = await token.project("web", observer)

        assert result == "`world.town.citizen`"


# =============================================================================
# Serialization Tests
# =============================================================================


class TestAGENTESEPathSerialization:
    """Tests for AGENTESEPath serialization."""

    def test_to_dict(self, token: AGENTESEPathToken) -> None:
        """Token can be serialized to dict."""
        result = token.to_dict()

        assert result["token_type"] == "agentese_path"
        assert result["source_text"] == "`world.town.citizen`"
        assert result["path"] == "world.town.citizen"
        assert result["context"] == "world"
        assert result["segments"] == ["town", "citizen"]
        assert result["exists"] is True
        assert result["is_ghost"] is False

    def test_polynomial_state_to_dict(self) -> None:
        """PolynomialState can be serialized."""
        state = PolynomialState(
            position="READY",
            valid_inputs=frozenset(["invoke", "query"]),
            description="Test state",
        )
        result = state.to_dict()

        assert result["position"] == "READY"
        assert set(result["valid_inputs"]) == {"invoke", "query"}
        assert result["description"] == "Test state"

    def test_hover_info_to_dict(self) -> None:
        """HoverInfo can be serialized."""
        info = HoverInfo(
            title="test.path",
            content="Test content",
            actions=["action1", "action2"],
        )
        result = info.to_dict()

        assert result["title"] == "test.path"
        assert result["content"] == "Test content"
        assert result["actions"] == ["action1", "action2"]
        assert result["is_ghost"] is False

    def test_navigation_result_to_dict(self) -> None:
        """NavigationResult can be serialized."""
        nav = NavigationResult(
            success=True,
            path="test.path",
            habitat={"type": "node"},
        )
        result = nav.to_dict()

        assert result["success"] is True
        assert result["path"] == "test.path"
        assert result["habitat"] == {"type": "node"}
