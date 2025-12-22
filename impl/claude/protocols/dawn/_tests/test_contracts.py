"""
Tests for Dawn Cockpit contracts.

Verifies the request/response types and helper functions.
"""

from datetime import datetime

import pytest

from ..contracts import (
    DawnManifestResponse,
    FocusAddRequest,
    FocusAddResponse,
    FocusDemoteRequest,
    FocusItemResponse,
    FocusListResponse,
    FocusMoveResponse,
    FocusPromoteRequest,
    FocusRemoveRequest,
    FocusRemoveResponse,
    SnippetAddRequest,
    SnippetAddResponse,
    SnippetCopyRequest,
    SnippetCopyResponse,
    SnippetListResponse,
    SnippetRemoveRequest,
    SnippetRemoveResponse,
    SnippetResponse,
    focus_item_to_response,
    snippet_to_response,
)
from ..focus import Bucket, FocusItem
from ..snippets import CustomSnippet, QuerySnippet, StaticSnippet


class TestFocusContracts:
    """Tests for focus-related contracts."""

    def test_focus_item_response_frozen(self) -> None:
        """FocusItemResponse is immutable."""
        response = FocusItemResponse(
            id="abc123",
            label="Test Item",
            target="path/to/file.md",
            bucket="today",
            added_at="2025-01-01T00:00:00",
            last_touched="2025-01-01T00:00:00",
            is_stale=False,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            response.label = "Modified"  # type: ignore

    def test_focus_list_response_fields(self) -> None:
        """FocusListResponse has correct fields."""
        items = (
            FocusItemResponse(
                id="1",
                label="Item 1",
                target="target1",
                bucket="today",
                added_at="2025-01-01T00:00:00",
                last_touched="2025-01-01T00:00:00",
                is_stale=False,
            ),
        )
        response = FocusListResponse(
            items=items,
            total_count=1,
            bucket_filter="today",
        )
        assert response.total_count == 1
        assert response.bucket_filter == "today"
        assert len(response.items) == 1

    def test_focus_add_request_defaults(self) -> None:
        """FocusAddRequest has sensible defaults."""
        request = FocusAddRequest(target="path/to/file.md")
        assert request.bucket == "today"
        assert request.label is None

    def test_focus_add_request_with_all_fields(self) -> None:
        """FocusAddRequest accepts all fields."""
        request = FocusAddRequest(
            target="path/to/file.md",
            label="My Task",
            bucket="week",
        )
        assert request.target == "path/to/file.md"
        assert request.label == "My Task"
        assert request.bucket == "week"

    def test_focus_move_response_tracks_buckets(self) -> None:
        """FocusMoveResponse tracks bucket changes."""
        response = FocusMoveResponse(
            item=FocusItemResponse(
                id="1",
                label="Item",
                target="target",
                bucket="today",
                added_at="2025-01-01T00:00:00",
                last_touched="2025-01-01T00:00:00",
                is_stale=False,
            ),
            previous_bucket="week",
            new_bucket="today",
        )
        assert response.previous_bucket == "week"
        assert response.new_bucket == "today"


class TestSnippetContracts:
    """Tests for snippet-related contracts."""

    def test_snippet_response_frozen(self) -> None:
        """SnippetResponse is immutable."""
        response = SnippetResponse(
            id="abc123",
            label="Test Snippet",
            type="static",
            kind="voice_anchor",
            content="Test content",
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            response.label = "Modified"  # type: ignore

    def test_snippet_list_response_counts(self) -> None:
        """SnippetListResponse has all count fields."""
        response = SnippetListResponse(
            snippets=(),
            total_count=10,
            static_count=4,
            query_count=2,
            custom_count=4,
        )
        assert response.total_count == 10
        assert response.static_count == 4
        assert response.query_count == 2
        assert response.custom_count == 4

    def test_snippet_copy_response_with_witness(self) -> None:
        """SnippetCopyResponse includes witness mark ID."""
        response = SnippetCopyResponse(
            snippet_id="abc123",
            label="Test Snippet",
            content="Test content",
            copied=True,
            witness_mark_id="mark-xyz",
        )
        assert response.witness_mark_id == "mark-xyz"

    def test_snippet_copy_response_without_witness(self) -> None:
        """SnippetCopyResponse works without witness."""
        response = SnippetCopyResponse(
            snippet_id="abc123",
            label="Test Snippet",
            content="Test content",
        )
        assert response.witness_mark_id is None
        assert response.copied is True


class TestHelperFunctions:
    """Tests for contract helper functions."""

    def test_focus_item_to_response(self) -> None:
        """focus_item_to_response converts FocusItem correctly."""
        now = datetime.now()
        item = FocusItem(
            id="abc123",
            label="Test Item",
            target="path/to/file.md",
            bucket=Bucket.TODAY,
            added_at=now,
            last_touched=now,
        )
        response = focus_item_to_response(item)

        assert response.id == "abc123"
        assert response.label == "Test Item"
        assert response.target == "path/to/file.md"
        assert response.bucket == "today"
        assert response.added_at == now.isoformat()
        assert response.is_stale is False

    def test_snippet_to_response_static(self) -> None:
        """snippet_to_response converts StaticSnippet correctly."""
        snippet = StaticSnippet(
            id="abc123",
            kind="voice_anchor",
            label="Test Voice",
            content="Voice content",
            source="CLAUDE.md",
        )
        response = snippet_to_response(snippet)

        assert response.id == "abc123"
        assert response.type == "static"
        assert response.kind == "voice_anchor"
        assert response.content == "Voice content"
        assert response.is_loaded is True

    def test_snippet_to_response_query_unloaded(self) -> None:
        """snippet_to_response handles unloaded QuerySnippet."""
        snippet = QuerySnippet(
            id="abc123",
            kind="now",
            label="NOW.md",
            query="self.brain.now",
        )
        response = snippet_to_response(snippet)

        assert response.id == "abc123"
        assert response.type == "query"
        assert response.content is None
        assert response.is_loaded is False

    def test_snippet_to_response_query_loaded(self) -> None:
        """snippet_to_response handles loaded QuerySnippet."""
        snippet = QuerySnippet(
            id="abc123",
            kind="now",
            label="NOW.md",
            query="self.brain.now",
        ).with_content("Loaded content")
        response = snippet_to_response(snippet)

        assert response.content == "Loaded content"
        assert response.is_loaded is True

    def test_snippet_to_response_custom(self) -> None:
        """snippet_to_response converts CustomSnippet correctly."""
        now = datetime.now()
        snippet = CustomSnippet(
            id="abc123",
            label="Custom Note",
            content="My custom content",
            created_at=now,
        )
        response = snippet_to_response(snippet)

        assert response.id == "abc123"
        assert response.type == "custom"
        assert response.kind is None
        assert response.content == "My custom content"


class TestManifestContract:
    """Tests for DawnManifestResponse."""

    def test_manifest_response_fields(self) -> None:
        """DawnManifestResponse has all required fields."""
        response = DawnManifestResponse(
            focus_count=5,
            today_count=2,
            week_count=2,
            someday_count=1,
            snippet_count=10,
            stale_count=1,
        )
        assert response.focus_count == 5
        assert response.today_count == 2
        assert response.stale_count == 1

    def test_manifest_response_optional_fields(self) -> None:
        """DawnManifestResponse optional fields default to None."""
        response = DawnManifestResponse(
            focus_count=0,
            today_count=0,
            week_count=0,
            someday_count=0,
            snippet_count=0,
            stale_count=0,
        )
        assert response.last_coffee is None
        assert response.session_id is None

    def test_manifest_response_frozen(self) -> None:
        """DawnManifestResponse is immutable."""
        response = DawnManifestResponse(
            focus_count=0,
            today_count=0,
            week_count=0,
            someday_count=0,
            snippet_count=0,
            stale_count=0,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            response.focus_count = 10  # type: ignore
