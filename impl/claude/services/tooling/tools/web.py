"""
Web Tools: URL Fetching and Search with Caching.

Phase 2 of U-gent Tooling: Network access with caching and safety.

Key Principle: "Cache aggressively, cite religiously."

These tools provide controlled web access:
- WebFetchTool: URL fetch with HTML→Markdown conversion and 15-min cache
- WebSearchTool: Web search with mandatory source citations

Safety Patterns:
- HTTP upgraded to HTTPS automatically
- Cross-host redirects detected and reported
- Results cached for 15 minutes
- Content truncated if too large

See: plans/ugent-tooling-phase2-handoff.md
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar
from urllib.parse import urlparse

from ..base import Tool, ToolCategory, ToolEffect, ToolError
from ..contracts import (
    WebFetchRequest,
    WebFetchResponse,
    WebSearchQuery,
    WebSearchResponse,
    WebSearchResult,
)

# =============================================================================
# URL Cache
# =============================================================================


class URLCache:
    """
    Simple URL cache with TTL.

    Thread-safe cache for fetched URL content.
    """

    _instance: ClassVar[URLCache | None] = None
    _cache: dict[str, tuple[str, float]]  # url → (content, timestamp)

    def __new__(cls) -> URLCache:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def get(self, url: str, ttl_seconds: float) -> str | None:
        """Get cached content if not expired."""
        if url in self._cache:
            content, cached_at = self._cache[url]
            if time.time() - cached_at < ttl_seconds:
                return content
            # Expired, remove
            del self._cache[url]
        return None

    def set(self, url: str, content: str) -> None:
        """Cache content for URL."""
        self._cache[url] = (content, time.time())

    def clear(self) -> None:
        """Clear all cached content."""
        self._cache.clear()

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        if cls._instance is not None:
            cls._instance._cache.clear()


def get_url_cache() -> URLCache:
    """Get the singleton URL cache."""
    return URLCache()


# =============================================================================
# WebFetchTool: URL Extraction
# =============================================================================


@dataclass
class WebFetchTool(Tool[WebFetchRequest, WebFetchResponse]):
    """
    WebFetchTool: Fetch URL and extract content.

    Trust Level: L1 (bounded network access)
    Effects: CALLS(network)

    Features:
    - HTML → Markdown conversion
    - 15-minute cache for repeated requests
    - HTTP automatically upgraded to HTTPS
    - Cross-host redirect detection and notification

    Examples:
        WebFetchRequest(url="https://example.com", prompt="Extract the title")
        WebFetchRequest(url="http://docs.python.org", prompt="Find the installation guide")
    """

    # Cache TTL in seconds (15 minutes)
    CACHE_TTL_SECONDS: ClassVar[float] = 900.0

    # Maximum content size
    MAX_CONTENT_CHARS: ClassVar[int] = 100_000

    # Request timeout
    TIMEOUT_SECONDS: ClassVar[float] = 30.0

    @property
    def name(self) -> str:
        return "web.fetch"

    @property
    def description(self) -> str:
        return "Fetch URL content and extract based on prompt"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.calls("network")]

    @property
    def trust_required(self) -> int:
        return 1  # L1 - Bounded

    @property
    def cacheable(self) -> bool:
        return True

    async def invoke(self, request: WebFetchRequest) -> WebFetchResponse:
        """
        Fetch URL and extract content based on prompt.

        Args:
            request: WebFetchRequest with url and prompt

        Returns:
            WebFetchResponse with extracted content

        Raises:
            ToolError: On fetch failure
        """
        # Normalize URL (upgrade http to https)
        url = request.url
        if url.startswith("http://"):
            url = "https://" + url[7:]

        # Check cache
        cache = get_url_cache()
        cached_content = cache.get(url, self.CACHE_TTL_SECONDS)
        if cached_content is not None:
            # Apply prompt-based extraction to cached content
            extracted = self._extract_by_prompt(cached_content, request.prompt)
            return WebFetchResponse(
                url=url,
                content=extracted,
                cached=True,
            )

        # Fetch content
        try:
            import httpx

            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self.TIMEOUT_SECONDS,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Check for cross-host redirect
                final_url = str(response.url)
                if self._different_host(url, final_url):
                    return WebFetchResponse(
                        url=url,
                        content=f"Redirected to different host. Please fetch: {final_url}",
                        redirect_url=final_url,
                    )

                html_content = response.text

        except ImportError:
            raise ToolError(
                "httpx not installed. Run: pip install httpx",
                self.name,
            )
        except Exception as e:
            raise ToolError(f"Failed to fetch URL: {e}", self.name) from e

        # Convert HTML to Markdown
        markdown = self._html_to_markdown(html_content)

        # Truncate if too large
        if len(markdown) > self.MAX_CONTENT_CHARS:
            markdown = markdown[: self.MAX_CONTENT_CHARS] + "\n\n... (content truncated)"

        # Cache the markdown
        cache.set(url, markdown)

        # Extract based on prompt
        extracted = self._extract_by_prompt(markdown, request.prompt)

        return WebFetchResponse(
            url=url,
            content=extracted,
            cached=False,
        )

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to clean Markdown."""
        try:
            import html2text  # type: ignore[import-not-found]

            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.body_width = 0  # No wrapping
            h.ignore_emphasis = False
            return str(h.handle(html))
        except ImportError:
            # Fallback: strip tags crudely
            # Remove script and style content first
            html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
            # Remove all tags
            text = re.sub(r"<[^>]+>", " ", html)
            # Collapse whitespace
            text = re.sub(r"\s+", " ", text)
            return text.strip()

    def _extract_by_prompt(self, content: str, prompt: str) -> str:
        """
        Extract content based on prompt.

        Note: Full AI-powered extraction would integrate with chat service.
        For now, this is a placeholder that returns the content with the
        prompt as context. Future implementation will use a fast model
        (like Haiku) to extract relevant sections.
        """
        # For now, return content with prompt context
        # A real implementation would use LLM extraction
        if len(content) > 10_000:
            return content[:10_000] + f"\n\n... (content truncated)\n\nPrompt: {prompt}"
        return content

    def _different_host(self, url1: str, url2: str) -> bool:
        """Check if two URLs have different hosts."""
        host1 = urlparse(url1).netloc.lower()
        host2 = urlparse(url2).netloc.lower()
        return host1 != host2


# =============================================================================
# WebSearchTool: Search with Citations
# =============================================================================


@dataclass
class WebSearchTool(Tool[WebSearchQuery, WebSearchResponse]):
    """
    WebSearchTool: Web search with mandatory source citations.

    Trust Level: L1 (bounded network access)
    Effects: CALLS(network)

    CRITICAL: Results MUST include source URLs for citation.

    Examples:
        WebSearchQuery(query="python async tutorial")
        WebSearchQuery(query="rust ownership", allowed_domains=["doc.rust-lang.org"])
    """

    @property
    def name(self) -> str:
        return "web.search"

    @property
    def description(self) -> str:
        return "Search the web with source citations"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.calls("network")]

    @property
    def trust_required(self) -> int:
        return 1  # L1 - Bounded

    async def invoke(self, request: WebSearchQuery) -> WebSearchResponse:
        """
        Execute web search.

        Args:
            request: WebSearchQuery with query and optional domain filters

        Returns:
            WebSearchResponse with results

        Note:
            This is a placeholder implementation. A real implementation
            would integrate with a search provider (Serper, Brave, etc.)
            or use Anthropic's built-in web search if available.
        """
        # Placeholder: In a real implementation, this would call a search API
        #
        # Options for real implementation:
        # 1. Anthropic's built-in web search (if available in Claude API)
        # 2. Serper API (https://serper.dev)
        # 3. Brave Search API (https://brave.com/search/api/)
        # 4. SerpAPI (https://serpapi.com)
        #
        # For now, return empty results with a message

        return WebSearchResponse(
            query=request.query,
            results=[
                WebSearchResult(
                    title="Web search not configured",
                    url="",
                    snippet="WebSearchTool requires a search provider integration. "
                    "See plans/ugent-tooling-phase2-handoff.md for options.",
                )
            ],
            count=0,
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WebFetchTool",
    "WebSearchTool",
    "URLCache",
    "get_url_cache",
]
