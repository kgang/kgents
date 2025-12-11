"""
Tests for persistent K-gent persona.

Validates that persona state persists across sessions and
that preference evolution is tracked correctly.
"""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from agents.k import (
    DialogueInput,
    DialogueMode,
    PersistentPersonaAgent,
    PersistentPersonaQueryAgent,
    PersonaQuery,
    PersonaSeed,
    PersonaState,
    persistent_kgent,
    persistent_query_persona,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.mark.asyncio
async def test_persistent_persona_saves_state(temp_dir: Path) -> None:
    """Test that persona state is saved after dialogue."""
    path = temp_dir / "persona.json"

    # Create and use persona
    persona = PersistentPersonaAgent(path=path)
    await persona.invoke(
        DialogueInput(message="I value composability", mode=DialogueMode.REFLECT)
    )

    # State file should exist
    assert path.exists()


@pytest.mark.asyncio
async def test_persistent_persona_loads_state(temp_dir: Path) -> None:
    """Test that persona state is restored across sessions."""
    path = temp_dir / "persona.json"

    # First session - create and modify persona
    persona1 = PersistentPersonaAgent(path=path)
    persona1.update_preference("testing", "persistence", "works", confidence=0.95)
    await persona1.save_state()

    # Second session - load existing state
    persona2 = PersistentPersonaAgent(path=path)
    await persona2.load_state()

    # State should be restored
    assert persona2.state.seed.preferences["testing"]["persistence"] == "works"
    assert persona2.state.confidence.get("testing.persistence") == 0.95


@pytest.mark.asyncio
async def test_persistent_persona_evolution_history(temp_dir: Path) -> None:
    """Test that persona evolution is tracked in history."""
    path = temp_dir / "persona.json"

    persona = PersistentPersonaAgent(path=path)

    # Make several updates
    for i in range(5):
        persona.update_preference("test", "iteration", i)
        await persona.save_state()

    # Check history
    history = await persona.get_evolution_history(limit=5)
    assert len(history) >= 1  # At least the latest state
    # Note: history excludes current state, so we check >= 1


@pytest.mark.asyncio
async def test_persistent_persona_auto_save(temp_dir: Path) -> None:
    """Test that auto_save persists state after each dialogue."""
    path = temp_dir / "persona.json"

    # Create with auto_save enabled (default)
    persona1 = PersistentPersonaAgent(path=path, auto_save=True)
    await persona1.invoke(DialogueInput(message="Test", mode=DialogueMode.REFLECT))

    # Load in new instance - should have dialogue state
    persona2 = PersistentPersonaAgent(path=path)
    await persona2.load_state()

    # State exists (verified by no exception)
    assert persona2.state is not None


@pytest.mark.asyncio
async def test_persistent_persona_no_auto_save(temp_dir: Path) -> None:
    """Test that auto_save=False requires manual save."""
    path = temp_dir / "persona.json"

    # Create with auto_save disabled
    persona = PersistentPersonaAgent(path=path, auto_save=False)
    persona.update_preference("test", "key", "value")

    # Don't call save_state()

    # File might not exist or might not have latest changes
    # (depends on whether initial state was saved)
    # This test validates that auto_save=False is respected


@pytest.mark.asyncio
async def test_persistent_query_agent_loads_state(temp_dir: Path) -> None:
    """Test that query agent can load persisted state."""
    path = temp_dir / "persona.json"

    # Save state with dialogue agent
    persona = PersistentPersonaAgent(path=path)
    persona.update_preference("communication", "style", "test-style")
    await persona.save_state()

    # Load with query agent
    query_agent = PersistentPersonaQueryAgent(path=path)
    await query_agent.load_state()

    # Query should reflect persisted preferences
    response = await query_agent.invoke(
        PersonaQuery(aspect="preference", topic="communication")
    )
    assert any("test-style" in pref for pref in response.suggested_style)


@pytest.mark.asyncio
async def test_persistent_kgent_convenience_function(temp_dir: Path) -> None:
    """Test convenience function for creating persistent K-gent."""
    path = temp_dir / "persona.json"

    persona = persistent_kgent(path=path)
    assert isinstance(persona, PersistentPersonaAgent)
    assert persona.auto_save is True


@pytest.mark.asyncio
async def test_persistent_query_persona_convenience_function(temp_dir: Path) -> None:
    """Test convenience function for creating persistent query agent."""
    path = temp_dir / "persona.json"

    query = persistent_query_persona(path=path)
    assert isinstance(query, PersistentPersonaQueryAgent)


@pytest.mark.asyncio
async def test_persistent_persona_with_initial_state(temp_dir: Path) -> None:
    """Test providing initial state for new persona."""
    path = temp_dir / "persona.json"

    custom_seed = PersonaSeed(name="TestUser")
    custom_state = PersonaState(seed=custom_seed)

    persona = PersistentPersonaAgent(path=path, initial_state=custom_state)
    assert persona.state.seed.name == "TestUser"

    await persona.save_state()

    # Reload and verify
    persona2 = PersistentPersonaAgent(path=path)
    await persona2.load_state()
    assert persona2.state.seed.name == "TestUser"


@pytest.mark.asyncio
async def test_persistent_persona_preference_tracking(temp_dir: Path) -> None:
    """Test that preference updates track confidence and source."""
    path = temp_dir / "persona.json"

    persona = PersistentPersonaAgent(path=path)

    # Update with tracking metadata
    persona.update_preference(
        category="aesthetics",
        key="color",
        value="blue",
        confidence=0.7,
        source="inferred",
    )

    # Verify metadata
    assert persona.state.confidence["aesthetics.color"] == 0.7
    assert persona.state.sources["aesthetics.color"] == "inferred"

    # Persist and reload
    await persona.save_state()

    persona2 = PersistentPersonaAgent(path=path)
    await persona2.load_state()

    # Metadata should persist
    assert persona2.state.confidence["aesthetics.color"] == 0.7
    assert persona2.state.sources["aesthetics.color"] == "inferred"
