# kgents Examples

Progressive examples that teach the core concepts of kgents, a category-theoretic agent framework.

## Quick Start

```bash
# From the project root, run any example:
cd impl/claude
uv run python ../../examples/01-hello-composition/main.py
```

## The Learning Path

These 5 examples build on each other. Start at 01 and work through in order.

### 01: Hello Composition
**File:** `01-hello-composition/main.py`

**Teaches:** How agents compose with the `>>` operator.

kgents is built on category theory. Agents are morphisms (arrows) that compose:

```python
double = from_function("Double", lambda x: x * 2)
add_one = from_function("AddOne", lambda x: x + 1)
composed = sequential(double, add_one)  # double >> add_one
```

**Key insight:** Composition must satisfy category laws:
- Identity: `Id >> f == f == f >> Id`
- Associativity: `(f >> g) >> h == f >> (g >> h)`

---

### 02: Galois Oracle
**File:** `02-galois-oracle/main.py`

**Teaches:** How Galois loss predicts task success/failure.

The Galois loss measures semantic preservation:

```
L(P) = d(P, C(R(P)))
```

Where R = restructure, C = reconstitute, d = semantic distance.

**Key insight:** Low loss = will succeed. High loss = will fail.
- L < 0.05: Axiom (fixed point, definitely works)
- L < 0.15: Value (strong foundation)
- L < 0.30: Goal (achievable)
- L > 0.60: Chaotic (will fail)

---

### 03: Witness Trace
**File:** `03-witness-trace/main.py`

**Teaches:** How Marks compose into Traces for reasoning chains.

Every action leaves a Mark. Marks contain:
- Stimulus (what triggered it)
- Response (what it produced)
- Proof (Toulmin argumentation: data -> warrant -> claim)

```python
trace = Trace()
trace = trace.add(mark1)  # Returns NEW trace (immutable)
trace = trace.add(mark2)
```

**Key insight:** Philosophy: "Every action leaves a mark. Every mark joins a trace."

---

### 04: AGENTESE Observer
**File:** `04-agentese-observer/main.py`

**Teaches:** Same path yields different results for different observers.

AGENTESE principle: "There is no view from nowhere."

```python
# Same entity, different observers:
house.manifest(architect)  # -> Blueprint
house.manifest(poet)       # -> Metaphor
house.manifest(guest)      # -> Facade
```

**Key insight:** Observer-dependent semantics. The same path returns different results based on WHO is observing.

---

### 05: Constitutional Check
**File:** `05-constitutional-check/main.py`

**Teaches:** Scoring actions against the 7 principles with ethical floor.

The 7 kgents principles:
1. TASTEFUL (w=1.0)
2. CURATED (w=1.0)
3. ETHICAL (FLOOR >= 0.6)
4. JOY_INDUCING (w=1.2)
5. COMPOSABLE (w=1.5)
6. HETERARCHICAL (w=1.0)
7. GENERATIVE (w=1.0)

**Key insight:** ETHICAL is NOT a weighted score - it's a floor constraint.
If ETHICAL < 0.6, action is REJECTED regardless of other scores.
You cannot trade off ethics for other values.

---

## Core Concepts Summary

| Concept | Example | One-liner |
|---------|---------|-----------|
| Composition | 01 | Agents compose like functions: `f >> g` |
| Galois Loss | 02 | Loss predicts success: low = works, high = fails |
| Witness | 03 | Every action leaves an immutable Mark |
| Observer | 04 | Same path, different observers = different results |
| Constitution | 05 | 7 principles with ethical floor (non-negotiable) |

## Next Steps

After completing these examples:

1. Read `docs/skills/` for detailed implementation guides
2. Explore `impl/claude/agents/` for real agent implementations
3. Check `spec/` for the formal specifications
4. Look at `impl/claude/services/` for production services

## Running Tests

To verify the examples work with the codebase:

```bash
cd impl/claude
uv run pytest -q  # Run all tests
```
