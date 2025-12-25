"""
W-gent: Minimal Process Observer

After radical refinement (2025-12), W-gent's only purpose is bridging
external processes (that don't participate in AGENTESE) to the Witness system.

For AGENTESE-native agents, use the Witness protocol directly.
For K-Block operations, witnessing is automatic.

Architectural shift:
- MiddlewareBus → replaced by AGENTESE protocol
- Interceptors → replaced by Witness Grant/Scope/Mark
- Value Dashboard → replaced by Witness Garden
- Cortex Dashboard → replaced by K-Block timeline
- Agent Registry → replaced by @node decorator

W-gent now exists solely to observe non-AGENTESE processes via stdout/stderr.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator


@dataclass
class WireEvent:
    """A single event from an external process."""

    timestamp: datetime
    level: str  # INFO, WARN, ERROR, DEBUG
    stage: str  # What phase/stage the process is in
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessObserver:
    """Observe non-AGENTESE processes via stdout/stderr capture."""

    process_id: str
    name: str = "external"

    async def observe_stream(
        self, stream: asyncio.StreamReader
    ) -> AsyncIterator[WireEvent]:
        """Convert stdout/stderr lines to WireEvents."""
        while True:
            line = await stream.readline()
            if not line:
                break
            yield self._parse_line(line.decode().strip())

    def _parse_line(self, line: str) -> WireEvent:
        """Parse a log line into a WireEvent. Override for custom formats."""
        # Default: treat entire line as message
        return WireEvent(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            stage="running",
            message=line,
        )


async def observe_subprocess(
    cmd: list[str],
    name: str | None = None,
) -> AsyncIterator[WireEvent]:
    """
    Observe a subprocess and yield WireEvents.

    Example:
        async for event in observe_subprocess(["python", "script.py"]):
            print(f"[{event.level}] {event.message}")
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    observer = ProcessObserver(
        process_id=str(process.pid),
        name=name or cmd[0],
    )

    # Merge stdout and stderr
    async def merged_streams() -> AsyncIterator[WireEvent]:
        if process.stdout:
            async for event in observer.observe_stream(process.stdout):
                yield event
        if process.stderr:
            async for event in observer.observe_stream(process.stderr):
                event.level = "ERROR"
                yield event

    async for event in merged_streams():
        yield event

    await process.wait()
