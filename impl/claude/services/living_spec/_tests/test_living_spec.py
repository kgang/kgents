"""
Living Spec Tests: Verify monad laws, polynomial transitions, and sheaf coherence.

These tests validate the core mathematical properties of the Living Spec system.
"""

from dataclasses import dataclass

import pytest

# =============================================================================
# Test: SpecPolynomial State Machine
# =============================================================================


class TestSpecPolynomial:
    """Verify SpecPolynomial state transitions."""

    def test_viewing_to_editing(self):
        """VIEWING + edit → EDITING with enter_monad effect."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        state, effect = SpecPolynomial.transition(SpecState.VIEWING, "edit")
        assert state == SpecState.EDITING
        assert effect.effect_type == "enter_monad"

    def test_editing_to_syncing(self):
        """EDITING + save → SYNCING with start_commit effect."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        state, effect = SpecPolynomial.transition(SpecState.EDITING, "save")
        assert state == SpecState.SYNCING
        assert effect.effect_type == "start_commit"

    def test_syncing_to_witnessing(self):
        """SYNCING + complete → WITNESSING with prompt_witness effect."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        state, effect = SpecPolynomial.transition(SpecState.SYNCING, "complete")
        assert state == SpecState.WITNESSING
        assert effect.effect_type == "prompt_witness"

    def test_witnessing_to_viewing(self):
        """WITNESSING + mark → VIEWING with mark_recorded effect."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        state, effect = SpecPolynomial.transition(SpecState.WITNESSING, "mark")
        assert state == SpecState.VIEWING
        assert effect.effect_type == "mark_recorded"

    def test_invalid_transition_is_noop(self):
        """Invalid transitions return same state with no_op effect."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        state, effect = SpecPolynomial.transition(SpecState.VIEWING, "invalid_action")
        assert state == SpecState.VIEWING
        assert effect.effect_type == "no_op"

    def test_all_states_have_directions(self):
        """Every state should have at least one valid direction."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        for state in SpecState:
            directions = SpecPolynomial.directions(state)
            assert len(directions) > 0, f"{state.name} has no valid directions"

    def test_editing_states(self):
        """Verify which states are considered editing."""
        from services.living_spec.polynomial import SpecPolynomial, SpecState

        assert SpecPolynomial.is_editing(SpecState.EDITING)
        assert SpecPolynomial.is_editing(SpecState.SYNCING)
        assert SpecPolynomial.is_editing(SpecState.CONFLICTING)
        assert not SpecPolynomial.is_editing(SpecState.VIEWING)
        assert not SpecPolynomial.is_editing(SpecState.NAVIGATING)


# =============================================================================
# Test: PortalSpecToken State Machine
# =============================================================================


class TestPortalSpecToken:
    """Verify PortalSpecToken state transitions."""

    def test_create_portal(self):
        """Create portal in COLLAPSED state."""
        from services.living_spec.tokens.portal import PortalSpecToken, PortalState

        portal = PortalSpecToken.create(
            edge_type="tests",
            destinations=["test_a.py", "test_b.py"],
        )
        assert portal.state == PortalState.COLLAPSED
        assert portal.edge_type == "tests"
        assert len(portal.destinations) == 2

    def test_collapse_expanded_portal(self):
        """Collapse transition works."""
        from services.living_spec.tokens.portal import PortalSpecToken, PortalState

        portal = PortalSpecToken.create(
            edge_type="tests",
            destinations=["test_a.py"],
        )
        # Manually set to EXPANDED for test
        object.__setattr__(portal, "_state", PortalState.EXPANDED)

        result = portal.collapse()
        assert portal.state == PortalState.COLLAPSED
        assert result.effect == "collapsed"

    def test_token_type(self):
        """Portal token type is 'portal'."""
        from services.living_spec.tokens.portal import PortalSpecToken

        portal = PortalSpecToken.create("tests", ["a.py"])
        assert portal.token_type == "portal"


# =============================================================================
# Test: Contracts
# =============================================================================


class TestContracts:
    """Verify contract types work correctly."""

    def test_observer_default(self):
        """Default observer has expected properties."""
        from services.living_spec.contracts import Observer, ObserverDensity, ObserverRole

        observer = Observer.default()
        assert observer.id == "default"
        assert observer.role == ObserverRole.DEVELOPER
        assert observer.density == ObserverDensity.COMFORTABLE
        assert "read" in observer.capabilities

    def test_content_delta_compute(self):
        """ContentDelta correctly computes changes."""
        from services.living_spec.contracts import ContentDelta

        delta = ContentDelta.compute(
            "Hello\nWorld",
            "Hello\nNew World\nMore lines",
        )
        assert delta.has_changes
        assert delta.additions > 0

    def test_edit_delta_serialization(self):
        """EditDelta round-trips through serialization."""
        from services.living_spec.contracts import EditDelta

        delta = EditDelta(
            operation="insert",
            position=10,
            new_text="inserted text",
        )
        serialized = delta.serialize()
        restored = EditDelta.deserialize(serialized)

        assert restored.operation == delta.operation
        assert restored.position == delta.position
        assert restored.new_text == delta.new_text

    def test_checkpoint_create(self):
        """Checkpoint creation generates hash."""
        from services.living_spec.contracts import Checkpoint

        cp = Checkpoint.create("test-checkpoint", "# Test Content")
        assert cp.name == "test-checkpoint"
        assert len(cp.content_hash) == 16
        assert cp.id.startswith("cp_")


# =============================================================================
# Test: Tokens
# =============================================================================


class TestTokens:
    """Verify token types work correctly."""

    def test_agentese_path_token(self):
        """AGENTESEPathToken extracts path and context."""
        from services.living_spec.tokens.base import AGENTESEPathToken

        token = AGENTESEPathToken(
            _span=(0, 20),
            _value="`world.town.citizen`",
        )
        assert token.token_type == "agentese_path"
        assert token.path == "world.town.citizen"
        assert token.context == "world"

    def test_task_checkbox_token(self):
        """TaskCheckboxToken detects checked state."""
        from services.living_spec.tokens.base import TaskCheckboxToken

        unchecked = TaskCheckboxToken(_span=(0, 20), _value="- [ ] Do something")
        checked = TaskCheckboxToken(_span=(0, 20), _value="- [x] Done")

        assert not unchecked.is_checked
        assert checked.is_checked
        assert unchecked.task_text == "Do something"
        assert checked.task_text == "Done"

    def test_code_block_token(self):
        """CodeBlockToken extracts language and code."""
        from services.living_spec.tokens.base import CodeBlockToken

        token = CodeBlockToken(
            _span=(0, 50),
            _value="```python\nprint('hello')\n```",
            _metadata={"language": "python"},
        )
        assert token.token_type == "code_block"
        assert token.language == "python"
        assert "print" in token.code


# =============================================================================
# Test: SpecNode
# =============================================================================


class TestSpecNode:
    """Verify SpecNode hypergraph operations."""

    def test_create_spec_node(self):
        """SpecNode creation with path."""
        from services.living_spec.node import SpecKind, SpecNode

        node = SpecNode(path="spec/protocols/k-block.md")
        assert node.path == "spec/protocols/k-block.md"
        assert node.kind == SpecKind.SPEC

    def test_edge_visibility_by_observer(self):
        """Different observers see different edges."""
        from services.living_spec.contracts import Observer, ObserverRole
        from services.living_spec.node import EDGE_VISIBILITY, SpecNode

        # Developer sees tests, imports
        dev_edges = EDGE_VISIBILITY[ObserverRole.DEVELOPER]
        assert "tests" in dev_edges
        assert "imports" in dev_edges

        # Newcomer sees different set
        newcomer_edges = EDGE_VISIBILITY[ObserverRole.NEWCOMER]
        assert "related" in newcomer_edges

    def test_to_dict(self):
        """SpecNode serializes to dict."""
        from services.living_spec.node import SpecNode

        node = SpecNode(path="test/path.md")
        data = node.to_dict()

        assert data["path"] == "test/path.md"
        assert "kind" in data


# =============================================================================
# Test: Sheaf
# =============================================================================


class TestSheaf:
    """Verify SpecSheaf coherence operations."""

    def test_view_types(self):
        """ViewType enum has expected values."""
        from services.living_spec.sheaf import ViewType

        assert ViewType.PROSE.value == 1
        assert ViewType.DIFF.value == 4

    def test_outline_render(self):
        """Outline view extracts headings."""
        from services.living_spec.sheaf import View, ViewType

        view = View(view_type=ViewType.OUTLINE)
        result = view.render("# Heading 1\n## Heading 2\nText")

        assert "headings" in result
        assert len(result["headings"]) == 2
        assert result["headings"][0]["level"] == 1
        assert result["headings"][0]["text"] == "Heading 1"

    def test_diff_render(self):
        """Diff view computes changes."""
        from services.living_spec.sheaf import View, ViewType

        view = View(view_type=ViewType.DIFF)
        result = view.render("New content", base_content="Old content")

        assert "diff" in result
        assert result["has_changes"] == True


# =============================================================================
# Test: AGENTESE Node
# =============================================================================


class TestAGENTESENode:
    """Verify LivingSpecNode operations."""

    def test_get_node_singleton(self):
        """get_living_spec_node returns singleton."""
        from services.living_spec.agentese_node import (
            get_living_spec_node,
            reset_living_spec_node,
        )

        reset_living_spec_node()
        node1 = get_living_spec_node()
        node2 = get_living_spec_node()
        assert node1 is node2

    def test_node_handle(self):
        """Node has correct AGENTESE handle."""
        from services.living_spec.agentese_node import get_living_spec_node

        node = get_living_spec_node()
        assert node.handle == "self.spec"


# =============================================================================
# Placeholder: Monad Laws (require async)
# =============================================================================


class TestMonadLaws:
    """
    Placeholder for monad law tests.

    Full monad law verification requires async tests.
    """

    def test_monad_creation(self):
        """SpecMonad can be created."""
        from services.living_spec.monad import SpecMonad
        from services.living_spec.node import SpecNode

        spec = SpecNode(path="test.md")
        monad = SpecMonad.pure(spec)

        assert monad.spec.path == "test.md"
        assert monad.isolation.name == "PRISTINE"

    def test_monad_bind(self):
        """SpecMonad.bind applies transformation."""
        from services.living_spec.monad import SpecMonad
        from services.living_spec.node import SpecNode

        spec = SpecNode(path="test.md")
        monad = SpecMonad.pure(spec)
        monad.working_content = "hello"
        monad.base_content = "hello"

        result = monad.bind(lambda x: x.upper())
        assert result.working_content == "HELLO"

    def test_monad_checkpoint(self):
        """SpecMonad checkpoint creates restore point."""
        from services.living_spec.monad import SpecMonad
        from services.living_spec.node import SpecNode

        spec = SpecNode(path="test.md")
        monad = SpecMonad.pure(spec)
        monad.working_content = "version 1"

        cp = monad.checkpoint("checkpoint-1")
        assert cp.name == "checkpoint-1"
        assert len(monad.checkpoints) == 1

        # Modify content
        monad.working_content = "version 2"

        # Rewind
        monad.rewind(cp.id)
        assert monad.working_content == "version 1"
