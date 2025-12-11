"""
L-gent test fixtures.

Provides shared fixtures for L-gent tests including:
- Registry: In-memory catalog for testing
- Lattice: Type lattice for composition verification
"""

import pytest
from agents.l.lattice import create_lattice
from agents.l.registry import Registry


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return Registry()


@pytest.fixture
def lattice(registry):
    """Create a lattice with a registry."""
    return create_lattice(registry)
