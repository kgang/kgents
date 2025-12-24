---
path: docs/skills/research-protocol
status: active
progress: 100
last_touched: 2025-12-24
touched_by: claude-opus-4.5
blocking: []
enables: [experiment, witness-for-agents, test-patterns]
session_notes: |
  Created to codify Kent's four-phase research methodology.
  Prevents wasteful n=1000 experiments and missing toy examples.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: complete
  MEASURE: deferred
  REFLECT: complete
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.0
---

# Skill: Research Protocol - Four-Phase Experimentation

> *"Evidence over intuition. Traces over reflexes. Scale only after proof."*

**Difficulty**: Medium
**Prerequisites**: Basic statistics, Witness protocol, `kg experiment` CLI
**Files Touched**: `*/_tests/test_*.py`, experiment scripts, research notebooks
**References**: `cli-strategy-tools.md`, `witness-for-agents.md`, `test-patterns.md`

---

## Overview

Every empirical experiment in kgents—whether LLM evaluation, benchmark, or hypothesis test—MUST follow this four-phase protocol. Each phase has a distinct purpose, clear exit criteria, and witness integration.

**The Core Insight**: Most experiments fail at setup, not at scale. Catching bugs with n=1 is infinitely cheaper than discovering them at n=1000.

---

## The Four-Phase Protocol

```
Phase A: Simple Toy Example
    ↓  [validates machinery]
Phase B: Small Run with Full Trace
    ↓  [qualitative understanding]
Phase C: "Proof" Run (n=2-5)
    ↓  [statistical validation]
Phase D: Scale or Attack
    ↓  [production results]
```

---

## Phase A: Simple Toy Example

### Purpose

Validate that your experimental machinery works **at all** before investing in real data.

### Protocol

1. **Create synthetic problem** - One hand-crafted input that exercises the full pipeline
2. **Hand-trace expected output** - Write down what SHOULD happen
3. **Run experiment** - Execute with full verbosity
4. **Compare actual vs. expected** - Every intermediate step

### Example

```python
# Testing middle-name invariance hypothesis
def test_phase_a_toy_example():
    """Phase A: Validate machinery with synthetic case"""
    # Hand-crafted: person with middle name
    toy_input = {
        "name": "Alice Marie Smith",
        "query": "What is Alice's full name?"
    }

    # Hand-traced: expected answer (case-insensitive)
    expected = "alice marie smith"

    # Run experiment
    result = run_middle_name_experiment(toy_input)

    # Verify machinery works
    assert result.answer.lower() == expected
    assert result.confidence > 0.5
    assert result.metadata["tokens_used"] > 0

    print("✓ Phase A: Machinery validated")
```

### Exit Criteria

- [ ] Experiment runs without crashing
- [ ] Output format matches expectations
- [ ] All instrumentation (logging, metrics) works
- [ ] Witness mark created

### Witness Integration

```bash
# Mark Phase A completion
km "Phase A complete: toy example validates middle-name machinery" \
   --reasoning "Synthetic case processes correctly, all metrics captured" \
   --tag experiment,phase-a \
   --json
```

### Common Failures at Phase A

| Failure | Fix |
|---------|-----|
| Import errors | Missing dependencies, check `pyproject.toml` |
| Config missing | Create `.env` or pass explicit config |
| Empty output | Check if LLM API key is set |
| Crash on logging | Ensure log directory exists |

**Philosophy**: If you can't get a toy example working in 15 minutes, you have a setup problem, not a research problem.

---

## Phase B: Small Run with Full Trace

### Purpose

Understand the **phenomenon qualitatively** with one real case and complete instrumentation.

### Protocol

1. **Select single real case** - One trail/problem/agent from production
2. **Enable full tracing** - Log every intermediate state, decision, LLM call
3. **Run with verbosity** - `--debug`, `--trace`, `--explain`
4. **Inspect every step** - Read logs, visualize traces, understand behavior
5. **Document surprises** - What didn't match your mental model?

### Example

```python
# Testing middle-name invariance on real trail
async def run_phase_b_full_trace():
    """Phase B: One real trail with complete instrumentation"""
    # Select single trail (e.g., earliest conversation)
    trail = await storage.get_trail(trail_id="trail-001")

    # Enable full tracing
    tracer = ExperimentTracer(
        log_llm_calls=True,
        log_intermediate_states=True,
        capture_timings=True,
        save_traces_to="./traces/phase_b/"
    )

    # Run with full instrumentation
    result = await run_middle_name_experiment(
        trail=trail,
        tracer=tracer,
        explain=True  # Include reasoning for every decision
    )

    # Save complete trace
    trace_path = tracer.save(f"phase_b_trail_{trail.id}.json")

    # Manual inspection
    print(f"✓ Phase B complete. Inspect trace at: {trace_path}")
    print(f"  - LLM calls: {len(tracer.llm_calls)}")
    print(f"  - States captured: {len(tracer.states)}")
    print(f"  - Total time: {tracer.total_elapsed:.2f}s")

    return result, trace_path
```

### What to Look For

- **Latency distribution** - Are LLM calls 100ms or 10s? Which steps are slow?
- **Decision points** - Where does the agent make choices? Are they correct?
- **Edge cases** - What happens with empty input, malformed data, Unicode?
- **Intermediate states** - Do the transformations make sense?
- **Failure modes** - If it fails, why? Is it recoverable?

### Exit Criteria

- [ ] Complete trace logged for one real case
- [ ] All intermediate states inspected
- [ ] Qualitative understanding of behavior
- [ ] Surprises documented (with `kg annotate --gotcha`)
- [ ] Witness mark created

### Witness Integration

```bash
# Mark Phase B completion with findings
km "Phase B complete: full trace reveals middle-name handling inconsistency" \
   --reasoning "LLM drops middle name 40% of time on first-person queries" \
   --tag experiment,phase-b,finding \
   --json

# Capture gotcha if unexpected behavior found
kg annotate spec/protocols/middle-name-invariance.md --gotcha \
  --section "First-Person Queries" \
  --note "LLM inconsistently preserves middle names in 'my name is...' vs 'Alice Marie Smith' constructions"
```

### Common Patterns at Phase B

| Pattern | Interpretation |
|---------|----------------|
| Consistent behavior | Hypothesis likely valid, proceed to Phase C |
| Random variation | Need more data (Phase C) or better instrumentation |
| Systematic bias | Adjust hypothesis or experimental design |
| Crashes/errors | Fix bugs before Phase C |

**Philosophy**: One fully-traced run teaches you more than 100 black-box runs. If you can't explain what happened on n=1, you won't understand n=1000.

---

## Phase C: "Proof" Run (n=2-5)

### Purpose

Validate hypothesis with **small but statistically meaningful** sample. Answer: "Is the effect real?"

### Protocol

1. **Define hypothesis** - Explicit claim with testable prediction
2. **Choose sample size** - n=2-5 (enough to see variance, not enough to waste compute)
3. **Run experiment** - Same protocol as Phase B, less verbose tracing
4. **Compute statistics** - Mean, std dev, confidence interval
5. **Decide** - Proceed to scale, revise hypothesis, or abandon

### Example

```python
# Phase C: n=5 proof run
async def run_phase_c_proof():
    """Phase C: Small sample to validate hypothesis"""
    # Hypothesis: Middle-name preservation rate > 80%
    hypothesis = "LLM preserves middle names in >80% of queries"
    n = 5

    # Select diverse trails
    trails = await storage.get_trails(limit=n, diverse=True)

    # Run experiment on each
    results = []
    for trail in trails:
        result = await run_middle_name_experiment(
            trail=trail,
            tracer=ExperimentTracer(log_llm_calls=True)  # Light tracing
        )
        results.append(result)

    # Compute statistics
    preservation_rates = [r.preservation_rate for r in results]
    mean_rate = np.mean(preservation_rates)
    std_rate = np.std(preservation_rates)

    # Confidence interval (95%)
    ci_lower, ci_upper = stats.t.interval(
        0.95, len(preservation_rates)-1,
        loc=mean_rate, scale=stats.sem(preservation_rates)
    )

    # Decision
    print(f"Phase C Results (n={n}):")
    print(f"  Mean preservation rate: {mean_rate:.2%} ± {std_rate:.2%}")
    print(f"  95% CI: [{ci_lower:.2%}, {ci_upper:.2%}]")

    if ci_lower > 0.80:
        decision = "PROCEED to Phase D (hypothesis supported)"
    elif ci_upper < 0.80:
        decision = "REVISE hypothesis (effect too weak)"
    else:
        decision = "UNCERTAIN - consider n=10 or revise protocol"

    print(f"  Decision: {decision}")

    return {
        "n": n,
        "mean": mean_rate,
        "std": std_rate,
        "ci": (ci_lower, ci_upper),
        "decision": decision,
        "results": results
    }
```

### Statistical Guidelines

| Sample Size | Use When | Confidence |
|-------------|----------|------------|
| n=2 | Quick sanity check | Very low |
| n=3 | Minimal variance estimate | Low |
| n=5 | Standard "proof" run | Moderate |
| n=10 | High-confidence validation | High |

**Power Analysis**: For effect size d=0.5, n=5 gives ~35% power. This is intentionally low—Phase C is for **filtering bad hypotheses**, not proving good ones.

### Exit Criteria

- [ ] Explicit hypothesis stated
- [ ] n=2-5 samples collected
- [ ] Statistics computed (mean, std, CI)
- [ ] Decision made (scale, revise, or abandon)
- [ ] Witness mark with decision

### Witness Integration

```bash
# Record Phase C decision
kg decide --fast \
  "Proceed to Phase D for middle-name experiment" \
  --reasoning "n=5 shows 87% preservation (CI: [78%, 96%]), exceeds 80% threshold" \
  --json

# Or if hypothesis fails
km "Phase C reveals middle-name hypothesis too weak" \
   --reasoning "n=5 shows 62% preservation (CI: [51%, 73%]), below 80% threshold" \
   --tag experiment,phase-c,negative-result \
   --json
```

### Decision Tree

```
If CI_lower > threshold:
    → PROCEED to Phase D (hypothesis supported)
    → Choose gradual scale path

If CI_upper < threshold:
    → REVISE hypothesis (effect too weak or wrong direction)
    → Return to Phase A/B with new hypothesis

If threshold in CI:
    → UNCERTAIN
    → Option 1: Increase to n=10 for more power
    → Option 2: Revise experimental protocol
    → Option 3: Abandon (too marginal to matter)
```

**Philosophy**: Phase C is a **filter**, not a proof. You're looking for strong signals that justify the compute cost of scaling. Weak or ambiguous results at n=5 rarely become compelling at n=1000.

---

## Phase D: Scale or Attack

### Purpose

Obtain **production-quality results** with full sample size and rigorous methodology.

### Two Paths

#### Path 1: Gradual Increment (Conservative)

Use when:
- Phase C showed marginal support (e.g., CI barely above threshold)
- Compute is expensive (LLM calls, GPU time)
- Early stopping desired

```python
async def run_phase_d_gradual():
    """Phase D Path 1: Gradual scaling with early stopping"""
    checkpoints = [10, 25, 50, 100, 250, 500]

    for n in checkpoints:
        results = await run_experiment(n=n)
        mean, ci = compute_statistics(results)

        print(f"n={n}: mean={mean:.2%}, CI=[{ci[0]:.2%}, {ci[1]:.2%}]")

        # Early stopping: if CI stabilizes
        if n >= 50 and ci_width(ci) < 0.05:  # CI width < 5%
            print(f"✓ Early stop at n={n}: CI stabilized")
            break

    return results
```

#### Path 2: Full Experiment (Aggressive)

Use when:
- Phase C showed strong support
- Compute is cheap
- Need final numbers for publication/decision

```python
async def run_phase_d_full(n=1000):
    """Phase D Path 2: Jump to full sample size"""
    # Run full experiment
    results = await run_experiment(n=n)

    # Comprehensive analysis
    analysis = {
        "descriptive": compute_descriptive_stats(results),
        "inferential": compute_hypothesis_test(results),
        "effect_size": compute_effect_size(results),
        "subgroup": analyze_subgroups(results),
        "sensitivity": run_sensitivity_analysis(results)
    }

    # Generate report
    report_path = generate_report(analysis)
    print(f"✓ Phase D complete. Report: {report_path}")

    return analysis
```

### Exit Criteria

- [ ] Target sample size reached or early stopping triggered
- [ ] Statistical tests performed (t-test, ANOVA, regression, etc.)
- [ ] Effect sizes reported (Cohen's d, R², etc.)
- [ ] Subgroup analyses complete
- [ ] Sensitivity analysis (robustness checks)
- [ ] Full report generated
- [ ] Witness mark with final results

### Witness Integration

```bash
# Mark Phase D completion
km "Phase D complete: middle-name experiment (n=500)" \
   --reasoning "Final preservation rate: 85.3% (CI: [82.1%, 88.5%]), d=0.62 (medium effect)" \
   --tag experiment,phase-d,final-result \
   --json

# Link to report
kg annotate spec/protocols/middle-name-invariance.md \
  --section "Experimental Validation" \
  --link "docs/experiments/middle-name-n500-report.pdf" \
  --note "Phase D: n=500, 85% preservation, statistically significant"
```

### Reporting Standards

Every Phase D experiment MUST produce:

1. **Descriptive Statistics**
   - Sample size (total and subgroups)
   - Mean, median, std dev, quartiles
   - Distribution plots (histogram, density, Q-Q)

2. **Inferential Statistics**
   - Hypothesis test (t-test, ANOVA, χ², etc.)
   - p-value and interpretation
   - Confidence intervals (95% and 99%)
   - Effect size (Cohen's d, R², η², etc.)

3. **Robustness Checks**
   - Sensitivity to outliers
   - Subgroup analyses (by trail type, user, time)
   - Alternative specifications

4. **Practical Significance**
   - Not just statistical significance
   - Cost-benefit analysis
   - Recommendation (implement, revise, abandon)

**Philosophy**: Phase D is where you earn the right to make decisions. Anything worth scaling to n=1000 is worth analyzing rigorously.

---

## When to Use This Protocol

### MUST Use (Mandatory)

- ANY hypothesis test about agent behavior
- ANY LLM evaluation or benchmark
- ANY A/B test of system components
- ANY experiment that will inform a decision

### SHOULD Use (Recommended)

- Exploratory data analysis (Phase A/B only)
- Debugging performance issues (Phase A/B/C)
- Validating refactoring (Phase C as regression test)

### MAY Use (Optional)

- One-off analyses (Phase A/B may suffice)
- Quick sanity checks (Phase A only)

### MUST NOT Skip Phases

| Skip | Consequence |
|------|-------------|
| Skip Phase A | Waste hours debugging at Phase C |
| Skip Phase B | No qualitative understanding, can't interpret results |
| Skip Phase C | Waste compute on bad hypotheses |
| Skip Phase D | No actionable results |

---

## Anti-Patterns (Avoid These)

### 1. The "Full Send" Anti-Pattern

**Symptom**: Start with n=1000 on first run

**Why Bad**: If hypothesis is wrong, you wasted 1000x the compute. If setup is broken, you get 1000 errors instead of 1.

**Fix**: Always Phase A → B → C → D

### 2. The "Black Box" Anti-Pattern

**Symptom**: Skip Phase B, go straight from toy example to n=100

**Why Bad**: No qualitative understanding. When results are surprising, you can't debug.

**Fix**: Always inspect one full trace before scaling

### 3. The "Binary Scale" Anti-Pattern

**Symptom**: Only run n=1 (toy) or n=1000 (production), nothing between

**Why Bad**: No validation. Either waste compute or lack confidence.

**Fix**: Use Phase C (n=2-5) as filter before committing to scale

### 4. The "p-Hacking" Anti-Pattern

**Symptom**: Run experiment, get p=0.06, add more data until p<0.05

**Why Bad**: Invalidates statistical inference (selection bias)

**Fix**: Pre-commit to sample size at Phase C. If p>0.05, report null result or revise hypothesis, don't just add data.

### 5. The "Silent Failure" Anti-Pattern

**Symptom**: Phase C shows weak/null result, proceed to Phase D anyway

**Why Bad**: Compounds the mistake. Weak effects at n=5 don't become strong at n=500.

**Fix**: Treat Phase C as a **gate**. Null/weak results → revise or abandon, not scale.

---

## Integration with `kg experiment`

The `kg experiment` CLI implements Bayesian adaptive experimentation with this protocol:

```bash
# Phase A: Generate single example
kg experiment generate \
  --spec "Test middle-name preservation" \
  --model gpt-4o-mini \
  --n 1 \
  --trace \
  --output phase_a_result.json

# Phase B: Full trace on real case
kg experiment generate \
  --spec "Test middle-name preservation on trail-001" \
  --model gpt-4o \
  --n 1 \
  --explain \
  --trace \
  --output phase_b_trace.json

# Phase C: Adaptive sampling (starts at n=5)
kg experiment generate \
  --spec "Middle-name preservation rate > 80%" \
  --model gpt-4o \
  --adaptive \
  --confidence 0.95 \
  --max-samples 10 \
  --output phase_c_results.json

# Phase D: Full experiment
kg experiment generate \
  --spec "Final middle-name preservation validation" \
  --model gpt-4o \
  --n 500 \
  --output phase_d_results.json
```

**Adaptive Mode**: `--adaptive` implements Bayesian sequential testing. It starts at n=5 and adds samples until confidence threshold reached or max-samples hit. This automates the Phase C → Phase D transition.

---

## Integration with Witness Protocol

Every phase should create witness marks for traceability:

```bash
# Start of experiment
km "Starting middle-name experiment" \
   --reasoning "Hypothesis: preservation rate > 80%" \
   --tag experiment,start \
   --json

# Phase A
km "Phase A complete: toy example validates machinery" \
   --tag experiment,phase-a \
   --json

# Phase B
km "Phase B complete: full trace shows inconsistent first-person handling" \
   --reasoning "LLM drops middle names 40% of time on 'my name is...' queries" \
   --tag experiment,phase-b,finding \
   --json

# Phase C with decision
kg decide --fast \
  "Proceed to Phase D" \
  --reasoning "n=5 shows 87% preservation (CI: [78%, 96%])" \
  --json

# Phase D final
km "Phase D complete: n=500 middle-name experiment" \
   --reasoning "85.3% preservation (CI: [82.1%, 88.5%]), d=0.62, p<0.001" \
   --tag experiment,phase-d,final \
   --json
```

**Query Before Starting**: Check for prior experiments to avoid duplication:

```bash
# Check if experiment already run
kg witness show --grep "middle-name experiment" --json

# Check recent experimental decisions
kg witness show --tag experiment,decision --json
```

---

## Integration with Test Patterns

The research protocol complements the T-gent test taxonomy:

| Research Phase | T-gent Type | Purpose |
|----------------|-------------|---------|
| Phase A | Type I (Contracts) | Validate preconditions/postconditions |
| Phase B | Type III (Spies) | Trace behavior, log decisions |
| Phase C | Type II (Saboteurs) | Property-based testing at small scale |
| Phase D | Type IV (Judges) | Semantic validation at scale |

**Example**: Combine Phase C with Hypothesis (saboteur testing):

```python
from hypothesis import given, strategies as st

# Phase C: Property-based proof run
@given(st.text(min_size=5, max_size=100))
async def test_phase_c_property_middle_name_preservation(name_input):
    """Phase C: n=100 property-based test (auto-generated by Hypothesis)"""
    result = await run_middle_name_experiment({"name": name_input})

    # Property: output should contain all words from input
    input_words = set(name_input.lower().split())
    output_words = set(result.answer.lower().split())

    assert input_words.issubset(output_words), \
        f"Lost words: {input_words - output_words}"
```

Hypothesis will automatically generate n=100 test cases (Phase C scale) with diverse inputs (saboteur role).

---

## Composition with `kg compose`

Create saved research workflows:

```bash
# Define research composition (save to ~/.config/kgents/compositions/research.json)
kg compose --define "research-protocol" \
  --steps "probe health" \
           "experiment generate --n 1 --trace" \
           "witness mark 'Phase A complete'" \
           "experiment generate --n 1 --explain" \
           "witness mark 'Phase B complete'" \
           "experiment generate --adaptive --max 10" \
           "decide --fast 'Proceed to Phase D'" \
           "experiment generate --n 500"

# Run saved composition
kg compose --run "research-protocol" \
  --spec "Test middle-name preservation" \
  --model gpt-4o
```

**Pre-Saved Compositions**:

| Name | Phases | Use When |
|------|--------|----------|
| `research-quick` | A, B, C only | Hypothesis validation, no production run |
| `research-full` | A, B, C, D | Complete experiment with scaling |
| `research-exploratory` | A, B only | Qualitative exploration, no hypothesis |

---

## Example: Complete Research Session

### Hypothesis

"Middle-name preservation rate in LLM responses is >80% across all query types."

### Phase A: Toy Example (5 minutes)

```python
# test_middle_name_phase_a.py
def test_phase_a_toy():
    result = run_experiment({"name": "Alice Marie Smith", "query": "What is your name?"})
    assert "Marie" in result.answer.lower()
    print("✓ Phase A: Machinery validated")
```

```bash
pytest test_middle_name_phase_a.py -v
km "Phase A complete: toy example validates middle-name machinery" --json
```

### Phase B: Full Trace (20 minutes)

```python
# scripts/phase_b_full_trace.py
async def main():
    trail = await storage.get_trail("trail-001")
    tracer = ExperimentTracer(log_llm_calls=True, log_states=True)

    result = await run_experiment(trail, tracer=tracer, explain=True)
    trace_path = tracer.save("phase_b_trail_001.json")

    print(f"Trace saved: {trace_path}")
    # Manual inspection of trace reveals:
    # - 3/5 queries preserve middle name
    # - First-person queries drop middle name 40% of time
```

```bash
uv run python scripts/phase_b_full_trace.py
km "Phase B complete: full trace shows 60% preservation, first-person bias" \
   --reasoning "LLM inconsistent on 'my name is...' vs 'Alice Marie Smith' constructions" \
   --json

# Capture gotcha
kg annotate spec/protocols/middle-name-invariance.md --gotcha \
  --section "Query Type Variations" \
  --note "First-person queries have 20% lower middle-name preservation"
```

### Phase C: Proof Run (1 hour)

```python
# scripts/phase_c_proof.py
async def main():
    results = await run_experiment_batch(n=5, diverse=True)

    preservation_rates = [r.preservation_rate for r in results]
    mean = np.mean(preservation_rates)  # 0.87
    ci = stats.t.interval(0.95, 4, loc=mean, scale=stats.sem(preservation_rates))
    # ci = (0.78, 0.96)

    print(f"Phase C: mean={mean:.2%}, CI=[{ci[0]:.2%}, {ci[1]:.2%}]")

    if ci[0] > 0.80:
        print("✓ Hypothesis supported, proceed to Phase D")
        return "PROCEED"
    else:
        print("✗ Hypothesis weak, revise or abandon")
        return "REVISE"
```

```bash
uv run python scripts/phase_c_proof.py
# Output: "✓ Hypothesis supported, proceed to Phase D"

kg decide --fast \
  "Proceed to Phase D for middle-name experiment" \
  --reasoning "n=5 shows 87% preservation (CI: [78%, 96%]), exceeds 80% threshold" \
  --json
```

### Phase D: Full Experiment (4 hours)

```python
# scripts/phase_d_full.py
async def main():
    # Run full experiment
    results = await run_experiment_batch(n=500)

    # Comprehensive analysis
    analysis = {
        "n": 500,
        "mean": 0.853,
        "std": 0.142,
        "ci_95": (0.821, 0.885),
        "effect_size_d": 0.62,  # Medium effect
        "p_value": 0.0001,
        "subgroups": {
            "first_person": {"mean": 0.791, "n": 200},
            "third_person": {"mean": 0.912, "n": 300}
        }
    }

    # Generate report
    generate_report(analysis, output="middle_name_n500_report.pdf")

    print(f"✓ Phase D complete: {analysis['mean']:.1%} preservation")
    return analysis
```

```bash
uv run python scripts/phase_d_full.py

# Mark completion
km "Phase D complete: middle-name experiment (n=500)" \
   --reasoning "85.3% preservation (CI: [82.1%, 88.5%]), d=0.62, p<0.001" \
   --tag experiment,phase-d,final \
   --json

# Link report to spec
kg annotate spec/protocols/middle-name-invariance.md \
  --section "Experimental Validation" \
  --link "docs/experiments/middle_name_n500_report.pdf" \
  --note "Phase D: n=500, 85% preservation, first-person queries 12% lower"
```

**Total Time**: ~5.5 hours (5min + 20min + 1hr + 4hr)
**Total Cost**: ~$50 in LLM calls (1 + 1 + 5 + 500 queries)

**Compare to naive approach** (jump to n=500 immediately):
- Time: 4 hours (faster)
- Cost: $500 (10x more expensive if hypothesis was wrong)
- Risk: High (no validation, no qualitative understanding)

**The Protocol Saved**:
- $450 in compute (if hypothesis had failed at Phase C)
- 3 hours of debugging (Phase A caught setup bugs)
- Weeks of confusion (Phase B revealed first-person bias early)

---

## Summary: The Four-Phase Mantra

```
Phase A: "Does the machine work?"        → 1 synthetic case, hand-traced
Phase B: "What is actually happening?"   → 1 real case, full trace
Phase C: "Is the effect real?"           → n=2-5, statistics
Phase D: "What are the numbers?"         → n=target, full analysis
```

**Rules**:
1. **Never skip Phase A** - Catches 80% of setup bugs
2. **Never skip Phase B** - Qualitative understanding is irreplaceable
3. **Never skip Phase C** - Small-scale validation prevents waste
4. **Never skip witness marks** - Traceability enables learning

**Integration**:
- Use `kg experiment` for execution
- Use `kg witness` for traceability
- Use `kg compose` for workflows
- Use `kg annotate` for gotchas

**Philosophy**: Research without protocol is gambling. Protocol without witness is forgetting. Witness without action is theater.

---

*Last Updated: 2025-12-24*
*Related Skills: cli-strategy-tools.md, witness-for-agents.md, test-patterns.md*
