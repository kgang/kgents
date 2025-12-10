# impl/claude HYDRATE

**Last Updated:** 2025-12-09 (B×G Phase 2 - Fiscal Constitution)

## Quick Start

```bash
cd impl/claude
source .venv/bin/activate
python evolve.py status           # Check evolution state
python evolve.py suggest          # Bootstrap-enhanced suggestions
python -m pytest tests/ -v        # Run tests
python demo_igents.py             # Demo I-gents fractal visualization
```

---

## Architecture Overview

```
impl/claude/
├── bootstrap/          # 7 irreducible agents (spec/bootstrap.md)
│   ├── types.py        # Core types: Agent, Result, VerdictType
│   ├── id.py           # Identity morphism
│   ├── compose.py      # f >> g composition
│   ├── ground.py       # Void → Facts (persona, world)
│   ├── contradict.py   # (A,B) → Tension
│   ├── sublate.py      # Tension → Synthesis|Hold
│   ├── judge.py        # Agent → Verdict (7 principles)
│   └── fix.py          # Fixed-point iteration with entropy
│
├── runtime/            # Execution infrastructure
│   ├── base.py         # LLMAgent, AgentContext, Result
│   ├── claude.py       # Anthropic API runtime
│   ├── openrouter.py   # Multi-model runtime
│   └── json_utils.py   # Robust JSON parsing (H5 ✅)
│
├── agents/             # Agent implementations by genus
│   ├── a/              # Abstract (meta-schemas)
│   ├── b/              # Bio/Scientific (robin, hypothesis)
│   ├── c/              # Category (functor, conditional)
│   ├── d/              # Data (volatile, persistent, lens)
│   ├── e/              # Evolution (safety, parser, prompts)
│   ├── f/              # Forge (artifact synthesis)
│   ├── h/              # Hegelian (hegel, jung, lacan)
│   ├── i/              # Interface (garden, renderers, export) ✨NEW
│   ├── j/              # JIT (jgent, chaosmonger, sandbox)
│   ├── k/              # Kent simulacra
│   ├── l/              # Library (catalog, search)
│   ├── t/              # Testing (mock, spy, failing)
│   └── w/              # Wire (observation, fidelity, server) ✨NEW
│
├── evolve.py           # Meta-evolution CLI (1,286 lines)
└── IMPROVEMENT_PLAN.md # Systematic refactoring roadmap
```

---

## Key Files by Purpose

### Bootstrap Agents
| File | Lines | Purpose |
|------|-------|---------|
| `bootstrap/types.py` | 511 | Core Agent protocol, Result types |
| `bootstrap/judge.py` | 420 | Evaluate against 7 principles |
| `bootstrap/contradict.py` | 360 | Detect contradictions |
| `bootstrap/sublate.py` | 337 | Hegelian synthesis |
| `bootstrap/fix.py` | 303 | Convergence iteration |

### Evolution Pipeline
| File | Lines | Purpose |
|------|-------|---------|
| `evolve.py` | 1,286 | CLI + EvolutionPipeline orchestration |
| `agents/e/safety.py` | 656 | Safe self-evolution with rollback |
| `agents/e/parser.py` | 687 | Multi-strategy code extraction |
| `agents/e/prompts.py` | 762 | Improvement prompt templates |

### JIT Compilation
| File | Lines | Purpose |
|------|-------|---------|
| `agents/j/jgent.py` | 450 | JIT agent compilation |
| `agents/j/sandbox.py` | 460 | Secure code execution |
| `agents/j/chaosmonger.py` | 620 | Stability analysis |
| `agents/j/meta_architect.py` | 607 | Agent generation |

### I-gents (Interface)
| File | Lines | Purpose |
|------|-------|---------|
| `agents/i/types.py` | 250 | Phase, Glyph, Scale, AgentState, GardenState |
| `agents/i/renderers.py` | 350 | ASCII renderers (Card, Page, Garden, Library) |
| `agents/i/export.py` | 200 | Markdown/Mermaid serialization |
| `agents/i/breath.py` | 120 | Contemplative breath cycle animation |
| `agents/i/observe.py` | 200 | W-gent integration ([observe] action) |

### W-gents (Wire)
| File | Lines | Purpose |
|------|-------|---------|
| `agents/w/protocol.py` | 300 | WireObservable mixin, WireState, WireEvent |
| `agents/w/fidelity.py` | 400 | Teletype, Documentarian, LiveWire adapters |
| `agents/w/server.py` | 200 | FastAPI server with SSE for live observation |

---

## Bootstrap Self-Improvement Patterns

The bootstrap agents enable **direct self-improvement** without external coordination:

### 1. Judge → Quality Gate
```python
from bootstrap import Judge, JudgeInput
verdict = await Judge().invoke(JudgeInput(agent=any_agent))
# Returns: ACCEPT | REVISE | REJECT with reasoning
```

### 2. Contradict + Sublate → Conflict Resolution
```python
from agents.h.hegel import HegelAgent
result = await HegelAgent().invoke(DialecticInput(thesis=old, antithesis=new))
# Returns: Synthesis or productive tension to hold
```

### 3. Fix → Convergence Iteration
```python
from bootstrap import Fix, FixConfig
fix = Fix(FixConfig(max_iterations=10, entropy_budget=1.0))
result = await fix.invoke((improve_fn, initial_state))
```

### 4. Ground → Context Injection
```python
from bootstrap import Ground, VOID
facts = await Ground().invoke(VOID)
# facts.persona: Kent's values | facts.world: current context
```

### 5. I-gent → Ecosystem Visualization
```python
from agents.i import Phase, AgentState, GardenRenderer, BreathCycle

state = AgentState(agent_id="robin", phase=Phase.ACTIVE, birth_time=datetime.now())
state.joy = 0.9
state.ethics = 0.85

garden = GardenState(name="research", session_start=datetime.now())
garden.add_agent(state)
print(GardenRenderer(garden).render())
# ASCII zen garden with moon phase glyphs
```

### 6. W-gent → Process Observation
```python
from agents.w import WireObservable, WireServer

class MyAgent(WireObservable):
    def __init__(self):
        super().__init__("my-agent")

    async def run(self):
        self.update_state(phase="active", progress=0.5)
        self.log_event("INFO", "work", "Processing...")

# Start observation server (opens browser at localhost:8000)
server = WireServer("my-agent", port=8000)
await server.start()
```

---

## Recent Commits

| Commit | Description |
|--------|-------------|
| `4b02086` | feat(i-gents): Living Codex Garden spec |
| `294b068` | fix(evolve): Expand builtins in preflight |
| `ea7c2a5` | feat(cross-poll): Phase C validation |
| `4d883d2` | refactor(impl): Evolution bug fixes |
| `0001386` | feat(f-gents): Sandbox with self-healing |

---

## Improvement Plan Status

See `IMPROVEMENT_PLAN.md` for full details.

### Completed
- [x] **H5**: JSON utilities → `runtime/json_utils.py`
- [x] Bootstrap integration in `evolve.py` (Judge, Fix, Contradict, Ground)

### Phase A: Quick Wins
- [ ] **H4**: Lazy imports in `evolve.py` (57 imports)
- [ ] **H2**: Extract SuggestionAgent (56 lines)

### Phase B: Core Refactoring
- [ ] **H1**: Decompose EvolutionPipeline (19 methods → 4 agents)
- [ ] **H7**: Split `prompts.py` (762 lines)
- [ ] **H10**: Split `sandbox.py` (460 lines)

### Key Targets
| Metric | Current | Target |
|--------|---------|--------|
| Files >500 lines | 18 | 10 |
| Functions >50 lines | 45+ | <20 |
| evolve.py lines | 1,286 | <800 |

---

## Testing

```bash
# Unit tests
python -m pytest tests/ -v

# Type checking
mypy --strict evolve.py

# Evolution self-test
python evolve.py test

# Safe meta-evolution (dry run)
python evolve.py meta --safe-mode --dry-run
```

---

## Spec ↔ Impl Mapping

| Spec | Impl |
|------|------|
| `spec/bootstrap.md` | `bootstrap/` |
| `spec/a-gents/` | `agents/a/` |
| `spec/b-gents/` | `agents/b/` (robin, hypothesis) |
| `spec/c-gents/` | `agents/c/` (functor, conditional) |
| `spec/d-gents/` | `agents/d/` (volatile, persistent) |
| `spec/e-gents/` | `agents/e/` + `evolve.py` |
| `spec/f-gents/` | `agents/f/` (forge, artifacts) |
| `spec/h-gents/` | `agents/h/` (hegel, jung, lacan) |
| `spec/i-gents/` | `agents/i/` (types, renderers, export, observe) ✨NEW |
| `spec/j-gents/` | `agents/j/` (jgent, sandbox) |
| `spec/k-gent/` | `agents/k/` |
| `spec/l-gents/` | `agents/l/` (catalog, search) |
| `spec/t-gents/` | `agents/t/` (mock, spy, failing) |
| `spec/w-gents/` | `agents/w/` (protocol, fidelity, server) ✨NEW |

---

## Recent Work

### I-gent & W-gent Spec Enhancement (2025-12-08) ✅

**Objective**: Create production-ready, batteries-included specs for I-gents (Living Codex Garden) and W-gents (Wire Observation) with deep bootstrap agent integration.

**I-gents Enhancements** (~600 lines added to `spec/i-gents/README.md`):
- **Bootstrap Integration**: Specialized visualizations for Ground, Judge, Contradict, Sublate, Fix
  - Ground: Persona + world facts as margin notes
  - Judge: Live 7-principles scorecard with real-time evaluation
  - Sublate: Synthesis decision tree (Preserve/Negate/Elevate strategies)
  - Fix: Convergence progress + entropy budget tracking
  - Contradict: Tension detection with polarity indicators

- **Cross-Genus Workflows**: Custom dashboards for E/F/H/D/L-gents
  - E-gent: Evolution pipeline progress (Ground → Hypothesize → Memory → Experiment → Validate)
  - F-gent: Forge phase indicators (Intent → Contract → Prototype → Validate → Crystallize)
  - H-gent: Dialectic synthesis with tension markers
  - D-gent: State timeline + history playback
  - L-gent: Catalog browsing + relationship graphs

- **evolve.py Integration**:
  - `kgents evolve --garden` flag for live evolution visualization
  - Real-time bootstrap agent orchestration
  - Pipeline progress tracking

- **CLI & Session Management**:
  - Commands: `kgents garden`, `kgents garden attach session-id`, `kgents garden export`
  - Keyboard shortcuts (TUI): o=observe, s=snapshot, h=history, r=replay
  - Persistent sessions: `.garden.json` format with resume capability
  - Hook system: `.garden-hooks.py` for extensibility

- **Integration Checklist**: 14 production requirements

**W-gents Specification** (~265 lines, new file `spec/w-gents/README.md`):
- **Philosophy**: Three virtues (Transparency, Ephemerality, Non-Intrusion)
- **WireObservable Mixin**: Zero-overhead pattern - any agent becomes observable
- **Three Fidelity Levels**:
  - Teletype (raw): <1ms latency, plain text for CI/logs
  - Documentarian (rendered): <50ms latency, box-drawing for SSH/terminal
  - LiveWire (dashboard): <100ms latency, web UI with graphs for debugging

- **I-gent Integration**: `[observe]` action in garden spawns W-gent server
  - Pattern: I-gent (ecosystem view) → W-gent (agent view)
  - Navigate: Use I-gent to choose agent, W-gent to drill down

- **CLI Integration**:
  - `kgents wire attach robin` - Spawn observation server
  - `kgents wire detach robin` - Stop observation
  - `kgents wire list` - Active observers
  - `kgents wire export robin --format json` - Export trace
  - `kgents wire replay trace.json` - Replay saved trace

- **Bootstrap Dashboards**: Custom UI for Ground/Judge/Contradict/Sublate/Fix
- **evolve.py Integration**: `--wire` flag for performance profiling during evolution
- **Real-World Example**: Debugging slow hypothesis generation with latency breakdown

**Demo Implementation** (`demo_igents.py` ~208 lines):
- All four fractal scales: Glyph → Card → Page → Garden
- Moon phase indicators: ○ dormant, ◐ waking, ● active, ◑ waning, ◌ empty
- Joy/ethics metrics visualization
- Margin notes for composition metadata
- Garden ecosystem with 12 agents (Bootstrap + Genus)
- Breath cycle aesthetic
- Successfully runs and displays all visualizations

**Files Modified**:
- `spec/i-gents/README.md`: +~600 lines
- `spec/w-gents/README.md`: New file, ~265 lines
- `demo_igents.py`: New file, ~208 lines
- `agents/i/`: Directory created with implementation stubs
- `HYDRATE.md`, `impl/claude/HYDRATE.md`: Session documentation

**Status**: ✅ Complete - Ready for commit or implementation

**Next Steps**:
1. **Commit**: Capture spec enhancements
2. **Implement**: Begin I-gent core (types, renderers, breath cycle)
3. **Implement**: Begin W-gent core (WireObservable, fidelity, server)

---

### CLI Phase 3: Flow Engine (2025-12-09) ✅

**Objective**: Implement the Flowfile engine from `docs/cli-integration-plan.md` Part 4 - the composition backbone for agent pipelines.

**Implementation** (5 new files, ~1,800 lines):

- **`protocols/cli/flow/types.py`** (~350 lines):
  - FlowStep: id, genus, operation, input, args, condition, on_error, debug
  - Flowfile: version, name, input/output schema, variables, steps, hooks, on_error
  - FlowResult/StepResult: execution status, timing, snapshots
  - FlowStatus/StepStatus enums: PENDING/RUNNING/COMPLETED/FAILED/SKIPPED
  - Error types: FlowValidationError, FlowExecutionError

- **`protocols/cli/flow/parser.py`** (~400 lines):
  - YAML parsing with PyYAML
  - Jinja2-compatible template rendering (regex-based, no dependency)
  - Variable expansion: `{{ var | default('value') }}`
  - Validation: step IDs, references, genera, error strategies
  - Dependency graph building with word-boundary matching
  - Topological sort with Kahn's algorithm
  - Visualization: ASCII pipeline diagrams
  - explain_flow(): human-readable flow descriptions

- **`protocols/cli/flow/engine.py`** (~400 lines):
  - FlowEngine: step execution, input passing, condition evaluation
  - Genus executors for P-gent, J-gent, G-gent, Bootstrap, W-gent, R-gent, L-gent, T-gent
  - Condition evaluation: `step.field == 'value'`, `not step.success`
  - Debug snapshots: saved to `.kgents/debug/`
  - Pre/post hooks: shell command execution
  - Error handling: halt, continue, retry strategies
  - execute_flow() convenience function

- **`protocols/cli/flow/commands.py`** (~350 lines):
  - `flow run <file> [input]`: Execute flowfile with progress output
  - `flow validate <file>`: Check syntax and references
  - `flow explain <file>`: Human-readable explanation
  - `flow visualize <file>`: ASCII graph
  - `flow new "<intent>"`: Generate flowfile from natural language
  - `flow list`: List saved flows in `.kgents/flows/`
  - `flow save <file> --name=<id>`: Save to registry
  - Rich terminal output with box-drawing characters

- **`protocols/cli/flow/_tests/test_flow.py`** (~600 lines):
  - 47 tests covering types, parsing, validation, engine, visualization
  - All tests passing (2 skipped for optional PyYAML)

**Key Design Decisions**:
1. **No Jinja2 dependency**: Simple regex rendering for `{{ var | default('value') }}`
2. **Word-boundary matching**: Dependency detection uses `\bstep_id\.` to avoid false positives
3. **Set-based dependencies**: Deduplicated to avoid topological sort issues
4. **Lazy loading**: Flow module only imported when `kgents flow` invoked

**CLI Integration**:
- hollow.py already has: `"flow": "protocols.cli.flow.commands:cmd_flow"`
- Help text updated with Flow Engine section

**Example Usage**:
```yaml
# review.yaml
version: "1.0"
name: "Code Review Pipeline"
input:
  type: file
  extensions: [.py, .js]
variables:
  strictness: "{{ strictness | default('high') }}"
steps:
  - id: parse
    genus: P-gent
    operation: extract
  - id: judge
    genus: Bootstrap
    operation: judge
    input: "from:parse"
    args:
      strictness: "{{ strictness }}"
  - id: refine
    genus: R-gent
    operation: optimize
    input: "from:judge"
    condition: "judge.verdict != 'APPROVED'"
```

```bash
kgents flow run review.yaml src/main.py --var strictness=medium
kgents flow explain review.yaml
```

**Status**: ✅ Complete - Ready for Phases 4+ (MCP Protocol, Intent Router, etc.)

**Next CLI Phases**:
- Phase 4: MCP Protocol server (`kgents mcp serve`)
- Phase 5: Intent Router (`kgents check`, `kgents think`)
- Phase 6: Genus Surface (`kgents grammar`, `kgents jit`)
- Phase 7: TUI Dashboard (`kgents dash`)

---

### B×G Phase 2: Fiscal Constitution (2025-12-09) ✅

**Objective**: Implement grammar-based financial safety where bankruptcy is grammatically impossible - not runtime validation, but structural impossibility.

**Implementation** (`agents/b/fiscal_constitution.py` ~900 lines):

**Core Insight**: Parse errors prevent illegal operations. If `parse(operation) → Success`, then `execute(operation)` is constitutionally sound.

**Key Components**:

1. **LedgerState** (~200 lines):
   - Multi-currency account management
   - Double-entry bookkeeping with transaction log
   - Supply invariant verification
   - Reserve/release operations for escrow patterns
   - `mint_initial()` only at setup (no minting after constitution active)

2. **LedgerTongueParser** (~250 lines):
   - Constitutional grammar with parse-time balance checking
   - Commands: TRANSFER, QUERY, RESERVE, RELEASE
   - Note: No MINT, DELETE, FORGE, DESTROY verbs exist in grammar
   - Insufficient funds → ParseError (not runtime error)
   - Double-spend prevention at parse time

3. **LedgerTongue** (~150 lines):
   - Complete tongue combining parsing + execution
   - `run()` method: parse → execute (guaranteed safe if parse succeeds)
   - Query support: balance, history, supply

4. **ConstitutionalBanker** (~200 lines):
   - Grammar-based enforcement with metering integration
   - `execute_sync()`: Synchronous execution for testing
   - `execute_financial_operation()`: Async with gas metering
   - `verify_constitution()`: Check all invariants hold

**Grammar Example**:
```
COMMAND ::= TRANSFER | QUERY | RESERVE | RELEASE

TRANSFER ::= "TRANSFER" <Amount> <Currency> "FROM" <Account> "TO" <Account> ["MEMO" <String>]
  WHERE Account(FROM).balance >= Amount  // Enforced at parse time

QUERY ::= "QUERY" ("BALANCE" "OF" <Account> "IN" <Currency>
                 | "HISTORY" "OF" <Account>
                 | "SUPPLY" "OF" <Currency>)

# Note: No MINT, DELETE, FORGE verbs exist
```

**Constitutional Invariants**:
1. **Total supply constant**: No money created or destroyed after initial mint
2. **No negative balances**: Transfer/reserve impossible if insufficient funds
3. **Double-entry**: Every transfer has matching debit and credit
4. **Atomic transactions**: Failed operations don't leave partial state

**Example Usage**:
```python
from agents.b import create_fiscal_constitution, LedgerTongue

# Create constitution with initial supply
banker = create_fiscal_constitution(
    initial_supply={"USD": 10000.0, "EUR": 5000.0},
    treasury_account="treasury"
)

# Constitutional execution
result = banker.execute_sync("TRANSFER 100 USD FROM treasury TO alice")
# → TransactionResult(success=True, type="CONSTITUTIONAL_EXECUTION")

# Attempt to overspend → ParseError (not runtime error!)
result = banker.execute_sync("TRANSFER 50000 USD FROM alice TO bob")
# → TransactionResult(success=False, type="GRAMMAR_REJECTION",
#                     reason="Constitutional violation: Insufficient funds...")

# Verify constitution holds
invariants = banker.verify_constitution()
# → {"supply_USD": True, "supply_EUR": True, "no_negative_balances": True, "double_entry": True}
```

**Tests** (`agents/b/_tests/test_fiscal_constitution.py` ~84 tests):
- AccountBalance, Account, LedgerState operations
- Parser syntax and constitutional balance checking
- Double-spend prevention at parse time
- LedgerTongue execution
- ConstitutionalBanker sync and async operations
- Edge cases and fuzz-like testing
- Constitutional invariant stress tests (500 random transfers)
- Integration tests (escrow workflow, multi-currency, audit trail)

**Success Criteria Met**:
- ✅ 0 runtime financial safety errors (caught at parse-time)
- ✅ No minting possible (MINT verb doesn't exist)
- ✅ No deletion possible (DELETE verb doesn't exist)
- ✅ Double-spend prevented at parse time
- ✅ Supply invariant maintained under stress testing

**Files Created/Modified**:
- `agents/b/fiscal_constitution.py`: New file, ~900 lines
- `agents/b/_tests/test_fiscal_constitution.py`: New file, ~84 tests
- `agents/b/__init__.py`: Updated exports

**Next B×G Phases**:
- Phase 3: Syntax Tax (Chomsky-based pricing)
- Phase 4: JIT Efficiency (G+J+B performance trio)
