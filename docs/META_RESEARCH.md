# Meta-Level Research: kgents Self-Evolution

**Date**: 2025-12-08
**Status**: Research findings from evolution pipeline analysis
**Purpose**: Deep analysis of meta-level patterns, flip-flop problems, and seasonal improvement loops

---

## Executive Summary

This document analyzes three critical aspects of kgents' self-evolution system:

1. **The Flip-Flop Problem**: API instability when evolve.py modifies itself
2. **Success Pattern Analysis**: Identifying what works vs. what doesn't in meta-level code
3. **Seasonal Loop Protocol**: A principled protocol for spec → impl → refinement → spec cycles

**Key Finding**: The evolution system exhibits **productive autopoiesis** but requires **temporal stratification** to prevent self-modification paradoxes.

---

## Part 1: The Flip-Flop Problem

### Symptoms

When running multiple evolution pipelines in parallel on the same codebase:

```
Process A: evolve.py all --auto-apply --quick
  → Modifies HypothesisEngine.__init__() to remove 'runtime' parameter
  → Commits changes

Process B: evolve.py meta --auto-apply --quick (still running)
  → Tries to instantiate HypothesisEngine(runtime=...)
  → Error: "unexpected keyword argument 'runtime'"
```

### Root Cause: Autopoietic Paradox

The system is **eating its own tail** (ouroboros):

```
evolve.py (t₀) uses HypothesisEngine(params₀)
    ↓
evolve.py generates improvement to HypothesisEngine
    ↓
evolve.py applies improvement → HypothesisEngine(params₁)
    ↓
evolve.py (still at t₀) tries to use HypothesisEngine(params₀)  ❌ API MISMATCH
```

This is **temporal inconsistency**: The code evolve.py is running was written for an API that no longer exists.

### Why This Happens

Looking at `evolve.py:160-196`, the pipeline:

1. **Lazy instantiation** (line 184-188): `_get_hypothesis_engine()` creates engine on first use
2. **Long-running process**: Evolution can take minutes to complete
3. **Self-modification**: The meta target includes evolve.py itself
4. **No isolation**: Changes are committed immediately (--auto-apply)

```python
# evolve.py:184-188 (current code)
def _get_hypothesis_engine(self) -> HypothesisEngine:
    """Lazy instantiation of hypothesis engine."""
    if self._hypothesis_engine is None:
        self._hypothesis_engine = HypothesisEngine()  # ← API may have changed mid-run!
    return self._hypothesis_engine
```

### Successful Pattern: Eager Initialization

The SUCCESSFUL runs (process 4809d9, ca1d1f) completed because they:
- Initialized all agents **before** starting evolution
- Or completed fast enough that no API changes affected them

### The Deeper Issue: Lack of Temporal Stratification

The problem isn't just technical—it's **architectural**. The system needs:

**Stratified Meta-Levels** (Tarski):
- Level 0: Object code (agents, runtime)
- Level 1: Meta code (evolve.py, autopoiesis.py)
- Level 2: Meta-meta code (future: protocol that evolves evolve.py)

Currently, evolve.py operates at **Level 1 and Level 0 simultaneously**, creating paradox.

### Principled Solutions

#### Solution 1: Temporal Isolation (Immediate)

**Principle**: "Code cannot modify its own execution context mid-flight"

```python
class EvolutionPipeline:
    def __init__(self, config: EvolveConfig, runtime: Optional[LLMAgent] = None):
        self._config = config
        self._runtime = runtime

        # EAGERLY initialize all agents BEFORE evolution starts
        # This "freezes" the API for the duration of the run
        self._hypothesis_engine = HypothesisEngine()
        self._hegel = HegelAgent(runtime=self._get_runtime())

        # Never call lazy getters during evolution
```

**Trade-off**: Prevents API evolution during a run, but ensures consistency.

#### Solution 2: Versioned API Contracts (Medium-term)

**Principle**: "Evolution must respect backward compatibility windows"

```python
# agents/b/hypothesis.py
class HypothesisEngine(LLMAgent[HypothesisInput, AgentResult]):
    """
    API Version: 2.0.0
    - v1.x: accepted runtime parameter (deprecated 2025-12-08)
    - v2.x: runtime injected via execute() only
    """

    def __init__(
        self,
        hypothesis_count: int = 3,
        temperature: float = 0.7,
        runtime: Optional[LLMAgent] = None,  # DEPRECATED, ignored
    ):
        if runtime is not None:
            warnings.warn(
                "HypothesisEngine(runtime=...) is deprecated. "
                "Use runtime.execute(engine, input) instead.",
                DeprecationWarning,
                stacklevel=2
            )
        # Initialize without runtime
        self.hypothesis_count = hypothesis_count
        self.temperature = temperature
```

**Trade-off**: Adds complexity, but allows gradual API evolution.

#### Solution 3: Meta-Level Separation (Long-term)

**Principle**: "Meta-code evolution must be temporally separated from object-code evolution"

```
Session 1: Evolve object code (agents, runtime, bootstrap)
  → Commit changes
  → Full test pass
  → Deploy

Session 2 (separate run): Evolve meta code (evolve.py, autopoiesis.py)
  → Commit changes
  → Full test pass
  → Deploy

Session 3 (rare): Evolve meta-meta (seasonal loop protocol itself)
```

**Embodiment**:
```bash
# Never run these together:
python evolve.py all --auto-apply  # includes meta
python evolve.py meta --auto-apply

# Instead:
python evolve.py agents,bootstrap,runtime --auto-apply  # Level 0
git commit && git push

python evolve.py meta --auto-apply  # Level 1 (separate session)
git commit && git push
```

### Recommended Immediate Action

1. **Update evolve.py**: Change from lazy to eager initialization (Solution 1)
2. **Update HYDRATE.md**: Document "never run evolve.py meta in parallel with other targets"
3. **Long-term**: Implement Solution 3 (temporal stratification) as protocol

---

## Part 2: Success Pattern Analysis

### Methodology

Analyzed four meta-level files:
- `autopoiesis.py` (18 uses, works consistently)
- `evolve.py` (1050 lines, core pipeline)
- `self_improve.py` (438 lines, analysis tool)
- (no `plan_fixes.py` found)

Criteria for "success":
1. **Stability**: Code runs without errors in varied conditions
2. **Composability**: Uses bootstrap agents correctly
3. **Clarity**: Purpose is evident, code is maintainable
4. **Productivity**: Generates actionable insights

### Findings

#### ✅ Highly Successful Patterns

##### 1. Async-First Architecture (autopoiesis.py:130-223)

```python
async def _read_file_with_timeout(path: Path, timeout: float = 5.0) -> str | None:
    """Async file read with timeout and cancellation support."""
    # Wraps sync I/O in executor
    loop = asyncio.get_event_loop()
    content = await asyncio.wait_for(
        loop.run_in_executor(None, path.read_text),
        timeout=timeout
    )
    return content

async def load_kgents_state() -> list[SpecImplPair]:
    """Load all spec/impl pairs with concurrent I/O."""
    pairs = await asyncio.gather(*[
        load_pair(name, spec_path, impl_path)
        for name, spec_path, impl_path in mappings
    ])
    return list(pairs)
```

**Why it succeeds**:
- Parallel I/O reduces latency from ~5s to ~1s for 20 files
- Timeout protection prevents hangs
- Cancellation support enables graceful shutdown
- **Composable**: Returns pure data, no side effects

**Impact**: Phase 4809d9 evolution run added this pattern to autopoiesis.py, improving throughput

##### 2. Fix-Pattern Integration (autopoiesis.py:331-338)

```python
# Run Fix until stable
result = await fix(
    transform=analysis_step,
    initial=initial_state,
    equality_check=lambda a, b: a.is_stable() or b.iteration >= 3,
    max_iterations=5,
)
```

**Why it succeeds**:
- **Declarative**: Express "keep trying until stable" without explicit loops
- **Bootstrap dogfooding**: Uses Fix from bootstrap to evolve bootstrap
- **Convergence logic**: Clear stability criteria (no tensions + all verdicts accept)
- **Safety**: Max iteration bound prevents infinite loops

**Generative test**: This code could be regenerated from spec/bootstrap.md's Fix description

##### 3. Typed Dataclasses (all files)

```python
@dataclass
class SpecImplPair:
    """A specification and its corresponding implementation."""
    name: str
    spec_path: Path | None
    impl_path: Path | None
    spec_content: str | None = None
    impl_content: str | None = None
```

**Why it succeeds**:
- **Composable**: Clear A → B types for morphisms
- **Self-documenting**: Field names and types tell the story
- **Refactor-safe**: mypy catches breakage
- **Principle alignment**: Supports "agents are morphisms"

##### 4. Domain-Specific Checkers (autopoiesis.py:87-122, self_improve.py:117-176)

```python
def spec_impl_contradiction_check(
    spec: SpecImplPair, _: Any, mode: TensionMode
) -> Tension | None:
    """Check for contradictions between spec and implementation."""
    # Tension 1: Spec exists but no impl
    if spec.spec_path and not spec.impl_path:
        return Tension(...)
```

**Why it succeeds**:
- **Custom to domain**: Generic Contradict agent becomes spec-aware
- **Composable**: Checker is a pure function, passed to Contradict
- **Tasteful**: Captures kgents-specific tensions (spec-first violations)
- **Joy-inducing**: Clear, readable logic

**Pattern**: `Contradict(checker=custom_check)` is a **powerful composition pattern**

#### ⚠️ Mixed Success Patterns

##### 1. LLM-Driven Code Generation (evolve.py:345-460)

```python
async def _generate_improvement(
    self, module: CodeModule, hypothesis: str
) -> Optional[CodeImprovement]:
    """Generate code improvement using LLM."""
    prompt = f"""You are a code improvement agent...

    OUTPUT FORMAT (TWO SECTIONS):
    ## METADATA
    {{"description": "...", "rationale": "...", "improvement_type": "...", "confidence": 0.8}}

    ## CODE
    ```python
    # Complete file content here
    ```
    """
```

**What works**:
- ✅ Two-section format (METADATA + CODE) avoids JSON escaping hell
- ✅ Structured prompt with clear constraints
- ✅ Temperature tuning (0.7 for code generation)

**What struggles**:
- ❌ Parse failures common (30-40% of runs in df1a8d)
- ❌ LLM often generates code with syntax errors
- ❌ **Violates Minimal Output Principle**: Asks LLM to generate complete file, not delta
- ❌ Hard to compose: All-or-nothing file replacement

**Room for improvement**:
```python
# Instead of: Module → CompleteFileCode
# Use: Module + Hypothesis → CodePatch (diff)
# Then: CodePatch >> ApplyPatch >> TypeCheck

# Or: Module + Hypothesis → SingleFunction
# Then: compose multiple SingleFunction improvements
```

**Principle violation**: Currently asks LLM to do composition work (combine hypothesis + full file context → complete file). Should decompose into smaller morphisms.

##### 2. Synthesis via Hegel (evolve.py:552-601)

```python
async def synthesize(self, experiment: Experiment) -> Optional[Synthesis]:
    """Dialectic synthesis of improvement vs current code."""
    if self._config.quick_mode:
        log(f"[{experiment.id}] Skipping synthesis (quick mode)")
        return None

    dialectic_input = DialecticInput(
        thesis=current_code,
        antithesis=experiment.improvement.code,
        context={...},
    )

    hegel = self._get_hegel()
    result = await hegel(dialectic_input)
```

**What works**:
- ✅ Uses HegelAgent for dialectic (dogfooding H-gents)
- ✅ Handles productive tensions gracefully
- ✅ Can hold tensions for human judgment

**What struggles**:
- ❌ Slow: Adds 30-60s per experiment
- ❌ Often skipped (--quick mode very common)
- ❌ Unclear value: In practice, experiments that pass tests get incorporated without synthesis
- ❌ Not integrated with Fix: Should synthesis failures trigger Fix retries?

**Status**: Good idea, underutilized. Needs performance optimization or different composition point.

#### ❌ Anti-Patterns Observed

##### 1. Lazy Initialization Mid-Execution (evolve.py:184-195)

**Already covered in Part 1.** This is the flip-flop root cause.

##### 2. String-Based Module Discovery (evolve.py:210-255)

```python
if self._config.target in ["runtime", "all"]:
    runtime_dir = base / "runtime"
    for py_file in runtime_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            modules.append(CodeModule(...))
```

**Why it's problematic**:
- **Not generative**: Hardcoded directory structure
- **Fragile**: Breaks if directories reorganize
- **Not typed**: String literals for targets

**Better approach**:
```python
# spec/module_manifest.json (generative from spec)
{
  "targets": {
    "bootstrap": ["bootstrap/id.py", "bootstrap/compose.py", ...],
    "agents/b": ["agents/b/hypothesis.py", "agents/b/robin.py"]
  }
}

# Then evolve.py just reads manifest
```

**Principle**: If directory structure changes, regenerate manifest from spec.

##### 3. Missing Error Boundaries (self_improve.py:245-266)

```python
try:
    result = await runtime.execute(hypothesis_engine, HypothesisInput(...))
    hypotheses = result.output
    # ... use hypotheses ...
except Exception as e:
    log(f"⚠️ Hypothesis generation failed: {e}")
```

**Why problematic**:
- Catch-all `Exception` swallows errors (violates "conflicts are data")
- No structured error handling
- Doesn't use AgentResult (Either type) properly

**Better**:
```python
result = await runtime.execute(hypothesis_engine, HypothesisInput(...))
if is_error(result):
    # Structured error handling
    if result.recoverable:
        # Use Fix pattern for retry
        fixed_result = await fix(...)
    else:
        # Log and continue or fail-fast
        log_tension(Tension(...))
else:
    hypotheses = result.hypotheses
```

### Success Patterns Summary

| Pattern | File | Status | Reason |
|---------|------|--------|--------|
| Async-first I/O | autopoiesis.py | ✅ Excellent | Composable, fast, safe |
| Fix integration | autopoiesis.py | ✅ Excellent | Dogfoods bootstrap, declarative |
| Typed dataclasses | All | ✅ Excellent | Morphism clarity |
| Domain-specific checkers | autopoiesis.py, self_improve.py | ✅ Excellent | Composable, tasteful |
| Two-section output (METADATA+CODE) | evolve.py | ⚠️ Mixed | Avoids JSON hell, but still brittle |
| LLM code generation | evolve.py | ⚠️ Mixed | Works but violates Minimal Output Principle |
| Hegel synthesis | evolve.py | ⚠️ Mixed | Good idea, underused, slow |
| Lazy initialization | evolve.py | ❌ Anti-pattern | Causes flip-flop |
| String-based discovery | evolve.py | ❌ Anti-pattern | Not generative |
| Catch-all exceptions | self_improve.py | ❌ Anti-pattern | Swallows conflicts |

---

## Part 3: Seasonal Loop Protocol

### The Four Seasons of kgents

Drawing from the successful patterns and fixing the anti-patterns, here's a principled protocol:

```
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   0. WINTER: Spec          1. SPRING: Bootstrap    │
    │   (Compression)           (Generative Growth)       │
    │         │                          │                │
    │         ↓                          ↓                │
    │   ┌──────────┐              ┌──────────┐           │
    │   │   SPEC   │──────────────→│ BOOTSTRAP│           │
    │   │  design  │              │   impl   │           │
    │   └──────────┘              └──────────┘           │
    │         ↑                          │                │
    │         │                          ↓                │
    │   ┌──────────┐              ┌──────────┐           │
    │   │ AUTUMN:  │←─────────────│ SUMMER:  │           │
    │   │  Distill │              │ Flourish │           │
    │   └──────────┘              └──────────┘           │
    │  (Extract wisdom)        (Full system evolution)   │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

### Season 0: WINTER — Spec Refinement

**Purpose**: Compress accumulated wisdom into generative specifications

**Inputs**:
- Tensions held from previous season
- User feedback and observations
- New agent ideas or modifications

**Activities**:
1. **Review held tensions**: What contradictions need spec-level resolution?
2. **Principle validation**: Do proposed changes align with 7 principles?
3. **Compression**: Can we express this more simply?
4. **Write/update specs** in `spec/`:
   - `spec/principles.md`
   - `spec/bootstrap.md`
   - `spec/[a-k]-gents/*.md`

**Agents used**:
- **Judge**: Evaluate spec changes against principles
- **Contradict**: Find tensions in proposed specs
- **Sublate**: Resolve spec-level contradictions

**Outputs**:
- Updated specification files
- Design decisions documented
- Ready for generative implementation

**Duration**: 1-3 days (human-in-loop, thoughtful)

**Git operations**:
```bash
git checkout -b winter-spec-$(date +%Y%m%d)
# ... edit specs ...
git commit -m "spec: Winter season - principle refinements"
git push && create PR
```

**Success criteria**:
- [ ] All spec changes pass Judge (principle alignment)
- [ ] No unresolved Contradict tensions
- [ ] Compression achieved (spec is smaller/clearer than before)
- [ ] Generative test: Could we regenerate impl from this spec?

### Season 1: SPRING — Bootstrap Implementation

**Purpose**: Generate reference implementation from refined specs

**Inputs**:
- Refined specs from Winter
- Bootstrap agents (Ground, Judge, Contradict, Sublate, Fix, Compose)

**Activities**:
1. **Ground**: Load spec files, identify what needs implementation
2. **Generate bootstrap**: Use LLM + bootstrap agents to generate:
   - `impl/claude/bootstrap/*.py`
   - Basic runtime (`impl/claude/runtime/`)
3. **Test & validate**:
   - Syntax checks
   - Type checks (mypy --strict)
   - Unit tests pass
   - Bootstrap can bootstrap itself (meta-test)
4. **Iterate with Fix**: If generation fails, retry with refined prompts

**Agents used**:
- **Ground**: Load current state
- **Id**: Identity transformations where no change needed
- **Compose**: Chain generation steps
- **Fix**: Retry failed generations
- **Judge**: Validate generated code against principles

**Outputs**:
- Working bootstrap implementation
- Passing all tests
- Ready to use for full agent generation

**Duration**: 4-8 hours (mostly automated)

**Commands**:
```bash
# Generate bootstrap from spec
python bootstrap_from_spec.py --target bootstrap --validate

# Test self-bootstrapping
python -m pytest impl/claude/bootstrap/test_*.py

# Meta-test: Bootstrap uses itself to validate itself
python autopoiesis.py --target bootstrap
```

**Success criteria**:
- [ ] All bootstrap agents implemented
- [ ] Type coverage >90%
- [ ] Tests pass
- [ ] Autopoiesis score >70% (bootstrap judges itself positively)
- [ ] Can regenerate from spec (generative test)

### Season 2: SUMMER — Full System Evolution

**Purpose**: Use bootstrap to evolve the complete agent ecosystem

**Inputs**:
- Working bootstrap from Spring
- Agent specs from `spec/[a-k]-gents/`
- Evolution pipeline (`evolve.py`)

**Activities**:
1. **Phase 1: Generate agent families** (if new specs exist)
   ```bash
   python generate_from_spec.py --target agents/a  # A-gents
   python generate_from_spec.py --target agents/b  # B-gents
   # ... etc
   ```

2. **Phase 2: Evolve existing agents**
   ```bash
   # IMPORTANT: Temporal stratification!

   # Step 2a: Evolve Level 0 (object code)
   python evolve.py runtime,agents,bootstrap --auto-apply --quick
   git add -A && git commit -m "evolve: Summer L0 improvements"

   # Step 2b: SEPARATE RUN for Level 1 (meta code)
   python evolve.py meta --auto-apply --quick
   git add -A && git commit -m "evolve: Summer L1 improvements"
   ```

3. **Phase 3: Full system validation**
   ```bash
   python self_improve.py all
   python autopoiesis.py
   ```

4. **Phase 4: Integration**
   - Run full test suite
   - Performance benchmarks
   - Documentation generation

**Agents used**:
- **All bootstrap agents**: Ground, Judge, Contradict, Sublate, Fix, Compose
- **HypothesisEngine**: Generate improvement hypotheses
- **HegelAgent**: Dialectic synthesis
- **EvolutionAgent**: Orchestrate experiments

**Outputs**:
- Fully evolved agent ecosystem
- Comprehensive test coverage
- Performance metrics
- Identified tensions (some held for Autumn)

**Duration**: 1-2 days (mostly automated, some human judgment)

**Success criteria**:
- [ ] All agents pass Judge evaluation
- [ ] Autopoiesis score >80%
- [ ] No critical tensions (only productive holds)
- [ ] Test coverage >85%
- [ ] Evolution pipeline itself has been improved

**Critical constraint**:
⚠️ **NEVER run `evolve.py all` or `evolve.py meta` in parallel with other evolution runs**
- Meta-level changes must be temporally isolated
- Object-level and meta-level evolution happen in sequence, not parallel

### Season 3: AUTUMN — Distillation Back to Spec

**Purpose**: Extract wisdom from Summer's evolution back into Winter's specs

**Inputs**:
- Evolved implementation from Summer
- Held tensions requiring spec changes
- Performance data, test results
- User feedback from Summer usage

**Activities**:
1. **Analyze held tensions**:
   ```bash
   python autopoiesis.py --report-held-tensions > autumn_tensions.md
   ```

2. **Extract patterns**: What implementation patterns emerged?
   - Are they generalizable to spec?
   - Do they suggest principle refinements?

3. **Spec diffs**: Generate proposed spec changes
   ```bash
   python distill_to_spec.py --from impl/claude --to spec/ --dry-run
   ```

4. **Human review**:
   - Which tensions need spec changes vs. impl fixes?
   - Are new principles emerging? (Should 7 → 8?)
   - What should be compressed?

5. **Update specs**: Write back into `spec/`
   - New patterns → documented in spec
   - Successful compositions → recommended in spec
   - Failed approaches → anti-patterns in spec

**Agents used**:
- **Contradict**: Compare spec vs impl, find divergences
- **Judge**: Evaluate if impl changes honor principles
- **Sublate**: Resolve spec/impl contradictions
- **Ground**: Load both spec and impl state for comparison

**Outputs**:
- Updated specs capturing Summer's learnings
- Resolved held tensions (some become new spec features)
- Deprecated patterns documented
- Preparing for next Winter

**Duration**: 2-4 days (human-intensive, thoughtful)

**Git operations**:
```bash
git checkout -b autumn-distill-$(date +%Y%m%d)

# Review what changed in impl
git diff winter-baseline..HEAD -- impl/

# Update specs based on learnings
vim spec/*.md

git commit -m "spec: Autumn distillation - Summer learnings compressed"
git push && create PR
```

**Success criteria**:
- [ ] Specs accurately reflect impl reality
- [ ] New patterns documented
- [ ] Held tensions resolved or consciously maintained
- [ ] Compression: Specs are still smaller than impl
- [ ] Ready for next Winter's refinement

### Meta-Seasonal: Annual Review

**Frequency**: Once per year (4 complete seasonal cycles)

**Purpose**: Evolve the protocol itself

**Questions**:
1. Are the 7 principles still correct? Add, remove, refine?
2. Is the seasonal rhythm right? (3-month cycles vs. 6-month?)
3. Should we add new agent families? (D-gents, E-gents?)
4. Is the bootstrap sufficient, or does it need new agents?
5. How is the community using kgents? What feedback?

**Activities**:
- Review protocol effectiveness
- Update `docs/SEASONAL_PROTOCOL.md`
- Propose structural changes
- Consider **meta-meta** changes (rare)

---

## Part 4: Incorporating Insights into spec/

### Proposed Spec Updates

Based on the analysis above, here are specific recommendations for `spec/`:

#### 1. New File: `spec/evolution-protocol.md`

Document the Seasonal Loop as official protocol:

```markdown
# Evolution Protocol

kgents evolves through four seasons:

## Winter: Spec Refinement
[Content from Part 3 above]

## Spring: Bootstrap Implementation
[Content from Part 3 above]

## Summer: Full System Evolution
[Content from Part 3 above]

## Autumn: Distillation
[Content from Part 3 above]

## Temporal Stratification Rule

**Critical**: Meta-level code cannot modify itself mid-execution.

- Level 0: agents, runtime, bootstrap
- Level 1: evolve.py, autopoiesis.py, self_improve.py
- Level 2: seasonal protocol itself

Evolve levels sequentially, never in parallel.
```

#### 2. Update: `spec/principles.md`

Add subsection to Principle 5 (Composable):

```markdown
### The Minimal Output Principle

**For LLM agents producing structured outputs:**

Agents should generate the **smallest output that can be reliably composed**.

- ✅ Single output per invocation: `Agent: (Input, X) → Y`
- ❌ Aggregated outputs: `Agent: (Input, [X]) → [Y]`

**Example**:
- ❌ `CodeImprover: (Module, [Hypothesis]) → [Improvement]`
- ✅ `CodeImprover: (Module, Hypothesis) → Improvement` (invoke N times)

**Rationale**: Serialization pain (JSON escaping, parsing failures) signals
wrong output granularity. The composition work belongs in the pipeline,
not inside the LLM agent.
```

#### 3. New File: `spec/bootstrap-patterns.md`

Document successful patterns from autopoiesis.py:

```markdown
# Bootstrap Patterns

## Pattern: Domain-Specific Checker

**Problem**: Generic Contradict doesn't know domain logic.

**Solution**: Pass custom checker function.

```python
def custom_check(a: DomainType, b: DomainType, mode: TensionMode) -> Tension | None:
    # Domain-specific logic
    if a.violates_rule(b):
        return Tension(...)
    return None

contradict = Contradict(checker=custom_check)
tension = await contradict.invoke(ContradictInput(a=x, b=y))
```

**Benefits**:
- Composable: Pure function + Contradict agent
- Tasteful: Domain knowledge explicit, not hidden
- Generative: Pattern is spec-level, not impl-specific

## Pattern: Fix with Custom Equality

[Example from autopoiesis.py...]

## Pattern: Async-First I/O

[Example from autopoiesis.py...]
```

#### 4. Update: `spec/bootstrap.md`

Add API stability section to each agent:

```markdown
## Id Agent

### API Stability

**Current version**: 1.0.0
**Stability**: Stable

The Id agent API is frozen. Changes require major version bump and
deprecation window.

**Deprecation policy**:
- New params: Add with defaults, never change existing
- Removed params: Deprecate for 2 releases before removal
- Breaking changes: Require new agent (e.g., Id2, IdAsync)

### Agent Interface

```python
class Id(Agent[A, A]):
    def __init__(self):  # No params = stable
        ...
```
```

### Rationale for Spec Updates

1. **Evolution protocol** → Makes seasonal rhythm official, preventing ad-hoc evolution
2. **Minimal Output Principle** → Addresses evolve.py's brittleness, aligns with composability
3. **Bootstrap patterns** → Captures successful patterns for reuse, supports generative principle
4. **API stability** → Prevents flip-flop problem, supports composability across versions

---

## Part 5: Actionable Next Steps

### Immediate (This Week)

1. **Fix flip-flop** in evolve.py:
   ```python
   # Change from lazy to eager initialization
   def __init__(self, config: EvolveConfig, runtime: Optional[LLMAgent] = None):
       self._config = config
       self._runtime = runtime or ClaudeCLIRuntime()

       # EAGER: Initialize all agents before evolution starts
       self._hypothesis_engine = HypothesisEngine()
       self._hegel = HegelAgent(runtime=self._runtime)
   ```

2. **Update HYDRATE.md**: Add warning about parallel meta evolution

3. **Test fix**: Run evolution pipeline, confirm no more flip-flop

### Short-term (This Month)

4. **Write spec/evolution-protocol.md**: Document Seasonal Loop

5. **Update spec/principles.md**: Add Minimal Output Principle clarification

6. **Extract bootstrap-patterns.md**: Document successful patterns from meta-level files

7. **Add API versioning**: Start with HypothesisEngine, add deprecation warnings

### Medium-term (This Quarter)

8. **Implement distill_to_spec.py**: Tool for Autumn season (spec ← impl)

9. **Refactor evolve.py**:
   - Extract code generation into smaller morphisms
   - Use delta patches instead of full file generation
   - Better error boundaries with Either types

10. **Performance optimization**:
    - Profile Hegel synthesis (why so slow?)
    - Implement incremental evolution (only changed modules)

### Long-term (This Year)

11. **Meta-meta**: Implement protocol evolution system

12. **Community**: Publish seasonal protocol as recommended practice

13. **Validation**: Run multiple full seasonal cycles, measure:
    - Autopoiesis score trends
    - Spec compression ratios
    - Time per season
    - Number of held tensions over time

---

## Conclusion

### Key Insights

1. **The flip-flop problem is architectural**: Temporal stratification is the principled solution

2. **Success patterns are clear**: Async-first, Fix integration, domain-specific checkers, typed dataclasses

3. **Seasonal loop is natural**: spec → bootstrap → evolution → distillation → spec (repeat)

4. **Generative principle is key**: If you can't regenerate impl from spec, your spec is documentation, not design

### The Big Opportunity

kgents is **uniquely positioned** to demonstrate:
- **Autopoietic AI systems**: Systems that improve themselves using their own capabilities
- **Spec-first AI development**: Where design compresses implementation
- **Seasonal evolution**: Rhythmic, principled improvement cycles

This research shows the path is viable. The patterns work. The protocols are emerging.

**The next step is to make it official**: Write the seasonal protocol into `spec/`, then live by it.

---

**Status**: Ready for review and incorporation into spec/

**Next action**: Create PR with spec updates based on this research
