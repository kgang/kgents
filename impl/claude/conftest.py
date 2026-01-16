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

=============================================================================
TESTING GOTCHAS (Read docs/skills/test-patterns.md for full patterns)
=============================================================================

1. TIMING TESTS: Use `preferred_backend="memory"` to avoid Postgres index
   lock contention (15-17s) under parallel xdist. Test capture() latency,
   not DB initialization.

2. HYPOTHESIS SLOW: Property tests generating PolyAgent chains take 1.3-1.5s
   per input. Use `suppress_health_check=[HealthCheck.too_slow]` - slowness
   IS thoroughness for categorical law tests.

3. DOMAIN OPERADS: ProbeOperad uses 'witness' not 'trace'. Add domain operads
   to DOMAIN_OPERADS list in test_registry_ci_gate.py - they have their own
   vocabulary.

4. HEURISTIC ASSERTIONS: Don't assert exact values for ML/heuristic outputs
   (Galois layer assignment). Assert valid ranges: `0 <= layer <= 7`.

5. LEGACY REMOVAL CASCADE: Removing from LEGACY_COMMANDS breaks downstream
   tests in: TestLegacyMappings, TestRouterIntegration, TestLongestPrefixMatching.

6. EXIT 137 = OOM: Reduce `-n` workers or run sequentially. Not a test logic error.

7. CONSTITUTION EVOLUTION: When K-Block count changes (22→23), update ALL tests
   that assert counts, with comments documenting the breakdown.
=============================================================================
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

    # Note: Park/Director operad removed 2025-12-21
    # Town
    from agents.town.operad import TOWN_OPERAD  # noqa: F401

    # Growth
    from protocols.agentese.contexts.self_grow.operad import GROWTH_OPERAD  # noqa: F401

    # N-Phase
    from protocols.nphase.operad import NPHASE_OPERAD  # noqa: F401

    # Optional operads (may not exist in all configurations)
    # Note: agents.emergence removed 2025-12-21

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
# Zombie Worker Cleanup & Session Watchdog
# =============================================================================
#
# Problem: pytest-xdist workers (`python3 -u -c import sys;exec(...)`) become
# orphaned when pytest is interrupted. They accumulate across sessions, consuming
# CPU and memory, and can cause subsequent pytest runs to hang.
#
# Solution (3-layer defense):
# 1. SESSION START: Kill orphan workers from previous runs
# 2. SESSION WATCHDOG: Auto-kill entire session after timeout (default: 10 min)
# 3. ATEXIT HANDLER: Best-effort cleanup on normal/abnormal exit
#
# Override timeout: PYTEST_SESSION_TIMEOUT_MINUTES=15
# Disable watchdog: PYTEST_SESSION_TIMEOUT_MINUTES=0
# =============================================================================

import atexit
import os
import signal
import subprocess
import threading
import time

# Watchdog state (module-level for atexit access)
_watchdog_thread: threading.Thread | None = None
_watchdog_stop_event = threading.Event()
_session_pid: int | None = None


def _kill_orphan_xdist_workers() -> int:
    """
    Kill orphan pytest-xdist workers from previous sessions.

    Returns number of processes killed.

    These workers are identifiable by their command signature:
        python3 -u -c import sys;exec(eval(sys.stdin.readline()))

    They become orphaned when:
    - pytest is killed with Ctrl+C
    - pytest times out
    - Parent process crashes
    """
    killed = 0
    try:
        # Find all xdist worker processes
        result = subprocess.run(
            ["pgrep", "-f", r"import sys;exec\(eval\(sys.stdin.readline\(\)\)\)"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            current_pid = os.getpid()
            current_ppid = os.getppid()

            for pid_str in pids:
                try:
                    pid = int(pid_str.strip())
                    # Don't kill our own children (they're from this session)
                    # Check if this pid's parent is our pytest process
                    ppid_result = subprocess.run(
                        ["ps", "-o", "ppid=", "-p", str(pid)],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    if ppid_result.returncode == 0:
                        parent_pid = int(ppid_result.stdout.strip())
                        # If parent is init (1) or doesn't match current session, it's orphaned
                        if parent_pid == 1 or (
                            parent_pid != current_pid and parent_pid != current_ppid
                        ):
                            os.kill(pid, signal.SIGKILL)
                            killed += 1
                except (ValueError, ProcessLookupError, PermissionError):
                    continue

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # pgrep not available or other error - skip cleanup
        pass

    return killed


def _watchdog_worker(timeout_seconds: int, session_pid: int) -> None:
    """
    Background thread that monitors session duration.

    If the session exceeds timeout_seconds, it kills the entire process tree.
    """
    start_time = time.time()

    while not _watchdog_stop_event.is_set():
        elapsed = time.time() - start_time

        if elapsed >= timeout_seconds:
            # Time's up - kill the session
            import sys

            print(
                f"\n\n{'=' * 60}\n"
                f"⏰ PYTEST SESSION TIMEOUT ({timeout_seconds // 60} minutes)\n"
                f"Killing pytest and all workers to prevent zombie accumulation.\n"
                f"Override: PYTEST_SESSION_TIMEOUT_MINUTES=N (0 to disable)\n"
                f"{'=' * 60}\n",
                file=sys.stderr,
            )

            # Kill our own process group (includes all xdist workers)
            try:
                os.killpg(os.getpgid(session_pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass

            # Give processes 2 seconds to cleanup, then SIGKILL
            time.sleep(2)

            try:
                os.killpg(os.getpgid(session_pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

            # Last resort: kill ourselves
            os._exit(1)

        # Check every 5 seconds
        _watchdog_stop_event.wait(5)


def _cleanup_on_exit() -> None:
    """atexit handler: Stop watchdog and kill any remaining workers."""
    global _watchdog_thread

    # Signal watchdog to stop
    _watchdog_stop_event.set()

    if _watchdog_thread is not None:
        _watchdog_thread.join(timeout=1)

    # Best-effort cleanup of any workers we spawned
    # (They should die with us, but be safe)
    _kill_orphan_xdist_workers()


# Register atexit handler once at module load
atexit.register(_cleanup_on_exit)


@pytest.fixture(scope="session", autouse=True)
def _xdist_worker_watchdog(request: Any) -> Any:
    """
    Session fixture that manages xdist worker lifecycle.

    1. Cleans up orphan workers from previous sessions
    2. Starts a watchdog thread to enforce session timeout
    3. Ensures clean shutdown on session end
    """
    global _watchdog_thread, _session_pid

    # Get timeout from environment (default: 10 minutes)
    # Supports fractional minutes: 0.5 = 30 seconds
    timeout_minutes = float(os.environ.get("PYTEST_SESSION_TIMEOUT_MINUTES", "10"))
    timeout_seconds = int(timeout_minutes * 60)

    # Phase 1: Clean up orphans from previous sessions
    killed = _kill_orphan_xdist_workers()
    if killed > 0:
        import sys

        print(
            f"🧹 Cleaned up {killed} orphan xdist worker(s) from previous sessions",
            file=sys.stderr,
        )

    # Phase 2: Start watchdog (if timeout enabled)
    if timeout_seconds > 0:
        _session_pid = os.getpid()
        _watchdog_stop_event.clear()

        _watchdog_thread = threading.Thread(
            target=_watchdog_worker,
            args=(timeout_seconds, _session_pid),
            daemon=True,  # Die with main process
            name="pytest-session-watchdog",
        )
        _watchdog_thread.start()

    yield

    # Phase 3: Clean shutdown
    _watchdog_stop_event.set()
    if _watchdog_thread is not None:
        _watchdog_thread.join(timeout=1)


# =============================================================================
# CPU Throttling: Dynamic Worker Count (pytest-xdist)
# =============================================================================
#
# This hook implements self-throttling for parallel test execution.
# It prevents CPU thrashing by adapting worker count to current system load.
#
# Philosophy (Heterarchical principle):
# - Resources flow where needed, not allocated top-down
# - The system self-adjusts based on current conditions
# - Leave headroom for the OS and other processes
#
# Override via environment variable: PYTEST_XDIST_AUTO_NUM_WORKERS=N
# =============================================================================


def pytest_xdist_auto_num_workers(config: Any) -> int | None:
    """
    Dynamically determine optimal number of pytest-xdist workers.

    Implements CPU throttling by:
    1. Checking current system load average
    2. Reducing workers when system is already under load
    3. Always leaving cores for the OS and other processes

    Returns:
        Number of workers to use, or None to fall back to xdist default.
    """
    import os

    # Allow explicit override via environment variable
    if override := os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS"):
        try:
            return int(override)
        except ValueError:
            pass

    try:
        cpu_count = os.cpu_count() or 4

        # Try to get system load (macOS/Linux only)
        try:
            # 1-minute load average
            load_avg = os.getloadavg()[0]

            # If system is already loaded (>80% of cores busy), throttle hard
            if load_avg > cpu_count * 0.8:
                # Use at most half the cores when system is busy
                return max(1, cpu_count // 2)

            # If system is moderately loaded (>50%), be conservative
            if load_avg > cpu_count * 0.5:
                # Leave 2 cores free
                return max(1, cpu_count - 2)

        except (AttributeError, OSError):
            # Windows doesn't have getloadavg(), fall through to default
            pass

        # Default: Use most cores but leave 1-2 for system responsiveness
        # For small machines (<=4 cores): leave 1 core
        # For larger machines (>4 cores): leave 2 cores
        if cpu_count <= 4:
            return max(1, cpu_count - 1)
        else:
            return max(1, cpu_count - 2)

    except Exception:
        # Never break pytest startup due to worker count detection
        return None


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
            # Note: gestalt/, gardener/, park/, coalition/ removed 2025-12-21
            "services/forge/",
            "services/muse/",
            "services/morpheus/",
            "services/witness/",
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
            # Note: gardener/, gestalt/, park/, domain/ removed 2025-12-21
            "agents/infra/",
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


# =============================================================================
# Database Isolation for Multi-Agent Test Execution
# =============================================================================
#
# When multiple Claude agents run tests simultaneously, they can conflict
# on shared database files. The solution follows kgents principles:
#
# - Heterarchical: Resources flow where needed, not allocated top-down
# - Graceful Degradation: Tests work in any environment
# - Composable: Each test session is independent
#
# See models/base.py _get_test_isolation_suffix() for the isolation logic.
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def _reset_database_engine_at_session_start():
    """
    Reset the database engine singleton at session start.

    This ensures each pytest session (including parallel xdist workers and
    multiple Claude agents) gets a fresh, isolated database engine pointing
    to its own isolated database file.

    The isolation happens via:
    1. models/base.py._get_test_isolation_suffix() generates unique DB names
    2. This fixture resets the engine singleton so it picks up the new URL
    3. Each worker/agent gets: membrane_test_gw0_12345.db (xdist) or
       membrane_test_12345.db (single pytest)
    """
    # Reset engine singleton to force re-creation with test-isolated URL
    import models.base as base_module

    # Clear existing engine (if any from previous run or parent process)
    if base_module._engine is not None:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't await in running loop - schedule for later
                pass
            else:
                loop.run_until_complete(base_module._engine.dispose())
        except RuntimeError:
            # No event loop - that's fine, engine will be GC'd
            pass
        finally:
            base_module._engine = None
            base_module._session_factory = None

    yield

    # Cleanup: try to clean up isolated test databases after session
    # (best effort - don't fail tests if cleanup fails)
    try:
        import os
        from pathlib import Path

        # Get the test isolation suffix
        suffix = base_module._get_test_isolation_suffix()
        if suffix:  # Only cleanup if we're in a test
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if xdg_data:
                data_dir = Path(xdg_data) / "kgents"
            else:
                data_dir = Path.home() / ".local" / "share" / "kgents"

            db_path = data_dir / f"membrane{suffix}.db"
            if db_path.exists():
                # Close engine first
                if base_module._engine is not None:
                    import asyncio

                    try:
                        loop = asyncio.get_event_loop()
                        if not loop.is_running():
                            loop.run_until_complete(base_module._engine.dispose())
                    except RuntimeError:
                        pass
                    base_module._engine = None
                    base_module._session_factory = None

                # Remove the isolated test database
                try:
                    db_path.unlink()
                    # Also remove WAL and SHM files if they exist
                    wal_path = db_path.with_suffix(".db-wal")
                    shm_path = db_path.with_suffix(".db-shm")
                    if wal_path.exists():
                        wal_path.unlink()
                    if shm_path.exists():
                        shm_path.unlink()
                except OSError:
                    pass  # Best effort
    except Exception:
        pass  # Never fail tests due to cleanup
