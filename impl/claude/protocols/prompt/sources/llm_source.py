"""
LLM Source: Infer section content via LLM.

The least rigid source type (rigidity ~0.1-0.3).
Used when file sources fail and we need to generate content.

Note: Actual LLM calls are abstracted behind a callable,
allowing for testing with mock implementations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable

from .base import SectionSource, SourcePriority, SourceResult

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)

# Type alias for LLM inference function
LLMInferFn = Callable[[str, "CompilationContext"], Awaitable[str | None]]


@dataclass
class LLMSource(SectionSource):
    """
    Source that infers content via LLM.

    The least rigid source - content is generated, not read.
    Used as fallback when file sources fail.

    Attributes:
        prompt_template: Template for the inference prompt
        infer_fn: Async function that performs the actual LLM call
        max_tokens: Maximum tokens for generated content
        cache_key: Optional key for caching results
    """

    prompt_template: str = "Generate content for section: {section_name}"
    infer_fn: LLMInferFn | None = None
    max_tokens: int = 500
    cache_key: str | None = None
    priority: SourcePriority = field(default=SourcePriority.INFERENCE)
    rigidity: float = 0.2

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Infer content via LLM."""
        traces = [f"LLMSource: Attempting inference for {self.name}"]

        if self.infer_fn is None:
            traces.append("No inference function configured")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Build prompt
        prompt = self.prompt_template.format(
            section_name=self.name,
            max_tokens=self.max_tokens,
        )
        traces.append(f"Prompt: {prompt[:100]}...")

        try:
            # Call inference function
            traces.append("Calling LLM inference...")
            content = await self.infer_fn(prompt, context)

            if content is None:
                traces.append("LLM returned None")
                return SourceResult(
                    content=None,
                    success=False,
                    source_name=self.name,
                    source_path=None,
                    reasoning_trace=tuple(traces),
                    rigidity=self.rigidity,
                )

            traces.append(f"LLM generated {len(content)} chars")

            # Truncate if too long
            if len(content) > self.max_tokens * 4:  # ~4 chars/token
                content = content[: self.max_tokens * 4]
                traces.append(f"Truncated to {len(content)} chars")

            return SourceResult(
                content=content,
                success=True,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        except Exception as e:
            traces.append(f"LLM inference failed: {e}")
            logger.error(f"LLM inference failed for {self.name}: {e}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )


@dataclass
class MockLLMSource(SectionSource):
    """
    Mock LLM source for testing.

    Returns predetermined content without actual LLM calls.
    """

    mock_content: str = "Mock generated content."
    should_fail: bool = False
    priority: SourcePriority = field(default=SourcePriority.INFERENCE)
    rigidity: float = 0.2

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Return mock content."""
        traces = [f"MockLLMSource: {self.name}"]

        if self.should_fail:
            traces.append("Configured to fail")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        traces.append(f"Returning mock content: {len(self.mock_content)} chars")
        return SourceResult(
            content=self.mock_content,
            success=True,
            source_name=self.name,
            source_path=None,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


__all__ = [
    "LLMSource",
    "MockLLMSource",
    "LLMInferFn",
]
