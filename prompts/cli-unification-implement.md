# CLI Unification: Implementation Prompt

> **Process**: Full 11-phase ceremony (AD-005)
> **Skill Reference**: `plans/skills/n-phase-cycle/README.md`
> **Plan Reference**: `plans/devex/cli-unification.md`

---

## Hydration Block

```
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification; phase=IMPLEMENT; ledger={PLAN:✓,RESEARCH:pending}; entropy=0.08
mission: Refactor CLI from 17,967 lines to < 8,000 lines with unified patterns.
actions:
  - SENSE: Map current handler structure and identify extraction points
  - ACT: Create shared infrastructure, then refactor soul.py first
  - REFLECT: Update plan with learnings, generate continuation
exit: soul.py refactored to < 300 lines; unified streaming works; all tests pass.
⟂[BLOCKED:test_failure] if tests break during refactor
⟂[BLOCKED:regression] if any command stops working
```

---

## Phase: PLAN

### Scope

**In Scope**:
- Extract shared infrastructure to `cli/shared/`
- Break `soul.py` (2019 lines) into `commands/soul/` (10+ files)
- Unify streaming patterns across commands
- Maintain backward compatibility

**Non-Goals**:
- New CLI features
- Breaking API changes
- Performance optimization

### Exit Criteria

1. Shared infrastructure exists in `cli/shared/`
2. `soul.py` < 300 lines (routing only)
3. Each dialogue mode has its own file
4. Unified streaming works for all modes
5. All existing tests pass
6. No command regressions

### Attention Budget

| Phase | Budget |
|-------|--------|
| SENSE (PLAN → DEVELOP) | 20% |
| ACT (IMPLEMENT → TEST) | 70% |
| REFLECT | 10% |

### Entropy Sip

```
void.entropy.sip[phase=PLAN][amount=0.02]
```

Exploration budget for discovering unexpected coupling in handlers.

---

## Phase: RESEARCH

### File Map (Critical Files)

| File | Lines | Role | Action |
|------|-------|------|--------|
| `handlers/soul.py` | 2019 | K-gent CLI | **Primary target** |
| `handlers/a_gent.py` | 1110 | Agent CLI | Secondary target |
| `handlers/turns.py` | 892 | Turn CLI | Review patterns |
| `handlers/infra.py` | 842 | K8s CLI | Consolidate later |
| `hollow.py` | ~200 | Entry point | Keep small |

### Extraction Points in soul.py

1. **Lines 1-100**: Imports, docstring, help → Keep in `__init__.py`
2. **Lines 100-400**: Mode parsing, context → `shared/context.py`
3. **Lines 400-600**: Streaming dialogue → `streaming.py`
4. **Lines 600-900**: Individual mode handlers → `reflect.py`, `challenge.py`, etc.
5. **Lines 900-1200**: Special commands (vibe, drift, tense) → `vibe.py`, etc.
6. **Lines 1200-2019**: Garden, validate, dream, etc. → `garden.py`, `validate.py`

### Blockers

| Blocker | Risk | Mitigation |
|---------|------|------------|
| Circular imports | Medium | Extract interfaces first |
| Test coupling | Medium | Run tests after each extraction |
| Hidden state | Low | Context object encapsulates |

---

## Phase: DEVELOP

### API Contracts

#### 1. Command Protocol

```python
from typing import Protocol

class Command(Protocol):
    """Every CLI command implements this."""

    name: str
    help: str

    async def execute(
        self,
        args: list[str],
        ctx: InvocationContext,
        output: OutputFormatter,
    ) -> int:
        """Execute the command. Return exit code."""
        ...
```

#### 2. OutputFormatter Contract

```python
@dataclass
class OutputFormatter:
    """Unified output handling."""

    json_mode: bool
    stream_mode: bool
    pipe_mode: bool

    def emit(self, text: str, data: dict | None = None) -> None: ...
    def emit_json(self, data: dict) -> None: ...
    def stream_chunk(self, chunk: str, index: int) -> None: ...
    def stream_metadata(self, metadata: dict) -> None: ...
    def emit_error(self, message: str, code: str | None = None) -> None: ...
```

#### 3. Streaming Handler Contract

```python
@dataclass
class StreamingHandler:
    """Handle streaming output for any command."""

    output: OutputFormatter

    async def stream_flux(self, flux: FluxStream[str]) -> StreamResult: ...
    async def stream_iterator(self, it: AsyncIterator[str]) -> StreamResult: ...
```

### Law Assertions

1. **Composition Law**: `(A >> B) >> C ≡ A >> (B >> C)` for command pipelines
2. **Identity Law**: `kgents soul reflect X | cat ≡ kgents soul reflect X`
3. **Pipe Law**: Output of command A is valid input to command B

---

## Phase: STRATEGIZE

### Sequencing

```
Phase 1: Shared Infrastructure
    │
    ├── 1.1 Create cli/shared/ directory structure
    ├── 1.2 Extract InvocationContext to shared/context.py
    ├── 1.3 Create OutputFormatter in shared/output.py
    ├── 1.4 Create StreamingHandler in shared/streaming.py
    └── 1.5 Create PipeReader/PipeWriter in shared/pipe.py
    │
    ▼
Phase 2: Soul Command Refactor
    │
    ├── 2.1 Create commands/soul/__init__.py (router)
    ├── 2.2 Extract reflect.py (first, proves pattern)
    ├── 2.3 Extract challenge.py, advise.py, explore.py
    ├── 2.4 Extract vibe.py, drift.py, tense.py
    ├── 2.5 Extract garden.py, validate.py, dream.py
    └── 2.6 Reduce original soul.py to router only
    │
    ▼
Phase 3: Integration Tests
    │
    ├── 3.1 Test all existing soul commands still work
    ├── 3.2 Test pipe composition works
    └── 3.3 Test streaming modes work
```

### Leverage Points

1. **OutputFormatter first** — Unlocks consistent output everywhere
2. **reflect.py first** — Simplest mode, proves extraction pattern
3. **Tests after each extraction** — Fast feedback, no regression accumulation

---

## Phase: CROSS-SYNERGIZE

### Compositions Identified

| This Work | Composes With | Opportunity |
|-----------|---------------|-------------|
| CLI Unification | Agent Town | CLI as agent control plane |
| Streaming infra | K-gent Soul | Unified dialogue streaming |
| Pipe composition | Flow Engine | `kgents flow run` uses pipes |
| OutputFormatter | Terrarium | CLI observability |
| Command Protocol | MCP | Commands as MCP tools |

### Dormant Plans Awakened

- `plans/self/cli-refactor.md` — Earlier CLI refactor attempt
- `plans/skills/cli-command.md` — CLI patterns skill

---

## Phase: IMPLEMENT

### Step-by-Step Actions

#### 1. Create Shared Infrastructure

```bash
# Create directory structure
mkdir -p impl/claude/protocols/cli/shared
mkdir -p impl/claude/protocols/cli/commands/soul
```

```python
# shared/context.py
@dataclass
class InvocationContext:
    """Shared context for all CLI commands."""
    session_id: str
    json_mode: bool = False
    stream_mode: bool = False
    pipe_mode: bool = False
    quiet: bool = False

    @classmethod
    def from_args(cls, args: list[str]) -> "InvocationContext": ...
```

```python
# shared/output.py
class OutputFormatter:
    """Unified output formatting."""
    ...
```

```python
# shared/streaming.py
class StreamingHandler:
    """Unified streaming for all commands."""
    ...
```

#### 2. Extract First Command (reflect.py)

```python
# commands/soul/reflect.py
"""Soul Reflect command - mirror back what you hear."""

from cli.shared.context import InvocationContext
from cli.shared.output import OutputFormatter
from cli.shared.streaming import StreamingHandler

async def execute(
    prompt: str,
    ctx: InvocationContext,
    output: OutputFormatter,
) -> int:
    """Execute soul reflect."""
    from agents.k import KgentSoul, DialogueMode, BudgetTier

    soul = KgentSoul()

    if ctx.stream_mode or ctx.pipe_mode:
        handler = StreamingHandler(output)
        return await handler.stream_flux(
            soul.dialogue_flux(prompt, mode=DialogueMode.REFLECT)
        )

    response = await soul.dialogue(prompt, mode=DialogueMode.REFLECT)
    output.emit(response.text, {"response": response.text})
    return 0
```

#### 3. Create Router

```python
# commands/soul/__init__.py
"""Soul commands - K-gent dialogue interface."""

from . import reflect, challenge, advise, explore, vibe, status

SUBCOMMANDS = {
    "reflect": reflect,
    "challenge": challenge,
    "advise": advise,
    "explore": explore,
    "vibe": vibe,
    "status": status,
}

def route(subcommand: str, args: list[str], ctx: InvocationContext) -> int:
    """Route to appropriate subcommand."""
    handler = SUBCOMMANDS.get(subcommand)
    if handler is None:
        return error(f"Unknown subcommand: {subcommand}")
    return asyncio.run(handler.execute(args, ctx))
```

#### 4. Test After Each Extraction

```bash
# After each file extraction:
pytest impl/claude/protocols/cli/handlers/_tests/test_soul.py -v
kgents soul reflect "test" --stream
echo "test" | kgents soul --pipe reflect | jq .
```

---

## Phase: QA

### Checklist

- [ ] `mypy impl/claude/protocols/cli/` passes
- [ ] `ruff check impl/claude/protocols/cli/` passes
- [ ] No security issues in new code
- [ ] No hardcoded paths or secrets

### Commands

```bash
cd impl/claude && uv run mypy protocols/cli/
cd impl/claude && uv run ruff check protocols/cli/
```

---

## Phase: TEST

### Test Coverage

| Test | Purpose |
|------|---------|
| `test_soul_reflect.py` | Unit tests for reflect command |
| `test_streaming.py` | StreamingHandler unit tests |
| `test_pipe_composition.py` | End-to-end pipe tests |
| `test_regression.py` | All existing commands still work |

### Integration Tests

```python
async def test_pipe_composition():
    """Test that piped commands compose correctly."""
    result = subprocess.run(
        'echo "What am I avoiding?" | kgents soul --pipe reflect | kgents soul --pipe challenge',
        shell=True,
        capture_output=True,
    )
    assert result.returncode == 0
    # Verify output is valid NDJSON
    for line in result.stdout.decode().strip().split('\n'):
        json.loads(line)
```

---

## Phase: EDUCATE

### Documentation Updates

1. **CLI Help Text** — Update with new command structure
2. **plans/skills/cli-command.md** — Update with new patterns
3. **README in cli/commands/** — Document structure

### Usage Notes

```bash
# New command structure (same behavior):
kgents soul reflect "What am I avoiding?"
kgents soul --stream reflect "What am I avoiding?"
echo "What am I avoiding?" | kgents soul --pipe reflect

# Composition:
kgents soul reflect "problem" | kgents soul challenge | kgents soul advise
```

---

## Phase: MEASURE

### Metrics to Track

| Metric | Before | Target | Owner |
|--------|--------|--------|-------|
| soul.py lines | 2019 | < 300 | This work |
| Total CLI lines | 17,967 | < 8,000 | This work |
| Largest file | 2019 | < 300 | This work |
| Test count | ~100 | +50 | This work |

### Dashboard Hook

After refactor, update `_status.md`:

```markdown
## CLI Unification — X% Complete

| Component | Status | Lines |
|-----------|--------|-------|
| Shared infrastructure | ✅ | ~200 |
| Soul commands | 🚧 | ~X |
| Agent commands | 📋 | ~Y |
```

---

## Phase: REFLECT

### Expected Learnings

1. **Extraction patterns** — Which patterns work for CLI refactoring?
2. **Streaming unification** — One impl for all commands
3. **Test strategies** — How to test CLI without LLM calls
4. **Composition** — Do commands actually compose well?

### Next-Loop Seeds

1. **Agent commands** — Apply same pattern to a_gent.py
2. **Infra consolidation** — Merge infra, daemon, telemetry
3. **Flow engine** — Build on unified pipes
4. **MCP integration** — Commands as MCP tools

---

## Auto-Continuation

On completion:

```
⟿[REFLECT]
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification; phase=REFLECT; ledger={PLAN:✓,...,IMPLEMENT:✓}; entropy=0.02
mission: Capture learnings from CLI unification.
actions:
  - Write epilogue to plans/_epilogues/
  - Update _status.md
  - Generate next-loop prompt
exit: Epilogue written; next work identified.
```

---

## Halt Conditions

- `⟂[BLOCKED:test_failure]` — Tests broken, needs fix
- `⟂[BLOCKED:regression]` — Command stopped working
- `⟂[BLOCKED:circular_import]` — Extraction created import cycle
- `⟂[ENTROPY_DEPLETED]` — Over budget, need to compress
- `⟂[DETACH:phase_complete]` — Soul refactor done, ready for next phase

---

*"The CLI is a functor from Intent to Action. Make the mapping lawful."*
