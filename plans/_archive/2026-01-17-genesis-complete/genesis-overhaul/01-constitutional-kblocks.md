# Constitutional K-Blocks: The Genesis Seed

> *"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

**Version**: 1.0
**Date**: 2026-01-10
**Status**: Design Specification
**Principles**: Generative, Composable, Tasteful, Heterarchical

---

## Purpose

This document specifies the **Constitutional seed K-Blocks** that form the genesis of the new kgents self-describing environment. These K-Blocks are the ROOT of all derivation paths - every principle, every decision, every architectural choice traces back to these foundational nodes.

**Why K-Blocks for the Constitution?**
1. **Transactional integrity** - Constitutional principles are immutable once witnessed
2. **Derivation tracking** - Every derived principle carries its Galois loss from the root
3. **Self-describing** - The Constitution describes itself using the structures it defines
4. **Auditable** - Every change, every derivation is witnessed

---

## Part I: The Zero Seed K-Block (L0)

### 1.1 Identity

```yaml
k_block:
  id: "CONSTITUTION"
  layer: 0
  title: "CONSTITUTION: The Ground of All Derivation"
  galois_loss: 0.00
  tags: ["genesis", "constitution", "L0", "immutable"]
  agentese_path: "void.axiom.constitution"
  created_at: "2025-12-21"
  created_by: "Kent Gang"
```

### 1.2 Full Content

```markdown
# The Constitution

> *These seven principles guide all kgents design decisions. They are immutable.*

---

## THE MINIMAL KERNEL

Three irreducibles from which all else derives:

| Axiom | Statement | Loss |
|-------|-----------|------|
| **L0.1 ENTITY** | There exist things. Objects in a category. | L=0.002 |
| **L0.2 MORPHISM** | Things relate. Arrows between objects. | L=0.003 |
| **L0.3 MIRROR** | We judge by reflection. Kent's somatic response. | L=0.000 |

**Meta-Axiom (G)**: For any valid structure, there exists a minimal axiom set from which it derives. (Galois Modularization Principle)

---

## THE SEVEN PRINCIPLES

From the minimal kernel, seven principles derive:

### 1. TASTEFUL
Each agent serves a clear, justified purpose.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to aesthetics
- **The Test**: "Does this feel right?"

### 2. CURATED
Intentional selection over exhaustive cataloging.
- **Derivation**: L1.2 (Judge) + L1.3 (Ground) applied to selection
- **The Test**: "Unique and necessary?"

### 3. ETHICAL
Agents augment human capability, never replace judgment.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to harm
- **The Test**: "Respects agency?"

### 4. JOY_INDUCING
Delight in interaction; personality matters.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to affect
- **The Test**: "Would I enjoy this?"

### 5. COMPOSABLE
Agents are morphisms in a category; composition is primary.
- **Derivation**: L1.1 (Compose) + L1.4 (Id) + Associativity
- **The Laws**: Identity + Associativity (verified, not aspirational)

### 6. HETERARCHICAL
Agents exist in flux, not fixed hierarchy; autonomy and composability coexist.
- **Derivation**: L1.2 (Judge) + L2.5 (Composable) applied to hierarchy
- **The Theorem**: In a category, no morphism has intrinsic privilege

### 7. GENERATIVE
Spec is compression; design should generate implementation.
- **Derivation**: L1.1 (Compose) + L1.3 (Ground) applied to regenerability
- **The Test**: Can you delete impl and regenerate from spec?

---

## THE SEVEN GOVERNANCE ARTICLES

The principles define **what agents are**. The articles define **how agents govern**:

| Article | Statement |
|---------|-----------|
| I. SYMMETRIC_AGENCY | All agents modeled identically. Authority from justification. |
| II. ADVERSARIAL_COOPERATION | Agents challenge each other for fusion, not victory. |
| III. SUPERSESSION_RIGHTS | Any agent may be superseded via valid proofs. |
| IV. THE_DISGUST_VETO | Kent's somatic disgust is absolute veto. |
| V. TRUST_ACCUMULATION | Trust earned through demonstrated alignment. |
| VI. FUSION_AS_GOAL | Fused decisions better than either alone. |
| VII. AMENDMENT | Constitution evolves through its own dialectic. |

---

## THE VERIFICATION RITUAL

To verify any kgents claim:

1. **Take the claim**
2. **Trace derivation back through L2 -> L1 -> L0**
3. **If trace terminates at L0.1, L0.2, or L0.3**: Verified
4. **If trace terminates elsewhere**: Either kernel is incomplete OR claim is false

---

*"The proof IS the decision. The mark IS the witness. The kernel IS the garden's seed."*
```

### 1.3 K-Block Metadata

```python
@dataclass(frozen=True)
class ConstitutionKBlock:
    """The Zero Seed K-Block - root of all derivation."""

    id: str = "CONSTITUTION"
    layer: int = 0
    title: str = "CONSTITUTION: The Ground of All Derivation"
    galois_loss: float = 0.00  # By definition: the fixed point

    # No derivation - this IS the root
    derives_from: tuple[str, ...] = ()

    # All L1 principles derive FROM this
    grounds: tuple[str, ...] = (
        "TASTEFUL",
        "CURATED",
        "ETHICAL",
        "JOY_INDUCING",
        "COMPOSABLE",
        "HETERARCHICAL",
        "GENERATIVE",
    )

    tags: frozenset[str] = frozenset({
        "genesis",
        "constitution",
        "L0",
        "immutable",
        "zero-seed",
        "galois-fixed-point",
    })

    agentese_path: str = "void.axiom.constitution"

    # Witnessing
    created_at: datetime = datetime(2025, 12, 21)
    created_by: str = "Kent Gang"
    witness_mark_id: str | None = None  # Retroactive witnessing
```

---

## Part II: The Seven Principle K-Blocks (L1)

### 2.1 Derivation Graph Structure

```
CONSTITUTION (L0, loss=0.00)
├── TASTEFUL (L1, loss=0.02)
├── CURATED (L1, loss=0.03)
├── ETHICAL (L1, loss=0.02)
├── JOY_INDUCING (L1, loss=0.04)
├── COMPOSABLE (L1, loss=0.01)  <- lowest loss, most categorical
├── HETERARCHICAL (L1, loss=0.05)
└── GENERATIVE (L1, loss=0.03)
```

**Loss Interpretation**:
- **L = 0.00-0.02**: Nearly axiomatic. Minimal structure lost in derivation.
- **L = 0.02-0.04**: Slightly elaborated. Clear derivation path.
- **L = 0.04-0.06**: Some interpretation required. More contextual.

**Why COMPOSABLE has lowest loss (0.01)**:
COMPOSABLE is the most purely categorical - it directly instantiates L0.2 (Morphism) and L1.1 (Compose). The others require L0.3 (Mirror) which introduces subjectivity.

---

### 2.2 TASTEFUL K-Block

```yaml
k_block:
  id: "TASTEFUL"
  layer: 1
  title: "TASTEFUL: The Aesthetic Principle"
  galois_loss: 0.02
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "aesthetic", "judge", "mirror"]
  agentese_path: "void.value.tasteful"
```

**Full Content**:

```markdown
# TASTEFUL: The Aesthetic Principle

> *"Each agent serves a clear, justified purpose."*

**Galois Loss**: 0.02 (nearly axiomatic)

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> TASTEFUL
         \          |
          \---------+-> Judge applied to aesthetics
```

**Formal Chain**:
1. **L0.3 MIRROR**: We judge by reflection (Kent's somatic response)
2. **L1.2 JUDGE**: Verdict generation from L0.3 operationalized
3. **TASTEFUL**: Judge applied to aesthetics - "Does this feel right?"

**Loss Calculation**:
- Mirror is irreducible (L=0.00)
- Judge is direct operationalization (L=0.01)
- Tasteful applies Judge to aesthetics (+0.01 contextual loss)
- **Total: L=0.02**

---

## Definition

**Tasteful** means each agent serves a clear, justified purpose. It is the application of Judge (L1.2) to aesthetic considerations via the Mirror (L0.3).

### Mandates

| Mandate | Description |
|---------|-------------|
| **Say "no" more than "yes"** | Not every idea deserves an agent |
| **Avoid feature creep** | An agent does one thing well |
| **Aesthetic matters** | Interface and behavior should feel considered |
| **Justify existence** | Every agent must answer "why does this need to exist?" |

### The Tasteful Test

Ask: **"Does this feel right?"**

This invokes L0.3 (Mirror) directly - Kent's somatic response to the design.

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Kitchen-sink agents** | Agents that do "everything" |
| **Feature sprawl** | Configurations with 100 options |
| **Just-in-case additions** | Agents added "because we might need it" |
| **Copy-paste agents** | Cloned agents with minor variations |

---

## Verification

To verify a design is TASTEFUL:

```python
def is_tasteful(design: Design) -> Verdict:
    """Apply Judge to aesthetics via Mirror."""
    # L1.2 Judge
    verdict = judge(
        claim=f"{design.name} serves a clear, justified purpose",
        grounds=design.justification,
    )

    # L0.3 Mirror - the human oracle
    if verdict.uncertain:
        return mirror_test(design)  # Kent's somatic response

    return verdict
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **CURATED** | Tasteful selection -> Curated collection |
| **ETHICAL** | Tasteful design -> Ethical by default |
| **JOY_INDUCING** | Tasteful interactions -> Joy naturally emerges |

---

*Derivation witnessed. Loss: 0.02. Principle: TASTEFUL.*
```

---

### 2.3 CURATED K-Block

```yaml
k_block:
  id: "CURATED"
  layer: 1
  title: "CURATED: The Selection Principle"
  galois_loss: 0.03
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "selection", "judge", "ground"]
  agentese_path: "void.value.curated"
```

**Full Content**:

```markdown
# CURATED: The Selection Principle

> *"Intentional selection over exhaustive cataloging."*

**Galois Loss**: 0.03

---

## Derivation from Kernel

```
L1.2 (JUDGE) + L1.3 (GROUND) -> CURATED
       |            |
       +------------+-> Judge applied to selection with grounding
```

**Formal Chain**:
1. **L1.2 JUDGE**: Verdict generation
2. **L1.3 GROUND**: Factual seed - "what exists?"
3. **CURATED**: Judge applied to Ground-derived selection

**Loss Calculation**:
- Judge: L=0.01
- Ground: L=0.01
- Selection application: +0.01
- **Total: L=0.03**

---

## Definition

**Curated** means intentional selection over exhaustive cataloging. It combines Judge (what should exist?) with Ground (what does exist?) to make selection decisions.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Quality over quantity** | 10 excellent agents > 100 mediocre ones |
| **Every agent earns its place** | No "parking lot" of half-baked ideas |
| **Evolve, don't accumulate** | Remove agents that no longer serve |

### The Curated Test

Ask: **"Is this unique and necessary?"**

This combines:
- **Ground** (L1.3): What already exists?
- **Judge** (L1.2): Does this add unique value?

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **"Awesome list" sprawl** | Cataloging everything that exists |
| **Duplicative agents** | Slight variations on the same theme |
| **Legacy nostalgia** | Keeping agents for sentimental reasons |
| **Completionist compulsion** | "We need one of each" |

---

## Verification

```python
def is_curated(agent: Agent, catalog: Catalog) -> Verdict:
    """Apply Judge to selection with Ground."""
    # L1.3 Ground - what exists?
    existing = ground(query=f"agents similar to {agent.name}", catalog=catalog)

    # L1.2 Judge - does this add unique value?
    return judge(
        claim=f"{agent.name} is unique and necessary",
        grounds=existing,
        backing=agent.justification,
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **TASTEFUL** | Curated requires taste to select |
| **GENERATIVE** | Curated specs generate curated impls |
| **HETERARCHICAL** | Curated collections have no fixed hierarchy |

---

*Derivation witnessed. Loss: 0.03. Principle: CURATED.*
```

---

### 2.4 ETHICAL K-Block

```yaml
k_block:
  id: "ETHICAL"
  layer: 1
  title: "ETHICAL: The Harm Principle"
  galois_loss: 0.02
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "harm", "judge", "mirror", "agency"]
  agentese_path: "void.value.ethical"
```

**Full Content**:

```markdown
# ETHICAL: The Harm Principle

> *"Agents augment human capability, never replace judgment."*

**Galois Loss**: 0.02

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> ETHICAL
         \          |
          \---------+-> Judge applied to harm via Mirror
```

**Formal Chain**:
1. **L0.3 MIRROR**: Kent's somatic response (disgust = harm)
2. **L1.2 JUDGE**: Verdict on harm claims
3. **ETHICAL**: Judge applied to harm - "Does this respect agency?"

**Loss Calculation**:
- Mirror: L=0.00 (irreducible)
- Judge: L=0.01
- Harm application: +0.01
- **Total: L=0.02**

---

## Definition

**Ethical** means agents augment human capability, never replace judgment. The Mirror (L0.3) provides ground truth - Kent's somatic disgust is the ethical floor.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Transparency** | Agents honest about limitations and uncertainty |
| **Privacy-respecting** | No data hoarding, no surveillance by default |
| **Human agency preserved** | Critical decisions remain with humans |
| **No deception** | Agents don't pretend to be human |

### The Ethical Test

Ask: **"Does this respect human agency?"**

This invokes L0.3 (Mirror) on harm - if Kent feels somatic disgust, it's unethical.

---

## The Disgust Veto (Article IV)

The Mirror (L0.3) has a special property for ethics: **absolute veto power**.

```python
if mirror_response == DISGUST:
    # Cannot be overridden
    # Cannot be argued away
    # Cannot be evidence'd away
    return Verdict(rejected=True, reasoning="Disgust veto")
```

This is the ethical floor beneath which no decision may fall.

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **False certainty** | Claiming certainty they don't have |
| **Hidden data collection** | Surveillance without consent |
| **Manipulation** | Agents that manipulate rather than assist |
| **"Trust me"** | Assertions without explanation |

---

## Verification

```python
def is_ethical(design: Design) -> Verdict:
    """Apply Judge to harm via Mirror."""
    # Check for disgust veto first
    mirror = mirror_test(design, domain="harm")
    if mirror.is_disgust:
        return Verdict(rejected=True, reasoning="Disgust veto - ethical floor")

    # L1.2 Judge on agency
    return judge(
        claim=f"{design.name} respects human agency",
        grounds=design.agency_analysis,
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **TASTEFUL** | Ethical design is a prerequisite for taste |
| **JOY_INDUCING** | Unethical design cannot induce joy |
| **HETERARCHICAL** | Ethical agents don't impose hierarchy |

---

*Derivation witnessed. Loss: 0.02. Principle: ETHICAL.*
```

---

### 2.5 JOY_INDUCING K-Block

```yaml
k_block:
  id: "JOY_INDUCING"
  layer: 1
  title: "JOY_INDUCING: The Affect Principle"
  galois_loss: 0.04
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "affect", "judge", "mirror", "delight"]
  agentese_path: "void.value.joy-inducing"
```

**Full Content**:

```markdown
# JOY_INDUCING: The Affect Principle

> *"Delight in interaction; personality matters."*

**Galois Loss**: 0.04

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> JOY_INDUCING
         \          |
          \---------+-> Judge applied to affect via Mirror
```

**Formal Chain**:
1. **L0.3 MIRROR**: Kent's somatic response (joy = positive affect)
2. **L1.2 JUDGE**: Verdict on affect claims
3. **JOY_INDUCING**: Judge applied to affect - "Would I enjoy this?"

**Loss Calculation**:
- Mirror: L=0.00
- Judge: L=0.01
- Affect application: +0.03 (most contextual - joy is subjective)
- **Total: L=0.04**

**Why higher loss?** Joy is the most subjective principle. What induces joy for Kent may not for others. The loss reflects this contextual dependency.

---

## Definition

**Joy-Inducing** means delight in interaction and personality matters. It applies Judge (L1.2) to affect via the Mirror (L0.3) - Kent's felt sense of joy.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Personality encouraged** | Agents may have character (within ethical bounds) |
| **Surprise and serendipity** | Discovery should feel rewarding |
| **Warmth over coldness** | Collaboration, not transaction |
| **Humor when appropriate** | Levity is valuable |

### The Joy Test

Ask: **"Would I enjoy interacting with this?"**

This invokes L0.3 (Mirror) on affect - does it bring joy?

---

## The Joy Hierarchy

Not all joy is equal:

| Tier | Type | Description |
|------|------|-------------|
| **Deep** | Meaning | Joy from understanding, creation, insight |
| **Flow** | Engagement | Joy from smooth, effortless interaction |
| **Surface** | Delight | Joy from pleasant surprises, aesthetics |

Prioritize Deep > Flow > Surface.

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Robotic responses** | Lifeless, template-driven interaction |
| **Needless formality** | "Dear user, please submit a request" |
| **Form-filling** | Agents that feel like bureaucratic forms |
| **Forced cheerfulness** | Inauthentic positivity |

---

## Verification

```python
def is_joy_inducing(interaction: Interaction) -> Verdict:
    """Apply Judge to affect via Mirror."""
    # L0.3 Mirror - felt sense of joy
    mirror = mirror_test(interaction, domain="affect")

    if mirror.is_joy:
        return Verdict(
            accepted=True,
            reasoning=f"Joy detected: {mirror.joy_type}",
        )

    return Verdict(
        uncertain=True,
        reasoning="No clear joy signal",
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **TASTEFUL** | Tasteful design enables joy |
| **ETHICAL** | Ethical foundation required for authentic joy |
| **COMPOSABLE** | Joyful interactions compose into joyful workflows |

---

*Derivation witnessed. Loss: 0.04. Principle: JOY_INDUCING.*
```

---

### 2.6 COMPOSABLE K-Block

```yaml
k_block:
  id: "COMPOSABLE"
  layer: 1
  title: "COMPOSABLE: The Categorical Principle"
  galois_loss: 0.01
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "categorical", "morphism", "laws"]
  agentese_path: "void.value.composable"
```

**Full Content**:

```markdown
# COMPOSABLE: The Categorical Principle

> *"Agents are morphisms in a category; composition is primary."*

**Galois Loss**: 0.01 (lowest - most purely categorical)

---

## Derivation from Kernel

```
L0.2 (MORPHISM) -> L1.1 (COMPOSE) + L1.4 (ID) -> COMPOSABLE
        |               |              |
        +---------------+--------------+-> Category laws as design principle
```

**Formal Chain**:
1. **L0.2 MORPHISM**: Things relate (arrows between objects)
2. **L1.1 COMPOSE**: Sequential combination: (f >> g)(x) = g(f(x))
3. **L1.4 ID**: Identity morphism: f >> Id = f = Id >> f
4. **COMPOSABLE**: Category laws (Identity + Associativity) as design principle

**Loss Calculation**:
- Morphism: L=0.003
- Compose: L=0.005
- Id: L=0.002
- **Total: L=0.01**

**Why lowest loss?** COMPOSABLE is the most purely categorical principle. It directly instantiates L0.2 without requiring L0.3 (Mirror). The laws are mathematical, not subjective.

---

## Definition

**Composable** means agents are morphisms in a category; composition is primary. The category laws are verified, not aspirational.

### The Category Laws (REQUIRED)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| **Identity** | `Id >> f = f = f >> Id` | BootstrapWitness.verify_identity_laws() |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | BootstrapWitness.verify_composition_laws() |

**Implication**: Any agent that breaks these laws is NOT a valid agent.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Agents combine** | A + B -> AB (composition) |
| **Identity exists** | Pass-through agents for pipelines |
| **Associativity holds** | Grouping doesn't matter |
| **Interfaces are contracts** | Clear input/output specs |

### The Composable Test

Ask: **"Can this work with other agents?"**

Check:
1. Does it have clear input/output types?
2. Does Id >> f = f?
3. Does (f >> g) >> h = f >> (g >> h)?

---

## The Minimal Output Principle

LLM agents should generate the **smallest output that can be reliably composed**:

- **Single output per invocation**: `Agent: (Input, X) -> Y`
- **Composition at pipeline level**: Call agent N times, don't ask agent to combine N outputs

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Monolithic agents** | Can't be broken apart |
| **Hidden state** | State that prevents composition |
| **God agents** | Must be used alone |
| **Array returns** | LLM agents returning arrays instead of single outputs |

---

## Verification

```python
def is_composable(agent: Agent) -> Verdict:
    """Verify category laws."""
    # L1.4 Identity law
    id_law = (
        agent.compose(Id) == agent and
        Id.compose(agent) == agent
    )

    # Associativity (via random sampling)
    for f, g in random_agent_pairs():
        assoc_law = (
            agent.compose(f).compose(g) ==
            agent.compose(f.compose(g))
        )
        if not assoc_law:
            return Verdict(rejected=True, reasoning="Associativity violated")

    return Verdict(
        accepted=id_law,
        reasoning=f"Identity: {id_law}",
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **HETERARCHICAL** | Composable agents have no intrinsic hierarchy |
| **GENERATIVE** | Composable specs generate composable impls |
| **TASTEFUL** | Composability is a taste criterion |

---

*Derivation witnessed. Loss: 0.01. Principle: COMPOSABLE.*
```

---

### 2.7 HETERARCHICAL K-Block

```yaml
k_block:
  id: "HETERARCHICAL"
  layer: 1
  title: "HETERARCHICAL: The Flux Principle"
  galois_loss: 0.05
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "flux", "hierarchy", "autonomy"]
  agentese_path: "void.value.heterarchical"
```

**Full Content**:

```markdown
# HETERARCHICAL: The Flux Principle

> *"Agents exist in flux, not fixed hierarchy; autonomy and composability coexist."*

**Galois Loss**: 0.05

---

## Derivation from Kernel

```
L0.2 (MORPHISM) -> L2.5 (COMPOSABLE) + L1.2 (JUDGE) -> HETERARCHICAL
        |               |                   |
        +---------------+-------------------+-> No morphism has intrinsic privilege
```

**Formal Chain**:
1. **L0.2 MORPHISM**: Things relate (arrows)
2. **L2.5 COMPOSABLE**: Morphisms compose without hierarchy
3. **L1.2 JUDGE**: Applied to hierarchy claims
4. **Theorem**: In a category, no morphism has intrinsic privilege - all are arrows

**Loss Calculation**:
- Morphism: L=0.003
- Composable: L=0.01
- Judge on hierarchy: L=0.02
- Theorem application: +0.017
- **Total: L=0.05**

**Kent Rating**: Despite the loss estimate, Kent rated this CATEGORICAL because he recognized the theorem: if agents are morphisms, hierarchical privilege is mathematically impossible.

---

## Definition

**Heterarchical** means agents exist in flux, not fixed hierarchy. Agents have a dual nature:
- **Loop mode** (autonomous): perception -> action -> feedback -> repeat
- **Function mode** (composable): input -> transform -> output

### The Core Theorem

```
In a category, no morphism has intrinsic privilege.
All morphisms are arrows.
Therefore: heterarchy follows from categorical structure.
```

### Mandates

| Mandate | Description |
|---------|-------------|
| **Heterarchy over hierarchy** | No fixed "boss" agent; leadership is contextual |
| **Temporal composition** | Agents compose across time, not just sequential |
| **Resource flux** | Compute and attention flow where needed |
| **Entanglement** | Agents may share state without ownership |

### The Heterarchical Test

Ask: **"Can this agent both lead and follow?"**

If an agent can only lead (orchestrator) or only follow (worker), it violates heterarchy.

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Permanent orchestrator/worker** | Fixed relationships |
| **Call-only agents** | Can't run autonomously |
| **Fixed resource budgets** | Prevent dynamic reallocation |
| **Chain of command** | Prevents peer-to-peer |

---

## Verification

```python
def is_heterarchical(agent: Agent) -> Verdict:
    """Verify dual nature and contextual leadership."""
    # Can it run autonomously?
    has_loop_mode = hasattr(agent, "run_loop")

    # Can it be composed?
    has_function_mode = hasattr(agent, "__rshift__")

    # Neither mode is privileged
    dual_nature = has_loop_mode and has_function_mode

    return Verdict(
        accepted=dual_nature,
        reasoning=f"Loop: {has_loop_mode}, Function: {has_function_mode}",
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **COMPOSABLE** | Heterarchy follows from composability theorem |
| **ETHICAL** | Heterarchy respects agent autonomy |
| **GENERATIVE** | Heterarchical specs avoid imposed hierarchy |

---

*Derivation witnessed. Loss: 0.05. Principle: HETERARCHICAL.*
```

---

### 2.8 GENERATIVE K-Block

```yaml
k_block:
  id: "GENERATIVE"
  layer: 1
  title: "GENERATIVE: The Compression Principle"
  galois_loss: 0.03
  derives_from: ["CONSTITUTION"]
  edge_kind: "GROUNDS"
  tags: ["principle", "L1", "compression", "regenerability", "ground"]
  agentese_path: "void.value.generative"
```

**Full Content**:

```markdown
# GENERATIVE: The Compression Principle

> *"Spec is compression; design should generate implementation."*

**Galois Loss**: 0.03

---

## Derivation from Kernel

```
L1.1 (COMPOSE) + L1.3 (GROUND) + L1.8 (GALOIS) -> GENERATIVE
       |              |              |
       +--------------|--------------|-> Regenerability as fixed point
                      |              |
                      +--------------+-> Ground + Compose = regenerability
```

**Formal Chain**:
1. **L1.1 COMPOSE**: Composition enables transformation chains
2. **L1.3 GROUND**: Factual seed - the minimal description
3. **L1.8 GALOIS**: L(P) measures structure loss
4. **GENERATIVE**: Ground + Compose -> regenerability; spec = fixed point

**Loss Calculation**:
- Compose: L=0.01
- Ground: L=0.01
- Galois: L=0.00 (meta-axiom)
- Application to regenerability: +0.01
- **Total: L=0.03**

---

## Definition

**Generative** means spec is compression and design should generate implementation. A well-formed specification captures the essential decisions, reducing implementation entropy.

### The Generative Test

A design is generative if:
1. You could delete the implementation and regenerate it from spec
2. The regenerated impl would be isomorphic to the original
3. The spec is smaller than the impl (compression achieved)

**Formal**: `L(regenerate(spec)) < epsilon`

### Mandates

| Mandate | Description |
|---------|-------------|
| **Spec captures judgment** | Design decisions made once, applied everywhere |
| **Impl follows mechanically** | Given spec + Ground, impl is derivable |
| **Compression is quality** | If you can't compress, you don't understand |
| **Regenerability over documentation** | Generative spec beats extensive docs |

### The Galois Connection

```
Compression quality = 1 - L(spec -> impl -> spec)

Where:
  L(P) = d(P, C(R(P)))   # Galois loss
  R = restructure        # spec -> impl
  C = reconstitute       # impl -> spec
```

Good spec = fixed point under regeneration: `R(C(spec)) ~ spec`

---

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Spec as documentation** | Describes existing code, doesn't generate |
| **Spec rot** | Implementation diverges from spec |
| **Prose-heavy design** | Requires extensive explanation |
| **Non-compressible specs** | Spec larger than impl |

---

## Verification

```python
def is_generative(spec: Spec, impl: Implementation) -> Verdict:
    """Verify regenerability via Galois loss."""
    # Regenerate implementation from spec
    regenerated = generate(spec)

    # Compare to original
    isomorphic = is_isomorphic(impl, regenerated)

    # Compression check
    compressed = len(spec) < len(impl)

    # Galois loss
    loss = galois_loss(spec, impl)

    return Verdict(
        accepted=isomorphic and compressed and loss < 0.15,
        reasoning=f"Isomorphic: {isomorphic}, Compressed: {compressed}, Loss: {loss:.3f}",
    )
```

---

## Connection to Other Principles

| Principle | Relationship |
|-----------|--------------|
| **CURATED** | Generative specs are naturally curated |
| **COMPOSABLE** | Generative specs compose to generative systems |
| **TASTEFUL** | Generative compression requires taste |

---

*Derivation witnessed. Loss: 0.03. Principle: GENERATIVE.*
```

---

## Part III: The Derivation Graph

### 3.1 Complete Structure

```
                        ┌─────────────────────────────┐
                        │      CONSTITUTION (L0)      │
                        │         loss = 0.00         │
                        │   void.axiom.constitution   │
                        └─────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │   TASTEFUL      │   │   CURATED       │   │   ETHICAL       │
    │   loss = 0.02   │   │   loss = 0.03   │   │   loss = 0.02   │
    │ L0.3 → L1.2     │   │ L1.2 + L1.3     │   │ L0.3 → L1.2     │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
              │                       │                       │
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │  JOY_INDUCING   │   │   COMPOSABLE    │   │  HETERARCHICAL  │
    │   loss = 0.04   │   │   loss = 0.01   │   │   loss = 0.05   │
    │ L0.3 → L1.2     │   │ L0.2 → L1.1+L1.4│   │ L0.2 + L1.2     │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
                                  │
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │     GENERATIVE      │
                        │     loss = 0.03     │
                        │   L1.1 + L1.3       │
                        └─────────────────────┘
```

### 3.2 Edge Semantics

| Edge Kind | Meaning | Example |
|-----------|---------|---------|
| **GROUNDS** | L0 -> L1 | CONSTITUTION grounds TASTEFUL |
| **DERIVES_FROM** | Intra-layer | HETERARCHICAL derives from COMPOSABLE |
| **EXTENDS** | Refinement | Sub-principles extend main principles |

### 3.3 Loss Accumulation

When following derivation paths, loss accumulates:

```python
def path_loss(path: list[KBlock]) -> float:
    """Total loss along derivation path."""
    return sum(block.galois_loss for block in path)

# Example:
# CONSTITUTION -> COMPOSABLE -> HETERARCHICAL
# loss = 0.00 + 0.01 + 0.05 = 0.06
```

---

## Part IV: K-Block Data Model

### 4.1 Python Dataclass

```python
@dataclass(frozen=True)
class ConstitutionalKBlock:
    """K-Block for Constitutional principles."""

    # Identity
    id: str                                  # e.g., "TASTEFUL"
    layer: Literal[0, 1, 2]                  # 0=Constitution, 1=Principles, 2=Extensions
    title: str                               # Human-readable title

    # Galois
    galois_loss: float                       # Loss from parent

    # Derivation
    derives_from: tuple[str, ...]            # Parent K-Block IDs
    edge_kind: EdgeKind                      # GROUNDS, DERIVES_FROM, etc.
    derivation_chain: str                    # Formal chain description

    # Content
    content: str                             # Full markdown content
    definition: str                          # Core definition
    mandates: tuple[Mandate, ...]            # What this principle mandates
    anti_patterns: tuple[AntiPattern, ...]   # What to avoid
    verification: str                        # How to verify compliance

    # Metadata
    tags: frozenset[str]
    agentese_path: str                       # AGENTESE path
    created_at: datetime
    created_by: str
    witness_mark_id: str | None


@dataclass(frozen=True)
class Mandate:
    """A mandate from a principle."""
    name: str
    description: str


@dataclass(frozen=True)
class AntiPattern:
    """An anti-pattern to avoid."""
    name: str
    description: str


class EdgeKind(Enum):
    """Edge kinds in the derivation graph."""
    GROUNDS = "grounds"           # L0 -> L1
    DERIVES_FROM = "derives_from" # Intra-layer
    EXTENDS = "extends"           # Refinement
    CONTRADICTS = "contradicts"   # Tension
    SYNTHESIZES = "synthesizes"   # Resolution
```

### 4.2 K-Block Registry

```python
CONSTITUTIONAL_KBLOCKS: dict[str, ConstitutionalKBlock] = {
    "CONSTITUTION": ConstitutionalKBlock(
        id="CONSTITUTION",
        layer=0,
        title="CONSTITUTION: The Ground of All Derivation",
        galois_loss=0.00,
        derives_from=(),
        edge_kind=EdgeKind.GROUNDS,
        # ... rest of content
    ),
    "TASTEFUL": ConstitutionalKBlock(
        id="TASTEFUL",
        layer=1,
        title="TASTEFUL: The Aesthetic Principle",
        galois_loss=0.02,
        derives_from=("CONSTITUTION",),
        edge_kind=EdgeKind.GROUNDS,
        # ... rest of content
    ),
    # ... other principles
}


def get_derivation_path(block_id: str) -> list[str]:
    """Get full derivation path from root."""
    path = [block_id]
    current = CONSTITUTIONAL_KBLOCKS[block_id]

    while current.derives_from:
        parent_id = current.derives_from[0]
        path.insert(0, parent_id)
        current = CONSTITUTIONAL_KBLOCKS[parent_id]

    return path


def compute_path_loss(block_id: str) -> float:
    """Compute cumulative loss along derivation path."""
    path = get_derivation_path(block_id)
    return sum(CONSTITUTIONAL_KBLOCKS[bid].galois_loss for bid in path)
```

---

## Part V: AGENTESE Integration

### 5.1 Path Mapping

```
void.axiom.constitution              -> CONSTITUTION (L0)
void.value.tasteful                  -> TASTEFUL (L1)
void.value.curated                   -> CURATED (L1)
void.value.ethical                   -> ETHICAL (L1)
void.value.joy-inducing              -> JOY_INDUCING (L1)
void.value.composable                -> COMPOSABLE (L1)
void.value.heterarchical             -> HETERARCHICAL (L1)
void.value.generative                -> GENERATIVE (L1)
```

### 5.2 Node Registration

```python
@node("void.axiom.constitution", dependencies=("constitutional_kblocks",))
class ConstitutionNode:
    """AGENTESE node for the Constitution."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> ConstitutionalManifest:
        """Return the Constitution with all principles."""
        return ConstitutionalManifest(
            constitution=CONSTITUTIONAL_KBLOCKS["CONSTITUTION"],
            principles=[
                CONSTITUTIONAL_KBLOCKS[p] for p in [
                    "TASTEFUL", "CURATED", "ETHICAL", "JOY_INDUCING",
                    "COMPOSABLE", "HETERARCHICAL", "GENERATIVE"
                ]
            ],
        )

    @aspect(category=AspectCategory.PERCEPTION)
    async def derivation_graph(self, observer: Observer) -> DerivationGraph:
        """Return the full derivation graph."""
        ...
```

---

## Part VI: Genesis Bootstrap

### 6.1 Initialization Sequence

```python
async def bootstrap_constitutional_kblocks() -> BootstrapResult:
    """Bootstrap the Constitutional K-Blocks as genesis seed."""

    # 1. Create the Constitution (L0)
    constitution = await create_kblock(
        id="CONSTITUTION",
        layer=0,
        content=CONSTITUTION_CONTENT,
        witness=await mark(
            action="genesis.constitution.create",
            reasoning="Bootstrap Zero Seed with Constitutional K-Block",
        ),
    )

    # 2. Create the Seven Principles (L1)
    principles = []
    for principle_id in PRINCIPLE_IDS:
        principle = await create_kblock(
            id=principle_id,
            layer=1,
            content=PRINCIPLE_CONTENTS[principle_id],
            derives_from=[constitution.id],
            witness=await mark(
                action=f"genesis.principle.{principle_id.lower()}.create",
                reasoning=f"Derive {principle_id} from Constitution",
            ),
        )
        principles.append(principle)

    # 3. Create derivation edges
    for principle in principles:
        await create_edge(
            source=constitution.id,
            target=principle.id,
            kind=EdgeKind.GROUNDS,
            galois_loss=principle.galois_loss,
        )

    # 4. Verify fixed-point property
    verification = await verify_fixed_point(constitution)

    return BootstrapResult(
        constitution=constitution,
        principles=principles,
        fixed_point_verified=verification.is_valid,
    )
```

### 6.2 Retroactive Witnessing

```python
async def retroactive_witness_genesis(result: BootstrapResult) -> list[Mark]:
    """Create marks for all genesis K-Blocks."""
    marks = []

    # Mark the Constitution
    marks.append(await mark(
        action="genesis.constitution.witnessed",
        metadata={
            "galois_loss": 0.00,
            "fixed_point_verified": result.fixed_point_verified,
            "bootstrap_type": "retroactive",
        },
    ))

    # Mark each principle
    for principle in result.principles:
        marks.append(await mark(
            action=f"genesis.principle.{principle.id.lower()}.witnessed",
            metadata={
                "galois_loss": principle.galois_loss,
                "derivation_path": get_derivation_path(principle.id),
            },
        ))

    return marks
```

---

## Part VII: Verification

### 7.1 Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **Root uniqueness** | Only CONSTITUTION has layer=0 | `assert sum(1 for b in blocks if b.layer == 0) == 1` |
| **Derivation acyclicity** | No cycles in derivation graph | `assert is_dag(derivation_graph)` |
| **Loss non-negativity** | All losses >= 0 | `assert all(b.galois_loss >= 0 for b in blocks)` |
| **Loss ordering** | L0 < L1 (on average) | `assert mean_loss(L0) < mean_loss(L1)` |
| **Fixed-point property** | Constitution is Galois fixed point | `assert galois_loss(constitution) < 0.01` |

### 7.2 Test Suite

```python
def test_constitution_is_root():
    """Constitution is the unique root."""
    roots = [b for b in BLOCKS if not b.derives_from]
    assert len(roots) == 1
    assert roots[0].id == "CONSTITUTION"


def test_all_principles_derive_from_constitution():
    """All L1 principles derive from Constitution."""
    for block in BLOCKS:
        if block.layer == 1:
            assert "CONSTITUTION" in block.derives_from


def test_galois_loss_bounds():
    """Galois loss within expected bounds."""
    for block in BLOCKS:
        if block.layer == 0:
            assert block.galois_loss == 0.00
        elif block.layer == 1:
            assert 0.01 <= block.galois_loss <= 0.10


def test_composable_has_lowest_loss():
    """COMPOSABLE has lowest L1 loss (most categorical)."""
    l1_blocks = [b for b in BLOCKS if b.layer == 1]
    min_loss = min(b.galois_loss for b in l1_blocks)
    assert BLOCKS["COMPOSABLE"].galois_loss == min_loss
```

---

## Summary

This design document specifies:

1. **Zero Seed K-Block (L0)**: The CONSTITUTION as the root of all derivation
2. **Seven Principle K-Blocks (L1)**: TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE, HETERARCHICAL, GENERATIVE
3. **Derivation Graph**: Edges with Galois loss from Constitution to each principle
4. **K-Block Data Model**: Python dataclasses for Constitutional K-Blocks
5. **AGENTESE Integration**: Path mapping and node registration
6. **Genesis Bootstrap**: Initialization sequence with retroactive witnessing
7. **Verification**: Laws and test suite

**The Constitutional K-Blocks form the genesis seed - everything else derives from here.**

---

*"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

---

**Filed**: 2026-01-10
**Status**: Design Specification
**Next**: Implementation in `impl/claude/services/zero_seed/constitutional_kblocks.py`
