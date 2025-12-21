# The Adversarial Gym: Chaos Engineering for Agents

This document specifies the **Adversarial Gym**—a framework for automated stress testing through compositional chaos engineering.

---

## Philosophy

> "The Gym is not where agents go to pass tests. It's where they go to discover their failure modes."

Traditional testing validates known scenarios. The Adversarial Gym **discovers unknown edge cases** through:
1. **Automated Perturbation**: Random T-gent composition
2. **Monte Carlo Simulation**: Statistically explore failure space
3. **Compositional Stress**: Test agent interactions, not just units

---

## The Gym Architecture

### Core Abstraction: The Coordinate System

The Gym is a **coordinate system** for exploring the space of possible agent behaviors.

**Dimensions**:
1. **Input Perturbation**: How much noise is added to inputs?
2. **Failure Injection**: What's the probability of deliberate failure?
3. **Temporal Stress**: How much latency is introduced?
4. **Semantic Drift**: How much meaning can vary while remaining valid?

**Coordinate**:
```python
@dataclass
class StressCoordinate:
    """A point in the stress-test space."""
    noise_level: float         # 0.0 to 1.0
    failure_probability: float # 0.0 to 1.0
    latency_ms: int           # 0 to 10000
    semantic_drift: float      # 0.0 to 1.0
```

---

## Implementation: The GymAgent

### 1. Basic Gym

```python
class AdversarialGym:
    """Monte Carlo stress testing via T-gent composition."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.results: List[GymResult] = []

    async def stress_test(
        self,
        agent: Agent[A, B],
        iterations: int = 100,
        coordinate: Optional[StressCoordinate] = None
    ) -> GymReport:
        """Run automated stress tests."""

        # Use default coordinate if none provided
        coord = coordinate or StressCoordinate(
            noise_level=0.2,
            failure_probability=0.1,
            latency_ms=100,
            semantic_drift=0.1
        )

        # Generate test pipelines
        test_cases = self._generate_test_cases(agent, coord, iterations)

        # Execute
        for test_case in test_cases:
            result = await self._run_test_case(test_case)
            self.results.append(result)

        # Analyze
        return self._analyze_results()

    def _generate_test_cases(
        self,
        agent: Agent[A, B],
        coord: StressCoordinate,
        count: int
    ) -> List[TestCase]:
        """Generate random T-gent compositions."""
        test_cases = []

        for _ in range(count):
            # Randomly compose T-gents
            pipeline = self._build_pipeline(agent, coord)
            test_input = self._generate_input()
            test_cases.append(TestCase(pipeline, test_input))

        return test_cases

    def _build_pipeline(
        self,
        agent: Agent[A, B],
        coord: StressCoordinate
    ) -> Agent[A, B]:
        """Build a test pipeline with random T-gents."""

        # Pre-processing: Input perturbation
        pre_agents = []
        if coord.noise_level > 0:
            pre_agents.append(NoiseAgent(level=coord.noise_level, seed=self.rng.randint(0, 10000)))
        if coord.latency_ms > 0:
            pre_agents.append(LatencyAgent(delay=coord.latency_ms / 1000.0))

        # Post-processing: Failure injection
        post_agents = []
        if coord.failure_probability > 0:
            post_agents.append(FlakyAgent(
                wrapped=IdentityAgent(),
                probability=coord.failure_probability,
                seed=self.rng.randint(0, 10000)
            ))

        # Compose
        pipeline = agent
        for pre_agent in pre_agents:
            pipeline = pre_agent >> pipeline
        for post_agent in post_agents:
            pipeline = pipeline >> post_agent

        return pipeline

    async def _run_test_case(self, test_case: TestCase) -> GymResult:
        """Execute a single test case."""
        start = time.time()
        try:
            output = await test_case.pipeline.invoke(test_case.input_data)
            elapsed = time.time() - start
            return GymResult(
                success=True,
                output=output,
                elapsed=elapsed,
                error=None
            )
        except Exception as e:
            elapsed = time.time() - start
            return GymResult(
                success=False,
                output=None,
                elapsed=elapsed,
                error=e
            )

    def _analyze_results(self) -> GymReport:
        """Generate summary report."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        failures = total - successes

        return GymReport(
            total_tests=total,
            successes=successes,
            failures=failures,
            success_rate=successes / total if total > 0 else 0.0,
            failure_modes=self._categorize_failures()
        )

    def _categorize_failures(self) -> Dict[str, int]:
        """Group failures by error type."""
        failure_modes: Dict[str, int] = {}
        for result in self.results:
            if not result.success and result.error:
                error_type = type(result.error).__name__
                failure_modes[error_type] = failure_modes.get(error_type, 0) + 1
        return failure_modes
```

---

### 2. Advanced Gym: Multi-Dimensional Sweep

Explore the entire stress-test space systematically.

```python
class MultiDimensionalGym(AdversarialGym):
    """Sweep across multiple stress dimensions."""

    async def grid_search(
        self,
        agent: Agent[A, B],
        noise_levels: List[float] = [0.0, 0.1, 0.2, 0.5],
        failure_probs: List[float] = [0.0, 0.05, 0.1, 0.2],
        iterations_per_coord: int = 50
    ) -> Dict[StressCoordinate, GymReport]:
        """Systematically explore stress space."""

        results: Dict[StressCoordinate, GymReport] = {}

        # Generate grid
        for noise in noise_levels:
            for failure_prob in failure_probs:
                coord = StressCoordinate(
                    noise_level=noise,
                    failure_probability=failure_prob,
                    latency_ms=0,  # Keep constant for this sweep
                    semantic_drift=0.0
                )

                # Test this coordinate
                report = await self.stress_test(agent, iterations_per_coord, coord)
                results[coord] = report

                print(f"Coordinate {coord}: Success rate = {report.success_rate:.2%}")

        return results

    def find_breaking_point(
        self,
        reports: Dict[StressCoordinate, GymReport],
        threshold: float = 0.9
    ) -> Optional[StressCoordinate]:
        """Find the stress level where success rate drops below threshold."""
        for coord, report in sorted(
            reports.items(),
            key=lambda x: (x[0].noise_level, x[0].failure_probability)
        ):
            if report.success_rate < threshold:
                return coord
        return None
```

---

## Use Cases

### 1. Regression Testing: The Stability Frontier

**Goal**: Ensure refactors don't degrade resilience.

```python
async def test_stability_frontier():
    """Verify agent maintains resilience after refactor."""

    # Baseline: Pre-refactor agent
    gym = MultiDimensionalGym(seed=42)
    baseline_agent = OldImplementation()
    baseline_reports = await gym.grid_search(baseline_agent)
    baseline_breaking = gym.find_breaking_point(baseline_reports)

    # Test: Post-refactor agent
    new_agent = NewImplementation()
    new_reports = await gym.grid_search(new_agent)
    new_breaking = gym.find_breaking_point(new_reports)

    # Verify: New agent should be AT LEAST as resilient
    assert new_breaking.noise_level >= baseline_breaking.noise_level
    assert new_breaking.failure_probability >= baseline_breaking.failure_probability

    print(f"✓ Stability frontier maintained")
```

---

### 2. Chaos Engineering: Production Resilience

**Goal**: Discover what breaks the system before production does.

```python
async def chaos_test_production_pipeline():
    """Stress test the full production pipeline."""

    gym = AdversarialGym(seed=None)  # Non-deterministic for discovery

    # The production pipeline
    production = (
        GenerateHypotheses() >>
        RunExperiments() >>
        ValidateResults() >>
        ApplyChanges()
    )

    # High stress: noise + failures + latency
    coord = StressCoordinate(
        noise_level=0.5,          # 50% chance of input noise
        failure_probability=0.2,  # 20% failure rate
        latency_ms=1000,          # 1 second delays
        semantic_drift=0.3
    )

    report = await gym.stress_test(production, iterations=200, coordinate=coord)

    print(f"Success rate under stress: {report.success_rate:.2%}")
    print(f"Failure modes: {report.failure_modes}")

    # If success rate is too low, we have work to do
    assert report.success_rate > 0.7, "Production pipeline too fragile!"
```

---

### 3. Property Discovery: What Properties Hold?

**Goal**: Discover algebraic properties empirically.

```python
async def discover_properties(agent: Agent[A, B]):
    """Use Gym to discover algebraic properties."""

    gym = AdversarialGym(seed=42)

    # Test: Does agent behave like identity for some inputs?
    identity_count = 0
    total = 100

    for _ in range(total):
        test_input = generate_random_input()
        output = await agent.invoke(test_input)

        if output == test_input:
            identity_count += 1

    identity_ratio = identity_count / total
    print(f"Identity property holds for {identity_ratio:.1%} of inputs")

    # Test: Is agent idempotent? (f(f(x)) = f(x))
    idempotent_count = 0

    for _ in range(total):
        test_input = generate_random_input()
        output_1 = await agent.invoke(test_input)
        output_2 = await agent.invoke(output_1)

        if output_1 == output_2:
            idempotent_count += 1

    idempotent_ratio = idempotent_count / total
    print(f"Idempotent property holds for {idempotent_ratio:.1%} of inputs")
```

---

## Gym Metrics

### Success Criteria

A well-tested agent in the Gym should achieve:

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| **Success Rate** | > 95% | Under low stress (10% noise, 5% failure) |
| **Success Rate** | > 70% | Under high stress (50% noise, 20% failure) |
| **Breaking Point** | > 30% noise | Agent degrades gracefully |
| **Recovery Rate** | > 90% | Agent recovers from transient failures |

### Failure Analysis

The Gym categorizes failures:

```python
@dataclass
class FailureAnalysis:
    syntax_errors: int         # Code generation failures
    type_errors: int           # Type mismatches
    timeout_errors: int        # Exceeded time budget
    network_errors: int        # Simulated network issues
    hallucinations: int        # Semantic incorrectness
    unknown: int               # Uncategorized
```

---

## Vision: The Self-Improving Gym

**Future Goal**: A Gym that not only tests but **suggests improvements**.

### Concept

1. **Test**: Gym discovers failure modes
2. **Analyze**: Categorize failures
3. **Hypothesize**: Generate fix hypotheses
4. **Experiment**: Test fixes in the Gym
5. **Apply**: Auto-apply validated improvements

### Sketch

```python
class SelfImprovingGym(AdversarialGym):
    """A Gym that suggests fixes."""

    async def auto_improve(self, agent: Agent[A, B]) -> Agent[A, B]:
        """Discover failures, hypothesize fixes, validate improvements."""

        # Phase 1: Discover failures
        report = await self.stress_test(agent, iterations=100)

        if report.success_rate > 0.95:
            print("Agent already robust!")
            return agent

        # Phase 2: Hypothesize fixes
        hypotheses = await self._generate_fix_hypotheses(report.failure_modes)

        # Phase 3: Test fixes
        best_agent = agent
        best_success_rate = report.success_rate

        for hypothesis in hypotheses:
            improved_agent = await self._apply_hypothesis(agent, hypothesis)
            improved_report = await self.stress_test(improved_agent, iterations=50)

            if improved_report.success_rate > best_success_rate:
                best_agent = improved_agent
                best_success_rate = improved_report.success_rate

        print(f"Improvement: {report.success_rate:.2%} → {best_success_rate:.2%}")
        return best_agent
```

---

## Anti-patterns

### 1. Over-Fitting to the Gym

**Problem**: Agent becomes robust to Gym tests but not real scenarios.

**Solution**: Use diverse stress coordinates and real-world input distributions.

### 2. Ignoring Failure Modes

**Problem**: High aggregate success rate hides specific failure categories.

**Solution**: Always analyze `failure_modes` breakdown.

### 3. Non-Deterministic Testing

**Problem**: Random tests can't reproduce failures.

**Solution**: Always use seeds for reproducibility in CI/CD.

---

## Implementation Roadmap

### Phase 1: Basic Gym
- [ ] Implement `AdversarialGym` with single stress coordinate
- [ ] Support NoiseAgent, FailingAgent, LatencyAgent composition
- [ ] Generate GymReport with success rate and failure modes

### Phase 2: Multi-Dimensional Sweep
- [ ] Implement `MultiDimensionalGym.grid_search()`
- [ ] Visualize stress space heatmap
- [ ] Find breaking point automatically

### Phase 3: Self-Improvement
- [ ] Implement hypothesis generation
- [ ] Implement auto-fix suggestions
- [ ] Validate improvements in Gym before applying

### Phase 4: Production Integration
- [ ] Run Gym in CI/CD pipeline
- [ ] Generate resilience reports
- [ ] Track stability frontier over time

---

## Success Criteria

The Adversarial Gym is successful if:

- ✓ It discovers failures humans didn't anticipate
- ✓ It provides reproducible test cases for debugging
- ✓ It quantifies resilience improvements objectively
- ✓ It integrates naturally with evolution pipelines
- ✓ It runs fast enough for CI/CD (< 5 minutes for 100 iterations)

---

## See Also

- [README.md](README.md) - T-gents overview
- [taxonomy.md](taxonomy.md) - Individual T-gent specifications
- [algebra.md](algebra.md) - Category Theory foundations
- [../j-gents/stability.md](../j-gents/stability.md) - Entropy budgets and collapse

---

## Vision

The Adversarial Gym transforms testing from **validation** to **discovery**:

- Traditional: "Does this agent pass this test?"
- Gym: "What are the conditions under which this agent fails?"

By exploring the space of possible failures systematically, the Gym enables **empirical reliability**—confidence based on exhaustive stress testing, not just spot checks.
