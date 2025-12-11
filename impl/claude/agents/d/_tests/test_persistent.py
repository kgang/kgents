"""Tests for PersistentAgent."""

import tempfile
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from agents.d.errors import StateCorruptionError, StateNotFoundError
from agents.d.persistent import PersistentAgent


@dataclass
class UserProfile:
    """Test state type."""

    name: str
    age: int


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for state files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def dgent(temp_dir: Path) -> PersistentAgent[UserProfile]:
    """PersistentAgent fixture with UserProfile."""
    return PersistentAgent(
        path=temp_dir / "state.json", schema=UserProfile, max_history=10
    )


@pytest.mark.asyncio
async def test_load_nonexistent_raises(dgent: PersistentAgent[UserProfile]) -> None:
    """Loading from nonexistent file raises StateNotFoundError."""
    with pytest.raises(StateNotFoundError):
        await dgent.load()


@pytest.mark.asyncio
async def test_save_and_load_round_trip(dgent: PersistentAgent[UserProfile]) -> None:
    """State survives save → load cycle."""
    original = UserProfile(name="Alice", age=30)

    await dgent.save(original)
    loaded = await dgent.load()

    assert loaded == original
    assert loaded.name == "Alice"
    assert loaded.age == 30


@pytest.mark.asyncio
async def test_multiple_saves_updates_state(
    dgent: PersistentAgent[UserProfile],
) -> None:
    """Multiple saves update state correctly."""
    await dgent.save(UserProfile(name="Alice", age=30))
    await dgent.save(UserProfile(name="Bob", age=25))
    await dgent.save(UserProfile(name="Carol", age=35))

    final = await dgent.load()
    assert final.name == "Carol"
    assert final.age == 35


@pytest.mark.asyncio
async def test_crash_recovery(temp_dir: Path) -> None:
    """State persists across D-gent instances (simulated crash)."""
    path = temp_dir / "state.json"
    original = UserProfile(name="Alice", age=30)

    # First instance: save state
    dgent1 = PersistentAgent(path=path, schema=UserProfile)
    await dgent1.save(original)

    # Simulate crash: delete object
    del dgent1

    # Second instance: load should succeed
    dgent2 = PersistentAgent(path=path, schema=UserProfile)
    loaded = await dgent2.load()

    assert loaded == original


@pytest.mark.asyncio
async def test_history_tracks_states(dgent: PersistentAgent[UserProfile]) -> None:
    """History records past states."""
    await dgent.save(UserProfile(name="Alice", age=30))
    await dgent.save(UserProfile(name="Bob", age=25))
    await dgent.save(UserProfile(name="Carol", age=35))

    history = await dgent.history()

    # History excludes current state, newest first
    assert len(history) == 3
    assert history[0].name == "Carol"
    assert history[1].name == "Bob"
    assert history[2].name == "Alice"


@pytest.mark.asyncio
async def test_history_limit(dgent: PersistentAgent[UserProfile]) -> None:
    """History respects limit parameter."""
    for i in range(10):
        await dgent.save(UserProfile(name=f"User{i}", age=20 + i))

    history = await dgent.history(limit=3)
    assert len(history) == 3


@pytest.mark.asyncio
async def test_history_bounded(temp_dir: Path) -> None:
    """History is bounded by max_history."""
    dgent = PersistentAgent(
        path=temp_dir / "state.json", schema=UserProfile, max_history=5
    )

    # Save 10 states
    for i in range(10):
        await dgent.save(UserProfile(name=f"User{i}", age=20 + i))

    history = await dgent.history()

    # Should only keep last 5
    assert len(history) <= 5


@pytest.mark.asyncio
async def test_empty_history_before_saves(dgent: PersistentAgent[UserProfile]) -> None:
    """History is empty before any saves."""
    # Save initial state (no history yet)
    await dgent.save(UserProfile(name="Alice", age=30))

    history = await dgent.history()
    # First save has no history
    assert len(history) == 1  # Just the initial save


@pytest.mark.asyncio
async def test_isolation_deepcopy(dgent: PersistentAgent[UserProfile]) -> None:
    """Loaded state is independent copy (mutations don't affect storage)."""
    original = UserProfile(name="Alice", age=30)
    await dgent.save(original)

    # Load and mutate
    loaded1 = await dgent.load()
    loaded1.age = 99

    # Load again - should be unchanged
    loaded2 = await dgent.load()
    assert loaded2.age == 30  # Not 99


@pytest.mark.asyncio
async def test_atomic_write_leaves_no_temp_files(
    dgent: PersistentAgent[UserProfile],
) -> None:
    """Atomic writes clean up temporary files."""
    await dgent.save(UserProfile(name="Alice", age=30))

    # Check no .tmp files left behind
    temp_files = list(dgent.path.parent.glob("*.tmp"))
    assert len(temp_files) == 0


@pytest.mark.asyncio
async def test_corrupted_json_raises(
    dgent: PersistentAgent[UserProfile], temp_dir: Path
) -> None:
    """Corrupted JSON raises StateCorruptionError."""
    # Write invalid JSON
    with open(dgent.path, "w") as f:
        f.write("{invalid json!}")

    with pytest.raises(StateCorruptionError):
        await dgent.load()


@pytest.mark.asyncio
async def test_primitive_state(temp_dir: Path) -> None:
    """PersistentAgent works with primitive types (not just dataclasses)."""
    dgent = PersistentAgent(path=temp_dir / "state.json", schema=dict)

    state = {"name": "Alice", "count": 42}
    await dgent.save(state)

    loaded = await dgent.load()
    assert loaded == state


@pytest.mark.asyncio
async def test_list_state(temp_dir: Path) -> None:
    """PersistentAgent works with list states."""
    dgent = PersistentAgent(path=temp_dir / "state.json", schema=list)

    state = [1, 2, 3, 4, 5]
    await dgent.save(state)

    loaded = await dgent.load()
    assert loaded == state
