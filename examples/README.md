# kgents Examples

> *"Joy-inducing > merely functional"*

Five progressive examples that teach the core concepts of kgents. Start at 01 and work through in order—each builds on the previous.

---

## Quick Start

```bash
# From the project root:
cd impl/claude
uv run python ../../examples/01-hello-composition/main.py
```

Run all examples:
```bash
cd impl/claude
for n in 01 02 03 04 05; do
  echo "=== Example $n ===" && uv run python ../../examples/${n}-*/main.py
  echo ""
done
```

---

## The Learning Path

| # | Example | What You Learn | Time |
|---|---------|---------------|------|
| **01** | [Hello Composition](./01-hello-composition/) | Agents compose with `>>`. Category laws (identity, associativity) are verified. | 5 min |
| **02** | [Galois Oracle](./02-galois-oracle/) | Galois Loss predicts task success/failure before execution. Low loss = will work. | 10 min |
| **03** | [Witness Trace](./03-witness-trace/) | Every action leaves a Mark. Marks compose into Traces via the Writer monad. | 10 min |
| **04** | [AGENTESE Observer](./04-agentese-observer/) | Same path, different observers → different results. Observer-dependent semantics. | 10 min |
| **05** | [Constitutional Check](./05-constitutional-check/) | 7 principles score actions. ETHICAL is a floor, not a weight—non-negotiable. | 10 min |

---

## 01: Hello Composition

**File**: `01-hello-composition/main.py`

kgents is built on category theory. The fundamental insight: agents are morphisms that compose.

```python
double = from_function("Double", lambda x: x * 2)
add_one = from_function("AddOne", lambda x: x + 1)
composed = sequential(double, add_one)  # double >> add_one
```

**Category Laws** (verified at runtime, not assumed):
- **Identity**: `Id >> f == f == f >> Id`
- **Associativity**: `(f >> g) >> h == f >> (g >> h)`

**Why it matters**: If these laws don't hold, composition is fragile. kgents checks them.

---

## 02: Galois Oracle

**File**: `02-galois-oracle/main.py`

The Galois Loss measures semantic preservation when content is restructured:

```
L(P) = d(P, C(R(P)))

R = restructure (decompose into modules)
C = reconstitute (reassemble)
d = semantic distance
```

**Layer Assignment**:
| Loss Range | Layer | Meaning |
|------------|-------|---------|
| < 0.05 | L1: Axiom | Fixed point, will definitely succeed |
| 0.05-0.15 | L2: Value | Strong foundation |
| 0.15-0.30 | L3: Goal | Achievable |
| 0.30-0.45 | L4: Obligation | Requires effort |
| 0.45-0.60 | L5: Execution | Risky |
| > 0.60 | L6-7: Chaotic | Will likely fail |

**Why it matters**: Predicting failure before you spend tokens is the killer feature.

---

## 03: Witness Trace

**File**: `03-witness-trace/main.py`

Every action in kgents leaves a **Mark**:

```python
@dataclass(frozen=True)
class Mark:
    origin: str           # Who created this
    stimulus: Stimulus    # What triggered it
    response: Response    # What it produced
    proof: Proof          # Why (Toulmin argumentation)
```

Marks compose into **Traces**:

```python
trace = Trace()
trace = trace.add(mark1)  # Returns NEW trace (immutable)
trace = trace.add(mark2)
```

**Philosophy**: *"Without trace: stimulus → response (reflex). With trace: stimulus → reasoning → response (agency)."*

---

## 04: AGENTESE Observer

**File**: `04-agentese-observer/main.py`

AGENTESE principle: *"There is no view from nowhere."*

The same entity manifests differently to different observers:

```python
house.manifest(architect)  # → Blueprint (structural view)
house.manifest(poet)       # → Metaphor (lyrical view)
house.manifest(guest)      # → Facade (surface view)
```

**Why it matters**: Observer-dependent semantics. The same API call returns different results based on WHO is calling. This enables sophisticated access control and personalization without separate endpoints.

---

## 05: Constitutional Check

**File**: `05-constitutional-check/main.py`

The 7 kgents principles score every action:

| Principle | Weight | Type |
|-----------|--------|------|
| ETHICAL | — | **FLOOR** (≥0.6 required) |
| COMPOSABLE | 1.5× | Weighted |
| JOY_INDUCING | 1.2× | Weighted |
| TASTEFUL | 1.0× | Weighted |
| CURATED | 1.0× | Weighted |
| HETERARCHICAL | 1.0× | Weighted |
| GENERATIVE | 1.0× | Weighted |

**The Ethical Floor**: Even if an action scores perfectly on all other principles, if ETHICAL < 0.6, it's **REJECTED**.

```
TASTEFUL: 1.0
CURATED: 1.0
JOY_INDUCING: 1.0
COMPOSABLE: 1.0
ETHICAL: 0.4      ← Below floor

Result: REJECTED (Cannot trade off ethics for other values)
```

---

## Core Concepts Summary

| Concept | Example | One-liner |
|---------|---------|-----------|
| **Composition** | 01 | Agents compose: `f >> g` means "f then g" |
| **Galois Loss** | 02 | Loss predicts success: low = works, high = fails |
| **Witness** | 03 | Every action leaves an immutable Mark |
| **Observer** | 04 | Same path + different observer = different result |
| **Constitution** | 05 | 7 principles with ethical floor (non-negotiable) |

---

## After These Examples

1. **[docs/skills/](../docs/skills/)** — 24 practical how-to guides for implementation
2. **[docs/theory/](../docs/theory/)** — 21-chapter mathematical foundations
3. **[impl/claude/agents/](../impl/claude/agents/)** — Real agent implementations
4. **[impl/claude/services/](../impl/claude/services/)** — 50+ production services

---

## Running Tests

Verify the examples work with the codebase:

```bash
cd impl/claude
uv run pytest -q  # Run all tests
```

---

*"The persona is a garden, not a museum."*
