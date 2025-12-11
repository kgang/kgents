"""
Root pytest configuration for kgents.

Philosophy: Fixtures are curated, not accumulated.
Only fixtures used by 3+ test files belong here.

This implements Phase 1 of the test evolution plan:
- Centralized fixtures hierarchy
- Custom markers for law verification
- BootstrapWitness integration

Meta-Bootstrap: Test failures are algedonic signals.
Phase 2: Flinches now route through FlinchStore (D-gent backed)
with JSONL fallback for zero regression.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Meta-Bootstrap: Test Flinch Logging (Phase 2)
# =============================================================================

# Find project root (where .kgents/ lives)
_PROJECT_ROOT = Path(__file__).parent.parent.parent  # impl/claude -> kgents
_GHOST_DIR = _PROJECT_ROOT / ".kgents" / "ghost"
_FLINCH_FILE = _GHOST_DIR / "test_flinches.jsonl"

# Lazy-loaded FlinchStore (avoid import during pytest collection)
_flinch_store = None


def _get_flinch_store():
    """Get or create the FlinchStore singleton with JSONL fallback."""
    global _flinch_store
    if _flinch_store is None:
        try:
            from protocols.cli.devex.flinch_store import Flinch, get_flinch_store

            # Initialize with JSONL fallback (D-gent stores added lazily if available)
            _flinch_store = get_flinch_store(jsonl_fallback=_FLINCH_FILE)
        except ImportError:
            # Fallback: FlinchStore not available, return None
            _flinch_store = None
    return _flinch_store


def _emit_test_flinch(report) -> None:
    """
    Emit a flinch signal for a failing test.

    Flinches are algedonic signals - raw pain indicators that bypass
    semantic processing. They accumulate for pattern analysis.

    Phase 2: Routes through FlinchStore for D-gent integration.
    Falls back to direct JSONL write if FlinchStore unavailable.
    """
    try:
        store = _get_flinch_store()
        if store is not None:
            from protocols.cli.devex.flinch_store import Flinch

            flinch = Flinch.from_report(report)
            store.emit_sync(flinch)
        else:
            # Fallback: direct JSONL write (Phase 1 behavior)
            import json
            import time

            _GHOST_DIR.mkdir(parents=True, exist_ok=True)
            flinch = {
                "ts": time.time(),
                "test": report.nodeid,
                "phase": report.when,
                "duration": getattr(report, "duration", 0),
                "outcome": report.outcome,
            }
            with _FLINCH_FILE.open("a") as f:
                f.write(json.dumps(flinch) + "\n")
    except Exception:
        # Never let flinch logging break tests
        pass


def pytest_runtest_logreport(report):
    """Pytest hook: log failures as flinch signals."""
    if report.failed:
        _emit_test_flinch(report)


# =============================================================================
# Core Agent Fixtures
# =============================================================================


@dataclass
class MockAgent:
    """Minimal agent for testing composition."""

    name: str = "MockAgent"

    async def invoke(self, input: Any) -> Any:
        return input


@dataclass
class EchoAgent:
    """Agent that echoes input."""

    name: str = "EchoAgent"

    async def invoke(self, input: Any) -> str:
        return f"Echo: {input}"


@dataclass
class IdentityAgent:
    """The Id morphism - returns input unchanged."""

    name: str = "Id"

    async def invoke(self, input: Any) -> Any:
        return input

    def __rshift__(self, other):
        from bootstrap import compose

        return compose(self, other)


@pytest.fixture
def mock_agent() -> MockAgent:
    """Minimal agent fixture."""
    return MockAgent()


@pytest.fixture
def echo_agent() -> EchoAgent:
    """Echo agent fixture."""
    return EchoAgent()


@pytest.fixture
def identity_agent() -> IdentityAgent:
    """Identity morphism fixture."""
    return IdentityAgent()


# =============================================================================
# Storage Fixtures
# =============================================================================


@pytest.fixture
def volatile_store():
    """In-memory volatile storage for testing."""
    from agents.d import VolatileAgent

    return VolatileAgent(agent_id="test_volatile")


@pytest.fixture
async def memory_store():
    """Memory crystal store for testing (N-gent)."""
    # Note: MemoryCrystalStore may not exist yet
    # Return VolatileAgent as fallback
    from agents.d import VolatileAgent

    return VolatileAgent(agent_id="test_memory")


# =============================================================================
# DNA Fixtures
# =============================================================================


@pytest.fixture
def test_dna():
    """Standard test DNA configuration."""
    from bootstrap.dna import BaseDNA

    return BaseDNA.germinate(exploration_budget=0.1)


@pytest.fixture
def hypothesis_dna():
    """Hypothesis DNA for B-gent testing."""
    from bootstrap.dna import HypothesisDNA

    return HypothesisDNA.germinate(
        confidence_threshold=0.7,
        falsification_required=True,
        max_hypotheses=5,
    )


@pytest.fixture
def jgent_dna():
    """J-gent DNA for judgment testing."""
    from bootstrap.dna import JGentDNA

    return JGentDNA.germinate(
        max_depth=5,
        entropy_budget=1.0,
        decay_factor=0.5,
    )


# =============================================================================
# Embedding Fixtures
# =============================================================================


@pytest.fixture
def test_embedding():
    """Standard test embedding (384-dim zeros)."""
    return [0.0] * 384


@pytest.fixture
def random_embedding():
    """Random test embedding for similarity tests."""
    import random

    return [random.random() for _ in range(384)]


# =============================================================================
# Bootstrap Witness Fixtures
# =============================================================================


@pytest.fixture
def bootstrap_witness():
    """BootstrapWitness for law verification."""
    from agents.o.bootstrap_witness import create_bootstrap_witness

    return create_bootstrap_witness(test_iterations=5)


@pytest.fixture
async def verified_bootstrap(bootstrap_witness):
    """Pre-verified bootstrap state."""
    result = await bootstrap_witness.invoke()
    assert result.kernel_intact, "Bootstrap kernel compromised"
    return result


# =============================================================================
# Custom Markers
# =============================================================================


def pytest_configure(config):
    """Register custom markers for kgents testing."""
    # Law markers
    config.addinivalue_line(
        "markers", "law(name): mark test as category law verification"
    )
    config.addinivalue_line(
        "markers", "law_identity: tests identity law (Id >> f == f == f >> Id)"
    )
    config.addinivalue_line(
        "markers",
        "law_associativity: tests associativity ((f >> g) >> h == f >> (g >> h))",
    )
    config.addinivalue_line(
        "markers", "law_functor_identity: tests functor identity (fmap id == id)"
    )
    config.addinivalue_line(
        "markers",
        "law_functor_composition: tests functor composition (fmap (g.f) == fmap g . fmap f)",
    )

    # Meta markers
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    config.addinivalue_line(
        "markers", "accursed_share: mark test as exploratory/chaos (Phase 5)"
    )
    config.addinivalue_line(
        "markers", "property: mark test as property-based (Phase 3)"
    )

    # Register WitnessPlugin if --witness flag is used
    if config.getoption("--witness", default=False):
        from testing.pytest_witness import WitnessPlugin

        config.pluginmanager.register(WitnessPlugin(enabled=True), "witness")


def pytest_addoption(parser):
    """Add kgents-specific command line options."""
    parser.addoption(
        "--witness",
        action="store_true",
        default=False,
        help="Enable BootstrapWitness verification at session start",
    )
