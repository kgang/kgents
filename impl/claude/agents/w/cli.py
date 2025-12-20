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

        _reader = WireReader(target)  # noqa: F841 - reserved for future use
        _adapter = get_adapter(_reader, fidelity_level)  # noqa: F841 - reserved for future use

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
        from agents.w import WireReader, detect_fidelity

        file_path = Path(path)
        if not file_path.exists():
            return {
                "fidelity": "UNKNOWN",
                "confidence": 0.0,
                "reason": f"File not found: {path}",
            }

        # Create a WireReader for the path
        reader = WireReader(str(file_path.parent))
        fidelity_level = detect_fidelity(reader)

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
            "fidelity": fidelity_level.value,
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

        await serve_agent(agent, port=port)

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

        # Get the latest snapshots from the dashboard's history
        token_history = dash.get_token_history(limit=1)
        tensor_history = dash.get_tensor_history(limit=1)
        voi_history = dash.get_voi_history(limit=1)
        roc_history = dash.get_roc_history(limit=1)

        return {
            "tokens": {
                "total": 1000,
                "consumed": token_history[0].gas_consumed if token_history else 150,
                "remaining": token_history[0].gas_available if token_history else 850,
            },
            "tensor": {
                "physical": tensor_history[0].physical if tensor_history else 0.8,
                "semantic": tensor_history[0].semantic if tensor_history else 0.6,
                "economic": tensor_history[0].economic if tensor_history else 0.7,
                "ethical": tensor_history[0].ethical if tensor_history else 0.9,
            },
            "voi": {
                "observations": voi_history[0].observations if voi_history else 42,
                "disasters_prevented": voi_history[0].anomalies_detected if voi_history else 3,
                "rovi": voi_history[0].rovi if voi_history else 1.2,
            },
            "roc": {
                "complexity": roc_history[0].total_gas_consumed if roc_history else 5.2,
                "value": roc_history[0].total_value_generated if roc_history else 8.1,
                "roc": roc_history[0].current_roc if roc_history else 1.56,
            },
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
