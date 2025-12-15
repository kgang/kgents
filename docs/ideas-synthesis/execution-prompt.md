---
path: ideas/impl/execution-prompt
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Enhanced execution prompt for parallel agent implementation.
  Incorporates DevEx awareness and categorical meta-construction.
  Two tracks: Legacy (CLI-first) and Generative (Spec-first).
---

# Enhanced Execution Prompt: Meta-Construction Implementation

You are implementing the kgents meta-construction system. Your goal is to shift from **enumerated ideas** to **generative machinery** while maintaining backward compatibility with existing DevEx infrastructure.

---

## Source Documents (Read These First)

### Categorical Foundation
- `plans/ideas/impl/categorical-critique.md` - Analysis of what's missing
- `plans/ideas/impl/meta-construction.md` - The generative solution
- `docs/categorical-foundations.md` - Existing categorical basis

### Legacy Implementation Plans
- `plans/ideas/impl/master-plan.md` - 11-phase lifecycle
- `plans/ideas/impl/quick-wins.md` - 70+ CLI commands
- `plans/ideas/impl/crown-jewels.md` - 45+ top ideas
- `plans/ideas/impl/cross-synergy.md` - Agent combinations

### DevEx Infrastructure (Already Working)
- `impl/claude/protocols/cli/devex/` - Ghost, Flinch, HYDRATE
- `impl/claude/infra/ghost/` - Daemon, collectors, health
- `impl/claude/protocols/cli/handlers/ghost.py` - `kgents ghost`
- `impl/claude/protocols/cli/handlers/flinch.py` - `kgents flinch`

---

## Two Implementation Tracks

### Track A: Legacy (CLI-First) — Parallel with Track B

Continue implementing the 70+ quick wins and crown jewels as CLI commands.
This provides immediate value while Track B builds the generative foundation.

```
Sprint 1-2: K-gent Soul CLI
  - kg soul vibe, kg soul drift, kg soul shadow
  - Wire to existing eigenvector infrastructure

Sprint 3-4: Infrastructure CLI
  - kg parse, kg reality, kg analyze
  - Wire to P-gent, J-gent

Sprint 5-6: Cross-Pollination
  - kg approve ("Would Kent Approve?")
  - kg introspect (K + H pipeline)
```

### Track B: Generative (Spec-First) — The Meta-Construction

Build the machinery that generates agents, not agents themselves.

```
Phase 1: Polynomial Primitives
  - Convert Agent[A,B] to PolyAgent[S,A,B]
  - Add positions, directions, transitions
  - File: impl/claude/agents/poly/

Phase 2: Universal Operad
  - Define Operad dataclass
  - Implement seq, par, branch, fix, trace
  - File: impl/claude/agents/operad/

Phase 3: Domain Operads
  - SOUL_OPERAD, PARSE_OPERAD, REALITY_OPERAD
  - Auto-generate CLI from operads
  - File: impl/claude/agents/operad/domains/

Phase 4: Sheaf Emergence
  - AgentSheaf with restrict/glue
  - SOUL_SHEAF over eigenvectors
  - File: impl/claude/agents/sheaf/
```

---

## DevEx Integration Points

### Ghost Sensorium (Use This)

Project meta-construction health to `.kgents/ghost/`:

```python
# Extend ghost daemon with meta collector
class MetaGhostCollector(GhostCollector):
    async def collect(self) -> CollectorResult:
        return CollectorResult(
            success=True,
            data={
                "primitives": len(PRIMITIVES),
                "operads": list(OPERAD_REGISTRY),
                "compositions_generated": composition_count,
            }
        )
```

### Flinch System (Wire Test Failures)

All operad law violations should register as flinches:

```python
# When operad law fails
flinch_store.record(FlinchRecord(
    nodeid="operad::associativity",
    error_type="LawViolation",
    message="seq(seq(a,b),c) ≠ seq(a,seq(b,c))"
))
```

### HYDRATE Signals (Track Progress)

```python
append_hydrate_signal(HydrateEvent.CUSTOM, "Phase 2: Operad complete, 5 ops defined")
append_hydrate_signal(HydrateEvent.TEST_RUN, "Operad laws: 12 passed, 0 failed")
```

---

## Parallel Agent Strategy

### Agent 1: Polynomial Foundation

```
Focus: impl/claude/agents/poly/
Tasks:
  - PolyAgent protocol (positions, directions, transitions)
  - Convert 7 bootstrap agents
  - Wiring diagram composition
Tests: Type I (unit) + Type II (property laws)
```

### Agent 2: Operad Infrastructure

```
Focus: impl/claude/agents/operad/
Tasks:
  - Operad dataclass
  - Universal operations (seq, par, branch, fix, trace)
  - Law verification at runtime
Tests: Type I + Type V (dialectic for laws)
```

### Agent 3: Domain Operads + CLI Generation

```
Focus: impl/claude/agents/operad/domains/
Tasks:
  - SOUL_OPERAD, PARSE_OPERAD, REALITY_OPERAD
  - CLIAlgebra functor
  - Auto-register handlers from operad
Tests: Type III (integration)
```

### Agent 4: Sheaf Emergence

```
Focus: impl/claude/agents/sheaf/
Tasks:
  - AgentSheaf protocol
  - SOUL_SHEAF over eigenvector contexts
  - Gluing verification
Tests: Type I + emergence verification
```

### Agent 5: DevEx + Ghost Integration

```
Focus: impl/claude/infra/ghost/
Tasks:
  - MetaGhostCollector
  - Operad health projection
  - Flinch integration for law violations
Tests: Type III (integration with daemon)
```

---

## Key Implementation Patterns

### Pattern 1: Polynomial Agent

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    name: str
    positions: FrozenSet[S]
    directions: Callable[[S], FrozenSet[A]]
    transition: Callable[[S, A], tuple[S, B]]

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        assert state in self.positions
        assert input in self.directions(state)
        return self.transition(state, input)
```

### Pattern 2: Operad Definition

```python
@dataclass
class Operad:
    name: str
    operations: dict[str, Operation]
    laws: list[str]

    def compose(self, op: str, *agents) -> PolyAgent:
        return self.operations[op].compose(*agents)

    def verify_laws(self) -> bool:
        # Runtime law verification
        ...
```

### Pattern 3: CLI from Operad

```python
class CLIAlgebra:
    def __init__(self, operad: Operad):
        self.operad = operad

    def to_cli(self, op_name: str) -> CLIHandler:
        # Automatic handler generation
        ...

    def register_all(self, cli: CLI) -> None:
        for op in self.operad.operations:
            cli.register(f"kg {self.operad.name} {op}", self.to_cli(op))
```

### Pattern 4: Sheaf Gluing

```python
class AgentSheaf:
    def restrict(self, agent: PolyAgent, ctx: Context) -> PolyAgent:
        # Restrict to subcontext
        ...

    def glue(self, locals: dict[Context, PolyAgent]) -> PolyAgent:
        # Verify compatibility, then glue
        assert self.compatible(locals)
        return self._glue_impl(locals)
```

---

## Testing Strategy

### Operad Law Tests (Type V - Dialectic)

```python
@pytest.mark.parametrize("a,b,c", agent_triples)
def test_associativity(a, b, c):
    """seq(seq(a,b),c) = seq(a,seq(b,c))"""
    left = operad.compose("seq", operad.compose("seq", a, b), c)
    right = operad.compose("seq", a, operad.compose("seq", b, c))
    assert agents_equivalent(left, right)

def test_identity():
    """seq(id, a) = a = seq(a, id)"""
    for a in primitives:
        assert agents_equivalent(operad.compose("seq", ID, a), a)
        assert agents_equivalent(operad.compose("seq", a, ID), a)
```

### Sheaf Gluing Tests

```python
def test_compatible_gluing():
    """Compatible local agents glue successfully."""
    locals = {ctx: restrict(soul, ctx) for ctx in contexts}
    global_soul = sheaf.glue(locals)
    assert global_soul is not None

def test_incompatible_rejection():
    """Incompatible local agents fail to glue."""
    incompatible = {"ctx1": agent_a, "ctx2": agent_b}  # Disagree on overlap
    with pytest.raises(GluingError):
        sheaf.glue(incompatible)
```

---

## Success Criteria

| Criterion | Target | Verification |
|-----------|--------|--------------|
| Polynomial primitives | 13+ agents converted | Unit tests |
| Universal operad | 5 operations (seq, par, branch, fix, trace) | Law tests |
| Domain operads | 3+ (Soul, Parse, Reality) | Integration tests |
| CLI auto-generation | 10+ handlers from operad | E2E tests |
| Sheaf emergence | Soul emergence working | Gluing tests |
| DevEx integration | Ghost projects operad health | Daemon test |
| Chaos composition | 100+ valid random agents | Property tests |

---

## File Structure After Implementation

```
impl/claude/agents/
├── poly/
│   ├── __init__.py
│   ├── protocol.py        # PolyAgent definition
│   ├── primitives.py      # 13 polynomial primitives
│   ├── wiring.py          # Wiring diagram composition
│   └── _tests/
│
├── operad/
│   ├── __init__.py
│   ├── core.py            # Operad, Operation dataclasses
│   ├── universal.py       # AGENT_OPERAD
│   ├── algebra.py         # CLIAlgebra functor
│   ├── domains/
│   │   ├── soul.py        # SOUL_OPERAD
│   │   ├── parse.py       # PARSE_OPERAD
│   │   └── reality.py     # REALITY_OPERAD
│   └── _tests/
│       ├── test_laws.py   # Operad law verification
│       └── test_algebra.py
│
├── sheaf/
│   ├── __init__.py
│   ├── protocol.py        # AgentSheaf definition
│   ├── soul_sheaf.py      # SOUL_SHEAF
│   └── _tests/
│       └── test_emergence.py
│
└── existing agents (k/, h/, u/, p/, etc.)
```

---

## The Fundamental Shift

**Before**: 600 ideas → implement each → 600 CLI commands
**After**: Operad + Primitives → generate → ∞ valid compositions

The operad guarantees validity.
The sheaf enables emergence.
The void.* provides chaos.

Careful design OR chaotic happenstance → valid agents.

---

## Commands to Verify Progress

```bash
# Check polynomial primitives
uv run pytest impl/claude/agents/poly/_tests/ -v

# Check operad laws
uv run pytest impl/claude/agents/operad/_tests/test_laws.py -v

# Check sheaf emergence
uv run pytest impl/claude/agents/sheaf/_tests/test_emergence.py -v

# Check auto-generated CLI
kg soul introspect  # Should work from operad

# Check ghost projection
kgents ghost --show  # Should include meta.json

# Full test suite
uv run pytest --cov=impl --cov-report=html
```

---

*"Build the grammar, not the sentences."*
