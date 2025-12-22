# Agentic Self-Hosting Compiler (ASHC)

**Status:** Emerging Standard
**Implementation:** `impl/claude/protocols/ashc/`
**Tests:** 276 passing (Phase 1: L0 47, Phase 2: Evidence 103, Phase 2.5: Adaptive 32, Phase 2.75: Economy ~94)
**Heritage:** DSPy, SPEAR, TextGRAD, Chaos Engineering, Property-Based Testing, SPRT, BEACON

> *"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof."*

---

## Purpose

ASHC compiles Kent's creative ideas into agent executables **with evidence**.

The evidence is not formal proof. It is:
- **Traces from many runs** of similar ideas in similar scenarios
- **Chaos tests** with thousands of degrees of freedom
- **Verification with the same tools** we use to verify our work (pytest, mypy, linting)
- **Causal tracking** between prompt nudges and outcomes

**Why?** Because writing a good prompt is easy—one shot is often enough. What's hard is knowing whether the spec and implementation are *equivalent*. The compiler's job is to accumulate empirical evidence that demonstrates this equivalence.

```
ASHC : Spec → (Executable, Evidence)

Evidence = {
    traces: [Run₁, Run₂, ..., Runₙ],
    chaos_results: ChaosReport,
    verification: TestResults,
    causal_graph: PromptNudge → Outcome
}
```

---

## Core Insight

**The compiler is a trace accumulator, not a code generator.**

LLMs are "good enough" at: idea → prompt → implementation. That pipeline works. What's missing is **evidence that the implementation matches the spec**. If you grow the same "tree" many times over, making nudges and adjustments, you're digesting intuitive proof by tracking causality between prompts and outcomes.

ASHC makes this explicit:

```
Kent's Idea (Spec)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    ASHC COMPILER                          │
│                                                          │
│  1. Generate N variations of the idea                    │
│  2. Run each through LLM → Implementation                │
│  3. Verify each with tests, types, lints                 │
│  4. Chaos test: compose variations combinatorially       │
│  5. Track causal relationships: nudge → outcome          │
│  6. Accumulate into evidence corpus                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │
       ▼
Agent Executable + Evidence Corpus
```

The Evidence Corpus is the "proof"—not mathematical proof, but **empirical proof through repeated observation**.

---

## The Failure of Prompt Engineering

Evergreen Prompt System has 216 tests. It works. But it solved the wrong problem.

**Writing prompts is not hard.** A competent developer can write a good system prompt in one sitting. The machinery of SoftSection, TextGRAD, rollback—it's over-engineered for a problem that doesn't need engineering.

**What IS hard:**
- How do I know my agent will behave correctly in edge cases?
- How do I verify that my spec matches what the agent actually does?
- How do I build confidence that changes won't break things?

These are verification problems, not generation problems.

---

## Type Signatures

### The Evidence Corpus

```python
@dataclass(frozen=True)
class Run:
    """A single execution of spec → implementation."""
    spec_hash: str              # Content-addressed spec
    prompt_used: str            # The actual prompt
    implementation: str         # Generated code
    test_results: TestReport    # pytest output
    type_results: TypeReport    # mypy output
    lint_results: LintReport    # ruff/lint output
    timestamp: datetime
    duration_ms: int
    nudges: tuple[Nudge, ...]   # What was tweaked from baseline

@dataclass(frozen=True)
class Evidence:
    """Accumulated evidence for spec↔impl equivalence."""
    runs: tuple[Run, ...]
    chaos_report: ChaosReport
    causal_graph: CausalGraph
    confidence: float           # 0.0-1.0, based on runs

    def equivalence_score(self) -> float:
        """
        How confident are we that spec matches impl?

        Based on:
        - Pass rate across runs
        - Diversity of chaos tests
        - Stability under nudges
        """
        pass_rate = sum(r.test_results.passed for r in self.runs) / len(self.runs)
        chaos_score = self.chaos_report.stability_score
        nudge_stability = self.causal_graph.stability_score
        return (pass_rate * 0.4 + chaos_score * 0.3 + nudge_stability * 0.3)
```

### Chaos Testing

```python
@dataclass(frozen=True)
class ChaosConfig:
    """Configuration for chaos testing."""
    n_variations: int = 100         # How many trees to grow
    composition_depth: int = 3      # How deep to compose
    mutation_rate: float = 0.1      # How much to mutate each variation
    principles_to_vary: tuple[str, ...] = ()  # Which principles to test

@dataclass(frozen=True)
class ChaosReport:
    """Results of chaos testing."""
    variations_tested: int
    compositions_tested: int
    pass_rate: float
    failure_modes: tuple[FailureMode, ...]
    stability_score: float          # How stable under perturbation

    @property
    def categorical_complexity(self) -> int:
        """
        Degrees of freedom from composition.

        If we have N passes that can compose, complexity is O(N!).
        Chaos testing samples this exponential space.
        """
        return factorial(self.compositions_tested)
```

### Causal Tracking

```python
@dataclass(frozen=True)
class Nudge:
    """A single adjustment to the prompt/spec."""
    location: str               # Where in spec/prompt
    before: str                 # Original content
    after: str                  # Modified content
    reason: str                 # Why this nudge

@dataclass(frozen=True)
class CausalEdge:
    """A tracked relationship between nudge and outcome."""
    nudge: Nudge
    outcome_delta: float        # Change in test pass rate
    confidence: float           # How confident in this relationship
    runs_observed: int          # How many runs inform this edge

@dataclass(frozen=True)
class CausalGraph:
    """Graph of nudge → outcome relationships."""
    edges: tuple[CausalEdge, ...]

    def predict_outcome(self, proposed_nudge: Nudge) -> float:
        """Predict outcome of a new nudge based on history."""
        similar = [e for e in self.edges if similar_nudge(e.nudge, proposed_nudge)]
        if not similar:
            return 0.5  # No data, uncertain
        return weighted_average(e.outcome_delta for e in similar)

    @property
    def stability_score(self) -> float:
        """How stable are outcomes under small nudges?"""
        small_nudges = [e for e in self.edges if len(e.nudge.after) < 100]
        if not small_nudges:
            return 1.0
        variance = statistics.variance(e.outcome_delta for e in small_nudges)
        return 1.0 / (1.0 + variance)
```

### The Compiler Output

```python
@dataclass(frozen=True)
class ASHCOutput:
    """The compiler's output: executable + evidence."""
    executable: AgentExecutable     # The actual agent code
    evidence: Evidence              # Proof of equivalence
    spec_hash: str                  # Content-addressed spec

    @property
    def is_verified(self) -> bool:
        """Is there sufficient evidence for this executable?"""
        return (
            self.evidence.equivalence_score() >= 0.8 and
            len(self.evidence.runs) >= 10 and
            self.evidence.chaos_report.pass_rate >= 0.95
        )

ASHC: Spec → ASHCOutput
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ASHC COMPILER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. PARSE                                                                  │
│      Spec → SpecAST (content-addressed)                                     │
│                                                                             │
│   2. GENERATE (n times, with variations)                                    │
│      SpecAST → Prompt → LLM → Implementation                                │
│      Track: which nudges produced which implementations                     │
│                                                                             │
│   3. VERIFY (each implementation)                                           │
│      Implementation → pytest, mypy, ruff                                    │
│      Use SAME tools we use to verify our work                               │
│                                                                             │
│   4. CHAOS (combinatorial composition)                                      │
│      Compose implementations in all valid ways                              │
│      Degrees of freedom = O(n!) from categorical complexity                 │
│      Sample this space probabilistically                                    │
│                                                                             │
│   5. ACCUMULATE                                                             │
│      Runs → Evidence Corpus                                                 │
│      Build causal graph: nudge → outcome                                    │
│                                                                             │
│   6. EMIT                                                                   │
│      Best implementation + Evidence → ASHCOutput                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Verification Stack

We use **the same tools we use to verify our own work**:

| Tool | What It Checks | ASHC Role |
|------|----------------|-----------|
| `pytest` | Behavior correctness | Primary evidence source |
| `mypy` | Type consistency | Structural soundness |
| `ruff` | Style/patterns | Compliance with conventions |
| `hypothesis` | Property-based | Chaos test generation |
| `git diff` | Change tracking | Nudge detection |

The insight: if these tools are good enough for us to verify our work, they're good enough for ASHC to verify generated work.

---

## The Causal Learning Loop

```
                    ┌────────────────────┐
                    │   Kent's Nudge     │
                    │ "Make it tasteful" │
                    └─────────┬──────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      Generate N Variations    │
              │   (with and without nudge)    │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      Verify All Variations    │
              │   (pytest, mypy, ruff)        │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Compute Causal Effect       │
              │   Δ = outcome_with - without  │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Add to Causal Graph         │
              │   "tasteful" → +15% pass rate │
              └───────────────────────────────┘
```

Over time, the causal graph becomes a **learned prior** about which nudges matter and how. This is the "intuitive proof" Kent described—accumulated evidence about what works.

---

## Laws / Invariants

### Evidence Sufficiency

```
∀ ASHCOutput O:
  O.is_verified ⟹ len(O.evidence.runs) ≥ 10
                ∧ O.evidence.equivalence_score() ≥ 0.8
                ∧ O.evidence.chaos_report.pass_rate ≥ 0.95
```

No output is "verified" without sufficient evidence.

### Verification Consistency

```
∀ Run R:
  R.test_results = pytest(R.implementation)
  R.type_results = mypy(R.implementation)
  R.lint_results = ruff(R.implementation)
```

We use the same tools, deterministically.

### Causal Monotonicity

```
∀ CausalGraph G, Nudge n₁, n₂:
  similarity(n₁, n₂) > 0.9 ⟹ |G.predict(n₁) - G.predict(n₂)| < 0.1
```

Similar nudges should predict similar outcomes.

### Chaos Sampling

```
∀ ChaosConfig C:
  categorical_complexity(C) ≫ C.n_variations
  # We sample, not enumerate
```

The space is exponential; we sample probabilistically.

---

## Adaptive Bayesian Evidence (Phase 2.5)

> *"If something is 97% reliable, we don't need 100 runs. We need just enough runs until confidence crystallizes."*

### The Cost Problem

Running N variations is expensive. LLM calls cost money. If a task is trivially easy, running 100 variations is wasteful. If a task is hard and likely to fail, we should discover that quickly and stop.

**The insight:** Evidence gathering should be **adaptive**—stop when you have enough confidence, not when you hit a fixed N.

### The n_diff Technique

Inspired by sequential hypothesis testing (Wald's SPRT), we use a margin-of-victory stopping rule:

```
Stop when |successes - failures| ≥ n_diff
```

**Example with n_diff = 2:**
```
Run 1: FAIL   → S=0, F=1, margin=1 → continue
Run 2: PASS   → S=1, F=1, margin=0 → continue
Run 3: FAIL   → S=1, F=2, margin=1 → continue
Run 4: FAIL   → S=1, F=3, margin=2 → STOP (failure wins)
```

**Why this works:** If the true success rate is p, the expected samples to reach n_diff margin is:

```
E[T] ≈ n_diff / |2p - 1|
```

| True p | n_diff=2 | n_diff=3 |
|--------|----------|----------|
| 0.97   | 2.1      | 3.2      |
| 0.80   | 3.3      | 5.0      |
| 0.60   | 10.0     | 15.0     |
| 0.50   | ∞        | ∞        |

For highly reliable operations (p=0.97), we need only ~2 samples on average. For coin flips (p=0.50), we never converge—which is correct! If something is pure noise, we shouldn't pretend we have evidence.

### Beta-Binomial Bayesian Updating

We use the Beta distribution as a conjugate prior for binary outcomes:

```
Prior:     Beta(α, β)
Data:      s successes, f failures
Posterior: Beta(α + s, β + f)
```

**Confidence Tiers** set the prior:

| Tier | Prior | Mean | Interpretation |
|------|-------|------|----------------|
| TRIVIALLY_EASY | Beta(20, 1) | 0.95 | "Almost certainly works" |
| LIKELY_WORKS | Beta(8, 2) | 0.80 | "Probably works" |
| UNCERTAIN | Beta(1, 1) | 0.50 | "No idea" (uniform) |
| LIKELY_FAILS | Beta(2, 8) | 0.20 | "Probably broken" |

**Dual Stopping Conditions:**
1. **n_diff margin reached** — One outcome dominates
2. **Bayesian confidence ≥ 0.95** — P(p > 0.5) or P(p < 0.5) is high enough

### LLM Pre-Verification for Cheap Priors

Before running expensive verification (pytest/mypy/ruff), we can ask an LLM:

> "On a scale of TRIVIALLY_EASY to LIKELY_FAILS, how confident are you this code is correct?"

This is a **cheap prior**—it costs one lightweight LLM call instead of N full verification runs. If the LLM says TRIVIALLY_EASY, we set n_diff=1 and max_samples=3. If it says LIKELY_FAILS, we set n_diff=3 and max_samples=20.

```python
# LLM estimate → Prior → Stopping config
tier = await estimate_confidence(code)  # Cheap LLM call
prior = BetaPrior.from_confidence(tier)
config = StoppingConfig.for_tier(tier)
```

### Reliability Boost from Majority Voting

If a single LLM call has reliability p, majority voting over n calls boosts reliability:

```
P(majority correct) = Σ C(n,k) * p^k * (1-p)^(n-k)  for k > n/2
```

| Base p | n=3 | n=5 | n=7 |
|--------|-----|-----|-----|
| 0.80   | 0.90 | 0.94 | 0.97 |
| 0.70   | 0.78 | 0.84 | 0.87 |
| 0.60   | 0.65 | 0.68 | 0.71 |

**Implication:** If we need 97% reliability for deployment, and our LLM is 80% reliable on this task, we can achieve it with 7-vote majority. This is cheaper than hoping for a single perfect run.

### Type Signatures (Adaptive)

```python
class ConfidenceTier(Enum):
    TRIVIALLY_EASY = "trivially_easy"
    LIKELY_WORKS = "likely_works"
    UNCERTAIN = "uncertain"
    LIKELY_FAILS = "likely_fails"

@dataclass
class BetaPrior:
    alpha: float = 1.0  # Successes + 1
    beta: float = 1.0   # Failures + 1

    @classmethod
    def from_confidence(cls, tier: ConfidenceTier) -> "BetaPrior":
        """Map confidence tier to prior."""

    def update(self, successes: int, failures: int) -> "BetaPrior":
        """Bayesian update: posterior = Beta(α+s, β+f)."""
        return BetaPrior(self.alpha + successes, self.beta + failures)

    def prob_success_above(self, threshold: float) -> float:
        """P(p > threshold) under this Beta distribution."""

@dataclass(frozen=True)
class StoppingConfig:
    n_diff: int = 2                    # Margin of victory required
    max_samples: int = 20              # Hard cap on samples
    confidence_threshold: float = 0.95  # Bayesian confidence for early stop

@dataclass
class StoppingState:
    prior: BetaPrior
    config: StoppingConfig
    successes: int = 0
    failures: int = 0

    def observe(self, success: bool) -> StoppingDecision:
        """Update state and return stopping decision."""
        # Check n_diff margin
        # Check Bayesian confidence
        # Check max_samples

class AdaptiveCompiler:
    """Compile with adaptive stopping based on evidence accumulation."""

    async def compile(
        self,
        spec: str,
        tier: ConfidenceTier | None = None,
        prior: BetaPrior | None = None,
    ) -> AdaptiveEvidence:
        """
        Adaptive compilation:
        1. Set prior from tier or explicit
        2. Run until stopping condition
        3. Return evidence with confidence bounds
        """
```

### The Adaptive Law

```
∀ AdaptiveCompiler C, Spec S:
  C.compile(S) terminates ⟹
    (margin ≥ n_diff) ∨ (bayesian_confidence ≥ threshold) ∨ (samples = max)
```

We always terminate, and we always have a reason for terminating.

---

## The Bootstrap Agents as Test Fixtures

The 7 bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix) become **test fixtures** for ASHC:

```python
BOOTSTRAP_SPECS = [
    ("Id", "spec/bootstrap/id.md"),
    ("Compose", "spec/bootstrap/compose.md"),
    ("Judge", "spec/bootstrap/judge.md"),
    ("Ground", "spec/bootstrap/ground.md"),
    ("Contradict", "spec/bootstrap/contradict.md"),
    ("Sublate", "spec/bootstrap/sublate.md"),
    ("Fix", "spec/bootstrap/fix.md"),
]

async def test_bootstrap_regeneration():
    """
    ASHC must be able to regenerate bootstrap with evidence.

    This is the self-hosting test: can ASHC compile its own kernel?
    """
    for name, spec_path in BOOTSTRAP_SPECS:
        spec = read_spec(spec_path)
        output = await ashc.compile(spec, chaos_config=ChaosConfig(n_variations=100))

        assert output.is_verified, f"Insufficient evidence for {name}"
        assert output.evidence.equivalence_score() >= 0.9, f"Low confidence for {name}"

        # Compare to installed
        installed = get_installed_bootstrap(name)
        assert is_equivalent(output.executable, installed), f"{name} diverged"
```

---

## Human Flow (Kent-Centered)

1. **Kent writes spec** in natural language with creative intent
2. **ASHC runs N variations** generating implementations
3. **ASHC verifies each** with pytest, mypy, ruff
4. **ASHC chaos tests** composing implementations combinatorially
5. **ASHC accumulates evidence** into causal graph
6. **Kent reviews evidence**, not code
   - "95% pass rate across 100 variations"
   - "Stable under nudges: small changes don't break things"
   - "Causal insight: 'tasteful' correlates with +15% pass rate"
7. **Kent makes nudges** based on intuition + evidence
8. **Loop refines** until evidence is sufficient

The lived effect: Kent writes ideas, reviews evidence, makes nudges. The code is a byproduct.

---

## Integration

### AGENTESE Paths

```
concept.compiler.*
  .compile           # Spec → ASHCOutput (runs N variations)
  .evidence          # View evidence for a spec
  .causal            # View causal graph
  .chaos             # Run chaos tests

time.trace.*
  .runs              # List all runs for a spec
  .compare           # Compare runs (A/B testing)
  .replay            # Replay a specific run
```

### CLI

```bash
# Compile with evidence gathering
ashc compile spec/agents/new.md --variations=100 --chaos

# View evidence
ashc evidence spec/agents/new.md
# → 100 runs, 95% pass rate, equivalence score: 0.87

# View causal graph
ashc causal spec/agents/new.md
# → "composable" → +12% pass rate (high confidence)
# → "joy-inducing" → +5% pass rate (medium confidence)

# Run chaos tests
ashc chaos spec/agents/new.md --depth=3
# → Testing 1000 compositions...
# → Stability score: 0.92
```

---

## Anti-Patterns

- **One-shot compilation**: Running once and trusting the output. Evidence requires repetition.
- **Ignoring verification failures**: A failed test is data, not noise.
- **Manual code review**: The evidence corpus IS the review. Trust the process.
- **Formal proof obsession**: We're not doing Coq. We're doing science.
- **Prompt over-engineering**: Writing prompts is easy. Gathering evidence is hard.

---

## Implementation Reference

See: `impl/claude/protocols/ashc/`

**Phase 1: L0 Kernel** (47 tests)
- `primitives.py` — compose, apply, match, emit, witness
- `program.py` — Fluent L0Program builder
- `runtime.py` — L0Result execution
- `ast.py` — L0 AST types
- `patterns.py` — Pattern matching

**Phase 2: Evidence Engine** (103 tests)
- `evidence.py` — Run, Evidence, ASHCOutput, EvidenceCompiler
- `verify.py` — Integration with pytest/mypy/ruff

**Phase 2.5: Adaptive Bayesian** (32 tests)
- `adaptive.py` — BetaPrior, StoppingState, AdaptiveCompiler, n_diff technique

**Planned:**
- `chaos.py` — Chaos testing engine (Phase 3)
- `causal.py` — Causal graph learning (Phase 4)

Related specs:
- `spec/services/verification.md`
- `spec/bootstrap.md`
- `spec/principles.md`

---

*"If you grow the tree a thousand times, the pattern of growth IS the proof."*

*"We don't prove equivalence. We observe it."*
