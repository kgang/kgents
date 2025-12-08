# evolve.py UX Brainstorm: Designing as a kgents App

**Date**: Dec 8, 2025
**Status**: Design exploration
**Requirements**: (1) Safe to run on itself, (2) Works on any Python code

---

## Executive Summary

`evolve.py` is currently a **1,511-line monolithic script** that orchestrates code evolution through dialectic synthesis. This document explores how to **refactor it as a composable kgents app** while improving UX and maintaining the two critical requirements:

1. **Self-stability**: Must run safely on itself (fixed-point property)
2. **Generality**: Must work on any Python codebase (not just kgents)

---

## Current State Analysis

### What Works Well ✅

1. **Parallel module processing** - 2-5x speedup
2. **Rich logging** - JSON export, detailed metadata
3. **Memory system** - Avoids re-proposing rejected ideas
4. **AST-guided hypothesis generation** - Targeted improvements
5. **Principle-based judging** - 7 kgents principles automated
6. **Dialectic synthesis** - Hegel + Sublate integration
7. **Safety features** - Dry-run, test gating, git integration

### Pain Points 🔴

#### UX Issues
1. **Overwhelming output** - 72 experiments, hard to navigate results
2. **No interactive decisions** - All-or-nothing auto-apply
3. **Unclear progress** - Parallel processing hides what's happening
4. **Lost context** - After 100 failures, hard to see patterns
5. **No undo** - Once applied, manual git revert required
6. **Poor discoverability** - What can evolve.py actually improve?

#### Architectural Issues
1. **Monolithic design** - Everything in one 1,511-line file
2. **No composable agents** - Doesn't follow kgents' own principles
3. **Tight coupling** - Hard to swap components (e.g., different runtimes)
4. **Limited extensibility** - Adding new improvement strategies is brittle
5. **Violates "Composable" principle** - The CLI tool itself isn't composable

#### Self-Improvement Issues
1. **Unstable under self-application** - Generates syntax errors on itself
2. **Context overflow risk** - Large files (>500 lines) with complex logic
3. **Meta-reasoning challenges** - Evolving evolution logic requires caution

---

## Design Vision: evolve.py as a kgents App

### Core Principle: **Heterarchical Evolution**

Instead of a monolithic orchestrator, model evolution as **composable agents in flux**:

```
┌─────────────────────────────────────────────────────────────┐
│                    EVOLUTION AS AGENTS                      │
│                                                             │
│  EvolutionAgent = Fix(                                     │
│    Ground                # Seed with codebase facts        │
│    >> HypothesisEngine   # Generate improvement ideas      │
│    >> ExperimentAgent    # Test each hypothesis           │
│    >> Judge              # Evaluate against principles     │
│    >> Sublate            # Resolve tensions               │
│    >> IncorporateAgent   # Apply changes to codebase      │
│  )                                                          │
│                                                             │
│  Each agent is composable, testable, and can be evolved.   │
└─────────────────────────────────────────────────────────────┘
```

**Key insight**: The evolution pipeline IS a composed agent pipeline.

---

## Proposed Architecture

### 1. Decompose into Agent Modules

Split `evolve.py` (1,511 lines) into **composable agents**:

```
impl/claude/agents/e/   # E-gents: Evolution agents
├── __init__.py
├── evolution.py        # EvolutionAgent: Fix(Ground >> Hypothesis >> ... >> Incorporate)
├── hypothesis.py       # Already exists! (agents/b/hypothesis.py)
├── experiment.py       # ExperimentAgent: Module × Hypothesis → TestResult
├── incorporate.py      # IncorporateAgent: Improvement → CodebaseChange
├── ast_analyzer.py     # ASTAnalyzer: Module → CodeStructure
└── memory.py           # MemoryAgent: Track rejected/accepted improvements
```

### 2. Command-Line Interface

**Current**:
```bash
python evolve.py all --dry-run --quick
```

**Proposed** (composable):
```bash
# Standard pipeline (same as current)
kgents evolve all --dry-run

# Compose with filters
kgents evolve agents/b | kgents filter-by-confidence 0.8 | kgents apply

# Target specific improvement types
kgents evolve all --only refactor,fix

# Self-improvement (fixed-point mode)
kgents evolve evolve.py --safe-mode
```

### 3. Undo/Rollback System

**Problem**: Once applied, no easy undo

**Solution**: Git-based checkpoint system

```bash
# Before applying improvements
$ kgents evolve all --dry-run
# Creates: .kgents/checkpoints/evolve_20251208_160000

# Apply improvements
$ kgents apply --checkpoint evolve_20251208_160000
✓ Applied 14 improvements
  Checkpoint saved as: kgents_pre_evolve_14_improvements

# Undo if needed
$ kgents rollback evolve_20251208_160000
✓ Rolled back 14 improvements
  HEAD is now at: <previous commit>
```

### 6. Safe Self-Evolution Mode

**Requirement**: Must run safely on itself

**Strategy**: Use **multiple safety layers**

```python
@dataclass
class SafetyConfig:
    """Safety configuration for self-evolution."""

    # Layer 1: Read-only mode first pass
    read_only: bool = True  # Analyze without modifying

    # Layer 2: Syntax validation (strict)
    require_syntax_valid: bool = True
    require_mypy_strict: bool = True

    # Layer 3: Behavioral testing
    require_self_test: bool = True  # evolve.py must still work on test code

    # Layer 4: Fixed-point check
    max_iterations: int = 3
    convergence_threshold: float = 0.95  # If 95% same as previous, converged

    # Layer 5: Human approval for meta-changes
    require_human_approval: bool = True  # For changes to evolution logic
```

**Implementation**:

```python
class SelfEvolutionAgent(Agent[Path, EvolutionReport]):
    """Safely evolve evolve.py using fixed-point iteration."""

    async def invoke(self, target: Path) -> EvolutionReport:
        if "evolve.py" in str(target):
            # Activate all safety layers
            config = SafetyConfig(
                read_only=False,  # After validation
                require_syntax_valid=True,
                require_mypy_strict=True,
                require_self_test=True,
                max_iterations=3,
                require_human_approval=True,
            )

            # Use Fix pattern for convergence
            fix_agent = Fix(
                agent=StandardEvolutionAgent(),
                should_continue=lambda prev, curr: not self._converged(prev, curr),
                max_iterations=config.max_iterations,
            )

            return await fix_agent.invoke(target)
        else:
            # Standard evolution
            return await StandardEvolutionAgent().invoke(target)

    def _converged(self, prev: EvolutionReport, curr: EvolutionReport) -> bool:
        """Check if evolution has converged (fixed point reached)."""
        # Compare code similarity, experiment outcomes, etc.
        similarity = self._code_similarity(prev, curr)
        return similarity >= 0.95
```

### 7. Generality: Works on Any Python Code

**Current state**: Tailored to kgents (uses kgents principles for judging)

**Proposed**: Make principles **pluggable**

```python
@dataclass
class EvolutionConfig:
    """Configuration for evolution pipeline."""

    # Pluggable principle checker
    principles: Optional[Principles] = None  # Defaults to kgents principles

    # Pluggable judging strategy
    judge: Optional[Agent[CodeImprovement, Verdict]] = None

    # Pluggable hypothesis generator
    hypothesis_engine: Optional[Agent[HypothesisInput, HypothesisOutput]] = None


# Example: Use on non-kgents code
config = EvolutionConfig(
    principles=None,  # Skip kgents-specific principles
    judge=GenericCodeJudge(),  # Use generic heuristics
)

pipeline = EvolutionPipeline(config)
await pipeline.run()
```

**Fallback judging** (when no principles):
- PEP 8 compliance
- Cyclomatic complexity reduction
- Type coverage increase
- Test coverage increase
- Documentation completeness

---

## Self-Stability Analysis

### Challenge: evolve.py evolving itself

**Why it's hard**:
1. **Meta-reasoning**: LLM must reason about code that reasons about code
2. **Context size**: evolve.py is 1,511 lines (large context)
3. **Breaking changes**: Changes to evolution logic could cause cascading failures
4. **Recursion risk**: Poorly applied improvement could break future improvements

### Proposed Solution: Fixed-Point Property

**Mathematical foundation**: A function `f` has a fixed point `x` if `f(x) = x`

For evolution:
```
Evolve(code) = code'    # Evolution produces code'

# Fixed point reached when:
Evolve(code') ≈ code'   # Evolving again produces minimal changes
```

**Implementation**:

```python
async def evolve_until_stable(target: Path, max_rounds: int = 3) -> Path:
    """
    Evolve code until reaching a fixed point (stability).

    Returns the stable version or raises if unstable after max_rounds.
    """
    current = target.read_text()

    for round in range(max_rounds):
        log(f"Evolution round {round + 1}/{max_rounds}")

        # Run evolution
        improved = await evolve(current)

        # Check convergence
        similarity = compute_similarity(current, improved)

        if similarity > 0.95:  # 95% similar → converged
            log(f"✓ Reached fixed point at round {round + 1}")
            return improved

        # Test that improved version still works
        if not await validate_works(improved):
            log(f"✗ Round {round + 1} broke functionality, reverting")
            return current

        current = improved

    raise RuntimeError(f"Failed to converge after {max_rounds} rounds")
```

**Validation layers**:
1. Syntax check (py_compile)
2. Type check (mypy --strict)
3. Self-test: Can the improved evolve.py still evolve test code?
4. Behavioral equivalence: Does it produce similar results on sample inputs?

### Safe Mode: Sandbox Testing

Before applying to real evolve.py:

```python
async def test_evolved_version_safely(improved_code: str) -> bool:
    """Test evolved version in sandboxed environment."""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write improved version to temp location
        test_evolve = Path(tmpdir) / "evolve.py"
        test_evolve.write_text(improved_code)

        # Test on sample code (not real codebase)
        sample_code = create_simple_test_module()

        # Run evolved version on sample
        result = subprocess.run(
            [sys.executable, str(test_evolve), "sample", "--dry-run"],
            capture_output=True,
            timeout=60,
        )

        # Validate:
        # 1. Didn't crash
        # 2. Produced valid output
        # 3. Generated reasonable improvements
        return (
            result.returncode == 0 and
            "EVOLUTION COMPLETE" in result.stdout and
            "error" not in result.stderr.lower()
        )
```

---

## Implementation Roadmap

### Phase 1: Extract Core Agents (Week 1)
**Goal**: Decompose evolve.py without changing UX

- [ ] Extract `ASTAnalyzer` → `agents/e/ast_analyzer.py`
- [ ] Extract `MemoryAgent` → `agents/e/memory.py`
- [ ] Extract `ExperimentAgent` → `agents/e/experiment.py`
- [ ] Extract `IncorporateAgent` → `agents/e/incorporate.py`
- [ ] Create `EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate`
- [ ] Update `evolve.py` to use new agents (backwards compatible)
- [ ] Validate: All existing tests pass

### Phase 2: Safety & Self-Evolution ✅ COMPLETE
**Goal**: Make it safe to run on itself

- [x] Implement `SafetyConfig` with multiple validation layers
- [x] Implement fixed-point convergence check
- [x] Implement sandbox testing for evolved version
- [x] Add `--safe-mode` flag for self-evolution
- [x] Wire SelfEvolutionAgent to EvolutionPipeline
- [ ] Validate: Successfully evolve evolve.py 3 times, reaches fixed point

### Phase 3: Generality
**Goal**: Make it work on any Python code

- [ ] Make principles pluggable (`EvolutionConfig.principles`)
- [ ] Implement `GenericCodeJudge` (PEP 8, complexity, coverage)
- [ ] Implement fallback hypothesis generation (no kgents context)
- [ ] Test on external codebases (Django, Flask, FastAPI samples)
- [ ] Document: How to use on non-kgents code
- [ ] Validate: Successfully evolve 3 external Python projects

### Phase 4: Polish & Documentation
**Goal**: Production-ready

- [ ] Implement undo/rollback system
- [ ] Implement checkpoint management
- [ ] Write user guide
- [ ] Write developer guide (for extending evolution)

---

## Open Questions

### 1. Composition at the CLI level?

**Question**: Should the CLI support Unix-style piping?

```bash
# Pipe evolution results to filters
kgents evolve all --json | jq '.passed[] | select(.confidence > 0.8)'

# Compose with other kgents commands?
kgents evolve agents/b | kgents apply | kgents test
```

**Trade-offs**:
- ✅ Very composable (Unix philosophy)
- ✅ Plays well with existing tools (jq, grep, etc.)
- ❌ More complex to implement (structured I/O)
- ❌ May be overkill for most users

**Recommendation**: Start simple, add JSON output if requested.

### 2. How to handle conflicts between improvements?

**Scenario**: Two experiments both modify the same function, both pass tests.

**Options**:
1. **Apply first, skip second** (simple but may miss good improvements)
2. **Ask user to choose** (interactive decision)
3. **Merge improvements** (use Hegel dialectic to synthesize)
4. **Apply in sequence, re-test after each** (safest but slowest)

**Recommendation**: Option 4 for now (safest), Option 3 for future (most sophisticated).

### 3. When to use Fix pattern for evolution itself?

**Current**: Single-pass evolution

**Proposed**: Iterative evolution with Fix

```python
# Option A: Fixed iterations
evolution_agent = Fix(
    agent=StandardEvolutionAgent(),
    should_continue=lambda _: False,  # Single pass
    max_iterations=1,
)

# Option B: Converge to fixed point
evolution_agent = Fix(
    agent=StandardEvolutionAgent(),
    should_continue=lambda prev, curr: not converged(prev, curr),
    max_iterations=5,
)
```

**Trade-offs**:
- Option A: Current behavior, simple, predictable
- Option B: Deeper evolution, but risk of instability

**Recommendation**: Option A for general use, Option B for `--deep-evolution` flag.

### 4. Should improvements be versioned?

**Motivation**: Track evolution history, enable rollback

```
.kgents/evolution_history/
├── 20251208_160000/
│   ├── improvements.json
│   ├── checkpoint_before.tar.gz
│   └── checkpoint_after.tar.gz
└── 20251207_140000/
    ├── improvements.json
    └── ...
```

**Trade-offs**:
- ✅ Enables time-travel debugging
- ✅ Easier to understand evolution trajectory
- ❌ Disk space (but can compress/archive)
- ❌ Adds complexity

**Recommendation**: Yes, implement versioning with automatic cleanup (keep last 10).

---

## Success Metrics

How to measure if these improvements work?

### 1. Self-Stability
- **Metric**: Can evolve.py evolve itself 3 times and reach a fixed point?
- **Target**: 95% similarity after 3 rounds
- **Validation**: Automated test in CI

### 2. Generality
- **Metric**: Success rate on external Python projects
- **Target**: Generate valid improvements for 80% of modules in Django/Flask/FastAPI
- **Validation**: Manual testing on 3 external codebases

### 3. Composability
- **Metric**: Can evolution agents be composed with other agents?
- **Example**: `Ground >> HypothesisEngine >> CustomFilter >> Judge >> Incorporate`
- **Target**: Yes, with <10 lines of code
- **Validation**: Write 3 example compositions

---

## Appendix: Code Samples

### Example: Composed Evolution Pipeline

```python
"""
Example: Custom evolution pipeline using agent composition.
"""

from bootstrap import Ground, Judge, Sublate, Fix, compose
from agents.b.hypothesis import HypothesisEngine
from agents.e.experiment import ExperimentAgent
from agents.e.incorporate import IncorporateAgent

# Custom filter: Only high-confidence improvements
class HighConfidenceFilter(Agent[list[Experiment], list[Experiment]]):
    async def invoke(self, experiments: list[Experiment]) -> list[Experiment]:
        return [e for e in experiments if e.improvement.confidence > 0.8]

# Compose the pipeline
evolution_pipeline = (
    Ground()
    >> HypothesisEngine()
    >> ExperimentAgent()
    >> HighConfidenceFilter()
    >> Judge()
    >> Sublate()
    >> IncorporateAgent()
)

# Run evolution with custom pipeline
report = await evolution_pipeline.invoke(target_module)
```

### Example: Self-Evolution with Fixed Point

```python
"""
Example: Safely evolve evolve.py using fixed-point iteration.
"""

from bootstrap import Fix
from agents.e.evolution import EvolutionAgent, SafetyConfig

# Create self-evolution agent with strict safety
self_evolution = Fix(
    agent=EvolutionAgent(
        config=SafetyConfig(
            require_syntax_valid=True,
            require_mypy_strict=True,
            require_self_test=True,
            require_human_approval=True,
        )
    ),
    should_continue=lambda prev, curr: similarity(prev, curr) < 0.95,
    max_iterations=3,
)

# Evolve evolve.py until stable
stable_version = await self_evolution.invoke(Path("evolve.py"))
print(f"Reached fixed point: {stable_version}")
```

---

## Conclusion

Refactoring `evolve.py` as a **composable kgents app** achieves:

1. ✅ **Self-stability**: Fixed-point iteration, sandbox testing, multiple validation layers
2. ✅ **Generality**: Pluggable principles, works on any Python code
3. ✅ **Composability**: Agents as morphisms, Unix-style composition

The proposed architecture follows kgents' own principles:
- **Composable**: Agents compose via `>>`
- **Heterarchical**: No fixed orchestrator, agents in flux
- **Generative**: Design compresses into regenerable spec
- **Tasteful**: Each agent has clear purpose
- **Curated**: Quality improvements over quantity

**Status**: Phase 2 complete ✅ (safety.py implemented). Continue with Phase 3 (Generality).
