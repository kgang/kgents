# Evolution Agent

**The composed pipeline for dialectical code evolution**

## Purpose

The Evolution Agent orchestrates safe, experimental code improvement through a multi-stage pipeline that:

1. Grounds hypotheses in static code analysis (AST)
2. Generates testable improvement proposals
3. Validates through multiple independent layers
4. Judges against foundational principles
5. Resolves productive tensions dialectically
6. Incorporates changes with git safety

Unlike deterministic refactoring tools, the Evolution Agent treats code improvement as a **creative dialogue** between current implementation and possible futures, mediated by testing, reasoning, and institutional memory.

## What It Does

- **Discovers modules** in a codebase based on target specification
- **Analyzes structure** via AST to identify improvement opportunities
- **Generates hypotheses** combining static analysis and LLM reasoning
- **Experiments safely** in isolated sandboxes with multi-layer validation
- **Judges rigorously** against the 7 kgents principles
- **Learns continuously** by recording outcomes in institutional memory
- **Applies carefully** using git safety protocols

## What It Doesn't Do

- ❌ Apply changes without comprehensive testing
- ❌ Ignore pre-existing errors or unstable modules (pre-flight checks)
- ❌ Re-propose hypotheses that were recently rejected
- ❌ Force synthesis when productive tension should be held
- ❌ Operate without clear rollback capability
- ❌ Self-modify without convergence detection

## Specification

```yaml
identity:
  name: EvolutionAgent
  genus: e
  version: "2.0.0"
  purpose: Evolve code through safe, experimental dialectical improvement

interface:
  input:
    type: EvolutionInput
    description: Modules to evolve and configuration parameters
  output:
    type: EvolutionReport
    description: Summary of experiments, outcomes, and incorporated changes
  errors:
    - code: MODULE_UNHEALTHY
      description: Pre-flight checks failed (syntax errors, import errors, etc.)
    - code: HYPOTHESIS_EXHAUSTED
      description: No viable hypotheses after memory filtering
    - code: EXPERIMENT_FAILED
      description: Generated code failed validation (syntax, types, tests)
    - code: INCORPORATION_BLOCKED
      description: Git working tree has uncommitted changes

behavior:
  description: |
    The Evolution Agent processes each module through a six-stage pipeline:

    1. **Pre-Flight**: Verify module health (syntax, imports, baseline errors)
    2. **Ground**: Analyze AST structure to identify improvement targets
    3. **Hypothesize**: Generate improvement ideas (AST + LLM), filter by memory
    4. **Experiment**: Generate improved code, validate through multiple layers
    5. **Judge**: Evaluate against 7 principles, return ACCEPT/REVISE/REJECT
    6. **Incorporate**: Apply accepted changes with git commit

    The pipeline is parallel across modules but sequential within each module.
    All stages are composable morphisms with clear input/output types.

  guarantees:
    - Experiments never modify production code (isolated validation)
    - No incorporation without passing all validation layers
    - Memory prevents re-proposing recently rejected hypotheses
    - Git safety ensures rollback capability for all changes
    - Pre-flight checks prevent evolution of unhealthy modules
    - All outcomes (accept/reject/hold) are logged with rationale

  constraints:
    - Requires git repository (for incorporation)
    - LLM runtime required for hypothesis generation and improvement
    - Cannot evolve modules with pre-existing syntax errors (unless pre-flight disabled)
    - Cannot incorporate when working tree has uncommitted changes
    - Memory persists across sessions (file-based storage)

  side_effects:
    - Writes to `.evolve_memory.json` (institutional memory)
    - Writes to `.evolve_logs/` directory (execution logs)
    - Creates git commits when auto-apply enabled
    - Modifies source files when improvements incorporated
    - May execute pytest, mypy as validation subprocesses

configuration:
  parameters:
    - name: target
      type: "runtime" | "agents" | "bootstrap" | "meta" | "all"
      default: "all"
      description: Which modules to evolve (meta targets evolve.py itself)

    - name: dry_run
      type: boolean
      default: false
      description: Preview improvements without applying (for safety)

    - name: auto_apply
      type: boolean
      default: false
      description: Automatically incorporate improvements that pass validation

    - name: max_improvements_per_module
      type: number
      default: 4
      description: Maximum hypotheses to test per module

    - name: hypothesis_count
      type: number
      default: 4
      description: Number of hypotheses to generate (AST + LLM combined)

    - name: quick_mode
      type: boolean
      default: false
      description: Skip dialectical synthesis for faster iteration

    - name: require_tests_pass
      type: boolean
      default: true
      description: Require pytest to pass before accepting improvements

    - name: require_type_check
      type: boolean
      default: true
      description: Require mypy strict mode to pass before accepting

    - name: enable_retry
      type: boolean
      default: true
      description: Enable retry with refined prompts on test failure

    - name: max_retries
      type: number
      default: 2
      description: Maximum retry attempts per hypothesis

    - name: enable_fallback
      type: boolean
      default: true
      description: Enable progressive simplification on persistent failure

    - name: enable_error_memory
      type: boolean
      default: true
      description: Track failure patterns across sessions for learning

types:
  EvolutionInput:
    modules: array<CodeModule>
    config: EvolutionConfig

  EvolutionConfig:
    target: string
    dry_run: boolean
    auto_apply: boolean
    max_improvements_per_module: number
    hypothesis_count: number
    quick_mode: boolean
    require_tests_pass: boolean
    require_type_check: boolean
    enable_retry: boolean
    max_retries: number
    enable_fallback: boolean
    enable_error_memory: boolean

  CodeModule:
    name: string
    category: string
    path: Path

  EvolutionReport:
    experiments: array<Experiment>
    incorporated: array<Experiment>
    rejected: array<Experiment>
    held: array<Experiment>
    summary: string
    elapsed_seconds: number

  Experiment:
    id: string
    module: CodeModule
    improvement: CodeImprovement
    hypothesis: string
    status: ExperimentStatus
    verdict: Verdict | null
    synthesis: Synthesis | null
    test_results: object | null
    error: string | null

  CodeImprovement:
    description: string
    rationale: string
    improvement_type: "refactor" | "fix" | "feature" | "test"
    code: string
    confidence: number
    metadata: object

  ExperimentStatus:
    enum: ["PENDING", "PASSED", "FAILED", "HELD"]

  Verdict:
    type: "ACCEPT" | "REVISE" | "REJECT"
    reasoning: string
    principle_scores: array<PrincipleScore>

  PrincipleScore:
    principle: string
    score: number
    reasoning: string
```

## The Six-Stage Pipeline

### 1. Pre-Flight Check

**Morphism**: `CodeModule → PreFlightReport`

**Purpose**: Prevent wasted LLM calls on unhealthy modules

Validates:
- ✓ File exists and is readable
- ✓ Valid Python syntax (AST parses)
- ✓ Imports can resolve
- ✓ Module is not empty or trivial (<10 lines)

Records:
- Baseline error count (for comparison after improvement)
- Blocking issues (must fix before evolution)
- Warnings (can evolve, but with caution)
- Recommendations (what to prioritize)

**Output**:
- `can_evolve: boolean` - Whether to proceed
- `blocking_issues: array<string>` - Must resolve before evolving
- `warnings: array<string>` - Proceed with caution
- `baseline_error_count: number` - Pre-existing errors

### 2. Ground (AST Analysis)

**Morphism**: `CodeModule → CodeStructure`

**Purpose**: Understand code structure to generate targeted hypotheses

Analyzes:
- Classes and their methods
- Functions and their signatures
- Imports and dependencies
- Complexity metrics (cyclomatic, nesting)
- Missing type annotations
- Docstring coverage

**Output**:
- `classes: array<ClassInfo>` - Class definitions with methods
- `functions: array<FunctionInfo>` - Top-level functions
- `imports: array<ImportInfo>` - Import statements
- `complexity_hints: array<string>` - High complexity locations
- `docstring: string | null` - Module-level docstring

This structure feeds into hypothesis generation (both AST-based and LLM-based).

### 3. Hypothesize (Idea Generation)

**Morphism**: `(CodeModule, CodeStructure, Memory) → array<Hypothesis>`

**Purpose**: Generate testable improvement proposals

**Two-phase generation**:

#### Phase 1: AST-Based Hypotheses (Targeted)
From structure analysis:
- "Add type annotations to function `foo` (currently untyped)"
- "Refactor `long_function` (50+ lines, cyclomatic complexity 15)"
- "Extract nested function `helper` from `parent` for reusability"

#### Phase 2: LLM-Based Hypotheses (Creative)
From code understanding:
- "Use composable >> operator for pipeline clarity"
- "Apply Fix pattern for retry logic instead of manual loop"
- "Separate concerns: split `do_everything` into focused morphisms"

#### Memory Filtering
Before returning, filter out:
- Recently rejected hypotheses (by module + similarity)
- Recently accepted hypotheses (avoid redundant proposals)
- Known failure patterns (from error memory)

**Output**: `array<string>` - Testable hypothesis statements

### 4. Experiment (Generate & Validate)

**Morphism**: `(Hypothesis, CodeModule) → Experiment`

**Purpose**: Test hypothesis by generating improved code and validating

#### Generation (LLM)
Build rich prompt context:
- Module code preview (with line numbers)
- AST structure summary
- Known failure patterns for this module (from error memory)
- Clear output format requirements (METADATA + CODE sections)

Generate improved code via LLM with temperature=0.7 for creativity.

#### Validation (Multi-Layer)

**Layer 1: Parsing**
- Extract METADATA (JSON) and CODE (Python) sections
- Try 4 fallback strategies if initial parse fails
- Repair common AST errors incrementally

**Layer 2: Schema Validation**
- Fast pre-mypy checks (constructor signatures, generic types)
- Catch obvious type errors without full mypy run

**Layer 3: Syntax Validation**
- Parse generated code as AST
- Verify valid Python 3.10+ syntax

**Layer 4: Type Checking** (if `require_type_check`)
- Run mypy in strict mode
- Fail if type errors introduced

**Layer 5: Test Execution** (if `require_tests_pass`)
- Run pytest on module's test file
- Fail if tests break

#### Recovery Strategies

**Retry** (if enabled, up to `max_retries`):
- Refine prompt with failure details
- Include validation error messages
- Suggest specific fixes to LLM

**Fallback** (if retry exhausted):
- Minimal: Simplest possible change
- Type-only: Add annotations without refactoring
- Docs-only: Improve documentation, no code change

**Output**: `Experiment` with status PASSED or FAILED

### 5. Judge (Principle Evaluation)

**Morphism**: `(Experiment, OriginalCode) → Verdict`

**Purpose**: Evaluate improvement against foundational principles

Scores improvement on each of the 7 principles (0.0 to 1.0):

1. **Tasteful**: Clear purpose, no feature creep, minimal design
2. **Curated**: Intentional selection, quality over quantity
3. **Ethical**: Preserves human agency, augments don't replace
4. **Joy-Inducing**: Code is more delightful to work with
5. **Composable**: Clear A → B morphism, >> compatible
6. **Heterarchical**: No unnecessary hierarchy or orchestration
7. **Generative**: Spec-first, regenerable from principles

Aggregates scores and reasoning into final verdict:
- **ACCEPT**: All principles scored ≥ 0.6, no critical concerns
- **REVISE**: Some principles weak but salvageable (not implemented yet)
- **REJECT**: Violations of core principles, or < 0.4 on any

**Output**: `Verdict` with type, reasoning, and per-principle scores

### 6. Incorporate (Safe Application)

**Morphism**: `Experiment → IncorporateResult`

**Purpose**: Apply accepted improvement with git safety

**Pre-conditions**:
- Experiment status is PASSED
- Verdict type is ACCEPT (or REVISE if implemented)
- Working tree is clean (no uncommitted changes) OR dry_run=true
- File is writable

**Process**:
1. Verify pre-conditions
2. Write improved code to file (atomic write via temp file)
3. Create git commit (if not dry_run):
   - Commit message includes: hypothesis, improvement type, confidence
   - Co-authored by "Claude Sonnet 4.5"
   - Includes link to Claude Code
4. Record in memory as "accepted"

**Output**:
- `success: boolean`
- `commit_sha: string | null`
- `error: string | null`

**Rollback**: If any step fails, rollback via git and return error.

## Pipeline Composition

The full pipeline composes six stages:

```python
evolution_pipeline = (
    preflight_checker
    >> ast_analyzer
    >> hypothesis_generator
    >> experiment_runner
    >> code_judge
    >> incorporator
)
```

Each stage is:
- **Independently testable**: Can invoke with mock inputs
- **Parallelizable**: Modules process in parallel, stages are sequential per module
- **Composable**: Clear input/output contracts enable >> composition
- **Recoverable**: Failures at any stage don't corrupt state

## Reliability Guarantees

The Evolution Agent achieves high reliability through **defense in depth**:

### Layer 1: Prompt Engineering
- Pre-flight checks prevent evolution of broken modules
- Rich context (AST, types, errors) improves generation quality
- Structured output format reduces parsing errors
- Clear requirements and constraints in prompt

### Layer 2: Parsing & Validation
- 4-strategy parser with progressive fallbacks
- Fast schema validation before expensive mypy
- AST-based repair for common errors
- Clear error messages for debugging

### Layer 3: Recovery & Learning
- Retry with refined prompts on failure
- Fallback to simpler changes if retry exhausted
- Error memory learns patterns across sessions
- Memory prevents re-proposing rejected hypotheses

### Layer 4: Git Safety
- Never incorporate with uncommitted changes
- Atomic writes via temp files
- Git commits enable rollback
- Dry-run mode for safe preview

## Example: Evolving a Simple Function

### Input

```python
# before.py
def calculate(x, y, op):
    if op == "add":
        return x + y
    elif op == "subtract":
        return x - y
    elif op == "multiply":
        return x * y
    elif op == "divide":
        return x / y
    else:
        return None
```

### Stage 1: Pre-Flight ✓

```yaml
can_evolve: true
blocking_issues: []
warnings: []
baseline_error_count: 0
```

### Stage 2: Ground

```yaml
functions:
  - name: calculate
    args: [x, y, op]
    returns: null  # No return type annotation
    complexity: 6  # Multiple branches
    has_docstring: false

complexity_hints:
  - "calculate has cyclomatic complexity 6"
  - "calculate has no type annotations"
  - "calculate has no docstring"
```

### Stage 3: Hypothesize

**AST-Based**:
1. "Add type annotations to function `calculate`"
2. "Add docstring to function `calculate`"

**LLM-Based**:
3. "Replace if-elif chain with dict-based dispatch for composability"
4. "Use operator module for built-in operations"

**Filtered**: None rejected recently, all 4 hypotheses pass to experiment.

### Stage 4: Experiment (Hypothesis 3)

**Generated Code**:

```python
from typing import Callable

def calculate(x: float, y: float, op: str) -> float | None:
    """
    Perform arithmetic operation on two numbers.

    Args:
        x: First operand
        y: Second operand
        op: Operation name (add, subtract, multiply, divide)

    Returns:
        Result of operation, or None if operation unknown
    """
    operations: dict[str, Callable[[float, float], float]] = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b,
    }

    operation = operations.get(op)
    return operation(x, y) if operation else None
```

**Validation**:
- ✓ Parsing: METADATA and CODE extracted
- ✓ Schema: Type annotations valid
- ✓ Syntax: AST parses successfully
- ✓ Types: mypy strict passes
- ✓ Tests: pytest passes (if tests exist)

**Status**: PASSED

### Stage 5: Judge

**Principle Scores**:
- Tasteful: 0.9 (cleaner, no feature creep)
- Curated: 0.8 (intentional pattern choice)
- Ethical: 1.0 (no ethical concerns)
- Joy-Inducing: 0.85 (more Pythonic, easier to extend)
- Composable: 0.9 (dict is composable, lambdas are morphisms)
- Heterarchical: 0.8 (flat structure, no unnecessary hierarchy)
- Generative: 0.85 (clear pattern, regenerable)

**Verdict**: ACCEPT (all ≥ 0.6)

**Reasoning**: "Improvement uses dict-based dispatch pattern which is more Pythonic and composable. Type annotations improve clarity. Docstring adds necessary documentation. No violations of principles detected."

### Stage 6: Incorporate

```bash
git commit -m "refactor: Use dict-based dispatch in calculate function

Replaced if-elif chain with composable dict dispatch pattern.
Added type annotations and comprehensive docstring.

Confidence: 0.85

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Output**:
```yaml
success: true
commit_sha: "a3f5c2d"
error: null
```

### Final Report

```yaml
experiments: 1
incorporated: 1
rejected: 0
held: 0
summary: "Evolved 1 module: 1 incorporated, 0 rejected, 0 held"
elapsed_seconds: 12.3
```

## Composition with Other Gents

Evolution Agent is fully composable:

### With K-gent (Personalization)

```python
# User preferences guide evolution priorities
k_gent_prefs = await k_gent.invoke(user_profile)

evolution_config = EvolutionConfig(
    target=k_gent_prefs.priority_modules,
    hypothesis_count=k_gent_prefs.exploration_level,
)

report = await evolution_agent.invoke(EvolutionInput(
    modules=modules,
    config=evolution_config,
))
```

### With B-gents (Scientific Rigor)

```python
# Use hypothesis engine for improvement ideas
hypothesis_engine = HypothesisEngine()
bio_hypotheses = await hypothesis_engine.invoke(HypothesisInput(
    observations=["Code complexity high", "Type coverage low"],
    domain="Software quality improvement",
))

# Feed into evolution pipeline
for hypothesis in bio_hypotheses.hypotheses:
    exp = await evolution_agent.run_experiment(module, hypothesis.statement)
```

### With H-gents (Dialectical Refinement)

```python
# Explicitly engage dialectical synthesis
hegel = HegelAgent()
dialectic = await hegel.invoke(DialecticInput(
    thesis=current_code,
    antithesis=improved_code,
))

if dialectic.tension:
    sublate = Sublate()
    result = await sublate.invoke(SublateInput(tensions=(dialectic.tension,)))
```

## Safe Self-Evolution

E-gents can evolve themselves using **fixed-point iteration**:

```python
# Meta-evolution with convergence detection
safe_evolution = SelfEvolutionAgent(SafetyConfig(
    read_only=False,
    max_iterations=3,
    convergence_threshold=0.95,
    require_human_approval=True,
))

result = await safe_evolution.invoke(SafeEvolutionInput(
    target=Path("evolve.py"),
))

if result.converged:
    print(f"Converged after {result.iterations} iterations")
    print(f"Similarity: {result.final_similarity:.2%}")
else:
    print(f"Did not converge (max iterations reached)")
```

**Safety mechanisms**:
1. **Similarity metric**: Detect when changes stabilize (Levenshtein + structural)
2. **Sandbox testing**: Validate evolved code before applying
3. **Iteration limit**: Prevent infinite loops
4. **Human approval**: Required for meta-changes above threshold

## Anti-Patterns

E-gents must **never**:

1. ❌ **Apply changes without validation**
   ```python
   # WRONG: No testing
   file.write_text(improved_code)

   # RIGHT: Multi-layer validation
   experiment = await experiment_runner.invoke(...)
   if experiment.status == ExperimentStatus.PASSED:
       await incorporator.invoke(experiment)
   ```

2. ❌ **Ignore memory filtering**
   ```python
   # WRONG: Re-propose rejected hypotheses
   hypotheses = await generator.invoke(module)

   # RIGHT: Filter by memory
   hypotheses = await generator.invoke(module)
   filtered = [h for h in hypotheses if not memory.was_rejected(h)]
   ```

3. ❌ **Force synthesis of irreconcilable tensions**
   ```python
   # WRONG: Always synthesize
   synthesis = force_merge(thesis, antithesis)

   # RIGHT: Hold unresolvable tensions
   result = await sublate.invoke(tensions)
   if isinstance(result, HoldTension):
       log_for_human_review(result)
   ```

4. ❌ **Evolve without git safety**
   ```python
   # WRONG: No rollback capability
   if not dry_run:
       file.write_text(improved_code)

   # RIGHT: Git commit with safety checks
   if has_uncommitted_changes():
       raise IncorporationError("Working tree must be clean")
   incorporate_with_commit(experiment)
   ```

## See Also

- **[grounding.md](./grounding.md)** - AST analysis and code structure agents
- **[memory.md](./memory.md)** - Institutional memory and learning
- **[safety.md](./safety.md)** - Self-evolution and convergence detection
- **[H-gents](../h-gents/)** - Dialectical reasoning (Sublate, Tension)
- **[B-gents](../b-gents/)** - Hypothesis generation methodology
- **[C-gents](../c-gents/)** - Composition rules and patterns
- **[spec/principles.md](../principles.md)** - The 7 foundational principles

---

*"Evolution is not a race to perfection—it's a dialogue with possibility."*
