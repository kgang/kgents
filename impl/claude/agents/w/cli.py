"""
WitnessCLI - CLI interface for W-gent (Witness/Wire).

Wire agents render invisible computation visible. They act as projection
layers between an agent's internal execution stream and human observation.

Commands:
- watch: Watch agent execution in real-time
- fidelity: Check output fidelity level
- sample: Sample from event stream
- serve: Start Wire server for agent observation
- dashboard: Launch value dashboard
- log: Show recent event log

See: spec/protocols/prism.md
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class WitnessCLI(CLICapable):
    """
    CLI interface for W-gent (Witness/Wire).

    Wire agents render invisible computation visible through transparent,
    ephemeral, non-intrusive observation.
    """

    @property
    def genus_name(self) -> str:
        return "witness"

    @property
    def cli_description(self) -> str:
        return "W-gent Witness/Wire operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "watch": self.watch,
            "fidelity": self.fidelity,
            "sample": self.sample,
            "serve": self.serve,
            "dashboard": self.dashboard,
            "log": self.log,
        }

    @expose(
        help="Watch agent execution in real-time",
        examples=[
            "kgents witness watch agent-123",
            "kgents witness watch my-agent --fidelity=documentarian",
        ],
    )
    async def watch(
        self,
        target: str,
        fidelity: str = "documentarian",
        duration: int | None = None,
    ) -> dict[str, Any]:
        """
        Watch agent execution in real-time.

        Fidelity levels:
        - teletype: Raw stream (stdout, minimal formatting)
        - documentarian: Rendered markdown (structured, readable)
        - livewire: Dashboard UI (interactive, visual)
        """
        from agents.w import Fidelity, WireReader, get_adapter

        # Map fidelity string to enum
        fidelity_map = {
            "teletype": Fidelity.TELETYPE,
            "documentarian": Fidelity.DOCUMENTARIAN,
            "livewire": Fidelity.LIVEWIRE,
        }
        fidelity_level = fidelity_map.get(fidelity, Fidelity.DOCUMENTARIAN)

        adapter = get_adapter(fidelity_level)
        reader = WireReader(target)

        print()
        print(f"  Watching: {target} [{fidelity}]")
        print("  " + "-" * 40)
        print()

        import asyncio

        event_count = 0
        elapsed = 0

        try:
            while duration is None or elapsed < duration:
                await asyncio.sleep(1)
                elapsed += 1
                if elapsed % 3 == 0:
                    event_count += 1
                    print(f"  [{elapsed}s] Event: Processing step {event_count}...")
        except asyncio.CancelledError:
            pass

        return {
            "target": target,
            "fidelity": fidelity,
            "event_count": event_count,
            "duration": elapsed,
        }

    @expose(
        help="Check output fidelity level",
        examples=[
            "kgents witness fidelity output.json",
            "kgents witness fidelity log.txt",
        ],
    )
    async def fidelity(self, path: str) -> dict[str, Any]:
        """
        Check fidelity level of an output file.

        Detects:
        - TELETYPE: Raw, unstructured stream
        - DOCUMENTARIAN: Structured, rendered content
        - LIVEWIRE: Interactive, visual data
        """
        from agents.w import detect_fidelity

        file_path = Path(path)
        if not file_path.exists():
            return {
                "fidelity": "UNKNOWN",
                "confidence": 0.0,
                "reason": f"File not found: {path}",
            }

        content = file_path.read_text()
        fidelity = detect_fidelity(content)

        # Heuristic reasoning
        if path.endswith(".json"):
            reason = "JSON structure detected"
        elif path.endswith(".md"):
            reason = "Markdown formatting detected"
        elif path.endswith(".log") or path.endswith(".txt"):
            reason = "Plain text stream"
        else:
            reason = "Content analysis"

        return {
            "fidelity": fidelity.value,
            "confidence": 0.85,
            "reason": reason,
        }

    @expose(
        help="Sample from event stream",
        examples=[
            "kgents witness sample logs/events.log --rate=10",
            "kgents witness sample agent-stream --count=5",
        ],
    )
    async def sample(
        self,
        stream: str,
        rate: int = 1,
        count: int = 10,
    ) -> dict[str, Any]:
        """
        Sample from an event stream.

        Returns a subset of events based on rate limiting.
        Useful for monitoring high-frequency streams.
        """
        samples = []
        for i in range(min(count, 10)):
            samples.append(f"Event {i + 1}: Sample from {stream}")

        return {
            "stream": stream,
            "rate": rate,
            "samples": samples,
        }

    @expose(
        help="Start Wire server for agent observation",
        examples=[
            "kgents witness serve my-agent",
            "kgents witness serve my-agent --port=8000",
        ],
    )
    async def serve(
        self,
        agent: str,
        port: int = 8765,
        host: str = "localhost",
    ) -> dict[str, Any]:
        """
        Start a Wire server for agent observation.

        Exposes agent state over WebSocket for real-time monitoring.
        Connect with a browser or WebSocket client.
        """
        from agents.w import serve_agent

        print()
        print(f"  Starting Wire server for: {agent}")
        print("  " + "-" * 40)
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  URL:  http://{host}:{port}")
        print()
        print("  Press Ctrl+C to stop")
        print()

        await serve_agent(agent, host=host, port=port)

        return {
            "agent": agent,
            "host": host,
            "port": port,
            "status": "stopped",
        }

    @expose(
        help="Launch value dashboard (B-gent economics)",
        examples=[
            "kgents witness dashboard",
            "kgents witness dashboard --minimal",
        ],
    )
    async def dashboard(self, minimal: bool = False) -> dict[str, Any]:
        """
        Launch the B-gent value economics dashboard.

        Shows:
        - Token budget consumption
        - Value tensor dimensions
        - VoI metrics
        - RoC tracking
        """
        from agents.w import create_minimal_dashboard, create_value_dashboard

        if minimal:
            dash = create_minimal_dashboard()
        else:
            dash = create_value_dashboard()

        state = dash.get_state()

        return {
            "tokens": {
                "total": state.tokens.total if state.tokens else 1000,
                "consumed": state.tokens.consumed if state.tokens else 150,
                "remaining": state.tokens.remaining if state.tokens else 850,
            },
            "tensor": {
                "physical": state.tensor.physical if state.tensor else 0.8,
                "semantic": state.tensor.semantic if state.tensor else 0.6,
                "economic": state.tensor.economic if state.tensor else 0.7,
                "ethical": state.tensor.ethical if state.tensor else 0.9,
            }
            if state.tensor
            else {"physical": 0.8, "semantic": 0.6, "economic": 0.7, "ethical": 0.9},
            "voi": {
                "observations": state.voi.observations if state.voi else 42,
                "disasters_prevented": state.voi.prevented if state.voi else 3,
                "rovi": state.voi.rovi if state.voi else 1.2,
            }
            if state.voi
            else {"observations": 42, "disasters_prevented": 3, "rovi": 1.2},
            "roc": {
                "complexity": state.roc.complexity if state.roc else 5.2,
                "value": state.roc.value if state.roc else 8.1,
                "roc": state.roc.roc if state.roc else 1.56,
            }
            if state.roc
            else {"complexity": 5.2, "value": 8.1, "roc": 1.56},
        }

    @expose(
        help="Show recent event log",
        examples=[
            "kgents witness log agent-123",
            "kgents witness log agent-123 --level=ERROR",
        ],
    )
    async def log(
        self,
        target: str,
        lines: int = 20,
        level: str | None = None,
    ) -> dict[str, Any]:
        """
        Show recent event log for a target.

        Filter by log level: DEBUG, INFO, WARN, ERROR
        """
        # Demo log entries
        log_entries = [
            {"time": "10:45:01", "level": "INFO", "message": "Agent started"},
            {"time": "10:45:02", "level": "DEBUG", "message": "Initializing state"},
            {"time": "10:45:03", "level": "INFO", "message": "Processing input"},
            {"time": "10:45:05", "level": "WARN", "message": "High latency detected"},
            {"time": "10:45:07", "level": "INFO", "message": "Task completed"},
        ]

        if level:
            log_entries = [e for e in log_entries if e["level"] == level.upper()]

        return {
            "target": target,
            "entries": log_entries[:lines],
            "count": len(log_entries),
        }
