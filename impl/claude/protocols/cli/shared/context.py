"""
InvocationContext: Shared context for all CLI commands.

This extracts the context handling patterns from individual handlers
into a unified interface.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext as ReflectorContext


@dataclass
class InvocationContext:
    """
    Unified context for CLI command invocation.

    Encapsulates:
    - Output modes (json, stream, pipe)
    - Session information
    - Budget configuration
    - Reflector context integration
    """

    # Output modes
    json_mode: bool = False
    stream_mode: bool = False
    pipe_mode: bool = False
    quiet: bool = False

    # Budget
    budget: str = "dialogue"  # whisper, dialogue, deep

    # Session
    session_id: str | None = None

    # Internal: reflector context for dual-channel output
    _reflector_ctx: Any = field(default=None, repr=False)

    @classmethod
    def from_args(
        cls, args: list[str], reflector_ctx: Any = None
    ) -> "InvocationContext":
        """
        Parse context from command-line arguments.

        Standard flags:
            --json      Output as JSON
            --stream    Stream response
            --pipe      JSON-lines for shell pipes
            --quiet     Minimal output
            --quick     Whisper budget (~100 tokens)
            --deep      Deep budget (~8000+ tokens)
        """
        json_mode = "--json" in args
        stream_mode = "--stream" in args
        pipe_mode = "--pipe" in args
        quiet = "--quiet" in args

        # Budget
        budget = "dialogue"
        if "--quick" in args:
            budget = "whisper"
        elif "--deep" in args:
            budget = "deep"

        # Auto-detect pipe mode when stdout is not a TTY
        if not pipe_mode and not sys.stdout.isatty():
            pipe_mode = True

        return cls(
            json_mode=json_mode,
            stream_mode=stream_mode,
            pipe_mode=pipe_mode,
            quiet=quiet,
            budget=budget,
            _reflector_ctx=reflector_ctx,
        )

    def output(self, human: str, semantic: dict[str, Any] | None = None) -> None:
        """
        Emit output via dual-channel if reflector context available.

        Args:
            human: Human-readable output for stdout
            semantic: Structured data for semantic channel (FD3)
        """
        if self._reflector_ctx is not None:
            self._reflector_ctx.output(human=human, semantic=semantic or {})
        else:
            print(human)

    @property
    def is_streaming(self) -> bool:
        """Check if any streaming mode is active."""
        return self.stream_mode or self.pipe_mode
