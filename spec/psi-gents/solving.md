# SOLVE Stage

> Reason within the metaphor space using its operations.

---

## Purpose

This is where the metaphor earns its keep. Use the metaphor's operations to derive a solution that would be harder to reach in the original problem space.

**The core question**: Given the projected problem, what does the metaphor tell us to do?

---

## Interface

```python
def solve(projection: Projection) -> MetaphorSolution:
    """
    Reason within the metaphor space to find a solution.

    Returns: MetaphorSolution with reasoning chain and conclusion.
    """
```

---

## What Makes an Operation "Executable"

In v2.0, operations were named but not executed—`_solve_in_metaphor_space()` returned stubs like "Applied symbiosis". This is the critical fix.

An operation is **executable** when:
1. It has preconditions that can be checked
2. It has effects that change the problem state
3. The LLM can reason about applying it to the projected problem

```python
@dataclass(frozen=True)
class Operation:
    name: str
    description: str
    signature: str  # e.g., "system → diagnosis" or "entity, entity → relationship"
    preconditions: tuple[str, ...]  # What must be true to apply
    effects: tuple[str, ...]  # What becomes true after applying
```

### Example: Plumbing Operations

```python
LOCATE_CONSTRICTION = Operation(
    name="locate_constriction",
    description="Find where flow is restricted in the system",
    signature="system with low flow → location of restriction",
    preconditions=(
        "system exhibits reduced flow",
        "flow was previously higher or expected to be higher"
    ),
    effects=(
        "constriction location is identified",
        "flow pattern before/after constriction is known"
    )
)

WIDEN_PIPE = Operation(
    name="widen_pipe",
    description="Increase capacity at a specific point",
    signature="location → modified system",
    preconditions=(
        "constriction location is known",
        "widening is physically possible"
    ),
    effects=(
        "flow capacity at location increases",
        "potential upstream/downstream effects"
    )
)

ADD_BYPASS = Operation(
    name="add_bypass",
    description="Create alternative flow path around blockage",
    signature="blocked location → system with bypass",
    preconditions=(
        "blockage location is known",
        "alternative route exists"
    ),
    effects=(
        "flow can route around blockage",
        "total system capacity may increase"
    )
)
```

---

## The Solving Process

### Step 1: State the Projected Problem

Establish the starting state in metaphor terms.

```python
def establish_initial_state(projection: Projection) -> dict[str, Any]:
    """Establish the problem state in metaphor terms."""

    prompt = f"""
    Projected problem: {projection.mapped_description}
    Metaphor: {projection.metaphor.name}

    What is the current state? List the conditions that are true:
    - What entities exist?
    - What relationships hold?
    - What is the problem condition?

    Format as a list of true statements in the metaphor's vocabulary.
    """

    response = llm_call(prompt)
    return {"conditions": parse_conditions(response)}
```

### Step 2: Identify Applicable Operations

Check which operations can be applied given the current state.

```python
def find_applicable_operations(
    state: dict[str, Any],
    metaphor: Metaphor
) -> list[Operation]:
    """Find operations whose preconditions are satisfied."""

    applicable = []
    conditions = set(state["conditions"])

    for op in metaphor.operations:
        # Check if preconditions are satisfied
        preconditions_met = all(
            precondition_satisfied(cond, conditions)
            for cond in op.preconditions
        )
        if preconditions_met:
            applicable.append(op)

    return applicable
```

### Step 3: Reason About Operation Application

This is the key step. The LLM reasons about what happens when operations are applied.

```python
def apply_operation(
    operation: Operation,
    state: dict[str, Any],
    projection: Projection
) -> tuple[dict[str, Any], str]:
    """Apply an operation and get new state + reasoning."""

    prompt = f"""
    Current state in {projection.metaphor.name} terms:
    {state["conditions"]}

    Applying operation: {operation.name}
    Description: {operation.description}
    Preconditions: {operation.preconditions}
    Effects: {operation.effects}

    Reason through what happens when this operation is applied:
    1. Why is this operation applicable now?
    2. What specifically happens when applied?
    3. What is the new state after application?

    Be specific to the projected problem: {projection.mapped_description}

    Format:
    REASONING: [your chain of thought]
    NEW_CONDITIONS: [list of conditions now true]
    PROGRESS: [what moved us toward the goal]
    """

    response = llm_call(prompt)
    reasoning, new_state = parse_operation_result(response)
    return new_state, reasoning
```

### Step 4: Build Solution Chain

Apply operations until reaching a solution or exhausting options.

```python
def solve(projection: Projection, max_steps: int = 5) -> MetaphorSolution:
    """Solve by applying operations in the metaphor space."""

    state = establish_initial_state(projection)
    reasoning_chain = []
    operations_applied = []

    for step in range(max_steps):
        # Find what we can do
        applicable = find_applicable_operations(state, projection.metaphor)

        if not applicable:
            reasoning_chain.append("No more applicable operations.")
            break

        # Choose best operation (could be more sophisticated)
        operation = select_best_operation(applicable, state, projection)

        # Apply it
        new_state, reasoning = apply_operation(operation, state, projection)
        reasoning_chain.append(f"Step {step + 1}: {operation.name}\n{reasoning}")
        operations_applied.append(operation.name)
        state = new_state

        # Check if we've reached a solution
        if goal_reached(state, projection):
            reasoning_chain.append("Goal reached.")
            break

    # Generate conclusion
    conclusion = synthesize_conclusion(reasoning_chain, state, projection)

    return MetaphorSolution(
        projection=projection,
        reasoning="\n\n".join(reasoning_chain),
        operations_applied=tuple(operations_applied),
        conclusion=conclusion
    )
```

---

## Operation Selection Strategies

### Greedy Selection

Choose the operation that seems most directly relevant.

```python
def select_best_operation_greedy(
    applicable: list[Operation],
    state: dict[str, Any],
    projection: Projection
) -> Operation:
    """Select operation that most directly addresses the problem."""

    prompt = f"""
    Current state: {state["conditions"]}
    Goal: Solve {projection.mapped_description}

    Available operations:
    {[(op.name, op.description) for op in applicable]}

    Which operation most directly addresses the problem?
    Consider: Which operation's effects would make the most progress?

    Answer with just the operation name.
    """

    response = llm_call(prompt, max_tokens=20)
    selected_name = response.strip()
    return next(op for op in applicable if op.name == selected_name)
```

### Means-Ends Analysis

Work backward from the goal.

```python
def select_best_operation_means_ends(
    applicable: list[Operation],
    state: dict[str, Any],
    projection: Projection
) -> Operation:
    """Select operation by means-ends analysis."""

    # Determine goal conditions
    goal = infer_goal_conditions(projection)

    # Find operation whose effects most reduce gap to goal
    best_op = None
    best_score = -1

    for op in applicable:
        # How many goal conditions would this operation satisfy?
        effects_toward_goal = sum(
            1 for effect in op.effects
            if effect_satisfies_goal(effect, goal)
        )
        if effects_toward_goal > best_score:
            best_score = effects_toward_goal
            best_op = op

    return best_op or applicable[0]
```

---

## Goal Detection

How do we know when we've solved the problem in metaphor space?

```python
def goal_reached(state: dict[str, Any], projection: Projection) -> bool:
    """Check if the metaphor-space goal is reached."""

    prompt = f"""
    Original problem: {projection.problem.description}
    Projected problem: {projection.mapped_description}

    Current state in metaphor terms:
    {state["conditions"]}

    Has the problem been solved in metaphor terms?
    - Is the undesirable condition resolved?
    - Is a solution path identified?

    Answer: SOLVED or NOT_SOLVED, then brief explanation.
    """

    response = llm_call(prompt, max_tokens=50)
    return "SOLVED" in response.upper()
```

---

## Synthesizing Conclusions

Turn the operation chain into a coherent conclusion.

```python
def synthesize_conclusion(
    reasoning_chain: list[str],
    final_state: dict[str, Any],
    projection: Projection
) -> str:
    """Synthesize operations into a conclusion in metaphor terms."""

    prompt = f"""
    Problem in {projection.metaphor.name} terms: {projection.mapped_description}

    Reasoning chain:
    {reasoning_chain}

    Final state:
    {final_state["conditions"]}

    Synthesize this into a clear conclusion:
    - What is the answer in metaphor terms?
    - What is the key insight the metaphor revealed?
    - What action does this recommend?

    Keep it in the metaphor's vocabulary (translation comes later).
    """

    return llm_call(prompt)
```

---

## Example: Full Solve

**Projection** (from previous stages):
```
Problem: "API is slow, caching didn't help"
Metaphor: Plumbing
Mapped: "Pipe system has low flow rate, reservoir was ineffective"
```

**Step 1 - Initial State**:
```
Conditions:
- pipe_system exists
- flow_rate is LOW
- reservoir was added
- reservoir did not improve flow
- consumers (users) are downstream
```

**Step 2 - Applicable Operations**:
- `locate_constriction` ✓ (flow is low)
- `widen_pipe` ✗ (constriction location not known)
- `add_bypass` ✗ (blockage location not known)

**Step 3 - Apply `locate_constriction`**:
```
REASONING: Flow is low despite reservoir. Reservoir buffers demand spikes
but doesn't address capacity issues. The constriction must be upstream
of where the reservoir was placed. We need to trace back to find where
flow is restricted.

In plumbing terms: walk upstream from the reservoir until we find where
pressure drops or flow narrows.

NEW_CONDITIONS:
- constriction is upstream of reservoir
- flow measurement needed at multiple points
- diagnostic operation recommended

PROGRESS: We now know where to look (upstream of cache/reservoir).
```

**Step 4 - Now `widen_pipe` is applicable**:
```
(Actually, we need more diagnosis first. Let's say the operation
"diagnose_flow_point" is available.)

REASONING: To widen the pipe, we need to know exactly where.
Measure flow at: source (incoming requests), after first processing,
after second processing, at reservoir, at consumers.
The largest drop indicates the constriction.

NEW_CONDITIONS:
- flow measurements at each stage are available
- constriction located at "second processing" stage
- widening is possible at that point

PROGRESS: Bottleneck identified. Can now decide: widen or bypass.
```

**Conclusion**:
```
In plumbing terms: The constriction is at the "second processing"
junction, upstream of the reservoir. The reservoir (cache) couldn't
help because flow was already restricted before reaching it.

Recommendation: Widen the pipe at "second processing" stage.
If widening isn't possible, add a bypass around that junction.
```

---

## Handling Operation Failure

What if an operation can't complete?

```python
def apply_operation_with_fallback(
    operation: Operation,
    state: dict[str, Any],
    projection: Projection
) -> tuple[dict[str, Any], str, bool]:
    """Apply operation with fallback on failure."""

    new_state, reasoning = apply_operation(operation, state, projection)

    # Check if operation actually succeeded
    success = operation_succeeded(operation, state, new_state)

    if not success:
        reasoning += "\n\nOperation failed to produce expected effects."
        # State may be partially modified
        return state, reasoning, False

    return new_state, reasoning, True
```

---

## Operation Traces for N-gent

Log each operation for forensics:

```python
@dataclass
class OperationTrace:
    operation: str
    state_before: dict[str, Any]
    state_after: dict[str, Any]
    reasoning: str
    success: bool
    timestamp: datetime

def trace_operation(
    operation: Operation,
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    reasoning: str,
    success: bool
) -> OperationTrace:
    """Create trace for N-gent logging."""
    return OperationTrace(
        operation=operation.name,
        state_before=state_before,
        state_after=state_after,
        reasoning=reasoning,
        success=success,
        timestamp=datetime.now()
    )
```

---

## Comparison with v2.0

| v2.0 | v3.0 |
|------|------|
| `_solve_in_metaphor_space` returns stub strings | Full reasoning chain with state tracking |
| Operations are named only | Operations have preconditions and effects |
| No state tracking | Explicit state before/after each operation |
| No goal detection | Goal detection drives termination |
| Single "solution" return | MetaphorSolution with full trace |

---

## Metrics

| Metric | Description |
|--------|-------------|
| `solve_time_ms` | Time to complete solve stage |
| `operations_applied` | Number of operations used |
| `operations_available` | Operations that were applicable |
| `goal_reached` | Did solving reach a goal state? |
| `reasoning_length` | Token count of reasoning chain |

---

*Solving is where metaphors prove their worth. An operation that changes nothing isn't an operation—it's decoration.*
