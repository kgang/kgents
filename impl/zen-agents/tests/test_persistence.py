"""Tests for persistence agents"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from zen_agents.types import SessionConfig, SessionType, SessionState
from zen_agents.persistence import (
    StateSave,
    StateLoad,
    state_save,
    state_load,
)


@pytest.mark.asyncio
class TestStateSave:
    async def test_save_state(self, sample_ground_state, temp_dir):
        save_path = temp_dir / "state.json"
        save_agent = StateSave(path=save_path)

        result = await save_agent.invoke(sample_ground_state)
        assert result == save_path
        assert save_path.exists()

        # Verify JSON structure
        with open(save_path) as f:
            data = json.load(f)
        assert "sessions" in data
        assert "config_cascade" in data
        assert "last_updated" in data

    async def test_save_creates_directory(self, sample_ground_state, temp_dir):
        nested_path = temp_dir / "nested" / "dir" / "state.json"
        save_agent = StateSave(path=nested_path)

        result = await save_agent.invoke(sample_ground_state)
        assert nested_path.exists()


@pytest.mark.asyncio
class TestStateLoad:
    async def test_load_nonexistent(self, temp_dir):
        load_path = temp_dir / "nonexistent.json"
        load_agent = StateLoad(default_path=load_path)

        result = await load_agent.invoke(load_path)
        assert result is None

    async def test_save_and_load_roundtrip(self, sample_ground_state, temp_dir):
        save_path = temp_dir / "state.json"

        # Save
        save_agent = StateSave(path=save_path)
        await save_agent.invoke(sample_ground_state)

        # Load
        load_agent = StateLoad(default_path=save_path)
        loaded = await load_agent.invoke(save_path)

        assert loaded is not None
        assert len(loaded.sessions) == len(sample_ground_state.sessions)
        assert loaded.max_sessions == sample_ground_state.max_sessions

    async def test_load_invalid_json(self, temp_dir):
        bad_path = temp_dir / "bad.json"
        bad_path.write_text("not valid json {{{")

        load_agent = StateLoad(default_path=bad_path)
        result = await load_agent.invoke(bad_path)
        assert result is None
