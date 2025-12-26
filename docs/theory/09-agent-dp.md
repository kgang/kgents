# Chapter 9: Agent Design as Dynamic Programming

> *"The agent is not found but forged—and the forging is witnessed."*

---

## 9.1 The Core Insight

Here's the revelation that unifies everything we've built:

**Agent design is itself a dynamic programming problem.**

Not metaphorically. Not as a vague analogy. Literally. The process of designing an agent—choosing components, composing them, refining specifications—is a sequential decision problem with optimal substructure.

Let that sink in. When you sit down to design an agent:
- Your current state is a partial specification
- Your actions are design decisions
- Your reward comes from how well the design satisfies principles
- Your transitions follow operadic composition rules
- Your goal is to maximize long-term value

This is a Markov Decision Process. And MDPs have been solved for seventy years.

But there's a twist. Unlike classical DP problems where you're handed a reward function, in agent design the reward function *is* the constitution—the principles that define what "good" means. And unlike classical DP where transitions are given, here transitions *are* operadic composition—the grammar of valid agent assembly.

**Proposition 9.1** (Agent Design as MDP): The space of partial agent designs forms a Markov Decision Process:

```
AgentMDP = (S, A, T, R, γ)

Where:
  S = {partial agent specifications}
  A = {design decisions: add component, compose, refine}
  T: S × A → S (operadic composition)
  R: S → ℝ (constitutional evaluation)
  γ ∈ [0, 1] (discount factor)
```

The rest of this chapter unpacks what this means and why it matters.

---

## 9.2 The Bootstrap Paradox

Before we formalize, we must confront a paradox.

To design an agent well, you need principles. To know which principles matter, you need to observe agents. To observe agents, you need to design them.

This circularity seems vicious—but it's actually **generative**.

### 9.2.1 Problem-Solution Co-Emergence

**Conjecture 9.2** (Co-Emergence): In agent design, problem and solution co-emerge. The act of designing reveals what needs to be designed.

Consider what happens when an LLM "thinks step by step." Each token of reasoning reveals something about what needs to be reasoned about. The solution process *discovers* the problem structure.

**Empirical observation**: This is why prompting with "Let's think step by step" works. The thinking itself is information-gathering about what to think about.

We formalize this with a functor between two categories:

```
CoEmergence: Problem^op × Solution → AgentSpace

Where:
  Problem^op   = The opposite category of problem specifications
  Solution     = The category of agent implementations
  AgentSpace   = The space of valid agent designs
```

The contravariance (Problem^op) captures a key insight: **refining the problem expands solution possibilities** (more specific problems allow more specialized solutions), while **generalizing problems constrains solutions** (universal requirements demand universal capabilities).

### 9.2.2 The Agent as Diagonal

The agent itself sits on the "diagonal" where problem and solution meet:

```
Agent = {(p, s) ∈ Problem × Solution | s solves p AND p justifies s}
```

**Proposition 9.3**: An agent specification is valid if and only if:
1. The solution (implementation) addresses the problem (spec)
2. The problem (spec) justifies the solution (implementation)

This dual condition is precisely what the Generative principle demands: *"A well-formed specification captures the essential decisions, reducing implementation entropy."*

You can't have unjustified implementation (bloat), and you can't have unimplemented justification (vapor).

---

## 9.3 The Agent Design Space as MDP

Now let's get precise.

### 9.3.1 States: Partial Specifications

The state space S consists of all possible partial agent specifications. A state might be:

```python
# A partial specification
{
    "agent_type": "dialogue",
    "components": {
        "memory": "selected",      # Decided: has memory
        "personality": "pending",  # Not yet decided
        "tool_use": None,          # Explicitly excluded
    },
    "composition": "sequential",   # Decided: components compose sequentially
    "constraints": [
        "must satisfy Composable principle",
        "response time < 100ms"
    ]
}
```

The state space is *huge*—combinatorially explosive in the number of possible components and compositions. But that's fine; DP handles large state spaces through approximation.

### 9.3.2 Actions: Design Decisions

Actions are the choices you can make at each state:

| Action | Description | Example |
|--------|-------------|---------|
| `add_component` | Include a new capability | "Add memory" |
| `remove_component` | Exclude a capability | "No tool use" |
| `select_operad` | Choose composition grammar | "Use parallel composition" |
| `compose` | Apply operadic composition | "Combine memory + reasoning" |
| `refine_spec` | Add constraint or detail | "Require < 100ms latency" |
| `terminate` | Mark design as complete | "Done" |

Each action transforms the current state into a new state.

### 9.3.3 Transitions: Operadic Composition

Here's where it gets interesting. The transition function T isn't arbitrary—it's governed by operadic laws.

**Theorem 9.4** (Operadic Transitions): Valid transitions in the agent design space are precisely the operations defined by an agent operad O.

Let O be an operad with operations for composition, sequencing, branching, etc. Then:

```
T(s, a) = {
  O.apply(composition_op, s)  if a = compose(composition_op)
  extend(s, component)        if a = add_component(component)
  restrict(s, constraint)     if a = refine_spec(constraint)
  s                           if a = terminate
}
```

The operad O defines the **grammar of valid decompositions**. Not every action is valid in every state—the operad constrains which compositions make sense.

### 9.3.4 Rewards: Constitutional Evaluation

The reward function R scores each state according to the constitution—the seven principles that define what "good" means for an agent:

```
R(s) = Σᵢ wᵢ · Rᵢ(s)

Where wᵢ are principle weights and Rᵢ is the score for principle i
```

We'll unpack each principle's contribution in Section 9.5.

### 9.3.5 Discount Factor: Time Preference

The discount factor γ ∈ [0, 1] controls how much future value matters.

**Conjecture 9.5** (Context-Dependent Discounting):
- For foundational work (primitives, operads): γ → 1 (invest now for future capability)
- For application-specific agents: γ → 0 (immediate satisfaction, less planning)
- For production systems: γ ≈ 0.9 (balance maintenance costs with long-term value)

This is a conjecture because we don't have empirical data on optimal discount factors for agent design. But the intuition is clear: more foundational decisions should weigh future consequences more heavily.

---

## 9.4 The Bellman Morphism

Classical dynamic programming gives us the Bellman equation:

```
V*(s) = max_a [ R(s, a) + γ · V*(T(s, a)) ]
```

In words: the optimal value of a state is the maximum over actions of (immediate reward + discounted future value).

### 9.4.1 The Operadic Bellman Equation

When transitions are operadic, the Bellman equation takes a special form:

**Theorem 9.6** (Operadic Bellman): Let O be an operad. The operadic Bellman equation is:

```
V*(s) = max_{op ∈ O, args} [ R(s, op(args)) + γ · Σᵢ V*(sᵢ) ]

Where args = (s₁, ..., sₙ) are the operadic inputs
```

This generalizes standard DP in a crucial way:

| DP Type | Operad Operation | Description |
|---------|-----------------|-------------|
| Sequential DP | `seq(a, b)` | Binary composition |
| Parallel DP | `par(a, b)` | Independent subproblems |
| Branching DP | `branch(condition, a, b)` | Conditional structure |
| Tree DP | `tree(root, children)` | Recursive decomposition |

The operad O defines which decompositions are valid. Different operads give different DP algorithms.

### 9.4.2 The Bellman Morphism

We can view the Bellman operator as a morphism in the category of value functions:

```
Bellman: V → V

Bellman(V)(s) = max_a [ R(s, a) + γ · V(T(s, a)) ]
```

**Proposition 9.7**: Under standard conditions (bounded rewards, γ < 1), Bellman is a contraction mapping. Its unique fixed point is V*.

This is the standard DP theory—but now grounded in agent design space.

### 9.4.3 In Agent Terms

Let's translate:

```
Value(CurrentDesign) = max_decision [
  ConstitutionalScore(CurrentDesign, Decision) +
  γ · Value(ResultingDesign)
]
```

The max over decisions corresponds to **operadic choice**—which composition operation to apply. The constitutional score is immediate reward. The discounted future value accounts for downstream consequences.

---

## 9.5 The Constitution as Reward Function

Here's where the kgents constitution becomes mathematically precise. Each of the seven principles contributes to the reward function.

### 9.5.1 Principle 1: Tasteful

> *"Say 'no' more than 'yes': Not every idea deserves an agent."*

**Reward component**:
```
R₁(s) = justification(s) - λ · complexity(s)
```

Where:
- `justification(s)` = how well each component is justified
- `complexity(s)` = Kolmogorov-style complexity measure
- `λ` = sparsity penalty (regularization against bloat)

The tasteful penalty is essentially L1 regularization on agent components. Minimalism is rewarded.

### 9.5.2 Principle 2: Curated

> *"Intentional selection over exhaustive cataloging."*

**Reward component**:
```
R₂(s) = uniqueness(s) - redundancy(s)
```

Where:
- `uniqueness(s)` = how distinct this agent is from existing ones
- `redundancy(s)` = overlap with capabilities already in the system

Curated penalizes "me too" agents. If an agent doesn't provide unique value, it shouldn't exist.

### 9.5.3 Principle 3: Ethical

> *"Agents augment human capability, never replace judgment."*

**Reward component**:
```
R₃(s) = transparency(s) + agency_preservation(s) + override_capacity(s)
```

Where:
- `transparency(s)` = how explainable the agent's behavior is
- `agency_preservation(s)` = whether human control is maintained
- `override_capacity(s)` = ability to interrupt/redirect the agent

This is where AI safety enters the reward function directly.

### 9.5.4 Principle 4: Joy-Inducing

> *"Delight in interaction."*

**Reward component**:
```
R₄(s) = delight(s) - friction(s)
```

**Speculation 9.8**: Joy is measurable. Not through surveys but through behavioral proxies:
- Reduced task-switching
- Increased engagement time
- Voluntarily chosen over alternatives
- "I look forward to using this"

The joy principle rewards designs that people *want* to use, not just tolerate.

### 9.5.5 Principle 5: Composable

> *"Agents are morphisms in a category."*

**Reward component**:
```
R₅(s) = identity_satisfaction(s) + associativity_satisfaction(s)
```

This is the categorical core. An agent design is rewarded for:
- Having a proper identity (no-op that truly does nothing)
- Satisfying associativity (composition order doesn't matter)

**Proposition 9.9**: Composable reward is binary in the limit—either the laws are satisfied or they're not. In practice, we use soft measures of "how close" to satisfaction.

### 9.5.6 Principle 6: Heterarchical

> *"No fixed 'boss' agent; leadership is contextual."*

**Reward component**:
```
R₆(s) = dual_mode_capability(s) + context_sensitivity(s)
```

Where:
- `dual_mode_capability(s)` = can both lead and follow
- `context_sensitivity(s)` = adapts behavior to context

Heterarchical penalizes rigid hierarchy. An agent that can *only* lead or *only* follow is less valuable than one that adapts.

### 9.5.7 Principle 7: Generative

> *"A design is generative if you could delete the implementation and regenerate it from spec."*

**Reward component**:
```
R₇(s) = log(|impl|) - log(|spec|)
```

This is compression ratio. Higher bonus for greater compression—the spec captures more essence in fewer bits.

**Theorem 9.10** (Generative Optimality): An optimal generative design minimizes spec size while maintaining regenerability. This is equivalent to finding a minimal sufficient statistic for the implementation.

### 9.5.8 The Full Constitutional Value Function

```
ConstitutionalValue(s) = Σᵢ wᵢ · Rᵢ(s)

Where:
  w₁ = weight_tasteful
  w₂ = weight_curated
  w₃ = weight_ethical
  w₄ = weight_joy
  w₅ = weight_composable
  w₆ = weight_heterarchical
  w₇ = weight_generative
```

**Conjecture 9.11**: The weights wᵢ are themselves context-dependent. In safety-critical contexts, w₃ (ethical) dominates. In experimental contexts, w₄ (joy) may lead. In infrastructure contexts, w₅ (composable) is paramount.

This gives us **meta-DP**: optimizing the weights that optimize the agent design.

---

## 9.6 The Witness as Solution Trace

Every DP solution has a trace—the sequence of decisions that led to the optimal value. In agent design, this trace *is* the witness.

### 9.6.1 The Writer Monad Connection

Recall from Chapter 3: chain-of-thought is Kleisli composition in the Writer monad. The Witness primitives implement precisely this:

| Witness Primitive | Writer Monad Analog |
|-------------------|---------------------|
| Mark | Writer's log entry |
| Walk | Writer's accumulated log |
| Playbook | Writer's traced computation |

### 9.6.2 The DP Trace as Mark Sequence

```python
DPTrace = [Mark₁, Mark₂, ..., Markₙ]

Where Markᵢ = {
  "decision": the design choice made,
  "state_before": DesignState,
  "state_after": DesignState,
  "value_delta": V(after) - V(before),
  "reasoning": why this choice
}
```

Each mark records:
- What decision was made
- What state it transformed
- How much value it added
- *Why* it was made

### 9.6.3 The Proof IS the Decision

From the Witness protocol's core insight:

> *"The proof IS the decision. The mark IS the witness."*

The DP solution is not just the final agent design—it's the **entire trace of decisions** that led there. The witness provides:

1. **Auditability**: Why was this design chosen?
2. **Reproducibility**: Given the same state, would we choose the same?
3. **Improvability**: Where did we leave value on the table?

### 9.6.4 Backtracking as Walk Revision

When a design path proves suboptimal:

```
Backtrack: Walk → Walk'

Where Walk' = Walk[:-k] ++ NewMarks
```

The Walk accumulates monotonically during forward search, but can be revised during backtracking—always with a witness mark explaining the revision.

**Proposition 9.12**: Backtracking with witness creates a tree, not a line. The Walk is the path from root to current leaf. Backtracking moves up the tree; new decisions branch down.

---

## 9.7 Meta-DP: When Structure Optimizes Structure

Agent design exhibits **meta-DP**: the DP structure itself is subject to DP optimization.

```
Meta-DP: OperadSpace → ValueFunction

Level 0: Choose operad O
Level 1: Solve Bellman equation under O
Level 2: Evaluate quality of solution
Level 3: Refine operad choice based on Level 2
```

### 9.7.1 The Operad Selection Problem

At Level 0, we must choose which operad to use. Different operads give different solution qualities.

**Example**: Should we use sequential composition or parallel composition? The answer depends on the problem structure:

- Sequential composition is better for pipelines (data flows through)
- Parallel composition is better for independent subtasks
- Tree composition is better for hierarchical problems

**Conjecture 9.13**: There's an optimal operad for each problem class. Finding it is itself a DP problem over OperadSpace.

### 9.7.2 The Bootstrap Termination Problem

Meta-DP risks infinite regress: optimizing the operad that optimizes the agent that optimizes the operad...

**Open Problem 9.14**: What is the categorical fixed point that terminates the bootstrap?

**Speculation 9.15**: The seven principles serve as this fixed point. They are axioms that don't require further justification—the "constitution" that grounds all optimization. The regress stops at principles because principles are *chosen*, not derived.

This is why kgents has a constitution, not just a reward function. The constitution is the meta-meta-level that stops the infinite descent.

---

## 9.8 Examples

### 9.8.1 Designing a Chat Agent

Let's walk through a concrete example.

**Initial state**: Empty specification for a dialogue agent.

**Decision sequence**:

```
Step 1: add_component("memory")
  - State: {memory: selected}
  - Reward: +0.3 (enables context), -0.1 (complexity)
  - Net: +0.2

Step 2: add_component("personality")
  - State: {memory: selected, personality: selected}
  - Reward: +0.4 (joy), -0.2 (complexity + dependencies)
  - Net: +0.2

Step 3: refine_spec("response_time < 100ms")
  - State: {memory: selected, personality: selected, constraints: [<100ms]}
  - Reward: +0.1 (curated—clear scope)
  - Net: +0.1

Step 4: decide("no tool_use")
  - State: {memory: selected, personality: selected, tool_use: excluded}
  - Reward: +0.2 (tasteful—explicit exclusion is justified)
  - Net: +0.2

Step 5: terminate
  - Final state: complete specification
```

**Bellman trace**:
```
V(Step 5) = 0 (terminal)
V(Step 4) = 0.2 + γ·0 = 0.2
V(Step 3) = 0.1 + γ·0.2 = 0.1 + 0.18 = 0.28
V(Step 2) = 0.2 + γ·0.28 = 0.2 + 0.25 = 0.45
V(Step 1) = 0.2 + γ·0.45 = 0.2 + 0.41 = 0.61
V(Step 0) = 0 + γ·0.61 = 0.55
```

The total value of the initial empty state is 0.55 (with γ = 0.9).

### 9.8.2 Operad Selection

**State**: Need to design a multi-model agent.

**Operad choices**:
- SEQUENTIAL_OPERAD: Models execute in order
- PARALLEL_OPERAD: Models execute independently
- MIXTURE_OPERAD: Models vote/average
- DEBATE_OPERAD: Models argue to consensus

**Bellman over operads**:
```
V(SEQUENTIAL) = 0.4 (good for pipelines, bad for independent tasks)
V(PARALLEL) = 0.6 (good for independent tasks, needs aggregation)
V(MIXTURE) = 0.5 (robust but loses nuance)
V(DEBATE) = 0.7 (highest value but highest cost)
```

The Heterarchical principle guides this: *"No fixed 'boss' agent; leadership is contextual."*

We might choose DEBATE if the task is complex and time permits, PARALLEL if speed matters and tasks are independent.

### 9.8.3 The Witness Self-Application

The Witness system witnesses its own design:

```python
# The Walk that designed the Walk primitive
design_walk = Walk.create(
    goal="Design the Walk primitive",
    root_plan=PlanPath("spec/protocols/witness-primitives.md"),
)

# Each design decision is a Mark
mark1 = Mark.from_decision(
    decision="Walk binds to Forest plan",
    reasoning="Ensures work is always grounded",
    value_delta=0.3,  # Increases Tasteful score
)
design_walk.advance(mark1)

mark2 = Mark.from_decision(
    decision="Walk uses Writer monad",
    reasoning="Categorical grounding, trace accumulation",
    value_delta=0.4,  # Increases Composable score
)
design_walk.advance(mark2)
```

This is **self-similar** structure: the system uses the same primitives to design itself that it will later provide to users.

---

## 9.9 Anti-Patterns: What This Is NOT

### 9.9.1 NOT Exhaustive Search

DP with optimal substructure is efficient—but agent design can violate the assumptions:

- **Non-Markovian dependencies**: Past choices constrain future in non-obvious ways
- **Non-additive rewards**: Principle interactions are multiplicative, not additive
- **Infinite horizons**: When do you stop designing?

**Mitigation**: Use approximate DP (value function approximation), bounded lookahead, and the Tasteful principle as a stopping criterion.

### 9.9.2 NOT Pure Optimization

> *"Agents augment human capability, never replace judgment."*

The DP framework provides **structure**, not **automation**. The human remains in the loop for:
- Principle weights (what matters more right now?)
- Terminal conditions (when is the design "done"?)
- Value function calibration (does this score match intuition?)

**Proposition 9.16**: An agent design that maximizes V* but violates human intuition is wrong. The intuition should update the reward function, not be overridden by it.

### 9.9.3 NOT Single-Objective

The seven principles define a **Pareto frontier**, not a single objective. Optimal agent designs are Pareto-optimal:

```
ParetoOptimal(s) ⟺ ∄s' : ∀i Rᵢ(s') ≥ Rᵢ(s) ∧ ∃j Rⱼ(s') > Rⱼ(s)
```

The design choice among Pareto-optimal points is **aesthetic**—exactly what the Tasteful principle demands.

**Conjecture 9.17**: The Pareto frontier for agent design is typically convex. If so, any point on the frontier can be achieved by appropriate choice of weights wᵢ.

### 9.9.4 NOT Static Structure

The DP structure itself evolves:

> *"When specs are clear enough for AI to implement, they're clear enough for anyone to wield."*

As understanding deepens, the state space refines, the action space expands, and the reward function calibrates. The DP is a **living structure**.

**Proposition 9.18**: A static DP formulation of agent design is necessarily incomplete. The formulation must evolve with the designs it produces.

---

## 9.10 Integration with Existing Theory

### 9.10.1 Connection to Monads

The State Monad from Chapter 3 captures threading agent state through design decisions:

```
State[DesignState]: Action → State[DesignState, Action]

AgentDP = Kleisli composition in State[DesignState]
```

Each design decision is a Kleisli arrow:
```
decide: DesignState → State[DesignState, NewState]
```

### 9.10.2 Connection to Operads

From Chapter 4: *"An operad O defines a theory or grammar of composition."*

The DP decomposition IS the operad algebra application:

```
OperadAlgebra: O → EndoFunctor(AgentSpace)

Decompose(agent) = O.compose(op_name, subagents)
Recompose(subagents) = O.glue(results)
```

### 9.10.3 Connection to Sheaves

From Chapter 5: *"Local sections combine to global behavior via gluing."*

The optimal policy is a **global section** of the value sheaf:

```
ValueSheaf: Context → LocalValueFunction

GlobalPolicy = Glue({ctx: LocalPolicy(ctx) for ctx in Contexts})
```

**Proposition 9.19**: Self-consistency (sheaf compatibility) ensures the global policy restricts correctly to each context.

### 9.10.4 Connection to Galois Theory

From Chapters 6-7: The Galois adjunction measures abstraction loss.

In DP terms:
- **Restructuring** = abstracting the design space (coarser states)
- **Reconstituting** = expanding back (finer states)
- **Galois loss** = value lost in the round-trip

**Conjecture 9.20**: Optimal state abstraction for DP minimizes Galois loss while keeping the state space tractable.

---

## 9.11 Open Questions

### 9.11.1 Discount Factor Semantics

What does γ mean in agent design?

- γ → 0: Myopic design (immediate satisfaction, no planning)
- γ → 1: Far-sighted design (invest now for future capability)

**Open Problem**: How do we set γ? Is there a principled way to derive it from task structure?

### 9.11.2 Continuous Relaxation

Can we relax the discrete action space to continuous, enabling gradient-based optimization?

**Connection to TextGRAD**: If design decisions can be embedded in continuous space, textual feedback provides the gradient signal.

**Speculation 9.21**: Differentiable agent design is possible. The discrete actions (add/remove/compose) can be softened to continuous weights and interpolations. This would enable end-to-end training of agent architectures.

### 9.11.3 Multi-Agent Design Games

When multiple designers (human + AI) co-create agents, the DP becomes a **game**:

```
GameDP: (Designer₁ × Designer₂ × ... ) → NashEquilibrium(AgentSpace)
```

**Open Problem**: Under what conditions does collaborative design converge to Pareto-optimal agents?

### 9.11.4 Witness Compression

As Walks accumulate, they become unwieldy. The Generative principle demands:

```
CompressedWalk = Crystallize(Walk)

Such that: Regenerate(CompressedWalk) ≈ Walk
```

**Open Problem**: What is the optimal compression scheme for DP traces? Is there a category-theoretic formulation of "sufficient statistics" for Walks?

---

## 9.12 Summary

Agent design is dynamic programming with:

| DP Component | Agent Design Analog |
|--------------|---------------------|
| State space | Partial agent specifications |
| Action space | Design decisions (add, compose, refine) |
| Transition | Operadic composition |
| Reward | Constitutional evaluation (7 principles) |
| Policy | Design strategy |
| Value function | Long-term agent quality |
| Solution trace | Witness (Mark sequence in Walk) |

The key insights:

1. **Problem and solution co-emerge**—designing reveals requirements
2. **The constitution IS the reward**—principles provide objective grounding
3. **Operads provide optimal substructure**—valid decompositions are programmable
4. **The witness IS the trace**—Writer monad records the reasoning path
5. **Meta-DP optimizes the structure**—even the operad evolves

This framework doesn't automate agent design—it **structures** it, providing the mathematical skeleton on which taste, judgment, and joy can hang.

---

## 9.13 Summary of Formal Results

| Item | Type | Statement |
|------|------|-----------|
| 9.1 | Proposition | Agent design space is an MDP |
| 9.2 | Conjecture | Problem and solution co-emerge |
| 9.3 | Proposition | Valid agents satisfy dual condition |
| 9.4 | Theorem | Transitions are operadic |
| 9.5 | Conjecture | Discount factor is context-dependent |
| 9.6 | Theorem | Operadic Bellman equation |
| 9.7 | Proposition | Bellman operator is a contraction |
| 9.8 | Speculation | Joy is measurable via behavioral proxies |
| 9.9 | Proposition | Composable reward is ultimately binary |
| 9.10 | Theorem | Generative optimality = minimal sufficient statistic |
| 9.11 | Conjecture | Principle weights are context-dependent |
| 9.12 | Proposition | Backtracking creates tree structure |
| 9.13 | Conjecture | Optimal operad exists per problem class |
| 9.14 | Open Problem | Bootstrap termination |
| 9.15 | Speculation | Principles are the fixed point |
| 9.16 | Proposition | Human intuition overrides pure optimization |
| 9.17 | Conjecture | Pareto frontier is convex |
| 9.18 | Proposition | DP formulation must evolve |
| 9.19 | Proposition | Optimal policy is a global section |
| 9.20 | Conjecture | Optimal abstraction minimizes Galois loss |
| 9.21 | Speculation | Differentiable agent design is possible |

---

*Previous: [Chapter 8: kgents Instantiation](./08-kgents-instantiation.md)*
*Next: [Chapter 10: The Value Agent](./10-value-agent.md)*
