"""
Tests for Portal Expansion Evidence.

These tests verify:
1. PortalExpansionEvidence creation
2. Evidence properties (always weak, source type)
3. Conversion to base Evidence type
4. Factory method from_expansion()

Spec: spec/protocols/portal-token.md section 10.2 (ASHC Evidence)
"""

import pytest

from ..evidence import PortalExpansionEvidence
from ..types import EvidenceStrength


# =============================================================================
# PortalExpansionEvidence Tests
# =============================================================================


class TestPortalExpansionEvidence:
    """Tests for PortalExpansionEvidence dataclass."""

    def test_creation_basic(self) -> None:
        """Basic evidence creation should work."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests/unit",
            edge_type="tests",
            files_opened=("/path/to/test.py",),
        )

        assert evidence.id == "test-id"
        assert evidence.portal_path == "tests/unit"
        assert evidence.edge_type == "tests"
        assert evidence.files_opened == ("/path/to/test.py",)

    def test_strength_always_weak(self) -> None:
        """Portal expansion evidence should always be weak."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests/unit",
            edge_type="tests",
            files_opened=("/path/to/test.py",),
        )

        assert evidence.strength == EvidenceStrength.WEAK

    def test_source_is_portal_expansion(self) -> None:
        """Source should be 'portal_expansion'."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests",
            edge_type="tests",
            files_opened=(),
        )

        assert evidence.source == "portal_expansion"

    def test_claim_includes_edge_type_and_path(self) -> None:
        """Claim should describe the exploration."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests/integration",
            edge_type="tests",
            files_opened=(),
        )

        claim = evidence.claim
        assert "tests" in claim
        assert "tests/integration" in claim

    def test_content_includes_files(self) -> None:
        """Content should include files opened."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests",
            edge_type="tests",
            files_opened=("/a.py", "/b.py"),
        )

        content = evidence.content
        assert "/a.py" in content
        assert "/b.py" in content

    def test_content_handles_no_files(self) -> None:
        """Content should handle empty files list."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests",
            edge_type="tests",
            files_opened=(),
        )

        content = evidence.content
        assert "no files" in content

    def test_to_evidence_conversion(self) -> None:
        """Should convert to base Evidence type."""
        portal_evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests/unit",
            edge_type="tests",
            files_opened=("/test.py",),
            parent_path="/root",
            depth=2,
        )

        base_evidence = portal_evidence.to_evidence()

        assert base_evidence.id == "test-id"
        assert base_evidence.strength == EvidenceStrength.WEAK
        assert base_evidence.source == "portal_expansion"
        assert "portal_path" in base_evidence.metadata
        assert base_evidence.metadata["portal_path"] == "tests/unit"
        assert base_evidence.metadata["depth"] == "2"

    def test_immutability(self) -> None:
        """Evidence should be immutable (frozen dataclass)."""
        evidence = PortalExpansionEvidence(
            id="test-id",
            portal_path="tests",
            edge_type="tests",
            files_opened=(),
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            evidence.portal_path = "modified"


# =============================================================================
# Factory Method Tests
# =============================================================================


class TestPortalExpansionEvidenceFactory:
    """Tests for from_expansion() factory method."""

    def test_from_expansion_basic(self) -> None:
        """from_expansion should create evidence with defaults."""
        evidence = PortalExpansionEvidence.from_expansion(
            portal_path="tests",
            edge_type="tests",
            files_opened=["/test.py"],
        )

        assert evidence.portal_path == "tests"
        assert evidence.edge_type == "tests"
        assert evidence.files_opened == ("/test.py",)
        assert evidence.parent_path == ""
        assert evidence.depth == 0
        # ID should be generated
        assert len(evidence.id) > 0

    def test_from_expansion_with_options(self) -> None:
        """from_expansion should accept all options."""
        evidence = PortalExpansionEvidence.from_expansion(
            portal_path="tests/integration",
            edge_type="tests",
            files_opened=("/a.py", "/b.py"),
            parent_path="/root/src",
            depth=3,
        )

        assert evidence.portal_path == "tests/integration"
        assert evidence.files_opened == ("/a.py", "/b.py")
        assert evidence.parent_path == "/root/src"
        assert evidence.depth == 3

    def test_from_expansion_converts_list_to_tuple(self) -> None:
        """from_expansion should convert list to tuple."""
        evidence = PortalExpansionEvidence.from_expansion(
            portal_path="tests",
            edge_type="tests",
            files_opened=["/a.py", "/b.py"],
        )

        assert isinstance(evidence.files_opened, tuple)
        assert evidence.files_opened == ("/a.py", "/b.py")

    def test_from_expansion_accepts_tuple(self) -> None:
        """from_expansion should accept tuple directly."""
        evidence = PortalExpansionEvidence.from_expansion(
            portal_path="tests",
            edge_type="tests",
            files_opened=("/a.py",),
        )

        assert evidence.files_opened == ("/a.py",)


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
