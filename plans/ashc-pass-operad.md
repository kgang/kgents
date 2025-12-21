# ASHC Phase 2: Pass Operad (Categorical Transform Engine)

> *"Passes are morphisms. The compiler is a category."*

**Parent**: `plans/ashc-master.md`
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md` §Passes as Agents
**Phase**: ✅ COMPLETE
**Tests**: Included in Phase 1 (47 total L0 + Pass tests)

---

## Purpose

The Categorical Transform Engine treats compiler passes as morphisms in a category. The Pass Operad defines which pass sequences are valid. This enables:

1. **Composability**: Passes compose via `>>`
2. **Law Verification**: Identity and associativity are checked, not assumed
3. **Bootstrap Integration**: The 7 bootstrap agents become the canonical passes

---

## Core Insight

**The compiler is an agent whose irreducible passes are the bootstrap agents.**

| Bootstrap Agent | Compiler Pass Role |
|-----------------|-------------------|
| **Id** | Identity pass (no-op) |
| **Compose** | Pass composition operator |
| **Judge** | Validation/acceptance pass |
| **Ground** | Empirical data injection pass |
| **Contradict** | Inconsistency detection pass |
| **Sublate** | Synthesis/resolution pass |
| **Fix** | Fixed-point iteration pass |

---

## Type Signatures

```python
@dataclass(frozen=True)
class Pass:
    """A single compiler pass."""
    name: str
    input_type: str
    output_type: str
    law_pack: tuple[str, ...]  # Laws this pass must satisfy

@dataclass(frozen=True)
class ProofCarryingIR:
    """IR with attached proofs from passes."""
    ir: IntermediateRepresentation
    witnesses: tuple[TraceWitness, ...]
    verification_graph: VerificationGraph

ApplyPass: (Pass, IR) -> ProofCarryingIR
```

### The Pass Operad

```python
@dataclass(frozen=True)
class PassOperad:
    """Grammar of valid pass compositions."""
    operations: dict[str, PassOperation]
    composition_laws: tuple[CompositionLaw, ...]

    def compose(self, passes: list[str]) -> Pass:
        """Compose passes into a single pass."""
        ...

    def verify_laws(self, composed: Pass) -> LawResult:
        """Verify composition satisfies laws."""
        ...

ASHC_OPERAD = PassOperad(
    operations={
        "id": PassOperation(arity=0, compose=identity_compose),
        "ground": PassOperation(arity=0, compose=ground_compose),
        "judge": PassOperation(arity=1, compose=judge_compose),
        "contradict": PassOperation(arity=2, compose=contradict_compose),
        "sublate": PassOperation(arity=1, compose=sublate_compose),
        "fix": PassOperation(arity=1, compose=fix_compose),
    },
    composition_laws=[
        IdentityLaw(),      # id >> p ≡ p ≡ p >> id
        AssociativityLaw(), # (p >> q) >> r ≡ p >> (q >> r)
        FunctorLaw(),       # lift(p >> q) ≡ lift(p) >> lift(q)
    ],
)
```

---

## Implementation Tasks

### Task 1: Pass Core Types
**Checkpoint**: Types compile, tests pass

```python
# impl/claude/protocols/ashc/passes/core.py

from dataclasses import dataclass
from typing import Protocol, TypeVar

IR = TypeVar("IR")

class PassProtocol(Protocol[IR]):
    """Protocol for compiler passes."""
    name: str
    input_type: str
    output_type: str

    async def invoke(self, ir: IR) -> ProofCarryingIR:
        """Execute pass, returning IR with witnesses."""
        ...

    def __rshift__(self, other: "PassProtocol") -> "ComposedPass":
        """Compose with another pass."""
        ...

@dataclass(frozen=True)
class ProofCarryingIR:
    ir: Any
    witnesses: tuple["TraceWitness", ...]
    verification_graph: "VerificationGraph"
```

### Task 2: Bootstrap Pass Implementations
**Checkpoint**: Each bootstrap agent wrapped as Pass

```python
# impl/claude/protocols/ashc/passes/bootstrap.py

class GroundPass(PassProtocol):
    """Ground: Void → Facts"""
    name = "ground"
    input_type = "Void"
    output_type = "Facts"

    async def invoke(self, _: None) -> ProofCarryingIR:
        from bootstrap.ground import ground
        facts = await ground()
        witness = TraceWitness(
            pass_name="ground",
            input_data=None,
            output_data=facts,
        )
        return ProofCarryingIR(
            ir=facts,
            witnesses=(witness,),
            verification_graph=VerificationGraph.empty(),
        )

class JudgePass(PassProtocol):
    """Judge: (Agent, Principles) → Verdict"""
    name = "judge"
    input_type = "Agent"
    output_type = "Verdict"

    async def invoke(self, agent: Any) -> ProofCarryingIR:
        from bootstrap.judge import judge
        verdict = await judge(agent)
        witness = TraceWitness(
            pass_name="judge",
            input_data=agent,
            output_data=verdict,
        )
        return ProofCarryingIR(
            ir=verdict,
            witnesses=(witness,),
            verification_graph=VerificationGraph.empty(),
        )

# ... ContradictPass, SublatePass, FixPass
```

### Task 3: Pass Composition
**Checkpoint**: `p >> q` produces valid composed pass

```python
# impl/claude/protocols/ashc/passes/composition.py

@dataclass
class ComposedPass(PassProtocol):
    """Result of composing two passes."""
    first: PassProtocol
    second: PassProtocol

    @property
    def name(self) -> str:
        return f"({self.first.name} >> {self.second.name})"

    @property
    def input_type(self) -> str:
        return self.first.input_type

    @property
    def output_type(self) -> str:
        return self.second.output_type

    async def invoke(self, ir: Any) -> ProofCarryingIR:
        result1 = await self.first.invoke(ir)
        result2 = await self.second.invoke(result1.ir)
        return ProofCarryingIR(
            ir=result2.ir,
            witnesses=result1.witnesses + result2.witnesses,
            verification_graph=merge_graphs(
                result1.verification_graph,
                result2.verification_graph,
            ),
        )

    def __rshift__(self, other: PassProtocol) -> "ComposedPass":
        return ComposedPass(self, other)
```

### Task 4: Pass Operad Implementation
**Checkpoint**: Operad validates compositions, rejects invalid ones

```python
# impl/claude/protocols/ashc/passes/operad.py

@dataclass(frozen=True)
class PassOperad:
    """The grammar of valid pass compositions."""
    operations: dict[str, PassOperation]
    composition_laws: tuple[CompositionLaw, ...]

    def compose(self, pass_names: list[str]) -> PassProtocol:
        """Compose named passes into a pipeline."""
        if not pass_names:
            return IdentityPass()

        passes = [self._resolve_pass(name) for name in pass_names]
        result = passes[0]
        for p in passes[1:]:
            result = result >> p
        return result

    def verify_laws(self, composed: PassProtocol) -> LawResult:
        """Verify all composition laws hold."""
        results = []
        for law in self.composition_laws:
            results.append(law.verify(composed))
        return LawResult.aggregate(results)

    def _resolve_pass(self, name: str) -> PassProtocol:
        if name not in self.operations:
            raise ValueError(f"Unknown pass: {name}")
        return self.operations[name].instantiate()
```

### Task 5: Law Verification Integration
**Checkpoint**: Uses existing BootstrapWitness infrastructure

```python
# impl/claude/protocols/ashc/passes/laws.py

class IdentityLaw(CompositionLaw):
    """Id >> p ≡ p ≡ p >> Id"""

    async def verify(self, pass_: PassProtocol) -> LawResult:
        from agents.o.bootstrap_witness import verify_identity_laws
        result = await verify_identity_laws()
        return LawResult(
            law="identity",
            holds=result.holds,
            evidence=result.evidence,
        )

class AssociativityLaw(CompositionLaw):
    """(p >> q) >> r ≡ p >> (q >> r)"""

    async def verify(self, pass_: PassProtocol) -> LawResult:
        from agents.o.bootstrap_witness import verify_composition_laws
        result = await verify_composition_laws()
        return LawResult(
            law="associativity",
            holds=result.holds,
            evidence=result.evidence,
        )
```

---

## File Structure

```
impl/claude/protocols/ashc/passes/
├── __init__.py
├── core.py             # PassProtocol, ProofCarryingIR
├── bootstrap.py        # Ground, Judge, Contradict, Sublate, Fix
├── composition.py      # ComposedPass, >>
├── operad.py           # PassOperad
├── laws.py             # Identity, Associativity, Functor
├── registry.py         # Pass registration
├── _tests/
│   ├── test_core.py
│   ├── test_bootstrap.py
│   ├── test_composition.py
│   ├── test_operad.py
│   └── test_laws.py
```

---

## Quality Checkpoints

| Checkpoint | Command | Expected |
|------------|---------|----------|
| Types Compile | `uv run mypy protocols/ashc/passes/` | 0 errors |
| Bootstrap Wraps | `pytest test_bootstrap.py` | All 7 passes work |
| Composition | `pytest test_composition.py` | >> works correctly |
| Identity Law | `pytest test_laws.py::test_identity` | PASS |
| Associativity | `pytest test_laws.py::test_associativity` | PASS |
| Full Operad | `kg concept.compiler.operad.verify` | All laws PASS |

---

## User Flows

### Flow: List Available Passes

```bash
$ kg concept.compiler.operad.manifest

┌─ ASHC PASS OPERAD ────────────────────────────────────┐
│ Passes:                                                │
│   ground     : Void → Facts        (arity 0)          │
│   judge      : Agent → Verdict     (arity 1)          │
│   contradict : (A, B) → Tension    (arity 2)          │
│   sublate    : Tension → Synthesis (arity 1)          │
│   fix        : (A → A) → A         (arity 1)          │
│   id         : A → A               (arity 0)          │
│                                                        │
│ Laws:                                                  │
│   ✓ identity      (verified)                          │
│   ✓ associativity (verified)                          │
│   ✓ functor       (verified)                          │
└────────────────────────────────────────────────────────┘
```

### Flow: Compose a Custom Pipeline

```bash
$ kg concept.compiler.operad.compose "ground >> judge >> fix"

Composing: ground >> judge >> fix

Type checking...
  ground: Void → Facts         ✓
  judge: Facts → Verdict       ✓ (Facts <: Agent)
  fix: Verdict → Verdict       ✓

Verifying laws...
  identity:      ✓
  associativity: ✓

Pipeline ready: (ground >> judge >> fix)
```

### Flow: Run a Pipeline on Spec

```bash
$ kg concept.compiler.compile --pipeline "ground >> judge" spec/agents/new.md

Parsing spec... ✓
Running pipeline...
  [1/2] ground: extracting facts from spec ███████████ done
  [2/2] judge: validating against principles ███████████ done

Witnesses captured: 2
Artifacts generated:
  - IR (validated)
  - TraceWitness (ground)
  - TraceWitness (judge)

Verdict: ACCEPT
```

---

## UI/UX Considerations

### Progress Visualization

For multi-pass pipelines, show streaming progress:

```
Compiling spec/agents/complex.md with 5 passes...

[ground    ] ████████████████████ done (0.2s)
[judge     ] ████████████████████ done (0.8s)
[contradict] ██████████░░░░░░░░░░ 50% checking...
[sublate   ] ░░░░░░░░░░░░░░░░░░░░ pending
[fix       ] ░░░░░░░░░░░░░░░░░░░░ pending
```

### Law Verification Dashboard

```
┌─ LAW VERIFICATION ─────────────────────────────────────┐
│                                                         │
│  Identity Law                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Id >> f ≡ f    [████████████████████] HOLDS     │  │
│  │ f >> Id ≡ f    [████████████████████] HOLDS     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Associativity Law                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ (f >> g) >> h  [████████████████████] VERIFIED  │  │
│  │ f >> (g >> h)  [████████████████████] VERIFIED  │  │
│  │ Equality: ✓ outputs match                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Error Messages

Per Verification Tower aesthetic—warm and actionable:

```
┌─ TYPE MISMATCH IN PIPELINE ────────────────────────────┐
│                                                         │
│ The passes don't quite connect where we expected:       │
│                                                         │
│   judge : Agent → Verdict                               │
│   contradict : (A, B) → Tension                         │
│                 ^                                       │
│                 ╰─ contradict needs 2 inputs,           │
│                    but judge only provides 1            │
│                                                         │
│ Suggestion: Use a pass that produces two values,        │
│ or apply contradict to a pair explicitly:               │
│                                                         │
│   ground >> (judge, judge) >> contradict                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Laws/Invariants

### Categorical Laws (Required)

```
Identity:       Id >> p ≡ p ≡ p >> Id
Associativity:  (p >> q) >> r ≡ p >> (q >> r)
Functor:        lift(p >> q) ≡ lift(p) >> lift(q)
```

### Proof-Carrying Law

```
∀ pass P, input I:
  P(I) = (output O, witness W)
  verify(W) == true
```

Every pass MUST emit a witness. Silent passes are compile failures.

### Type Safety

```
∀ passes p: A → B, q: C → D:
  (p >> q) valid iff B <: C
```

Composition only works if types align.

---

## Integration Points

| System | Integration |
|--------|-------------|
| **L0 Kernel** | `invoke` primitive calls passes |
| **BootstrapWitness** | Law verification delegates to existing infra |
| **Verification Tower** | TraceWitness, VerificationGraph shared |
| **AGENTESE** | `concept.compiler.operad.*` paths |

---

## Flexibility Points

| Fixed | Flexible |
|-------|----------|
| 7 bootstrap passes | Additional derived passes |
| Category laws | Additional custom laws |
| Pass composition via >> | Custom operators for parallel |
| Witness emission | Witness format details |

---

## Testing Strategy

### Unit Tests
- Each bootstrap pass in isolation
- Composition produces correct types
- Law verification passes

### Property Tests
```python
@given(st.lists(st.sampled_from(PASS_NAMES), min_size=1, max_size=5))
def test_composition_associativity(pass_names):
    """Any composition order produces same result."""
    left = ((p1 >> p2) >> p3)
    right = (p1 >> (p2 >> p3))
    assert left.output_type == right.output_type
```

### Integration Tests
- Full pipeline on real spec
- Witness chain verification
- VerificationGraph construction

---

## Success Criteria

✅ All 7 bootstrap agents wrapped as passes
✅ Pass composition via >> works
✅ Identity law verified
✅ Associativity law verified
✅ `kg concept.compiler.operad.verify` shows all PASS
✅ Pipeline execution produces ProofCarryingIR

---

## Dependencies

### From Phase 1
- L0 Kernel operational
- `invoke` primitive working

### Existing Infrastructure
- `agents/o/bootstrap_witness.py` — law verification
- `agents/operad/` — operad primitives
- `services/verification/` — TraceWitness types

---

## Next Phase

After Pass Operad: `plans/ashc-evergreen-integration.md`

---

*"The operad defines the grammar. The passes speak the language."*
