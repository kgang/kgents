"""
I-gent Observe Action: Integration with W-gents.

The [observe] action in I-gent spawns a W-gent attached to the selected agent.
This provides the "drill down" from ecosystem view to process internals.

Flow:
1. User clicks [observe] on an agent in I-gent
2. I-gent spawns W-gent attached to that agent
3. W-gent starts localhost server
4. Browser opens to localhost:8000
5. W-gent projects agent internals
6. Observations can be exported back to I-gent margin notes
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types import GardenState, MarginNote


class ObserveAction:
    """
    Manages the [observe] action from I-gent to W-gent.

    This is the bridge between ecosystem visualization (I-gent)
    and process internals visualization (W-gent).
    """

    def __init__(
        self,
        base_port: int = 8000,
        auto_open: bool = True,
    ):
        """
        Initialize observe action handler.

        Args:
            base_port: Starting port for W-gent servers (increments for multiple)
            auto_open: Whether to auto-open browser
        """
        self.base_port = base_port
        self.auto_open = auto_open
        self._active_wgents: dict[str, int] = {}  # agent_name -> port
        self._processes: dict[str, subprocess.Popen[bytes]] = {}

    def get_port(self, agent_name: str) -> int:
        """
        Get port for an agent's W-gent.

        If already observing, returns existing port.
        Otherwise, allocates a new port.
        """
        if agent_name in self._active_wgents:
            return self._active_wgents[agent_name]

        # Find next available port
        used_ports = set(self._active_wgents.values())
        port = self.base_port
        while port in used_ports:
            port += 1

        return port

    async def observe(
        self,
        agent_name: str,
        fidelity: Optional[str] = None,
    ) -> tuple[int, str]:
        """
        Start observing an agent.

        Args:
            agent_name: Name of the agent to observe
            fidelity: Optional fidelity level (teletype, documentarian, livewire)

        Returns:
            Tuple of (port, url) where W-gent is serving
        """
        # Check if already observing
        if agent_name in self._active_wgents:
            port = self._active_wgents[agent_name]
            url = f"http://127.0.0.1:{port}"
            return port, url

        port = self.get_port(agent_name)

        # Build command
        cmd = [
            sys.executable,
            "-m",
            "agents.w.server",
            agent_name,
            "--port",
            str(port),
        ]

        if fidelity:
            cmd.extend(["--mode", fidelity])

        if not self.auto_open:
            cmd.append("--no-open")

        # Start W-gent process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self._active_wgents[agent_name] = port
        self._processes[agent_name] = process

        # Wait a moment for server to start
        await asyncio.sleep(1.0)

        url = f"http://127.0.0.1:{port}"
        return port, url

    def stop_observe(self, agent_name: str) -> bool:
        """
        Stop observing an agent.

        Args:
            agent_name: Name of the agent to stop observing

        Returns:
            True if stopped, False if wasn't observing
        """
        if agent_name not in self._active_wgents:
            return False

        if agent_name in self._processes:
            process = self._processes[agent_name]
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
            del self._processes[agent_name]

        del self._active_wgents[agent_name]
        return True

    def stop_all(self) -> int:
        """
        Stop all W-gent observations.

        Returns:
            Number of W-gents stopped
        """
        count = 0
        for agent_name in list(self._active_wgents.keys()):
            if self.stop_observe(agent_name):
                count += 1
        return count

    def is_observing(self, agent_name: str) -> bool:
        """Check if an agent is being observed."""
        return agent_name in self._active_wgents

    def list_observations(self) -> dict[str, int]:
        """List all active observations (agent_name -> port)."""
        return dict(self._active_wgents)


async def import_wgent_notes(
    agent_name: str,
    port: int = 8000,
) -> list[str]:
    """
    Import observations from W-gent as margin notes.

    This fetches the export endpoint from a running W-gent
    and returns the notes to be added to I-gent.

    Args:
        agent_name: Name of the observed agent
        port: Port where W-gent is serving

    Returns:
        List of margin note strings
    """
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{port}/export")
            if response.status_code == 200:
                text = response.text.strip()
                if text:
                    return text.split("\n")
    except Exception:
        pass

    return []


class GardenObserver:
    """
    Manages observation for an entire garden.

    Provides higher-level interface for I-gent to manage
    multiple W-gent observations.
    """

    def __init__(self, garden_state: "GardenState"):
        """
        Initialize garden observer.

        Args:
            garden_state: The garden state to observe
        """
        self.garden = garden_state
        self.action = ObserveAction()

    async def observe_focused(self) -> Optional[tuple[int, str]]:
        """
        Start observing the currently focused agent.

        Returns:
            Tuple of (port, url) or None if no agent is focused
        """
        if not self.garden.focus:
            return None

        return await self.action.observe(self.garden.focus)

    async def observe_agent(self, agent_id: str) -> Optional[tuple[int, str]]:
        """
        Start observing a specific agent.

        Args:
            agent_id: ID of the agent to observe

        Returns:
            Tuple of (port, url) or None if agent not in garden
        """
        if agent_id not in self.garden.agents:
            return None

        return await self.action.observe(agent_id)

    async def import_notes_for_agent(self, agent_id: str) -> list["MarginNote"]:
        """
        Import W-gent observations as margin notes for an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            List of MarginNote objects (also added to agent state)
        """
        from .types import MarginNote, NoteSource

        if agent_id not in self._active_observations:
            return []

        port = self.action._active_wgents.get(agent_id)
        if not port:
            return []

        note_strings = await import_wgent_notes(agent_id, port)

        notes = []
        agent = self.garden.agents.get(agent_id)
        if agent:
            for note_str in note_strings:
                # Parse note string: "HH:MM:SS — [source] content"
                parts = note_str.split(" — ", 1)
                if len(parts) == 2:
                    content = parts[1]
                    # Extract source if present
                    if content.startswith("[w-gent]"):
                        content = content[9:].strip()

                    note = MarginNote(
                        timestamp=datetime.now(),
                        source=NoteSource.WGENT,
                        content=content,
                        agent_id=agent_id,
                    )
                    agent.margin_notes.append(note)
                    notes.append(note)

        return notes

    @property
    def _active_observations(self) -> dict[str, int]:
        """Get active observations."""
        return self.action._active_wgents

    def stop_all_observations(self) -> int:
        """Stop all active observations."""
        return self.action.stop_all()
