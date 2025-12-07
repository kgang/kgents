#!/usr/bin/env python3
"""
zen-agents Demonstration
========================

A comprehensive tour of the kgents architecture through zen-agents.

This demo showcases:
    - The Agent abstraction (morphisms with name, genus, purpose)
    - Ground as empirical seed (the world model)
    - Judge as validation against principles
    - Composition patterns (pipelines as agents)
    - Conflict detection and resolution (Contradict/Sublate)
    - Fix-based state detection (polling as fixed-point search)
    - Session lifecycle (create, pause, kill, revive)
    - Discovery and reconciliation

Run: uv run python demo.py
     uv run python demo.py --section ground    # Run specific section
     uv run python demo.py --list              # List all sections
"""

import asyncio
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Callable, Awaitable

from zen_agents.types import (
    SessionConfig, SessionType, SessionState, Session, TmuxSession,
    ZenGroundState, ConfigLayer, SessionVerdict,
)
from zen_agents.ground import ZenGround, zen_ground
from zen_agents.judge import ZenJudge, zen_judge
from zen_agents.session.create import SessionCreate, create_session
from zen_agents.session.detect import detect_state, DetectionResult
from zen_agents.session.lifecycle import (
    SessionPause, SessionKill, SessionRevive,
    pause_session, kill_session, revive_session,
)
from zen_agents.conflicts import (
    SessionContradict, SessionSublate, SessionConflictPipeline,
    SessionContradictInput, SessionSublateInput,
    session_contradict, session_sublate, conflict_pipeline,
    ConflictType,
)
from zen_agents.discovery import (
    TmuxDiscovery, SessionReconcile, ClaudeSessionDiscovery,
    tmux_discovery, session_reconcile, claude_session_discovery,
    DiscoveryInput, ReconcileInput,
)
from zen_agents.commands import (
    CommandBuild, CommandValidate,
    command_build, command_validate,
    generate_banner,
)
from zen_agents.persistence import StateSave, StateLoad, state_save, state_load
from pipelines.new_session import NewSessionPipeline, create_session_pipeline
from pipelines.session_tick import SessionTickPipeline, session_tick, TickResult


# =============================================================================
# DISPLAY UTILITIES
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def header(title: str, char: str = "=") -> None:
    """Print a section header."""
    width = 70
    print(f"\n{Colors.CYAN}{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}{Colors.RESET}\n")


def subheader(title: str) -> None:
    """Print a subsection header."""
    print(f"\n{Colors.YELLOW}--- {title} ---{Colors.RESET}\n")


def agent_info(agent) -> None:
    """Display agent metadata."""
    print(f"  {Colors.BOLD}Agent:{Colors.RESET} {agent.name}")
    print(f"  {Colors.DIM}Genus:{Colors.RESET} {agent.genus}")
    print(f"  {Colors.DIM}Purpose:{Colors.RESET} {agent.purpose}")


def success(msg: str) -> None:
    """Print a success message."""
    print(f"  {Colors.GREEN}[OK]{Colors.RESET} {msg}")


def info(msg: str) -> None:
    """Print an info message."""
    print(f"  {Colors.BLUE}[*]{Colors.RESET} {msg}")


def warn(msg: str) -> None:
    """Print a warning message."""
    print(f"  {Colors.YELLOW}[!]{Colors.RESET} {msg}")


def error(msg: str) -> None:
    """Print an error message."""
    print(f"  {Colors.RED}[X]{Colors.RESET} {msg}")


def kv(key: str, value, indent: int = 4) -> None:
    """Print a key-value pair."""
    spaces = " " * indent
    print(f"{spaces}{Colors.DIM}{key}:{Colors.RESET} {value}")


# =============================================================================
# DEMO SECTIONS
# =============================================================================

async def demo_intro() -> None:
    """Introduction to zen-agents."""
    header("ZEN-AGENTS: Zenportal Reimagined Through kgents")

    print("""
    zen-agents demonstrates that the kgents agent framework can serve
    as a foundation for real applications. It reimagines zenportal's
    session management through composable agent primitives.

    Core insight: SERVICES ARE AGENTS; COMPOSITION IS PRIMARY

    | Zenportal                  | zen-agents                          |
    |----------------------------|-------------------------------------|
    | SessionManager.create()    | NewSessionPipeline                  |
    | ConfigManager (3-tier)     | ZenGround (config cascade)          |
    | StateRefresher.refresh()   | SessionTickPipeline (Fix-based)     |
    | TmuxService.*              | zen_agents/tmux/* agents            |
    | DiscoveryService           | TmuxDiscovery, SessionReconcile     |

    The following sections demonstrate each architectural component.
    """)


async def demo_ground() -> None:
    """Demonstrate ZenGround - the empirical seed."""
    header("1. GROUND: The Empirical Seed")

    print("""
    Ground produces the irreducible facts about the world.
    For zen-agents, this includes:
        - Configuration hierarchy (global > portal > session)
        - Known session states
        - Raw tmux facts
        - User preferences

    Type signature: Ground: Void -> ZenGroundState
    """)

    subheader("Creating Ground")
    ground = ZenGround(discover_tmux=False)  # Don't call tmux in demo
    agent_info(ground)

    subheader("Invoking Ground")
    state = await ground.invoke(None)

    print("\n  Ground state produced:")
    kv("Config layers", len(state.config_cascade))
    kv("Known sessions", len(state.sessions))
    kv("tmux sessions", len(state.tmux_sessions))
    kv("Default session type", state.default_session_type.value)
    kv("Max sessions", state.max_sessions)
    kv("Auto discovery", state.auto_discovery)
    kv("Last updated", state.last_updated.strftime("%H:%M:%S"))

    subheader("Config Cascade")
    for layer in state.config_cascade:
        print(f"\n    Layer: {Colors.BOLD}{layer.name}{Colors.RESET}")
        for k, v in layer.values.items():
            kv(k, v, indent=6)

    subheader("Ground Query")
    info("ground.query('config.default_shell') allows dotted path queries")

    # The query method isn't shown working because we'd need to access the cache
    print("""
    Ground is the "world model" from which all agents operate.
    It's the empirical foundation - facts, not opinions.
    """)


async def demo_judge() -> None:
    """Demonstrate ZenJudge - validation against principles."""
    header("2. JUDGE: Validation Against Principles")

    print("""
    Judge evaluates inputs against the 6 kgents principles:
        1. Tasteful - Clear, justified purpose
        2. Curated - Unique value
        3. Ethical - Respects human agency
        4. Joy-Inducing - Delightful interaction
        5. Composable - Works with other agents
        6. Heterarchical - Can lead and follow

    For sessions, Judge validates:
        - Name format (alphanumeric, dash, underscore only)
        - Session type validity
        - Working directory existence
        - Resource limits

    Type signature: Judge: SessionConfig -> SessionVerdict
    """)

    # Get ground state for context
    ground = ZenGround(discover_tmux=False)
    ground_state = await ground.invoke(None)
    judge = zen_judge.with_ground(ground_state)

    subheader("Agent Metadata")
    agent_info(judge)

    subheader("Validating a Good Config")
    good_config = SessionConfig(
        name="my-claude-session",
        session_type=SessionType.CLAUDE,
        working_dir=str(Path.cwd()),
        model="claude-sonnet-4-20250514",
        tags=["demo", "test"],
    )
    verdict = await judge.invoke(good_config)

    kv("Name", good_config.name)
    kv("Type", good_config.session_type.value)
    kv("Valid", verdict.valid)
    if verdict.valid:
        success("Config passes all validation rules")

    subheader("Validating Bad Configs")

    # Bad name
    bad_name = SessionConfig(
        name="bad name with spaces!",
        session_type=SessionType.CLAUDE,
    )
    verdict = await judge.invoke(bad_name)
    kv("Name", bad_name.name)
    kv("Valid", verdict.valid)
    for issue in verdict.issues:
        error(issue)

    # Reserved name
    reserved = SessionConfig(
        name="__internal__",
        session_type=SessionType.SHELL,
    )
    verdict = await judge.invoke(reserved)
    kv("Name", reserved.name)
    kv("Valid", verdict.valid)
    for issue in verdict.issues:
        error(issue)

    # Nonexistent working directory
    bad_dir = SessionConfig(
        name="valid-name",
        session_type=SessionType.CLAUDE,
        working_dir="/nonexistent/path/that/does/not/exist",
    )
    verdict = await judge.invoke(bad_dir)
    kv("Working dir", bad_dir.working_dir)
    kv("Valid", verdict.valid)
    for issue in verdict.issues:
        error(issue)

    print("""
    Judge embodies the "principle of principles" - every input
    is validated against the kgents design philosophy.
    """)


async def demo_session_create() -> None:
    """Demonstrate SessionCreate - pure transformation."""
    header("3. SESSION CREATE: Pure Transformation")

    print("""
    SessionCreate is a pure transformation:
        SessionConfig -> Session

    It doesn't spawn tmux or interact with the world.
    It simply transforms intent (config) into structure (session).

    This separation allows:
        - Testing without side effects
        - Composition with other agents
        - Clear responsibility boundaries
    """)

    subheader("Agent Metadata")
    agent_info(create_session)

    subheader("Creating Sessions")

    configs = [
        SessionConfig(
            name="demo-claude",
            session_type=SessionType.CLAUDE,
            working_dir=str(Path.cwd()),
            model="claude-sonnet-4-20250514",
            tags=["ai", "coding"],
        ),
        SessionConfig(
            name="demo-shell",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
            tags=["utility"],
        ),
        SessionConfig(
            name="custom-workflow",
            session_type=SessionType.CUSTOM,
            command="htop",
            tags=["monitoring"],
        ),
    ]

    for config in configs:
        session = await create_session.invoke(config)
        print(f"\n  {Colors.BOLD}{session.config.name}{Colors.RESET}")
        kv("ID", session.id)
        kv("State", session.state.value)
        kv("Type", session.config.session_type.value)
        kv("Working dir", session.config.working_dir or "(none)")
        kv("tmux attached", session.tmux is not None)

    print("""
    Note: All sessions start in CREATING state with no tmux.
    Spawning happens in a separate agent (TmuxSpawn).
    """)


async def demo_conflicts() -> None:
    """Demonstrate Contradict/Sublate for conflict resolution."""
    header("4. CONFLICTS: Contradict and Sublate")

    print("""
    Contradict detects tensions (conflicts) between inputs.
    Sublate resolves them through synthesis.

    This is the dialectical pattern from kgents:
        Thesis + Antithesis -> Synthesis (via Sublate)

    For sessions:
        - Name collisions -> Auto-rename
        - Resource limits -> Reject or suggest cleanup
        - Worktree conflicts -> Manual resolution needed
    """)

    # Set up ground with existing sessions
    ground = ZenGround(discover_tmux=False)
    ground_state = await ground.invoke(None)

    # Add an existing session
    existing_session = Session(
        id="existing-123",
        config=SessionConfig(name="my-session", session_type=SessionType.CLAUDE),
        state=SessionState.RUNNING,
        started_at=datetime.now(),
    )
    ground_state.sessions["existing-123"] = existing_session

    subheader("Contradict: Detecting Conflicts")
    agent_info(session_contradict)

    # Try to create session with same name
    conflicting_config = SessionConfig(
        name="my-session",  # Same as existing!
        session_type=SessionType.CLAUDE,
    )

    conflicts = await session_contradict.invoke(SessionContradictInput(
        config=conflicting_config,
        ground_state=ground_state,
    ))

    print(f"\n  Checking config: name='{conflicting_config.name}'")
    kv("Conflicts found", len(conflicts))

    for conflict in conflicts:
        warn(f"{conflict.conflict_type}: {conflict.description}")
        if conflict.suggested_resolution:
            info(f"Suggestion: {conflict.suggested_resolution}")

    subheader("Sublate: Resolving Conflicts")
    agent_info(session_sublate)

    for conflict in conflicts:
        resolution = await session_sublate.invoke(SessionSublateInput(
            conflict=conflict,
            auto_resolve=True,
        ))

        kv("Resolved", resolution.resolved)
        kv("Resolution type", resolution.resolution_type)
        kv("Message", resolution.message)

        if resolution.result:
            success(f"New name: {resolution.result.name}")

    subheader("Resource Limit Conflict")

    # Fill up sessions to hit limit
    for i in range(10):
        fake_session = Session(
            id=f"session-{i}",
            config=SessionConfig(name=f"session-{i}", session_type=SessionType.SHELL),
            state=SessionState.RUNNING,
        )
        ground_state.sessions[f"session-{i}"] = fake_session

    new_config = SessionConfig(name="one-more", session_type=SessionType.CLAUDE)
    conflicts = await session_contradict.invoke(SessionContradictInput(
        config=new_config,
        ground_state=ground_state,
    ))

    for conflict in conflicts:
        if conflict.conflict_type == ConflictType.RESOURCE_LIMIT:
            error(f"{conflict.description}")
            warn(f"Resolvable: {conflict.resolvable}")
            info(f"Suggestion: {conflict.suggested_resolution}")

    print("""
    Contradict/Sublate embodies Hegelian dialectic:
    oppositions are detected and resolved through synthesis.
    """)


async def demo_pipeline() -> None:
    """Demonstrate NewSessionPipeline - composition in action."""
    header("5. PIPELINE: Composition as Agent")

    print("""
    A Pipeline is itself an Agent - composition produces agents.

    NewSessionPipeline composes:
        Judge -> Create -> Spawn -> Detect

    Type signature: SessionConfig -> PipelineResult

    This is equivalent to zenportal's SessionManager.create_session()
    but with explicit, transparent composition.
    """)

    subheader("Pipeline Structure")
    pipeline = create_session_pipeline(tmux_prefix="demo")
    agent_info(pipeline)

    print("""
    The pipeline composes four agents:

    1. Judge(config)
       Validate against principles
       Returns: SessionVerdict

    2. Create(config)
       Transform to session object
       Returns: Session (state=CREATING)

    3. Spawn(session)
       Create tmux session
       Returns: TmuxSession | SpawnError

    4. Detect(session)
       Fix-based state detection
       Returns: DetectionResult
    """)

    subheader("Conceptual Flow")
    print("""
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   Judge     │ --> │   Create    │ --> │   Spawn     │ --> │   Detect    │
    │ (validate)  │     │ (transform) │     │ (tmux)      │     │ (fix-based) │
    └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
          │                   │                   │                   │
          v                   v                   v                   v
    SessionVerdict       Session           TmuxSession         DetectionResult
    """)

    subheader("Key Properties")
    print("""
    - Transparent: Every step is visible and testable
    - Composable: Add more agents (conflict check, persistence)
    - Fail-fast: Errors at any stage stop the pipeline
    - Auditable: Intermediate results preserved in PipelineResult
    """)

    info("(Skipping actual execution to avoid creating tmux sessions)")

    print("""
    The pipeline IS an agent. Agents compose to make agents.
    This is the C-gents principle: "Agents are morphisms."
    """)


async def demo_fix() -> None:
    """Demonstrate Fix-based state detection."""
    header("6. FIX: Polling as Fixed-Point Search")

    print("""
    The key insight: polling IS fixed-point search.

    Traditional approach:
        while True:
            state = check_state()
            if state.stable: break
            sleep(0.5)

    kgents approach:
        fix(transform, initial, equality_check)

    Both iterate until stable. Fix makes this explicit.
    """)

    subheader("State Detection Agent")
    agent_info(detect_state)

    subheader("Simulated Session Output")

    # Create a session with simulated output
    session = Session(
        id="fix-demo-123",
        config=SessionConfig(name="fix-demo", session_type=SessionType.SHELL),
        state=SessionState.RUNNING,
        started_at=datetime.now(),
        output_lines=[
            "$ echo 'Starting task...'",
            "Starting task...",
            "Processing item 1 of 10...",
            "Processing item 2 of 10...",
            "Processing item 3 of 10...",
            "Task complete!",
            "$ ",  # Shell prompt indicates completion
        ]
    )

    print("  Output lines:")
    for line in session.output_lines[-5:]:
        print(f"    {Colors.DIM}{line}{Colors.RESET}")

    result = await detect_state.invoke(session)

    subheader("Detection Result")
    kv("State", result.state.value)
    kv("Confidence", f"{result.confidence:.2f}")
    kv("Iterations", result.iterations)
    kv("Indicators", result.indicators)

    subheader("Different Output Patterns")

    patterns = [
        (
            "Active processing",
            ["Running...", "Working on task...", "45% complete..."],
            SessionState.RUNNING,
        ),
        (
            "Error output",
            ["Error: Connection refused", "Traceback (most recent call last):", "SystemExit: 1"],
            SessionState.FAILED,
        ),
        (
            "Clean completion",
            ["Done!", "Exiting...", "$ "],
            SessionState.COMPLETED,
        ),
    ]

    for name, lines, expected_state in patterns:
        test_session = replace(session, output_lines=lines)
        result = await detect_state.invoke(test_session)
        status = Colors.GREEN if result.state == expected_state else Colors.RED
        print(f"\n  {Colors.BOLD}{name}{Colors.RESET}")
        kv("Sample output", lines[-1][:40])
        print(f"    {Colors.DIM}Detected:{Colors.RESET} {status}{result.state.value}{Colors.RESET}")

    print("""
    Fix-based detection is more principled than ad-hoc polling:
        - Explicit convergence criterion
        - Bounded iteration with max_iterations
        - Confidence scoring for ambiguous states
    """)


async def demo_lifecycle() -> None:
    """Demonstrate session lifecycle agents."""
    header("7. LIFECYCLE: Create, Pause, Kill, Revive")

    print("""
    Session lifecycle is a state machine managed by agents:

    CREATING -> RUNNING -> PAUSED -> RUNNING (revive)
                  |          |
                  v          v
               COMPLETED  COMPLETED
                  |
                  v
               FAILED

    Each transition is an agent:
        - SessionPause: RUNNING -> PAUSED
        - SessionKill: Any -> COMPLETED
        - SessionRevive: PAUSED/COMPLETED/FAILED -> RUNNING
    """)

    # Create a running session
    session = Session(
        id="lifecycle-demo",
        config=SessionConfig(
            name="lifecycle-demo",
            session_type=SessionType.SHELL,
            command="zsh -l",
        ),
        state=SessionState.RUNNING,
        tmux=TmuxSession(
            id="@42",
            name="lifecycle-demo",
            pane_id="%0",
            created_at=datetime.now(),
        ),
        started_at=datetime.now(),
    )

    subheader("Initial State")
    kv("Session", session.config.name)
    kv("State", session.state.value)
    kv("Has tmux", session.tmux is not None)

    subheader("SessionPause")
    agent_info(pause_session)
    info("Transition: RUNNING -> PAUSED (kills tmux but preserves state)")

    # Note: We can't actually pause without tmux, but show the concept
    print("""
    In real execution:
        1. Clear tmux history (for security)
        2. Kill tmux session
        3. Set state to PAUSED
        4. Record pause time
    """)

    subheader("SessionKill")
    agent_info(kill_session)
    info("Transition: Any alive state -> COMPLETED")

    print("""
    Kill is terminal. Use for:
        - User-requested termination
        - Error recovery
        - Resource cleanup
    """)

    subheader("SessionRevive")
    agent_info(revive_session)
    info("Transition: PAUSED/COMPLETED/FAILED -> RUNNING")

    print("""
    Revive respawns the tmux session:
        1. Clean up any old tmux session
        2. Spawn new tmux with same command
        3. Set state to RUNNING
        4. Clear completed_at, set started_at

    This is powerful - even FAILED sessions can be revived!
    """)

    subheader("State Machine Diagram")
    print("""
                 create
                   |
                   v
    ┌──────────────────────────┐
    │        CREATING          │
    └──────────────────────────┘
                   |
                   | spawn success
                   v
    ┌──────────────────────────┐    pause     ┌────────────────┐
    │         RUNNING          │ -----------> │     PAUSED     │
    └──────────────────────────┘              └────────────────┘
         |              |                            |
         | complete     | fail                       | revive
         v              v                            |
    ┌─────────┐   ┌─────────┐                       |
    │COMPLETED│   │ FAILED  │ <--------------------+
    └─────────┘   └─────────┘
         ^              ^
         |              |
         +----- kill ---+
    """)


async def demo_discovery() -> None:
    """Demonstrate discovery and reconciliation."""
    header("8. DISCOVERY: Finding and Reconciling Sessions")

    print("""
    Discovery agents find existing sessions:
        - TmuxDiscovery: Find running tmux sessions with zen prefix
        - ClaudeSessionDiscovery: Find Claude Code session files
        - SessionReconcile: Match known sessions against discovered tmux
    """)

    subheader("TmuxDiscovery")
    agent_info(tmux_discovery)

    print("""
    Discovers tmux sessions matching pattern (e.g., "zen-*").
    Used on startup to find sessions from previous runs.
    """)

    # Demo with fake sessions for illustration
    discovered = await tmux_discovery.invoke(DiscoveryInput(prefix="zen-"))
    kv("Sessions found", len(discovered))

    subheader("SessionReconcile")
    agent_info(session_reconcile)

    print("""
    Reconciles known sessions with tmux reality:
        - matched: Session has corresponding tmux
        - orphaned: tmux exists but no session record
        - missing: Session record but tmux died
    """)

    # Create example for reconciliation
    known_sessions = {
        "sess-1": Session(
            id="sess-1",
            config=SessionConfig(name="zen-project", session_type=SessionType.CLAUDE),
            state=SessionState.RUNNING,
            tmux=TmuxSession(id="@1", name="zen-project", pane_id="%0", created_at=datetime.now()),
        ),
        "sess-2": Session(
            id="sess-2",
            config=SessionConfig(name="zen-shell", session_type=SessionType.SHELL),
            state=SessionState.RUNNING,
            tmux=TmuxSession(id="@2", name="zen-shell", pane_id="%1", created_at=datetime.now()),
        ),
    }

    # Simulate tmux reality (one matched, one orphaned)
    tmux_sessions = [
        TmuxSession(id="@1", name="zen-project", pane_id="%0", created_at=datetime.now()),
        TmuxSession(id="@99", name="zen-orphan", pane_id="%99", created_at=datetime.now()),
    ]

    result = await session_reconcile.invoke(ReconcileInput(
        known_sessions=known_sessions,
        tmux_sessions=tmux_sessions,
    ))

    print(f"\n  Reconciliation result:")
    kv("Matched", len(result.matched))
    kv("Orphaned", len(result.orphaned))
    kv("Missing", len(result.missing))

    for session, tmux in result.matched:
        success(f"Matched: {session.config.name} <-> {tmux.name}")

    for tmux in result.orphaned:
        warn(f"Orphaned tmux: {tmux.name} (no session record)")

    for session in result.missing:
        error(f"Missing tmux: {session.config.name} (session says running)")

    subheader("ClaudeSessionDiscovery")
    agent_info(claude_session_discovery)

    print("""
    Finds Claude Code sessions from ~/.claude/projects/.
    Used for "resume session" functionality.
    """)

    # List Claude sessions for current directory
    sessions = await claude_session_discovery.invoke(Path.cwd())
    kv("Claude sessions found", len(sessions))

    if sessions:
        for sess in sessions[:3]:
            print(f"\n    Session: {sess.session_id[:8]}...")
            kv("Project", sess.project_path, indent=6)
            kv("Modified", sess.modified_at.strftime("%Y-%m-%d %H:%M"), indent=6)


async def demo_commands() -> None:
    """Demonstrate command building."""
    header("9. COMMANDS: Building Session Commands")

    print("""
    CommandBuild transforms SessionConfig into shell commands.
    CommandValidate ensures required binaries exist.

    Features:
        - Session-type-specific command generation
        - OpenRouter proxy configuration
        - Procedural banner generation for visual identity
    """)

    subheader("CommandValidate")
    agent_info(command_validate)

    print("\n  Checking binaries for each session type:")
    for stype in SessionType:
        result = await command_validate.invoke(stype)
        status = Colors.GREEN + "[OK]" if result.valid else Colors.RED + "[X]"
        print(f"    {status}{Colors.RESET} {stype.value}")
        if result.error:
            print(f"       {Colors.DIM}{result.error}{Colors.RESET}")

    subheader("CommandBuild")
    agent_info(command_build)

    configs = [
        SessionConfig(
            name="claude-project",
            session_type=SessionType.CLAUDE,
            model="claude-sonnet-4-20250514",
        ),
        SessionConfig(
            name="shell-session",
            session_type=SessionType.SHELL,
        ),
        SessionConfig(
            name="custom-htop",
            session_type=SessionType.CUSTOM,
            command="htop -d 10",
        ),
    ]

    for config in configs:
        result = await command_build.invoke(config)
        print(f"\n  {Colors.BOLD}{config.name}{Colors.RESET}")
        kv("Type", config.session_type.value)
        kv("Command", " ".join(result.command))
        if result.env:
            kv("Env vars", len(result.env))

    subheader("Procedural Banners")

    print("""
    Each session gets a unique visual banner based on its ID.
    Same ID = same banner (deterministic).
    """)

    banner = generate_banner("demo-session", "abc123")
    print(banner)


async def demo_persistence() -> None:
    """Demonstrate state persistence."""
    header("10. PERSISTENCE: Saving and Loading State")

    print("""
    StateSave and StateLoad persist ground state to disk.
    Default location: ~/.zen-agents/state.json

    This enables:
        - Session survival across restarts
        - State recovery after crashes
        - Multi-instance coordination (future)
    """)

    subheader("StateSave")
    agent_info(state_save)

    subheader("StateLoad")
    agent_info(state_load)

    print("""
    Usage:
        # Save current state
        await state_save.invoke(ground_state)

        # Load state on startup
        loaded = await state_load.invoke(None)

    File format: JSON with session configs, states, and timestamps.
    Sessions are restored but tmux connections must be re-established
    via discovery and reconciliation.
    """)


async def demo_bootstrap_mapping() -> None:
    """Show the mapping to bootstrap agents."""
    header("11. BOOTSTRAP: The 7 Irreducible Agents")

    print("""
    kgents defines 7 bootstrap agents - the irreducible kernel
    from which all other agents can be derived.

    All 7 are used in zen-agents:
    """)

    mappings = [
        ("Id", "Pass-through transforms", "Session -> Session (unchanged)"),
        ("Compose", "Pipeline construction", "Judge -> Create -> Spawn -> Detect"),
        ("Judge", "Principle validation", "ZenJudge validates against 6 principles"),
        ("Ground", "Empirical seed", "ZenGround: config + state + tmux facts"),
        ("Contradict", "Conflict detection", "SessionContradict finds name collisions"),
        ("Sublate", "Conflict resolution", "SessionSublate auto-renames duplicates"),
        ("Fix", "Fixed-point iteration", "State detection polls until stable"),
    ]

    print(f"\n  {'Bootstrap':<12} {'Role':<24} {'Implementation'}")
    print(f"  {'-'*12} {'-'*24} {'-'*40}")
    for agent, role, impl in mappings:
        print(f"  {Colors.CYAN}{agent:<12}{Colors.RESET} {role:<24} {Colors.DIM}{impl}{Colors.RESET}")

    subheader("Minimal Bootstrap")

    print("""
    The minimal kernel is {Compose, Judge, Ground}:
        - Compose: Structure (how to combine)
        - Judge: Direction (what to accept)
        - Ground: Material (what exists)

    From these three, you can derive the others:
        - Id = Compose with identity
        - Fix = Compose with iteration
        - Contradict/Sublate = Judge specializations
    """)

    subheader("Why These 7?")

    print("""
    After maximal algorithmic compression, these remain:
        - Recursion has done all it can (Fix handles iteration)
        - Composition has done all it can (Compose is primitive)
        - Dialectic has done all it can (Contradict/Sublate handle tension)

    They are the "residue" - what cannot be reduced further.
    """)


async def demo_summary() -> None:
    """Final summary."""
    header("SUMMARY: What zen-agents Demonstrates")

    print(f"""
    {Colors.BOLD}Key Architectural Insights:{Colors.RESET}

    1. {Colors.CYAN}SERVICES ARE AGENTS{Colors.RESET}
       SessionManager -> NewSessionPipeline
       Each service method is a composable morphism.

    2. {Colors.CYAN}CONFIG IS GROUND{Colors.RESET}
       3-tier cascade (global > portal > session) = ZenGround
       The empirical seed from which all else derives.

    3. {Colors.CYAN}POLLING IS FIX{Colors.RESET}
       State detection via iteration until stable.
       The Y combinator made safe and bounded.

    4. {Colors.CYAN}COMPOSITION IS PRIMARY{Colors.RESET}
       Judge -> Create -> Spawn -> Detect
       Complex behavior emerges from simple agent composition.

    5. {Colors.CYAN}CONFLICTS ARE DIALECTIC{Colors.RESET}
       Contradict detects tension; Sublate resolves it.
       Thesis + Antithesis -> Synthesis.

    6. {Colors.CYAN}ALL 7 BOOTSTRAP AGENTS IN USE{Colors.RESET}
       The irreducible kernel is sufficient for real applications.

    {Colors.BOLD}This proves:{Colors.RESET}
    kgents is a viable foundation for production applications.
    The agent abstraction scales from theory to practice.

    {Colors.DIM}Next: Run 'uv run pytest tests/ -v' to see the test suite.{Colors.RESET}
    """)


# =============================================================================
# DEMO RUNNER
# =============================================================================

SECTIONS: dict[str, tuple[str, Callable[[], Awaitable[None]]]] = {
    "intro": ("Introduction", demo_intro),
    "ground": ("Ground: Empirical Seed", demo_ground),
    "judge": ("Judge: Validation", demo_judge),
    "create": ("Session Create", demo_session_create),
    "conflicts": ("Conflicts: Contradict/Sublate", demo_conflicts),
    "pipeline": ("Pipeline: Composition", demo_pipeline),
    "fix": ("Fix: State Detection", demo_fix),
    "lifecycle": ("Lifecycle: Pause/Kill/Revive", demo_lifecycle),
    "discovery": ("Discovery: Finding Sessions", demo_discovery),
    "commands": ("Commands: Building Shell Commands", demo_commands),
    "persistence": ("Persistence: Save/Load State", demo_persistence),
    "bootstrap": ("Bootstrap: The 7 Agents", demo_bootstrap_mapping),
    "summary": ("Summary", demo_summary),
}


async def run_all() -> None:
    """Run all demo sections in order."""
    for name, (_, func) in SECTIONS.items():
        await func()


async def run_section(name: str) -> None:
    """Run a specific demo section."""
    if name not in SECTIONS:
        print(f"Unknown section: {name}")
        print(f"Available: {', '.join(SECTIONS.keys())}")
        return
    _, func = SECTIONS[name]
    await func()


def list_sections() -> None:
    """List all available sections."""
    print("\nAvailable demo sections:\n")
    for name, (desc, _) in SECTIONS.items():
        print(f"  {Colors.CYAN}{name:<12}{Colors.RESET} {desc}")
    print(f"\nRun specific section: uv run python demo.py --section <name>")
    print(f"Run all: uv run python demo.py")


async def main() -> None:
    """Main entry point."""
    args = sys.argv[1:]

    if "--list" in args or "-l" in args:
        list_sections()
        return

    if "--section" in args or "-s" in args:
        try:
            idx = args.index("--section") if "--section" in args else args.index("-s")
            section = args[idx + 1]
            await run_section(section)
        except (IndexError, ValueError):
            print("Usage: demo.py --section <name>")
            list_sections()
        return

    if "--help" in args or "-h" in args:
        print(__doc__)
        list_sections()
        return

    # Run all sections
    await run_all()


if __name__ == "__main__":
    asyncio.run(main())
