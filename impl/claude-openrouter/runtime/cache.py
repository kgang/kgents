"""
Response Caching

Simple disk-based cache with TTL for LLM responses.
Reduces redundant LLM calls for repeated queries.
"""

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .config import get_config, RuntimeConfig
from .messages import CompletionResult, Message, TokenUsage


class ResponseCache:
    """Disk-based response cache with TTL"""

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or get_config()
        self._cache_dir = self._config.cache_dir / "responses"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, messages: list[Message], model: str, system: str | None = None) -> str:
        """Create a cache key from messages and parameters"""
        key_data = {
            "messages": [(m.role, m.content) for m in messages],
            "model": model,
            "system": system or "",
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def _cache_path(self, key: str) -> Path:
        """Get the file path for a cache key"""
        return self._cache_dir / f"{key}.json"

    def get(
        self,
        messages: list[Message],
        model: str,
        system: str | None = None
    ) -> CompletionResult | None:
        """Get a cached response if available and not expired"""
        if not self._config.enable_cache:
            return None

        key = self._make_key(messages, model, system)
        path = self._cache_path(key)

        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)

            # Check TTL
            cached_at = data.get("cached_at", 0)
            if time.time() - cached_at > self._config.cache_ttl_seconds:
                path.unlink(missing_ok=True)
                return None

            # Reconstruct CompletionResult
            return CompletionResult(
                content=data["content"],
                model=data["model"],
                usage=TokenUsage(
                    input_tokens=data["usage"]["input_tokens"],
                    output_tokens=data["usage"]["output_tokens"]
                ),
                cached=True,
                finish_reason=data.get("finish_reason")
            )

        except (json.JSONDecodeError, KeyError, OSError):
            # Corrupted cache entry, remove it
            path.unlink(missing_ok=True)
            return None

    def set(
        self,
        messages: list[Message],
        model: str,
        result: CompletionResult,
        system: str | None = None
    ) -> None:
        """Cache a response"""
        if not self._config.enable_cache:
            return

        key = self._make_key(messages, model, system)
        path = self._cache_path(key)

        data = {
            "content": result.content,
            "model": result.model,
            "usage": {
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
            },
            "finish_reason": result.finish_reason,
            "cached_at": time.time(),
        }

        try:
            with open(path, "w") as f:
                json.dump(data, f)
        except OSError:
            # Ignore cache write failures
            pass

    def clear(self) -> int:
        """Clear all cached responses. Returns number of entries cleared."""
        count = 0
        for path in self._cache_dir.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except OSError:
                pass
        return count

    def clear_expired(self) -> int:
        """Clear expired cache entries. Returns number of entries cleared."""
        count = 0
        now = time.time()
        ttl = self._config.cache_ttl_seconds

        for path in self._cache_dir.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                cached_at = data.get("cached_at", 0)
                if now - cached_at > ttl:
                    path.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Corrupted entry, remove it
                try:
                    path.unlink()
                    count += 1
                except OSError:
                    pass
        return count


# Global cache singleton
_cache: ResponseCache | None = None


def get_cache() -> ResponseCache:
    """Get the global response cache"""
    global _cache
    if _cache is None:
        _cache = ResponseCache()
    return _cache


def reset_cache() -> None:
    """Reset the global cache"""
    global _cache
    _cache = None
