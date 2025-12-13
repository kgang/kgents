# Turn-gents Realization: From Theory to Developer Impact

> *"A feature that exists but isn't felt doesn't exist."*

## Mission

Make Turn-gents **felt** by developers. The protocol is implemented (267 tests, 7 phases complete), but it's not yet changing how developers work. This prompt drives Turn-gents from infrastructure to impact.

## Current State

Turn-gents is fully implemented but **dormant**:
- ✅ Turn schema, CausalCone, YieldHandler, TurnBudgetTracker all work
- ✅ TurnBasedAdapter wraps agents via `@Capability.TurnBased`
- ✅ TurnDAGRenderer can visualize turn history
- ❌ No CLI commands expose Turn-gents to developers
- ❌ Dashboard doesn't show turn-based debugging
- ❌ No agents are actually decorated with `@TurnBased`
- ❌ YIELD approvals have no UI
- ❌ Context compression isn't measured or reported

## The Goal: Developer-Facing Turn-gents

After this work, developers should:
1. **See** turn history when debugging (`kg turns`, `kg dag`)
2. **Feel** context compression in faster agent responses
3. **Control** high-risk actions via YIELD approval prompts
4. **Monitor** budget utilization in the dashboard
5. **Debug** causality issues with cone visualization

---

## Realization Tasks

### Task 1: CLI Commands for Turn-gents

**Goal**: `kg turns` and `kg dag` commands for turn debugging.

**Create** `protocols/cli/handlers/turns.py`:
```python
@app.command()
def turns(
    agent: str = typer.Argument(..., help="Agent name to inspect"),
    last: int = typer.Option(10, help="Number of recent turns"),
    show_thoughts: bool = typer.Option(False, "--thoughts", help="Show THOUGHT turns"),
):
    """Show turn history for an agent."""
    # Load agent's weave from persistent storage
    # Render with TurnDAGRenderer
    # Show compression ratio

@app.command()
def dag(
    agent: str = typer.Argument(None, help="Agent to highlight cone for"),
    interactive: bool = typer.Option(False, "-i", help="Interactive TUI mode"),
):
    """Visualize turn DAG."""
    # If interactive, launch TUI with turn_dag panel
    # Otherwise, render static Rich output
```

**Add to** `protocols/cli/handlers/flinch.py`:
- `--turns` flag to show turn panel in Terrarium
- Keyboard shortcut `t` to toggle turn DAG visibility

**Tests**: CLI commands work, show correct data, handle missing agents gracefully.

---

### Task 2: Dashboard Integration

**Goal**: Turn metrics visible in Terrarium dashboard.

**Update** `agents/i/screens/mri.py`:
- Replace "Token Context Window" placeholder with actual CausalCone visualization
- Add turn statistics panel (counts by type, compression ratio)
- Show budget utilization (order vs surplus)

**Create** `agents/i/data/turn_collectors.py`:
```python
class TurnMetricsCollector:
    """Collect turn metrics for dashboard."""

    def collect_turn_stats(self, agent_id: str) -> TurnStats:
        """Get turn statistics for an agent."""

    def collect_budget_stats(self, agent_id: str) -> BudgetStats:
        """Get budget utilization stats."""

    def collect_compression_stats(self, agent_id: str) -> CompressionStats:
        """Get context compression metrics."""
```

**Integration with Ghost collectors**:
- Emit turn metrics as OTEL spans
- Budget utilization as gauges
- Compression ratio as histogram

**Tests**: Collectors work, metrics are accurate, dashboard renders correctly.

---

### Task 3: Apply @TurnBased to Key Agents

**Goal**: At least 3 agent genera using Turn-gents in practice.

**Candidates**:
1. **K-gent (Soul)**: Perfect for YIELD governance - high-risk persona decisions
2. **D-gent (Memory)**: State changes should be tracked as turns
3. **Poly agents**: Polynomial state transitions map naturally to turns

**For each agent**:
```python
@Capability.TurnBased(
    allowed_types={"SPEECH", "ACTION", "YIELD"},
    yield_threshold=0.5,  # YIELD for uncertain actions
    entropy_budget=10.0,
    surplus_fraction=0.1,
)
class KgentAgent(Agent[SoulInput, SoulOutput]):
    ...
```

**Verify**:
- Turns are being recorded
- Context compression is happening
- YIELD triggers for low-confidence actions

**Tests**: Decorated agents record turns, compression is measurable, YIELD works.

---

### Task 4: YIELD Approval UI

**Goal**: Developer can approve/reject YIELD turns interactively.

**Options**:
1. **CLI prompt**: When YIELD occurs, prompt in terminal
2. **TUI panel**: Pending approvals panel in Terrarium
3. **Notification**: System notification for pending YIELDs

**Create** `protocols/cli/handlers/approve.py`:
```python
@app.command()
def approve(turn_id: str):
    """Approve a pending YIELD turn."""

@app.command()
def reject(turn_id: str, reason: str = ""):
    """Reject a pending YIELD turn."""

@app.command()
def pending():
    """List all pending YIELD turns awaiting approval."""
```

**Add to Terrarium**:
- Pending approvals panel (shows YIELD turns awaiting action)
- Keyboard shortcuts: `a` to approve, `r` to reject
- Visual indicator when YIELDs are pending

**Tests**: Approval flow works end-to-end, rejected YIELDs prevent action.

---

### Task 5: Context Compression Metrics

**Goal**: Prove Turn-gents delivers on H1 (>50% token reduction).

**Create** `weave/metrics.py`:
```python
@dataclass
class CompressionMetrics:
    """Track context compression over time."""

    full_context_tokens: int
    cone_context_tokens: int
    compression_ratio: float

    @classmethod
    def measure(cls, weave: TheWeave, agent_id: str) -> CompressionMetrics:
        """Measure compression for an agent."""

def log_compression_event(
    agent_id: str,
    full_tokens: int,
    cone_tokens: int,
) -> None:
    """Log a compression event for analysis."""
```

**Integration**:
- Log compression on every context projection
- Aggregate in dashboard
- Alert if compression ratio drops below threshold

**Tests**: Metrics accurate, logging works, aggregation correct.

---

### Task 6: Fork/Rewind in Practice

**Goal**: Developers can fork from any turn for debugging.

**Add to** `protocols/cli/handlers/turns.py`:
```python
@app.command()
def fork(
    turn_id: str = typer.Argument(..., help="Turn ID to fork from"),
    name: str = typer.Option(None, help="Name for forked branch"),
):
    """Fork a new branch from a specific turn."""
    # Use TurnDAGRenderer.fork_from()
    # Persist the forked weave
    # Allow running agents in the forked branch
```

**TUI integration**:
- Select turn in DAG view
- `f` to fork from selected turn
- Show forked branches in tree view

**Tests**: Fork creates valid branch, original unchanged, can run agents in fork.

---

## Integration Points

### With Existing Systems

| System | Turn-gents Integration |
|--------|----------------------|
| Ghost (Observability) | Emit turn metrics as OTEL spans |
| Terrarium (TUI) | TurnDAG panel, approval UI |
| CLI (kgents) | `kg turns`, `kg dag`, `kg approve` |
| LocalProjector | Already wraps with TurnBasedAdapter |
| TheWeave | Already stores turns |

### New Developer Workflows

| Before Turn-gents | After Turn-gents |
|-------------------|------------------|
| Debug by reading logs | Debug by inspecting turn DAG |
| Full context always | Cone-projected minimal context |
| No visibility into agent "thinking" | THOUGHT turns visible (toggle) |
| Actions happen without check | YIELD for uncertain actions |
| Unknown resource usage | Budget tracking and limits |

---

## Success Criteria

From the Turn-gents plan's Falsifiable Hypotheses:

- **H1 (Context Efficiency)**: Measure and display >50% compression
- **H2 (Debuggability)**: Fork/rewind demonstrably speeds debugging
- **H3 (Governance)**: YIELD prevents at least one risky action in demo
- **H4 (Concurrency)**: Multiple agents' cones don't cross-pollinate

## Verification Commands

```bash
# After implementation, these should work:

# Show turn history
kg turns kgent --last 20

# Visualize DAG interactively
kg dag --interactive

# Show pending approvals
kg pending

# Approve a YIELD
kg approve turn-abc123

# Fork for debugging
kg fork turn-xyz789 --name "debug-branch"

# Show compression stats
kg stats compression

# Run full test suite
cd impl/claude
uv run pytest -v
```

---

## Principles Alignment

| Principle | How This Realizes It |
|-----------|---------------------|
| **Tasteful** | CLI commands are minimal, focused |
| **Curated** | Only expose what developers need |
| **Ethical** | YIELD UI makes governance tangible |
| **Joy-Inducing** | Turn DAG is satisfying to explore |
| **Composable** | Fork/rewind enables experimentation |
| **Accursed Share** | Surplus budget visible in dashboard |

---

## How to Proceed

1. **Start with Task 1** (CLI commands) - most immediate developer impact
2. **Then Task 4** (YIELD UI) - makes governance tangible
3. **Then Task 3** (Apply to agents) - creates real turn data
4. **Then Task 2** (Dashboard) - visualize the data
5. **Finally Tasks 5-6** (Metrics, Fork) - polish and prove value

Each task should include:
- Implementation
- Tests (unit + integration)
- Documentation update
- Demo/verification

---

*"The noun is a lie. There is only the rate of change."* — AGENTESE

*"A feature that exists but isn't felt doesn't exist."* — DevEx
