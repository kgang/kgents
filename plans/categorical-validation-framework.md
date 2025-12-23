# Categorical Validation Framework

> *"If you can't measure it, you can't claim it."*

---

## The Problem

The phase plans have success propositions:
- "Monad identity correlates with accuracy (r > 0.3)"
- "CPRM heads achieve AUC > 0.75"
- "SBM retains bindings at 100 tokens with >95% accuracy"

But no infrastructure to:
1. Run the experiments
2. Store the results
3. Compare against thresholds
4. Make go/no-go decisions

This document defines that infrastructure.

---

## The Validation Schema

```yaml
# validation/thresholds.yaml

phase_1:
  name: "Foundations"
  gate: "all_required_pass"

  propositions:
    monad_identity_correlation:
      metric: "pearson_r"
      threshold: 0.3
      direction: ">"
      required: true

    sheaf_coherence_correlation:
      metric: "pearson_r"
      threshold: 0.4
      direction: ">"
      required: true

    combined_prediction_auc:
      metric: "roc_auc"
      threshold: 0.7
      direction: ">"
      required: true

phase_2:
  name: "Integration"
  gate: "all_required_pass"

  propositions:
    cprm_monad_head_auc:
      metric: "roc_auc"
      threshold: 0.75
      direction: ">"
      required: true

    cprm_sheaf_head_auc:
      metric: "roc_auc"
      threshold: 0.75
      direction: ">"
      required: true

    search_efficiency_gain:
      metric: "percent_reduction"
      threshold: 30
      direction: ">"
      required: true

    coherence_detection_recall:
      metric: "recall"
      threshold: 0.8
      direction: ">"
      required: true

phase_3:
  name: "Architecture"
  gate: "all_required_pass"

  propositions:
    sbm_retention_100_tokens:
      metric: "accuracy"
      threshold: 0.95
      direction: ">"
      required: true

    sbm_multi_variable:
      metric: "accuracy"
      threshold: 0.9
      direction: ">"
      required: true

    binding_detection_f1:
      metric: "f1"
      threshold: 0.9
      direction: ">"
      required: true

phase_4:
  name: "Synthesis"
  gate: "all_required_pass"

  propositions:
    categorical_agent_compatibility:
      metric: "test_pass_rate"
      threshold: 1.0
      direction: "="
      required: true

    gsm8k_improvement:
      metric: "accuracy_delta"
      threshold: 5.0
      direction: ">"
      required: true

    demo_correct:
      metric: "binary"
      threshold: 1
      direction: "="
      required: true
```

---

## The Validation Runner

```python
# validation/runner.py

from dataclasses import dataclass
from pathlib import Path
import yaml
import json
from datetime import datetime

@dataclass
class PropositionResult:
    name: str
    metric: str
    value: float
    threshold: float
    direction: str
    passed: bool
    required: bool

@dataclass
class PhaseResult:
    phase: str
    propositions: list[PropositionResult]
    passed: bool
    timestamp: str

class ValidationRunner:
    """
    Run experiments, check thresholds, record results.
    """

    def __init__(self, thresholds_path: str = "validation/thresholds.yaml"):
        with open(thresholds_path) as f:
            self.thresholds = yaml.safe_load(f)
        self.results_dir = Path("validation/results")
        self.results_dir.mkdir(exist_ok=True)

    def validate_phase(self, phase: str, measurements: dict[str, float]) -> PhaseResult:
        """
        Check measurements against phase thresholds.

        Args:
            phase: "phase_1", "phase_2", etc.
            measurements: {"monad_identity_correlation": 0.35, ...}

        Returns:
            PhaseResult with pass/fail for each proposition
        """
        phase_config = self.thresholds[phase]
        results = []

        for prop_name, prop_config in phase_config["propositions"].items():
            value = measurements.get(prop_name)

            if value is None:
                # Missing measurement
                results.append(PropositionResult(
                    name=prop_name,
                    metric=prop_config["metric"],
                    value=float('nan'),
                    threshold=prop_config["threshold"],
                    direction=prop_config["direction"],
                    passed=False,
                    required=prop_config["required"]
                ))
                continue

            # Check threshold
            threshold = prop_config["threshold"]
            direction = prop_config["direction"]

            if direction == ">":
                passed = value > threshold
            elif direction == ">=":
                passed = value >= threshold
            elif direction == "<":
                passed = value < threshold
            elif direction == "=":
                passed = abs(value - threshold) < 0.001
            else:
                passed = False

            results.append(PropositionResult(
                name=prop_name,
                metric=prop_config["metric"],
                value=value,
                threshold=threshold,
                direction=direction,
                passed=passed,
                required=prop_config["required"]
            ))

        # Check gate condition
        gate = phase_config["gate"]
        if gate == "all_required_pass":
            phase_passed = all(r.passed for r in results if r.required)
        elif gate == "any_pass":
            phase_passed = any(r.passed for r in results)
        else:
            phase_passed = all(r.passed for r in results)

        result = PhaseResult(
            phase=phase,
            propositions=results,
            passed=phase_passed,
            timestamp=datetime.now().isoformat()
        )

        # Save result
        self._save_result(result)

        return result

    def _save_result(self, result: PhaseResult):
        """Persist result to disk."""
        filename = f"{result.phase}_{result.timestamp.replace(':', '-')}.json"
        path = self.results_dir / filename

        with open(path, 'w') as f:
            json.dump({
                'phase': result.phase,
                'passed': result.passed,
                'timestamp': result.timestamp,
                'propositions': [
                    {
                        'name': p.name,
                        'metric': p.metric,
                        'value': p.value,
                        'threshold': p.threshold,
                        'direction': p.direction,
                        'passed': p.passed,
                        'required': p.required
                    }
                    for p in result.propositions
                ]
            }, f, indent=2)

    def print_result(self, result: PhaseResult):
        """Human-readable output."""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\n{'='*60}")
        print(f"Phase: {result.phase} — {status}")
        print(f"{'='*60}\n")

        for p in result.propositions:
            icon = "✅" if p.passed else "❌"
            req = "[REQUIRED]" if p.required else "[optional]"
            print(f"{icon} {p.name}")
            print(f"   {p.value:.4f} {p.direction} {p.threshold} {req}")
            print()

        if result.passed:
            print("→ Proceed to next phase")
        else:
            failed = [p.name for p in result.propositions if not p.passed and p.required]
            print(f"→ BLOCKED: Fix {', '.join(failed)}")
```

---

## Phase-Specific Experiment Runners

```python
# validation/experiments/phase1.py

async def run_phase1_experiments(
    llm: LLM,
    monad_probe: MonadProbe,
    sheaf_detector: SheafDetector,
    problems: list[Problem],
    n_traces: int = 10
) -> dict[str, float]:
    """
    Run all Phase 1 experiments, return measurements.
    """
    results = []

    for problem in problems:
        for _ in range(n_traces):
            trace = await llm.generate_cot(problem.question)
            answer = extract_answer(trace)

            results.append({
                'correct': problem.check(answer),
                'monad_identity': await monad_probe.identity_test(llm, problem.question),
                'sheaf_coherence': (await sheaf_detector.detect(trace)).score
            })

    df = pd.DataFrame(results)

    # Compute correlations
    monad_corr = df['monad_identity'].corr(df['correct'])
    sheaf_corr = df['sheaf_coherence'].corr(df['correct'])

    # Train simple classifier for AUC
    X = df[['monad_identity', 'sheaf_coherence']]
    y = df['correct']
    clf = LogisticRegression().fit(X, y)
    auc = roc_auc_score(y, clf.predict_proba(X)[:, 1])

    return {
        'monad_identity_correlation': monad_corr,
        'sheaf_coherence_correlation': sheaf_corr,
        'combined_prediction_auc': auc
    }


# validation/experiments/phase2.py

async def run_phase2_experiments(
    cprm: CPRM,
    val_dataset: Dataset,
    search: CPRMSearch,
    baseline_search: BaselineSearch,
    problems: list[Problem]
) -> dict[str, float]:
    """
    Run all Phase 2 experiments.
    """
    # CPRM head AUCs
    predictions = cprm.predict(val_dataset)
    monad_auc = roc_auc_score(val_dataset['monad_label'], predictions.monad)
    sheaf_auc = roc_auc_score(val_dataset['sheaf_label'], predictions.sheaf)

    # Search efficiency
    cprm_nodes = []
    baseline_nodes = []

    for problem in problems[:100]:
        cprm_result = await search.search(problem.question)
        baseline_result = await baseline_search.search(problem.question)

        cprm_nodes.append(cprm_result.nodes_explored)
        baseline_nodes.append(baseline_result.nodes_explored)

    efficiency_gain = (1 - np.mean(cprm_nodes) / np.mean(baseline_nodes)) * 100

    # Coherence detection (synthetic test)
    contradictions = generate_synthetic_contradictions(100)
    detected = sum(1 for c in contradictions if coherence.detect(c).violations)
    recall = detected / len(contradictions)

    return {
        'cprm_monad_head_auc': monad_auc,
        'cprm_sheaf_head_auc': sheaf_auc,
        'search_efficiency_gain': efficiency_gain,
        'coherence_detection_recall': recall
    }


# validation/experiments/phase3.py

async def run_phase3_experiments(
    model: BindingAwareLM,
    baseline: LLM
) -> dict[str, float]:
    """
    Run all Phase 3 experiments.
    """
    benchmark = BindingBenchmark()

    # Retention at 100 tokens
    sbm_results = await benchmark.evaluate(model, gaps=[100])
    baseline_results = await benchmark.evaluate(baseline, gaps=[100])

    # Multi-variable test
    multi_var_accuracy = await benchmark.evaluate_multi_variable(model, n_vars=5)

    # Binding detection F1
    test_set = load_binding_test_set()
    predictions = model.predict_bindings(test_set)
    f1 = f1_score(test_set['labels'], predictions)

    return {
        'sbm_retention_100_tokens': sbm_results[100],
        'sbm_multi_variable': multi_var_accuracy,
        'binding_detection_f1': f1
    }
```

---

## CLI Interface

```python
# validation/cli.py

import click

@click.group()
def cli():
    """Categorical validation CLI."""
    pass

@cli.command()
@click.argument('phase', type=click.Choice(['phase_1', 'phase_2', 'phase_3', 'phase_4']))
def validate(phase: str):
    """Run validation for a phase."""
    runner = ValidationRunner()

    # Load appropriate experiment runner
    if phase == 'phase_1':
        measurements = asyncio.run(run_phase1_experiments(...))
    elif phase == 'phase_2':
        measurements = asyncio.run(run_phase2_experiments(...))
    # etc.

    result = runner.validate_phase(phase, measurements)
    runner.print_result(result)

    sys.exit(0 if result.passed else 1)

@cli.command()
def status():
    """Show validation status across all phases."""
    runner = ValidationRunner()

    for phase in ['phase_1', 'phase_2', 'phase_3', 'phase_4']:
        latest = runner.get_latest_result(phase)
        if latest:
            status = "✅" if latest.passed else "❌"
            print(f"{status} {phase}: {latest.timestamp}")
        else:
            print(f"⬜ {phase}: Not run")

if __name__ == '__main__':
    cli()
```

---

## Usage

```bash
# Run Phase 1 validation
kg validate phase_1

# Output:
# ============================================================
# Phase: phase_1 — ✅ PASSED
# ============================================================
#
# ✅ monad_identity_correlation
#    0.3500 > 0.3 [REQUIRED]
#
# ✅ sheaf_coherence_correlation
#    0.4200 > 0.4 [REQUIRED]
#
# ✅ combined_prediction_auc
#    0.7300 > 0.7 [REQUIRED]
#
# → Proceed to next phase

# Check overall status
kg validate status

# Output:
# ✅ phase_1: 2025-01-15T14:30:00
# ⬜ phase_2: Not run
# ⬜ phase_3: Not run
# ⬜ phase_4: Not run
```

---

## Integration with Witness

```python
# Every validation run gets witnessed

async def validate_with_witness(phase: str):
    runner = ValidationRunner()
    measurements = await run_experiments(phase)
    result = runner.validate_phase(phase, measurements)

    # Witness the decision
    await witness.mark(
        action=f"Validated {phase}",
        reasoning=f"{'PASSED' if result.passed else 'FAILED'}: {json.dumps(measurements)}",
        principles=["composable", "generative"]
    )

    if result.passed:
        await witness.mark(
            action=f"Gate passed: {phase} → next phase",
            reasoning="All required propositions satisfied",
            principles=["composable"]
        )
    else:
        failed = [p.name for p in result.propositions if not p.passed and p.required]
        await witness.mark(
            action=f"Gate blocked: {phase}",
            reasoning=f"Failed: {', '.join(failed)}",
            principles=["ethical"]  # Honest about failures
        )

    return result
```

---

## File Structure

```
validation/
├── thresholds.yaml          # Success criteria
├── runner.py                # Core validation logic
├── cli.py                   # Command-line interface
├── experiments/
│   ├── phase1.py            # Phase 1 experiment runner
│   ├── phase2.py            # Phase 2 experiment runner
│   ├── phase3.py            # Phase 3 experiment runner
│   └── phase4.py            # Phase 4 experiment runner
└── results/                 # Stored validation results
    ├── phase_1_2025-01-15T14-30-00.json
    └── ...
```

---

This is the missing piece. Now the plans have teeth.
