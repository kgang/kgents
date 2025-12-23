# Chapter 8: kgents Instantiation

> *"Theory without practice is empty; practice without theory is blind."*
> — Kant (adapted)

---

## 8.1 From Theory to Code

This chapter grounds our categorical theory in the kgents codebase. We show how abstract structures—categories, monads, operads, sheaves—manifest in concrete Python code.

The relationship is **bidirectional**:
- Theory motivates code design: categorical structures suggest what to build
- Code validates theory: implementation tests whether abstractions work

This is not merely "applying theory to code." The code is an **algebra** for the theory—a concrete instantiation that must satisfy the abstract laws.

---

## 8.2 PolyAgent: The State Polynomial

### 8.2.1 Theoretical Background

Recall from Chapter 3: reasoning with state lives in a Kleisli category for the State monad.

More generally, **polynomial functors** capture state-dependent behavior:

```
P(X) = Σ_{s ∈ S} X^{A_s} × B_s
```

Where:
- S is the set of states
- A_s is the input type in state s
- B_s is the output type in state s

This says: depending on state s, accept input A_s and produce output B_s.

### 8.2.2 kgents Implementation

```python
# From impl/claude/agents/poly_agent.py (conceptual)
from typing import TypeVar, Generic

S = TypeVar('S')  # State type
A = TypeVar('A')  # Input type
B = TypeVar('B')  # Output type

class PolyAgent(Generic[S, A, B]):
    """
    A polynomial agent with state-dependent behavior.

    Categorical interpretation:
    - Objects: States S
    - Morphisms: State transitions induced by inputs
    - This IS a Kleisli category for State monad
    """

    def __init__(self, initial_state: S):
        self.state = initial_state

    def input_type(self, state: S) -> type:
        """What input type is expected in this state?"""
        # Polymorphic: different states accept different inputs
        ...

    def step(self, input: A) -> B:
        """Process input, update state, return output."""
        # This is a Kleisli morphism: A → (B, S)
        output, new_state = self._transition(self.state, input)
        self.state = new_state
        return output

    def _transition(self, state: S, input: A) -> tuple[B, S]:
        """The core state transition function."""
        raise NotImplementedError
```

### 8.2.3 Categorical Laws

**Identity law**: `step` with no-op input should leave state unchanged:
```python
assert agent.step(no_op_input) preserves agent.state
```

**Composition**: Sequential steps compose correctly:
```python
# (f >> g)(x) = g(f(x))
result_1 = agent.step(input_1)
result_2 = agent.step(input_2)
# Combined effect = effect of chained transitions
```

**kgents verifies these laws in tests.**

### 8.2.4 Example: Soul Mode Agent

```python
class SoulModes(Enum):
    AWAKE = "awake"
    DREAMING = "dreaming"
    REFLECTING = "reflecting"

class SoulAgent(PolyAgent[SoulModes, Query, Response]):
    """
    K-gent's soul with mode-dependent reasoning.

    State polynomial:
    - AWAKE: accepts dialogue queries, returns responses
    - DREAMING: accepts nothing, generates insights
    - REFLECTING: accepts feedback, returns meta-responses
    """

    def _transition(self, state: SoulModes, input: Query) -> tuple[Response, SoulModes]:
        match state:
            case SoulModes.AWAKE:
                response = self.dialogue(input)
                next_state = self._decide_next_state(response)
                return (response, next_state)
            case SoulModes.DREAMING:
                insight = self.dream()
                return (insight, SoulModes.AWAKE)
            case SoulModes.REFLECTING:
                meta = self.reflect(input)
                return (meta, SoulModes.AWAKE)
```

The polynomial structure is explicit: each state has its own input/output behavior.

---

## 8.3 Operad: The Grammar of Composition

### 8.3.1 Theoretical Background

Recall from Chapter 4: operads capture multi-input operations and their composition.

An operad O has:
- Operations O(n) of each arity
- Composition: substitute operations
- Identity: the 1-ary identity

### 8.3.2 kgents Implementation

```python
# From impl/claude/agents/operad.py (conceptual)
from dataclasses import dataclass
from typing import List, Callable, Any

@dataclass
class Operation:
    """An n-ary operation in the operad."""
    name: str
    arity: int
    action: Callable[[List[Any]], Any]

class Operad:
    """
    A collection of operations with composition.

    Categorical interpretation:
    - Operations = multi-input morphisms
    - Composition = plugging outputs into inputs
    - This encodes the "grammar" of valid compositions
    """

    def __init__(self, name: str):
        self.name = name
        self.operations: dict[str, Operation] = {}
        self.laws: list[Law] = []

    def register(self, op: Operation):
        """Add an operation to the operad."""
        self.operations[op.name] = op

    def compose(self, outer: Operation, *inner: Operation) -> Operation:
        """
        Operadic composition: plug inner operations into outer.

        outer ∈ O(n), inner_i ∈ O(k_i)
        → composed ∈ O(k_1 + ... + k_n)
        """
        assert outer.arity == len(inner)

        total_arity = sum(op.arity for op in inner)

        def composed_action(inputs: List[Any]) -> Any:
            # Partition inputs for each inner operation
            cursor = 0
            inner_outputs = []
            for op in inner:
                op_inputs = inputs[cursor:cursor + op.arity]
                inner_outputs.append(op.action(op_inputs))
                cursor += op.arity
            # Apply outer to inner outputs
            return outer.action(inner_outputs)

        return Operation(
            name=f"{outer.name}({','.join(op.name for op in inner)})",
            arity=total_arity,
            action=composed_action
        )

    def verify_laws(self, algebra: 'OparadAlgebra') -> bool:
        """Check if an algebra satisfies operad laws."""
        for law in self.laws:
            if not law.check(algebra):
                return False
        return True
```

### 8.3.3 Example: Town Operad

```python
# The operad for Agent Town reasoning
TOWN_OPERAD = Operad("Town")

# Unary operations
TOWN_OPERAD.register(Operation(
    name="deliberate",
    arity=1,
    action=lambda args: args[0].reason()  # Single citizen deliberates
))

# Binary operations
TOWN_OPERAD.register(Operation(
    name="debate",
    arity=2,
    action=lambda args: Debate(args[0], args[1]).resolve()  # Two citizens debate
))

# N-ary operations
TOWN_OPERAD.register(Operation(
    name="vote",
    arity=-1,  # Variable arity
    action=lambda args: majority_vote([a.opinion for a in args])
))

# Composition example:
# debate(deliberate(A), deliberate(B)) = A and B each think, then debate
composed = TOWN_OPERAD.compose(
    TOWN_OPERAD.operations["debate"],
    TOWN_OPERAD.operations["deliberate"],
    TOWN_OPERAD.operations["deliberate"]
)
```

### 8.3.4 Operad Laws in Code

**Associativity law**:
```python
# (f ∘ g) ∘ h = f ∘ (g ∘ h)
left = operad.compose(operad.compose(f, g), h)
right = operad.compose(f, operad.compose(g, h))
assert left.action(inputs) == right.action(inputs)
```

**Identity law**:
```python
identity = Operation("id", arity=1, action=lambda x: x[0])
# f ∘ id = f = id ∘ f
assert operad.compose(f, identity).action(inputs) == f.action(inputs)
```

---

## 8.4 Sheaf: Local-to-Global Coherence

### 8.4.1 Theoretical Background

Recall from Chapter 5: sheaves manage local-to-global coherence.

Key operations:
- Restriction: Global → Local
- Compatibility: Do locals agree on overlaps?
- Gluing: Compatible locals → Global

### 8.4.2 kgents Implementation

```python
# From impl/claude/services/town/sheaf.py (conceptual)
from typing import Set, Dict, Optional

class TownSheaf:
    """
    Sheaf over the space of agent subsets.

    Categorical interpretation:
    - Open sets = subsets of agents
    - Sections = beliefs held by a subset
    - Restriction = projecting beliefs to shared domain
    - Gluing = combining compatible beliefs
    """

    def __init__(self, agents: Set['Agent']):
        self.agents = agents
        self.sections: Dict[frozenset, 'Belief'] = {}

    def set_section(self, subset: Set['Agent'], belief: 'Belief'):
        """Assign a belief to an agent subset."""
        self.sections[frozenset(subset)] = belief

    def restrict(self, belief: 'Belief',
                 from_subset: Set['Agent'],
                 to_subset: Set['Agent']) -> 'Belief':
        """Restrict a belief to a smaller subset."""
        assert to_subset <= from_subset
        shared_domain = self._shared_domain(from_subset, to_subset)
        return belief.project_to(shared_domain)

    def compatible(self, sections: Dict[frozenset, 'Belief']) -> bool:
        """Check if local sections can glue."""
        for (s1, b1), (s2, b2) in itertools.combinations(sections.items(), 2):
            overlap = s1 & s2
            if overlap:
                r1 = self.restrict(b1, set(s1), set(overlap))
                r2 = self.restrict(b2, set(s2), set(overlap))
                if r1 != r2:
                    return False
        return True

    def glue(self, sections: Dict[frozenset, 'Belief']) -> Optional['Belief']:
        """Glue compatible local beliefs into global."""
        if not self.compatible(sections):
            return None  # Sheaf condition fails

        # Construct global belief
        global_belief = Belief.empty()
        for subset, belief in sections.items():
            global_belief = global_belief.merge(belief)
        return global_belief

    def consensus(self, query: 'Query') -> 'Belief':
        """Get agent consensus via sheaf gluing."""
        # Each agent produces local section
        sections = {}
        for agent in self.agents:
            sections[frozenset([agent])] = agent.reason(query)

        # Try to glue
        global_belief = self.glue(sections)

        if global_belief is None:
            # Sheaf condition fails - use dialectic
            return self.dialectic_resolve(sections)

        return global_belief
```

### 8.4.3 Self-Consistency via Sheaf

```python
class SelfConsistencySheaf(TownSheaf):
    """
    Self-consistency as sheaf gluing over reasoning paths.
    """

    def sample_chains(self, problem: str, n: int) -> Dict[int, str]:
        """Sample n reasoning chains."""
        chains = {}
        for i in range(n):
            chains[i] = self.llm.generate_cot(problem)
        return chains

    def extract_answer(self, chain: str) -> str:
        """Extract final answer from chain."""
        return self.parser.get_answer(chain)

    def check_consistency(self, chains: Dict[int, str]) -> float:
        """Compute consistency score (sheaf condition approximation)."""
        answers = [self.extract_answer(c) for c in chains.values()]
        most_common = Counter(answers).most_common(1)[0]
        return most_common[1] / len(answers)

    def decode(self, problem: str, n: int = 10) -> tuple[str, float]:
        """Self-consistency decoding."""
        chains = self.sample_chains(problem, n)

        # Group by answer (defining "compatibility" as same answer)
        by_answer = defaultdict(list)
        for i, chain in chains.items():
            answer = self.extract_answer(chain)
            by_answer[answer].append(chain)

        # Most common answer = glued section
        best_answer = max(by_answer, key=lambda a: len(by_answer[a]))
        confidence = len(by_answer[best_answer]) / n

        return best_answer, confidence
```

---

## 8.5 Witness: Reasoning Traces as Morphisms

### 8.5.1 Theoretical Background

The Witness system records reasoning traces—sequences of marks that form a morphism chain:

```
State₀ --[mark₁]--> State₁ --[mark₂]--> State₂ --[mark₃]--> State₃
```

This is Kleisli composition in the Writer monad: each mark is a traced inference.

### 8.5.2 kgents Implementation

```python
# From impl/claude/services/witness/ (conceptual)
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Mark:
    """
    A reasoning mark - one inference step.

    Categorical interpretation:
    - A morphism in the reasoning category
    - Carries trace information (Writer monad)
    """
    id: str
    timestamp: datetime
    action: str
    reasoning: str
    principles: List[str]
    parent_id: Optional[str] = None  # For composition

class Witness:
    """
    The Witness service records reasoning as morphism chains.

    Categorical interpretation:
    - Witness IS a Kleisli category for Writer(MarkLog)
    - mark() creates a morphism
    - Chains of marks are composed morphisms
    """

    def __init__(self, storage: 'StorageProvider'):
        self.storage = storage
        self.current_chain: List[Mark] = []

    async def mark(
        self,
        action: str,
        reasoning: str,
        principles: List[str] = None
    ) -> Mark:
        """
        Create a mark - record one reasoning step.

        This is: A → Writer(B, MarkLog)
        """
        parent = self.current_chain[-1] if self.current_chain else None

        mark = Mark(
            id=generate_id(),
            timestamp=datetime.now(),
            action=action,
            reasoning=reasoning,
            principles=principles or [],
            parent_id=parent.id if parent else None
        )

        await self.storage.save_mark(mark)
        self.current_chain.append(mark)

        return mark

    def get_chain(self) -> List[Mark]:
        """Get the current reasoning chain (composed morphism)."""
        return self.current_chain

    def verify_chain(self) -> bool:
        """Verify the chain satisfies reasoning laws."""
        for i in range(1, len(self.current_chain)):
            prev = self.current_chain[i-1]
            curr = self.current_chain[i]
            # Check composition: curr's parent should be prev
            if curr.parent_id != prev.id:
                return False
        return True
```

### 8.5.3 Witnessing as Functor

The Witness creates a **functor** from reasoning to persistence:

```python
# Functor: Reason → Storage
#
# Objects: Reasoning states → Database records
# Morphisms: Inference steps → Mark records
# Composition: Chain → Linked list of marks

class WitnessFunctor:
    """The functor from reasoning to storage."""

    def map_object(self, state: ReasoningState) -> StorageRecord:
        """Send a reasoning state to its storage representation."""
        return self.storage.encode(state)

    def map_morphism(self, step: InferenceStep) -> Mark:
        """Send an inference step to its mark representation."""
        return Mark(
            action=step.description,
            reasoning=step.justification,
            principles=step.applicable_laws
        )

    def preserve_composition(self, chain: List[InferenceStep]) -> List[Mark]:
        """Map a chain, preserving composition."""
        marks = [self.map_morphism(step) for step in chain]
        # Link marks to preserve composition
        for i in range(1, len(marks)):
            marks[i].parent_id = marks[i-1].id
        return marks
```

---

## 8.6 AGENTESE: The Typed Reasoning Language

### 8.6.1 Theoretical Background

AGENTESE paths encode typed reasoning actions:

```
world.problem.decompose >> concept.solution.synthesize >> self.belief.update
```

This is a **typed morphism chain** in a category where:
- Objects are typed (world, concept, self, time, void)
- Morphisms are path-encoded operations
- Composition is `>>` chaining

### 8.6.2 kgents Implementation

```python
# From impl/claude/protocols/agentese/ (conceptual)
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class AGENTESEPath:
    """
    A path in AGENTESE.

    Categorical interpretation:
    - context.entity.action encodes a typed morphism
    - >> is composition
    - Paths are elements of a free category
    """
    context: str   # world, self, concept, time, void
    entity: str    # The noun
    action: str    # The verb

    def __rshift__(self, other: 'AGENTESEPath') -> 'AGENTESEChain':
        """Composition via >>"""
        return AGENTESEChain([self, other])

class AGENTESEChain:
    """A composed sequence of paths."""

    def __init__(self, paths: list[AGENTESEPath]):
        self.paths = paths

    def __rshift__(self, other: AGENTESEPath) -> 'AGENTESEChain':
        return AGENTESEChain(self.paths + [other])

class Logos:
    """
    The AGENTESE interpreter.

    Categorical interpretation:
    - Logos provides an algebra for the AGENTESE operad
    - invoke() evaluates an operadic term
    """

    def __init__(self):
        self.nodes: Dict[str, 'Node'] = {}

    def register(self, path: str, node: 'Node'):
        """Register a node at a path."""
        self.nodes[path] = node

    async def invoke(
        self,
        path: str,
        observer: 'Umwelt',
        **kwargs
    ) -> Any:
        """
        Invoke a path with an observer.

        Categorical interpretation:
        - path encodes a morphism
        - observer provides the evaluation context
        - Return is the morphism's codomain value
        """
        node = self.nodes.get(path)
        if node is None:
            raise PathNotFoundError(path)

        return await node.execute(observer, **kwargs)

    async def invoke_chain(
        self,
        chain: AGENTESEChain,
        observer: 'Umwelt',
        **kwargs
    ) -> Any:
        """Invoke a composed chain."""
        result = None
        for path in chain.paths:
            result = await self.invoke(
                f"{path.context}.{path.entity}.{path.action}",
                observer,
                previous_result=result,
                **kwargs
            )
        return result
```

### 8.6.3 Type Checking as Law Verification

```python
class AGENTESETypeChecker:
    """
    Type checking for AGENTESE paths.

    Categorical interpretation:
    - Types are objects
    - Valid paths have matching source/target types
    - Type checking verifies morphism composition is valid
    """

    def check_path(self, path: AGENTESEPath) -> bool:
        """Check a single path is well-typed."""
        # Each context has valid entities
        valid_entities = self.context_entities.get(path.context, set())
        if path.entity not in valid_entities:
            return False

        # Each entity has valid actions
        valid_actions = self.entity_actions.get(path.entity, set())
        if path.action not in valid_actions:
            return False

        return True

    def check_chain(self, chain: AGENTESEChain) -> bool:
        """Check a chain is well-typed (composition valid)."""
        for i in range(len(chain.paths) - 1):
            current = chain.paths[i]
            next_path = chain.paths[i + 1]

            # Output type of current must match input type of next
            output_type = self.get_output_type(current)
            input_type = self.get_input_type(next_path)

            if not self.types_compatible(output_type, input_type):
                return False

        return True
```

---

## 8.7 The Dialectic: Cocone Construction

### 8.7.1 Theoretical Background

When beliefs don't glue (sheaf condition fails), we construct a cocone:

```
       Synthesis
       ╱       ╲
      ╱         ╲
Kent's view   Claude's view
```

The synthesis doesn't eliminate disagreement—it provides a vantage from which both views are visible.

### 8.7.2 kgents Implementation

```python
# From impl/claude/services/witness/dialectic.py (conceptual)
@dataclass
class View:
    """A perspective/belief."""
    content: str
    reasoning: str
    confidence: float

@dataclass
class Synthesis:
    """
    A cocone over disagreeing views.

    Categorical interpretation:
    - The apex of a cocone diagram
    - Each original view has a morphism into Synthesis
    - Synthesis is universal: any other cocone factors through it
    """
    kent_view: View
    claude_view: View
    kent_projection: str  # How Kent's view fits
    claude_projection: str  # How Claude's view fits
    synthesis: str  # The unified understanding
    remaining_tension: Optional[str]  # What couldn't be resolved

class DialecticEngine:
    """
    Constructs cocones over disagreeing views.
    """

    async def fuse(
        self,
        kent_view: View,
        claude_view: View
    ) -> Synthesis:
        """
        Dialectical fusion: construct cocone.

        Categorical interpretation:
        - We're computing a colimit over {Kent, Claude}
        - The result is universal: it captures all that both views share
        """

        # Find common ground (what both views agree on)
        common = await self._find_agreement(kent_view, claude_view)

        # Identify tensions (where they disagree)
        tensions = await self._find_tensions(kent_view, claude_view)

        # Construct synthesis (cocone apex)
        synthesis_text = await self._synthesize(
            common=common,
            tensions=tensions,
            kent_view=kent_view,
            claude_view=claude_view
        )

        return Synthesis(
            kent_view=kent_view,
            claude_view=claude_view,
            kent_projection=await self._explain_fit(kent_view, synthesis_text),
            claude_projection=await self._explain_fit(claude_view, synthesis_text),
            synthesis=synthesis_text,
            remaining_tension=tensions if not await self._fully_resolved(tensions) else None
        )
```

---

## 8.8 Validation: Theory Meets Tests

### 8.8.1 Testing Categorical Laws

```python
# From tests/categorical_laws.py (conceptual)

class TestPolyAgentLaws:
    """Test that PolyAgent satisfies categorical laws."""

    def test_identity_law(self, agent: PolyAgent):
        """Identity: step(noop) preserves state."""
        initial_state = agent.state
        agent.step(NoOpInput())
        assert agent.state == initial_state

    def test_composition_associativity(self, agent: PolyAgent):
        """(f >> g) >> h = f >> (g >> h)"""
        # Run (f >> g) >> h
        agent_1 = deepcopy(agent)
        agent_1.step(input_f)
        agent_1.step(input_g)
        agent_1.step(input_h)

        # Run f >> (g >> h)
        agent_2 = deepcopy(agent)
        agent_2.step(input_f)
        intermediate = agent_2.state
        agent_2.step(input_g)
        agent_2.step(input_h)

        assert agent_1.state == agent_2.state

class TestOperadLaws:
    """Test that Operad satisfies operadic laws."""

    def test_identity(self, operad: Operad):
        """f ∘ id = f = id ∘ f"""
        f = operad.operations["test_op"]
        identity = operad.identity

        left = operad.compose(f, identity)
        right = operad.compose(identity, f)

        test_input = [1, 2, 3]
        assert left.action(test_input) == f.action(test_input)
        assert right.action(test_input) == f.action(test_input)

    def test_associativity(self, operad: Operad):
        """(f ∘ g) ∘ h = f ∘ (g ∘ h)"""
        f, g, h = [operad.operations[n] for n in ["f", "g", "h"]]

        left = operad.compose(operad.compose(f, g), h)
        right = operad.compose(f, operad.compose(g, h))

        test_input = list(range(left.arity))
        assert left.action(test_input) == right.action(test_input)

class TestSheafLaws:
    """Test sheaf gluing properties."""

    def test_locality(self, sheaf: TownSheaf):
        """If sections agree everywhere, they're equal."""
        s1 = sheaf.sections[frozenset({"A", "B"})]
        s2 = sheaf.sections[frozenset({"A", "B"})]

        # If restrictions to all covers agree...
        for cover in sheaf.covers({"A", "B"}):
            r1 = sheaf.restrict(s1, {"A", "B"}, cover)
            r2 = sheaf.restrict(s2, {"A", "B"}, cover)
            assert r1 == r2

        # ...then sections are equal
        assert s1 == s2

    def test_gluing(self, sheaf: TownSheaf):
        """Compatible sections glue uniquely."""
        sections = {
            frozenset({"A"}): belief_a,
            frozenset({"B"}): belief_b,
        }

        if sheaf.compatible(sections):
            glued = sheaf.glue(sections)

            # Glued section restricts to originals
            assert sheaf.restrict(glued, {"A", "B"}, {"A"}) == belief_a
            assert sheaf.restrict(glued, {"A", "B"}, {"B"}) == belief_b
```

---

## 8.9 Summary: The Implementation Pattern

| Theory | kgents Implementation |
|--------|----------------------|
| Category | Module with objects & functions |
| Morphism | Function / method call |
| Composition | Method chaining, `>>` operator |
| Monad | PolyAgent state threading |
| Operad | Operad class with compose() |
| Sheaf | TownSheaf with glue() |
| Kleisli | Witness mark chains |
| Functor | Type-preserving mappings |

**The bidirectional relationship**:
- Theory tells us what to build (categorical structure)
- Code tells us if theory works (tests pass)
- Failures reveal where theory needs refinement or where code has bugs

This is not "applied category theory"—it's **validated category theory**. The code is a proof that the theory works.

---

*Previous: [Chapter 7: The Neurosymbolic Bridge](./07-neurosymbolic-bridge.md)*
*Next: [Chapter 9: Open Problems and Conjectures](./09-open-problems.md)*
