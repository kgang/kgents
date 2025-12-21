# ASHC Phase 5: Bootstrap Regeneration

> *"The kernel that proves itself is the kernel that trusts itself."*

**Parent**: `plans/ashc-master.md`
**Previous**: Phase 4 (VoidHarness + LLM Compiler) ✅ 346 tests
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md`
**Phase**: IMPLEMENT
**Effort**: ~2 sessions

---

## 🎯 GROUNDING IN KENT'S INTENT

*"Daring, bold, creative, opinionated but not gaudy"*
*"The Mirror Test: Does K-gent feel like me on my best day?"*

**The Ultimate Self-Hosting Test**: Can ASHC regenerate its own bootstrap from specs, and is the output isomorphic to the installed implementation?

This is **not** about replacing human judgment—it's about building confidence that spec ↔ impl equivalence holds.

---

## Vision

With Phase 4 complete (VoidHarness can generate real LLM implementations), Phase 5 proves the core thesis:

```
compile_bootstrap(spec/bootstrap.md) ≅ impl/claude/bootstrap/
```

**Key insight**: We're not trying to generate *identical* code. We're testing whether:
1. Generated code satisfies the same laws
2. Generated code passes the same tests
3. Generated code exhibits equivalent behavior

The isomorphism is **behavioral**, not textual.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP REGENERATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. PARSE                                                               │
│      spec/bootstrap.md → BootstrapAgentSpec × 7                          │
│      Extract: name, signature, laws, section_content                     │
│                                                                          │
│   2. GENERATE (via VoidHarness)                                          │
│      Each spec → VoidHarness.generate() → Python code                    │
│      Collect: GenerationResult with metadata                             │
│                                                                          │
│   3. VERIFY                                                              │
│      Generated code → pytest/mypy/ruff                                   │
│      Use existing bootstrap tests as verification                        │
│                                                                          │
│   4. COMPARE (Isomorphism Check)                                         │
│      Generated behavior vs Installed behavior                            │
│      Check: Laws hold, properties match, types compatible                │
│                                                                          │
│   5. EMIT                                                                │
│      BootstrapRegenerationResult with isomorphism score                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Types

### BootstrapAgentSpec (Parser Output)

```python
@dataclass(frozen=True)
class BootstrapAgentSpec:
    """Parsed specification for a single bootstrap agent."""
    name: str                    # "Id", "Compose", "Judge", etc.
    signature: str               # "A → A", "(Agent, Agent) → Agent"
    description: str             # Purpose from spec
    laws: tuple[str, ...]        # Laws that must hold
    section_content: str         # Full markdown section

    @property
    def spec_hash(self) -> str:
        """Content-addressed identifier for the spec."""
        return hashlib.sha256(self.section_content.encode()).hexdigest()[:12]
```

### IsomorphismResult

```python
@dataclass(frozen=True)
class BehaviorComparison:
    """Result of comparing two implementations' behavior."""
    agent_name: str
    test_pass_rate: float        # 0.0-1.0
    type_compatible: bool        # mypy passes
    laws_satisfied: bool         # All stated laws hold
    property_tests_pass: bool    # Hypothesis finds no counterexamples

    @property
    def is_isomorphic(self) -> bool:
        """Behavioral isomorphism requires all checks to pass."""
        return (
            self.test_pass_rate >= 0.95 and  # Allow some variance
            self.type_compatible and
            self.laws_satisfied and
            self.property_tests_pass
        )

@dataclass(frozen=True)
class BootstrapIsomorphism:
    """Overall result of bootstrap regeneration."""
    comparisons: tuple[BehaviorComparison, ...]
    overall_score: float         # 0.0-1.0
    regeneration_time_ms: float
    tokens_used: int

    @property
    def is_isomorphic(self) -> bool:
        """All agents are behaviorally isomorphic."""
        return all(c.is_isomorphic for c in self.comparisons)
```

---

## Implementation Tasks

### Task 1: Bootstrap Spec Parser (~30 min)

Parse `spec/bootstrap.md` into structured BootstrapAgentSpecs.

```python
# protocols/ashc/bootstrap/parser.py

AGENT_NAMES = ["Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix"]

def parse_bootstrap_spec(spec_path: Path) -> tuple[BootstrapAgentSpec, ...]:
    """
    Parse spec/bootstrap.md into individual agent specs.

    Strategy:
    1. Split by ## headers
    2. Find sections for each agent
    3. Extract signature, description, laws from each
    """
```

**Key Patterns in spec/bootstrap.md**:
```markdown
### 1. Id (Identity)

```
Id: A → A
Id(x) = x
```

The agent that does nothing. Required by the category-theoretic structure:
- Left identity: Id ∘ f = f
- Right identity: f ∘ Id = f
```

Parse: name="Id", signature="A → A", laws=["Id(x) = x", "Id ∘ f = f", "f ∘ Id = f"]

### Task 2: Generation Prompts for Each Agent (~1 hour)

Create tailored prompts that maximize regeneration quality.

```python
# protocols/ashc/bootstrap/prompts.py

def make_generation_prompt(spec: BootstrapAgentSpec) -> str:
    """
    Build generation prompt from agent spec.

    The prompt must be self-contained (void directory = no context).
    Include:
    - Type signature
    - Laws to satisfy
    - Expected interface (Agent base class)
    """
    return f"""Generate a Python implementation for the {spec.name} agent.

## Type Signature
{spec.signature}

## Laws (MUST satisfy)
{format_laws(spec.laws)}

## Required Interface
- Must inherit from Agent[A, B]
- Must implement async def invoke(self, input: A) -> B
- Must have @property name -> str

## Style
- Use dataclasses for types
- Include docstrings
- Use type hints throughout
- Follow kgents conventions

## Full Specification
{spec.section_content}

Generate only the Python code, no markdown:
"""
```

### Task 3: Isomorphism Checker (~1.5 hours)

The heart of Phase 5: determining behavioral equivalence.

```python
# protocols/ashc/bootstrap/isomorphism.py

async def check_isomorphism(
    generated_code: str,
    installed_module: ModuleType,
    spec: BootstrapAgentSpec,
) -> BehaviorComparison:
    """
    Compare generated code against installed implementation.

    Strategy:
    1. Write generated to temp file
    2. Import as module
    3. Run existing tests against generated
    4. Run property tests for law verification
    5. Compare type signatures
    """

async def verify_laws(
    agent_module: ModuleType,
    spec: BootstrapAgentSpec,
) -> bool:
    """
    Verify that agent satisfies stated laws.

    Uses Hypothesis for property-based testing:
    - Id: ∀x. Id(x) = x
    - Compose: ∀f,g,h. (f >> g) >> h = f >> (g >> h)
    - etc.
    """
```

### Task 4: BootstrapRegenerator Pipeline (~2 hours)

Wire everything together.

```python
# protocols/ashc/bootstrap/regenerator.py

class BootstrapRegenerator:
    """
    Regenerate bootstrap from spec using VoidHarness.

    Usage:
        regenerator = BootstrapRegenerator()
        result = await regenerator.regenerate()

        if result.is_isomorphic:
            print("Bootstrap can be regenerated from spec! ✓")
        else:
            print(f"Differences found: {result.summary()}")
    """

    def __init__(
        self,
        spec_path: Path = Path("spec/bootstrap.md"),
        harness_config: VoidHarnessConfig | None = None,
        budget: TokenBudget | None = None,
    ):
        self.spec_path = spec_path
        self.harness = VoidHarness(harness_config, budget)

    async def regenerate(
        self,
        agents: list[str] | None = None,  # None = all 7
        n_variations: int = 3,             # Generate multiple for confidence
    ) -> BootstrapIsomorphism:
        """
        Regenerate bootstrap and check isomorphism.

        1. Parse spec
        2. For each agent:
           a. Generate n variations
           b. Verify each with pytest/mypy
           c. Compare behavior to installed
           d. Record isomorphism result
        3. Return overall isomorphism score
        """
```

### Task 5: Integration Tests (~1 hour)

Tests that can run without LLM (fast, always-on) + integration tests (with LLM).

```python
# protocols/ashc/_tests/test_bootstrap_regeneration.py

# Unit tests (no LLM)
class TestSpecParser:
    def test_parses_all_seven_agents(self):
        specs = parse_bootstrap_spec(SPEC_PATH)
        assert len(specs) == 7
        assert {s.name for s in specs} == set(AGENT_NAMES)

    def test_extracts_laws_correctly(self):
        specs = parse_bootstrap_spec(SPEC_PATH)
        id_spec = next(s for s in specs if s.name == "Id")
        assert "Id(x) = x" in id_spec.laws

class TestIsomorphismChecker:
    async def test_identical_is_isomorphic(self):
        """Same code should be isomorphic to itself."""
        from bootstrap.id import Id
        result = await check_isomorphism(ID_SOURCE, Id, ID_SPEC)
        assert result.is_isomorphic

# Integration tests (with LLM, opt-in)
@pytest.mark.skipif(not RUN_LLM_TESTS, reason="LLM tests disabled")
class TestBootstrapRegeneration:
    async def test_regenerate_id_agent(self):
        """Can regenerate Id agent from spec."""
        regenerator = BootstrapRegenerator()
        result = await regenerator.regenerate(agents=["Id"])
        assert result.is_isomorphic

    async def test_regenerate_compose_agent(self):
        """Can regenerate Compose agent from spec."""
        regenerator = BootstrapRegenerator()
        result = await regenerator.regenerate(agents=["Compose"])
        assert result.is_isomorphic
```

---

## File Structure

```
impl/claude/protocols/ashc/bootstrap/
├── __init__.py
├── parser.py           # Spec parsing
├── prompts.py          # Generation prompt construction
├── isomorphism.py      # Behavioral comparison
├── regenerator.py      # Main pipeline
├── _tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_isomorphism.py
│   └── integration/
│       ├── __init__.py
│       └── test_regeneration.py
```

---

## Quality Checkpoints

| Checkpoint | Criteria | Test |
|------------|----------|------|
| Parser | All 7 agents extracted | `len(specs) == 7` |
| Laws Extraction | Each agent has laws | `all(s.laws for s in specs)` |
| Id Regeneration | Generates valid Id | `result.test_pass_rate >= 0.95` |
| Compose Regeneration | Generates valid Compose | `result.laws_satisfied` |
| Full Bootstrap | All 7 isomorphic | `result.is_isomorphic` |

---

## Expected Outcomes

### Optimistic (70% likely)
- 5-6 of 7 agents regenerate with high isomorphism score
- Simple agents (Id, Compose) are near-perfect
- Complex agents (Judge, Ground) may need prompt tuning

### Realistic (25% likely)
- 3-4 agents regenerate successfully
- Need iteration on prompts for others
- This is still valuable: identifies which specs are generative

### Pessimistic (5% likely)
- Only 1-2 agents regenerate
- Indicates spec/impl drift that needs addressing
- Also valuable: reveals where spec needs improvement

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Spec parsing | 7/7 agents | Parser completeness |
| Id isomorphism | ≥0.95 | Simplest agent |
| Compose isomorphism | ≥0.90 | Core composition |
| Overall isomorphism | ≥0.80 | Bootstrap regeneration works |
| Test coverage | +30 tests | Quality gates |

---

## Token Budget Estimation

Per agent regeneration (n=3 variations):
- Prompt: ~1500 tokens
- Generation: ~2000 tokens
- Total per variation: ~3500 tokens

For all 7 agents with 3 variations each:
- 7 × 3 × 3500 = ~73,500 tokens
- Plus overhead: ~100,000 tokens budget

**Recommendation**: Start with Id and Compose (simplest) to validate pipeline, then proceed to others.

---

## Anti-Patterns to Avoid

- ❌ **Textual comparison**: Comparing code text is fragile. Compare behavior.
- ❌ **One-shot generation**: Generate multiple variations for confidence.
- ❌ **Ignoring failures**: A failed regeneration is data about spec quality.
- ❌ **Over-prompting**: Let the spec speak for itself.

---

## Relation to Existing Plans

This plan **supersedes** `plans/ashc-bootstrap-supplanting.md` which was written before Phase 4 VoidHarness was implemented. The key differences:

1. **Simpler architecture**: Use VoidHarness directly, not abstract generators
2. **Behavioral isomorphism**: Focus on behavior, not code structure
3. **Integration with existing tests**: Reuse bootstrap/_tests/ for verification
4. **Realistic scope**: Start with Id/Compose, scale up

---

## Next Phase

After Phase 5: **Phase 6: VoiceGate + Verification Tower** (`plans/ashc-voice-verification.md`)

- VoiceGate: Trust-gated output (L0-L3)
- Verification Tower: Stack of verifiers (pytest → mypy → ruff → semantic)
- Evidence integration: Link VoiceGate decisions to causal graph

---

*"We don't prove equivalence. We observe it."*
*"If you grow the tree a thousand times, the pattern of growth IS the proof."*
