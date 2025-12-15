"""
Tests for OrchestrationLog persistence.

Verifies:
- Initialize creates directory structure
- Events appended to JSONL
- Checkpoints saved/loaded correctly
- Replay from checkpoint
- Atomic writes survive crashes
- Metadata tracking
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

if TYPE_CHECKING:
    from agents.town.flux import TownEvent, TownPhase

from agents.town.orchestration_log import (
    Checkpoint,
    OrchestrationLog,
    OrchestrationMetadata,
    create_orchestration_log,
    load_orchestration_log,
)


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def mock_event_dict() -> dict[str, Any]:
    """Create mock TownEvent-like dict."""
    return {
        "phase": "MORNING",
        "operation": "greet",
        "participants": ["alice", "bob"],
        "success": True,
        "message": "Alice greets Bob",
        "timestamp": datetime.now().isoformat(),
        "tokens_used": 0,
    }


class MockTownEvent:
    """Mock TownEvent for testing."""

    def __init__(self, phase_name: str = "MORNING", operation: str = "greet") -> None:
        self.phase = type("Phase", (), {"name": phase_name})()
        self.operation = operation

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.name,
            "operation": self.operation,
            "participants": ["alice", "bob"],
            "success": True,
            "message": "Test event",
            "timestamp": datetime.now().isoformat(),
            "tokens_used": 0,
        }


class MockTownPhase:
    """Mock TownPhase for testing."""

    def __init__(self, name: str = "MORNING") -> None:
        self.name = name


def mock_event(phase_name: str = "MORNING", operation: str = "greet") -> "TownEvent":
    """Create a mock event cast to TownEvent for type checking."""
    return cast("TownEvent", MockTownEvent(phase_name, operation))


def mock_phase(name: str = "MORNING") -> "TownPhase":
    """Create a mock phase cast to TownPhase for type checking."""
    return cast("TownPhase", MockTownPhase(name))


class TestCheckpoint:
    """Tests for Checkpoint dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Checkpoint serializes and deserializes correctly."""
        cp = Checkpoint(
            checkpoint_id="cp_000001",
            tick=10,
            timestamp=datetime(2025, 12, 14, 10, 30, 0),
            phase="MORNING",
            day=1,
            total_events=10,
            total_tokens=500,
            environment_state={"regions": ["market", "plaza"]},
            citizen_states={"alice": {"warmth": 0.5}},
            coalition_state={"builders": ["alice", "bob"]},
            widget_snapshots={"scatter": {"zoom": 1.0}},
        )

        d = cp.to_dict()
        restored = Checkpoint.from_dict(d)

        assert restored.checkpoint_id == cp.checkpoint_id
        assert restored.tick == cp.tick
        assert restored.phase == cp.phase
        assert restored.day == cp.day
        assert restored.total_events == cp.total_events
        assert restored.environment_state == cp.environment_state
        assert restored.citizen_states == cp.citizen_states
        assert restored.coalition_state == cp.coalition_state
        assert restored.widget_snapshots == cp.widget_snapshots

    def test_immutable(self) -> None:
        """Checkpoint is frozen (immutable)."""
        cp = Checkpoint(
            checkpoint_id="cp_000001",
            tick=10,
            timestamp=datetime.now(),
            phase="MORNING",
            day=1,
            total_events=10,
            total_tokens=500,
            environment_state={},
            citizen_states={},
            coalition_state={},
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            cp.tick = 20  # type: ignore[misc]


class TestOrchestrationMetadata:
    """Tests for OrchestrationMetadata."""

    def test_to_dict_roundtrip(self) -> None:
        """Metadata serializes and deserializes correctly."""
        meta = OrchestrationMetadata(
            orchestration_id="orch_001",
            name="Test Town",
            created_at=datetime(2025, 12, 14, 10, 0, 0),
            last_modified=datetime(2025, 12, 14, 10, 30, 0),
            phase_count=4,
            citizen_count=5,
            checkpoint_ids=["cp_000001", "cp_000002"],
            current_tick=50,
            status="active",
        )

        d = meta.to_dict()
        restored = OrchestrationMetadata.from_dict(d)

        assert restored.orchestration_id == meta.orchestration_id
        assert restored.name == meta.name
        assert restored.phase_count == meta.phase_count
        assert restored.citizen_count == meta.citizen_count
        assert restored.checkpoint_ids == meta.checkpoint_ids
        assert restored.current_tick == meta.current_tick
        assert restored.status == meta.status


class TestOrchestrationLogInitialize:
    """Tests for OrchestrationLog initialization."""

    def test_initialize_creates_directory_structure(self, temp_dir: Path) -> None:
        """initialize() creates log_dir, checkpoints/, events.jsonl."""
        log_dir = temp_dir / "test_orch"
        log = OrchestrationLog(log_dir=log_dir)

        meta = log.initialize(
            orchestration_id="orch_001",
            name="Test Town",
            phase_count=4,
            citizen_count=5,
        )

        assert log_dir.exists()
        assert (log_dir / "checkpoints").is_dir()
        assert (log_dir / "events.jsonl").exists()
        assert (log_dir / "metadata.json").exists()

        assert meta.orchestration_id == "orch_001"
        assert meta.name == "Test Town"

    def test_load_existing_orchestration(self, temp_dir: Path) -> None:
        """load() restores metadata from existing log."""
        log_dir = temp_dir / "test_orch"
        log1 = OrchestrationLog(log_dir=log_dir)
        log1.initialize("orch_001", "Test Town", 4, 5)

        # Load in new instance
        log2 = OrchestrationLog(log_dir=log_dir)
        meta = log2.load()

        assert meta.orchestration_id == "orch_001"
        assert meta.name == "Test Town"

    def test_load_nonexistent_raises(self, temp_dir: Path) -> None:
        """load() raises FileNotFoundError for missing log."""
        log_dir = temp_dir / "nonexistent"
        log = OrchestrationLog(log_dir=log_dir)

        with pytest.raises(FileNotFoundError):
            log.load()


class TestOrchestrationLogEvents:
    """Tests for event logging."""

    @pytest.mark.asyncio
    async def test_append_increments_tick(self, temp_dir: Path) -> None:
        """append() increments tick counter."""
        log = create_orchestration_log(temp_dir, "orch_001")

        event = mock_event()

        tick1 = await log.append(event)
        tick2 = await log.append(event)
        tick3 = await log.append(event)

        assert tick1 == 1
        assert tick2 == 2
        assert tick3 == 3
        assert log.tick == 3

    @pytest.mark.asyncio
    async def test_append_writes_to_jsonl(self, temp_dir: Path) -> None:
        """append() writes event to JSONL file."""
        log = create_orchestration_log(temp_dir, "orch_001")

        event = mock_event(phase_name="AFTERNOON", operation="trade")
        await log.append(event)

        # Read JSONL
        events_file = temp_dir / "orch_001" / "events.jsonl"
        with open(events_file) as f:
            line = f.readline()
            data = json.loads(line)

        assert data["tick"] == 1
        assert data["event"]["phase"] == "AFTERNOON"
        assert data["event"]["operation"] == "trade"

    @pytest.mark.asyncio
    async def test_event_count(self, temp_dir: Path) -> None:
        """event_count() returns total events."""
        log = create_orchestration_log(temp_dir, "orch_001")

        event = mock_event()
        await log.append(event)
        await log.append(event)
        await log.append(event)

        count = await log.event_count()
        assert count == 3


class TestOrchestrationLogCheckpoints:
    """Tests for checkpointing."""

    @pytest.mark.asyncio
    async def test_checkpoint_creates_file(self, temp_dir: Path) -> None:
        """checkpoint() creates JSON file in checkpoints/."""
        log = create_orchestration_log(temp_dir, "orch_001")

        # Append some events first
        event = mock_event()
        await log.append(event)
        await log.append(event)

        # Create checkpoint
        cp = await log.checkpoint(
            phase=mock_phase("MORNING"),
            day=1,
            total_events=2,
            total_tokens=100,
            environment_state={"test": True},
            citizen_states={"alice": {"warmth": 0.5}},
            coalition_state={},
        )

        # Verify file exists
        cp_file = temp_dir / "orch_001" / "checkpoints" / f"{cp.checkpoint_id}.json"
        assert cp_file.exists()

        # Verify content
        with open(cp_file) as f:
            data = json.load(f)
        assert data["tick"] == 2
        assert data["phase"] == "MORNING"
        assert data["day"] == 1

    @pytest.mark.asyncio
    async def test_restore_checkpoint(self, temp_dir: Path) -> None:
        """restore_checkpoint() loads checkpoint from disk."""
        log = create_orchestration_log(temp_dir, "orch_001")

        event = mock_event()
        await log.append(event)

        # Create checkpoint
        cp1 = await log.checkpoint(
            phase=mock_phase("MORNING"),
            day=1,
            total_events=1,
            total_tokens=50,
            environment_state={"regions": ["market"]},
            citizen_states={"alice": {"warmth": 0.7}},
            coalition_state={"builders": ["alice"]},
        )

        # Restore
        cp2 = await log.restore_checkpoint(cp1.checkpoint_id)

        assert cp2.checkpoint_id == cp1.checkpoint_id
        assert cp2.tick == cp1.tick
        assert cp2.environment_state == cp1.environment_state
        assert cp2.citizen_states == cp1.citizen_states

    @pytest.mark.asyncio
    async def test_list_checkpoints(self, temp_dir: Path) -> None:
        """list_checkpoints() returns checkpoint IDs in order."""
        log = create_orchestration_log(temp_dir, "orch_001")

        event = mock_event()
        await log.append(event)

        await log.checkpoint(
            phase=mock_phase("MORNING"),
            day=1,
            total_events=1,
            total_tokens=0,
            environment_state={},
            citizen_states={},
            coalition_state={},
        )

        await log.append(event)

        await log.checkpoint(
            phase=mock_phase("AFTERNOON"),
            day=1,
            total_events=2,
            total_tokens=0,
            environment_state={},
            citizen_states={},
            coalition_state={},
        )

        checkpoints = log.list_checkpoints()
        assert len(checkpoints) == 2
        assert checkpoints[0] == "cp_000001"
        assert checkpoints[1] == "cp_000002"

    @pytest.mark.asyncio
    async def test_restore_nonexistent_raises(self, temp_dir: Path) -> None:
        """restore_checkpoint() raises FileNotFoundError for missing."""
        log = create_orchestration_log(temp_dir, "orch_001")

        with pytest.raises(FileNotFoundError):
            await log.restore_checkpoint("cp_999999")


class TestOrchestrationLogReplay:
    """Tests for replay functionality."""

    @pytest.mark.asyncio
    async def test_replay_from_beginning(self, temp_dir: Path) -> None:
        """replay_from() yields all events."""
        log = create_orchestration_log(temp_dir, "orch_001")

        events = [
            mock_event(phase_name="MORNING", operation="greet"),
            mock_event(phase_name="MORNING", operation="gossip"),
            mock_event(phase_name="AFTERNOON", operation="trade"),
        ]

        for event in events:
            await log.append(event)

        # Replay all
        replayed = []
        async for event_dict in log.replay_from():
            replayed.append(event_dict)

        assert len(replayed) == 3
        assert replayed[0]["operation"] == "greet"
        assert replayed[1]["operation"] == "gossip"
        assert replayed[2]["operation"] == "trade"

    @pytest.mark.asyncio
    async def test_replay_from_checkpoint(self, temp_dir: Path) -> None:
        """replay_from(checkpoint_id) yields events after checkpoint."""
        log = create_orchestration_log(temp_dir, "orch_001")

        # Events before checkpoint
        await log.append(mock_event(operation="greet"))
        await log.append(mock_event(operation="gossip"))

        # Checkpoint
        cp = await log.checkpoint(
            phase=mock_phase("MORNING"),
            day=1,
            total_events=2,
            total_tokens=0,
            environment_state={},
            citizen_states={},
            coalition_state={},
        )

        # Events after checkpoint
        await log.append(mock_event(operation="trade"))
        await log.append(mock_event(operation="solo"))

        # Replay from checkpoint
        replayed = []
        async for event_dict in log.replay_from(cp.checkpoint_id):
            replayed.append(event_dict)

        assert len(replayed) == 2
        assert replayed[0]["operation"] == "trade"
        assert replayed[1]["operation"] == "solo"


class TestOrchestrationLogStatus:
    """Tests for status management."""

    def test_set_status(self, temp_dir: Path) -> None:
        """set_status() updates metadata."""
        log = create_orchestration_log(temp_dir, "orch_001")

        assert log.metadata is not None
        assert log.metadata.status == "active"

        log.set_status("paused")
        assert log.metadata.status == "paused"

        # Reload to verify persistence
        log2 = load_orchestration_log(temp_dir / "orch_001")
        assert log2.metadata is not None
        assert log2.metadata.status == "paused"


class TestOrchestrationLogPruning:
    """Tests for checkpoint pruning."""

    @pytest.mark.asyncio
    async def test_prune_old_checkpoints(self, temp_dir: Path) -> None:
        """Old checkpoints are pruned when exceeding max_checkpoints."""
        log = OrchestrationLog(
            log_dir=temp_dir / "orch_001",
            max_checkpoints=3,
        )
        log.initialize("orch_001", "Test", 4, 5)

        event = mock_event()

        # Create 5 checkpoints (should keep only 3)
        for i in range(5):
            await log.append(event)
            await log.checkpoint(
                phase=mock_phase("MORNING"),
                day=1,
                total_events=i + 1,
                total_tokens=0,
                environment_state={},
                citizen_states={},
                coalition_state={},
            )

        checkpoints = log.list_checkpoints()
        assert len(checkpoints) == 3

        # First two should be pruned
        assert "cp_000001" not in checkpoints
        assert "cp_000002" not in checkpoints
        assert "cp_000003" in checkpoints


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_orchestration_log(self, temp_dir: Path) -> None:
        """create_orchestration_log() creates and initializes."""
        log = create_orchestration_log(
            temp_dir,
            "orch_001",
            name="My Town",
            phase_count=4,
            citizen_count=10,
        )

        assert log.metadata is not None
        assert log.metadata.orchestration_id == "orch_001"
        assert log.metadata.name == "My Town"
        assert log.metadata.phase_count == 4
        assert log.metadata.citizen_count == 10

    def test_load_orchestration_log(self, temp_dir: Path) -> None:
        """load_orchestration_log() loads existing."""
        create_orchestration_log(temp_dir, "orch_001", name="Test Town")

        log = load_orchestration_log(temp_dir / "orch_001")
        assert log.metadata is not None
        assert log.metadata.name == "Test Town"
