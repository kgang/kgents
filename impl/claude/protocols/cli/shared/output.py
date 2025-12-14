"""
OutputFormatter: Unified output handling for CLI commands.

This provides consistent output formatting across all commands,
supporting JSON, streaming, and pipe modes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

from .context import InvocationContext


@dataclass
class OutputFormatter:
    """
    Unified output formatting for all CLI commands.

    Handles:
    - JSON output (--json)
    - Streaming output (--stream)
    - Pipe output (--pipe, NDJSON)
    - Plain text output (default)
    """

    ctx: InvocationContext

    def emit(self, text: str, data: dict[str, Any] | None = None) -> None:
        """
        Emit output in the appropriate format.

        Args:
            text: Human-readable text
            data: Structured data (used for JSON mode)
        """
        if self.ctx.json_mode:
            self.emit_json(data or {"text": text})
        else:
            self.ctx.output(text, data)

    def emit_json(self, data: dict[str, Any]) -> None:
        """Emit structured JSON output."""
        output = json.dumps(data, indent=2)
        self.ctx.output(output, data)

    def emit_line(self, data: dict[str, Any]) -> None:
        """Emit a single JSON line (NDJSON format)."""
        print(json.dumps(data), flush=True)

    def stream_chunk(self, chunk: str, index: int) -> None:
        """
        Emit a streaming chunk.

        In pipe mode: JSON line
        Otherwise: Raw character output
        """
        if self.ctx.pipe_mode:
            self.emit_line({"type": "chunk", "index": index, "data": chunk})
        else:
            sys.stdout.write(chunk)
            sys.stdout.flush()

    def stream_metadata(self, metadata: dict[str, Any]) -> None:
        """
        Emit streaming metadata (tokens, model, etc).

        In pipe mode: JSON line
        Otherwise: Footer text
        """
        if self.ctx.pipe_mode:
            self.emit_line({"type": "metadata", **metadata})
        else:
            if metadata.get("tokens_used", 0) > 0:
                print(f"\n  [{metadata['tokens_used']} tokens]")

    def stream_error(self, message: str, chunks_emitted: int = 0) -> None:
        """Emit a streaming error."""
        if self.ctx.pipe_mode:
            self.emit_line(
                {
                    "type": "error",
                    "message": message,
                    "chunks_emitted": chunks_emitted,
                }
            )
        else:
            print(f"\n[Error] {message}")

    def emit_error(self, message: str, code: str | None = None) -> None:
        """Emit an error message."""
        data = {"error": message}
        if code:
            data["code"] = code

        if self.ctx.json_mode:
            self.emit_json(data)
        else:
            self.ctx.output(f"[ERROR] {message}", data)


def mode_icon(mode: str) -> str:
    """Get the icon for a dialogue mode."""
    icons = {
        "reflect": "~",
        "advise": ">",
        "challenge": "!",
        "explore": "?",
    }
    return icons.get(mode.lower(), "*")


def format_dialogue_header(mode: str) -> str:
    """Format a dialogue mode header."""
    icon = mode_icon(mode)
    return f"[{icon} SOUL:{mode.upper()}]"
