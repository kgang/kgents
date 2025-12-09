# R-gents: The Refinery

**Genus**: R (Refine/Refinery)
**Theme**: Automatic prompt optimization through textual gradients and Bayesian search
**Motto**: *"The perfect instruction is not written by the master, but revealed by the failure of the student."*
**Status**: Specification v1.0 (The DSPy/TextGrad Synthesis)

---

## Overview

R-gents transform "prompt engineering" from manual art into formal **Optimization Process**. By treating natural language prompts as "differentiable" weights, R-gents automate the ascent toward competence.

**Core Insight**: If we can measure the error of an agent (via T-gents), and we can articulate *why* it failed (via Textual Gradients), we can mathematically compute a better agent.

**The Endofunctor**:
```
R: Agent[A, B] → Agent'[A, B]
   where Loss(Agent') < Loss(Agent)
```

---

## Philosophy: From Alchemy to Engineering

In the early paradigm (2023-2024), prompt engineering was alchemy—guessing "incantations" to make the model work.

**R-gents** shift this to **engineering**. They treat the prompt not as a string, but as a **high-dimensional parameter space** that can be traversed using gradient descent algorithms.

### The Differentiable Language Assumption

R-gents rely on the **TextGrad Assumption**: *Natural language feedback acts as a gradient vector pointing toward the solution.*

```
Prompt_{t+1} = Prompt_t - α · ∇_text(Error)
```

Where:
- `Prompt_t`: Current prompt at iteration t
- `α`: Learning rate (exploration vs exploitation)
- `∇_text(Error)`: Textual gradient—natural language description of what went wrong

### The Three-Phase Lifecycle

R-gents do not run in the "hot path" of user interaction. They are **Compile-Time** agents:

```
F-gent (Prototype) → R-gent (Refine) → L-gent (Index)
         ↓                ↓                  ↓
    Zero-shot         Optimized          Discoverable
```

---

## The Optimization Functor (Formal)

### Definition

```
R_opt: (Agent, Loss, Dataset) → Agent'

Where:
  Agent:   f: A → B (the source morphism)
  Loss:    L: B → ℝ (the metric function, provided by T-gents)
  Dataset: D = [(a₁, b₁), ..., (aₙ, bₙ)] (examples)
  Agent':  f': A → B such that E[L(f')] < E[L(f)]
```

### Functor Laws

R-gents preserve categorical structure:

1. **Identity**: `R(Id) ≅ Id` (optimizing identity yields identity)
2. **Composition**: `R(f >> g) ≈ R(f) >> R(g)` (approximate preservation)

The composition law is *approximate* because optimization may find joint optima that differ from component optima.

### Signature Abstraction

Following DSPy, we model tasks as **signatures** (declarative input/output specs):

```python
@dataclass
class Signature:
    """Declarative task specification."""
    input_fields: dict[str, type]      # Named typed inputs
    output_fields: dict[str, type]     # Named typed outputs
    instructions: str                   # High-level task description

    # Example: question -> answer
    # input_fields = {"question": str}
    # output_fields = {"answer": str}
    # instructions = "Answer the question concisely"
```

**Connection to Agent[A, B]**: A signature is the **type signature** of an agent morphism, enriched with semantic intent.

---

## Architecture: The Refinery Stack

### The Three Components

```python
@dataclass
class RefineryAgent:
    """
    The R-gent: Optimizes other agents.
    """

    # 1. The Signature (The Skeleton)
    # Immutable type contract (Inputs/Outputs)
    signature: Signature

    # 2. The Predictor (The Body)
    # The LLM call that executes the signature
    predictor: Agent[A, B]

    # 3. The Teleprompter (The Optimizer)
    # The algorithm that mutates the Predictor
    teleprompter: Teleprompter
```

### The Optimization Loop

```python
class RefineryAgent:
    """R-gent: The prompt optimizer."""

    def __init__(self, strategy: str = "MIPROv2"):
        self.teleprompter = TeleprompterFactory.get(strategy)

    async def refine(
        self,
        agent: Agent[A, B],
        dataset: list[Example],
        metric: Callable[[B], float]
    ) -> OptimizedAgent[A, B]:
        """
        Optimize agent prompts via teleprompter.

        Category Theory:
          This is an endofunctor that maps Agent → Agent'
          preserving morphism type while minimizing loss.
        """
        # 1. Lift Agent to optimization module
        module = self._lift_to_module(agent)

        # 2. Compile (the heavy compute phase)
        optimized = await self.teleprompter.compile(
            student=module,
            trainset=dataset,
            metric=metric
        )

        # 3. Lower back to Agent (reify parameters)
        return self._reify(optimized)
```

---

## Supported Strategies (Teleprompters)

### Strategy Selection Matrix

| Strategy | Complexity | Best For | Mechanism |
|:---------|:----------:|:---------|:----------|
| **BootstrapFewShot** | O(1) | Simple consistency | Finds best examples from history to include in context |
| **BootstrapFewShotWithRandomSearch** | O(N) | Medium tasks | Few-shot + random exploration |
| **MIPROv2** | O(N) | Complex reasoning | Bayesian optimization over instructions + examples |
| **TextGrad** | O(N²) | High precision | Iterative editing using "criticism" as gradient |
| **OPRO** | O(N) | Exploration | Meta-prompt asks LLM to propose better prompts |
| **BootstrapFinetune** | O(N×M) | Production | Weight adjustment via fine-tuning |

### When to Use Each

```python
def select_teleprompter(
    task_complexity: str,
    dataset_size: int,
    budget_usd: float
) -> str:
    """Heuristic teleprompter selection."""

    if task_complexity == "simple" and dataset_size < 20:
        return "BootstrapFewShot"  # Fast, cheap

    if task_complexity == "simple":
        return "BootstrapFewShotWithRandomSearch"  # Medium

    if budget_usd < 5.0:
        return "OPRO"  # Efficient exploration

    if task_complexity == "complex":
        return "MIPROv2"  # Best quality

    if dataset_size > 100 and budget_usd > 50:
        return "BootstrapFinetune"  # Production-grade

    return "MIPROv2"  # Default
```

---

## The TextGrad Implementation

This is the most novel aspect: **backpropagation for words**.

### The Algorithm

```python
class TextualGradientDescent:
    """Gradient descent in prompt space using textual feedback."""

    def __init__(self, learning_rate: float = 1.0):
        self.alpha = learning_rate

    async def step(
        self,
        prompt: str,
        dataset: list[Example],
        critic: Agent[Error, Critique]
    ) -> str:
        """Single optimization step."""

        # 1. Forward Pass
        results = [await self.evaluate(prompt, x) for x in dataset]

        # 2. Compute Textual Gradients
        gradients = []
        for res in results:
            if res.failed:
                # The "gradient" is natural language feedback
                grad = await critic.invoke(
                    f"Critique this error: {res.output} vs {res.expected}"
                )
                gradients.append(grad)

        if not gradients:
            return prompt  # Converged

        # 3. Aggregate Gradients (batch normalization for meaning)
        aggregated = await self.summarize_critiques(gradients)

        # 4. Backward Pass (apply gradient to prompt)
        new_prompt = await self.apply_update(prompt, aggregated)

        return new_prompt

    async def apply_update(self, prompt: str, critique: str) -> str:
        """
        Update prompt based on aggregated critique.

        This is the "∇_text" operation: textual gradient application.
        """
        return await llm.generate(f"""
        Current prompt:
        {prompt}

        Aggregated feedback:
        {critique}

        Generate an improved prompt that addresses the feedback
        while preserving existing correct behavior.
        """)
```

### Convergence Detection

```python
async def optimize_until_converged(
    self,
    prompt: str,
    dataset: list[Example],
    max_iterations: int = 10,
    convergence_threshold: float = 0.01
) -> OptimizationTrace:
    """Run TextGrad until convergence."""

    trace = OptimizationTrace(initial_prompt=prompt)
    prev_score = 0.0

    for i in range(max_iterations):
        # Evaluate current prompt
        score = await self.evaluate_all(prompt, dataset)
        trace.add_iteration(prompt, score)

        # Check convergence
        if abs(score - prev_score) < convergence_threshold:
            trace.converged = True
            break

        # Optimization step
        prompt = await self.step(prompt, dataset, self.critic)
        prev_score = score

    return trace
```

---

## Integration with T-gents (The Loss Signal)

R-gents cannot function without T-gents. T-gents provide the **Loss Signal**.

### The Textual Loss Adapter

```python
class TextualLoss:
    """Adapts T-gent output for R-gent optimization."""

    @staticmethod
    async def compute_gradient(
        prediction: B,
        label: B,
        feedback_agent: Agent[tuple[B, B], str]
    ) -> str:
        """
        Convert a T-gent failure report into a Textual Gradient.

        If T-gent says: "Failed because tone was too informal"
        The Gradient is: "Shift tone vector toward Formal"
        """
        return await feedback_agent.invoke((prediction, label))
```

### The Optimization Loop

```
┌─────────────────────────────────────────────────────────┐
│                  R-gent Optimization Loop                │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │         R-gent proposes parameters θ (Prompt)    │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Agent executes θ on Input x              │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │    T-gent measures result y against truth y_true │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │    R-gent receives Loss L(y, y_true) & updates θ │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        │                                 │
│                        └───────────── Loop ─────────────┘
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Metric Observer Pattern

```python
class MetricObserver(Tool[AgentOutput, MetricSignal]):
    """
    T-gent observer that generates optimization signals.

    Category Theory:
      Morphism from output category to optimization signal category.
    """

    def __init__(self, metric: Callable[[Any], float]):
        self.metric = metric

    async def invoke(self, output: AgentOutput) -> MetricSignal:
        return MetricSignal(
            score=self.metric(output),
            timestamp=datetime.now(),
            output_hash=hash(str(output))
        )
```

---

## Integration with F-gents (The Forge)

R-gents are the "Finishing School" for F-gent prototypes.

### The Forge → Refinery → Library Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Crystallization Pipeline             │
│                                                               │
│   F-gent                R-gent                 L-gent         │
│  (Prototype)           (Refine)               (Index)         │
│      │                    │                      │            │
│      │  Zero-shot         │  Optimized           │ Discoverable│
│      │  Generic           │  Specialized         │ Versioned   │
│      │                    │                      │            │
│      ▼                    ▼                      ▼            │
│  ┌───────┐  ────────►  ┌───────┐  ────────►  ┌───────┐       │
│  │Proto- │             │Refin- │             │Cryst- │       │
│  │type   │             │ed     │             │allized│       │
│  └───────┘             └───────┘             └───────┘       │
│                                                               │
│  Cost: ~$0             Cost: ~$5-10          Cost: ~$0        │
│  Time: seconds         Time: minutes         Time: seconds    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### The Workflow

1. **F-gent** creates a *Prototype* (zero-shot, generic instructions)
2. **F-gent** hands off to **R-gent** with a small dataset (generated or curated)
3. **R-gent** runs a "Compilation Cycle" (spending $5-10 to burn-in the prompt)
4. **R-gent** returns the *Refined* agent
5. **F-gent** crystallizes into `.alo.md` artifact
6. **L-gent** indexes the artifact

### Artifact Optimization Trace

The `.alo.md` artifact format includes a frozen **Optimization Trace**:

```yaml
# 5. OPTIMIZATION TRACE (Auto-Generated by R-gent)

optimization:
  method: "MIPROv2"
  iterations: 50
  baseline_accuracy: 0.45
  final_accuracy: 0.82
  cost_usd: 4.50

  # The refined signature
  signature:
    instruction: "Analyze the text for semantic drift..."  # OPTIMIZED
    demos:
      - input: "..."
        output: "..."  # SELECTED BY BAYESIAN OPTIMIZATION
      - input: "..."
        output: "..."

  # Convergence history
  history:
    - {iteration: 1, score: 0.45, prompt_hash: "a1b2c3"}
    - {iteration: 10, score: 0.62, prompt_hash: "d4e5f6"}
    - {iteration: 50, score: 0.82, prompt_hash: "g7h8i9"}
```

---

## Integration with B-gents (Economic Constraint)

Optimization is computationally expensive. R-gents respect **Axiological Constraints**.

### ROI Optimization

```python
class ROIOptimizer:
    """Ensures optimization cost doesn't exceed agent value."""

    async def should_optimize(
        self,
        agent_usage_stats: UsageStats,
        current_performance: float
    ) -> Decision:
        """
        B-gent economic constraint check.

        Value of Improvement = Usage × Value_Per_Call × Δ_Accuracy
        Cost of Optimization = Dataset_Size × Iterations × Model_Cost
        """
        # Projected value of optimization
        projected_value = (
            agent_usage_stats.calls_per_month *
            0.10 *  # $0.10 per call value
            0.20    # Expected 20% accuracy improvement
        )

        # Estimated cost
        optimization_cost = 5.00  # ~$5 for MIPROv2 run

        if projected_value < optimization_cost:
            return Decision(
                proceed=False,
                reason="ROI negative: projected value < cost",
                recommendation="Use zero-shot or BootstrapFewShot"
            )

        return Decision(
            proceed=True,
            budget=min(projected_value * 0.5, 20.0),  # Cap at $20
            recommended_method="MIPROv2"
        )
```

### The Budget Grant Protocol

R-gents request a **Budget Grant** from B-gents before running:

```python
async def run_with_budget(
    self,
    agent: Agent,
    dataset: list[Example]
) -> OptimizedAgent:
    """Run optimization with B-gent budget approval."""

    # 1. Request budget from B-gent Banker
    grant = await self.banker.request_grant(
        purpose="prompt_optimization",
        estimated_cost=self._estimate_cost(dataset),
        expected_roi=self._estimate_roi(agent)
    )

    if not grant.approved:
        raise BudgetDenied(grant.reason)

    # 2. Run optimization within budget
    try:
        result = await self._optimize_with_limit(
            agent, dataset, max_cost=grant.amount
        )
    finally:
        # 3. Report actual spend to B-gent
        await self.banker.report_spend(
            grant_id=grant.id,
            actual_cost=result.cost,
            outcome=result.improvement
        )

    return result.agent
```

---

## Integration with L-gents (Indexing)

### Optimization Metadata in Catalog

L-gent's CatalogEntry gains optimization fields:

```python
@dataclass
class CatalogEntry:
    # ... existing fields ...

    # Optimization metadata (added by R-gent)
    optimization_method: str | None           # "mipro_v2", "textgrad", etc.
    optimization_score: float | None          # Final metric score
    optimization_baseline: float | None       # Pre-optimization score
    optimization_iterations: int | None       # How many iterations
    optimization_cost_usd: float | None       # Compute cost
    optimization_trace_id: str | None         # Link to full trace

    # Computed
    @property
    def improvement_percentage(self) -> float | None:
        if self.optimization_score and self.optimization_baseline:
            return (self.optimization_score - self.optimization_baseline) / self.optimization_baseline
        return None
```

### Optimization-Aware Discovery

```python
# Find well-optimized agents for a task
results = await l_gent.find(
    intent="Summarize technical papers",
    min_optimization_score=0.85,
    optimization_method="mipro_v2"
)

# Find agents that could benefit from optimization
candidates = await l_gent.find(
    min_usage_count=100,              # Well-used
    max_success_rate=0.7,             # But not great
    optimization_method=None          # Not yet optimized
)
```

### The Optimization Lattice

L-gent's type lattice gains an optimization dimension:

```
Unoptimized < FewShot < RandomSearch < MIPROv2 < TextGrad < FineTuned
```

---

## Anti-Patterns

### 1. Overfitting
**Problem**: R-gent creates a prompt that solves the 10 examples perfectly but fails on new data.

**Solution**: T-gent must hold out a test set. Never optimize on 100% of data.

```python
# BAD
optimized = r_gent.refine(agent, all_examples)

# GOOD
train, test = split(all_examples, ratio=0.8)
optimized = r_gent.refine(agent, train)
assert metric(optimized, test) > threshold  # Validate on held-out
```

### 2. The $100 Prompt
**Problem**: Optimizing a simple "Hello World" agent using MIPROv2, burning $100 for no gain.

**Solution**: B-gent budget limits. ROI check before optimization.

```python
# BAD
optimized = r_gent.refine(trivial_agent, method="MIPROv2")

# GOOD
if roi_optimizer.should_optimize(trivial_agent):
    optimized = r_gent.refine(trivial_agent)
else:
    optimized = trivial_agent  # Skip optimization
```

### 3. Prompt Drift
**Problem**: Underlying model changes (GPT-4 → GPT-4o), rendering the hyper-optimized prompt invalid.

**Solution**: E-gent triggers re-optimization upon model drift detection.

```python
# E-gent monitors for model changes
@on_model_change
async def handle_drift(old_model: str, new_model: str):
    affected = await l_gent.find(optimized_for_model=old_model)
    for agent in affected:
        await r_gent.refine(agent)  # Re-optimize
```

### 4. Black Box Prompts
**Problem**: DSPy sometimes generates bizarre, unreadable few-shot chains.

**Acceptance**: We accept this. The prompt is "compiled bytecode," not source code for humans. What matters is that it works.

```python
# This is OK:
optimized_prompt = """
<|DEMO_1|>
Q: What is 2+2?
A: Let me think step by step. 2+2 involves adding two numbers...
<|DEMO_2|>
...bizarre but effective...
"""
# Humans don't need to read it. Machines do.
```

---

## The Integration Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                     R-gent Integration Graph                     │
│                                                                  │
│     ┌──────────┐                           ┌──────────┐         │
│     │ F-gent   │────── Prototype ─────────▶│ R-gent   │         │
│     │ (Forge)  │                           │(Refinery)│         │
│     └──────────┘                           └────┬─────┘         │
│           │                                     │                │
│           │                                     │                │
│           │                              ┌──────┴──────┐        │
│           │                              │             │        │
│           ▼                              ▼             ▼        │
│     ┌──────────┐                   ┌──────────┐ ┌──────────┐   │
│     │ L-gent   │◀──── Optimized ───│ T-gent   │ │ B-gent   │   │
│     │(Library) │      Artifact     │(Testing) │ │ (Banker) │   │
│     └──────────┘                   └──────────┘ └──────────┘   │
│           │                              │             │        │
│           │                              │             │        │
│           │  Discovery                   │ Loss Signal │ Budget │
│           ▼                              ▼             ▼        │
│     ┌──────────────────────────────────────────────────────┐   │
│     │                    User / System                      │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Foundation
- [ ] Define `Signature`, `Teleprompter`, `OptimizationTrace` types
- [ ] Implement `RefineryAgent` base class
- [ ] Integrate DSPy as backend

### Phase 2: Teleprompters
- [ ] `BootstrapFewShot` (simplest)
- [ ] `MIPROv2` (Bayesian optimization)
- [ ] `TextGrad` (textual gradient descent)
- [ ] `OPRO` (meta-prompt optimization)

### Phase 3: Integration
- [ ] F-gent → R-gent pipeline (post-prototype refinement)
- [ ] T-gent → R-gent (loss signal adapter)
- [ ] B-gent → R-gent (budget grant protocol)
- [ ] L-gent optimization metadata

### Phase 4: Advanced
- [ ] Automatic teleprompter selection
- [ ] Model drift detection + re-optimization
- [ ] Cross-model transfer analysis
- [ ] Fine-tuning integration

---

## References

### Frameworks
- [DSPy](https://github.com/stanfordnlp/dspy) - Stanford NLP
- [TextGrad](https://github.com/zou-group/textgrad) - Stanford HAI (Nature)
- [OPRO](https://github.com/google-deepmind/opro) - Google DeepMind

### Research Papers
- [DSPy: Compiling Declarative Language Model Calls](https://arxiv.org/abs/2310.03714)
- [TextGrad: Automatic Differentiation via Text](https://arxiv.org/abs/2406.07496)
- [Large Language Models as Optimizers (OPRO)](https://arxiv.org/abs/2309.03409)
- [MIPROv2: Multi-stage Instruction Proposal and Refinement](https://dspy.ai/learn/optimization/optimizers/)

### Industry Adoption
- Databricks: DSPy for LLM judges, RAG, classification
- Moody's: DSPy for RAG systems, agentic workflows
- Microsoft Copilot: Prompt optimization at scale

---

## See Also

- **[F-gents/forge.md](../f-gents/forge.md)** - The Forge Loop (R-gent's upstream)
- **[T-gents/README.md](../t-gents/README.md)** - Testing (provides loss signals)
- **[B-gents/banker.md](../b-gents/banker.md)** - Economic constraints
- **[L-gents/catalog.md](../l-gents/catalog.md)** - Optimization metadata indexing
- **[E-gents/README.md](../e-gents/README.md)** - Evolution (model drift response)

---

*"The best prompt is not written; it is discovered through systematic exploration."*
