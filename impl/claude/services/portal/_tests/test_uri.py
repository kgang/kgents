"""
Tests for PortalURI parser.

Tests:
- URI parsing for all resource types
- Fragment parsing
- Implicit file: prefix
- Roundtrip (parse → render → parse)

See: spec/protocols/portal-resource-system.md §II, §VIII.1
"""

from __future__ import annotations

import pytest

from services.portal import PortalURI


class TestPortalURIParsing:
    """Test URI parsing for different resource types."""

    def test_parse_file_explicit(self):
        """File URI with explicit file: prefix."""
        uri = PortalURI.parse("file:spec/protocols/witness.md")

        assert uri.resource_type == "file"
        assert uri.resource_path == "spec/protocols/witness.md"
        assert uri.fragment is None
        assert uri.raw == "file:spec/protocols/witness.md"

    def test_parse_file_implicit(self):
        """File URI with implicit file: prefix."""
        uri = PortalURI.parse("spec/protocols/witness.md")

        assert uri.resource_type == "file"
        assert uri.resource_path == "spec/protocols/witness.md"
        assert uri.fragment is None

    def test_parse_chat_session(self):
        """Chat session URI."""
        uri = PortalURI.parse("chat:session-abc123")

        assert uri.resource_type == "chat"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment is None

    def test_parse_chat_with_turn_fragment(self):
        """Chat URI with turn fragment."""
        uri = PortalURI.parse("chat:session-abc123#turn-5")

        assert uri.resource_type == "chat"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment == "turn-5"

    def test_parse_mark(self):
        """Mark URI."""
        uri = PortalURI.parse("mark:session-abc123#turn-5")

        assert uri.resource_type == "mark"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment == "turn-5"

    def test_parse_crystal(self):
        """Crystal URI."""
        uri = PortalURI.parse("crystal:design-decisions-2025")

        assert uri.resource_type == "crystal"
        assert uri.resource_path == "design-decisions-2025"
        assert uri.fragment is None

    def test_parse_trace(self):
        """Trace URI."""
        uri = PortalURI.parse("trace:session-abc123")

        assert uri.resource_type == "trace"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment is None

    def test_parse_evidence(self):
        """Evidence URI."""
        uri = PortalURI.parse("evidence:session-abc123")

        assert uri.resource_type == "evidence"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment is None

    def test_parse_constitutional(self):
        """Constitutional URI."""
        uri = PortalURI.parse("constitutional:session-abc123")

        assert uri.resource_type == "constitutional"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment is None

    def test_parse_constitutional_with_turn(self):
        """Constitutional URI with turn fragment."""
        uri = PortalURI.parse("constitutional:session-abc123#turn-5")

        assert uri.resource_type == "constitutional"
        assert uri.resource_path == "session-abc123"
        assert uri.fragment == "turn-5"

    def test_parse_witness(self):
        """Witness URI."""
        uri = PortalURI.parse("witness:mark-xyz123")

        assert uri.resource_type == "witness"
        assert uri.resource_path == "mark-xyz123"
        assert uri.fragment is None

    def test_parse_node(self):
        """AGENTESE node URI."""
        uri = PortalURI.parse("node:world.brain.status")

        assert uri.resource_type == "node"
        assert uri.resource_path == "world.brain.status"
        assert uri.fragment is None

    def test_parse_unknown_type(self):
        """Unknown resource type (should still parse)."""
        uri = PortalURI.parse("custom:some-resource")

        assert uri.resource_type == "custom"
        assert uri.resource_path == "some-resource"
        assert uri.fragment is None


class TestFragmentParsing:
    """Test fragment parsing."""

    def test_fragment_turn_number(self):
        """Fragment: turn-N."""
        uri = PortalURI.parse("chat:session-abc123#turn-5")
        assert uri.fragment == "turn-5"

    def test_fragment_mark_id(self):
        """Fragment: mark-ID."""
        uri = PortalURI.parse("trace:session-abc123#mark-xyz")
        assert uri.fragment == "mark-xyz"

    def test_fragment_custom(self):
        """Fragment: custom identifier."""
        uri = PortalURI.parse("file:README.md#installation")
        assert uri.fragment == "installation"

    def test_no_fragment(self):
        """No fragment."""
        uri = PortalURI.parse("file:README.md")
        assert uri.fragment is None

    def test_empty_fragment_ignored(self):
        """Empty fragment (trailing #) is ignored."""
        uri = PortalURI.parse("file:README.md#")
        assert uri.fragment is None


class TestRoundtrip:
    """Test roundtrip: parse → render → parse."""

    def test_roundtrip_file_explicit(self):
        """Roundtrip for explicit file: URI."""
        original = "file:spec/protocols/witness.md"
        uri = PortalURI.parse(original)
        rendered = uri.render()

        assert rendered == original

        # Parse again
        uri2 = PortalURI.parse(rendered)
        assert uri2.resource_type == uri.resource_type
        assert uri2.resource_path == uri.resource_path
        assert uri2.fragment == uri.fragment

    def test_roundtrip_with_fragment(self):
        """Roundtrip for URI with fragment."""
        original = "chat:session-abc123#turn-5"
        uri = PortalURI.parse(original)
        rendered = uri.render()

        assert rendered == original

    def test_roundtrip_all_types(self):
        """Roundtrip for all resource types."""
        test_uris = [
            "file:README.md",
            "chat:session-abc123",
            "chat:session-abc123#turn-5",
            "mark:session-abc123#turn-5",
            "crystal:design-decisions-2025",
            "trace:session-abc123",
            "evidence:session-abc123",
            "constitutional:session-abc123",
            "constitutional:session-abc123#turn-5",
            "witness:mark-xyz123",
            "node:world.brain.status",
        ]

        for original in test_uris:
            uri = PortalURI.parse(original)
            rendered = uri.render()
            assert rendered == original, f"Roundtrip failed for {original}"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_uri(self):
        """Empty URI raises ValueError."""
        with pytest.raises(ValueError, match="URI cannot be empty"):
            PortalURI.parse("")

    def test_whitespace_only_uri(self):
        """Whitespace-only URI raises ValueError."""
        with pytest.raises(ValueError, match="URI cannot be empty"):
            PortalURI.parse("   ")

    def test_empty_resource_type(self):
        """Empty resource type raises ValueError."""
        with pytest.raises(ValueError, match="Resource type cannot be empty"):
            PortalURI.parse(":some-path")

    def test_empty_resource_path(self):
        """Empty resource path raises ValueError."""
        with pytest.raises(ValueError, match="Resource path cannot be empty"):
            PortalURI.parse("chat:")

    def test_whitespace_normalization(self):
        """Whitespace is normalized."""
        uri = PortalURI.parse("  file:README.md  ")

        assert uri.resource_type == "file"
        assert uri.resource_path == "README.md"

    def test_str_representation(self):
        """String representation uses render()."""
        uri = PortalURI.parse("chat:session-abc123#turn-5")
        assert str(uri) == "chat:session-abc123#turn-5"

    def test_repr_representation(self):
        """Repr shows helpful format."""
        uri = PortalURI.parse("chat:session-abc123#turn-5")
        repr_str = repr(uri)

        assert "PortalURI" in repr_str
        assert "chat:session-abc123#turn-5" in repr_str


class TestImplicitFilePrefix:
    """Test implicit file: prefix behavior."""

    def test_relative_path(self):
        """Relative path treated as file."""
        uri = PortalURI.parse("spec/protocols/witness.md")
        assert uri.resource_type == "file"

    def test_absolute_path(self):
        """Absolute path treated as file."""
        uri = PortalURI.parse("/Users/kent/file.txt")
        assert uri.resource_type == "file"

    def test_path_with_dots(self):
        """Path with dots treated as file."""
        uri = PortalURI.parse("../README.md")
        assert uri.resource_type == "file"

    def test_file_with_fragment(self):
        """Implicit file with fragment."""
        uri = PortalURI.parse("README.md#installation")

        assert uri.resource_type == "file"
        assert uri.resource_path == "README.md"
        assert uri.fragment == "installation"
