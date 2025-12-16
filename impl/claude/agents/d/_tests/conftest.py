"""
Pytest configuration for new D-gent tests.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from ..backends.memory import MemoryBackend
from ..backends.jsonl import JSONLBackend
from ..backends.sqlite import SQLiteBackend
from ..bus import DataBus


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for file-based backends."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Fresh memory backend for each test."""
    return MemoryBackend()


@pytest.fixture
def jsonl_backend(temp_dir: Path) -> Generator[JSONLBackend, None, None]:
    """Fresh JSONL backend for each test."""
    backend = JSONLBackend(namespace="test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture
def sqlite_backend(temp_dir: Path) -> Generator[SQLiteBackend, None, None]:
    """Fresh SQLite backend for each test."""
    backend = SQLiteBackend(namespace="test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture
def bus() -> DataBus:
    """Fresh data bus for each test."""
    return DataBus()
