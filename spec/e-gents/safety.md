# Safety Agents

**Safe self-modification through convergence detection**

## Purpose

Safety agents enable E-gents to **safely evolve themselves** without risk of self-corruption:

1. **Fixed-point iteration**: Evolve → test → measure similarity → repeat until convergence
2. **Convergence detection**: Detect when changes stabilize (similarity > threshold)
3. **Sandbox validation**: Test evolved code before applying (syntax, types, self-test)
4. **Human approval gates**: Require approval for meta-changes above risk threshold
5. **Rollback capability**: Maintain git history for recovery from bad self-modifications

This enables the meta-circular property: **Evolution agents can evolve themselves** safely.

## What It Does

- **Iterate improvements** on self (evolve.py, agents/e/*.py, etc.)
- **Measure similarity** between iterations (Levenshtein + structural)
- **Detect convergence** when similarity exceeds threshold (typically 95%)
- **Sandbox test** evolved code in isolation before applying
- **Gate by risk** requiring human approval for high-impact changes
- **Provide rollback** via git commits at each iteration

## What It Doesn't Do

- ❌ Evolve without validation (every iteration must pass tests)
- ❌ Ignore convergence (max iterations is a hard limit, not infinite loop)
- ❌ Self-modify in production (sandbox testing required)
- ❌ Hide failures (all sandbox results logged)
- ❌ Skip human approval for high-risk changes (safety threshold enforced)

## Specification: Self-Evolution Agent

```yaml
identity:
  name: SelfEvolutionAgent
  genus: e
  version: "2.0.0"
  purpose: Safely evolve E-gent agents through fixed-point iteration

interface:
  input:
    type: SafeEvolutionInput
    description: Target file to evolve and safety configuration
  output:
    type: SafeEvolutionResult
    description: Whether convergence achieved and final evolved code
  errors:
    - code: SANDBOX_FAILURE
      description: Evolved code failed sandbox validation
    - code: MAX_ITERATIONS_REACHED
      description: Did not converge within iteration limit
    - code: HUMAN_APPROVAL_DENIED
      description: User rejected high-risk change
    - code: DIVERGENCE_DETECTED
      description: Similarity decreasing instead of increasing (instability)

behavior:
  description: |
    Evolve target file through fixed-point iteration:

    1. **Baseline**: Compute initial state (code, tests, types)
    2. **Iterate**:
       a. Generate improvement using EvolutionPipeline
       b. Sandbox test (syntax, types, self-test)
       c. Measure similarity to previous iteration
       d. If similarity > threshold: CONVERGED
       e. If similarity decreasing: WARNING (potential divergence)
       f. If max iterations reached: STOP
    3. **Approve**: If converged, require human approval (if configured)
    4. **Apply**: Write evolved code and commit

    Convergence threshold is typically 0.95 (95% similarity).
    Max iterations typically 3-5 (prevent infinite loops).

  guarantees:
    - Every iteration passes sandbox validation (syntax, types, tests)
    - Similarity is monotonically non-decreasing (or warning issued)
    - Human approval required if configured (high-risk changes)
    - Git commits at each iteration (rollback capability)
    - Read-only mode never modifies files (safe exploration)

  constraints:
    - Requires git repository (for iteration tracking)
    - Requires pytest for self-testing (validates evolved code works)
    - Cannot evolve code that doesn't initially pass tests
    - Similarity threshold is fixed per agent (not dynamic)
    - Max iterations is hard limit (prevents infinite loops)

  side_effects:
    - Writes to target file on convergence (if not read-only)
    - Creates git commits per iteration (if not read-only)
    - Executes evolved code in sandbox (subprocess isolation)
    - Logs all sandbox results to `.evolve_logs/`

configuration:
  parameters:
    - name: read_only
      type: boolean
      default: true
      description: Preview mode, never modify files

    - name: require_syntax_valid
      type: boolean
      default: true
      description: Every iteration must parse as valid Python

    - name: require_mypy_strict
      type: boolean
      default: true
      description: Every iteration must pass mypy strict mode

    - name: require_self_test
      type: boolean
      default: true
      description: Every iteration must pass its own test suite

    - name: max_iterations
      type: number
      default: 3
      description: Maximum fixed-point iterations before stopping

    - name: convergence_threshold
      type: number
      default: 0.95
      description: Similarity threshold for convergence (0.0-1.0)

    - name: require_human_approval
      type: boolean
      default: true
      description: Require manual approval before applying changes

    - name: risk_threshold
      type: number
      default: 0.7
      description: Similarity below this triggers mandatory approval

types:
  SafeEvolutionInput:
    target: Path
    config: SafetyConfig

  SafetyConfig:
    read_only: boolean
    require_syntax_valid: boolean
    require_mypy_strict: boolean
    require_self_test: boolean
    max_iterations: number
    convergence_threshold: number
    require_human_approval: boolean
    risk_threshold: number

  SafeEvolutionResult:
    success: boolean
    converged: boolean
    iterations: number
    final_similarity: number
    evolved_code: string | null
    sandbox_results: array<SandboxTestResult>
    error: string | null

  SandboxTestResult:
    iteration: number
    passed: boolean
    syntax_valid: boolean
    types_valid: boolean
    tests_passed: boolean
    similarity: number
    error: string | null
```

## Similarity Metrics

Two complementary similarity measures:

### 1. Levenshtein Similarity (Edit Distance)

**Definition**: Normalized edit distance between code strings

```python
def levenshtein_similarity(code1: str, code2: str) -> float:
    distance = levenshtein_distance(code1, code2)
    max_len = max(len(code1), len(code2))
    return 1.0 - (distance / max_len)
```

**Properties**:
- 1.0 = identical strings
- 0.0 = completely different
- Sensitive to whitespace and formatting (can be normalized)

**Use case**: Detect when code stops changing significantly

### 2. Structural Similarity (AST-based)

**Definition**: Compare AST structures (classes, functions, imports)

```python
def structural_similarity(code1: str, code2: str) -> float:
    ast1 = parse_ast(code1)
    ast2 = parse_ast(code2)

    # Compare counts
    class_sim = jaccard(ast1.classes, ast2.classes)
    func_sim = jaccard(ast1.functions, ast2.functions)
    import_sim = jaccard(ast1.imports, ast2.imports)

    return (class_sim + func_sim + import_sim) / 3
```

**Properties**:
- Ignores formatting and comments
- Focuses on structure (what exists, not how it's written)
- More robust to refactoring (rename function = high similarity)

**Use case**: Detect when structure stabilizes (even if code keeps changing)

### Combined Metric

```python
def compute_code_similarity(code1: str, code2: str) -> float:
    lev = levenshtein_similarity(code1, code2)
    struct = structural_similarity(code1, code2)

    # Weighted average (favor structural)
    return 0.3 * lev + 0.7 * struct
```

**Interpretation**:
- 0.95+ = Converged (minimal changes)
- 0.80-0.95 = Stabilizing (small improvements)
- 0.60-0.80 = Evolving (moderate changes)
- <0.60 = Diverging (major changes, potential instability)

## Fixed-Point Iteration

```python
def fixed_point_evolution(target: Path, config: SafetyConfig) -> SafeEvolutionResult:
    """
    Iterate: evolve → test → measure → repeat until convergence.

    Fixed point: f(code) ≈ code (improvement function stabilizes)
    """
    current_code = target.read_text()
    iterations = 0
    sandbox_results = []

    while iterations < config.max_iterations:
        iterations += 1

        # Apply evolution function
        improved_code = evolve(current_code)

        # Sandbox test
        sandbox_result = sandbox_test(improved_code, config)
        sandbox_results.append(sandbox_result)

        if not sandbox_result.passed:
            return SafeEvolutionResult(
                success=False,
                converged=False,
                iterations=iterations,
                error=sandbox_result.error,
            )

        # Measure similarity
        similarity = compute_code_similarity(current_code, improved_code)
        sandbox_result.similarity = similarity

        # Check convergence
        if similarity >= config.convergence_threshold:
            return SafeEvolutionResult(
                success=True,
                converged=True,
                iterations=iterations,
                final_similarity=similarity,
                evolved_code=improved_code,
                sandbox_results=sandbox_results,
            )

        # Check divergence (similarity decreasing)
        if iterations > 1 and similarity < sandbox_results[-2].similarity:
            log_warning(f"Divergence detected: {similarity:.2%}")

        # Continue iteration
        current_code = improved_code

    # Max iterations reached without convergence
    return SafeEvolutionResult(
        success=False,
        converged=False,
        iterations=iterations,
        final_similarity=similarity,
        sandbox_results=sandbox_results,
        error="Max iterations reached without convergence",
    )
```

## Sandbox Testing

**Morphism**: `(Code, SafetyConfig) → SandboxTestResult`

**Purpose**: Validate evolved code in isolation before applying

```python
def sandbox_test(code: str, config: SafetyConfig) -> SandboxTestResult:
    """
    Run evolved code in sandbox (separate process) and validate:
    1. Syntax: Can parse as AST?
    2. Types: Passes mypy strict?
    3. Self-test: Passes pytest on itself?
    """
    result = SandboxTestResult(passed=False)

    # Test 1: Syntax validation
    if config.require_syntax_valid:
        try:
            ast.parse(code)
            result.syntax_valid = True
        except SyntaxError as e:
            result.error = f"Syntax error: {e}"
            return result

    # Test 2: Type checking
    if config.require_mypy_strict:
        temp_file = write_temp(code)
        mypy_result = subprocess.run(
            ["mypy", "--strict", str(temp_file)],
            capture_output=True
        )
        if mypy_result.returncode == 0:
            result.types_valid = True
        else:
            result.error = f"Type error: {mypy_result.stdout}"
            return result

    # Test 3: Self-test (run pytest on evolved code)
    if config.require_self_test:
        test_file = find_test_file(temp_file)
        if test_file:
            pytest_result = subprocess.run(
                ["pytest", str(test_file), "-v"],
                capture_output=True
            )
            if pytest_result.returncode == 0:
                result.tests_passed = True
            else:
                result.error = f"Test failure: {pytest_result.stdout}"
                return result

    result.passed = True
    return result
```

## Example: Evolving evolve.py

### Initial State

```python
# evolve.py (iteration 0)
def generate_hypotheses(module: CodeModule) -> list[str]:
    """Generate improvement hypotheses."""
    # Simple LLM call, no AST analysis
    return llm.generate(f"Improve {module.name}")
```

### Iteration 1

**Improvement**: Add AST-based hypothesis generation

```python
# evolve.py (iteration 1)
def generate_hypotheses(module: CodeModule) -> list[str]:
    """Generate improvement hypotheses using AST + LLM."""
    # Add AST analysis
    structure = analyze_ast(module.path)
    ast_hypotheses = generate_from_structure(structure)

    # Keep LLM generation
    llm_hypotheses = llm.generate(f"Improve {module.name}")

    return ast_hypotheses + llm_hypotheses
```

**Sandbox Test**:
- ✓ Syntax valid
- ✓ Types valid (mypy strict passes)
- ✓ Self-test passes (evolve.py can still evolve)

**Similarity**: 0.75 (significant change, structure evolved)

**Verdict**: CONTINUE (below convergence threshold)

### Iteration 2

**Improvement**: Add memory filtering

```python
# evolve.py (iteration 2)
def generate_hypotheses(module: CodeModule, memory: ImprovementMemory) -> list[str]:
    """Generate hypotheses using AST + LLM, filtered by memory."""
    structure = analyze_ast(module.path)
    ast_hypotheses = generate_from_structure(structure)
    llm_hypotheses = llm.generate(f"Improve {module.name}")

    # Add memory filtering
    all_hypotheses = ast_hypotheses + llm_hypotheses
    filtered = [h for h in all_hypotheses if not memory.was_rejected(module.name, h)]

    return filtered
```

**Sandbox Test**:
- ✓ Syntax valid
- ✓ Types valid
- ✓ Self-test passes

**Similarity**: 0.92 (small change, just added filtering)

**Verdict**: CONTINUE (close to convergence)

### Iteration 3

**Improvement**: Minor refinement (type hints, docstring)

```python
# evolve.py (iteration 3)
def generate_hypotheses(
    module: CodeModule,
    memory: ImprovementMemory
) -> list[str]:
    """
    Generate improvement hypotheses using AST + LLM, filtered by memory.

    Returns:
        List of testable hypothesis strings
    """
    structure: CodeStructure | None = analyze_ast(module.path)
    ast_hypotheses: list[str] = generate_from_structure(structure)
    llm_hypotheses: list[str] = llm.generate(f"Improve {module.name}")

    all_hypotheses = ast_hypotheses + llm_hypotheses
    filtered = [h for h in all_hypotheses if not memory.was_rejected(module.name, h)]

    return filtered
```

**Sandbox Test**:
- ✓ Syntax valid
- ✓ Types valid
- ✓ Self-test passes

**Similarity**: 0.97 (minor formatting/typing changes only)

**Verdict**: **CONVERGED** (similarity ≥ 0.95)

### Result

```yaml
success: true
converged: true
iterations: 3
final_similarity: 0.97
evolved_code: <iteration 3 code>
sandbox_results:
  - iteration: 1, passed: true, similarity: 0.75
  - iteration: 2, passed: true, similarity: 0.92
  - iteration: 3, passed: true, similarity: 0.97
```

## Human Approval Gates

When `require_human_approval: true` or similarity < `risk_threshold`:

```python
if config.require_human_approval or similarity < config.risk_threshold:
    print("\n" + "="*60)
    print("HUMAN APPROVAL REQUIRED")
    print("="*60)
    print(f"Target: {target}")
    print(f"Iterations: {iterations}")
    print(f"Similarity: {similarity:.2%}")
    print(f"\nChanges:")
    print_diff(current_code, improved_code)
    print("\nApprove? [y/N]: ", end="")

    approval = input().strip().lower()
    if approval != 'y':
        raise HumanApprovalDenied("User rejected changes")
```

**Approval criteria** (user decides):
- Does the change align with intent?
- Are the modifications reasonable in scope?
- Do sandbox tests provide sufficient confidence?
- Is rollback straightforward (git commit)?

## Risk Assessment

Classify changes by risk level:

### Low Risk (similarity > 0.9)

- Minor refactoring (rename variables, add types)
- Documentation improvements
- Code formatting
- Adding test coverage

**Gate**: Optional approval (can auto-apply)

### Medium Risk (0.7 < similarity ≤ 0.9)

- Structural refactoring (extract functions, change class hierarchy)
- Adding new features
- Changing algorithms (same behavior, different implementation)

**Gate**: Recommended approval (warn if auto-apply)

### High Risk (similarity ≤ 0.7)

- Major architectural changes
- Changing core interfaces
- Self-modifying evolution logic
- Changes to safety mechanisms

**Gate**: **Mandatory approval** (never auto-apply)

## Convergence Guarantees

### Theorem: Bounded Convergence

**Given**:
- Evolution function `f: Code → Code`
- Similarity metric `sim: (Code, Code) → [0, 1]`
- Convergence threshold `θ ∈ [0, 1]`
- Max iterations `n ∈ ℕ`

**Then**:
- Either `∃k ≤ n : sim(f^k(c₀), f^(k-1)(c₀)) ≥ θ` (converges)
- Or iterations terminate at `n` (bounded)

**Proof**: By induction on iteration count. ∎

**Implication**: Fixed-point iteration **always terminates** (either by convergence or iteration limit).

### Theorem: Monotonic Improvement (Desired, Not Guaranteed)

**Claim**: Under ideal conditions, `sim(f^(k+1)(c), f^k(c))` should be non-decreasing.

**Reality**: Not guaranteed! Evolution can diverge if:
- Hypotheses are too aggressive
- Tests are incomplete (false positives)
- LLM introduces instability

**Mitigation**: Warn on decreasing similarity, consider earlier checkpoint as final result.

## Anti-Patterns

❌ **Don't skip sandbox testing**

```python
# WRONG: Apply changes without validation
improved_code = evolve(current_code)
target.write_text(improved_code)  # DANGEROUS!

# RIGHT: Sandbox test first
improved_code = evolve(current_code)
sandbox_result = sandbox_test(improved_code, config)
if sandbox_result.passed:
    target.write_text(improved_code)
```

❌ **Don't trust similarity alone**

```python
# WRONG: High similarity doesn't mean correct
if similarity > 0.95:
    auto_apply(improved_code)  # Could still be broken!

# RIGHT: Similarity + sandbox tests
if similarity > 0.95 and sandbox_result.passed:
    auto_apply(improved_code)
```

❌ **Don't iterate infinitely**

```python
# WRONG: No iteration limit
while not converged:
    improved_code = evolve(current_code)
    # ... could run forever!

# RIGHT: Bounded iteration
for iteration in range(max_iterations):
    improved_code = evolve(current_code)
    if converged:
        break
```

❌ **Don't evolve without git safety**

```python
# WRONG: No rollback if self-corruption occurs
target.write_text(evolved_code)

# RIGHT: Git commit after each iteration
target.write_text(evolved_code)
subprocess.run(["git", "add", str(target)])
subprocess.run(["git", "commit", "-m", f"Self-evolution iteration {n}"])
# Now can rollback: git reset HEAD~1
```

## Composability

Self-Evolution Agent composes with the Evolution Agent:

```python
# Normal evolution (agents evolve code)
evolution_agent = EvolutionAgent()

# Meta-evolution (agents evolve themselves)
self_evolution_agent = SelfEvolutionAgent(SafetyConfig(
    max_iterations=3,
    convergence_threshold=0.95,
))

# Composition: Evolve codebase, then evolve evolution agents
meta_pipeline = evolution_agent >> self_evolution_agent
```

## See Also

- **[evolution-agent.md](./evolution-agent.md)** - Main evolution pipeline
- **[grounding.md](./grounding.md)** - AST analysis for structure comparison
- **[memory.md](./memory.md)** - Learning from past self-evolution attempts
- **[C-gents/composition.md](../c-gents/composition.md)** - Fixed-point combinator
- **[spec/principles.md](../principles.md)** - Principle 3 (Ethical): Safe augmentation

---

*"To safely evolve thyself, first know thyself—through testing, measurement, and bounded iteration."*
