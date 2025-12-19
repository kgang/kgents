# kgentsd: The 8th Crown Jewel

> *"The ghost is not a haunting—it's a witnessing that becomes a doing."*

**Status**: EXECUTING (Phase 0.5)
**Created**: 2025-12-19
**Updated**: 2025-12-19 (vertical slice refinement)
**Author**: Kent + Claude (collaborative architecture)
**Priority**: TRANSFORMATIVE
**Aligned With**: AD-009 (Metaphysical Fullstack), AD-006 (Unified Categorical Foundation)

---

## Creative Direction

🎯 **Grounding in Intent**:

*"Daring, bold, creative, opinionated but not gaudy"*
*"Tasteful > feature-complete; Joy-inducing > merely functional"*
*"Depth over breadth"*

### What Makes kgentsd Different

This isn't another monitoring daemon. It's a **Witness** that becomes an **Agent**.

| Principle | Application |
|-----------|-------------|
| **Daring** | Trust escalation from observer → actor is philosophically bold |
| **Opinionated** | We believe developer tools should learn and anticipate |
| **Joy-inducing** | Thought stream reads like a diary, not a log file |
| **Not gaudy** | Minimal surface area; five event sources, not fifty |

### The Mirror Test

Does kgentsd feel like Kent on his best day? A good developer doesn't just react—they:
- Notice patterns before they become problems
- Build trust through consistent, valuable observations
- Earn the right to act autonomously through track record
- Know when NOT to intervene

---

## Vision

**kgentsd** (pronounced "kay-gents-dee") is the Witness Agent that watches, learns, and acts. It graduates from "invisible infrastructure" to the **8th Crown Jewel**—the only jewel that can invoke all others.

| Before (Ghost) | After (kgentsd) |
|----------------|-----------------|
| Timer-driven polling (3 min) | Event-driven reactive streams |
| File projection only | Multi-surface projection (CLI/Web/SSE/Files) |
| Read-only observation | Full autonomous capability (Trust Level 3) |
| Separate from AGENTESE | Native AGENTESE citizen |
| Infrastructure utility | **Crown Jewel** with its own frontend |
| 7 collectors, separate code | Unified WatcherPolynomial per source |

### The kgentsd Thesis

**kgentsd is Kent's developer agency, crystallized into code.**

At Trust Level 3, kgentsd can do everything Kent does:
- Run tests and fix failing code
- Commit changes with meaningful messages
- Refactor based on detected patterns
- Create PRs and respond to reviews
- Invoke any Crown Jewel on Kent's behalf
- Write documentation when gaps detected
- Suggest architectural improvements

The Witness is not a replacement—it's an amplification.

---

## The Eight Jewel Crown

| # | Jewel | Vision | Status |
|---|-------|--------|--------|
| 1 | Brain | Spatial cathedral of memory | 100% |
| 2 | Gardener | Cultivation practice for ideas | 100% |
| 3 | Gestalt | Living garden where code breathes | 100% |
| 4 | Forge | Developer's workshop for metaphysical fullstack agents | 85% |
| 5 | Coalition | Workshop where agents collaborate visibly | 55% |
| 6 | Park | Westworld where hosts can say no | 40% |
| 7 | Domain | Enterprise categorical foundation | 0% |
| **8** | **kgentsd** | **System daemon that watches, learns, acts** | **0%** |

**kgentsd is unique**: It's the only jewel that can invoke all other jewels. It observes the entire system and acts on Kent's behalf across all domains.

---

## Architectural Foundation

### Event-Driven Core (No Timers)

**The old way** (timer-driven):
```python
# BAD: Timer-driven zombie loop
while running:
    await asyncio.sleep(180)  # Arbitrary 3-minute interval
    await project_once()       # What if nothing changed?
```

**The new way** (event-driven):
```python
# GOOD: React to events via Flux
class Kgentsd(FluxAgent[DaemonState, SystemEvent, DaemonAction]):
    """
    Event-driven daemon using Flux lifting.

    Reacts to:
    - Filesystem changes (inotify/FSEvents)
    - Git operations (commit, push, pull)
    - Test results (pass/fail signals)
    - AGENTESE invocations across all jewels
    - CI/CD pipeline events
    - User commands
    """

    async def react(self, event: SystemEvent) -> AsyncGenerator[DaemonAction, None]:
        """React to system events, emit actions."""
        match event:
            case FileChanged(path) if self.is_relevant(path):
                yield await self.analyze_change(path)
            case TestFailed(test_id):
                yield await self.investigate_failure(test_id)
            case GitCommit(sha):
                yield await self.record_commit(sha)
            case TrustEscalation(new_level):
                yield await self.upgrade_capabilities(new_level)
```

### AGENTESE Path Structure

kgentsd exposes itself through AGENTESE:

```
# Daemon State (self.*)
self.daemon.manifest          → Current daemon state, trust level, active watchers
self.daemon.health            → Health status (replaces health.status file)
self.daemon.thoughts          → Recent thought stream
self.daemon.tensions          → Active tension points
self.daemon.trust             → Trust level + escalation history

# Daemon Actions (self.daemon.*)
self.daemon.watch             → Add a path to watch list
self.daemon.unwatch           → Remove a path from watch list
self.daemon.escalate          → Request trust escalation
self.daemon.act               → Execute an autonomous action (Level 3+)

# Daemon Configuration (concept.daemon.*)
concept.daemon.policy         → Projection policy, event filters
concept.daemon.collectors     → Registered collectors and their status
concept.daemon.capabilities   → What daemon can do at each trust level

# Cross-Jewel Invocation (world.daemon.*)
world.daemon.invoke           → Invoke any jewel on behalf of observer
world.daemon.pipeline         → Chain multiple jewel invocations
world.daemon.schedule         → Schedule future invocations

# Temporal Awareness (time.daemon.*)
time.daemon.history           → Action history with outcomes
time.daemon.patterns          → Detected behavioral patterns
time.daemon.forecast          → Predicted future events/needs
```

### Trust Escalation Model

```
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 0: READ-ONLY                                                  │
│ ─────────────────                                                   │
│ Can: Observe filesystem, git, tests, all jewels                     │
│ Can: Project to files, emit thoughts                                │
│ Cannot: Modify anything                                             │
│                                                                     │
│ Escalation trigger: Consistent accurate observations for 24h        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: BOUNDED MODIFICATION                                       │
│ ────────────────────────────                                        │
│ Can: All Level 0 + write to .kgents/ directory                      │
│ Can: Update ghost files, manage cache                               │
│ Cannot: Modify source code, run commands                            │
│                                                                     │
│ Escalation trigger: 100 successful bounded operations               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: SUGGESTION + CONFIRMATION                                  │
│ ─────────────────────────────────                                   │
│ Can: All Level 1 + propose code changes                             │
│ Can: Draft commits, suggest refactors                               │
│ Requires: Human confirmation before execution                       │
│                                                                     │
│ Escalation trigger: 50 confirmed suggestions with >90% acceptance   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: AUTONOMOUS OPERATION                                       │
│ ────────────────────────────                                        │
│ Can: Everything Kent can do                                         │
│ - Run tests, fix failures                                           │
│ - Commit changes with meaningful messages                           │
│ - Create PRs, respond to reviews                                    │
│ - Invoke any Crown Jewel                                            │
│ - Refactor based on patterns                                        │
│ - Write documentation                                               │
│                                                                     │
│ Rails: All actions logged, reversible, within defined boundaries    │
│ Escalation: No further levels; this IS Kent's developer agency      │
└─────────────────────────────────────────────────────────────────────┘
```

### Categorical Structure

**kgentsd Polynomial**:
```python
DAEMON_POLYNOMIAL = PolyAgent[
    DaemonState,      # S: trust level, watchers, thought history
    SystemEvent,      # A: filesystem, git, test, AGENTESE events
    DaemonAction      # B: observe, project, suggest, act
](
    state=DaemonState.initial(),
    directions={
        TrustLevel.READ_ONLY: ReadOnlyBehavior,
        TrustLevel.BOUNDED: BoundedBehavior,
        TrustLevel.SUGGESTION: SuggestionBehavior,
        TrustLevel.AUTONOMOUS: AutonomousBehavior,
    },
    transition=trust_transition_function,
)
```

**kgentsd Operad**:
```python
DAEMON_OPERAD = Operad(
    name="DAEMON_OPERAD",
    operations={
        # Collection operations
        "sense": Operation(arity=0, output="SystemEvent"),
        "aggregate": Operation(arity="*", output="AggregateState"),

        # Analysis operations
        "analyze": Operation(arity=1, output="Analysis"),
        "pattern": Operation(arity="*", output="Pattern"),

        # Action operations (trust-gated)
        "suggest": Operation(arity=1, output="Suggestion", requires=TrustLevel.SUGGESTION),
        "act": Operation(arity=1, output="ActionResult", requires=TrustLevel.AUTONOMOUS),

        # Cross-jewel operations
        "invoke_jewel": Operation(arity=2, output="JewelResult"),
        "pipeline": Operation(arity="*", output="PipelineResult"),
    },
    laws={
        "trust_monotonic": "trust(t+1) >= trust(t) - epsilon",
        "action_logged": "forall a in actions: exists log(a)",
        "action_reversible": "forall a in actions: exists inverse(a) or checkpoint(a)",
        "jewel_composition": "invoke(A) >> invoke(B) = invoke(A >> B)",
    }
)
```

**kgentsd Sheaf**:
```python
class DaemonSheaf(Sheaf):
    """
    Local sections: Each collector/watcher provides local observation
    Gluing condition: Observations from same timestamp are compatible
    Global section: Unified daemon state coherent across all sources
    """

    contexts = {
        "filesystem": FilesystemCollector,
        "git": GitCollector,
        "tests": TestCollector,
        "jewels": JewelObserver,
        "ci": CICollector,
    }

    def glue(self, sections: dict[str, LocalObservation]) -> GlobalState:
        """Sheaf gluing: compatible local observations → global daemon state."""
        # Compatibility check: all timestamps within tolerance
        # Gluing: merge observations into coherent state
        pass
```

---

## Event Sources

kgentsd reacts to events from multiple sources:

### Filesystem Events (via inotify/FSEvents)

```python
@event_source("filesystem")
class FilesystemWatcher:
    """
    Watches filesystem for relevant changes.
    Uses inotify (Linux) or FSEvents (macOS).
    """

    patterns = [
        "**/*.py",           # Python source
        "**/*.ts",           # TypeScript source
        "**/*.tsx",          # React components
        "**/pyproject.toml", # Config changes
        "**/package.json",   # Dependency changes
        "spec/**/*.md",      # Spec changes
        "plans/**/*.md",     # Plan changes
    ]

    ignore = [
        "**/__pycache__/**",
        "**/node_modules/**",
        "**/.git/**",
        "**/.venv/**",
    ]
```

### Git Events (via hooks)

```python
@event_source("git")
class GitWatcher:
    """
    Watches git operations.
    Can install hooks or poll git status.
    """

    events = [
        "pre-commit",   # Before commit (can block)
        "post-commit",  # After commit
        "pre-push",     # Before push (can block)
        "post-merge",   # After merge/pull
        "post-checkout", # After branch switch
    ]
```

### Test Events (via pytest hooks)

```python
@event_source("tests")
class TestWatcher:
    """
    Watches test execution.
    Integrates with pytest via conftest.py hooks.
    """

    events = [
        TestStarted(test_id, file, line),
        TestPassed(test_id, duration),
        TestFailed(test_id, error, traceback),
        TestSkipped(test_id, reason),
        SessionFinished(passed, failed, skipped, duration),
    ]
```

### AGENTESE Events (via SynergyBus)

```python
@event_source("agentese")
class AgenteseWatcher:
    """
    Watches all AGENTESE invocations across jewels.
    Subscribes to SynergyBus events.
    """

    subscriptions = [
        "world.**",     # All world events
        "self.**",      # All self events
        "concept.**",   # All concept events
        "time.**",      # All time events
        "void.entropy", # Entropy sips
    ]
```

### CI Events (via webhook or polling)

```python
@event_source("ci")
class CIWatcher:
    """
    Watches CI/CD pipeline events.
    Can receive webhooks or poll GitHub Actions.
    """

    events = [
        WorkflowStarted(workflow, run_id),
        JobCompleted(job, status, duration),
        WorkflowCompleted(workflow, status, duration),
        CheckFailed(check, details),
    ]
```

---

## Frontend Projection

As a Crown Jewel, kgentsd gets its own frontend experience:

### CLI Projection

```bash
# Start daemon (foreground)
kgents daemon

# Start daemon (background)
kgents daemon --background

# Check daemon status
kgents daemon status
# → kgentsd: running | trust:2 | watchers:7 | thoughts:142 | actions:23

# View thought stream
kgents daemon thoughts
# → Real-time stream of daemon thoughts

# View tensions
kgents daemon tensions
# → List of detected tension points

# Request trust escalation
kgents daemon escalate
# → Request escalation to next trust level

# Execute action (Level 3)
kgents daemon act "fix failing tests"
# → Daemon analyzes failures and fixes them
```

### Web Projection

```
/daemon                    → Dashboard: health, trust level, recent activity
/daemon/thoughts           → Real-time thought stream (SSE)
/daemon/tensions           → Tension map visualization
/daemon/history            → Action history with outcomes
/daemon/config             → Configuration and policy editor
/daemon/trust              → Trust level details, escalation path
```

### REPL Integration

```
kg> self.daemon.manifest
{
  "trust_level": 2,
  "watchers": ["filesystem", "git", "tests", "agentese", "ci"],
  "thought_count": 142,
  "tension_count": 3,
  "last_action": "suggested refactor in services/town/",
  "uptime": "4h 23m"
}

kg> self.daemon.thoughts --limit=5
- [10:23] Detected pattern: test failures cluster in services/town/
- [10:21] Git: 3 uncommitted changes in impl/claude/
- [10:19] CI: workflow 'test' passed in 4m 23s
- [10:15] Filesystem: 7 files changed since last observation
- [10:12] AGENTESE: 23 invocations in last hour

kg> self.daemon.act "analyze test failures"
[Level 3 required] Analyzing test failures...
Found 3 failing tests, all in services/town/:
  - test_citizen_consent: Consent threshold assertion
  - test_coalition_merge: Coalition size boundary
  - test_inhabit_flow: Missing mock for soul service

Suggested fix: Update test fixtures to include soul mock.
Shall I apply? [y/n]
```

---

## Implementation Strategy: Vertical Slice First

> *"Depth over breadth"* — We prove the architecture with ONE complete slice before expanding.

### The Anti-Waterfall Approach

The original 6-week plan risks being waterfall-esque. Instead:

```
WRONG: Phase 1 (all foundation) → Phase 2 (all watchers) → Phase 3 (all trust) → ...
RIGHT: Phase 0.5 (ONE complete vertical slice) → Validate → Expand
```

### What Exists Today (Ghost Audit)

```
infra/ghost/
├── daemon.py          # Timer-based loop (180s interval) - REPLACE
├── collectors.py      # 7 collectors (Git, Flinch, Infra, Meta, Trace, Memory, CI)
├── health.py          # CompositeHealth aggregation - KEEP
├── lifecycle.py       # TTL cache with human labels - KEEP
├── cache.py           # GlassCacheManager - KEEP
└── ci_collector.py    # CISignalCollector - MIGRATE
```

**What to Keep**: Health aggregation, lifecycle cache, glass cache
**What to Replace**: Timer loop, file-only projection
**What to Migrate**: Collectors → WatcherPolynomials

---

## Phase 0.5: The Git Watcher Vertical Slice (THIS SPRINT)

**Goal**: Prove the entire architecture with ONE event source end-to-end.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    VERTICAL SLICE: Git Watcher                           │
├──────────────────────────────────────────────────────────────────────────┤
│  7. PROJECTION     CLI: `kg witness thoughts` | Web: /witness/thoughts   │
├──────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE       self.witness.manifest | self.witness.thoughts         │
├──────────────────────────────────────────────────────────────────────────┤
│  5. @node          WitnessNode with aspects + contracts                  │
├──────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE        services/witness/ (Crown Jewel location)              │
├──────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD         WITNESS_OPERAD: sense, analyze, suggest               │
├──────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL     WitnessPolynomial[TrustLevel, Event, Action]          │
├──────────────────────────────────────────────────────────────────────────┤
│  1. FLUX           GitWatcherFlux (event-driven, no timers)              │
└──────────────────────────────────────────────────────────────────────────┘
```

### Deliverables (Phase 0.5)

| Item | Path | Purpose |
|------|------|---------|
| WitnessPolynomial | `services/witness/polynomial.py` | Trust-gated state machine |
| WITNESS_OPERAD | `services/witness/operad.py` | Composition grammar |
| GitWatcherFlux | `services/witness/watchers/git.py` | Event-driven git monitoring |
| WitnessNode | `protocols/agentese/contexts/self_witness.py` | AGENTESE integration |
| CLI handler | `protocols/cli/handlers/witness.py` | `kg witness *` commands |
| Basic tests | `services/witness/_tests/` | Property-based polynomial tests |

### Why "Witness" Not "Daemon"?

**Daemon** implies invisible background process (Unix heritage).
**Witness** implies:
- Observer that can testify (trust-gated action)
- Presence matters (not just background noise)
- Philosophical alignment with Observer-dependent ontology

The name is opinionated—*"daring, bold, creative"*.

### Phase 0.5 Success Criteria

- [ ] `kg witness start` starts event-driven watcher (no timers)
- [ ] Git commits trigger immediate thought stream update
- [ ] `kg witness thoughts` shows recent observations
- [ ] `self.witness.manifest` returns trust level and watcher status
- [ ] Tests verify polynomial state transitions
- [ ] Architecture is proven; other watchers are "just more of the same"

---

## Implementation Phases (Post-Vertical-Slice)

### Phase 1: Foundation Complete (Week 1-2)

**Goal**: Complete the service skeleton and add remaining watchers

- [ ] Migrate `infra/ghost/` → `services/witness/` (preserve what works)
- [ ] Add FileSystemWatcherFlux (inotify/FSEvents)
- [ ] Add TestWatcherFlux (pytest hooks)
- [ ] Add AgenteseWatcherFlux (SynergyBus subscription)
- [ ] Add CIWatcherFlux (GitHub Actions)

**Deliverables**:
- `services/witness/watchers/` — All five event sources
- `services/witness/aggregator.py` — Sheaf-like gluing of watcher sections

### Phase 2: Event Sources (Week 2)

**Goal**: Implement all event sources

- [ ] Filesystem watcher (inotify/FSEvents integration)
- [ ] Git watcher (hook integration or polling)
- [ ] Test watcher (pytest hook integration)
- [ ] AGENTESE watcher (SynergyBus subscription)
- [ ] CI watcher (GitHub Actions webhook/polling)

**Deliverables**:
- `services/daemon/watchers/filesystem.py`
- `services/daemon/watchers/git.py`
- `services/daemon/watchers/tests.py`
- `services/daemon/watchers/agentese.py`
- `services/daemon/watchers/ci.py`

### Phase 3: Trust Escalation (Week 3)

**Goal**: Implement trust level system

- [ ] Define trust level capabilities
- [ ] Implement escalation triggers
- [ ] Add confirmation flow for Level 2
- [ ] Implement autonomous action execution for Level 3
- [ ] Add action logging and reversibility

**Deliverables**:
- `services/daemon/trust.py` — Trust level system
- `services/daemon/actions.py` — Action execution
- `services/daemon/history.py` — Action history and rollback

### Phase 4: Cross-Jewel Integration (Week 4)

**Goal**: Enable daemon to invoke all jewels

- [ ] Implement `world.daemon.invoke` for single jewel invocation
- [ ] Implement `world.daemon.pipeline` for chained invocations
- [ ] Add scheduling for future invocations
- [ ] Connect to all existing jewels

**Deliverables**:
- `services/daemon/invoke.py` — Cross-jewel invocation
- `services/daemon/pipeline.py` — Pipeline composition
- `services/daemon/schedule.py` — Future scheduling

### Phase 5: Frontend Experience (Week 5)

**Goal**: Build daemon frontend

- [ ] CLI commands (`kgents daemon *`)
- [ ] Web dashboard at `/daemon`
- [ ] REPL integration
- [ ] Real-time thought stream (SSE)

**Deliverables**:
- `protocols/cli/handlers/daemon.py` — CLI handler
- `web/src/pages/Daemon/` — Web components
- REPL integration in existing shell

### Phase 6: Production Hardening (Week 6)

**Goal**: Make daemon production-ready

- [ ] Add comprehensive tests (property-based for trust transitions)
- [ ] Add performance baselines
- [ ] Add graceful degradation
- [ ] Add metrics and observability
- [ ] Documentation

**Deliverables**:
- `services/daemon/_tests/` — Comprehensive test suite
- `docs/daemon.md` — User documentation
- `spec/agents/daemon.md` — Specification

---

## Success Criteria

### Functional
- [ ] Daemon starts and runs without timer loops
- [ ] Reacts to filesystem, git, test, AGENTESE, CI events
- [ ] Trust levels gate capabilities correctly
- [ ] Level 3 can execute Kent's common developer tasks
- [ ] All actions are logged and reversible

### Non-Functional
- [ ] Event latency < 100ms (detect to react)
- [ ] Memory usage < 100MB idle
- [ ] Zero false positive actions at Level 3
- [ ] 100% action reversibility or checkpoint coverage

### Aesthetic
- [ ] Thought stream reads like a diary, not a log
- [ ] Tensions are surfaced with empathy
- [ ] Actions are explained clearly
- [ ] Trust escalation feels earned, not arbitrary

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive autonomous actions | High | Conservative escalation triggers; all actions reversible |
| Event storm overwhelming daemon | Medium | Debouncing, priority queues, backpressure |
| Trust gaming by adversarial input | Medium | Trust based on outcomes, not inputs; anomaly detection |
| Cross-jewel invocation failures | Medium | Circuit breaker pattern; graceful degradation |
| Filesystem watcher platform differences | Low | Abstract watcher interface; platform-specific implementations |

---

## Design Decisions (Resolved)

### 1. Trust Persistence ✅

**Decision**: Yes, trust persists across restarts WITH decay.

```python
# Trust decays by 0.1 levels per 24h of inactivity
# Minimum decay floor: L1 (never drops below L1 after first achievement)
def compute_trust_with_decay(stored_level: TrustLevel, last_active: datetime) -> TrustLevel:
    hours_inactive = (datetime.now() - last_active).total_seconds() / 3600
    decay_steps = int(hours_inactive / 24) * 0.1
    effective_level = max(stored_level.value - decay_steps, 1)  # Floor at L1
    return TrustLevel(int(effective_level))
```

**Rationale**: Trust must be earned, and inactivity should modestly erode it. But the first climb from L0→L1 should never be lost.

### 2. Multi-User ✅

**Decision**: Per-repository trust, keyed by git user email.

```python
# Trust stored in .kgents/witness/trust/{git_email_hash}.json
# Each developer earns their own trust level
# Shared repos have shared OBSERVATIONS but separate TRUST
```

**Rationale**: Developer agency should be personal. My kgentsd shouldn't act on your behalf.

### 3. Forbidden Actions ✅

**Decision**: Hardcoded NEVER list, not configurable.

```python
FORBIDDEN_ACTIONS = frozenset({
    "git push --force origin main",
    "git push --force origin master",
    "rm -rf /",
    "DROP DATABASE",
    "DELETE FROM",  # Must use soft-delete pattern
    "kubectl delete namespace",
    "vault token",  # Never touch secrets
    "stripe",       # Never touch payments
})
```

**Rationale**: Some things should NEVER be autonomous, period. This is not negotiable. *"Daring"* doesn't mean *"reckless"*.

### 4. Rollback Scope ✅

**Decision**: Last 100 actions OR 7 days, whichever is smaller.

```python
# Every action creates a reversibility checkpoint
# Checkpoints are automatically pruned after 7 days
# ActionHistory is append-only with bounded window

@dataclass(frozen=True)
class ActionCheckpoint:
    action_id: str
    timestamp: datetime
    action_type: str
    inverse: str | None  # The undo command, if determinable
    snapshot_path: Path  # Git stash or file backup
```

**Rationale**: 7 days is long enough to notice problems, short enough to not bloat storage. 100 actions is sufficient granularity for debugging.

---

## Related Documents

- `plans/kgentsd-event-architecture.md` — Detailed event source design
- `plans/kgentsd-trust-system.md` — Trust escalation deep dive
- `plans/kgentsd-cross-jewel.md` — Cross-jewel invocation patterns
- `spec/agents/daemon.md` — Specification (to be created)
- `docs/skills/daemon-patterns.md` — Implementation patterns (to be created)

---

*"The daemon is Kent's will, made manifest in the machine."*
