# Experiments Protocol: Detailed Designs

> *"The experiment IS the validation."*

**Purpose**: Detailed protocols for empirically validating kgents theoretical claims
**Priority**: HIGH
**Status**: Ready to Execute

---

## Overview

This document provides complete experimental protocols for validating the kgents theoretical framework. Each experiment includes:
- Hypothesis
- Methodology
- Data collection
- Success criteria
- Analysis plan
- Timeline

---

## Pilot Integration

**Goal**: Make every pilot run an experiment with explicit hypotheses.

### Minimal Run Artifacts
Create `runs/run-XXX/EXPERIMENTS.md` with:

```
# Experiments (Run XXX)

## Hypothesis H1
Claim: [what change should improve]
Metric: [how measured]
Threshold: [success target]

## Hypothesis H2 (optional)
Claim: [secondary]
Metric: [secondary]
Threshold: [success target]
```

### Prompt Hooks (Minimal Insertions)
Add a short "Experiment Hook" at the top of each role prompt:
- CREATIVE: state intended outcome change
- ADVERSARIAL: state verification metric
- PLAYER: state experiential metric

### Outcome Target
- Each run yields a measurable delta tied to one hypothesis.
- Enables post-run comparison across pilots without ambiguous goals.

---

## Experiment 1: Loss-Difficulty Correlation

### 1.1 Hypothesis

**H1**: Galois loss L(P) correlates with task failure probability.

```
P(failure | T) ∝ L(P)
```

**Theoretical Basis**: spec/theory/galois-modularization.md, Conjecture 4.1.1

### 1.2 Methodology

```python
@dataclass
class LossDifficultyExperiment:
    """
    Validate correlation between Galois loss and task difficulty.

    Independent Variable: Galois loss L(P)
    Dependent Variable: Failure rate over N trials
    """

    # Configuration
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.0
    trials_per_task: int = 20
    n_tasks: int = 200

    # Dataset (stratified by domain)
    task_domains = {
        "coding": 50,
        "writing": 50,
        "reasoning": 50,
        "data_analysis": 50,
    }

    async def run(self) -> ExperimentResult:
        results = []

        for domain, count in self.task_domains.items():
            tasks = await self.load_tasks(domain, count)

            for task in tqdm(tasks, desc=f"Processing {domain}"):
                # Step 1: Compute Galois loss
                galois = GaloisLossComputer(llm=self.llm)
                loss_result = await galois.compute(task.prompt)

                # Step 2: Execute task multiple times
                successes = 0
                for trial in range(self.trials_per_task):
                    result = await self.execute_task(task)
                    if result.success:
                        successes += 1

                failure_rate = 1 - (successes / self.trials_per_task)

                results.append(TaskResult(
                    task_id=task.id,
                    domain=domain,
                    galois_loss=loss_result.total,
                    failure_rate=failure_rate,
                    trials=self.trials_per_task,
                ))

        return self.analyze(results)

    def analyze(self, results: list[TaskResult]) -> ExperimentResult:
        """Statistical analysis of results."""
        from scipy import stats
        import numpy as np

        losses = [r.galois_loss for r in results]
        failures = [r.failure_rate for r in results]

        # Primary analysis: Pearson correlation
        r, p_value = stats.pearsonr(losses, failures)

        # Secondary: Spearman (robust to outliers)
        rho, rho_p = stats.spearmanr(losses, failures)

        # Tertiary: Linear regression
        slope, intercept, r_value, p_val, std_err = stats.linregress(losses, failures)

        return ExperimentResult(
            hypothesis="H1: Loss-Difficulty Correlation",
            primary_metric=PearsonCorrelation(r=r, p=p_value),
            secondary_metrics={
                "spearman": SpearmanCorrelation(rho=rho, p=rho_p),
                "linear_regression": LinearRegression(
                    slope=slope,
                    intercept=intercept,
                    r_squared=r_value**2,
                    std_err=std_err,
                ),
            },
            success=r > 0.6 and p_value < 0.01,
            n=len(results),
            by_domain={
                domain: self._analyze_domain(
                    [r for r in results if r.domain == domain]
                )
                for domain in self.task_domains
            },
        )
```

### 1.3 Task Dataset Specification

```yaml
# Task dataset structure
task_schema:
  id: string
  domain: enum[coding, writing, reasoning, data_analysis]
  prompt: string
  ground_truth: string | null  # For automated evaluation
  difficulty_label: enum[easy, medium, hard]  # Human-assigned baseline
  evaluation_method: enum[exact_match, semantic_similarity, llm_judge]

# Example tasks per domain
coding_examples:
  - id: "code_001"
    prompt: "Write a function to check if a number is prime"
    difficulty_label: easy
    evaluation_method: exact_match

  - id: "code_050"
    prompt: "Implement a red-black tree with insertion, deletion, and rebalancing"
    difficulty_label: hard
    evaluation_method: llm_judge

writing_examples:
  - id: "write_001"
    prompt: "Write a one-paragraph summary of the French Revolution"
    difficulty_label: easy

  - id: "write_050"
    prompt: "Write a technical blog post explaining transformer architectures to non-ML engineers"
    difficulty_label: hard

reasoning_examples:
  - id: "reason_001"
    prompt: "If all A are B, and all B are C, what can we conclude about A and C?"
    difficulty_label: easy
    ground_truth: "All A are C"

  - id: "reason_050"
    prompt: "Given these 5 constraints, find all valid assignments..."
    difficulty_label: hard
```

### 1.4 Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Pearson r | > 0.6 | Moderate-strong correlation |
| p-value | < 0.01 | Statistical significance |
| Consistency | ±0.15 across domains | Generalization |

### 1.5 Timeline

- **Week 1**: Curate task dataset (200 tasks)
- **Week 2**: Implement data collection pipeline
- **Week 3-4**: Execute experiments (8000 task executions)
- **Week 5**: Analysis and reporting

---

## Experiment 2: Polynomial Emergence

### 2.1 Hypothesis

**H2**: Repeated restructuring converges to polynomial functor structure.

```
lim_{n→∞} Rⁿ(P) = Fix(R) ≅ PolyAgent[S, A, B]
```

**Theoretical Basis**: spec/theory/galois-modularization.md, Corollary 3.1.3

### 2.2 Methodology

```python
@dataclass
class PolynomialEmergenceExperiment:
    """
    Test whether restructuring converges to polynomial structure.

    Measures:
    1. Convergence rate (iterations to stability)
    2. Polynomial structure presence (states, inputs, outputs)
    3. Stability of fixed point
    """

    prompts: list[str]  # 100 diverse prompts
    max_iterations: int = 20
    convergence_threshold: float = 0.01

    async def run(self) -> ConvergenceResult:
        results = []

        for prompt in tqdm(self.prompts):
            trajectory = [prompt]
            losses = []

            for i in range(self.max_iterations):
                # Restructure
                modular = await self.restructure(trajectory[-1])
                flattened = await self.reconstitute(modular)
                trajectory.append(flattened)

                # Compute loss (delta from previous)
                if i > 0:
                    delta = await self.semantic_distance(
                        trajectory[-1], trajectory[-2]
                    )
                    losses.append(delta)

                    # Check convergence
                    if delta < self.convergence_threshold:
                        break

            # Analyze fixed point
            fixed_point = trajectory[-1]
            poly_structure = await self.extract_polynomial_structure(fixed_point)

            results.append(PromptConvergence(
                initial_prompt=prompt,
                iterations=len(trajectory) - 1,
                converged=len(trajectory) < self.max_iterations + 1,
                final_loss=losses[-1] if losses else None,
                loss_trajectory=losses,
                polynomial=poly_structure,
            ))

        return self.analyze(results)

    async def extract_polynomial_structure(
        self, prompt: str
    ) -> PolynomialStructure:
        """
        Extract S, A(s), B from converged prompt.

        A valid polynomial structure has:
        - States: Distinct operational modes
        - Inputs: Mode-dependent valid inputs
        - Output: Common output type
        """
        response = await self.llm.generate(
            system="""Analyze this prompt for polynomial functor structure.
Identify:
1. States (S): Distinct modes or phases of operation
2. Inputs per state (A(s)): What inputs are valid for each state
3. Output (B): The common output type

Format as JSON:
{
    "states": ["state1", "state2", ...],
    "inputs": {"state1": ["input_type1", ...], "state2": [...]},
    "output": "output_type",
    "is_polynomial": true/false,
    "confidence": 0.0-1.0
}""",
            user=f"Analyze:\n\n{prompt}",
            temperature=0.0,
        )

        return PolynomialStructure.parse(response)

    def analyze(self, results: list[PromptConvergence]) -> ConvergenceResult:
        """Analyze convergence results."""
        converged = [r for r in results if r.converged]
        has_poly = [r for r in converged if r.polynomial.is_polynomial]

        return ConvergenceResult(
            total_prompts=len(results),
            converged_count=len(converged),
            convergence_rate=len(converged) / len(results),
            mean_iterations=np.mean([r.iterations for r in converged]),
            polynomial_count=len(has_poly),
            polynomial_rate=len(has_poly) / len(converged) if converged else 0,
            success=len(converged) / len(results) > 0.9 and
                    len(has_poly) / len(converged) > 0.85 if converged else False,
        )
```

### 2.3 Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Convergence rate | > 90% | Most prompts should converge |
| Mean iterations | < 10 | Convergence should be fast |
| Polynomial rate | > 85% | Fixed points should be polynomial |

### 2.4 Timeline

- **Week 1**: Curate 100 diverse prompts
- **Week 2**: Implement convergence tracker
- **Week 3**: Execute experiments
- **Week 4**: Analysis and polynomial verification

---

## Experiment 3: Metric Comparison

### 3.1 Hypothesis

**H3**: Ensemble metrics outperform individual metrics for semantic distance.

### 3.2 Methodology

```python
@dataclass
class MetricComparisonExperiment:
    """
    Compare semantic distance metrics.

    Ground truth: Human similarity ratings (1-5 scale)
    """

    prompts: list[tuple[str, str]]  # 200 (original, reconstituted) pairs
    human_ratings: list[float]  # Human similarity ratings

    metrics = {
        "bertscore": lambda a, b: 1 - bert_score(a, b).F1,
        "cosine": lambda a, b: 1 - cosine_similarity(embed(a), embed(b)),
        "menli": lambda a, b: menli_contradiction(a, b),
        "bleu_inverse": lambda a, b: 1 - bleu_score(a, b),
        "llm_judge": lambda a, b: llm_rate_distance(a, b),
    }

    async def run(self) -> MetricAnalysis:
        metric_results = {}

        for name, metric_fn in self.metrics.items():
            scores = []
            times = []

            for orig, recon in self.prompts:
                start = time.time()
                score = await metric_fn(orig, recon) if asyncio.iscoroutinefunction(metric_fn) else metric_fn(orig, recon)
                elapsed = time.time() - start

                scores.append(score)
                times.append(elapsed)

            # Correlation with human ratings
            r, p = stats.pearsonr(scores, self.human_ratings)

            # Test-retest reliability (run twice, correlate)
            scores2 = [metric_fn(o, r) for o, r in self.prompts]
            icc = self._compute_icc(scores, scores2)

            metric_results[name] = MetricEvaluation(
                name=name,
                correlation=r,
                p_value=p,
                mean_time=np.mean(times),
                icc=icc,
            )

        # Ensemble analysis
        ensemble_weights = self._optimize_ensemble(metric_results)
        ensemble_scores = self._compute_ensemble(ensemble_weights)
        ensemble_r, _ = stats.pearsonr(ensemble_scores, self.human_ratings)

        return MetricAnalysis(
            individual_metrics=metric_results,
            ensemble_weights=ensemble_weights,
            ensemble_correlation=ensemble_r,
            recommended=self._select_best(metric_results, ensemble_r),
        )

    def _optimize_ensemble(
        self, metrics: dict[str, MetricEvaluation]
    ) -> dict[str, float]:
        """Find optimal weights via constrained optimization."""
        from scipy.optimize import minimize

        # Get all metric scores
        all_scores = {name: self._get_scores(name) for name in metrics}

        def loss(weights):
            ensemble = sum(
                w * np.array(all_scores[name])
                for name, w in zip(metrics.keys(), weights)
            )
            r, _ = stats.pearsonr(ensemble, self.human_ratings)
            return -r  # Minimize negative correlation

        n_metrics = len(metrics)
        result = minimize(
            loss,
            x0=[1/n_metrics] * n_metrics,
            constraints={"type": "eq", "fun": lambda w: sum(w) - 1},
            bounds=[(0, 1)] * n_metrics,
        )

        return dict(zip(metrics.keys(), result.x))
```

### 3.3 Success Criteria

| Metric | Threshold |
|--------|-----------|
| Best single metric r | > 0.85 |
| Ensemble r | > 0.90 |
| Mean computation time | < 100ms |
| Test-retest ICC | > 0.80 |

### 3.4 Timeline

- **Week 1**: Collect human ratings (crowdsource 200 pairs)
- **Week 2**: Implement metric suite
- **Week 3**: Execute comparisons
- **Week 4**: Optimize ensemble, report

---

## Experiment 4: Fusion Quality Study

### 4.1 Hypothesis

**H4**: Dialectical fusion produces better decisions than either Kent or Claude alone.

```
Quality(Fusion) > max(Quality(Kent), Quality(Claude))
```

**Theoretical Basis**: spec/principles/CONSTITUTION.md, Article VI

### 4.2 Methodology

```python
@dataclass
class FusionQualityExperiment:
    """
    Validate that fusion beats individual decisions.

    Data source: Historical architectural decisions from git
    """

    decisions: list[HistoricalDecision]  # 50 decisions from git history

    async def run(self) -> FusionAnalysis:
        results = []

        for decision in self.decisions:
            # Reconstruct what Kent would have decided alone
            kent_alone = await self.simulate_kent_alone(decision.context)

            # Reconstruct what Claude would have decided alone
            claude_alone = await self.simulate_claude_alone(decision.context)

            # Get the actual fusion result
            actual_fusion = decision.outcome

            # Evaluate each
            evaluator = DialecticalQualityEvaluator(llm=self.llm)

            kent_quality = await evaluator.evaluate_decision(kent_alone, decision.context)
            claude_quality = await evaluator.evaluate_decision(claude_alone, decision.context)
            fusion_quality = await evaluator.evaluate_decision(actual_fusion, decision.context)

            # Compute synergy
            synergy = fusion_quality.overall - max(
                kent_quality.overall, claude_quality.overall
            )

            results.append(DecisionComparison(
                decision_id=decision.id,
                kent_quality=kent_quality.overall,
                claude_quality=claude_quality.overall,
                fusion_quality=fusion_quality.overall,
                synergy=synergy,
                best_individual="kent" if kent_quality.overall > claude_quality.overall else "claude",
            ))

        return self.analyze(results)

    def analyze(self, results: list[DecisionComparison]) -> FusionAnalysis:
        synergies = [r.synergy for r in results]
        positive_synergy = [s for s in synergies if s > 0]

        return FusionAnalysis(
            total_decisions=len(results),
            positive_synergy_count=len(positive_synergy),
            positive_synergy_rate=len(positive_synergy) / len(results),
            mean_synergy=np.mean(synergies),
            median_synergy=np.median(synergies),

            # Breakdown by which individual was better
            kent_better_cases=[r for r in results if r.best_individual == "kent"],
            claude_better_cases=[r for r in results if r.best_individual == "claude"],

            success=len(positive_synergy) / len(results) > 0.6 and np.mean(synergies) > 0.05,
        )
```

### 4.3 Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Positive synergy rate | > 60% | Majority of decisions benefit |
| Mean synergy | > 0.05 | Average 5% improvement |
| No negative outliers | > -0.20 | Fusion shouldn't badly harm |

### 4.4 Timeline

- **Week 1**: Extract 50 decisions from git history
- **Week 2**: Implement simulation and evaluation
- **Week 3**: Execute comparisons
- **Week 4**: Analysis and Article VI validation

---

## Experiment 5: Operad Law Verification

### 5.1 Hypothesis

**H5**: Experience Quality composition laws hold empirically.

### 5.2 Methodology

```python
@dataclass
class OperadLawExperiment:
    """
    Empirically verify that operad composition laws hold.

    Laws to verify:
    1. Identity: Q >> Id = Q = Id >> Q
    2. Associativity: (A >> B) >> C ≈ A >> (B >> C)
    3. Commutativity (parallel): A || B = B || A
    4. Floor gate: F=0 => Q=0
    """

    experiences: list[Experience]  # 100 experiences

    async def run(self) -> LawVerificationResult:
        results = {}

        # Law 1: Identity
        identity_violations = []
        for exp in self.experiences:
            q = await measure_quality(exp)
            q_then_id = sequential_compose(q, quality_unit())
            id_then_q = sequential_compose(quality_unit(), q)

            left_error = abs(q.overall - q_then_id.overall)
            right_error = abs(q.overall - id_then_q.overall)

            if left_error > 0.01 or right_error > 0.01:
                identity_violations.append((exp.id, left_error, right_error))

        results["identity"] = LawResult(
            law="Identity: Q >> Id = Q = Id >> Q",
            violations=len(identity_violations),
            violation_rate=len(identity_violations) / len(self.experiences),
            max_error=max([max(l, r) for _, l, r in identity_violations], default=0),
            passed=len(identity_violations) == 0,
        )

        # Law 2: Associativity
        # Test on triplets of experiences
        assoc_violations = []
        for i in range(0, len(self.experiences) - 2, 3):
            a = await measure_quality(self.experiences[i])
            b = await measure_quality(self.experiences[i + 1])
            c = await measure_quality(self.experiences[i + 2])

            left = sequential_compose(sequential_compose(a, b), c)
            right = sequential_compose(a, sequential_compose(b, c))

            error = abs(left.overall - right.overall)
            if error > 0.05:  # Allow some tolerance
                assoc_violations.append((i, error))

        results["associativity"] = LawResult(
            law="Associativity: (A >> B) >> C ≈ A >> (B >> C)",
            violations=len(assoc_violations),
            violation_rate=len(assoc_violations) / (len(self.experiences) // 3),
            max_error=max([e for _, e in assoc_violations], default=0),
            passed=len(assoc_violations) / (len(self.experiences) // 3) < 0.05,
        )

        # Law 3: Commutativity (parallel)
        commut_violations = []
        for i in range(0, len(self.experiences) - 1, 2):
            a = await measure_quality(self.experiences[i])
            b = await measure_quality(self.experiences[i + 1])

            left = parallel_compose(a, b)
            right = parallel_compose(b, a)

            error = abs(left.overall - right.overall)
            if error > 0.001:  # Should be exact
                commut_violations.append((i, error))

        results["commutativity"] = LawResult(
            law="Commutativity: A || B = B || A",
            violations=len(commut_violations),
            violation_rate=len(commut_violations) / (len(self.experiences) // 2),
            max_error=max([e for _, e in commut_violations], default=0),
            passed=len(commut_violations) == 0,
        )

        # Law 4: Floor gate
        floor_violations = []
        for exp in self.experiences:
            q = await measure_quality(exp)
            if not q.floor_passed and q.overall != 0.0:
                floor_violations.append((exp.id, q.overall))

        results["floor_gate"] = LawResult(
            law="Floor gate: F=0 => Q=0",
            violations=len(floor_violations),
            violation_rate=len(floor_violations) / len(self.experiences),
            max_error=max([o for _, o in floor_violations], default=0),
            passed=len(floor_violations) == 0,
        )

        return LawVerificationResult(
            laws=results,
            all_passed=all(r.passed for r in results.values()),
        )
```

### 5.3 Success Criteria

| Law | Tolerance | Pass Criterion |
|-----|-----------|----------------|
| Identity | ε = 0.01 | 0 violations |
| Associativity | ε = 0.05 | < 5% violation rate |
| Commutativity | ε = 0.001 | 0 violations |
| Floor gate | exact | 0 violations |

---

## Summary: Experiment Schedule

| Week | Experiment | Status |
|------|------------|--------|
| 1-5 | Loss-Difficulty Correlation | Primary |
| 1-4 | Polynomial Emergence | Primary |
| 1-4 | Metric Comparison | Primary |
| 5-8 | Fusion Quality Study | Secondary |
| 5-8 | Operad Law Verification | Secondary |

**Total Timeline**: 8 weeks for complete validation suite.

---

*"Without data, you're just another person with an opinion." — W. Edwards Deming*
