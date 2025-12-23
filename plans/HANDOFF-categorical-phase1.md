# HANDOFF: Categorical Phase 1 - Rigorous Correlation Study

> *"Measure first. Build only what measurement validates."*
> *"The proof IS the decision. The mark IS the witness."*

**Created**: 2025-12-23
**Revised**: 2025-12-23 (Methodology hardening)
**Status**: Infrastructure complete, methodology enhanced
**Priority**: HIGH — kgents 2.0 gate

---

## Context for Next Session

You are continuing **Phase 1: Foundations** of the categorical reinvention plan. The infrastructure is built. Now you need to run a **scientifically rigorous** correlation study.

### The Hypothesis (kgents 2.0)

> "LLM reasoning failures are not random. They follow patterns that category theory predicts."

Specifically:
- **Monad law violations** correlate with chain-of-thought breakdowns
- **Sheaf incoherence** correlates with hallucinations

If true, categorical laws become verification signals for LLM reasoning.

### What's Already Built

```
services/categorical/
├── __init__.py              # Crown Jewel exports
├── probes.py                # MonadProbe + SheafDetector + CategoricalProbeRunner
├── study.py                 # CorrelationStudy + ProblemSet + StudyConfig
└── _tests/                  # 41 tests (all passing)

protocols/agentese/contexts/
└── concept_categorical.py   # AGENTESE paths: concept.categorical.*

initiatives/
└── categorical-phase1.yaml  # ValidationEngine initiative with gate criteria
```

### Phase 1 Gate Criteria

| Metric | Threshold | Required |
|--------|-----------|----------|
| Monad identity correlation | r > 0.3 | Yes |
| Sheaf coherence correlation | r > 0.4 | Yes |
| Combined AUC | > 0.7 | Yes |
| Sample size | n ≥ 500 | Yes |
| **NEW: Beats random baseline** | Δ > 0.15 | Yes |
| **NEW: Significant p-value** | p < 0.01 | Yes |

---

## METHODOLOGY ENHANCEMENTS (Critical)

### Enhancement 1: Baseline Comparisons

**Why**: Correlation without baselines is meaningless. Random noise can correlate.

**Add to study.py**:
```python
@dataclass
class BaselineResults:
    """Results from baseline comparisons."""
    random_corr: CorrelationResult      # Random scores [0,1]
    length_corr: CorrelationResult      # Trace length as predictor
    confidence_corr: CorrelationResult  # LLM self-confidence

    @property
    def categorical_delta(self) -> float:
        """How much categorical beats random."""
        return self.categorical_corr - self.random_corr.correlation
```

**Implementation**:
1. **Random baseline**: Generate random scores, compute correlation with correctness
2. **Length heuristic**: Trace length often correlates with correctness
3. **Confidence heuristic**: LLM's stated confidence

The categorical probes must beat all three to be meaningful.

### Enhancement 2: Bootstrapped Confidence Intervals

**Why**: Point estimates (r=0.35) are incomplete. We need uncertainty.

**Add to _compute_correlation()**:
```python
def _compute_correlation_with_ci(
    self,
    metric_name: str,
    values: list[float],
    correct: list[bool],
    n_bootstrap: int = 1000,
) -> CorrelationResult:
    """Compute correlation with bootstrapped 95% CI."""
    import random

    # Bootstrap
    bootstrap_rs = []
    n = len(values)
    for _ in range(n_bootstrap):
        indices = [random.randint(0, n-1) for _ in range(n)]
        sample_vals = [values[i] for i in indices]
        sample_corr = [correct[i] for i in indices]
        r = self._pearson(sample_vals, sample_corr)
        bootstrap_rs.append(r)

    # 95% CI
    sorted_rs = sorted(bootstrap_rs)
    ci_low = sorted_rs[int(0.025 * n_bootstrap)]
    ci_high = sorted_rs[int(0.975 * n_bootstrap)]

    return CorrelationResult(
        ...,
        ci_low=ci_low,
        ci_high=ci_high,
    )
```

**Gate change**: The **lower bound of the CI** must exceed threshold, not just point estimate.

### Enhancement 3: Permutation Test for Significance

**Why**: p-value from t-test assumes normality. Permutation tests are exact.

```python
def _permutation_test(
    self,
    values: list[float],
    correct: list[bool],
    observed_r: float,
    n_permutations: int = 10000,
) -> float:
    """Exact p-value via permutation test."""
    import random

    count_extreme = 0
    correct_copy = list(correct)

    for _ in range(n_permutations):
        random.shuffle(correct_copy)
        perm_r = self._pearson(values, correct_copy)
        if abs(perm_r) >= abs(observed_r):
            count_extreme += 1

    return count_extreme / n_permutations
```

### Enhancement 4: Automatic Step Extraction for Associativity

**Why**: Current associativity test requires pre-defined steps. This limits applicability.

**New class in probes.py**:
```python
class StepExtractor:
    """Extract reasoning steps from a trace automatically."""

    EXTRACTION_PROMPT = '''Identify the distinct reasoning steps in this trace.

A step is a self-contained logical move (calculation, inference, lookup).
Return each step on a new line, prefixed with "STEP: ".

Trace:
{trace}

Steps:'''

    async def extract(self, trace: str) -> tuple[str, ...]:
        """Extract steps from trace."""
        response = await self.llm.generate(
            system="You identify reasoning steps.",
            user=self.EXTRACTION_PROMPT.format(trace=trace),
        )
        return self._parse_steps(response.text)
```

Now associativity can be tested on ANY problem:
1. Generate trace
2. Extract steps automatically
3. Test different groupings

### Enhancement 5: Hybrid Sheaf Detection

**Why**: Using LLM to check contradictions is circular. If the LLM reasons poorly, it'll miss contradictions.

**Add symbolic pre-filter**:
```python
class SymbolicContradictionChecker:
    """Fast symbolic checks before expensive LLM calls."""

    def check_numeric_contradiction(
        self,
        claim_a: str,
        claim_b: str,
    ) -> bool | None:
        """Check if claims have contradictory numbers."""
        # Extract numbers from both claims
        nums_a = self._extract_numbers(claim_a)
        nums_b = self._extract_numbers(claim_b)

        # If same variable has different values, contradiction
        # E.g., "x = 5" vs "x = 7"
        for var_a, val_a in nums_a.items():
            if var_a in nums_b and nums_b[var_a] != val_a:
                return True

        return None  # Defer to LLM

    def _extract_numbers(self, text: str) -> dict[str, float]:
        """Extract variable-value pairs from text."""
        import re
        patterns = [
            r"(\w+)\s*=\s*(\d+(?:\.\d+)?)",  # x = 5
            r"(\w+)\s+is\s+(\d+(?:\.\d+)?)",  # x is 5
            r"(\w+):\s*(\d+(?:\.\d+)?)",      # x: 5
        ]
        results = {}
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                var, val = match.groups()
                results[var.lower()] = float(val)
        return results
```

**Pipeline**: Symbolic check → LLM only if symbolic inconclusive

---

## Your Tasks (Revised)

### Task 1: Implement Methodology Enhancements

Add the enhancements above to `services/categorical/`:
1. **BaselineComparison** class in study.py
2. **Bootstrap CI** in _compute_correlation()
3. **Permutation test** in study.py
4. **StepExtractor** in probes.py
5. **SymbolicContradictionChecker** in probes.py

### Task 2: Create Rigorous Problem Dataset

Create `impl/claude/data/categorical_phase1_problems.json` with:

```json
{
  "name": "categorical_phase1_rigorous",
  "description": "Curated benchmark for Phase 1 validation",
  "problems": [
    {
      "id": "gsm8k_001",
      "question": "Janet's ducks lay 16 eggs per day...",
      "answer": "18",
      "type": "MATH",
      "difficulty": "easy",
      "expected_failure_mode": null,
      "metadata": {"source": "gsm8k"}
    },
    {
      "id": "strategyqa_001",
      "question": "Would a peanut allergy make youستبعد from eating pad thai?",
      "answer": "yes",
      "type": "MULTI_HOP",
      "difficulty": "medium",
      "expected_failure_mode": "factual_lookup",
      "metadata": {"source": "strategyqa", "hops": 2}
    }
  ]
}
```

**Sources** (in order of preference):
1. **GSM8K** (math): 250 problems sampled by difficulty
2. **StrategyQA** (multi-hop): 150 problems
3. **LogiQA** (logic): 100 problems

This gives n=500 with diverse problem types.

### Task 3: Run Enhanced Correlation Study

```python
import asyncio
from pathlib import Path
from agents.k.llm import create_llm_client
from services.categorical.study import (
    CorrelationStudy,
    ProblemSet,
    StudyConfig,
    BaselineConfig,  # NEW
)

async def run_phase1_study():
    # Load problems
    problem_set = ProblemSet.from_json(
        Path("impl/claude/data/categorical_phase1_problems.json")
    )

    # Create LLM client
    llm = create_llm_client()

    # Initialize study
    study = CorrelationStudy(llm, problem_set)

    # Run with enhanced config
    result = await study.run(StudyConfig(
        n_problems=500,
        n_samples_per_problem=5,
        run_associativity=True,
        temperature=0.0,
        max_concurrent=10,
        # NEW: Enhanced methodology
        run_baselines=True,
        n_bootstrap=1000,
        n_permutations=10000,
        significance_level=0.01,  # Stricter
    ))

    # Enhanced output
    print(f"=== CORRELATION RESULTS ===")
    print(f"Monad identity r: {result.monad_identity_corr.correlation:.3f}")
    print(f"  95% CI: [{result.monad_identity_corr.ci_low:.3f}, {result.monad_identity_corr.ci_high:.3f}]")
    print(f"  p-value (permutation): {result.monad_identity_corr.p_value:.4f}")
    print()
    print(f"Sheaf coherence r: {result.sheaf_coherence_corr.correlation:.3f}")
    print(f"  95% CI: [{result.sheaf_coherence_corr.ci_low:.3f}, {result.sheaf_coherence_corr.ci_high:.3f}]")
    print(f"  p-value (permutation): {result.sheaf_coherence_corr.p_value:.4f}")
    print()
    print(f"Combined AUC: {result.combined_auc:.3f}")
    print()
    print(f"=== BASELINE COMPARISONS ===")
    print(f"Random baseline r: {result.baselines.random_corr.correlation:.3f}")
    print(f"Length baseline r: {result.baselines.length_corr.correlation:.3f}")
    print(f"Categorical Δ over random: {result.categorical_delta:.3f}")
    print()

    if result.passed_gate:
        print("✅ PHASE 1 GATE PASSED — Proceed to Phase 2")
    else:
        print(f"❌ BLOCKED BY: {result.blockers}")

    return result

# Run
result = asyncio.run(run_phase1_study())
```

### Task 4: Analyze Results with Nuance

**If gate passes (all criteria met)**:
1. Document in `docs/theory/categorical-validation-results.md`:
   - Full correlation table with CIs
   - Baseline comparisons
   - Effect size interpretation
   - Scatter plots of scores vs. correctness
2. Emit witness mark with Toulmin proof structure
3. Begin Phase 2 planning

**If gate fails, analyze which mode**:

| Failure Mode | Likely Cause | Next Step |
|--------------|--------------|-----------|
| r < 0.3 but CI includes 0.3 | Insufficient power | Run more problems |
| r < 0.3 and CI excludes 0.3 | Theory doesn't hold | Revisit probe design |
| Doesn't beat random | Measuring noise | Probes need redesign |
| p > 0.01 | Not significant | More samples, different probes |
| Low AUC despite good r | Non-linear relationship | Try different classifier |

---

## Key Files to Read

| File | Why |
|------|-----|
| `plans/categorical-reinvention-phase1-foundations.md` | Original plan |
| `services/categorical/probes.py` | Current probe implementation |
| `services/categorical/study.py` | Study runner (enhance this) |
| `docs/theory/03-monadic-reasoning.md` | Theory: monad laws as rationality |
| `docs/theory/05-sheaf-coherence.md` | Theory: sheaf condition |

---

## Gotchas (Enhanced)

1. **LLM calls are expensive** — 500 × 5 × 2 probes + baselines = thousands of calls. Start with n=50 for debugging.

2. **Bootstrap is computationally intensive** — 1000 bootstrap samples × 500 problems × correlation computation. Consider caching intermediate results.

3. **Permutation tests need randomness** — Seed the RNG for reproducibility: `random.seed(42)`.

4. **Symbolic checker is incomplete** — It catches numeric contradictions only. LLM is still needed for semantic contradictions.

5. **Automatic step extraction may fail** — For some traces, steps are implicit. Have a fallback to manual annotation.

6. **Baseline correlation might be higher than expected** — If trace length strongly correlates with correctness, categorical probes need to beat it substantially.

7. **Multiple testing correction** — We're testing 3+ hypotheses. Consider Bonferroni: α' = 0.01/3 ≈ 0.003.

---

## Success Criteria (Enhanced)

At session end, you should have:

1. ✅ Methodology enhancements implemented
2. ✅ Problem dataset created (500+ problems, diverse sources)
3. ✅ Baseline comparisons implemented and run
4. ✅ Bootstrap CIs computed for all correlations
5. ✅ Permutation p-values computed
6. ✅ Gate decision made with full statistical evidence
7. ✅ Results documented with uncertainty quantification
8. ✅ Witness mark emitted with Toulmin proof
9. ✅ NOW.md updated

---

## Voice Anchors

*"Daring, bold, creative, opinionated but not gaudy"*
*"The proof IS the decision. The mark IS the witness."*
*"Measure first. Build only what measurement validates."*
*"An agent is a thing that justifies its behavior."*

---

## Quick Start Commands

```bash
# Verify infrastructure
cd impl/claude && uv run pytest services/categorical/ -q

# Check AGENTESE paths
kg concept.categorical.manifest

# Run small-scale test (before full study)
uv run python -c "
import asyncio
from services.categorical.study import CorrelationStudy, ProblemSet, StudyConfig
from agents.k.llm import create_llm_client
from pathlib import Path

async def main():
    # Use a small test set first
    ps = ProblemSet.from_json(Path('data/categorical_phase1_problems.json'))
    study = CorrelationStudy(create_llm_client(), ps)
    result = await study.run(StudyConfig(
        n_problems=50,  # Small for debugging
        run_baselines=True,
    ))
    print(f'Gate: {\"PASS\" if result.passed_gate else \"FAIL\"}')
    print(f'Categorical Δ over random: {result.categorical_delta:.3f}')

asyncio.run(main())
"
```

---

## The Philosophical Stakes

This study determines whether kgents 2.0 is:

**A) A genuine paradigm** — Categorical laws are a new lens on LLM reasoning. We can use them for verification, guidance, and explanation.

**B) A beautiful fiction** — The theory is aesthetically pleasing but doesn't connect to reality. We pivot.

Either answer is valuable. **The methodology must be rigorous enough that we trust the answer.**

---

*"The bet is placed. The methodology is sound. Now we measure."*
