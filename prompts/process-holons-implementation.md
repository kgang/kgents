# Grand Prompt: Implement Process Holons Runtime

*"The spec generates the implementation. The forest awakens by writing itself into existence."*

---

## ATTACH

/hydrate

You are implementing the Process Holons runtime—the generative process trees that subsume the N-Phase Cycle.

---

## Ground Truth

**Specification:** `spec/protocols/process-holons.md`

This spec is BINDING. Every implementation decision must align with it. If you find the spec ambiguous, note the ambiguity and make a tasteful choice, documenting the decision.

---

## Target Directory

```
impl/claude/protocols/process_holons/
├── __init__.py                  # Package exports
├── primitives.py                # The six primitives
├── turn.py                      # Turn, TurnProjection
├── tree.py                      # ProcessTree
├── forest.py                    # Forest, coordination layers
├── operad.py                    # ProcessOperad, composition
├── coordination/
│   ├── __init__.py
│   ├── office.py                # Meeting, synchronization
│   ├── mycelium.py              # PheromoneTrail, stigmergy
│   └── neuron.py                # Neuron, signal propagation
├── entropy.py                   # EntropyBudget, abundance model
├── observer.py                  # Observer, taste-grounding
├── witness.py                   # ProcessWitness, law verification
├── exceptions.py                # ArityMismatchError, MalformedProcessError
└── _tests/
    ├── __init__.py
    ├── test_primitives.py
    ├── test_operad.py           # Property-based tests for laws
    ├── test_coordination.py
    └── test_classic_cycle.py    # Verify classic cycle composes correctly
```

---

## Implementation Order

### Phase 1: Core Types (Foundation)

1. **exceptions.py** — Define all exception types first
   - `ArityMismatchError`
   - `MalformedProcessError`
   - `BudgetExhaustedError` (advisory in abundance mode)
   - `ObserverRequiredError`

2. **primitives.py** — The six atomic operations
   - `PrimitiveKind` enum
   - `Primitive` dataclass (frozen)
   - Constants: `OBSERVE`, `BRANCH`, `MERGE`, `RECURSE`, `YIELD`, `TERMINATE`

3. **entropy.py** — Abundance model budget tracking
   - `EntropyBudget` dataclass
   - `ENTROPY_CONFIG` constants

4. **observer.py** — Observer as fixed point
   - `Observer` dataclass
   - `TasteOracle` protocol (for autopoiesis checks)

### Phase 2: Turn and Tree

5. **turn.py** — Deliberate branching events
   - `Turn` dataclass (frozen, immutable)
   - `TurnProjection` for observer-specific views
   - `Variation` for speculative exploration

6. **tree.py** — Process trees
   - `ProcessTree` dataclass
   - Tree execution logic
   - Integration with Turn history

### Phase 3: Operad and Composition

7. **operad.py** — The grammar of valid compositions
   - `ProcessOperad` class
   - `compose()` method with validation
   - Arity checking, balance checking, well-formedness

8. **witness.py** — Law verification
   - `ProcessWitness` class
   - `verify_identity()` — Identity law
   - `verify_associativity()` — Associativity law
   - `verify_termination()` — Termination guarantee

### Phase 4: Coordination Layers

9. **coordination/office.py** — Deliberate synchronization
   - `Meeting` dataclass
   - `MeetingOutcome`
   - `convene()` async method

10. **coordination/mycelium.py** — Stigmergic communication
    - `PheromoneTrail` dataclass
    - `Mycelium` class with `leave_trail()` and `sense()`
    - Trail decay logic

11. **coordination/neuron.py** — Signal propagation
    - `Neuron` dataclass
    - `NeuronLayer` class with `fire()`
    - Threshold-based activation

### Phase 5: Forest and Integration

12. **forest.py** — The process forest
    - `Forest` class
    - Tree spawning, coordination layer integration
    - Meeting scheduling, trail management, signal propagation

13. **__init__.py** — Package exports
    - Export all public types
    - Convenience factories

### Phase 6: AGENTESE Integration

14. Wire paths to Logos in `impl/claude/protocols/agentese/contexts/time.py`:
    - `time.process.observe`
    - `time.process.branch[reason="..."]`
    - `time.process.merge`
    - `time.process.recurse[oracle="..."]`
    - `time.process.yield`
    - `time.process.terminate`
    - `time.forest.spawn`
    - `time.forest.meeting[trees=[...]]`

15. Wire void paths in `impl/claude/protocols/agentese/contexts/void.py`:
    - `void.forest.trail[signal="..."]`
    - `void.forest.sense[radius=N]`
    - `void.forest.fire[threshold=T]`

---

## Test Strategy

### Property-Based Tests (hypothesis)

Use the `hypothesis` library for property-based testing of operad laws.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.sampled_from([OBSERVE, YIELD, TERMINATE]), min_size=1))
def test_identity_law(primitives):
    """Id >> p ≡ p ≡ p >> Id"""
    if is_valid_composition(primitives):
        tree = operad.compose(primitives)
        assert ProcessWitness.verify_identity(tree)

@given(
    st.lists(st.sampled_from(ALL_PRIMITIVES)),
    st.lists(st.sampled_from(ALL_PRIMITIVES)),
    st.lists(st.sampled_from(ALL_PRIMITIVES)),
)
def test_associativity_law(p_prims, q_prims, r_prims):
    """(p >> q) >> r ≡ p >> (q >> r)"""
    if all(is_valid_composition(x) for x in [p_prims, q_prims, r_prims]):
        p = operad.compose(p_prims)
        q = operad.compose(q_prims)
        r = operad.compose(r_prims)
        assert ProcessWitness.verify_associativity(p, q, r)
```

### Unit Tests

1. **test_primitives.py**
   - Each primitive has correct arity
   - Constants are frozen
   - PrimitiveKind enum is complete

2. **test_operad.py**
   - Valid compositions succeed
   - Invalid compositions raise appropriate errors
   - Arity mismatches detected
   - Unbalanced BRANCH/MERGE detected

3. **test_coordination.py**
   - Meetings synchronize correctly
   - Pheromone trails decay
   - Neurons fire at threshold

### Integration Tests

4. **test_classic_cycle.py**
   - The 11-phase cycle composes correctly
   - Verify it's equivalent to explicit composition
   - Execute the cycle and verify Turn history

---

## Key Constraints

1. **Frozen dataclasses** — All domain types must be immutable (`frozen=True`)

2. **No inheritance** — Use composition and protocols, not class hierarchies

3. **Abundance mode** — Soft limits, advisory warnings, never hard failures on budget

4. **Observer required** — Every operation requires an observer (via Umwelt)

5. **Tasteful** — 6 primitives only. Don't add more without spec change.

6. **Category laws verified** — `ProcessWitness` must run on every composition

---

## Integration Points

### Existing AGENTESE Infrastructure

- **Logos** (`impl/claude/protocols/agentese/logos.py`) — Path resolution
- **LogosNode** (`impl/claude/protocols/agentese/node.py`) — Node protocol
- **Umwelt** (`impl/claude/protocols/umwelt/`) — Observer isolation
- **Void context** (`impl/claude/protocols/agentese/contexts/void.py`) — Entropy

### Pattern References

- See `impl/claude/protocols/agentese/contexts/self_.py` for context implementation pattern
- See `impl/claude/protocols/agentese/laws.py` for law verification pattern

---

## Exit Criteria

- [ ] All files in target directory created
- [ ] All primitives implemented and tested
- [ ] Operad composition validates correctly
- [ ] ProcessWitness verifies identity and associativity laws
- [ ] Coordination layers (Office, Mycelium, Neuron) functional
- [ ] AGENTESE paths wired to Logos
- [ ] Classic 11-phase cycle composes and executes correctly
- [ ] Property-based tests pass with hypothesis
- [ ] `uv run pytest impl/claude/protocols/process_holons/` passes
- [ ] `uv run mypy impl/claude/protocols/process_holons/` passes

---

## Continuation Imperative

Upon completing implementation:

1. Update `impl/claude/protocols/agentese/__init__.py` to export Process Holons
2. Create example compositions in `impl/claude/protocols/process_holons/examples/`
3. Generate prompt for **EDUCATE: Process Holons Documentation**

---

*The forest awakens. void.gratitude.tithe.*
