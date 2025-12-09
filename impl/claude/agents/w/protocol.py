"""
W-gent Wire Protocol: How agents expose state for observation.

The wire protocol offers conventions, not requirements. W-gents adapt
to what agents provide—there is no mandatory format.

Protocol Layers (in order of capability):
1. File System: Agent writes to .wire/ directory
2. IPC: Unix socket at /tmp/agent-{name}.sock
3. HTTP API: localhost endpoint at port 9000
4. Standard Streams: Subprocess stdout/stderr capture

Minimum compliance:
- Write text to stdout, OR
- Write to .wire/stream.log

That's it. Everything else is optional enhancement.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


@dataclass
class WireEvent:
    """A single event in the wire stream."""

    timestamp: datetime
    level: str  # DEBUG, INFO, WARN, ERROR
    stage: str  # Pipeline stage name
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "timestamp": self.timestamp.isoformat() + "Z",
            "level": self.level,
            "stage": self.stage,
            "message": self.message,
        }

    def to_log_line(self) -> str:
        """Format as log line: [timestamp] [level] [stage] message"""
        ts = self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"[{ts}] [{self.level}] [{self.stage}] {self.message}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WireEvent:
        """Create from dict."""
        ts = data.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts[:-1]
        return cls(
            timestamp=datetime.fromisoformat(ts),
            level=data.get("level", "INFO"),
            stage=data.get("stage", "unknown"),
            message=data.get("message", ""),
        )


@dataclass
class WireMetrics:
    """Performance metrics for wire observation."""

    uptime_seconds: float
    memory_mb: Optional[float] = None
    api_calls: Optional[int] = None
    tokens_processed: Optional[int] = None
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": self.uptime_seconds,
        }
        if self.memory_mb is not None:
            result["memory_mb"] = self.memory_mb
        if self.api_calls is not None:
            result["api_calls"] = self.api_calls
        if self.tokens_processed is not None:
            result["tokens_processed"] = self.tokens_processed
        if self.custom:
            result["custom"] = self.custom
        return result


@dataclass
class WireState:
    """
    Current state snapshot for wire observation.

    This is the core state.json schema.
    """

    agent_id: str
    phase: str  # Moon phase: dormant, waking, active, waning, empty
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Optional fields
    current_task: Optional[str] = None
    progress: Optional[float] = None  # 0.0 - 1.0
    stage: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Protocol version
    protocol_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result = {
            "_protocol_version": self.protocol_version,
            "agent_id": self.agent_id,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat() + "Z",
        }
        if self.current_task:
            result["current_task"] = self.current_task
        if self.progress is not None:
            result["progress"] = self.progress
        if self.stage:
            result["stage"] = self.stage
        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WireState:
        """Create from dict."""
        ts = data.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts[:-1]
        return cls(
            agent_id=data.get("agent_id", "unknown"),
            phase=data.get("phase", "empty"),
            timestamp=datetime.fromisoformat(ts) if ts else datetime.utcnow(),
            current_task=data.get("current_task"),
            progress=data.get("progress"),
            stage=data.get("stage"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            protocol_version=data.get("_protocol_version", "1.0"),
        )


class WireObservable:
    """
    Mixin to make any agent W-gent observable.

    Provides methods to:
    - Write state.json (current state snapshot)
    - Append to stream.log (event stream)
    - Write metrics.json (performance counters)

    Usage:
        class MyAgent(WireObservable):
            def __init__(self):
                super().__init__("my-agent")

            def do_work(self):
                self.update_state(phase="active", progress=0.5)
                self.log_event("INFO", "work", "Processing...")
    """

    def __init__(
        self,
        agent_name: str,
        wire_base: Optional[Path] = None,
    ):
        """
        Initialize wire observability.

        Args:
            agent_name: Unique identifier for this agent
            wire_base: Base directory for .wire files (default: ./.wire/{agent_name}/)
        """
        self.agent_name = agent_name
        self.wire_dir = wire_base or Path(f".wire/{agent_name}")
        self.wire_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.wire_dir / "state.json"
        self.stream_file = self.wire_dir / "stream.log"
        self.metrics_file = self.wire_dir / "metrics.json"
        self.output_dir = self.wire_dir / "output"
        self.output_dir.mkdir(exist_ok=True)

        # Track start time for uptime
        self._start_time = datetime.utcnow()

        # Initialize state
        self._current_state = WireState(
            agent_id=agent_name,
            phase="dormant",
        )
        self._write_state()

    def update_state(
        self,
        phase: Optional[str] = None,
        current_task: Optional[str] = None,
        progress: Optional[float] = None,
        stage: Optional[str] = None,
        error: Optional[str] = None,
        **metadata: Any,
    ) -> WireState:
        """
        Update state.json with new data.

        Args:
            phase: New phase (dormant, waking, active, waning, empty)
            current_task: Current task description
            progress: Progress value 0.0 - 1.0
            stage: Pipeline stage name
            error: Error message (sets phase to 'empty' if provided)
            **metadata: Additional metadata to include

        Returns:
            Updated WireState
        """
        if phase is not None:
            self._current_state.phase = phase
        if current_task is not None:
            self._current_state.current_task = current_task
        if progress is not None:
            self._current_state.progress = max(0.0, min(1.0, progress))
        if stage is not None:
            self._current_state.stage = stage
        if error is not None:
            self._current_state.error = error
            self._current_state.phase = "empty"
        if metadata:
            self._current_state.metadata.update(metadata)

        self._current_state.timestamp = datetime.utcnow()
        self._write_state()
        return self._current_state

    def log_event(
        self,
        level: str,
        stage: str,
        message: str,
    ) -> WireEvent:
        """
        Append to stream.log.

        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR)
            stage: Pipeline stage name
            message: Event message

        Returns:
            The created WireEvent
        """
        event = WireEvent(
            timestamp=datetime.utcnow(),
            level=level.upper(),
            stage=stage,
            message=message,
        )

        with open(self.stream_file, "a") as f:
            f.write(event.to_log_line() + "\n")

        return event

    def update_metrics(
        self,
        memory_mb: Optional[float] = None,
        api_calls: Optional[int] = None,
        tokens_processed: Optional[int] = None,
        **custom: Any,
    ) -> WireMetrics:
        """
        Update metrics.json with performance counters.

        Args:
            memory_mb: Memory usage in MB
            api_calls: Number of API calls made
            tokens_processed: Number of tokens processed
            **custom: Custom metrics

        Returns:
            The updated WireMetrics
        """
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        metrics = WireMetrics(
            uptime_seconds=uptime,
            memory_mb=memory_mb,
            api_calls=api_calls,
            tokens_processed=tokens_processed,
            custom=custom,
        )

        with open(self.metrics_file, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)

        return metrics

    def write_output(self, filename: str, content: str) -> Path:
        """
        Write an output file to the output/ directory.

        Args:
            filename: Name of the output file
            content: Content to write

        Returns:
            Path to the written file
        """
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            f.write(content)
        return output_path

    def get_state(self) -> WireState:
        """Get current state."""
        return self._current_state

    def get_stream(self, tail: Optional[int] = None) -> List[WireEvent]:
        """
        Read events from stream.log.

        Args:
            tail: Number of recent events to return (None = all)

        Returns:
            List of WireEvent objects
        """
        if not self.stream_file.exists():
            return []

        events = []
        with open(self.stream_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Parse log line: [timestamp] [level] [stage] message
                try:
                    # Extract parts
                    parts = line.split("] ", 3)
                    if len(parts) >= 4:
                        ts = parts[0][1:]  # Remove leading [
                        level = parts[1][1:]  # Remove leading [
                        stage = parts[2][1:]  # Remove leading [
                        message = parts[3]

                        if ts.endswith("Z"):
                            ts = ts[:-1]

                        events.append(
                            WireEvent(
                                timestamp=datetime.fromisoformat(ts),
                                level=level,
                                stage=stage,
                                message=message,
                            )
                        )
                except (ValueError, IndexError):
                    continue

        if tail is not None:
            events = events[-tail:]

        return events

    def cleanup(self) -> None:
        """
        Clean up wire files.

        Call this when agent is done to leave no trace.
        """
        import shutil

        if self.wire_dir.exists():
            shutil.rmtree(self.wire_dir)

    def _write_state(self) -> None:
        """Write current state to state.json."""
        with open(self.state_file, "w") as f:
            json.dump(self._current_state.to_dict(), f, indent=2)


class WireReader:
    """
    Read wire state from an observable agent.

    This is used by W-gent servers to read agent state without
    modifying it.
    """

    def __init__(self, agent_name: str, wire_base: Optional[Path] = None):
        """
        Initialize wire reader.

        Args:
            agent_name: Name of the agent to observe
            wire_base: Base directory for .wire files
        """
        self.agent_name = agent_name
        self.wire_dir = wire_base or Path(f".wire/{agent_name}")

        self.state_file = self.wire_dir / "state.json"
        self.stream_file = self.wire_dir / "stream.log"
        self.metrics_file = self.wire_dir / "metrics.json"
        self.output_dir = self.wire_dir / "output"

    def exists(self) -> bool:
        """Check if wire directory exists."""
        return self.wire_dir.exists()

    def read_state(self) -> Optional[WireState]:
        """Read current state from state.json."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            return WireState.from_dict(data)
        except (json.JSONDecodeError, IOError):
            return None

    def read_stream(self, tail: Optional[int] = None) -> List[WireEvent]:
        """Read events from stream.log."""
        if not self.stream_file.exists():
            return []

        events = []
        with open(self.stream_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split("] ", 3)
                    if len(parts) >= 4:
                        ts = parts[0][1:]
                        level = parts[1][1:]
                        stage = parts[2][1:]
                        message = parts[3]

                        if ts.endswith("Z"):
                            ts = ts[:-1]

                        events.append(
                            WireEvent(
                                timestamp=datetime.fromisoformat(ts),
                                level=level,
                                stage=stage,
                                message=message,
                            )
                        )
                except (ValueError, IndexError):
                    continue

        if tail is not None:
            events = events[-tail:]

        return events

    def read_metrics(self) -> Optional[WireMetrics]:
        """Read metrics from metrics.json."""
        if not self.metrics_file.exists():
            return None
        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)
            return WireMetrics(
                uptime_seconds=data.get("uptime_seconds", 0),
                memory_mb=data.get("memory_mb"),
                api_calls=data.get("api_calls"),
                tokens_processed=data.get("tokens_processed"),
                custom=data.get("custom", {}),
            )
        except (json.JSONDecodeError, IOError):
            return None

    def list_outputs(self) -> List[str]:
        """List output files."""
        if not self.output_dir.exists():
            return []
        return [f.name for f in self.output_dir.iterdir() if f.is_file()]

    def read_output(self, filename: str) -> Optional[str]:
        """Read an output file."""
        output_path = self.output_dir / filename
        if not output_path.exists():
            return None
        with open(output_path, "r") as f:
            return f.read()
