# Chapter 10: The Value Agent

> *"The value IS the agent. The agent IS the value function. There is no distinction."*

---

## 10.1 The Core Claim

This chapter develops the central insight of DP-native agent design: **every agent is a value function**.

Not "agents can be modeled as value functions" or "value functions are useful for agents"—stronger: the agent IS its value function. Agent state IS DP state. Agent output IS optimal action plus value estimate.

This identification is not metaphorical. It has mathematical content:

**Theorem 10.1** (Agent-DP Isomorphism)

There exists an isomorphism between well-behaved agents and MDP formulations:

| Agent Component | DP Component |
|-----------------|--------------|
| State space S | MDP state space |
| Actions A | MDP action space |
| Transitions | Dynamics T : S x A -> S |
| Quality measure | Reward function R |
| Behavior | Policy pi : S -> A |
| Assessment | Value function V : S -> R |

The isomorphism is structure-preserving: agent composition corresponds to Bellman backup; agent optimality corresponds to DP optimality.

### 10.1.1 Why This Matters

Traditional agent frameworks treat decision-making as one capability among many. An agent might reason, act, perceive, plan. Decision-making is a module.

The DP-native view inverts this. Decision-making is not a module—it's the foundation. Everything else—perception, reasoning, acting—is the computation required to evaluate the value function.

**Implication 1**: Agent design reduces to reward design. If you can specify the reward, you've specified the agent. The Constitution (Chapter 8) becomes the single source of truth for agent behavior.

**Implication 2**: Agent introspection becomes tractable. An agent can explain its behavior by reporting its value estimates. "I chose action A because V(T(s,A)) > V(T(s,B))."

**Implication 3**: Agent composition has a canonical form. Compose value functions via the Bellman equation, and you get composed agents automatically.

---

## 10.2 The Value Agent Definition

We now give the formal definition:

### Definition 10.2 (ValueAgent)

A **ValueAgent** is a tuple (S, A, V, pi, T) where:

- **S** is a finite set of states
- **A** is a finite set of actions
- **V : S -> R** is the value function (assigning worth to states)
- **pi : S -> A** is the policy (choosing actions)
- **T : S x A -> S** is the transition function (dynamics)

These components satisfy:

**Bellman Consistency**: V(s) = R(s, pi(s)) + gamma * V(T(s, pi(s)))

**Policy Optimality**: pi(s) = argmax_a [R(s,a) + gamma * V(T(s,a))]

### 10.2.1 The Full Type Signature

For implementation, we make this generic:

```
ValueAgent[S, A, V]:
  state: S
  evaluate: S -> V          # Value function
  act: S -> A               # Policy
  transition: (S, A) -> S   # Dynamics
```

The type parameter V is typically R (real numbers) but could be:
- Tuple[R, R, ...] for multi-objective optimization
- Distribution[R] for uncertainty-aware values
- (R, Trace) for value + justification (Writer monad)

### 10.2.2 Minimal vs. Augmented Agents

**Minimal ValueAgent**: Just the tuple. No memory, no history, no frills.

**Augmented ValueAgent**: The minimal agent plus:
- Reward function R : S x A x S -> R
- Discount factor gamma in [0, 1]
- Value iteration algorithm
- Q-function Q : S x A -> R

The minimal form is theoretically clean. The augmented form is practically useful. They're equivalent given the Bellman consistency constraint.

---

## 10.3 Connection to PolyAgent

How does ValueAgent relate to our polynomial agent from Chapter 8?

### Theorem 10.3 (PolyAgent-ValueAgent Correspondence)

PolyAgent[S, A, B] is isomorphic to ValueAgent[S, A, V] when:

1. B includes value information (B >= V)
2. A is action-typed
3. PolyAgent.step implements Bellman backup

*Proof sketch.*

A PolyAgent has state S, accepts input A, produces output B via step().

Define:
- V(s) = B.value_component for the output of step(noop_input) in state s
- pi(s) = argmax_a step(a).value_component
- T(s, a) = state after step(a)

Then (S, A, V, pi, T) is a ValueAgent.

Conversely, given ValueAgent (S, A, V, pi, T), define:
- PolyAgent.state = S
- PolyAgent.step(a) = (pi(T(s,a)), V(T(s,a)))

The constructions are inverse. QED.

### 10.3.1 Same Structure, Different Emphasis

PolyAgent emphasizes **state-dependent behavior**: different modes accept different inputs.

ValueAgent emphasizes **optimization**: every action is chosen to maximize value.

These are compatible perspectives on the same underlying structure. The polynomial functor is the state machine; the value function is what the state machine optimizes.

### 10.3.2 When They Diverge

The correspondence breaks when:
- PolyAgent has side effects not captured by state transitions
- ValueAgent's reward is not representable as PolyAgent output
- The action space is continuous (requires care with argmax)

In kgents, we design to maintain correspondence. This keeps theory and implementation aligned.

---

## 10.4 Bellman as Composition Law

The Bellman equation is not just an optimization technique—it's a **composition law**.

### 10.4.1 The Equation

V*(s) = max_a [R(s,a) + gamma * V*(T(s,a))]

This says: the value of state s equals the immediate reward plus discounted future value, maximized over actions.

### 10.4.2 Why It's a Composition Law

Consider two agents A1 and A2 with value functions V1 and V2. How do we compose them?

**Sequential composition** (A1 >> A2):
```
V_{A1>>A2}(s) = V_A1(s) + gamma^n * V_A2(T^n(s, pi_A1))
```

Where n is the number of steps A1 takes. This IS Bellman iteration with A1's policy for n steps, then switching to A2.

**Parallel composition** (A1 || A2):
```
V_{A1||A2}(s) = max(V_A1(s), V_A2(s))
```

Choose whichever agent has higher value. This IS policy switching.

**Branching composition** (if c then A1 else A2):
```
V_{branch}(s) = P(c|s) * V_A1(s) + (1 - P(c|s)) * V_A2(s)
```

Expected value under condition uncertainty.

### 10.4.3 The Category of Value Agents

**Theorem 10.4**: Value agents form a category where:
- Objects: State spaces S
- Morphisms: Value agents (S, A, V, pi, T) where T ends in target state space
- Composition: Bellman combination of value functions
- Identity: The trivial agent with V(s) = 0, pi(s) = noop, T(s, noop) = s

The categorical laws (associativity, identity) follow from the algebraic properties of max, +, and gamma.

### 10.4.4 Agents Satisfying Bellman Compose Correctly

**Key insight**: An agent satisfies the Bellman equation iff it can be composed with other Bellman-satisfying agents without value inconsistency.

Non-Bellman agents can still be composed, but the composed value function may not reflect actual returns. Bellman consistency ensures that V(s) really is the expected return from s—and this property propagates through composition.

---

## 10.5 Policy Extraction

Given a value function, how do we get a policy?

### 10.5.1 The Standard Extraction

pi(s) = argmax_a Q(s, a)

Where Q(s, a) = R(s, a) + gamma * V(T(s, a))

This is **greedy policy extraction**: always choose the action that looks best right now.

### 10.5.2 Q as Morphism

The Q-function Q : S x A -> V is itself a morphism in a suitable category:

**Definition 10.5**: The **state-action category** has:
- Objects: State-action pairs (s, a)
- Morphisms: Q-functions assigning values
- Composition: Bellman backup Q'(s, a) = R + gamma * max_a' Q(T(s,a), a')

Q-functions are morphisms from (state, action) space to value space, satisfying the Bellman equation.

### 10.5.3 Policy as Natural Transformation

**Definition 10.6**: Given Q-function Q, the **policy natural transformation** pi_Q is:

pi_Q : States -> Actions
pi_Q(s) = argmax_a Q(s, a)

**Theorem 10.7**: If Q satisfies Bellman optimality, pi_Q is the unique optimal policy.

*Proof sketch.*

By Bellman optimality: Q*(s, a) = R(s, a) + gamma * max_a' Q*(T(s, a), a')

Taking argmax preserves optimality—any other policy achieves strictly lower value. The uniqueness follows from strict maximization (ties can be broken arbitrarily).

### 10.5.4 Soft Policy Extraction

Hard argmax is discontinuous—small changes in Q cause discrete policy jumps. For differentiable systems, use **soft extraction**:

pi_soft(a | s) = exp(Q(s, a) / tau) / Z(s)

Where tau is temperature and Z(s) is the partition function. As tau -> 0, this approaches hard argmax.

This is relevant for TextGRAD integration (Section 10.6).

---

## 10.6 Temporal Difference as Gradient

The TD error is the "gradient" in value space:

### 10.6.1 TD Error Definition

delta_t = R_t + gamma * V(s_{t+1}) - V(s_t)

This is the discrepancy between:
- What we expected: V(s_t)
- What we observed: R_t + gamma * V(s_{t+1})

### 10.6.2 TD as Value Gradient

**Claim**: TD error is the gradient of value accuracy loss.

*Argument.*

Define value accuracy loss: L(V) = E[(V(s) - V_true(s))^2]

The gradient: dL/dV(s) = 2 * (V(s) - V_true(s))

We don't know V_true, but we have a sample: V_true(s) ≈ R + gamma * V(s')

Substituting: dL/dV(s) ≈ 2 * (V(s) - [R + gamma * V(s')]) = 2 * (-delta)

So -delta is (proportional to) the gradient. Updating V(s) += alpha * delta does gradient descent on value accuracy.

### 10.6.3 Connection to TextGRAD

TextGRAD treats language model outputs as differentiable. The "gradient" of a text output is natural language feedback on how to improve.

**Insight**: TD error is to value functions what TextGRAD feedback is to text outputs.

| DP / Value Functions | TextGRAD / Language |
|----------------------|---------------------|
| TD error delta | Natural language feedback |
| V(s) += alpha * delta | Output += feedback |
| Value accuracy loss | Task performance loss |
| Bellman target | Desired output |

### 10.6.4 Unified Gradient View

**Conjecture 10.8**: There exists a general "agent gradient" framework unifying TD learning and TextGRAD:

AgentGrad[X](x, x_target) = direction to move x toward x_target

For X = real-valued functions: TD error
For X = text outputs: TextGRAD feedback
For X = policies: Policy gradient
For X = constitutions: Principle score gradient

This suggests a **differential geometry of agent space** where improvement is always gradient-like.

---

## 10.7 Multi-Agent Value

When multiple agents interact, value functions become game-theoretic.

### 10.7.1 Each Agent Has a Value Function

In a multi-agent system, each agent i has:
- State space S_i (may share components with others)
- Action space A_i
- Value function V_i : S -> R
- Policy pi_i : S -> A_i

The joint state is S = S_1 x S_2 x ... x S_n.

### 10.7.2 Game-Theoretic Equilibria

**Definition 10.9** (Nash Equilibrium in Values)

A policy profile (pi_1, ..., pi_n) is a **Nash equilibrium** if for all i:

V_i(s; pi_1, ..., pi_i, ..., pi_n) >= V_i(s; pi_1, ..., pi'_i, ..., pi_n)

for all alternative policies pi'_i. No agent can unilaterally improve.

### 10.7.3 Cooperative vs. Competitive

**Cooperative**: All agents share a reward. V_i = V for all i.

The multi-agent problem reduces to single-agent with joint action space. Composition is straightforward.

**Competitive** (zero-sum): One agent's reward is another's loss.

Value functions satisfy: V_1(s) = -V_2(s). The equilibrium is minimax.

**Mixed**: General-sum games. Complex equilibria.

### 10.7.4 Multi-Agent Composition

**Theorem 10.10**: Cooperative value agents compose as single-agent:

ValueAgent[S1, A1, V] || ValueAgent[S2, A2, V] = ValueAgent[S1 x S2, A1 x A2, V]

The shared value function ensures aligned incentives.

**Warning**: Non-cooperative agents don't compose cleanly. Their joint system may not have a single value function—only a value function profile.

---

## 10.8 Implementation Pattern

We now give the concrete implementation:

### 10.8.1 Core Class

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from abc import ABC, abstractmethod

S = TypeVar('S')  # State type
A = TypeVar('A')  # Action type
V = TypeVar('V')  # Value type (typically float)

@dataclass
class ValuedOutput(Generic[A, V]):
    """Output with value estimate."""
    action: A
    value: V
    rationale: str = ""  # Why this action? (trace)

class ValueAgent(Generic[S, A, V], ABC):
    """
    DP-Native Agent: Every agent IS a value function.

    V(s) = max_a [R(s,a) + gamma * V(T(s,a))]

    This is not an agent that uses DP—this agent IS its value function.
    """

    def __init__(self, initial_state: S, gamma: float = 0.99):
        self.state = initial_state
        self.gamma = gamma

    @abstractmethod
    def evaluate(self, state: S) -> V:
        """The value function V : S -> V."""
        ...

    @abstractmethod
    def reward(self, state: S, action: A, next_state: S) -> float:
        """Immediate reward R(s, a, s')."""
        ...

    @abstractmethod
    def transition(self, state: S, action: A) -> S:
        """Dynamics T : S x A -> S."""
        ...

    @abstractmethod
    def actions(self, state: S) -> list[A]:
        """Available actions in state."""
        ...

    def q_value(self, state: S, action: A) -> V:
        """Q(s, a) = R(s, a, s') + gamma * V(s')."""
        next_state = self.transition(state, action)
        immediate = self.reward(state, action, next_state)
        future = self.gamma * self.evaluate(next_state)
        return immediate + future

    def policy(self, state: S) -> A:
        """pi(s) = argmax_a Q(s, a)."""
        available = self.actions(state)
        if not available:
            raise ValueError(f"No actions available in state {state}")
        return max(available, key=lambda a: self.q_value(state, a))

    def step(self, observation: S = None) -> ValuedOutput[A, V]:
        """
        The main agent interface.

        Takes optional observation, returns action with value estimate.
        """
        # Update state if observation provided
        if observation is not None:
            self.state = observation

        # Compute value and action
        value = self.evaluate(self.state)
        action = self.policy(self.state)

        # Execute transition
        next_state = self.transition(self.state, action)

        # Build output with trace
        output = ValuedOutput(
            action=action,
            value=value,
            rationale=f"V(s)={value:.3f}, "
                      f"Q(s,a)={self.q_value(self.state, action):.3f}"
        )

        # Update state
        self.state = next_state

        return output
```

### 10.8.2 Constitution-Based Reward

```python
from enum import Enum

class Principle(Enum):
    """The 7 principles as reward components."""
    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy_inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"

class Constitution:
    """
    The Constitution IS the reward function.

    R(s, a, s') = sum_i w_i * R_i(s, a, s')
    """

    WEIGHTS = {
        Principle.ETHICAL: 2.0,       # Safety first
        Principle.COMPOSABLE: 1.5,    # Architecture second
        Principle.JOY_INDUCING: 1.2,  # Kent's aesthetic
        Principle.TASTEFUL: 1.0,
        Principle.CURATED: 1.0,
        Principle.HETERARCHICAL: 1.0,
        Principle.GENERATIVE: 1.0,
    }

    def __init__(self, principle_scorers: dict[Principle, Callable]):
        self.scorers = principle_scorers

    def reward(self, state: S, action: A, next_state: S) -> float:
        """Compute constitutional reward."""
        total = 0.0
        for principle, scorer in self.scorers.items():
            score = scorer(state, action, next_state)
            weight = self.WEIGHTS.get(principle, 1.0)
            total += weight * score
        return total
```

### 10.8.3 Value Iteration

```python
class ValueIterationMixin:
    """Mixin providing value iteration for ValueAgent."""

    def value_iterate(self, epsilon: float = 1e-6, max_iters: int = 1000):
        """
        Compute optimal value function via iteration.

        Repeatedly apply: V'(s) = max_a [R(s,a) + gamma * V(T(s,a))]
        Until convergence.
        """
        # Initialize value estimates
        V = {s: 0.0 for s in self.all_states()}

        for i in range(max_iters):
            V_new = {}
            max_delta = 0.0

            for s in self.all_states():
                q_values = [
                    self.reward(s, a, self.transition(s, a))
                    + self.gamma * V[self.transition(s, a)]
                    for a in self.actions(s)
                ]
                V_new[s] = max(q_values) if q_values else 0.0
                max_delta = max(max_delta, abs(V_new[s] - V[s]))

            V = V_new

            if max_delta < epsilon:
                break

        self._value_table = V
        return V

    def evaluate(self, state: S) -> float:
        """Look up precomputed value."""
        if not hasattr(self, '_value_table'):
            self.value_iterate()
        return self._value_table.get(state, 0.0)
```

---

## 10.9 Examples

We illustrate with three concrete value agents:

### 10.9.1 Chat Agent with Conversation Value

```python
@dataclass
class ConversationState:
    """State: conversation history + user engagement."""
    history: list[str]
    engagement: float  # 0 to 1
    turns_remaining: int

class ChatValueAgent(ValueAgent[ConversationState, str, float]):
    """
    Chat agent that maximizes conversation value.

    Value = engagement sustained over remaining turns.
    """

    def evaluate(self, state: ConversationState) -> float:
        # Value = current engagement * expected future turns
        return state.engagement * state.turns_remaining

    def reward(self, s: ConversationState, a: str, s_: ConversationState) -> float:
        # Reward = engagement change
        return s_.engagement - s.engagement

    def transition(self, state: ConversationState, action: str) -> ConversationState:
        # Generate response, update engagement
        engagement_delta = self._predict_engagement(state, action)
        return ConversationState(
            history=state.history + [action],
            engagement=min(1.0, max(0.0, state.engagement + engagement_delta)),
            turns_remaining=state.turns_remaining - 1
        )

    def actions(self, state: ConversationState) -> list[str]:
        # Generate candidate responses
        return self._generate_candidates(state.history)
```

### 10.9.2 Code Agent with Quality Value

```python
@dataclass
class CodeState:
    """State: codebase + test status + complexity."""
    files: dict[str, str]
    tests_passing: int
    tests_total: int
    cyclomatic_complexity: float

class CodeValueAgent(ValueAgent[CodeState, 'CodeAction', float]):
    """
    Code agent that maximizes code quality.

    Value = test pass rate - complexity penalty.
    """

    def evaluate(self, state: CodeState) -> float:
        pass_rate = state.tests_passing / max(1, state.tests_total)
        complexity_penalty = 0.1 * state.cyclomatic_complexity
        return pass_rate - complexity_penalty

    def reward(self, s: CodeState, a: 'CodeAction', s_: CodeState) -> float:
        # Reward = quality improvement
        return self.evaluate(s_) - self.evaluate(s)

    def transition(self, state: CodeState, action: 'CodeAction') -> CodeState:
        # Apply code action, recompute metrics
        new_files = action.apply(state.files)
        return CodeState(
            files=new_files,
            tests_passing=self._run_tests(new_files),
            tests_total=state.tests_total,
            cyclomatic_complexity=self._compute_complexity(new_files)
        )
```

### 10.9.3 Research Agent with Knowledge Value

```python
@dataclass
class KnowledgeState:
    """State: known facts + confidence + gaps."""
    facts: set[str]
    confidence: dict[str, float]  # fact -> confidence
    gaps: set[str]  # Unknown areas

class ResearchValueAgent(ValueAgent[KnowledgeState, 'ResearchAction', float]):
    """
    Research agent that maximizes knowledge value.

    Value = total confident knowledge - gap penalty.
    """

    def evaluate(self, state: KnowledgeState) -> float:
        # Sum of confidences in known facts
        knowledge = sum(state.confidence.values())
        # Penalty for gaps
        gap_penalty = 0.5 * len(state.gaps)
        return knowledge - gap_penalty

    def reward(self, s: KnowledgeState, a: 'ResearchAction', s_: KnowledgeState) -> float:
        # Reward = knowledge gain + gap reduction
        knowledge_gain = self.evaluate(s_) - self.evaluate(s)
        gaps_closed = len(s.gaps) - len(s_.gaps)
        return knowledge_gain + 0.1 * gaps_closed

    def actions(self, state: KnowledgeState) -> list['ResearchAction']:
        # Can: investigate gap, verify fact, synthesize
        actions = []
        for gap in state.gaps:
            actions.append(InvestigateAction(gap))
        for fact in state.facts:
            if state.confidence[fact] < 0.9:
                actions.append(VerifyAction(fact))
        actions.append(SynthesizeAction())
        return actions
```

---

## 10.10 Summary

We have established:

1. **Every agent IS a value function**: Not a metaphor—structural isomorphism between agents and MDP formulations.

2. **ValueAgent formalizes this**: (S, A, V, pi, T) with Bellman consistency.

3. **PolyAgent and ValueAgent correspond**: Same structure, different emphasis. State machines that optimize.

4. **Bellman IS composition law**: Sequential, parallel, branching composition all reduce to Bellman operations.

5. **Policy extraction IS natural transformation**: From Q-functions to policies via argmax.

6. **TD error IS gradient**: Value improvement follows gradient descent on accuracy loss.

7. **Multi-agent value IS game theory**: Cooperative agents share value functions; competitive agents play minimax.

8. **Implementation pattern**: ValueAgent class with Constitution-based reward.

The Value Agent is the DP-native primitive. It replaces the question "what should my agent do?" with "what does my agent value?"—and the rest follows from optimization.

---

## 10.11 Formal Summary

**Theorem 10.11** (Value Agent Completeness)

For any agent A satisfying:
- (A1) Finite state space S
- (A2) Finite action space A
- (A3) Deterministic transitions
- (A4) Bounded rewards
- (A5) Discount factor gamma < 1

There exists a unique optimal ValueAgent formulation with:
- V* satisfying Bellman optimality
- pi* achieving V* from any state
- Composition via Bellman backup preserving optimality

**Corollary 10.12** (Categorical Structure)

Value agents form a symmetric monoidal category:
- Tensor: Parallel composition of independent agents
- Unit: Trivial agent with V = 0
- Braiding: Agent reordering (symmetric)

This category embeds into the category of polynomial functors via the PolyAgent correspondence.

---

*Previous: [Chapter 9: Open Problems and Conjectures](./09-open-problems.md)*
*Next: [Chapter 11: Meta-DP and Strange Loops](./11-meta-dp.md)*
