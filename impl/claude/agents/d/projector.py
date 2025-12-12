"""
ContextProjector: Galois Connection for lossy context compression.

NOT A LENS - this is fundamentally lossy. Information is discarded.

A Lens requires:
- Get-Put: put(get(s), s) = s (if you get and put back, nothing changes)
- Put-Get: get(put(a, s)) = a (what you put is what you get)

Compression violates Get-Put: compress(expand(compressed)) <= compressed
The developer is explicitly warned: there is no inverse.

Galois Connection Property:
    compress ⊣ expand (compress is left adjoint to expand)
    compress(expand(c)) <= c  AND  s <= expand(compress(s))

Strategy (respects linearity):
1. Partition by resource class
2. Drop DROPPABLE regions first (observation masking)
3. Summarize REQUIRED regions (preserve decisions, drop reasoning)
4. NEVER touch PRESERVED regions (focus fragments)

AGENTESE: self.stream.project
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from .context_window import ContextWindow, Turn, TurnRole
from .linearity import ResourceClass


class Summarizer(Protocol):
    """Protocol for text summarization."""

    async def summarize(self, text: str, max_tokens: int) -> str:
        """Summarize text to fit within max_tokens."""
        ...


@dataclass
class DefaultSummarizer:
    """
    Simple heuristic summarizer (no LLM required).

    Strategies:
    - First N sentences
    - Key phrase extraction (simple)
    - Truncation with ellipsis
    """

    async def summarize(self, text: str, max_tokens: int) -> str:
        """Summarize text using heuristics."""
        # Rough estimate: 4 chars per token
        max_chars = max_tokens * 4

        if len(text) <= max_chars:
            return text

        # Strategy 1: First N sentences
        sentences = self._split_sentences(text)
        result = []
        current_len = 0

        for sentence in sentences:
            if current_len + len(sentence) > max_chars:
                break
            result.append(sentence)
            current_len += len(sentence)

        if result:
            return " ".join(result) + "..."

        # Strategy 2: Truncation
        return text[: max_chars - 3] + "..."

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        import re

        # Simple sentence splitter
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


@dataclass
class CompressionResult:
    """Result of a compression operation."""

    window: ContextWindow
    original_tokens: int
    compressed_tokens: int
    dropped_count: int
    summarized_count: int
    preserved_count: int

    @property
    def compression_ratio(self) -> float:
        """Ratio of compressed to original tokens."""
        if self.original_tokens == 0:
            return 1.0
        return self.compressed_tokens / self.original_tokens

    @property
    def savings(self) -> float:
        """Token savings as percentage."""
        return 1.0 - self.compression_ratio


@dataclass
class CompressionConfig:
    """Configuration for compression behavior."""

    # Target pressure after compression (0.0 to 1.0)
    target_pressure: float = 0.5

    # Minimum tokens to keep (never go below this)
    min_tokens: int = 100

    # Summarization target (tokens per summarized turn)
    summary_tokens: int = 50

    # Whether to merge adjacent turns of same role
    merge_adjacent: bool = True

    # Maximum turns to drop in one pass
    max_drops_per_pass: int = 10


@dataclass
class ContextProjector:
    """
    A Galois Connection for context compression.

    NOT a Lens—compression is lossy. The developer is warned:
    there is NO inverse operation.

    Property: compress(expand(c_hat)) <= c_hat

    Usage:
        projector = ContextProjector()

        # Compress when pressure is high
        if window.needs_compression:
            result = await projector.compress(window)
            # result.window is the compressed window
            # result.compression_ratio shows how much was saved
    """

    config: CompressionConfig = field(default_factory=CompressionConfig)
    summarizer: Summarizer = field(default_factory=DefaultSummarizer)

    async def compress(
        self,
        window: ContextWindow,
        target_pressure: float | None = None,
    ) -> CompressionResult:
        """
        Compress context while respecting resource classes.

        Strategy:
        1. Partition by resource class
        2. Drop DROPPABLE regions first (observation masking)
        3. Summarize REQUIRED regions (preserving decisions)
        4. Never touch PRESERVED regions (focus fragments)

        Args:
            window: The context window to compress
            target_pressure: Target pressure (default from config)

        Returns:
            CompressionResult with compressed window and stats
        """
        target = target_pressure or self.config.target_pressure
        original_tokens = window.total_tokens

        # Track what we do
        dropped_count = 0
        summarized_count = 0
        preserved_count = len(window.preserved_turns())

        # Create a new window for the compressed result
        compressed = ContextWindow(max_tokens=window.max_tokens)

        # Partition turns by resource class
        droppable = window.droppable_turns()
        required = window.required_turns()
        preserved = window.preserved_turns()

        # Phase 1: Calculate how many tokens we need to remove
        target_tokens = int(window.max_tokens * target)
        tokens_to_remove = max(0, original_tokens - target_tokens)

        # Phase 2: Drop DROPPABLE turns first
        droppable_tokens = sum(t.token_estimate for t in droppable)
        if tokens_to_remove > 0 and droppable_tokens > 0:
            # Sort by position (prefer dropping older turns)
            droppable_sorted = sorted(droppable, key=lambda t: t.timestamp)

            # Drop until we've removed enough
            removed = 0
            turns_to_keep: set[str] = set()

            for turn in droppable_sorted:
                if removed >= tokens_to_remove:
                    turns_to_keep.add(turn.resource_id)
                else:
                    removed += turn.token_estimate
                    dropped_count += 1

            # Update tokens to remove
            tokens_to_remove = max(0, tokens_to_remove - removed)

            # Filter droppable to only keep the ones we're keeping
            droppable = [t for t in droppable if t.resource_id in turns_to_keep]

        # Phase 3: Summarize REQUIRED turns if still over pressure
        if tokens_to_remove > 0:
            required = await self._summarize_required(
                required,
                tokens_to_remove,
            )
            summarized_count = len([t for t in required if "[summarized]" in t.content])

        # Phase 4: Reconstruct window with remaining turns
        # Collect all turns we're keeping and sort by timestamp
        all_remaining = droppable + required + preserved
        all_remaining.sort(key=lambda t: t.timestamp)

        for turn in all_remaining:
            compressed.append_turn(turn)

        # Update metadata
        compressed._meta.compression_count = window._meta.compression_count + 1
        compressed._meta.last_compression = datetime.now(UTC)

        return CompressionResult(
            window=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed.total_tokens,
            dropped_count=dropped_count,
            summarized_count=summarized_count,
            preserved_count=preserved_count,
        )

    async def _summarize_required(
        self,
        turns: list[Turn],
        tokens_to_remove: int,
    ) -> list[Turn]:
        """
        Summarize REQUIRED turns while preserving key decisions.

        Only summarizes turns that are over the target summary size.
        """
        result = []
        removed = 0

        for turn in turns:
            # Only summarize if we still need to remove tokens
            # and this turn is larger than target
            if (
                removed < tokens_to_remove
                and turn.token_estimate > self.config.summary_tokens
            ):
                # Summarize
                summarized_content = await self.summarizer.summarize(
                    turn.content,
                    self.config.summary_tokens,
                )

                # Create new turn with summarized content
                new_turn = Turn(
                    role=turn.role,
                    content=f"[summarized] {summarized_content}",
                    timestamp=turn.timestamp,
                    resource_id=turn.resource_id,
                    metadata={**turn.metadata, "original_length": len(turn.content)},
                )

                removed += turn.token_estimate - new_turn.token_estimate
                result.append(new_turn)
            else:
                result.append(turn)

        return result

    async def selective_compress(
        self,
        window: ContextWindow,
        keep_roles: set[TurnRole] | None = None,
        keep_recent: int = 5,
    ) -> CompressionResult:
        """
        Compress with selective retention rules.

        Args:
            window: The context window to compress
            keep_roles: Roles to always preserve
            keep_recent: Number of recent turns to preserve

        Returns:
            CompressionResult with compressed window
        """
        keep_roles = keep_roles or {TurnRole.USER, TurnRole.SYSTEM}
        original_tokens = window.total_tokens

        # Get all turns
        all_turns = window.all_turns()

        # Determine which turns to keep
        turns_to_keep: list[Turn] = []
        dropped_count = 0

        for i, turn in enumerate(all_turns):
            # Always keep if role matches
            if turn.role in keep_roles:
                turns_to_keep.append(turn)
                continue

            # Always keep if in recent window
            if i >= len(all_turns) - keep_recent:
                turns_to_keep.append(turn)
                continue

            # Check linearity class
            rc = window.get_resource_class(turn)
            if rc == ResourceClass.PRESERVED:
                turns_to_keep.append(turn)
                continue

            # Otherwise, can be dropped
            dropped_count += 1

        # Reconstruct window
        compressed = ContextWindow(max_tokens=window.max_tokens)
        for turn in turns_to_keep:
            compressed.append_turn(turn)

        preserved_count = len(
            [
                t
                for t in turns_to_keep
                if window.get_resource_class(t) == ResourceClass.PRESERVED
            ]
        )

        compressed._meta.compression_count = window._meta.compression_count + 1
        compressed._meta.last_compression = datetime.now(UTC)

        return CompressionResult(
            window=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed.total_tokens,
            dropped_count=dropped_count,
            summarized_count=0,
            preserved_count=preserved_count,
        )


# === Adaptive Thresholds ===


@dataclass
class AdaptiveThreshold:
    """
    ACON-style adaptive compression thresholds.

    Key insight: Fixed thresholds (70%, 95%) ignore task dynamics.
    Adaptive thresholds respond to task progress.

    Factors:
    - Early in task: Higher threshold (keep more context)
    - Near completion: Lower threshold (compress aggressively)
    - After errors: Higher threshold (preserve debug info)
    - Loop detected: Lower threshold (break the pattern)
    """

    base_threshold: float = 0.7
    task_progress: float = 0.0
    error_rate: float = 0.0
    loop_detected: bool = False

    @property
    def effective_threshold(self) -> float:
        """
        Compute adaptive threshold based on context.

        Returns value between 0.5 and 0.95.
        """
        threshold = self.base_threshold

        # Early task: be more conservative
        if self.task_progress < 0.2:
            threshold += 0.1

        # Near completion: can be more aggressive
        if self.task_progress > 0.8:
            threshold -= 0.1

        # Errors: preserve more context for debugging
        threshold += self.error_rate * 0.15

        # Loop detected: compress to break pattern
        if self.loop_detected:
            threshold -= 0.15

        # Clamp to reasonable range
        return max(0.5, min(0.95, threshold))

    def update(
        self,
        task_progress: float | None = None,
        error_rate: float | None = None,
        loop_detected: bool | None = None,
    ) -> "AdaptiveThreshold":
        """Update threshold parameters."""
        if task_progress is not None:
            self.task_progress = max(0.0, min(1.0, task_progress))
        if error_rate is not None:
            self.error_rate = max(0.0, min(1.0, error_rate))
        if loop_detected is not None:
            self.loop_detected = loop_detected
        return self


# === Factory Functions ===


def create_projector(
    target_pressure: float = 0.5,
    summarizer: Summarizer | None = None,
) -> ContextProjector:
    """Create a ContextProjector with configuration."""
    config = CompressionConfig(target_pressure=target_pressure)
    return ContextProjector(
        config=config,
        summarizer=summarizer or DefaultSummarizer(),
    )


async def auto_compress(
    window: ContextWindow,
    projector: ContextProjector | None = None,
) -> ContextWindow:
    """
    Automatically compress a window if needed.

    Returns the original window if compression not needed,
    otherwise returns the compressed window.
    """
    if not window.needs_compression:
        return window

    proj = projector or ContextProjector()
    result = await proj.compress(window)
    return result.window
