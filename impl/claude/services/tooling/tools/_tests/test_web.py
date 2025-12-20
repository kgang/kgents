"""
Tests for Web Tools: WebFetchTool, WebSearchTool.

Test Strategy (T-gent Type II: Delta Tests):
- Focus on caching, URL normalization, and redirect detection
- Mock httpx for network isolation
- Verify tool metadata and contract translation

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.tooling.base import ToolCategory, ToolEffect, ToolError
from services.tooling.contracts import WebFetchRequest, WebSearchQuery
from services.tooling.tools.web import (
    URLCache,
    WebFetchTool,
    WebSearchTool,
)


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    """Reset the URL cache between tests."""
    URLCache.reset()


class TestWebFetchToolURLNormalization:
    """Tests for WebFetchTool URL handling."""

    async def test_upgrades_http_to_https(self) -> None:
        """WebFetchTool upgrades http:// to https://."""
        tool = WebFetchTool()

        # Mock httpx
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tool.invoke(WebFetchRequest(url="http://example.com", prompt="Test"))

        # Verify the result URL is https
        assert result.url.startswith("https://")

    async def test_detects_cross_host_redirect(self) -> None:
        """WebFetchTool detects cross-host redirects."""
        tool = WebFetchTool()

        # Mock httpx with redirect to different host
        mock_response = MagicMock()
        mock_response.text = "<html><body>Redirected</body></html>"
        mock_response.url = "https://different-host.com/page"  # Different host
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tool.invoke(WebFetchRequest(url="https://example.com", prompt="Test"))

        # Should detect redirect and provide redirect URL
        assert result.redirect_url == "https://different-host.com/page"
        assert "Redirected to different host" in result.content


class TestWebFetchToolCaching:
    """Tests for WebFetchTool caching."""

    async def test_caches_responses(self) -> None:
        """WebFetchTool caches for 15 minutes."""
        tool = WebFetchTool()

        # Mock httpx
        mock_response = MagicMock()
        mock_response.text = "<html><body>Cached content</body></html>"
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            # First fetch
            result1 = await tool.invoke(WebFetchRequest(url="https://example.com", prompt="Test"))
            assert result1.cached is False

            # Second fetch (should hit cache)
            result2 = await tool.invoke(WebFetchRequest(url="https://example.com", prompt="Test"))
            assert result2.cached is True

        # Verify httpx was only called once
        assert mock_client.get.call_count == 1

    async def test_cache_cleared_on_reset(self) -> None:
        """URLCache.reset() clears cached content."""
        cache = URLCache()
        cache.set("https://example.com", "content")

        assert cache.get("https://example.com", ttl_seconds=900) is not None

        URLCache.reset()

        assert cache.get("https://example.com", ttl_seconds=900) is None


class TestWebFetchToolHTMLConversion:
    """Tests for WebFetchTool HTML to Markdown conversion."""

    async def test_converts_html_to_markdown(self) -> None:
        """WebFetchTool converts HTML to Markdown."""
        tool = WebFetchTool()

        # Mock httpx
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Title</h1><p>Paragraph</p></body></html>"
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tool.invoke(WebFetchRequest(url="https://example.com", prompt="Test"))

        # Content should be converted (exact format depends on html2text availability)
        assert "Title" in result.content
        assert "Paragraph" in result.content

    async def test_strips_script_tags_in_fallback(self) -> None:
        """WebFetchTool strips script tags when html2text unavailable."""
        tool = WebFetchTool()

        html = "<html><script>alert('bad')</script><body>Safe content</body></html>"

        # Use internal method directly to test fallback
        # First, simulate html2text import failure
        with patch.dict("sys.modules", {"html2text": None}):
            # Force reimport to trigger fallback
            result = tool._html_to_markdown(html)

        # Script content should be removed
        assert "alert" not in result
        assert "Safe content" in result or "Safe" in result


class TestWebFetchToolErrors:
    """Tests for WebFetchTool error handling."""

    async def test_raises_on_fetch_failure(self) -> None:
        """WebFetchTool raises ToolError on fetch failure."""
        tool = WebFetchTool()

        # Mock httpx to raise exception
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(ToolError) as exc_info:
                await tool.invoke(WebFetchRequest(url="https://example.com", prompt="Test"))

        assert "Failed to fetch URL" in str(exc_info.value)
        assert exc_info.value.tool_name == "web.fetch"


class TestWebFetchToolMetadata:
    """Tests for WebFetchTool metadata."""

    def test_tool_properties(self) -> None:
        """WebFetchTool has correct metadata."""
        tool = WebFetchTool()

        assert tool.name == "web.fetch"
        assert tool.trust_required == 1  # L1 - Bounded
        assert tool.category == ToolCategory.SYSTEM
        assert tool.cacheable is True

    def test_tool_effects(self) -> None:
        """WebFetchTool declares correct effects."""
        tool = WebFetchTool()

        effect_types = [e[0] for e in tool.effects]
        assert ToolEffect.CALLS in effect_types


class TestWebSearchTool:
    """Tests for WebSearchTool."""

    async def test_returns_placeholder_results(self) -> None:
        """WebSearchTool returns placeholder until configured."""
        tool = WebSearchTool()

        result = await tool.invoke(WebSearchQuery(query="python async tutorial"))

        # Should return configuration message
        assert result.count == 0
        assert len(result.results) == 1
        assert "not configured" in result.results[0].title.lower()

    async def test_accepts_domain_filters(self) -> None:
        """WebSearchTool accepts domain filter parameters."""
        tool = WebSearchTool()

        # Should not raise even with domain filters
        result = await tool.invoke(
            WebSearchQuery(
                query="rust ownership",
                allowed_domains=["doc.rust-lang.org"],
                blocked_domains=["stackoverflow.com"],
            )
        )

        assert result.query == "rust ownership"

    def test_tool_properties(self) -> None:
        """WebSearchTool has correct metadata."""
        tool = WebSearchTool()

        assert tool.name == "web.search"
        assert tool.trust_required == 1  # L1 - Bounded
        assert tool.category == ToolCategory.SYSTEM

    def test_tool_effects(self) -> None:
        """WebSearchTool declares correct effects."""
        tool = WebSearchTool()

        effect_types = [e[0] for e in tool.effects]
        assert ToolEffect.CALLS in effect_types


class TestURLCache:
    """Tests for URLCache singleton."""

    def test_cache_is_singleton(self) -> None:
        """URLCache is a singleton."""
        cache1 = URLCache()
        cache2 = URLCache()

        assert cache1 is cache2

    def test_cache_set_and_get(self) -> None:
        """URLCache stores and retrieves content."""
        cache = URLCache()
        cache.set("https://example.com", "test content")

        result = cache.get("https://example.com", ttl_seconds=900)
        assert result == "test content"

    def test_cache_expires(self) -> None:
        """URLCache respects TTL."""
        cache = URLCache()
        cache.set("https://example.com", "test content")

        # With 0 TTL, should be expired
        result = cache.get("https://example.com", ttl_seconds=0)
        assert result is None

    def test_cache_clear(self) -> None:
        """URLCache.clear() removes all entries."""
        cache = URLCache()
        cache.set("https://example.com", "content1")
        cache.set("https://example.org", "content2")

        cache.clear()

        assert cache.get("https://example.com", ttl_seconds=900) is None
        assert cache.get("https://example.org", ttl_seconds=900) is None
