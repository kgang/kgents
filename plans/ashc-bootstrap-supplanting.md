# ASHC Phase 4: Bootstrap Supplanting

> *"The bootstrap stops being a static kernel and becomes a verified output."*

**Parent**: `plans/ashc-master.md`
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md` §Bootstrap Supplanting
**Related**: `spec/bootstrap.md`
**Phase**: PLAN
**Effort**: ~3 sessions

---

## Purpose

Bootstrap Supplanting is the heart of ASHC's self-hosting capability. The 7 bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix) become **compiled artifacts** that are:

1. **Regenerated** from spec each run
2. **Verified** against the installed bootstrap
3. **Isomorphic** to the original

```
Invariant: compile_bootstrap(spec).agents ~= installed_bootstrap.agents
```

ASHC does not delete the bootstrap—it **absorbs** it.

---

## Core Types

### BootstrapBundle (From Spec)

```python
@dataclass(frozen=True)
class BootstrapBundle:
    """Complete regenerated bootstrap."""
    agents: tuple[Agent, ...]  # Id, Compose, Judge, Ground, Contradict, Sublate, Fix
    witnesses: tuple[TraceWitness, ...]
    operad: Operad

CompileBootstrap: Spec -> BootstrapBundle
```

### IsomorphismResult

```python
@dataclass(frozen=True)
class IsomorphismResult:
    """Result of comparing generated vs installed bootstrap."""
    is_isomorphic: bool
    differences: tuple[BootstrapDiff, ...]
    confidence: float  # 0.0-1.0

@dataclass(frozen=True)
class BootstrapDiff:
    """A specific difference between bootstraps."""
    agent_name: str
    diff_type: str  # "signature", "behavior", "law_violation"
    description: str
    severity: str  # "critical", "warning", "cosmetic"
```

---

## Implementation Tasks

### Task 1: Bootstrap Spec Parser
**Checkpoint**: Parse `spec/bootstrap.md` into structured form

```python
# impl/claude/protocols/ashc/bootstrap/parser.py

@dataclass(frozen=True)
class BootstrapAgentSpec:
    """Parsed spec for a bootstrap agent."""
    name: str
    signature: str  # "A → B"
    description: str
    laws: tuple[str, ...]
    section_content: str

async def parse_bootstrap_spec(spec_path: Path) -> tuple[BootstrapAgentSpec, ...]:
    """
    Parse spec/bootstrap.md into structured agent specs.

    Extracts:
    - Agent name (Id, Compose, Judge, etc.)
    - Type signature (A → A, (Agent, Agent) → Agent, etc.)
    - Laws/invariants
    - Description
    """
    content = spec_path.read_text()

    # Parse markdown sections
    sections = parse_markdown_sections(content)

    specs = []
    for section in sections:
        if is_agent_section(section):
            specs.append(BootstrapAgentSpec(
                name=extract_name(section),
                signature=extract_signature(section),
                description=extract_description(section),
                laws=extract_laws(section),
                section_content=section,
            ))

    return tuple(specs)
```

### Task 2: Agent Generator
**Checkpoint**: Generate agent code from spec

```python
# impl/claude/protocols/ashc/bootstrap/generator.py

async def generate_agent(
    spec: BootstrapAgentSpec,
    grammar: GrammarSpec,
) -> GeneratedAgent:
    """
    Generate agent implementation from spec.

    Uses LLM to fill in implementation details,
    constrained by grammar and type signature.
    """
    # Build prompt with spec, grammar constraints
    prompt = build_generation_prompt(spec, grammar)

    # Generate via K-gent (ensures voice alignment)
    code = await logos.invoke(
        "concept.compiler.generate",
        L0_UMWELT,
        spec=spec,
        grammar=grammar,
    )

    # Parse and validate generated code
    parsed = parse_python(code)
    validate_signature(parsed, spec.signature)

    return GeneratedAgent(
        name=spec.name,
        code=code,
        spec=spec,
        witness=TraceWitness(
            pass_name="generate_agent",
            input_data=spec,
            output_data=code,
        ),
    )
```

### Task 3: Isomorphism Checker
**Checkpoint**: Compare generated vs installed bootstrap

```python
# impl/claude/protocols/ashc/bootstrap/isomorphism.py

async def check_isomorphism(
    generated: BootstrapBundle,
    installed: BootstrapBundle,
) -> IsomorphismResult:
    """
    Verify generated bootstrap is isomorphic to installed.

    Checks:
    1. All agents present with same names
    2. Signatures match
    3. Behaviors match (property testing)
    4. Laws hold for both
    """
    differences = []

    # 1. Structural check: same agents present
    gen_names = {a.name for a in generated.agents}
    inst_names = {a.name for a in installed.agents}
    if gen_names != inst_names:
        differences.append(BootstrapDiff(
            agent_name="<all>",
            diff_type="structure",
            description=f"Agent sets differ: {gen_names ^ inst_names}",
            severity="critical",
        ))

    # 2. Signature check
    for gen_agent in generated.agents:
        inst_agent = find_agent(installed, gen_agent.name)
        if inst_agent and gen_agent.signature != inst_agent.signature:
            differences.append(BootstrapDiff(
                agent_name=gen_agent.name,
                diff_type="signature",
                description=f"Signature mismatch: {gen_agent.signature} vs {inst_agent.signature}",
                severity="critical",
            ))

    # 3. Behavioral check (property testing)
    for gen_agent in generated.agents:
        inst_agent = find_agent(installed, gen_agent.name)
        if inst_agent:
            behavior_match = await check_behavior_match(gen_agent, inst_agent)
            if not behavior_match.matches:
                differences.append(BootstrapDiff(
                    agent_name=gen_agent.name,
                    diff_type="behavior",
                    description=behavior_match.reason,
                    severity="warning",
                ))

    # 4. Law check
    gen_laws = await verify_bootstrap_laws(generated)
    inst_laws = await verify_bootstrap_laws(installed)
    if gen_laws != inst_laws:
        differences.append(BootstrapDiff(
            agent_name="<laws>",
            diff_type="law_violation",
            description=f"Law results differ",
            severity="critical",
        ))

    return IsomorphismResult(
        is_isomorphic=len([d for d in differences if d.severity == "critical"]) == 0,
        differences=tuple(differences),
        confidence=1.0 - (len(differences) * 0.1),
    )
```

### Task 4: Bootstrap Compiler Pipeline
**Checkpoint**: Full compile_bootstrap flow works

```python
# impl/claude/protocols/ashc/bootstrap/compiler.py

async def compile_bootstrap(spec_path: Path) -> BootstrapBundle:
    """
    Compile bootstrap from spec.

    Full pipeline:
    1. Parse spec
    2. Extract grammar
    3. Generate agents
    4. Verify laws
    5. Bundle with witnesses
    """
    # 1. Parse spec
    agent_specs = await parse_bootstrap_spec(spec_path)

    # 2. Get grammar from Evergreen
    grammar = await get_grammar_spec()

    # 3. Generate each agent
    generated_agents = []
    witnesses = []
    for spec in agent_specs:
        gen = await generate_agent(spec, grammar)
        generated_agents.append(gen)
        witnesses.append(gen.witness)

    # 4. Build operad from generated agents
    operad = build_bootstrap_operad(generated_agents)

    # 5. Verify laws
    law_result = await verify_operad_laws(operad)
    if not law_result.all_pass:
        raise BootstrapLawViolation(law_result)

    return BootstrapBundle(
        agents=tuple(g.agent for g in generated_agents),
        witnesses=tuple(witnesses),
        operad=operad,
    )
```

### Task 5: Supplanting Decision Logic
**Checkpoint**: Smart decision on what to do with differences

```python
# impl/claude/protocols/ashc/bootstrap/supplanting.py

@dataclass(frozen=True)
class SupplantingDecision:
    """What to do when generated differs from installed."""
    action: str  # "use_generated", "keep_installed", "require_review"
    reason: str
    diff_summary: str

async def decide_supplanting(
    iso_result: IsomorphismResult,
    context: SupplantingContext,
) -> SupplantingDecision:
    """
    Decide what to do when isomorphism check reveals differences.

    Policy:
    - Isomorphic → use generated (proves bootstrap is stable)
    - Cosmetic diffs only → use generated (formatting doesn't matter)
    - Warning diffs → notify, use generated
    - Critical diffs → require review, keep installed
    """
    if iso_result.is_isomorphic:
        return SupplantingDecision(
            action="use_generated",
            reason="Bootstrap regeneration verified",
            diff_summary="No meaningful differences",
        )

    critical = [d for d in iso_result.differences if d.severity == "critical"]
    if critical:
        return SupplantingDecision(
            action="require_review",
            reason=f"{len(critical)} critical differences found",
            diff_summary=format_diffs(critical),
        )

    warnings = [d for d in iso_result.differences if d.severity == "warning"]
    if warnings:
        return SupplantingDecision(
            action="use_generated",  # Still use, but notify
            reason=f"{len(warnings)} warnings (non-critical)",
            diff_summary=format_diffs(warnings),
        )

    return SupplantingDecision(
        action="use_generated",
        reason="Only cosmetic differences",
        diff_summary="",
    )
```

---

## File Structure

```
impl/claude/protocols/ashc/bootstrap/
├── __init__.py
├── parser.py           # Spec parsing (Task 1)
├── generator.py        # Agent generation (Task 2)
├── isomorphism.py      # Comparison (Task 3)
├── compiler.py         # Full pipeline (Task 4)
├── supplanting.py      # Decision logic (Task 5)
├── _tests/
│   ├── test_parser.py
│   ├── test_generator.py
│   ├── test_isomorphism.py
│   ├── test_compiler.py
│   └── test_supplanting.py
```

---

## Quality Checkpoints

| Checkpoint | Command | Expected |
|------------|---------|----------|
| Parser | `pytest test_parser.py` | All 7 agents parsed |
| Generator | `pytest test_generator.py` | Code generated for each |
| Isomorphism | `pytest test_isomorphism.py` | Match detection works |
| Full Compile | `kg concept.compiler.bootstrap` | Bundle returned |
| Validation | `kg concept.compiler.validate` | Isomorphism PASS |

---

## User Flows

### Flow: Validate Current Bootstrap (Most Common)

```bash
$ kg concept.compiler.validate

┌─ BOOTSTRAP VALIDATION ─────────────────────────────────┐
│                                                         │
│ Parsing spec/bootstrap.md...              ✓             │
│ Extracting grammar from CLAUDE.md...      ✓             │
│                                                         │
│ Generating bootstrap agents:                            │
│   [1/7] Id         ████████████████████ ✓              │
│   [2/7] Compose    ████████████████████ ✓              │
│   [3/7] Judge      ████████████████████ ✓              │
│   [4/7] Ground     ████████████████████ ✓              │
│   [5/7] Contradict ████████████████████ ✓              │
│   [6/7] Sublate    ████████████████████ ✓              │
│   [7/7] Fix        ████████████████████ ✓              │
│                                                         │
│ Comparing with installed bootstrap...                   │
│                                                         │
│ RESULT: ISOMORPHIC ✓                                    │
│                                                         │
│ The bootstrap can be regenerated from spec.             │
│ This is the proof that kgents is self-hosting.          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Differences Detected

```bash
$ kg concept.compiler.validate

┌─ BOOTSTRAP VALIDATION ─────────────────────────────────┐
│                                                         │
│ ... (generation steps) ...                              │
│                                                         │
│ Comparing with installed bootstrap...                   │
│                                                         │
│ DIFFERENCES FOUND:                                      │
│                                                         │
│ ⚠ Judge (warning)                                       │
│   Behavior: Generated version handles edge case         │
│   differently for empty principle lists.                │
│                                                         │
│ Decision: USE GENERATED                                 │
│ Reason: Warning-level difference (non-breaking)         │
│                                                         │
│ Would you like to:                                      │
│   [1] Accept generated (update installed)               │
│   [2] Keep installed (update spec to match)             │
│   [3] Review diff in detail                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Critical Difference (Rare)

```bash
$ kg concept.compiler.validate

┌─ BOOTSTRAP VALIDATION ─────────────────────────────────┐
│                                                         │
│ ... (generation steps) ...                              │
│                                                         │
│ CRITICAL DIFFERENCES FOUND:                             │
│                                                         │
│ ✗ Compose (critical)                                    │
│   Signature mismatch:                                   │
│     Spec: (Agent, Agent) → Agent                        │
│     Installed: (Agent[A,B], Agent[B,C]) → Agent[A,C]    │
│                                                         │
│ This is a fundamental disagreement between spec and     │
│ implementation. Manual review required.                 │
│                                                         │
│ Options:                                                │
│   [1] Update spec to match implementation               │
│   [2] Update implementation to match spec               │
│   [3] Open diff in editor                               │
│                                                         │
│ WARNING: This may indicate spec drift. The spec is      │
│ the source of truth—prefer option 1 carefully.          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Full Regeneration

```bash
$ kg concept.compiler.bootstrap --regenerate

Regenerating bootstrap from spec...

Parsing...            ✓
Generating agents...  ✓
Verifying laws...     ✓
Writing to impl/claude/bootstrap/...

Files updated:
  - impl/claude/bootstrap/id.py
  - impl/claude/bootstrap/compose.py
  - impl/claude/bootstrap/judge.py
  - impl/claude/bootstrap/ground.py
  - impl/claude/bootstrap/contradict.py
  - impl/claude/bootstrap/sublate.py
  - impl/claude/bootstrap/fix.py

Witnesses captured: 7
Proofs attached: ✓

Bootstrap regeneration complete.
Run 'kg concept.compiler.validate' to verify.
```

---

## UI/UX Considerations

### Progress Visualization

For the regeneration process, show which agent is being generated:

```
Generating bootstrap (7 agents)...

Id          [✓] 0.2s
Compose     [✓] 0.3s
Judge       [█░░░░░░░░░] generating...
Ground      [ ] pending
Contradict  [ ] pending
Sublate     [ ] pending
Fix         [ ] pending
```

### Diff Visualization

When showing differences, use familiar diff format:

```
┌─ DIFF: Judge ──────────────────────────────────────────┐
│                                                         │
│ @@ spec/bootstrap.md: line 124 @@                       │
│                                                         │
│   Judge: (Agent, Principles) → Verdict                  │
│ - Judge(agent, principles) = {accept, reject, revise}   │
│ + Judge(agent, principles) = {accept, reject}           │
│                                                         │
│ @@ impl/claude/bootstrap/judge.py: line 45 @@           │
│                                                         │
│   class Verdict(Enum):                                  │
│       ACCEPT = "accept"                                 │
│       REJECT = "reject"                                 │
│ -     REVISE = "revise"  # Removed in implementation    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Confidence Meter

Show confidence in isomorphism check:

```
Isomorphism Confidence: ████████░░ 80%

Factors:
  Structure match: 100%
  Signature match: 100%
  Behavior match:   85%  (3 edge cases differ)
  Law compliance:  100%
```

---

## Laws/Invariants

### Bootstrap Regeneration Law (From Spec)
```
compile_bootstrap(spec).agents ~= bootstrap.agents
```

The generated bootstrap MUST be isomorphic to the installed one.

### Witness Completeness
```
∀ agent A in compile_bootstrap():
  ∃ witness W: W.pass_name == "generate_agent" ∧ W.output_data == A
```

Every generated agent has a witness.

### Law Preservation
```
verify_laws(compile_bootstrap(spec)) == verify_laws(installed_bootstrap)
```

Generated bootstrap satisfies the same laws.

---

## Integration Points

| System | Integration |
|--------|-------------|
| **BootstrapWitness** | Existing verification used |
| **Pass Operad** | Generated operad matches ASHC_OPERAD |
| **Evergreen** | Grammar guides generation |
| **VoiceGate** | Generated docs pass voice check |

---

## Flexibility Points

| Fixed | Flexible |
|-------|----------|
| 7 bootstrap agents | Agent internals |
| Isomorphism requirement | Tolerance for cosmetic diffs |
| Witness emission | Witness format details |
| Law verification | Additional custom checks |

---

## Testing Strategy

### Unit Tests
- Parse each section of bootstrap.md
- Generate code for mock spec
- Isomorphism detection for known cases

### Property Tests
```python
@given(st.sampled_from(BOOTSTRAP_AGENTS))
async def test_roundtrip(agent_name):
    """Generated agent satisfies original laws."""
    spec = get_spec(agent_name)
    generated = await generate_agent(spec, grammar)
    laws = await verify_laws(generated)
    assert laws.all_pass
```

### Integration Tests
- Full compile_bootstrap on real spec
- Isomorphism check against real bootstrap
- Supplanting decision flow

---

## Success Criteria

✅ `spec/bootstrap.md` parses into 7 BootstrapAgentSpecs
✅ Each agent generates valid Python code
✅ Isomorphism check passes for current bootstrap
✅ `kg concept.compiler.validate` shows ISOMORPHIC
✅ Full regeneration produces working bootstrap
✅ Witnesses captured for all generation steps

---

## Dependencies

### From Phase 3
- GrammarSpec available
- Grammar extraction working

### Existing Infrastructure
- `spec/bootstrap.md` — canonical spec
- `impl/claude/bootstrap/` — current implementation
- `agents/o/bootstrap_witness.py` — verification

---

## Next Phase

After Bootstrap Supplanting: `plans/ashc-voice-verification.md`

---

*"The kernel that proves itself is the kernel that trusts itself."*
