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
from typing import Any, cast

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


def _get_flinch_store() -> Any:
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


def _emit_test_flinch(report: Any) -> None:
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
            flinch_data: dict[str, Any] = {
                "ts": time.time(),
                "test": report.nodeid,
                "phase": report.when,
                "duration": getattr(report, "duration", 0),
                "outcome": report.outcome,
            }
            with _FLINCH_FILE.open("a") as f:
                f.write(json.dumps(flinch_data) + "\n")
    except Exception:
        # Never let flinch logging break tests
        pass


def pytest_runtest_logreport(report: Any) -> None:
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

    def __rshift__(self, other: Any) -> Any:
        from agents.poly.types import Agent, ComposedAgent

        return ComposedAgent(cast(Agent[Any, Any], self), other)


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
def volatile_store() -> Any:
    """In-memory volatile storage for testing."""
    from agents.d import VolatileAgent

    return VolatileAgent(_state={})


@pytest.fixture
async def memory_store() -> Any:
    """Memory crystal store for testing (N-gent)."""
    # Note: MemoryCrystalStore may not exist yet
    # Return VolatileAgent as fallback
    from agents.d import VolatileAgent

    return VolatileAgent(_state={})


# =============================================================================
# DNA Fixtures
# =============================================================================


@pytest.fixture
def test_dna() -> Any:
    """Standard test DNA configuration."""
    from protocols.config.dna import BaseDNA

    return BaseDNA.germinate(exploration_budget=0.1)


@pytest.fixture
def hypothesis_dna() -> Any:
    """Hypothesis DNA for B-gent testing."""
    from protocols.config.dna import HypothesisDNA

    return HypothesisDNA.germinate(
        confidence_threshold=0.7,
        falsification_required=True,
        max_hypotheses=5,
    )


@pytest.fixture
def jgent_dna() -> Any:
    """J-gent DNA for judgment testing."""
    from protocols.config.dna import JGentDNA

    return JGentDNA.germinate(
        max_depth=5,
        entropy_budget=1.0,
        decay_factor=0.5,
    )


# =============================================================================
# Embedding Fixtures
# =============================================================================


@pytest.fixture
def test_embedding() -> list[float]:
    """Standard test embedding (384-dim zeros)."""
    return [0.0] * 384


@pytest.fixture
def random_embedding() -> list[float]:
    """Random test embedding for similarity tests."""
    import random

    return [random.random() for _ in range(384)]


# =============================================================================
# Bootstrap Witness Fixtures
# =============================================================================


@pytest.fixture
def bootstrap_witness() -> Any:
    """BootstrapWitness for law verification."""
    from agents.o.bootstrap_witness import create_bootstrap_witness

    return create_bootstrap_witness(test_iterations=5)


@pytest.fixture
async def verified_bootstrap(bootstrap_witness: Any) -> Any:
    """Pre-verified bootstrap state."""
    result = await bootstrap_witness.invoke()
    assert result.kernel_intact, "Bootstrap kernel compromised"
    return result


# =============================================================================
# Global Registry Population (xdist-safe)
# =============================================================================
#
# These fixtures ensure all global registries are populated at session start.
# This is CRITICAL for pytest-xdist parallel execution where each worker is
# a separate process with independent Python state.
#
# The Problem:
# - Global singletons (OperadRegistry, NodeRegistry) use class/module-level state
# - Registration happens at module import time (OperadRegistry.register(...))
# - In xdist, different workers may import different modules in different orders
# - Tests checking registry state fail inconsistently across workers
#
# The Solution:
# - Session-scoped fixtures that run ONCE per worker at session start
# - Import ALL modules that register with singletons
# - Place in ROOT conftest.py so ALL tests get consistent state
#
# WARNING: Do NOT reset these registries! Re-import won't re-register because
# Python caches modules. Only import, never clear.


def _populate_operad_registry() -> None:
    """Import all operad modules to trigger registration."""
    # Core (auto-registered)
    # Note: Atelier removed 2025-12-21

    # Brain
    from agents.brain.operad import BRAIN_OPERAD  # noqa: F401

    # Flow (4 operads)
    from agents.f.operad import (  # noqa: F401
        CHAT_OPERAD,
        COLLABORATION_OPERAD,
        FLOW_OPERAD,
        RESEARCH_OPERAD,
    )
    from agents.operad.core import AGENT_OPERAD  # noqa: F401

    # Park/Director
    from agents.park.operad import DIRECTOR_OPERAD  # noqa: F401

    # Town
    from agents.town.operad import TOWN_OPERAD  # noqa: F401

    # Growth
    from protocols.agentese.contexts.self_grow.operad import GROWTH_OPERAD  # noqa: F401

    # N-Phase
    from protocols.nphase.operad import NPHASE_OPERAD  # noqa: F401

    # Optional operads (may not exist in all configurations)
    try:
        from agents.emergence.operad import EMERGENCE_OPERAD  # noqa: F401
    except ImportError:
        pass

    try:
        from agents.design.operad import DESIGN_OPERAD  # noqa: F401
    except ImportError:
        pass

    try:
        from agents.differance.operad import TRACED_OPERAD  # noqa: F401
    except ImportError:
        pass


def _populate_node_registry() -> None:
    """Import all AGENTESE node modules to trigger @node registration."""
    from protocols.agentese.gateway import _import_node_modules

    _import_node_modules()


@pytest.fixture(scope="session", autouse=True)
def _ensure_global_registries_populated():
    """
    Ensure all global registries are populated at session start.

    This is the CRITICAL fixture for xdist-safe parallel execution.
    It runs ONCE per worker process before any tests execute.

    Canary tests: See agents/operad/_tests/test_xdist_registry_canary.py
    """
    _populate_operad_registry()
    _populate_node_registry()


# =============================================================================
# Custom Markers
# =============================================================================


def pytest_configure(config: Any) -> None:
    """Register custom markers for kgents testing."""
    import os

    # Disable auto-LLM creation during tests to avoid slow subprocess calls
    # Tests that need actual LLM should use MockLLMClient or explicitly set auto_llm=True
    os.environ.setdefault("KGENTS_NO_AUTO_LLM", "1")

    # Test Tier markers (stratified testing)
    # tier1: Unit tests - pure functions, no I/O, no mocks (<30s target)
    # tier2: Integration tests - mocked external deps (<5m target)
    # tier3: E2E tests - real external services (K8s, APIs)
    config.addinivalue_line("markers", "tier1: Unit tests (pure functions, no I/O, no mocks)")
    config.addinivalue_line("markers", "tier2: Integration tests (mocked external deps)")
    config.addinivalue_line("markers", "tier3: E2E tests (real external services like K8s cluster)")

    # Law markers
    config.addinivalue_line("markers", "law(name): mark test as category law verification")
    config.addinivalue_line("markers", "law_identity: tests identity law (Id >> f == f == f >> Id)")
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
    config.addinivalue_line("markers", "accursed_share: mark test as exploratory/chaos (Phase 5)")
    config.addinivalue_line("markers", "property: mark test as property-based (Phase 3)")
    config.addinivalue_line(
        "markers", "needs_llm: mark test as requiring real LLM (auto_llm enabled)"
    )
    config.addinivalue_line(
        "markers", "sentinel: mark test as CI safety/sentinel infrastructure (Phase 3)"
    )
    config.addinivalue_line(
        "markers", "llm_integration: mark test as requiring real LLM (ASHC VoidHarness)"
    )

    # Register WitnessPlugin if --witness flag is used
    if config.getoption("--witness", default=False):
        from testing.pytest_witness import WitnessPlugin

        config.pluginmanager.register(WitnessPlugin(enabled=True), "witness")

    # Register test optimization plugin if --profile-tests is used
    try:
        from testing.optimization.pytest_plugin import pytest_configure as opt_configure

        opt_configure(config)
    except ImportError:
        pass  # Plugin not available


def pytest_addoption(parser: Any) -> None:
    """Add kgents-specific command line options."""
    parser.addoption(
        "--witness",
        action="store_true",
        default=False,
        help="Enable BootstrapWitness verification at session start",
    )

    parser.addoption(
        "--run-llm-tests",
        action="store_true",
        default=False,
        help="Run LLM integration tests (ASHC VoidHarness). Also enabled by RUN_LLM_TESTS=1",
    )

    # Test optimization plugin options
    # Import and register the optimization plugin's options
    try:
        from testing.optimization.pytest_plugin import pytest_addoption as opt_addoption

        opt_addoption(parser)
    except ImportError:
        pass  # Plugin not available


# =============================================================================
# Domain Auto-Marking for Compartmentalized CI
# =============================================================================
#
# This hook automatically applies domain markers to tests based on file paths.
# Enables multi-agent CI where different domains run in parallel.
#
# Usage:
#   pytest -m "domain_foundation"           # Run only foundation tests
#   pytest -m "domain_crown or domain_cli"  # Run crown jewels + CLI
#   pytest -m "not domain_agents_aux"       # Skip auxiliary agents
#
# Domain boundaries align with architectural layers:
#   Foundation → Crown Jewels → AGENTESE → CLI → API
#
# =============================================================================

# Domain definitions: (marker_name, path_patterns)
# Order matters: first match wins
_DOMAIN_RULES: list[tuple[str, list[str]]] = [
    # Foundation: Pure category theory, no external deps
    (
        "domain_foundation",
        [
            "agents/poly/",
            "agents/operad/",
            "agents/sheaf/",
        ],
    ),
    # Crown Jewels: Core services with business logic
    (
        "domain_crown",
        [
            "services/brain/",
            "services/town/",
            "services/conductor/",
            "services/gestalt/",
            "services/gardener/",
            "services/park/",
            "services/forge/",
            "services/muse/",
            "services/morpheus/",
            "services/witness/",
            "services/coalition/",
            "services/chat/",
            "services/tooling/",
            "services/verification/",
            "services/interactive_text/",
            "services/principles/",
        ],
    ),
    # AGENTESE: Protocol layer
    (
        "domain_agentese",
        [
            "protocols/agentese/",
        ],
    ),
    # CLI: Command-line interface
    (
        "domain_cli",
        [
            "protocols/cli/",
        ],
    ),
    # API: HTTP/billing protocols
    (
        "domain_api",
        [
            "protocols/api/",
            "protocols/billing/",
            "protocols/licensing/",
            "protocols/tenancy/",
        ],
    ),
    # Core Agents: High-traffic agent modules
    (
        "domain_agents_core",
        [
            "agents/k/",
            "agents/town/",
            "agents/brain/",
            "agents/f/",
            "agents/j/",
            "agents/flux/",
        ],
    ),
    # Auxiliary Agents: Supporting agent modules
    (
        "domain_agents_aux",
        [
            "agents/a/",
            "agents/b/",
            "agents/c/",
            "agents/d/",
            "agents/g/",
            "agents/i/",
            "agents/l/",
            "agents/m/",
            "agents/n/",
            "agents/o/",
            "agents/p/",
            "agents/s/",
            "agents/t/",
            "agents/u/",
            "agents/v/",
            "agents/w/",
            "agents/atelier/",
            "agents/design/",
            "agents/differance/",
            "agents/emergence/",
            "agents/gallery/",
            "agents/gardener/",
            "agents/gestalt/",
            "agents/infra/",
            "agents/park/",
            "agents/domain/",
            "agents/shared/",
            "agents/testagent/",
        ],
    ),
    # Infrastructure: Shared utilities and system
    (
        "domain_infra",
        [
            "weave/",
            "field/",
            "hypha/",
            "shared/",
            "system/",
            "bootstrap/",
            "runtime/",
            "testing/",
            "infra/",
            "poly/",  # Root-level poly (distinct from agents/poly/)
            "models/",  # Data models
            "services/_tests/",  # Root-level service tests
        ],
    ),
    # Protocol Infrastructure: Protocol subdirs not in AGENTESE/CLI/API
    # Must come AFTER specific protocol domains but BEFORE agent catch-alls
    (
        "domain_agentese",
        [
            "protocols/garden/",  # Garden protocol
            "protocols/gardener_logos/",  # Gardener logos
            "protocols/gestalt/",  # Gestalt protocol
            "protocols/nphase/",  # N-phase protocol
            "protocols/projection/",  # Projection layer
            "protocols/prompt/",  # Prompt templates
            "protocols/streaming/",  # Streaming protocol
            "protocols/synergy/",  # Event synergy
            "protocols/config/",  # Config protocol
            "protocols/proto/",  # Proto definitions
            "protocols/_archived/",  # Archived protocols
            "protocols/_tests/",  # Root-level protocol tests
        ],
    ),
    # Catch-all for remaining agent-level tests (e.g., agents/_tests/)
    # Must come LAST - catches integration tests at agents root
    (
        "domain_agents_core",
        [
            "agents/_tests/",  # Root-level agent integration tests
        ],
    ),
]


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """
    Auto-apply domain markers and skip LLM tests unless explicitly requested.

    LLM tests (ASHC VoidHarness) are skipped unless:
    - --run-llm-tests flag is passed
    - RUN_LLM_TESTS=1 environment variable is set

    Domain markers enable compartmentalized CI where different test domains
    run in parallel, reducing feedback time for multi-agent development.
    """
    import os

    # Check if LLM tests should run
    run_llm = config.getoption("--run-llm-tests", default=False) or os.getenv("RUN_LLM_TESTS")
    skip_llm = pytest.mark.skip(
        reason="LLM tests require --run-llm-tests flag or RUN_LLM_TESTS=1 env var"
    )

    for item in items:
        # Get relative path from impl/claude/
        path = str(item.fspath)

        # Skip LLM integration tests unless explicitly enabled
        # Check for: marker, path contains 'integration', or file named test_*_integration.py
        is_llm_test = (
            item.get_closest_marker("llm_integration") is not None or "integration" in path
        )
        if is_llm_test and not run_llm:
            item.add_marker(skip_llm)

        # Find matching domain
        for marker_name, patterns in _DOMAIN_RULES:
            if any(pattern in path for pattern in patterns):
                item.add_marker(getattr(pytest.mark, marker_name))
                break
        # Tests not matching any domain remain unmarked (will run with all)
