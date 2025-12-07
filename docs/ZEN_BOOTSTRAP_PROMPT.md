# PROMPT: Generate zen-agents with Bootstrap Agents

## Context

You are building `zen-agents`, a contemplative TUI for managing AI assistant sessions. You have access to the 7 bootstrap agents from `impl/claude-openrouter/bootstrap/`:

```python
from bootstrap import (
    Id, compose, ComposedAgent,
    Judge, JudgeInput, make_default_principles,
    Ground, Facts, PersonaSeed, WorldSeed,
    Contradict, ContradictInput, NameCollisionChecker, ConfigConflictChecker,
    Sublate, MergeConfigSublate,
    Fix, fix, FixResult, RetryFix, ConvergeFix,
    Agent, Verdict, Tension, Synthesis, HoldTension
)
```

## Design Goal

A Textual TUI that manages parallel AI sessions (Claude, Codex, Gemini, OpenRouter, Shell) with tmux isolation. Sessions have states: `RUNNING`, `COMPLETED`, `PAUSED`, `FAILED`, `KILLED`.

## Architecture: Bootstrap Agent Mappings

### 1. Session Lifecycle as Compose

Every multi-step operation is a pipeline of agents:

```python
# Create session pipeline
CreateSessionPipeline = (
    ValidateConfig         # Judge: config passes principles
    >> ResolveConfig       # Ground: merge tiers (session > portal > defaults)
    >> DetectConflicts     # Contradict: name collision, resource conflict
    >> ResolveConflicts    # Sublate: auto-resolve or surface to user
    >> SpawnTmux           # Id: pure creation
    >> DetectInitialState  # Fix: poll until state stabilizes
)

# Revive session pipeline
ReviveSessionPipeline = (
    ValidateSession
    >> SpawnTmux
    >> DetectState
)
```

### 2. State Detection as Fix

Polling is Fix. Replace `while True` loops with fixed-point iteration:

```python
@dataclass
class DetectionState:
    session_state: SessionState
    confidence: float
    exit_code: Optional[int] = None

async def poll_once(state: DetectionState) -> DetectionState:
    """One polling iteration."""
    tmux_running = await check_tmux_pane(session)
    if not tmux_running:
        exit_code = await get_exit_code(session)
        new_state = COMPLETED if exit_code == 0 else FAILED
        return DetectionState(new_state, confidence=1.0, exit_code=exit_code)
    return DetectionState(RUNNING, min(state.confidence + 0.1, 1.0))

# In StateRefresher service
result = await fix(
    transform=poll_once,
    initial=DetectionState(RUNNING, 0.0),
    equality_check=lambda a, b: a.session_state == b.session_state and b.confidence >= 0.8,
    max_iterations=50,
)
```

### 3. Conflict Detection as Contradict

Pre-creation validation surfaces tensions before runtime errors:

```python
@dataclass
class SessionConflict(Tension):
    conflict_type: Literal["NAME_COLLISION", "WORKTREE_CONFLICT", "LIMIT_EXCEEDED"]
    suggested_resolution: str

class SessionContradict(Contradict):
    """Detect conflicts before session creation."""

    async def invoke(self, input: ContradictInput) -> Optional[Tension]:
        config, existing_sessions = input.a, input.b

        # Name collision check
        if any(s.name == config.name for s in existing_sessions):
            return SessionConflict(
                mode=TensionMode.PRAGMATIC,
                thesis=config.name,
                antithesis=[s.name for s in existing_sessions],
                description=f"Session '{config.name}' already exists",
                conflict_type="NAME_COLLISION",
                suggested_resolution="append timestamp"
            )

        # Limit check
        if len(existing_sessions) >= MAX_SESSIONS:
            return SessionConflict(...)

        return None  # No conflict
```

### 4. Config Resolution as Ground + Sublate

Configuration tiers are grounded facts that may conflict:

```python
class ConfigGround(Ground):
    """Load config from all tiers."""

    async def invoke(self, _: None) -> Facts:
        return Facts(
            persona=PersonaSeed(
                name="zen-agents",
                preferences={
                    "poll_interval": 1.0,
                    "grace_period": 5.0,
                    "max_sessions": 10,
                }
            ),
            world=WorldSeed(
                date=datetime.now().isoformat(),
                context={
                    "session_config": load_session_config(),
                    "portal_config": load_portal_config(),
                    "default_config": DEFAULT_CONFIG,
                }
            )
        )

class ConfigSublate(Sublate):
    """Merge config tiers: session > portal > default."""

    async def invoke(self, tension: Tension) -> Synthesis:
        tiers = tension.thesis  # {session: {...}, portal: {...}, default: {...}}
        merged = {**tiers['default'], **tiers['portal'], **tiers['session']}
        return Synthesis(
            resolution_type=ResolutionType.ELEVATE,
            result=merged,
            explanation="Merged with session > portal > default precedence"
        )
```

### 5. Pipeline Steps as Agents

Each step in a pipeline is a typed agent:

```python
class ValidateLimit(Agent[NewSessionConfig, NewSessionConfig]):
    """Judge: Does this creation stay within limits?"""

    @property
    def name(self) -> str:
        return "ValidateLimit"

    async def invoke(self, config: NewSessionConfig) -> NewSessionConfig:
        if len(self.sessions) >= MAX_SESSIONS:
            raise ValidationError("Session limit reached")
        return config

class SpawnTmux(Agent[NewSessionConfig, Session]):
    """Create tmux session and return Session model."""

    async def invoke(self, config: NewSessionConfig) -> Session:
        tmux_name = f"zen-{uuid4().hex[:8]}"
        await run_tmux_command(f"new-session -d -s {tmux_name}")
        return Session(
            id=uuid4(),
            name=config.name,
            tmux_name=tmux_name,
            state=SessionState.RUNNING,
            session_type=config.session_type,
        )

# Compose into pipeline
CreatePipeline = ValidateLimit() >> SpawnTmux() >> DetectInitialState()
```

### 6. The Judge: Quality Gates

Judge evaluates at key decision points:

```python
class SessionJudge(Judge):
    """Evaluate session quality."""

    async def invoke(self, input: JudgeInput) -> Verdict:
        session, principles = input.agent, input.principles

        reasons = []

        # Tasteful: Is the name meaningful?
        if len(session.name) < 2 or session.name.isdigit():
            reasons.append("Name should be descriptive")

        # Composable: Can this session work with others?
        if session.session_type == SessionType.SHELL and session.isolated:
            reasons.append("Isolated shells reduce composability")

        if reasons:
            return Verdict.revise(reasons, ["Consider renaming"])
        return Verdict.accept()
```

## File Structure

```
impl/zen-agents/
├── app.py                    # Textual App entry
├── models/
│   └── session.py            # Session, SessionState, SessionType
├── agents/                   # Bootstrap-derived agents
│   ├── pipelines/
│   │   ├── create.py         # CreateSessionPipeline
│   │   ├── revive.py         # ReviveSessionPipeline
│   │   └── clean.py          # CleanSessionPipeline
│   ├── detection.py          # Fix-based state detection
│   ├── conflict.py           # Contradict-based validation
│   ├── config.py             # Ground + Sublate for config
│   └── judge.py              # Session quality checks
├── services/
│   ├── session_manager.py    # Orchestrates pipelines
│   ├── tmux.py               # Tmux operations (pure functions)
│   └── state_refresher.py    # Fix-based polling service
├── widgets/
│   └── session_list.py       # Textual widgets
└── screens/
    └── main.py               # MainScreen
```

## Key Patterns

1. **No while-True loops** — All iteration is Fix
2. **No silent failures** — All conflicts are Contradict + Sublate
3. **No monolithic functions** — All multi-step operations are Compose
4. **Config is Ground** — Facts grounded from tiers, tensions sublated
5. **Quality gates are Judge** — Validation returns Verdict, not bool

## Example: Full Create Flow

```python
async def create_session(manager: SessionManager, config: NewSessionConfig) -> Session:
    # 1. Ground: Load facts
    facts = await ConfigGround().invoke(None)

    # 2. Judge: Validate config
    verdict = await SessionJudge().invoke(JudgeInput(config, make_default_principles()))
    if verdict.type == VerdictType.REJECT:
        raise ValidationError(verdict.reasons)

    # 3. Contradict: Check for conflicts
    conflict = await SessionContradict().invoke(ContradictInput(config, manager.sessions))
    if conflict:
        # 4. Sublate: Resolve or hold
        resolution = await ConflictSublate().invoke(conflict)
        if isinstance(resolution, HoldTension):
            raise ConflictError(resolution.reason)
        config = resolution.result  # Resolved config

    # 5. Compose: Execute pipeline
    pipeline = ValidateLimit() >> ResolveConfig() >> SpawnTmux()
    session = await pipeline.invoke(config)

    # 6. Fix: Poll until stable
    result = await fix(
        transform=lambda s: detect_state(s, manager.tmux),
        initial=session,
        equality_check=lambda a, b: a.state == b.state,
    )

    return result.value
```

## Constraints

- MAX_SESSIONS = 10
- Poll interval: 1s (via Fix, not sleep loops)
- tmux scrollback: 50,000 lines
- Session types: CLAUDE, CODEX, GEMINI, SHELL, OPENROUTER

## Generate

Implement zen-agents following these patterns. Every iteration is Fix. Every conflict is Contradict. Every pipeline is Compose. Every validation is Judge. Every fact is Ground.
