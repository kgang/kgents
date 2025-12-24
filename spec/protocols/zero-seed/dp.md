# Zero Seed: DP-Native Integration

> *"The value IS the agent. The trace IS the proof."*

**Module**: DP-Native Integration
**Depends on**: [`core.md`](./core.md), [`proof.md`](./proof.md)

---

## Purpose

This module reveals that Zero Seed's seven-layer structure **IS** a dynamic programming formulation. This is not an analogy—it's an isomorphism.

The DP-Native framework (`spec/theory/dp-native-kgents.md`) shows that:
- Every kgents domain is an MDP (Markov Decision Process)
- Constitutional principles are reward functions
- Toulmin proofs are policy traces
- The telescope is a discount factor

---

## The Agent-DP Isomorphism

### Zero Seed as MDP

```python
ZeroSeedMDP = MDP(
    S = {ZeroNode instances},            # State space
    A = {EdgeKind operations},            # Action space
    T = traverse_edge,                     # Transition function
    R = constitution.reward,               # Constitutional reward
    γ = focal_distance,                    # Discount factor
)
```

| MDP Component | Zero Seed Mapping | Description |
|---------------|-------------------|-------------|
| State `S` | `ZeroNode` | Current node in graph |
| Action `A` | `EdgeKind` | Edge creation/traversal |
| Transition `T` | `traverse_edge(s, a)` | Follow edge to new node |
| Reward `R` | `Constitution.reward(s, a, s')` | 7-principle weighted sum |
| Discount `γ` | `focal_distance` | 0.0=myopic, 1.0=far-sighted |

### The Bellman Equation

Navigating the seven-layer holarchy follows the Bellman equation:

```python
def bellman_value(node: ZeroNode, graph: ZeroGraph, constitution: Constitution) -> float:
    """
    V*(node) = max_edge [
        Constitution.reward(node, edge, target) +
        γ · V*(target)
    ]
    """
    if node.layer == 7:
        # Terminal state
        return constitution.reward(None, "terminal", node).total

    max_value = float('-inf')
    gamma = graph.telescope_state.focal_distance

    for edge in graph.edges_from(node.id):
        target = graph.get_node(edge.target)
        immediate_reward = constitution.reward(node, edge.kind.value, target).total
        future_value = bellman_value(target, graph, constitution)
        value = immediate_reward + gamma * future_value
        max_value = max(max_value, value)

    return max_value
```

### Discount Factor Semantics

The discount factor γ maps directly to telescope focal distance:

| γ Value | Focal Distance | Behavior |
|---------|----------------|----------|
| 0.0 - 0.2 | Micro | Myopic: only immediate reward matters |
| 0.2 - 0.5 | Meso | Balanced: some future consideration |
| 0.5 - 0.8 | Macro | Far-sighted: future rewards weighted heavily |
| 0.8 - 1.0 | Orbital | Infinite horizon: full trajectory consideration |

```python
@property
def gamma(self) -> float:
    """Discount factor from telescope state."""
    return self.telescope_state.focal_distance
```

---

## Toulmin Proof as PolicyTrace

The DP PolicyTrace and Toulmin Proof are isomorphic:

| PolicyTrace | Toulmin Proof | Zero Seed |
|-------------|---------------|-----------|
| `state_before` | `data` | Source node |
| `action` | `warrant` | Edge kind |
| `state_after` | `claim` | Target node |
| `value` | `qualifier` | Confidence |
| `rationale` | `backing` | Context |
| `log` | `rebuttals` | Contradiction edges |

### Proof ↔ Trace Conversion

```python
def proof_to_trace(proof: Proof, source: ZeroNode, target: ZeroNode) -> PolicyTrace[NodeId]:
    """Convert Toulmin proof to DP trace."""
    entry = TraceEntry(
        state_before=source.id,
        action=proof.warrant,  # Warrant IS the action justification
        state_after=target.id,
        value=qualifier_to_value(proof.qualifier),
        rationale=proof.backing,
    )
    return PolicyTrace.pure(target.id).with_entry(entry)


def trace_to_proof(trace: PolicyTrace[NodeId], graph: ZeroGraph) -> Proof:
    """Convert DP trace to Toulmin proof."""
    entries = trace.log

    if not entries:
        return Proof(
            data="Empty trace",
            warrant="No actions taken",
            claim="Identity",
            qualifier="unknown",
            backing="",
            tier=EvidenceTier.CATEGORICAL,
            principles=(),
            rebuttals=(),
        )

    return Proof(
        data=str(entries[0].state_before),
        warrant=" → ".join(e.action for e in entries),
        claim=str(entries[-1].state_after),
        qualifier=value_to_qualifier(trace.total_value()),
        backing="; ".join(e.rationale for e in entries if e.rationale),
        tier=EvidenceTier.CATEGORICAL,
        principles=(),
        rebuttals=extract_rebuttals_from_trace(trace, graph),
    )


def qualifier_to_value(qualifier: str) -> float:
    """Map qualifier to numeric value."""
    return {
        "definitely": 1.0,
        "probably": 0.8,
        "possibly": 0.5,
        "uncertain": 0.3,
        "unknown": 0.1,
    }.get(qualifier, 0.5)


def value_to_qualifier(value: float) -> str:
    """Map numeric value to qualifier."""
    if value >= 0.95:
        return "definitely"
    elif value >= 0.70:
        return "probably"
    elif value >= 0.40:
        return "possibly"
    elif value >= 0.10:
        return "uncertain"
    else:
        return "unknown"
```

---

## Constitution as Seven-Principle Reward

The Constitutional reward function evaluates every transition:

```python
class ZeroSeedConstitution(Constitution):
    """Constitutional reward for Zero Seed operations."""

    def __init__(self):
        super().__init__()

        # Principle evaluators for Zero Seed domain
        self.set_evaluator(
            Principle.TASTEFUL,
            lambda s, a, ns: self._tasteful_score(s, a, ns),
            lambda s, a, ns: "Concise, justified nodes are tasteful"
        )

        self.set_evaluator(
            Principle.CURATED,
            lambda s, a, ns: self._curated_score(s, a, ns),
            lambda s, a, ns: "Intentional selection over accumulation"
        )

        self.set_evaluator(
            Principle.ETHICAL,
            lambda s, a, ns: self._ethical_score(s, a, ns),
            lambda s, a, ns: "Axioms cannot be superseded without Mirror Test"
        )

        self.set_evaluator(
            Principle.JOY_INDUCING,
            lambda s, a, ns: self._joy_score(s, a, ns),
            lambda s, a, ns: "Delightful interactions"
        )

        self.set_evaluator(
            Principle.COMPOSABLE,
            lambda s, a, ns: self._composable_score(s, a, ns),
            lambda s, a, ns: "Edges follow layer ordering"
        )

        self.set_evaluator(
            Principle.HETERARCHICAL,
            lambda s, a, ns: self._heterarchical_score(s, a, ns),
            lambda s, a, ns: "Flux between layers"
        )

        self.set_evaluator(
            Principle.GENERATIVE,
            lambda s, a, ns: self._generative_score(s, a, ns),
            lambda s, a, ns: "Node derives from axioms"
        )

    def _tasteful_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Tasteful: concise, clear purpose."""
        if ns.content is None:
            return 0.5
        # Prefer concise content
        length_score = min(1.0, 500 / max(len(ns.content), 1))
        # Prefer nodes with clear titles
        title_score = 1.0 if ns.title and len(ns.title) < 50 else 0.7
        return (length_score + title_score) / 2

    def _curated_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Curated: intentional, not accumulated."""
        # Higher score for nodes with proofs (intentional)
        if ns.proof:
            return 0.9
        # Axioms are curated by definition
        if ns.layer <= 2:
            return 1.0
        return 0.6

    def _ethical_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Ethical: preserve human agency."""
        # Superseding axioms is low-ethical unless Mirror Test
        if a == "supersedes" and s and s.layer <= 2:
            return 0.1  # Very low score
        # Contradicting is fine (dialectical)
        if a == "contradicts":
            return 0.8
        return 1.0

    def _composable_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Composable: edges follow layer ordering."""
        if s is None:
            return 0.5
        # Inter-layer edges should follow DAG order
        LAYER_EDGES = {
            1: ["grounds"],
            2: ["justifies"],
            3: ["specifies"],
            4: ["implements"],
            5: ["reflects_on"],
            6: ["represents"],
        }
        expected = LAYER_EDGES.get(s.layer, [])
        if a in expected:
            return 1.0
        elif a in ["derives_from", "extends", "refines"]:
            return 0.9  # Intra-layer is fine
        elif a in ["contradicts", "synthesizes"]:
            return 0.8  # Dialectical is fine
        else:
            return 0.5  # Layer skip

    def _generative_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Generative: derives from axioms."""
        # More ancestors = more grounded
        return min(1.0, len(ns.lineage) / 3)

    def _heterarchical_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Heterarchical: flux between layers."""
        # Nodes accessible from multiple layers are more heterarchical
        return 0.8  # Default; actual computation requires graph context

    def _joy_score(self, s: ZeroNode | None, a: str, ns: ZeroNode) -> float:
        """Joy-inducing: delight in interaction."""
        # Nodes with personality indicators
        if any(tag in ns.tags for tag in ["playful", "creative", "bold"]):
            return 1.0
        return 0.7


# Usage
zero_constitution = ZeroSeedConstitution()
reward = zero_constitution.reward(source_node, edge_kind, target_node)
```

---

## Axiom Discovery as MetaDP

The three-stage axiom discovery process IS MetaDP—iterating on problem formulations:

```python
class AxiomDiscoveryMetaDP(MetaDP[str, str]):
    """
    MetaDP for finding optimal axiom formulations.

    Level 0: Initial formulation (Constitution mining)
    Level 1: Solve Bellman (which axioms satisfy principles?)
    Level 2: Evaluate quality (Mirror Test alignment)
    Level 3: Refine formulation (living corpus validation)
    """

    def __init__(self, constitution_paths: list[str]):
        super().__init__()

        # Stage 1: Constitution Mining as initial formulation
        stage1 = ProblemFormulation(
            name="constitution_mining",
            description="Extract axiom candidates from principles docs",
            state_type=str,
            initial_states=frozenset(constitution_paths),
            goal_states=frozenset(),  # Unknown until discovery
            available_actions=lambda s: frozenset(["extract", "filter", "rank"]),
            transition=lambda s, a: self._mine_transition(s, a),
            reward=lambda s, a, ns: self._mining_reward(s, a, ns),
        )
        self.add_formulation(stage1)

        # Stage 2: Mirror Test as reformulation
        self.add_reformulator(
            "mirror_test",
            lambda f: self._apply_mirror_test(f)
        )

        # Stage 3: Living Corpus as refinement
        self.add_reformulator(
            "living_corpus",
            lambda f: self._validate_with_corpus(f)
        )

    def _mining_reward(self, state: str, action: str, next_state: str) -> float:
        """Reward axiom candidates that compress well."""
        if action == "extract":
            return 0.3  # Extraction is easy, low reward
        elif action == "filter":
            return 0.6  # Filtering requires judgment
        elif action == "rank":
            return 0.9  # Ranking is the goal
        return 0.5

    def _apply_mirror_test(self, formulation: ProblemFormulation) -> ProblemFormulation:
        """Reformulate based on Mirror Test results."""
        # Mirror Test asks: "Does this feel true on your best day?"
        # Results add/remove axiom candidates
        return formulation.with_refined_goal_states(
            self._get_mirror_test_accepted()
        )

    def _validate_with_corpus(self, formulation: ProblemFormulation) -> ProblemFormulation:
        """Reformulate based on behavioral validation."""
        # Living corpus shows what user actually acts on
        # Align axioms with demonstrated behavior
        return formulation.with_refined_rewards(
            self._behavior_aligned_reward
        )
```

---

## OptimalSubstructure as Sheaf Coherence

The DP optimal substructure property IS the sheaf gluing condition:

```
OptimalSubstructure:
    "Optimal solutions to subproblems compose to optimal solutions"

Sheaf Gluing:
    "Local sections that agree on overlaps glue to a global section"

In Zero Seed:
    Local: Proof for edge A→B, proof for edge B→C
    Overlap: Node B (shared endpoint)
    Global: Proof for path A→B→C
```

```python
class ZeroSeedOptimalSubstructure(OptimalSubstructure[NodeId]):
    """Verify that Zero Seed proofs compose correctly."""

    def verify_path(self, path: list[ZeroEdge]) -> bool:
        """
        Verify that a path through the hypergraph has optimal substructure.

        Each edge must be locally optimal, and the glued path must be
        globally optimal (i.e., no better path exists).
        """
        if len(path) < 2:
            return True

        # Get subproblem solutions for each edge
        subsolutions = []
        for edge in path:
            key = (edge.source, edge.target)
            solution = self.solutions.get(key)
            if solution is None:
                return False  # Edge not yet verified as optimal
            subsolutions.append(solution)

        # Glue and verify
        glued = subsolutions[0]
        for sub in subsolutions[1:]:
            glued_result = self.glue(glued, sub)
            if glued_result is None:
                return False  # Gluing failed
            glued = glued_result

        return True

    def glue(self, sol_a: SubproblemSolution, sol_b: SubproblemSolution) -> SubproblemSolution | None:
        """Glue two solutions at their shared boundary."""
        # Check overlap compatibility
        if sol_a.boundary_out != sol_b.boundary_in:
            return None

        return SubproblemSolution(
            subproblem=sol_a.subproblem + sol_b.subproblem,
            optimal_value=sol_a.optimal_value + sol_b.optimal_value,
            boundary_in=sol_a.boundary_in,
            boundary_out=sol_b.boundary_out,
            trace=sol_a.trace + sol_b.trace,
        )
```

---

## Contradiction as Pareto Frontier

Paraconsistent tolerance maps to multi-objective DP:

```python
def handle_contradiction_dp(
    node_a: ZeroNode,
    node_b: ZeroNode,
    constitution: ZeroSeedConstitution,
) -> ContradictionResolution:
    """
    Contradictions are Pareto frontiers, not errors.

    Two nodes contradict iff:
    - Neither dominates the other on all principles
    - They represent incomparable trade-offs
    """
    score_a = constitution.evaluate(None, "exist", node_a)
    score_b = constitution.evaluate(None, "exist", node_b)

    a_dominates = all(
        pa.score >= pb.score
        for pa, pb in zip(score_a.principle_scores, score_b.principle_scores)
    )
    b_dominates = all(
        pb.score >= pa.score
        for pa, pb in zip(score_a.principle_scores, score_b.principle_scores)
    )

    if a_dominates and not b_dominates:
        return ContradictionResolution(winner=node_a, reason="A dominates B on all principles")
    elif b_dominates and not a_dominates:
        return ContradictionResolution(winner=node_b, reason="B dominates A on all principles")
    else:
        # Pareto-incomparable: both are valid, dialectical invitation
        return ContradictionResolution(
            winner=None,
            reason="Pareto-incomparable: dialectical invitation",
            synthesis_required=True,
            pareto_frontier=compute_pareto_frontier([score_a, score_b]),
        )
```

---

## ValueAgent for Intelligent Navigation

Telescope navigation becomes value-guided:

```python
@dataclass
class TelescopeValueAgent(ValueAgent[TelescopeState, NavigationAction, NodeId]):
    """
    Value-guided telescope navigation.

    The optimal policy tells you where to look next.
    """
    graph: ZeroGraph
    constitution: ZeroSeedConstitution
    preferred_layer: int = 4  # Default focus on specs

    def __post_init__(self):
        self.states = self._compute_telescope_states()
        self.actions = lambda s: self._available_navigation_actions(s)
        self.transition = lambda s, a: self._navigate(s, a)
        self.output_fn = lambda s, a, ns: ns.focal_point

    def _navigation_reward(
        self,
        state: TelescopeState,
        action: NavigationAction,
        next_state: TelescopeState,
    ) -> float:
        """
        Reward navigation that leads to high-value nodes.

        JOY_INDUCING: Finding interesting nodes is delightful
        TASTEFUL: Focused navigation over random wandering
        """
        if next_state.focal_point is None:
            return 0.1  # Lost focus is bad

        target_node = self.graph.get_node(next_state.focal_point)
        if target_node is None:
            return 0.1

        # Higher value for more connected nodes
        connectivity = len(self.graph.edges_from(target_node.id))
        connectivity_score = min(1.0, connectivity / 5)

        # Higher value for nodes at preferred layer
        layer_alignment = 1.0 - abs(target_node.layer - self.preferred_layer) / 7.0

        # Constitutional score
        const_score = self.constitution.reward(None, "focus", target_node).total

        return (
            0.3 * connectivity_score +
            0.3 * layer_alignment +
            0.4 * const_score
        )

    def suggest_next(self, current: TelescopeState) -> NodeId:
        """Suggest optimal next focus based on value function."""
        best_value = float('-inf')
        best_target = None

        for action in self._available_navigation_actions(current):
            next_state = self._navigate(current, action)
            value = self._navigation_reward(current, action, next_state)
            if value > best_value:
                best_value = value
                best_target = next_state.focal_point

        return best_target
```

---

## Summary: DP-Native Zero Seed

| Zero Seed Concept | DP-Native Mapping |
|-------------------|-------------------|
| 7 Epistemic Layers | State space partitions |
| Edge traversal | Action selection |
| Proof/Witness | PolicyTrace |
| Constitution (7 principles) | Reward function |
| Telescope focal distance | Discount factor γ |
| Axiom discovery | MetaDP reformulation |
| Contradiction tolerance | Pareto frontier |
| Sheaf coherence | OptimalSubstructure |

**The Core Synthesis**:

```
Zero Seed = MetaDP[
    States = ZeroNode,
    Actions = EdgeKind,
    Reward = Constitution(7 principles),
    Trace = PolicyTrace ≅ Toulmin Proof ≅ Witness Mark
]
```

---

## Open Questions

1. **Value iteration convergence**: Does Zero Seed guarantee convergence?
2. **Exploration vs exploitation**: How should navigation balance?
3. **Multi-agent DP**: When multiple users share a graph?

---

*"The proof IS the decision. The trace IS the witness. The value IS the agent."*
