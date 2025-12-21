# ASHC Phase 1: L0 Kernel (The Germline)

> *"The minimal interpreter exists only to bootstrap self-hosting. Then it gets out of the way."*

**Parent**: `plans/ashc-master.md`
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md` §L0 Kernel
**Phase**: ✅ COMPLETE
**Tests**: 47 passing

---

## Purpose

L0 is the **germline**—the smallest possible trusted base that interprets a data-first DSL. Operads, sheaves, and phase grammars are **data**, not code. L0 only knows how to evaluate this data.

**Constraint**: <1000 LOC. If L0 grows beyond this, the trusted base is broken.

---

## Type Signature

```python
@dataclass(frozen=True)
class L0Kernel:
    """
    Minimal interpreter in host language (Python/TS).

    L0 interprets a data-first DSL where operads, sheaves,
    and phase grammars are data, not code.
    """
    eval: Callable[[AST_L0], Runtime]
    primitives: frozenset[str]  # compose, apply, match, emit, witness

L0Kernel: AST_L0 -> Runtime
```

---

## The Five Primitives

| Primitive | Signature | Purpose |
|-----------|-----------|---------|
| `compose` | `(f, g) → f >> g` | Sequential composition |
| `apply` | `(f, x) → f(x)` | Function application |
| `match` | `(pattern, value) → bindings \| None` | Pattern matching |
| `emit` | `(artifact_type, content) → Artifact` | Output generation |
| `witness` | `(pass, input, output) → TraceWitness` | Proof capture |

These five are **irreducible**. Everything else derives from them.

---

## AST_L0 Grammar

```ebnf
program    := stmt*
stmt       := define | invoke | emit_stmt
define     := "define" IDENT "=" expr
invoke     := "invoke" path args
emit_stmt  := "emit" type content

expr       := literal | reference | composition | application | match_expr
literal    := STRING | NUMBER | LIST | DICT
reference  := IDENT
composition := expr ">>" expr
application := expr "(" args ")"
match_expr := "match" pattern "in" expr

path       := IDENT ("." IDENT)*
args       := (expr ("," expr)*)?
pattern    := literal | IDENT | "_" | pattern "," pattern
```

**Example L0 Program**:
```
define ground = invoke self.ground.manifest {}
define judged = ground >> invoke concept.principles.judge {}
emit IR judged
witness "ground_judge" ground judged
```

---

## Implementation Tasks

### Task 1: AST Types
**Checkpoint**: Types compile with mypy strict

```python
# impl/claude/protocols/ashc/ast.py

@dataclass(frozen=True)
class L0Program:
    statements: tuple[L0Statement, ...]

@dataclass(frozen=True)
class L0Define:
    name: str
    value: L0Expr

@dataclass(frozen=True)
class L0Invoke:
    path: str
    args: dict[str, L0Expr]

@dataclass(frozen=True)
class L0Emit:
    artifact_type: str
    content: L0Expr

# ... etc for full grammar
```

### Task 2: Lexer/Parser
**Checkpoint**: Parse example programs without error

```python
# impl/claude/protocols/ashc/parser.py

def parse_l0(source: str) -> L0Program:
    """Parse L0 source into AST."""
    # Simple recursive descent parser
    # No dependencies beyond stdlib
    ...
```

### Task 3: Evaluator
**Checkpoint**: `eval(parse("define x = 1")) → Runtime{x: 1}`

```python
# impl/claude/protocols/ashc/evaluator.py

@dataclass
class Runtime:
    """Execution state for L0 programs."""
    bindings: dict[str, Any]
    artifacts: list[Artifact]
    witnesses: list[TraceWitness]

async def eval_l0(
    program: L0Program,
    primitives: L0Primitives,
) -> Runtime:
    """Evaluate L0 program with given primitives."""
    runtime = Runtime({}, [], [])
    for stmt in program.statements:
        runtime = await eval_stmt(stmt, runtime, primitives)
    return runtime
```

### Task 4: Primitive Implementation
**Checkpoint**: Each primitive passes unit tests

```python
# impl/claude/protocols/ashc/primitives.py

@dataclass(frozen=True)
class L0Primitives:
    """The five irreducible operations."""

    async def compose(self, f: Agent, g: Agent) -> Agent:
        return f >> g

    async def apply(self, f: Agent, x: Any) -> Any:
        return await f.invoke(x)

    def match(self, pattern: Pattern, value: Any) -> dict | None:
        # Pattern matching logic
        ...

    async def emit(self, artifact_type: str, content: Any) -> Artifact:
        return Artifact(type=artifact_type, content=content, timestamp=now())

    def witness(
        self,
        pass_name: str,
        input_data: Any,
        output_data: Any
    ) -> TraceWitness:
        return TraceWitness(
            pass_name=pass_name,
            input_data=input_data,
            output_data=output_data,
            timestamp=now(),
        )
```

### Task 5: AGENTESE Integration
**Checkpoint**: `invoke self.x.y` resolves via Logos

```python
# Integration with existing Logos

async def resolve_path(path: str, args: dict) -> Any:
    """Resolve AGENTESE path in L0 context."""
    from protocols.agentese.gateway import logos
    umwelt = create_l0_umwelt()
    return await logos.invoke(path, umwelt, **args)
```

---

## File Structure

```
impl/claude/protocols/ashc/
├── __init__.py
├── ast.py              # AST types (Task 1)
├── parser.py           # Lexer/Parser (Task 2)
├── evaluator.py        # Core eval loop (Task 3)
├── primitives.py       # 5 primitives (Task 4)
├── runtime.py          # Runtime state
├── _tests/
│   ├── test_ast.py
│   ├── test_parser.py
│   ├── test_evaluator.py
│   └── test_primitives.py
└── examples/
    ├── minimal.l0      # define x = 1
    ├── compose.l0      # f >> g
    └── bootstrap.l0    # Compile bootstrap from spec
```

---

## Quality Checkpoints

| Checkpoint | Command | Expected |
|------------|---------|----------|
| AST Types | `uv run mypy protocols/ashc/ast.py` | 0 errors |
| Parser | `uv run pytest protocols/ashc/_tests/test_parser.py` | PASS |
| Eval Minimal | `uv run python -c "..."` | Runtime with binding |
| Primitives | `uv run pytest protocols/ashc/_tests/test_primitives.py` | PASS |
| Full Smoke | `kg concept.compiler.kernel.status` | OPERATIONAL |

---

## User Flows

### Flow: Check Kernel Status

```bash
$ kg concept.compiler.manifest

┌─ ASHC KERNEL ─────────────────────────────────────────┐
│ Status:    OPERATIONAL                                 │
│ Version:   0.1.0                                       │
│ Primitives: compose, apply, match, emit, witness      │
│ LOC:       487 / 1000 (48% of budget)                 │
└────────────────────────────────────────────────────────┘
```

### Flow: Parse and Eval

```bash
$ kg concept.compiler.eval "define x = 1; emit JSON x"

Parsing...    ✓
Evaluating... ✓
Artifacts:
  1. JSON: 1

Witnesses:
  (none - no passes invoked)
```

---

## UI/UX Considerations

### Terminal Output

1. **Minimal noise**: L0 is low-level; output should be sparse
2. **LOC budget visible**: Always show remaining budget
3. **Witness count**: Surface how many proofs captured

### Error Messages

Warm, sympathetic, per Verification Tower aesthetic:

```
┌─ L0 PARSE ERROR ───────────────────────────────────────┐
│ I found something unexpected at line 3, column 12:     │
│                                                        │
│   define x = invoke self.ground.manifest               │
│                    ^^^ missing "{}" after path         │
│                                                        │
│ Suggestion: Add empty args: invoke self.ground.manifest {} │
└────────────────────────────────────────────────────────┘
```

---

## Laws/Invariants

### LOC Budget Law
```
LOC(L0) < 1000
```
Enforced by CI. If this fails, the trusted base is compromised.

### Primitive Closure
```
∀ operation O in L0: O ∈ {compose, apply, match, emit, witness}
```
Any new "primitive" must derive from these five.

### Witness Completeness
```
∀ pass P: witness(P, input, output) emitted
```
Every pass must emit a witness. Silent passes are invalid.

---

## Integration Points

| System | Integration |
|--------|-------------|
| **AGENTESE** | `invoke` resolves via `logos.invoke()` |
| **Bootstrap** | `BootstrapWitness.verify_*` called via L0 |
| **Verification** | `TraceWitness` structure matches existing |
| **N-Phase** | L0 programs can express phase sequences |

---

## Flexibility

| Fixed | Flexible |
|-------|----------|
| 5 primitives | Composition into higher-order ops |
| <1000 LOC | Exact line count |
| AST structure | Syntax sugar for common patterns |
| Python host | TypeScript port for web |

---

## Testing Strategy

### Unit Tests (per task)
- `test_ast.py`: Type construction, equality
- `test_parser.py`: Parse → AST for each grammar rule
- `test_evaluator.py`: Eval → Runtime state
- `test_primitives.py`: Each primitive in isolation

### Property Tests
```python
@given(st.from_type(L0Program))
def test_parse_unparse_roundtrip(program):
    """Parse(unparse(program)) ≡ program."""
    source = unparse(program)
    reparsed = parse_l0(source)
    assert reparsed == program
```

### Integration Tests
- `test_bootstrap_compile.l0`: Compile minimal bootstrap agent
- `test_agentese_invoke.l0`: Invoke real AGENTESE path

---

## Success Criteria

✅ L0 parses and evaluates example programs
✅ LOC budget < 1000
✅ All 5 primitives implemented
✅ AGENTESE paths resolve correctly
✅ TraceWitness emission works
✅ `kg concept.compiler.kernel.status` shows OPERATIONAL

---

## Next Phase

After L0 Kernel: `plans/ashc-pass-operad.md` (Pass Operad)

---

*"The germline is the seed. It must be small enough to fit in a single mind."*
