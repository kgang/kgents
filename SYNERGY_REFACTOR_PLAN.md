# T-gents × J-gents × E-gents: Master Synergy Refactor Plan

**Date**: 2025-12-08
**Status**: Phase 3 Complete → Cross-Reconciliation
**Goal**: Maximize synergy between Test, JIT, and Evolution agent genera

---

## Executive Summary

All three genera (T-gents, J-gents, E-gents) have excellent spec-implementation alignment and are production-ready. However, significant synergy opportunities exist:

1. **Working Integration**: J-gents Chaosmonger → E-gents Safety ✓
2. **Missing Integration**: E-gents → T-gents (regression/property testing)
3. **Abstraction Opportunity**: ValidationPipeline, ResilientAgent, AgentMemory patterns
4. **Meta-Circular Vision**: J-gents JIT + E-gents Evolution = self-improving agents

**Priority**: Focus on high-value, low-effort wins first (extract AST utils, add regression testing), then explore meta-circular evolution.

---

## Current State Analysis

### T-gents: Testing Agents ✓ COMPLETE
- **Spec**: 4 files (~1,800 lines)
- **Impl**: 12 agents (~66KB code)
- **Tests**: `test_t_gents_phase3.py` (12 tests passing)
- **Types**: Nullifiers (Mock, Fixture), Saboteurs (Failing, Noise, Latency, Flaky), Observers (Spy, Predicate, Counter, Metrics), Critics (Judge, Oracle, Property)

### J-gents: JIT Intelligence ✓ PHASE 3 COMPLETE
- **Spec**: 5 files (~2,500 lines)
- **Impl**: 5 agents (~65KB code)
- **Tests**: `test_j_gents_phase3.py` (22 tests passing)
- **Features**: Promise/lazy computation, Reality trichotomy, Chaosmonger stability, MetaArchitect JIT compilation, Sandbox execution

### E-gents: Evolution Agents ✓ COMPLETE
- **Spec**: 5 files (~2,800 lines)
- **Impl**: 17 modules (~240KB code)
- **Tests**: `test_e_gents_demo.py`
- **Pipeline**: 6-stage (PreFlight → Ground → Hypothesize → Experiment → Judge → Incorporate)
- **Reliability**: 3-layer defense (prompt engineering, parse/validate, recovery/learning)

---

## Synergy Opportunities

### 1. SHARED CONCEPTS (Duplicated → Should Unify)

#### 1.1 Judge Agents: Two Implementations, Same Concept

**Current State**:
- **T-gents Judge** (`agents/t/judge.py`): LLM-as-Judge for semantic evaluation
  - Scores: correctness, safety, style (0-1 floats)
  - Generic intent/output evaluation
  - Marked `__is_test__ = True`

- **E-gents Judge** (`agents/e/judge.py`): Code-specific principle evaluation
  - Scores: 7 kgents principles (tasteful, curated, ethical, etc.)
  - Heuristic-based (not LLM)
  - Two variants: CodeJudge + GenericCodeJudge

**Refactor**:
```python
# Proposed: agents/c/judge.py (or agents/shared/judge.py)
class JudgeAgent(Protocol[A, B]):
    """Universal evaluation morphism."""
    async def judge(self, input: A, output: B) -> JudgmentResult: ...

# Concrete implementations
class SemanticJudge(JudgeAgent):  # LLM-based (from T-gents)
    ...

class PrincipleJudge(JudgeAgent):  # Heuristic (from E-gents)
    ...

class HybridJudge(JudgeAgent):    # Both layers
    def __init__(self, semantic: SemanticJudge, principle: PrincipleJudge):
        self.layers = [semantic, principle]
```

**Benefit**: E-gents gets semantic evaluation option, T-gents gets principle evaluation, both share interface.

**Priority**: P1 (High Value, Low Effort)

---

#### 1.2 AST Analysis: Duplicated Logic

**Current State**:
- **J-gents Chaosmonger** (`agents/j/chaosmonger.py`):
  - `_extract_imports()`, `_calculate_cyclomatic_complexity()`, `_estimate_branching_factor()`
  - `_has_unbounded_recursion()`, `_calculate_max_nesting()`

- **E-gents ASTAnalyzer** (`agents/e/ast_analyzer.py`):
  - Extracts classes, functions, imports, docstrings
  - Complexity hints, type annotation detection

**Refactor**:
```python
# Proposed: agents/shared/ast_utils.py
class ASTAnalysisKit:
    """Common AST operations for all genera."""

    @staticmethod
    def extract_imports(tree: ast.Module) -> list[str]: ...

    @staticmethod
    def calculate_complexity(node: ast.FunctionDef) -> int: ...

    @staticmethod
    def calculate_nesting_depth(node: ast.AST) -> int: ...

    @staticmethod
    def extract_functions(tree: ast.Module) -> list[FunctionInfo]: ...

    @staticmethod
    def extract_classes(tree: ast.Module) -> list[ClassInfo]: ...
```

**Benefit**: DRY, consistent metrics, easier testing.

**Priority**: P1 (High Value, Low Effort)

---

### 2. MISSING INTEGRATIONS (Where Genera Should Use Each Other)

#### 2.1 E-gents → T-gents: Regression & Property Testing

**Gap**: E-gents validates evolved code with syntax/type/unit tests, but doesn't check for behavioral regressions or invariants.

**Integration**:
```python
# In E-gents experiment.py or new regression_validator.py
from agents.t import RegressionOracle, PropertyAgent, IntGenerator

class EvolutionValidator:
    """Validate evolved code preserves behavior and invariants."""

    def __init__(self, original_agent: Agent, evolved_agent: Agent):
        self.regression_oracle = RegressionOracle(
            reference=original_agent,
            system_under_test=evolved_agent
        )
        self.property_agents = [
            PropertyAgent(
                agent=evolved_agent,
                property_fn=self._type_preservation,
                num_cases=50
            ),
            PropertyAgent(
                agent=evolved_agent,
                property_fn=self._no_exceptions,
                num_cases=100
            )
        ]

    async def validate(self, test_inputs: list[Any]) -> ValidationResult:
        # 1. Regression test: evolved matches original on known inputs
        regression_result = await self.regression_oracle.invoke(test_inputs)

        # 2. Property test: invariants hold on random inputs
        property_results = [
            await p.invoke(PropertyInput(...)) for p in self.property_agents
        ]

        return ValidationResult(
            regression_passed=regression_result.passed,
            properties_passed=all(r.passed for r in property_results),
            details={...}
        )
```

**Benefit**:
- Catch behavioral regressions early
- Verify evolved code maintains type contracts, doesn't introduce exceptions
- Property-based testing catches edge cases unit tests miss

**Priority**: P1 (High Value, Low Effort)

---

#### 2.2 J-gents → E-gents: Meta-Circular Evolution

**Vision**: JIT-compiled agents start with templates, get refined by evolution.

**Workflow**:
```
MetaArchitect generates template agent
    ↓
E-gents evolves it (hypothesis → experiment → judge)
    ↓
J-gents Chaosmonger validates stability
    ↓
Execute if stable, collapse to Ground if not
```

**Implementation**:
```python
# Proposed: agents/meta/circular.py
class MetaCircularAgent:
    """Self-improving JIT agent generation."""

    def __init__(
        self,
        architect: MetaArchitect,
        evolver: EvolutionAgent,
        validator: Chaosmonger
    ):
        self.architect = architect
        self.evolver = evolver
        self.validator = validator

    async def generate_and_evolve(
        self,
        intent: str,
        context: dict,
        iterations: int = 3
    ) -> Agent:
        # 1. Generate initial agent
        source = await self.architect.invoke(ArchitectInput(
            intent=intent,
            context=context,
            constraints=...
        ))

        # 2. Evolve it
        for i in range(iterations):
            evolved = await self.evolver.evolve(source)

            # 3. Validate stability
            stability = await self.validator.invoke(StabilityInput(
                source_code=evolved,
                entropy_budget=1.0 / (i + 1)
            ))

            if stability.is_stable:
                source = evolved
            else:
                break  # Collapse, use last stable version

        # 4. Compile and return
        return compile_agent(source)
```

**Benefit**:
- Agents that improve themselves over time
- Combines J's on-demand generation with E's iterative refinement
- True meta-programming: code generating better code

**Priority**: P3 (Exploratory, High Effort - but very cool!)

---

#### 2.3 E-gents → J-gents: Reality Classification for Task Triage

**Gap**: E-gents uses heuristics to decide whether to evolve code. J-gents has more principled Reality trichotomy.

**Integration**:
```python
# In E-gents evolution.py or hypothesis.py
from agents.j import classify_intent, Reality

class SmartEvolutionAgent(EvolutionAgent):
    """Evolution with reality-aware task triage."""

    async def should_evolve(self, module: ModuleInfo) -> bool:
        reality = await classify_intent(f"Improve {module.name}")

        if reality == Reality.DETERMINISTIC:
            # Simple, bounded - safe to evolve directly
            return True
        elif reality == Reality.PROBABILISTIC:
            # Complex - use full pipeline with extra validation
            return True
        else:  # CHAOTIC
            # Unbounded/unstable - skip or use conservative fallback
            return False
```

**Benefit**:
- Smarter resource allocation
- Avoid wasting evolution attempts on chaotic/intractable improvements
- Explicit reasoning about task complexity

**Priority**: P3 (Exploratory, Medium Effort)

---

#### 2.4 T-gents → J-gents: Chaosmonger for Test Validation

**Gap**: T-gents generates test fixtures and mock data, but doesn't validate the test code itself.

**Integration**:
```python
# In T-gents fixture.py or mock.py
from agents.j import check_stability, StabilityConfig

class SafeFixtureAgent(FixtureAgent):
    """Fixture with stability validation."""

    async def load_fixture(self, fixture_code: str) -> Dict[I, O]:
        # Validate fixture code before execution
        stability = await check_stability(
            source_code=fixture_code,
            config=StabilityConfig(
                max_cyclomatic_complexity=10,
                allowed_imports=["typing", "dataclasses"],
                entropy_budget=1.0
            )
        )

        if not stability.is_stable:
            raise ValueError(f"Unsafe fixture: {stability.violations}")

        # Compile and execute in sandbox
        return compile_fixtures(fixture_code)
```

**Benefit**:
- Prevent malicious test fixtures
- Catch overly complex test code
- Same safety guarantees for tests as for production code

**Priority**: P4 (Nice to Have, Low Effort)

---

### 3. ABSTRACTION OPPORTUNITIES (Extract Common Patterns)

#### 3.1 ValidationPipeline Pattern

**Observation**: All three genera use multi-layer validation with progressive filtering.

**Current Implementations**:
- **E-gents**: PreFlight → Parser → Validator → Repair → Test
- **J-gents**: Chaosmonger → Judge → Type Check → Sandbox
- **T-gents**: Spy → Predicate → Counter → Metrics (observability pipeline)

**Extract**:
```python
# Proposed: agents/c/validation.py
class ValidationLayer(Protocol[A]):
    """One layer in a validation pipeline."""

    async def validate(self, value: A) -> LayerResult[A]:
        """
        Returns:
        - PASS: Continue to next layer
        - FAIL: Stop pipeline, return error
        - REPAIR: Attempt fix, re-validate
        """
        ...

class ValidationPipeline(Agent[A, ValidationResult[A]]):
    """Composable multi-layer validation."""

    def __init__(self, layers: list[ValidationLayer[A]]):
        self.layers = layers

    async def invoke(self, input: A) -> ValidationResult[A]:
        current = input
        history = []

        for layer in self.layers:
            result = await layer.validate(current)
            history.append(result)

            if result.status == Status.FAIL:
                return ValidationResult(
                    status=Status.FAIL,
                    value=None,
                    error=result.error,
                    history=history
                )

            if result.status == Status.REPAIR:
                current = result.repaired_value
                # Re-validate repaired value
                continue

            # PASS: continue
            current = result.value

        return ValidationResult(
            status=Status.PASS,
            value=current,
            history=history
        )

# Usage in E-gents
evolution_validator = ValidationPipeline([
    SyntaxLayer(),
    TypeLayer(),
    TestLayer(),
    PrincipleLayer()
])

# Usage in J-gents
jit_validator = ValidationPipeline([
    StabilityLayer(chaosmonger),
    TasteLayer(judge),
    SandboxLayer()
])
```

**Benefit**:
- Reusable across all genera
- Reduces boilerplate
- Clear composition semantics
- Easy to add/remove layers

**Priority**: P2 (High Value, Medium Effort)

---

#### 3.2 ResilientAgent Wrapper

**Observation**: Retry and fallback logic is complex and duplicated.

**Current Implementations**:
- **E-gents**: `RetryStrategy` (sophisticated failure-aware prompt refinement) + `FallbackStrategy` (progressive simplification)
- **J-gents**: Implicit in entropy budget (collapse to Ground on failure)
- **T-gents**: `FlakyAgent` (for testing retry logic, not using it)

**Extract**:
```python
# Proposed: agents/c/resilient.py
@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff: BackoffStrategy = ExponentialBackoff()
    retry_exceptions: tuple[Type[Exception], ...] = (Exception,)

@dataclass
class FallbackConfig:
    levels: list[FallbackLevel]
    # Example: [FullMode(), MinimalMode(), TypeOnlyMode(), DocsMode()]

class ResilientAgent(Agent[A, B]):
    """Wrap any agent with retry + fallback logic."""

    def __init__(
        self,
        agent: Agent[A, B],
        retry_config: Optional[RetryConfig] = None,
        fallback_agent: Optional[Agent[A, B]] = None
    ):
        self.agent = agent
        self.retry_config = retry_config or RetryConfig()
        self.fallback = fallback_agent

    async def invoke(self, input: A) -> B:
        last_exception = None

        # Retry loop
        for attempt in range(self.retry_config.max_attempts):
            try:
                result = await self.agent.invoke(input)
                return result
            except self.retry_config.retry_exceptions as e:
                last_exception = e
                await self.retry_config.backoff.sleep(attempt)
                continue

        # All retries failed, try fallback
        if self.fallback:
            try:
                return await self.fallback.invoke(input)
            except Exception as e:
                raise FallbackFailedError(
                    f"Both agent and fallback failed: {last_exception}, {e}"
                )

        raise last_exception

# Usage
resilient_llm = ResilientAgent(
    agent=GPT4Agent(),
    retry_config=RetryConfig(max_attempts=3, backoff=ExponentialBackoff()),
    fallback_agent=GPT3Agent()
)
```

**Benefit**:
- Every genus gets resilience
- Consistent error handling
- Easy to test (use T-gents FlakyAgent!)

**Priority**: P2 (High Value, Medium Effort)

---

#### 3.3 AgentMemory (D-gents Bootstrap)

**Observation**: Cross-session state is needed by multiple genera.

**Current Implementations**:
- **E-gents**: `ImprovementMemory` (tracks accepted/rejected hypotheses, error patterns)
- **J-gents**: Implicit in Promise trees (parent-child relationships)
- **T-gents**: `SpyAgent.history`, `CounterAgent.count` (in-memory only)

**Extract**:
```python
# Proposed: agents/d/memory.py (D-gents: Data agents)
class AgentMemory(Protocol):
    """Cross-session persistent state for agents."""

    async def remember(self, key: str, value: Any, metadata: dict = {}) -> None:
        """Store a key-value pair with optional metadata."""
        ...

    async def recall(self, key: str) -> Optional[Any]:
        """Retrieve value by exact key."""
        ...

    async def query(self, predicate: Callable[[Any], bool]) -> list[Any]:
        """Fuzzy search by predicate."""
        ...

    async def forget(self, key: str) -> None:
        """Delete a key-value pair."""
        ...

    async def forget_matching(self, predicate: Callable[[Any], bool]) -> int:
        """Delete all entries matching predicate. Returns count deleted."""
        ...

# Concrete implementation (based on E-gents ImprovementMemory)
class JSONFileMemory(AgentMemory):
    """Persistent memory backed by JSON file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._cache: dict = self._load()

    def _load(self) -> dict:
        if self.file_path.exists():
            return json.loads(self.file_path.read_text())
        return {}

    def _save(self) -> None:
        self.file_path.write_text(json.dumps(self._cache, indent=2))

    async def remember(self, key: str, value: Any, metadata: dict = {}) -> None:
        self._cache[key] = {"value": value, "metadata": metadata, "timestamp": time.time()}
        self._save()

    # ... other methods

# Usage in E-gents
evolution_memory = JSONFileMemory(Path(".evolution_memory.json"))
await evolution_memory.remember("rejected_hypothesis", "Add async/await", {"reason": "too complex"})

# Usage in T-gents
test_memory = JSONFileMemory(Path(".test_results.json"))
await test_memory.remember("test_run", {"status": "passed", "duration": 1.23})

# Usage in J-gents
promise_cache = JSONFileMemory(Path(".promise_cache.json"))
await promise_cache.remember(f"promise_{hash(intent)}", compiled_agent)
```

**Benefit**:
- All genera get persistent state
- Unified data layer (foundation for D-gents)
- Easier debugging (inspect memory across sessions)
- Cache JIT-compiled agents, evolution results, test outcomes

**Priority**: P3 (Exploratory, High Effort)

---

#### 3.4 Similarity Metrics

**Observation**: Different genera need to compare values for similarity.

**Current Implementations**:
- **E-gents**: `compute_code_similarity()` (Levenshtein), `compute_structural_similarity()` (AST-based)
- **T-gents**: `OracleAgent` with custom `equality_fn` parameter
- **J-gents**: Implicit in convergence detection

**Extract**:
```python
# Proposed: agents/c/similarity.py
class SimilarityMetric(Protocol[A]):
    """Measure similarity between values of type A."""

    def similarity(self, a: A, b: A) -> float:
        """Return 0.0 (completely different) to 1.0 (identical)."""
        ...

# Concrete implementations
class LevenshteinSimilarity(SimilarityMetric[str]):
    """String edit distance."""

    def similarity(self, a: str, b: str) -> float:
        distance = Levenshtein.distance(a, b)
        max_len = max(len(a), len(b))
        return 1.0 - (distance / max_len) if max_len > 0 else 1.0

class StructuralSimilarity(SimilarityMetric[str]):
    """AST-based code similarity."""

    def similarity(self, code_a: str, code_b: str) -> float:
        tree_a = ast.parse(code_a)
        tree_b = ast.parse(code_b)
        return self._compare_asts(tree_a, tree_b)

class SemanticSimilarity(SimilarityMetric[str]):
    """LLM-based semantic similarity."""

    def __init__(self, llm: Agent):
        self.llm = llm

    async def similarity(self, text_a: str, text_b: str) -> float:
        prompt = f"Rate semantic similarity 0-1:\nA: {text_a}\nB: {text_b}"
        result = await self.llm.invoke(prompt)
        return float(result)

class NumericalSimilarity(SimilarityMetric[float]):
    """Epsilon-based numerical tolerance."""

    def __init__(self, epsilon: float = 1e-6):
        self.epsilon = epsilon

    def similarity(self, a: float, b: float) -> float:
        diff = abs(a - b)
        return 1.0 if diff < self.epsilon else max(0, 1.0 - diff)

# Usage
code_sim = StructuralSimilarity()
if code_sim.similarity(original, evolved) > 0.95:
    print("Code is very similar (minimal change)")

semantic_sim = SemanticSimilarity(llm=GPT4Agent())
if await semantic_sim.similarity(hypothesis_a, hypothesis_b) > 0.8:
    print("These hypotheses are semantically similar")
```

**Benefit**:
- Consistent comparison across genera
- Pluggable similarity strategies
- Easier testing (mock similarity metrics)

**Priority**: P4 (Nice to Have, Low Effort)

---

## Implementation Roadmap

### Phase 4A: Quick Wins (1-2 weeks)

**Goal**: High-value, low-effort extractions and integrations.

1. **Extract AST Utilities** (2-3 hours)
   - [ ] Create `agents/shared/ast_utils.py`
   - [ ] Move import extraction from J-gents Chaosmonger
   - [ ] Move complexity calculation from E-gents ASTAnalyzer
   - [ ] Update J-gents and E-gents to use shared module
   - [ ] Test: `test_ast_utils.py`

2. **E-gents Regression Testing** (4-6 hours)
   - [ ] Create `agents/e/regression_validator.py`
   - [ ] Integrate T-gents `RegressionOracle`
   - [ ] Add regression check to E-gents experiment validation
   - [ ] Test: Add regression tests to `test_e_gents_demo.py`

3. **Unify Judge Interface** (3-4 hours)
   - [ ] Create `agents/shared/judge.py` (or promote to C-gents)
   - [ ] Extract common `JudgeAgent` protocol
   - [ ] Refactor T-gents Judge → `SemanticJudge`
   - [ ] Refactor E-gents Judge → `PrincipleJudge`
   - [ ] Create `HybridJudge` composition
   - [ ] Update E-gents to optionally use semantic judge
   - [ ] Test: `test_judge_integration.py`

**Deliverables**:
- `agents/shared/ast_utils.py`
- `agents/e/regression_validator.py`
- `agents/shared/judge.py`
- Updated tests
- HYDRATE.md updated with Phase 4A completion

---

### Phase 4B: Abstraction Layer (2-3 weeks)

**Goal**: Extract reusable patterns into C-gents or shared modules.

1. **ValidationPipeline Abstraction** (8-12 hours)
   - [ ] Design `ValidationLayer` protocol
   - [ ] Create `agents/c/validation.py`
   - [ ] Implement `ValidationPipeline` composition
   - [ ] Refactor E-gents to use ValidationPipeline
   - [ ] Refactor J-gents to use ValidationPipeline
   - [ ] Test: `test_validation_pipeline.py`

2. **Property-Based Evolution Testing** (6-8 hours)
   - [ ] Create `agents/e/property_validator.py`
   - [ ] Integrate T-gents `PropertyAgent`
   - [ ] Add property tests: type preservation, no exceptions, idempotence
   - [ ] Add to E-gents experiment validation pipeline
   - [ ] Test: Add property tests to E-gents demo

3. **ResilientAgent Wrapper** (10-15 hours)
   - [ ] Design `RetryConfig`, `FallbackConfig`, `BackoffStrategy`
   - [ ] Create `agents/c/resilient.py`
   - [ ] Implement `ResilientAgent` wrapper
   - [ ] Refactor E-gents retry/fallback to use ResilientAgent
   - [ ] Add resilience wrappers to J-gents JIT pipeline
   - [ ] Test: Use T-gents `FlakyAgent` to validate retry logic
   - [ ] Test: `test_resilient_agent.py`

**Deliverables**:
- `agents/c/validation.py`
- `agents/e/property_validator.py`
- `agents/c/resilient.py`
- Updated E-gents and J-gents to use abstractions
- HYDRATE.md updated with Phase 4B completion

---

### Phase 4C: Exploratory Integration (3-4 weeks)

**Goal**: Research-level integrations with high potential impact.

1. **Meta-Circular Evolution** (20-30 hours)
   - [ ] Write spec: `spec/meta/circular.md`
   - [ ] Design `MetaCircularAgent` architecture
   - [ ] Create `agents/meta/circular.py`
   - [ ] Implement: MetaArchitect → E-gents → Chaosmonger pipeline
   - [ ] Add convergence detection
   - [ ] Sandbox execution with safety checks
   - [ ] Test: Generate simple agent, evolve it, validate improvement
   - [ ] Test: Self-evolution (meta-circular agent improves itself)

2. **Reality Classification in E-gents** (8-12 hours)
   - [ ] Add J-gents Reality import to E-gents
   - [ ] Create `SmartEvolutionAgent` with reality triage
   - [ ] Classify improvement tasks: DETERMINISTIC/PROBABILISTIC/CHAOTIC
   - [ ] Skip chaotic improvements or use conservative fallback
   - [ ] Test: Verify reality classification improves success rate

3. **D-gents Memory Layer** (15-20 hours)
   - [ ] Write spec: `spec/d-gents/memory.md`
   - [ ] Create `agents/d/memory.py`
   - [ ] Extract E-gents `ImprovementMemory` → `JSONFileMemory`
   - [ ] Implement `AgentMemory` protocol
   - [ ] Add memory backends: JSON, SQLite, Redis
   - [ ] Refactor E-gents to use D-gents memory
   - [ ] Add memory to T-gents (test results persistence)
   - [ ] Add memory to J-gents (promise cache)
   - [ ] Test: `test_agent_memory.py`

**Deliverables**:
- `spec/meta/circular.md`
- `agents/meta/circular.py`
- `spec/d-gents/memory.md`
- `agents/d/memory.py`
- Updated E-gents, T-gents, J-gents to use D-gents memory
- Demo: Self-improving agent
- HYDRATE.md updated with Phase 4C completion

---

### Phase 4D: Polish & Documentation (1 week)

**Goal**: Final cleanup, comprehensive documentation, demo videos.

1. **Similarity Metrics** (4-6 hours)
   - [ ] Create `agents/c/similarity.py`
   - [ ] Extract E-gents similarity functions
   - [ ] Add T-gents equality functions
   - [ ] Implement: Levenshtein, Structural, Semantic, Numerical
   - [ ] Refactor genera to use shared similarity
   - [ ] Test: `test_similarity.py`

2. **T-gents Chaosmonger Integration** (3-4 hours)
   - [ ] Add stability validation to T-gents fixture loading
   - [ ] Create `SafeFixtureAgent` wrapper
   - [ ] Test: Reject malicious fixture code

3. **Documentation Updates** (6-8 hours)
   - [ ] Update `spec/c-gents/integration.md` with new abstractions
   - [ ] Write `spec/synergy-patterns.md` documenting cross-genus usage
   - [ ] Update README.md with Phase 4 achievements
   - [ ] Create demo scripts:
     - `demo_regression_testing.py`
     - `demo_meta_circular.py`
     - `demo_reality_classification.py`
   - [ ] Update HYDRATE.md with Phase 4 complete

**Deliverables**:
- `agents/c/similarity.py`
- `agents/t/safe_fixture.py`
- `spec/synergy-patterns.md`
- `spec/c-gents/integration.md` (updated)
- Demo scripts
- HYDRATE.md Phase 4 complete

---

## Anti-Patterns to Avoid

1. **Don't Merge Genera**: Keep T, J, E as distinct identities. Extract shared code to C-gents or `agents/shared/`, not into one genus.

2. **Don't Extract Prematurely**: Only create abstractions when pattern appears in 2+ genera and is genuinely reusable.

3. **Don't Break Tests**: All existing tests must pass after refactoring. Maintain backward compatibility.

4. **Don't Skip Specs**: Write spec before implementation. Implementation follows specification.

5. **Don't Over-Engineer**: Simple is better than complex. If abstraction is harder to use than duplication, don't extract it.

6. **Don't Lose Composability**: Every extracted abstraction must be a proper morphism with clear input/output types.

---

## Success Criteria

### Phase 4A Success:
- [ ] All tests passing (T-gents, J-gents, E-gents)
- [ ] AST utils shared and tested
- [ ] E-gents uses T-gents regression testing
- [ ] Judge interface unified, both semantic and principle evaluation available

### Phase 4B Success:
- [ ] ValidationPipeline used in E-gents and J-gents
- [ ] Property-based testing validates evolved code
- [ ] ResilientAgent provides retry/fallback across genera
- [ ] No duplicated validation or retry logic

### Phase 4C Success:
- [ ] Meta-circular agent generates and evolves agents
- [ ] Reality classification improves E-gents success rate
- [ ] D-gents memory layer used by all three genera
- [ ] Persistent state across sessions

### Phase 4D Success:
- [ ] All code documented and tested
- [ ] Demo scripts showcase cross-genus synergies
- [ ] Spec files updated with integration patterns
- [ ] HYDRATE.md reflects complete Phase 4

---

## File References

### Current Implementation Files

**T-gents**:
- `/Users/kentgang/git/kgents/impl/claude/agents/t/judge.py` (LLM Judge)
- `/Users/kentgang/git/kgents/impl/claude/agents/t/oracle.py` (Regression Oracle)
- `/Users/kentgang/git/kgents/impl/claude/agents/t/property.py` (Property Testing)

**J-gents**:
- `/Users/kentgang/git/kgents/impl/claude/agents/j/chaosmonger.py` (AST Stability)
- `/Users/kentgang/git/kgents/impl/claude/agents/j/meta_architect.py` (JIT Compilation)
- `/Users/kentgang/git/kgents/impl/claude/agents/j/sandbox.py` (Safe Execution)
- `/Users/kentgang/git/kgents/impl/claude/agents/j/reality.py` (Reality Classification)

**E-gents**:
- `/Users/kentgang/git/kgents/impl/claude/agents/e/judge.py` (Principle Judge)
- `/Users/kentgang/git/kgents/impl/claude/agents/e/safety.py` (Uses Chaosmonger)
- `/Users/kentgang/git/kgents/impl/claude/agents/e/ast_analyzer.py` (AST Analysis)
- `/Users/kentgang/git/kgents/impl/claude/agents/e/retry.py` (Retry Logic)
- `/Users/kentgang/git/kgents/impl/claude/agents/e/fallback.py` (Fallback Logic)
- `/Users/kentgang/git/kgents/impl/claude/agents/e/memory.py` (Improvement Memory)

### New Files to Create

**Phase 4A**:
- `/Users/kentgang/git/kgents/impl/claude/agents/shared/ast_utils.py`
- `/Users/kentgang/git/kgents/impl/claude/agents/e/regression_validator.py`
- `/Users/kentgang/git/kgents/impl/claude/agents/shared/judge.py`

**Phase 4B**:
- `/Users/kentgang/git/kgents/impl/claude/agents/c/validation.py`
- `/Users/kentgang/git/kgents/impl/claude/agents/e/property_validator.py`
- `/Users/kentgang/git/kgents/impl/claude/agents/c/resilient.py`

**Phase 4C**:
- `/Users/kentgang/git/kgents/spec/meta/circular.md`
- `/Users/kentgang/git/kgents/impl/claude/agents/meta/circular.py`
- `/Users/kentgang/git/kgents/spec/d-gents/memory.md`
- `/Users/kentgang/git/kgents/impl/claude/agents/d/memory.py`

**Phase 4D**:
- `/Users/kentgang/git/kgents/impl/claude/agents/c/similarity.py`
- `/Users/kentgang/git/kgents/spec/synergy-patterns.md`

---

## Conclusion

This plan maximizes synergy between T-gents, J-gents, and E-gents while preserving their distinct identities. The roadmap is progressive:

1. **Phase 4A**: Quick wins (AST utils, regression testing, unified judge)
2. **Phase 4B**: Abstractions (validation pipeline, resilient wrapper, property testing)
3. **Phase 4C**: Exploratory (meta-circular evolution, D-gents memory)
4. **Phase 4D**: Polish (similarity metrics, docs, demos)

Each phase builds on the previous, with clear deliverables and success criteria. The result will be a tightly integrated agent ecosystem where each genus enhances the others while maintaining composability and testability.

**Next Step**: Start Phase 4A with AST utilities extraction.
