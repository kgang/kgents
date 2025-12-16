"""
Test fixtures for new M-gent tests.

Provides Memory, AssociativeMemory, and DataBus fixtures.
"""

from __future__ import annotations

import pytest
from typing import AsyncGenerator

from agents.d.backends.memory import MemoryBackend
from agents.d.bus import DataBus, get_data_bus, reset_data_bus
from agents.m.memory import Memory, Lifecycle, simple_embedding
from agents.m.associative import AssociativeMemory


# === Memory Fixtures ===


@pytest.fixture
def memory_basic() -> Memory:
    """Basic memory with default values."""
    return Memory.create(
        datum_id="test_datum_001",
        embedding=simple_embedding("test content"),
    )


@pytest.fixture
def memory_with_metadata() -> Memory:
    """Memory with metadata."""
    return Memory.create(
        datum_id="test_datum_002",
        embedding=simple_embedding("test content with metadata"),
        metadata={"topic": "testing", "author": "claude"},
    )


@pytest.fixture
def memory_low_relevance() -> Memory:
    """Memory with low relevance (candidate for forgetting)."""
    memory = Memory.create(
        datum_id="test_datum_003",
        embedding=simple_embedding("low relevance content"),
        relevance=0.1,
    )
    return memory


@pytest.fixture
def memory_cherished() -> Memory:
    """Cherished memory (protected from forgetting)."""
    memory = Memory.create(
        datum_id="test_datum_004",
        embedding=simple_embedding("cherished content"),
    )
    return memory.cherish()


# === D-gent Backend Fixtures ===


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """In-memory D-gent backend."""
    return MemoryBackend()


# === M-gent Fixtures ===


@pytest.fixture
def associative_memory(memory_backend: MemoryBackend) -> AssociativeMemory:
    """AssociativeMemory with in-memory backend."""
    return AssociativeMemory(dgent=memory_backend)


# === Data Bus Fixtures ===


@pytest.fixture
def data_bus() -> DataBus:
    """Fresh DataBus instance."""
    reset_data_bus()
    return get_data_bus()


@pytest.fixture
async def populated_memory(
    associative_memory: AssociativeMemory,
) -> AssociativeMemory:
    """AssociativeMemory with sample memories."""
    # Add some test memories
    await associative_memory.remember(
        b"Python is a programming language",
        metadata={"topic": "programming"},
    )
    await associative_memory.remember(
        b"JavaScript runs in browsers",
        metadata={"topic": "programming"},
    )
    await associative_memory.remember(
        b"The quick brown fox jumps",
        metadata={"topic": "animals"},
    )
    await associative_memory.remember(
        b"Machine learning uses neural networks",
        metadata={"topic": "ai"},
    )
    return associative_memory
