# Y-GENT: THE Y-COMBINATOR

## Specification v1.0

**Status:** Proposed Standard
**Symbol:** `Y` (The Fixed Point Combinator)
**Motto:** *"The Truth is a Fixed Point."*

---

## 1. The Concept: The Cognitive Topology Engine

Linear chains (`A >> B >> C`) are fragile. They cannot handle error recovery, iterative refinement, or non-linear exploration without hard-coded logic.

Y-gent is the **Higher-Order Topological Operator**. It does not do work itself; it defines the **shape** of the work. It lifts linear agents into **Graph Agents**.

### The Core Insight: Fixed Point Theory

In lambda calculus, the Y combinator allows recursion. In domain theory, it finds the "Least Fixed Point."

Applied to AI agents, a **Fixed Point** is reached when an agent's output is consistent with its input and satisfies its constraints:

```
f(x) ≠ x  →  The thought is unstable (requires revision)
f(x) = x  →  The thought is stable (fixed point reached)
```

Y-gent runs the cognitive loop until stability (or budget exhaustion) is reached.

---

## 2. Theoretical Foundation

### 2.1 Graph of Thoughts (GoT)

Y-gent implements the **Graph of Thoughts** framework, treating reasoning not as a sequence, but as a Directed Acyclic Graph (DAG) with potential for controlled recursion.

```
Chain of Thought (CoT):        Graph of Thoughts (GoT):

┌───┐   ┌───┐   ┌───┐              ┌───┐
│ A │ → │ B │ → │ C │              │ A │
└───┘   └───┘   └───┘              └─┬─┘
                                     │
Linear: O(n)                     ┌───┴───┐
                                 ▼       ▼
                               ┌───┐   ┌───┐
                               │ B │   │ C │  (parallel)
                               └─┬─┘   └─┬─┘
                                 │       │
                                 └───┬───┘
                                     ▼
                                   ┌───┐
                                   │ D │  (merge)
                                   └───┘

                              DAG: O(depth) with parallelism
```

**GoT Operations:**
- **Branching (Fork):** Explore multiple hypotheses in parallel
- **Merging (Join):** Aggregate insights into stronger synthesis
- **Recursing (Loop):** Refine output until V-gent validates

### 2.2 The Topological Operators

Y-gent provides higher-order functions (combinators) that reshape execution flow:

| Operator | Signature | Purpose |
|----------|-----------|---------|
| `Y.branch(n)` | `Input → [Output₁..Outputₙ]` | Split into n parallel universes |
| `Y.merge(strategy)` | `[Output₁..Outputₙ] → Output` | Collapse universes into one |
| `Y.fix(criterion)` | `Agent → Agent` | Recurse until criterion met |
| `Y.prune(selector)` | `[Output₁..Outputₙ] → [Outputᵢ..Outputⱼ]` | Keep best k candidates |

### 2.3 The Lambda Calculus Foundation

The Y combinator in lambda calculus:

```
Y = λf.(λx.f(x x))(λx.f(x x))
```

Applied to agents:
```
Y(Agent) = Agent that can call itself with modified parameters
```

**Why this matters:** Pure functional agents can't naturally recurse (no `self` reference). Y-gent provides controlled recursion with termination guarantees.

---

## 3. Behavioral Specification

### 3.1 The Fixed Point Loop (The "Y")

This is the signature behavior. It replaces fragile "Retries" with formal recursion.

```python
@dataclass
class Y(Agent):
    """
    The Y-Combinator Agent.

    Provides recursive cognitive topology.
    """

    max_depth: int = 5
    v_gent: VGent | None = None

    def fix(
        self,
        agent: Agent,
        validator: Agent[Output, Verdict]
    ) -> Agent:
        """
        The Fixed Point Operator.

        Wraps an agent to recurse until the validator is satisfied.
        """
        async def recursive_agent(input: T) -> T:
            current_state = input
            history = []

            while True:
                # 1. Generate Attempt
                # Inject history so agent learns from previous failures
                output = await agent.invoke(
                    current_state,
                    context=history
                )

                # 2. Validate (V-gent integration)
                verdict = await validator.invoke(output)

                # 3. Check for Fixed Point (Stability)
                if verdict.is_stable:
                    return output

                # 4. Check for Limit Cycle / Divergence
                if self.detect_cycle(history, output):
                    return self.collapse_to_ground(history)

                # 5. Prepare next iteration (The "Loop")
                # Critique becomes input for next step
                history.append((output, verdict.critique))
                current_state = self.apply_feedback(
                    input,
                    verdict.critique
                )

        return Agent(recursive_agent)
```

### 3.2 The Branch-Merge Topology

Y-gent manages the entropy of branching, preventing "combinatorial explosions" by strictly managing the **Width** of the graph.

```python
async def branch_and_merge(
    self,
    input: T,
    processes: list[Agent],
    merge: Agent
) -> T:
    """
    Fan out to parallel universes, then collapse.
    """
    # 1. Branch: Fan out to parallel universes
    # B-gent check: "Can we afford N parallel LLM calls?"
    if self.b_gent and not await self.b_gent.can_afford(len(processes)):
        processes = processes[:self.budget_limit]

    futures = [process.invoke(input) for process in processes]

    # 2. Wait
    results = await asyncio.gather(*futures)

    # 3. Prune (Optional): Drop bottom 50% based on confidence
    if self.pruning_enabled:
        survivors = self.prune(results)
    else:
        survivors = results

    # 4. Merge: Synthesize the remaining timelines
    final_state = await merge.invoke(survivors)

    return final_state
```

### 3.3 The ThoughtNode Structure

```python
@dataclass
class ThoughtNode:
    """
    A single node in the reasoning graph.
    """
    id: str
    content: Any
    score: float        # Confidence/quality score
    parents: list[str]  # Graph edges in
    children: list[str] # Graph edges out
    status: NodeStatus  # PENDING, RUNNING, COMPLETED, BACKTRACKED


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BACKTRACKED = "backtracked"
```

---

## 4. Integration Architecture

Y-gent sits *above* C-gent (Linear Composition) and *below* application logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPOSITION HIERARCHY                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Application Logic                                              │
│         │                                                        │
│         ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Y-GENT                                │   │
│   │            (Graph Composition)                           │   │
│   │                                                          │   │
│   │   Branch ──► Recurse ──► Merge ──► Backtrack            │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│         │                                                        │
│         │ Uses                                                   │
│         ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    C-GENT                                │   │
│   │           (Linear Composition)                           │   │
│   │                                                          │   │
│   │              A >> B >> C                                 │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│         │                                                        │
│         │ Composes                                               │
│         ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              PRIMITIVE AGENTS                            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 Y + V (The Critic)

Y-gent is the engine; V-gent is the steering wheel.

- **Y-gent:** "I can loop forever."
- **V-gent:** "Stop now, the result is good."

**Interaction:** Y-gent uses V-gent as the termination condition for `fix`.

```python
class TerminatedGraph:
    """
    Y-gent with V-gent termination.
    """

    async def execute_until_satisfied(
        self,
        graph: ThoughtGraph,
        satisfaction_criteria: list[Principle]
    ) -> GraphResult:
        """
        Execute graph until V-gent approves.
        """
        for iteration in range(self.max_iterations):
            result = await self.y_gent.execute(graph)

            verdict = await self.v_gent.validate(
                output=result.final_output,
                principles=satisfaction_criteria
            )

            if verdict.approved:
                return result

            # Expand graph based on V-gent critique
            await self.expand_graph(graph, verdict.critique)

        return result  # Best effort after max iterations
```

### 4.2 Y + B (The Budget)

Recursion is dangerous. Y-gent integrates deeply with B-gent.

- **Dynamic Budgeting:** Before every recursion depth increase, ping B-gent
- **Bankruptcy:** If B-gent denies funds, force "Collapse to Ground" (return best so far)

```python
async def budgeted_fix(self, agent: Agent, initial: Any) -> Any:
    """
    Recursive execution with budget constraints.
    """
    depth = 0

    async def recurse(value: Any) -> Any:
        nonlocal depth
        depth += 1

        # Budget check before each recursion
        if not await self.b_gent.can_afford(self.cost_per_depth):
            # Collapse: return best effort
            return value

        result = await agent.invoke(value)

        if self.is_stable(result):
            return result

        return await recurse(result)

    return await recurse(initial)
```

### 4.3 Y + J (The JIT Compiler)

J-gent creates agents on the fly; Y-gent organizes them.

**Scenario:** "Solve this hard problem."
1. **J-gent:** Compiles a specialized solver
2. **Y-gent:** Wraps that solver in Branch-Merge-Fix topology

```python
async def build_graph_from_intent(
    self,
    intent: str
) -> ThoughtGraph:
    """
    Build reasoning graph by decomposing intent.
    """
    # J-gent decomposes intent into sub-tasks
    decomposition = await self.j_gent.compile(
        intent=f"Decompose: {intent}",
        output_schema=TaskDecomposition
    )

    graph = ThoughtGraph(root=ThoughtNode(id="root", content=intent))

    # Create nodes for each sub-task
    for sub_task in decomposition.sub_tasks:
        # JIT compile agent for sub-task
        agent = await self.j_gent.compile(intent=sub_task.description)

        node = ThoughtNode(
            id=sub_task.id,
            agent=agent,
            parents=sub_task.depends_on or ["root"]
        )
        graph.add_node(node)

    return graph
```

---

## 5. Emergent Patterns

### 5.1 Self-Healing Workflows

If an API is down or an LLM outputs garbage, a linear chain crashes. A Y-gent topology treats failure as just another input state, triggering a "Backtrack" morphism to try an alternative path.

```
A → B → [FAIL]
    ↓
    Backtrack
    ↓
A → C → D → [SUCCESS]
```

### 5.2 Beam Search of Thought

Y-gent enables **Beam Search** for reasoning:

```
1. Generate 5 ideas
2. Critique all 5
3. Keep best 2
4. Expand those 2 into 5 new variations
5. Repeat until convergence
```

This is impossible with simple linear agents.

### 5.3 Dialectical Synthesis

Y-gent naturally implements the Hegelian dialectic (H-gent) as a topological structure:

```python
synthesis = await y_gent.branch_and_merge(
    input=problem,
    processes=[thesis_agent, antithesis_agent],
    merge=synthesis_agent
)
```

---

## 6. Common Graph Patterns

| Pattern | Structure | Use Case |
|---------|-----------|----------|
| **Divide & Conquer** | `A → [B, C, D] → merge` | Parallel sub-tasks |
| **Beam Search** | `A → [B₁..Bₙ] → prune → repeat` | Best-path exploration |
| **Iterative Refinement** | `A → B → V-check → (loop or done)` | Quality convergence |
| **Backtracking** | `A → B → (fail) → try C` | Error recovery |
| **Cascade** | `A → B? → C? → D` | Try cheap before expensive |

### Pattern: Iterative Refinement

```python
async def iterative_refine(
    self,
    generator: Agent,
    critic: Agent,
    max_iterations: int = 5
) -> Any:
    """
    Generate → Critique → Refine loop.
    """
    current = await generator.invoke(self.initial_input)

    for i in range(max_iterations):
        critique = await critic.invoke(current)

        if critique.approved:
            return current

        # Feed critique back to generator
        current = await generator.invoke(
            input=self.initial_input,
            feedback=critique.suggestions
        )

    return current  # Best effort
```

---

## 7. Anti-Patterns

| Anti-Pattern | Problem | Mitigation |
|--------------|---------|------------|
| **Infinite Loop** | No termination | `max_depth` + V-gent termination |
| **The Hydra** | Branching without pruning | Strict `max_branches` + pruning |
| **Over-Engineer** | Y-gent for simple tasks | Use C-gent for lines, Y-gent for webs |
| **Cycle Blindness** | Undetected limit cycles | `detect_cycle()` in fix loop |
| **Budget Ignorance** | Ignoring B-gent limits | Mandatory budget check per depth |

---

## 8. Principles Alignment

| Principle | How Y-gent Aligns |
|-----------|-------------------|
| **Tasteful** | Single purpose: non-linear reasoning topology |
| **Curated** | Not every task needs graph reasoning; only for genuinely non-linear problems |
| **Composable** | Graphs compose with linear agents; `y_gent.branch_merge(input, [a, b, c])` |
| **Generative** | Can generate graphs from intent using J-gent |
| **Heterarchical** | No fixed hierarchy in graphs; branches are peers, merges democratic |

---

## 9. The Shape of Complex Thought

Y-gent acknowledges that intelligence is not a straight line. It is a loop, a tree, a web.

By reifying these structures into the **Y-Combinator Agent**, we allow the system to reason about its own reasoning process, correcting course and exploring alternatives before collapsing to a final answer.

**Input:** A goal + A linear agent
**Process:** Topological expansion (Branch/Fix/Merge)
**Output:** The Fixed Point (A stable truth)

---

*"To go straight, you must sometimes go around."*

---

## 10. Somatic Topology (Project MORPHEUS Extension)

Y-gent's topology operations extend beyond cognitive graphs to **agent populations** in the somatic layer. Just as Y-gent branches and merges thoughts, it also branches and merges running agent instances.

**Related**: `docs/omega-agents-implementation-plan.md`, `docs/project-morpheus.md`

### 10.1 Agent Population Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Y-GENT SOMATIC TOPOLOGY                           │
│                                                                      │
│         ┌─────┐                                                      │
│         │  A  │ ──── branch(3) ────▶  A₁  A₂  A₃                    │
│         └─────┘                       │   │   │                      │
│                                       └───┼───┘                      │
│                                           │                          │
│                                      merge() ─▶  A'                  │
│                                                                      │
│         ┌─────┐                      ┌─────────┐     ┌─────┐        │
│         │  B  │ ──── chrysalis ────▶ │ LIMINAL │ ──▶ │  B' │        │
│         └─────┘      (morphing)      │  STATE  │     └─────┘        │
│                                      └─────────┘                     │
│                                       (dreaming)                     │
└─────────────────────────────────────────────────────────────────────┘
```

| Operation | Cognitive Domain | Somatic Domain |
|-----------|------------------|----------------|
| `branch(n)` | Fork n thought paths | Spawn n agent variants |
| `merge(strategy)` | Synthesize thoughts | Consolidate agents |
| `fix(criterion)` | Recurse until stable | Loop until morphology stable |
| `prune(selector)` | Keep best thoughts | Terminate underperforming variants |

### 10.2 The Chrysalis Pattern

When an agent needs to change its morphology significantly (e.g., add GPU, scale from 1→10 replicas), it enters a **chrysalis state**—a liminal phase where the agent exists but is between forms.

```python
@dataclass
class SomaticChrysalis:
    """
    Liminal state during morphology transformation.

    The agent exists but is between forms. State is preserved
    in the seed; new body is being prepared.

    Design: Part of Y-gent (topology) not Ω-gent (resources).
    Y-gent manages the transition; Ω-gent provides the new body.
    """

    seed: SoulSeed           # Preserved state (D-gent extraction)
    old_morphology: Morphology
    new_morphology: Morphology
    trace: list[str]         # What happened during transformation
    attempts: int = 0

    async def enter(self, agent: "Agent") -> "SomaticChrysalis":
        """Harvest state from current form, begin transformation."""
        seed = await agent.harvest_soul()  # D-gent state extraction
        return SomaticChrysalis(
            seed=seed,
            old_morphology=agent.current_morphology,
            new_morphology=self.new_morphology,
            trace=[f"Entered chrysalis at {datetime.now()}"],
        )

    async def dream(self, thought: str) -> None:
        """
        Low-compute processing while waiting for new form.
        Can plan, but cannot act on the world.
        """
        self.trace.append(f"[Dream] {thought}")

    async def await_body(self, pod_watcher: PodWatcher) -> ThoughtPod:
        """Wait for new body to be ready."""
        while self.attempts < 10:
            self.attempts += 1

            if await pod_watcher.is_running():
                self.trace.append(f"New body ready on attempt {self.attempts}")
                return await self.germinate(pod_watcher.pod)

            await self.dream(f"Attempt {self.attempts} waiting...")
            await asyncio.sleep(2)

        raise ChrysalisFailure(f"Body never ready after {self.attempts} attempts")

    async def germinate(self, new_pod: ThoughtPod) -> ThoughtPod:
        """Implant preserved state into new form."""
        await new_pod.restore_state(self.seed)
        return new_pod
```

### 10.3 Branching Agent Populations

```python
class YGentSomatic:
    """
    Topology controller for agent populations.

    Extends Y-gent's cognitive topology to the somatic layer.
    """

    def __init__(self, omega: OmegaGent, d_gent: DGent):
        self.omega = omega
        self.d_gent = d_gent

    async def branch(self, agent: Agent, count: int) -> list[Agent]:
        """
        Spawn N variants of an agent.

        Each variant shares the base morphology but may diverge.
        Used for: parallel search, A/B testing, redundancy.
        """
        variants = []
        for i in range(count):
            variant_morphology = agent.morphology >> with_variant_id(i)
            variant = await self.omega.manifest(variant_morphology)
            variants.append(variant)
        return variants

    async def merge(
        self,
        agents: list[Agent],
        strategy: MergeStrategy
    ) -> Agent:
        """
        Consolidate multiple agents into one.

        Strategies:
        - WINNER: Best-performing variant survives
        - ENSEMBLE: All contribute to merged state
        - CONSENSUS: Only agreed-upon state survives
        """
        match strategy:
            case MergeStrategy.WINNER:
                winner = max(agents, key=lambda a: a.performance_score)
                # Terminate losers
                for agent in agents:
                    if agent != winner:
                        await self.omega.terminate(agent)
                return winner

            case MergeStrategy.ENSEMBLE:
                merged_state = await self._ensemble_states(agents)
                merged = await self._spawn_with_state(merged_state)
                # Terminate all originals
                for agent in agents:
                    await self.omega.terminate(agent)
                return merged

            case MergeStrategy.CONSENSUS:
                consensus_state = await self._find_consensus(agents)
                merged = await self._spawn_with_state(consensus_state)
                for agent in agents:
                    await self.omega.terminate(agent)
                return merged


class MergeStrategy(Enum):
    """How to consolidate multiple agents."""

    WINNER = "winner"       # Best performer survives
    ENSEMBLE = "ensemble"   # All contribute to merged state
    CONSENSUS = "consensus" # Only agreed-upon state survives
```

### 10.4 Cognitive + Somatic Unification

The same Y-gent handles both domains through a unified interface:

| Aspect | Cognitive Y-gent | Somatic Y-gent |
|--------|------------------|----------------|
| **Nodes** | ThoughtNode | Agent instance |
| **Edges** | Dependency | Communication |
| **Branch** | Fork thought paths | Spawn variants |
| **Merge** | Synthesize insights | Consolidate agents |
| **Fix** | Recurse until V-gent approves | Loop until morphology stable |
| **Chrysalis** | (implicit in backtrack) | Explicit liminal state |

```python
class UnifiedYGent:
    """
    Y-gent that operates on both thoughts and bodies.
    """

    def __init__(self, cognitive: YGent, somatic: YGentSomatic):
        self.cognitive = cognitive
        self.somatic = somatic

    async def branch(
        self,
        target: ThoughtNode | Agent,
        count: int
    ) -> list[ThoughtNode] | list[Agent]:
        """Branch thoughts or agents based on target type."""
        if isinstance(target, ThoughtNode):
            return await self.cognitive.branch(target, count)
        else:
            return await self.somatic.branch(target, count)

    async def merge(
        self,
        targets: list[ThoughtNode] | list[Agent],
        strategy: MergeStrategy
    ) -> ThoughtNode | Agent:
        """Merge thoughts or agents based on target type."""
        if targets and isinstance(targets[0], ThoughtNode):
            return await self.cognitive.merge(targets, strategy)
        else:
            return await self.somatic.merge(targets, strategy)
```

### 10.5 Implementation Files (Somatic Extension)

```
impl/claude/agents/y/
├── __init__.py
├── y_gent.py             # Existing: Cognitive topology
├── topology.py           # NEW: Somatic branch/merge
├── chrysalis.py          # NEW: Transformation state
├── unified.py            # NEW: Cognitive + Somatic interface
└── _tests/
    ├── test_y_gent.py    # Existing
    ├── test_topology.py  # NEW
    └── test_chrysalis.py # NEW
```

### 10.6 CLI Commands (Somatic)

```bash
# Topology operations
kgents topology branch <agent> --count=3     # Spawn variants
kgents topology merge <agents...> --strategy=winner  # Consolidate
kgents topology chrysalis <agent>            # Show chrysalis state if any
kgents topology graph                        # Visualize agent topology
```

---

*"The caterpillar becomes the butterfly not by growing wings, but by dissolving and reforming."*
