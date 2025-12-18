"""
L-gent test fixtures.

Provides shared fixtures for L-gent tests including:
- Registry: In-memory catalog for testing
- Lattice: Type lattice for composition verification
"""

from __future__ import annotations

import pytest

from agents.l.lattice import TypeLattice, create_lattice
from agents.l.registry import Registry


@pytest.fixture
def registry() -> Registry:
    """Create a fresh registry for each test."""
    return Registry()


@pytest.fixture
def lattice(registry: Registry) -> TypeLattice:
    """Create a lattice with a registry."""
    return create_lattice(registry)
