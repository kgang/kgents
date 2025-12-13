# Turn-gents Continuation: From CLI to Living System

> *"A feature that exists but isn't felt doesn't exist."*

## Mission

Turn-gents infrastructure is complete but **dormant** - no agents are actually recording turns. This prompt advances Turn-gents from infrastructure to a living, breathing system that developers can feel.

## Current State: What's Built

### CLI Commands (✅ Complete)
```bash
kg turns [agent]          # Show turn history
kg dag [--interactive]    # Visualize turn DAG
kg fork <turn_id>         # Fork from a turn for debugging
kg pending                # List pending YIELD turns
kg approve <turn_id>      # Approve a YIELD turn
kg reject <turn_id>       # Reject a YIELD turn
kg flinch --turns         # Turn panel in test failure analysis
```

### Infrastructure (✅ Complete)
| Module | Components |
|--------|------------|
| `weave/turn.py` | Turn, TurnType, YieldTurn |
| `weave/causal_cone.py` | CausalCone, CausalConeStats |
| `weave/yield_handler.py` | YieldHandler, ApprovalStrategy, ApprovalResult |
| `weave/economics.py` | TurnBudgetTracker, BudgetPolicy |
| `agents/i/screens/turn_dag.py` | TurnDAGRenderer, TurnDAGConfig |
| `system/projector/local.py` | TurnBasedAdapter |
| `agents/a/halo.py` | @Capability.TurnBased decorator |

### Tests (✅ Complete)
- 61 tests for CLI handlers (`test_turns.py`, `test_approve.py`)
- 46 tests for Turn/YieldTurn (`test_turn.py`)
- 21 tests for CausalCone (`test_causal_cone.py`)
- 28 tests for YieldHandler (`test_yield_handler.py`)

## The Problem

Running `kg turns` shows **"No turns recorded"** because:
1. No agents are decorated with `@Capability.TurnBased`
2. Global Weave isn't connected to lifecycle/storage
3. TurnBasedAdapter creates instance-local weaves

---

## Continuation Tasks

### Task 1: Connect Global Weave to Lifecycle (Priority: Critical)

Without this, every TurnBasedAdapter creates its own isolated Weave.

**File**: `protocols/cli/instance_db/lifecycle.py`

Add Weave to LifecycleState:
```python
from weave import TheWeave

@dataclass
class LifecycleState:
    mode: LifecycleMode
    instance_id: str | None
    storage_provider: Any
    weave: TheWeave = field(default_factory=TheWeave)  # ADD THIS
```

**File**: `system/projector/local.py`

Update TurnBasedAdapter to use shared weave:
```python
def _get_or_create_weave(self) -> TheWeave:
    """Get global weave or create instance-local fallback."""
    # Try lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state
        state = get_lifecycle_state()
        if state and hasattr(state, 'weave'):
            return state.weave
    except ImportError:
        pass

    # Fallback to instance-local
    if self._weave is None:
        from weave import TheWeave
        self._weave = TheWeave()
    return self._weave
```

**File**: `protocols/cli/handlers/turns.py`

Update `_get_global_weave()`:
```python
def _get_global_weave() -> Any:
    """Get the global Weave from lifecycle state."""
    try:
        from protocols.cli.hollow import get_lifecycle_state
        state = get_lifecycle_state()
        if state and hasattr(state, 'weave'):
            return state.weave
    except ImportError:
        pass

    from weave import TheWeave
    return TheWeave()  # Empty fallback
```

### Task 2: Apply @TurnBased to K-gent (Priority: High)

K-gent is the ideal first candidate - it already handles persona and governance.

**File**: Find K-gent's main agent class (likely `agents/k/__init__.py` or similar)

```python
@Capability.TurnBased(
    allowed_types={"SPEECH", "ACTION", "THOUGHT", "YIELD"},
    yield_threshold=0.5,  # YIELD for uncertain persona decisions
    entropy_budget=10.0,
    surplus_fraction=0.1,
)
@Capability.Soulful(persona="K-gent")
class KgentAgent(Agent[SoulInput, SoulOutput]):
    ...
```

**Verification**:
```bash
# Run K-gent
kg soul challenge "What should I prioritize?"

# Check turns were recorded
kg turns k-gent --last 10

# View DAG
kg dag --agent k-gent
```

### Task 3: Dashboard Turn Metrics Panel

**File**: `agents/i/data/turn_collectors.py` (create)

```python
"""Turn metrics collectors for dashboard integration."""

from dataclasses import dataclass
from typing import Any

@dataclass
class TurnStats:
    total_turns: int
    by_type: dict[str, int]
    by_source: dict[str, int]
    pending_yields: int

@dataclass
class CompressionStats:
    agent_id: str
    cone_size: int
    total_size: int
    compression_ratio: float
    estimated_token_savings: int

class TurnMetricsCollector:
    """Collect turn metrics for dashboard."""

    def __init__(self, weave: Any) -> None:
        self.weave = weave

    def collect_turn_stats(self) -> TurnStats:
        from weave import Turn, TurnType
        from protocols.cli.handlers.approve import get_yield_handler

        by_type: dict[str, int] = {}
        by_source: dict[str, int] = {}

        for event in self.weave.monoid.events:
            source = getattr(event, 'source', 'unknown')
            by_source[source] = by_source.get(source, 0) + 1

            if isinstance(event, Turn):
                type_name = event.turn_type.name
                by_type[type_name] = by_type.get(type_name, 0) + 1

        handler = get_yield_handler()
        pending = len(handler.list_pending())

        return TurnStats(
            total_turns=len(self.weave),
            by_type=by_type,
            by_source=by_source,
            pending_yields=pending,
        )

    def collect_compression_stats(self, agent_id: str) -> CompressionStats:
        from weave import CausalCone

        cone = CausalCone(self.weave)
        cone_size = cone.cone_size(agent_id)
        total = len(self.weave)
        ratio = cone.compression_ratio(agent_id)

        # ~100 chars/event, ~4 chars/token
        tokens_saved = ((total - cone_size) * 100) // 4

        return CompressionStats(
            agent_id=agent_id,
            cone_size=cone_size,
            total_size=total,
            compression_ratio=ratio,
            estimated_token_savings=tokens_saved,
        )
```

**File**: `agents/i/screens/mri.py`

Find the dashboard render method and add:
```python
def _render_turn_panel(self) -> Panel:
    """Render Turn-gents metrics panel."""
    from agents.i.data.turn_collectors import TurnMetricsCollector
    from protocols.cli.handlers.turns import _get_global_weave

    weave = _get_global_weave()
    if len(weave) == 0:
        return Panel("[dim]No turns recorded[/]", title="Turn-gents")

    collector = TurnMetricsCollector(weave)
    stats = collector.collect_turn_stats()

    content = Text()
    content.append(f"Total: {stats.total_turns}\n", style="bold")

    type_colors = {
        "SPEECH": "green", "ACTION": "blue", "THOUGHT": "dim",
        "YIELD": "yellow", "SILENCE": "dim"
    }
    for t, count in sorted(stats.by_type.items()):
        content.append(f"  {t}: {count}\n", style=type_colors.get(t, "white"))

    if stats.pending_yields > 0:
        content.append(f"\n[yellow]Pending: {stats.pending_yields}[/]")

    return Panel(content, title="Turn-gents", border_style="cyan")
```

### Task 4: Compression Metrics for H1 Validation

**File**: `weave/metrics.py` (create)

```python
"""Compression metrics for Turn-gents hypothesis validation."""

import time
from dataclasses import dataclass
from typing import Any

_compression_events: list["CompressionEvent"] = []

@dataclass
class CompressionEvent:
    timestamp: float
    agent_id: str
    full_tokens: int
    cone_tokens: int
    compression_ratio: float

@dataclass
class CompressionMetrics:
    total_events: int
    avg_compression: float
    total_tokens_saved: int
    h1_passed: bool  # >50% compression?

def log_compression(agent_id: str, full: int, cone: int) -> None:
    """Log a compression event."""
    ratio = 1.0 - (cone / full) if full > 0 else 0.0
    _compression_events.append(CompressionEvent(
        timestamp=time.time(),
        agent_id=agent_id,
        full_tokens=full,
        cone_tokens=cone,
        compression_ratio=ratio,
    ))

def get_metrics() -> CompressionMetrics:
    """Get aggregated compression metrics."""
    if not _compression_events:
        return CompressionMetrics(0, 0.0, 0, False)

    saved = sum(e.full_tokens - e.cone_tokens for e in _compression_events)
    avg = sum(e.compression_ratio for e in _compression_events) / len(_compression_events)

    return CompressionMetrics(
        total_events=len(_compression_events),
        avg_compression=avg,
        total_tokens_saved=saved,
        h1_passed=avg >= 0.5,
    )
```

**Integration**: Call `log_compression()` in TurnBasedAdapter.get_context().

### Task 5: YIELD TUI Panel in Terrarium

**File**: Find Terrarium screen file (e.g., `agents/i/screens/terrarium.py`)

Add pending approvals widget:
```python
class PendingApprovalsWidget(Static):
    """Shows pending YIELD turns."""

    BINDINGS = [
        ("a", "approve", "Approve"),
        ("r", "reject", "Reject"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(id="pending-list")

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        from protocols.cli.handlers.approve import get_yield_handler

        handler = get_yield_handler()
        pending = handler.list_pending()

        if not pending:
            self.query_one("#pending-list").update("[dim]No pending[/]")
            return

        content = Text()
        for t in pending[:5]:
            content.append(f"[{t.id[:8]}] ", style="cyan")
            content.append(f"{t.source}: {t.yield_reason[:30]}\n")
        self.query_one("#pending-list").update(content)

    async def action_approve(self) -> None:
        from protocols.cli.handlers.approve import get_yield_handler
        handler = get_yield_handler()
        pending = handler.list_pending()
        if pending:
            await handler.approve(pending[0].id, "human")
            self._refresh()
```

---

## Verification Plan

After implementation:

```bash
# 1. Bootstrap creates weave
kg status  # Should show weave in lifecycle

# 2. Run agent interaction
kg soul challenge "What should I focus on?"

# 3. Verify turns recorded
kg turns k-gent --last 10
# Should show SPEECH, THOUGHT, ACTION turns

# 4. View DAG
kg dag --agent k-gent
# Should render tree with causal structure

# 5. Check compression
kg turns --stats
# Should show compression ratios

# 6. If YIELD triggered
kg pending
kg approve <turn-id>

# 7. Run tests
cd impl/claude
uv run pytest protocols/cli/handlers/_tests/test_turns.py \
    protocols/cli/handlers/_tests/test_approve.py \
    weave/_tests/test_turn.py -v
```

---

## Success Criteria

From Turn-gents Falsifiable Hypotheses:

| Hypothesis | Metric | Target |
|------------|--------|--------|
| H1 (Efficiency) | Compression ratio | >50% |
| H2 (Debuggability) | Root cause time | -30% |
| H3 (Governance) | False YIELD rate | <10% |
| H4 (Concurrency) | Cross-leak events | 0 |

## Files to Touch

| File | Action |
|------|--------|
| `protocols/cli/instance_db/lifecycle.py` | Add `weave` field |
| `system/projector/local.py` | Use global weave |
| `protocols/cli/handlers/turns.py` | Connect to lifecycle |
| `agents/k/__init__.py` | Add @TurnBased |
| `agents/i/data/turn_collectors.py` | Create |
| `agents/i/screens/mri.py` | Add turn panel |
| `weave/metrics.py` | Create |

## Priority Order

1. **Global Weave** (Task 1) - Foundation
2. **@TurnBased on K-gent** (Task 2) - Creates data
3. **Dashboard metrics** (Task 3) - Visibility
4. **Compression metrics** (Task 4) - Prove value
5. **YIELD TUI** (Task 5) - Polish

---

*"The noun is a lie. There is only the rate of change."* — AGENTESE
