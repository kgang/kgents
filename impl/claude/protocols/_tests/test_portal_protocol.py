"""
Tests for Portal Token Protocol (Phase 4: PortalToken Unification).

Verifies:
1. Both implementations satisfy PortalTokenProtocol
2. Bidirectional conversion via UnifiedPortalBridge
3. Roundtrip conversion preserves protocol fields

Spec: plans/portal-fullstack-integration.md §6 (Phase 4)
"""

import pytest

from protocols.portal_protocol import (
    PortalTokenProtocol,
    ExpandableTokenProtocol,
    satisfies_protocol,
    get_canonical_dict,
)
from protocols.context.outline import PortalToken as OutlinePortalToken
from protocols.file_operad.portal import (
    PortalLink,
    PortalState,
    PortalToken as FilePortalToken,
)
from protocols.context.portal_bridge import UnifiedPortalBridge


# =============================================================================
# Protocol Satisfaction Tests
# =============================================================================


class TestOutlinePortalTokenProtocol:
    """Test that outline.PortalToken satisfies PortalTokenProtocol."""

    def test_structural_typing(self) -> None:
        """Outline token satisfies protocol via structural typing."""
        token = OutlinePortalToken(
            source_path="world.house",
            edge_type="tests",
            destinations=["tests/test_house.py", "tests/test_room.py"],
            expanded=False,
            depth=1,
        )

        # Protocol check using runtime_checkable
        assert satisfies_protocol(token)
        assert isinstance(token, PortalTokenProtocol)

    def test_protocol_properties(self) -> None:
        """All protocol properties are accessible."""
        token = OutlinePortalToken(
            source_path="world.house",
            edge_type="imports",
            destinations=["pathlib.Path", "typing.Any"],
            expanded=True,
            depth=2,
        )

        assert token.edge_type == "imports"
        assert token.path == "pathlib.Path"  # First destination
        assert token.is_expanded is True
        assert token.depth == 2

    def test_property_protocol(self) -> None:
        """Properties are actual properties (not just attributes)."""
        token = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
        )

        # path and is_expanded are computed properties
        assert hasattr(type(token), "path")
        assert hasattr(type(token), "is_expanded")
        assert isinstance(type(token).path, property)
        assert isinstance(type(token).is_expanded, property)

    def test_to_dict_protocol_fields(self) -> None:
        """to_dict() includes all protocol-required fields."""
        token = OutlinePortalToken(
            source_path="self.brain",
            edge_type="enables",
            destinations=["memory.capture"],
            expanded=False,
            depth=0,
        )

        d = token.to_dict()

        # Protocol-required fields
        assert "edge_type" in d
        assert "path" in d
        assert "is_expanded" in d
        assert "depth" in d

        # Values match
        assert d["edge_type"] == "enables"
        assert d["path"] == "memory.capture"
        assert d["is_expanded"] is False
        assert d["depth"] == 0


class TestFileOperadPortalTokenProtocol:
    """Test that file_operad.PortalToken satisfies PortalTokenProtocol."""

    def test_structural_typing(self) -> None:
        """File token satisfies protocol via structural typing."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = FilePortalToken(link=link, depth=1)

        # Protocol check using runtime_checkable
        assert satisfies_protocol(token)
        assert isinstance(token, PortalTokenProtocol)

    def test_satisfies_expandable_protocol(self) -> None:
        """File token also satisfies ExpandableTokenProtocol."""
        link = PortalLink(edge_type="feeds", path="ASHC")
        token = FilePortalToken(link=link, depth=0)

        # Has load() and collapse() methods
        assert isinstance(token, ExpandableTokenProtocol)

    def test_protocol_properties(self) -> None:
        """All protocol properties are accessible."""
        link = PortalLink(
            edge_type="triggered_by",
            path="AGENT_OPERAD/branch",
            note="records alternatives",
        )
        token = FilePortalToken(
            link=link,
            state=PortalState.EXPANDED,
            depth=3,
        )

        assert token.edge_type == "triggered_by"
        assert token.path == "AGENT_OPERAD/branch"
        assert token.is_expanded is True
        assert token.depth == 3

    def test_is_expanded_maps_to_state(self) -> None:
        """is_expanded correctly reflects PortalState."""
        link = PortalLink(edge_type="tests", path="test.op")

        collapsed = FilePortalToken(link=link, state=PortalState.COLLAPSED)
        loading = FilePortalToken(link=link, state=PortalState.LOADING)
        expanded = FilePortalToken(link=link, state=PortalState.EXPANDED)
        error = FilePortalToken(link=link, state=PortalState.ERROR)

        assert collapsed.is_expanded is False
        assert loading.is_expanded is False
        assert expanded.is_expanded is True
        assert error.is_expanded is False

    def test_to_dict_protocol_fields(self) -> None:
        """to_dict() includes all protocol-required fields."""
        link = PortalLink(edge_type="imports", path="pathlib")
        token = FilePortalToken(link=link, depth=1)

        d = token.to_dict()

        # Protocol-required fields
        assert "edge_type" in d
        assert "path" in d
        assert "is_expanded" in d
        assert "depth" in d


# =============================================================================
# Unified Bridge Tests
# =============================================================================


class TestUnifiedPortalBridge:
    """Test bidirectional conversion via UnifiedPortalBridge."""

    def test_outline_to_file_conversion(self) -> None:
        """Convert outline token to file token."""
        bridge = UnifiedPortalBridge()

        outline_token = OutlinePortalToken(
            source_path="world.house",
            edge_type="tests",
            destinations=["tests/test_house.py"],
            expanded=True,
            depth=2,
        )

        file_token = bridge.outline_to_file(outline_token)

        assert file_token.edge_type == "tests"
        assert file_token.path == "tests/test_house.py"
        assert file_token.is_expanded is True
        assert file_token.depth == 2
        assert file_token.state == PortalState.EXPANDED

    def test_file_to_outline_conversion(self) -> None:
        """Convert file token to outline token."""
        bridge = UnifiedPortalBridge()

        link = PortalLink(edge_type="imports", path="pathlib.Path")
        file_token = FilePortalToken(
            link=link,
            state=PortalState.COLLAPSED,
            depth=1,
        )

        outline_token = bridge.file_to_outline(file_token)

        assert outline_token.edge_type == "imports"
        assert outline_token.path == "pathlib.Path"
        assert outline_token.is_expanded is False
        assert outline_token.depth == 1
        assert outline_token.destinations == ["pathlib.Path"]

    def test_roundtrip_preserves_protocol_fields(self) -> None:
        """Roundtrip conversion preserves protocol-defined fields."""
        bridge = UnifiedPortalBridge()

        original = OutlinePortalToken(
            source_path="self.brain",
            edge_type="enables",
            destinations=["memory.capture"],
            expanded=False,
            depth=3,
        )

        roundtripped = bridge.roundtrip_outline(original)

        # Protocol fields preserved
        assert roundtripped.edge_type == original.edge_type
        assert roundtripped.path == original.path
        assert roundtripped.is_expanded == original.is_expanded
        assert roundtripped.depth == original.depth

    def test_roundtrip_approximate(self) -> None:
        """Roundtrip is approximate (some fields differ)."""
        bridge = UnifiedPortalBridge()

        original = OutlinePortalToken(
            source_path="world.house",
            edge_type="tests",
            destinations=["test1.py", "test2.py", "test3.py"],  # Multiple
            expanded=True,
            depth=1,
        )

        roundtripped = bridge.roundtrip_outline(original)

        # Protocol fields preserved
        assert roundtripped.edge_type == original.edge_type
        assert roundtripped.path == original.path  # First destination

        # Non-protocol fields may differ
        # destinations collapsed to single (only first preserved in roundtrip)
        assert len(roundtripped.destinations) == 1
        assert roundtripped.id != original.id  # New ID generated

    def test_are_equivalent_same_impl(self) -> None:
        """are_equivalent works for same implementation."""
        bridge = UnifiedPortalBridge()

        token1 = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
            depth=1,
        )
        token2 = OutlinePortalToken(
            source_path="different",  # Non-protocol field differs
            edge_type="tests",
            destinations=["test.py"],
            depth=1,
        )

        # Same protocol fields
        assert bridge.are_equivalent(token1, token2)

    def test_are_equivalent_cross_impl(self) -> None:
        """are_equivalent works across implementations."""
        bridge = UnifiedPortalBridge()

        outline_token = OutlinePortalToken(
            source_path="",
            edge_type="enables",
            destinations=["target.op"],
            expanded=True,
            depth=2,
        )

        link = PortalLink(edge_type="enables", path="target.op")
        file_token = FilePortalToken(
            link=link,
            state=PortalState.EXPANDED,
            depth=2,
        )

        # Same protocol fields, different implementations
        assert bridge.are_equivalent(outline_token, file_token)

    def test_are_equivalent_different_values(self) -> None:
        """are_equivalent returns False when values differ."""
        bridge = UnifiedPortalBridge()

        token1 = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
            depth=1,
        )
        token2 = OutlinePortalToken(
            source_path="",
            edge_type="imports",  # Different edge_type
            destinations=["test.py"],
            depth=1,
        )

        assert not bridge.are_equivalent(token1, token2)


# =============================================================================
# Exit Criteria Tests (from plan)
# =============================================================================


class TestExitCriteria:
    """Tests matching the plan's exit criteria."""

    def test_both_implementations_satisfy_protocol(self) -> None:
        """
        Exit criteria from plan:
        # Both implementations satisfy the protocol
        from protocols.portal_protocol import PortalTokenProtocol

        outline_token: PortalTokenProtocol = outline.PortalToken(...)
        file_token: PortalTokenProtocol = portal.PortalToken(...)
        """
        # Outline token
        outline_token: PortalTokenProtocol = OutlinePortalToken(
            source_path="test",
            edge_type="tests",
            destinations=["test.py"],
        )

        # File token
        link = PortalLink(edge_type="tests", path="test.py")
        file_token: PortalTokenProtocol = FilePortalToken(link=link)

        # Both satisfy protocol (type annotation accepted)
        assert satisfies_protocol(outline_token)
        assert satisfies_protocol(file_token)

    def test_bridge_roundtrip_conversion(self) -> None:
        """
        Exit criteria from plan:
        # Bridge converts correctly (roundtrip)
        bridge = UnifiedPortalBridge()
        assert bridge.file_to_outline(bridge.outline_to_file(outline_token)) == outline_token
        """
        bridge = UnifiedPortalBridge()

        outline_token = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
            expanded=True,
            depth=2,
        )

        # Roundtrip
        roundtripped = bridge.file_to_outline(bridge.outline_to_file(outline_token))

        # Protocol-level equivalence (not exact equality due to id regeneration)
        assert bridge.are_equivalent(outline_token, roundtripped)


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Test protocol helper functions."""

    def test_satisfies_protocol_with_valid_token(self) -> None:
        """satisfies_protocol returns True for valid tokens."""
        token = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
        )
        assert satisfies_protocol(token)

    def test_satisfies_protocol_with_invalid_object(self) -> None:
        """satisfies_protocol returns False for invalid objects."""
        assert not satisfies_protocol("not a token")
        assert not satisfies_protocol(42)
        assert not satisfies_protocol(None)
        assert not satisfies_protocol({"edge_type": "tests"})  # Dict not enough

    def test_get_canonical_dict(self) -> None:
        """get_canonical_dict extracts protocol fields."""
        token = OutlinePortalToken(
            source_path="world.house",
            edge_type="tests",
            destinations=["test.py"],
            expanded=True,
            depth=2,
        )

        canonical = get_canonical_dict(token)

        assert canonical == {
            "edge_type": "tests",
            "path": "test.py",
            "is_expanded": True,
            "depth": 2,
        }

    def test_get_canonical_dict_cross_impl(self) -> None:
        """get_canonical_dict works across implementations."""
        outline_token = OutlinePortalToken(
            source_path="",
            edge_type="imports",
            destinations=["pathlib"],
            depth=1,
        )

        link = PortalLink(edge_type="imports", path="pathlib")
        file_token = FilePortalToken(link=link, depth=1)

        # Same canonical representation
        assert get_canonical_dict(outline_token) == get_canonical_dict(file_token)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_destinations(self) -> None:
        """Outline token with no destinations."""
        token = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=[],  # Empty
        )

        assert token.path == ""  # Empty string, not error
        assert satisfies_protocol(token)

    def test_deep_nesting(self) -> None:
        """Tokens at deep nesting levels."""
        token = OutlinePortalToken(
            source_path="",
            edge_type="nested",
            destinations=["deep.py"],
            depth=100,
        )

        assert token.depth == 100
        assert satisfies_protocol(token)

    def test_special_characters_in_path(self) -> None:
        """Paths with special characters."""
        token = OutlinePortalToken(
            source_path="world/special-chars_test",
            edge_type="tests",
            destinations=["tests/special chars/test file.py"],
        )

        assert token.path == "tests/special chars/test file.py"
        assert satisfies_protocol(token)

    def test_content_preservation_in_conversion(self) -> None:
        """Content is preserved through conversion (when present)."""
        bridge = UnifiedPortalBridge()

        outline_token = OutlinePortalToken(
            source_path="",
            edge_type="tests",
            destinations=["test.py"],
        )
        outline_token._content = {"test.py": "def test_foo(): pass"}

        file_token = bridge.outline_to_file(outline_token)
        assert file_token._content is not None
        assert "def test_foo(): pass" in file_token._content

        # Roundtrip
        back = bridge.file_to_outline(file_token)
        assert back._content is not None
        assert "def test_foo(): pass" in back._content.get(back.path, "")
