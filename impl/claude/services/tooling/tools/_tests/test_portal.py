"""
Tests for Portal Tools: PortalTool, PortalWriteTool.

Test Strategy (T-gent Type II: Delta Tests):
- Each test verifies portal behavior with FileEditGuard integration
- Focus on session state tracking and access control
- Verify contract translation and error wrapping

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import pytest

from services.conductor.file_guard import reset_file_guard
from services.tooling.base import CausalityViolation, ToolError
from services.tooling.contracts import PortalRequest, PortalWriteRequest
from services.tooling.tools.portal import (
    PortalTool,
    PortalWriteTool,
    get_open_portals,
    reset_open_portals,
)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset FileEditGuard and portal registry between tests."""
    reset_file_guard()
    reset_open_portals()


class TestPortalTool:
    """Tests for PortalTool adapter."""

    async def test_emits_portal_for_existing_file(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool emits portal with content preview."""
        file = tmp_path / "test.txt"  # type: ignore
        content = "line1\nline2\nline3\nline4\nline5"
        file.write_text(content)

        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(file), edge_type="context", preview_lines=3)
        )

        assert result.destination == str(file)
        assert result.edge_type == "context"
        assert result.exists is True
        assert result.line_count == 5
        assert result.content_full == content
        assert result.content_preview == "line1\nline2\nline3"
        assert result.portal_id != ""

    async def test_emits_portal_with_full_content_if_short(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool includes full content if under preview limit."""
        file = tmp_path / "short.txt"  # type: ignore
        file.write_text("short")

        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(file), preview_lines=10)
        )

        assert result.line_count == 1
        assert result.content_preview is None  # Full content fits in preview
        assert result.content_full == "short"

    async def test_tracks_open_portal_in_registry(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool registers open portal in session state."""
        file = tmp_path / "tracked.txt"  # type: ignore
        file.write_text("tracked content")

        tool = PortalTool()
        result = await tool.invoke(PortalRequest(destination=str(file)))

        portals = get_open_portals()
        assert result.portal_id in portals
        assert portals[result.portal_id].destination == str(file)
        assert portals[result.portal_id].access == "read"

    async def test_emits_portal_with_readwrite_access(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool can open portal with write access."""
        file = tmp_path / "writable.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(file), access="readwrite")
        )

        portals = get_open_portals()
        assert portals[result.portal_id].access == "readwrite"
        assert result.access == "readwrite"

    async def test_emits_portal_for_missing_file(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool emits portal with exists=False for missing file."""
        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(tmp_path / "missing.txt"))  # type: ignore
        )

        assert result.exists is False
        assert result.content_full is None
        assert result.content_preview is None
        assert result.line_count == 0

    async def test_emits_portal_with_custom_edge_type(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool respects custom edge types."""
        file = tmp_path / "spec.md"  # type: ignore
        file.write_text("# Spec")

        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(file), edge_type="implements")
        )

        assert result.edge_type == "implements"

    async def test_emits_portal_with_auto_expand_flag(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool preserves auto_expand flag."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        result = await tool.invoke(
            PortalRequest(destination=str(file), auto_expand=False)
        )

        assert result.auto_expand is False

    async def test_portal_emission_serialization(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalEmission serializes correctly."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        result = await tool.invoke(PortalRequest(destination=str(file)))

        # to_dict
        data = result.to_dict()
        assert data["portal_id"] == result.portal_id
        assert data["destination"] == str(file)
        assert data["exists"] is True

        # from_dict
        from services.tooling.contracts import PortalEmission

        restored = PortalEmission.from_dict(data)
        assert restored.portal_id == result.portal_id
        assert restored.destination == result.destination

    async def test_tool_properties(self) -> None:
        """PortalTool has correct metadata."""
        tool = PortalTool()

        assert tool.name == "portal.emit"
        assert tool.trust_required == 1  # L1
        assert tool.cacheable is False
        assert len(tool.effects) == 1
        assert tool.effects[0][0].value == "reads"


class TestPortalWriteTool:
    """Tests for PortalWriteTool adapter."""

    async def test_writes_through_open_portal(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalWriteTool writes content through open portal."""
        file = tmp_path / "writable.txt"  # type: ignore
        file.write_text("original")

        # Open portal with readwrite access
        portal_tool = PortalTool()
        emission = await portal_tool.invoke(
            PortalRequest(destination=str(file), access="readwrite")
        )

        # Write through portal
        write_tool = PortalWriteTool()
        result = await write_tool.invoke(
            PortalWriteRequest(portal_id=emission.portal_id, content="updated")
        )

        assert result.success is True
        assert result.bytes_written == len("updated")
        assert result.new_content_hash != ""
        assert file.read_text() == "updated"

    async def test_raises_on_portal_not_open(self) -> None:
        """PortalWriteTool raises CausalityViolation if portal not open."""
        write_tool = PortalWriteTool()

        with pytest.raises(CausalityViolation) as exc_info:
            await write_tool.invoke(
                PortalWriteRequest(portal_id="nonexistent", content="content")
            )

        assert "Portal not open" in str(exc_info.value)
        assert exc_info.value.tool_name == "portal.write"

    async def test_raises_on_read_only_portal(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalWriteTool raises CausalityViolation for read-only portal."""
        file = tmp_path / "readonly.txt"  # type: ignore
        file.write_text("original")

        # Open portal with read-only access
        portal_tool = PortalTool()
        emission = await portal_tool.invoke(
            PortalRequest(destination=str(file), access="read")
        )

        # Attempt write
        write_tool = PortalWriteTool()
        with pytest.raises(CausalityViolation) as exc_info:
            await write_tool.invoke(
                PortalWriteRequest(portal_id=emission.portal_id, content="updated")
            )

        assert "read-only" in str(exc_info.value)
        assert file.read_text() == "original"  # Not modified

    async def test_updates_portal_content_hash(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalWriteTool updates portal state after write."""
        file = tmp_path / "tracked.txt"  # type: ignore
        file.write_text("original")

        # Open portal
        portal_tool = PortalTool()
        emission = await portal_tool.invoke(
            PortalRequest(destination=str(file), access="readwrite")
        )

        portals = get_open_portals()
        original_hash = portals[emission.portal_id].content_hash

        # Write through portal
        write_tool = PortalWriteTool()
        result = await write_tool.invoke(
            PortalWriteRequest(portal_id=emission.portal_id, content="updated")
        )

        # Check hash updated
        assert portals[emission.portal_id].content_hash != original_hash
        assert portals[emission.portal_id].content_hash == result.new_content_hash

    async def test_write_preserves_portal_metadata(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalWriteTool preserves edge_type and other metadata."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("original")

        # Open portal with specific edge type
        portal_tool = PortalTool()
        emission = await portal_tool.invoke(
            PortalRequest(
                destination=str(file), edge_type="implements", access="readwrite"
            )
        )

        portals = get_open_portals()
        assert portals[emission.portal_id].edge_type == "implements"

        # Write through portal
        write_tool = PortalWriteTool()
        await write_tool.invoke(
            PortalWriteRequest(portal_id=emission.portal_id, content="updated")
        )

        # Metadata unchanged
        assert portals[emission.portal_id].edge_type == "implements"
        assert portals[emission.portal_id].destination == str(file)

    async def test_tool_properties(self) -> None:
        """PortalWriteTool has correct metadata."""
        tool = PortalWriteTool()

        assert tool.name == "portal.write"
        assert tool.trust_required == 2  # L2
        assert tool.cacheable is False
        assert len(tool.effects) == 1
        assert tool.effects[0][0].value == "writes"


class TestPortalAccessControl:
    """Tests for portal access control patterns."""

    async def test_multiple_portals_tracked_independently(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Multiple portals can be open simultaneously."""
        file1 = tmp_path / "file1.txt"  # type: ignore
        file2 = tmp_path / "file2.txt"  # type: ignore
        file1.write_text("content1")
        file2.write_text("content2")

        tool = PortalTool()
        emission1 = await tool.invoke(PortalRequest(destination=str(file1)))
        emission2 = await tool.invoke(PortalRequest(destination=str(file2)))

        portals = get_open_portals()
        assert len(portals) == 2
        assert emission1.portal_id in portals
        assert emission2.portal_id in portals
        assert portals[emission1.portal_id].destination == str(file1)
        assert portals[emission2.portal_id].destination == str(file2)

    async def test_portal_registry_reset_clears_state(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """reset_open_portals() clears portal registry."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        await tool.invoke(PortalRequest(destination=str(file)))

        assert len(get_open_portals()) == 1

        reset_open_portals()
        assert len(get_open_portals()) == 0

    async def test_readwrite_portal_can_write_multiple_times(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Portal with readwrite access allows multiple writes."""
        file = tmp_path / "multi.txt"  # type: ignore
        file.write_text("v1")

        # Open portal
        portal_tool = PortalTool()
        emission = await portal_tool.invoke(
            PortalRequest(destination=str(file), access="readwrite")
        )

        write_tool = PortalWriteTool()

        # First write
        await write_tool.invoke(
            PortalWriteRequest(portal_id=emission.portal_id, content="v2")
        )
        assert file.read_text() == "v2"

        # Second write
        await write_tool.invoke(
            PortalWriteRequest(portal_id=emission.portal_id, content="v3")
        )
        assert file.read_text() == "v3"


class TestPortalEdgeCases:
    """Tests for portal edge cases and error handling."""

    async def test_portal_to_directory_raises_error(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalTool raises error for directory paths."""
        tool = PortalTool()

        with pytest.raises(ToolError):
            await tool.invoke(PortalRequest(destination=str(tmp_path)))

    async def test_portal_emission_includes_timestamp(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """PortalEmission includes ISO datetime timestamp."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        result = await tool.invoke(PortalRequest(destination=str(file)))

        assert result.emitted_at != ""
        # Verify it's a valid ISO format (will raise if invalid)
        from datetime import datetime

        datetime.fromisoformat(result.emitted_at)

    async def test_portal_unique_ids_per_emission(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Each portal emission gets a unique ID."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("content")

        tool = PortalTool()
        emission1 = await tool.invoke(PortalRequest(destination=str(file)))
        emission2 = await tool.invoke(PortalRequest(destination=str(file)))

        assert emission1.portal_id != emission2.portal_id
