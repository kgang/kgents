"""
Test fixtures for new M-gent tests.

Provides Memory, AssociativeMemory, and DataBus fixtures.

V-gent Integration (Phase 5):
    - vgent_memory_backend: In-memory V-gent backend
    - vgent_associative_memory: AssociativeMemory with V-gent integration
"""

from __future__ import annotations

from typing import AsyncGenerator

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.d.bus import DataBus, get_data_bus, reset_data_bus
from agents.m.associative import AssociativeMemory
from agents.m.memory import Lifecycle, Memory, simple_embedding
from agents.v import MemoryVectorBackend

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


# === V-gent Integration Fixtures ===


@pytest.fixture
def vgent_memory_backend() -> MemoryVectorBackend:
    """In-memory V-gent backend for testing.

    Uses dimension=64 to match HashEmbedder default.
    """
    return MemoryVectorBackend(dimension=64)


@pytest.fixture
async def vgent_associative_memory(
    memory_backend: MemoryBackend,
    vgent_memory_backend: MemoryVectorBackend,
) -> AssociativeMemory:
    """AssociativeMemory with V-gent integration."""
    return await AssociativeMemory.create_with_vgent(
        dgent=memory_backend,
        vgent=vgent_memory_backend,
    )


@pytest.fixture
async def populated_vgent_memory(
    vgent_associative_memory: AssociativeMemory,
) -> AssociativeMemory:
    """V-gent-backed AssociativeMemory with sample memories."""
    await vgent_associative_memory.remember(
        b"Python is a programming language",
        metadata={"topic": "programming"},
    )
    await vgent_associative_memory.remember(
        b"JavaScript runs in browsers",
        metadata={"topic": "programming"},
    )
    await vgent_associative_memory.remember(
        b"The quick brown fox jumps",
        metadata={"topic": "animals"},
    )
    await vgent_associative_memory.remember(
        b"Machine learning uses neural networks",
        metadata={"topic": "ai"},
    )
    return vgent_associative_memory
