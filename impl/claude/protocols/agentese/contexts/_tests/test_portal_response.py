"""
Tests for PortalResponse canonical response type.

Verifies the contract between frontend and backend for portal operations.

Teaching:
    gotcha: PortalResponse is returned in metadata["result"] when
            response_format="json", NOT as the top-level response.
            The gateway wraps it in {path, aspect, result: ...}.
            (Evidence: test_response_unwrapping)
"""

import pytest

from protocols.agentese.contexts.portal_response import PortalResponse


class TestPortalResponseToDict:
    """Test to_dict serialization."""

    def test_success_response_minimal(self) -> None:
        """Success response with minimal fields."""
        response = PortalResponse(
            success=True,
            path="self.portal",
            aspect="manifest",
        )
        d = response.to_dict()
        assert d["success"] is True
        assert d["path"] == "self.portal"
        assert d["aspect"] == "manifest"
        # Optional fields should not be present
        assert "tree" not in d
        assert "error" not in d

    def test_success_response_with_tree(self) -> None:
        """Success response with tree data."""
        tree_data = {"root": {"path": "/foo/bar.py", "children": []}}
        response = PortalResponse(
            success=True,
            path="self.portal",
            aspect="manifest",
            tree=tree_data,
        )
        d = response.to_dict()
        assert d["tree"] == tree_data

    def test_expand_success_response(self) -> None:
        """Expand success includes expanded_path."""
        response = PortalResponse.expand_success(
            tree={"root": {"path": "test.py"}},
            expanded_path="imports/pathlib",
            evidence_id="mark_123",
        )
        d = response.to_dict()
        assert d["success"] is True
        assert d["aspect"] == "expand"
        assert d["expanded_path"] == "imports/pathlib"
        assert d["evidence_id"] == "mark_123"

    def test_expand_failure_response(self) -> None:
        """Expand failure includes error details."""
        response = PortalResponse.expand_failure(
            portal_path="nonexistent",
            error="Path not found",
        )
        d = response.to_dict()
        assert d["success"] is False
        assert d["error"] == "Path not found"
        assert d["error_code"] == "expansion_failed"

    def test_optional_fields_not_included_when_none(self) -> None:
        """None fields should not appear in dict."""
        response = PortalResponse(
            success=True,
            path="self.portal",
            aspect="manifest",
            trail_id=None,
            evidence_id=None,
        )
        d = response.to_dict()
        assert "trail_id" not in d
        assert "evidence_id" not in d


class TestPortalResponseToText:
    """Test to_text for CLI fallback."""

    def test_success_text(self) -> None:
        """Success response renders as text."""
        response = PortalResponse(
            success=True,
            path="self.portal",
            aspect="manifest",
        )
        text = response.to_text()
        assert "[MANIFEST]" in text
        assert "self.portal" in text

    def test_failure_text(self) -> None:
        """Failure response shows error."""
        response = PortalResponse(
            success=False,
            path="self.portal",
            aspect="expand",
            error="Path not found",
        )
        text = response.to_text()
        assert "[FAILED]" in text
        assert "Path not found" in text

    def test_expand_text_shows_path(self) -> None:
        """Expand success shows the expanded path."""
        response = PortalResponse.expand_success(
            tree={"root": {}},
            expanded_path="imports/os",
        )
        text = response.to_text()
        assert "Expanded: imports/os" in text


class TestFactoryMethods:
    """Test factory methods for common response patterns."""

    def test_manifest_factory(self) -> None:
        """manifest() creates correct response."""
        response = PortalResponse.manifest(
            tree={"root": {"path": "test.py"}},
            observer="developer",
        )
        assert response.success is True
        assert response.aspect == "manifest"
        assert response.tree is not None
        assert response.metadata["observer"] == "developer"

    def test_collapse_success_factory(self) -> None:
        """collapse_success() creates correct response."""
        response = PortalResponse.collapse_success(
            tree={"root": {}},
            collapsed_path="tests",
        )
        assert response.success is True
        assert response.aspect == "collapse"
        assert response.collapsed_path == "tests"

    def test_collapse_failure_factory(self) -> None:
        """collapse_failure() creates correct response."""
        response = PortalResponse.collapse_failure(
            portal_path="missing",
            error="Not expanded",
        )
        assert response.success is False
        assert response.error_code == "collapse_failed"

    def test_trail_factory(self) -> None:
        """trail() creates correct response."""
        response = PortalResponse.trail(
            trail_id="trail_abc123",
            step_count=7,
            name="My Investigation",
        )
        assert response.success is True
        assert response.aspect == "trail"
        assert response.trail_id == "trail_abc123"
        assert response.metadata["step_count"] == 7


class TestRenderableProtocol:
    """Test that PortalResponse satisfies Renderable protocol."""

    def test_has_to_dict(self) -> None:
        """PortalResponse has to_dict method."""
        response = PortalResponse(
            success=True,
            path="test",
            aspect="manifest",
        )
        assert hasattr(response, "to_dict")
        assert callable(response.to_dict)

    def test_has_to_text(self) -> None:
        """PortalResponse has to_text method."""
        response = PortalResponse(
            success=True,
            path="test",
            aspect="manifest",
        )
        assert hasattr(response, "to_text")
        assert callable(response.to_text)

    def test_is_renderable(self) -> None:
        """PortalResponse satisfies Renderable protocol."""
        from protocols.agentese.node import Renderable

        response = PortalResponse(
            success=True,
            path="test",
            aspect="manifest",
        )
        # Protocol check
        assert isinstance(response, Renderable)


class TestPhase2ReadinessFields:
    """Test fields prepared for Phase 2 (Witness Mark Integration)."""

    def test_evidence_id_field_exists(self) -> None:
        """evidence_id field ready for witness marks."""
        response = PortalResponse.expand_success(
            tree={},
            expanded_path="imports",
            evidence_id="mark_witness_123",
        )
        assert response.evidence_id == "mark_witness_123"

    def test_trail_id_field_exists(self) -> None:
        """trail_id field ready for trail persistence."""
        response = PortalResponse.trail(
            trail_id="trail_abc",
            step_count=5,
            name="Test",
        )
        assert response.trail_id == "trail_abc"
