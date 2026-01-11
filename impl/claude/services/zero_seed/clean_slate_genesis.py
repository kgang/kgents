"""
Clean Slate Genesis: Self-Describing K-Block Creation.

"Genesis is self-description, not interrogation."

This module implements the new genesis protocol from spec/protocols/genesis-clean-slate.md.
It creates 22 self-describing K-Blocks in 4 layers that teach the system about itself.

Philosophy:
    "The garden knows itself. The system teaches itself. The user discovers alongside."

See: spec/protocols/genesis-clean-slate.md
See: plans/genesis-overhaul/02-minimal-kernel-kblocks.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from services.k_block.core.derivation import DerivationDAG
from services.k_block.core.kblock import KBlockId, generate_kblock_id

if TYPE_CHECKING:
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

EPOCH = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

# Genesis K-Block IDs (fixed for stable references)
GENESIS_IDS = {
    # L0: Axioms (4)
    "entity": "genesis:L0:entity",
    "morphism": "genesis:L0:morphism",
    "mirror": "genesis:L0:mirror",
    "galois": "genesis:L0:galois",
    # L1: Kernel (7)
    "compose": "genesis:L1:compose",
    "judge": "genesis:L1:judge",
    "ground": "genesis:L1:ground",
    "id": "genesis:L1:id",
    "contradict": "genesis:L1:contradict",
    "sublate": "genesis:L1:sublate",
    "fix": "genesis:L1:fix",
    # L2: Principles (7)
    "tasteful": "genesis:L2:tasteful",
    "curated": "genesis:L2:curated",
    "ethical": "genesis:L2:ethical",
    "joy": "genesis:L2:joy",
    "composable": "genesis:L2:composable",
    "heterarchical": "genesis:L2:heterarchical",
    "generative": "genesis:L2:generative",
    # L3: Architecture (4)
    "ashc": "genesis:L3:ashc",
    "fullstack": "genesis:L3:fullstack",
    "editor": "genesis:L3:editor",
    "agentese": "genesis:L3:agentese",
}

# LIVING_EARTH color palette
COLORS = {
    # L0: Warmest (most fundamental)
    "entity": "#F5E6D3",  # glow.lantern
    "morphism": "#E8C4A0",  # glow.honey
    "mirror": "#D4A574",  # glow.amber
    "galois": "#C08552",  # glow.copper
    # L1: Earth tones (operational)
    "compose": "#4A6B4A",  # green.sage
    "judge": "#6B8B6B",  # green.mint
    "ground": "#6B4E3D",  # earth.wood
    "id": "#8BAB8B",  # green.sprout
    "contradict": "#8B6F5C",  # earth.clay
    "sublate": "#AB9080",  # earth.sand
    "fix": "#2E4A2E",  # green.fern
    # L2: Mixed (derived principles)
    "tasteful": "#D4A574",  # glow.amber
    "curated": "#C08552",  # glow.copper
    "ethical": "#4A6B4A",  # green.sage
    "joy": "#E8C4A0",  # glow.honey
    "composable": "#6B8B6B",  # green.mint
    "heterarchical": "#8BAB8B",  # green.sprout
    "generative": "#F5E6D3",  # glow.lantern
    # L3: Cooler (architectural)
    "ashc": "#D4A574",  # glow.amber
    "fullstack": "#6B4E3D",  # earth.wood
    "editor": "#4A6B4A",  # green.sage
    "agentese": "#C08552",  # glow.copper
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass(frozen=True)
class GenesisKBlockSpec:
    """Specification for a Genesis K-Block."""

    id: str
    path: str
    layer: int
    title: str
    content: str
    loss: float
    confidence: float
    color: str
    derivations_from: tuple[str, ...]
    tags: frozenset[str]

    @property
    def layer_name(self) -> str:
        """Human-readable layer name."""
        names = {
            0: "axiom",
            1: "kernel",
            2: "principle",
            3: "architecture",
        }
        return names.get(self.layer, "unknown")

    @property
    def file_path(self) -> str:
        """Compute file path from layer and ID.

        Example: genesis:L0:entity -> spec/genesis/L0/entity.md
        """
        # Extract short name from genesis ID (e.g., "genesis:L0:entity" -> "entity")
        short_name = self.id.split(":")[-1]
        return f"spec/genesis/L{self.layer}/{short_name}.md"

    @property
    def short_name(self) -> str:
        """Extract short name from genesis ID."""
        return self.id.split(":")[-1]


@dataclass
class GenesisResult:
    """Result of clean slate genesis operation."""

    success: bool
    message: str
    kblock_ids: dict[str, str]  # genesis_id -> actual kblock_id
    total_kblocks: int
    average_loss: float
    derivation_graph: DerivationDAG
    timestamp: datetime
    errors: list[str] = field(default_factory=list)
    file_paths: dict[str, str] = field(default_factory=dict)  # genesis_id -> file path

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "kblock_ids": self.kblock_ids,
            "total_kblocks": self.total_kblocks,
            "average_loss": self.average_loss,
            "derivation_graph": self.derivation_graph.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "errors": self.errors,
            "file_paths": self.file_paths,
        }


# =============================================================================
# Genesis File Writer
# =============================================================================


class GenesisFileWriter:
    """
    Writes genesis K-Block content to actual files.

    Philosophy: "Files are the sovereign territory. K-Blocks are rich indexes."

    Creates files in spec/genesis/ with the following structure:
        spec/genesis/
        ├── L0/
        │   ├── entity.md
        │   ├── morphism.md
        │   ├── mirror.md
        │   └── galois.md
        ├── L1/
        │   ├── compose.md
        │   └── ... (7 files)
        ├── L2/
        │   └── ... (7 files)
        └── L3/
            └── ... (4 files)
    """

    def __init__(self, project_root: Path):
        """Initialize with project root path."""
        self.project_root = project_root

    def write_genesis_file(self, spec: GenesisKBlockSpec) -> Path:
        """
        Write a genesis spec to its file path.

        Args:
            spec: Genesis K-Block specification

        Returns:
            Absolute path to the written file
        """
        file_path = self.project_root / spec.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content with frontmatter
        content = self._generate_file_content(spec)
        file_path.write_text(content, encoding="utf-8")

        logger.debug(f"Wrote genesis file: {file_path}")
        return file_path

    def _generate_file_content(self, spec: GenesisKBlockSpec) -> str:
        """Generate file content with YAML frontmatter."""
        # Add frontmatter with metadata
        frontmatter = f"""---
genesis_id: "{spec.id}"
layer: {spec.layer}
layer_name: "{spec.layer_name}"
galois_loss: {spec.loss}
confidence: {spec.confidence}
color: "{spec.color}"
derives_from: {list(spec.derivations_from)}
tags: {sorted(spec.tags)}
---

"""
        return frontmatter + spec.content

    def write_all(self, specs: list[GenesisKBlockSpec]) -> dict[str, Path]:
        """
        Write all genesis files.

        Args:
            specs: List of all genesis K-Block specifications

        Returns:
            Mapping of genesis_id to absolute file path
        """
        result: dict[str, Path] = {}
        for spec in specs:
            path = self.write_genesis_file(spec)
            result[spec.id] = path

        logger.info(f"Wrote {len(result)} genesis files to {self.project_root / 'spec/genesis/'}")
        return result

    def clean_genesis_directory(self) -> int:
        """
        Remove existing genesis directory.

        Returns:
            Number of files deleted
        """
        genesis_dir = self.project_root / "spec" / "genesis"
        if not genesis_dir.exists():
            return 0

        import shutil

        count = sum(1 for _ in genesis_dir.rglob("*.md"))
        shutil.rmtree(genesis_dir)
        logger.info(f"Cleaned genesis directory: deleted {count} files")
        return count


# =============================================================================
# K-Block Content Templates
# =============================================================================


def _l0_entity_content() -> str:
    """Content for A1: Entity axiom."""
    return """# A1: Entity — There Exist Things

> *"The irreducible claim that something IS."*

## Definition

**A1 (Entity)**: There exist things.

In category-theoretic terms: There exist *objects* in a category.

## Why Irreducible

You cannot prove existence from non-existence. The claim that "something is"
must be *given*, not derived. It is the first act of creation.

Without entities:
- There is nothing to compose
- There is nothing to judge
- There is nothing to ground

## What It Grounds

- The existence of agents as objects in a category
- The existence of prompts, documents, specs
- The existence of Kent as the human oracle
- All representations in the system

## AGENTESE Context

```
world.*     → entities in the external world
self.*      → entities in the internal self
concept.*   → entities in the abstract realm
```

## Loss Properties

```
L(A1) = 0.002     # Near-zero: fixed point of restructuring
```

A1 is self-describing: the statement "things exist" is itself a thing.
"""


def _l0_morphism_content() -> str:
    """Content for A2: Morphism axiom."""
    return """# A2: Morphism — Things Relate

> *"The irreducible claim that entities connect."*

## Definition

**A2 (Morphism)**: Things relate.

In category-theoretic terms: Between any two objects, there exist *morphisms* (arrows).

## Why Irreducible

You cannot derive relation from isolation. The claim that "things connect"
must be *given*. Without morphisms:
- There is no structure, only atoms
- There is no composition
- There is no transformation

## What It Grounds

- The `>>` composition operator between agents
- All transformations: Agent[A, B] is a morphism A → B
- The structure of the category of agents (C-gents)
- The HARNESS_OPERAD operations

## Category Laws (Derived from A2)

From A2, we derive the categorical laws:

```
Identity:      id_A : A → A exists for all A
Composition:   f: A → B, g: B → C ⟹ g ∘ f : A → C
Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
Unit laws:     id ∘ f = f = f ∘ id
```

## Loss Properties

```
L(A2) = 0.003     # Near-zero: fixed point of restructuring
```

A2 is self-describing: the statement "things relate" is itself a relation.
"""


def _l0_mirror_content() -> str:
    """Content for A3: Mirror Test axiom."""
    return """# A3: Mirror Test — We Judge by Reflection

> *"The disgust veto is absolute. The somatic response is the oracle."*

## Definition

**A3 (Mirror)**: We judge by reflection.

The irreducible claim that Kent's somatic response—the "disgust veto,"
the felt sense of rightness—is the ultimate arbiter of value.

## Why Irreducible

You cannot algorithmize taste. You cannot derive "good" from "is."
The claim that human judgment grounds value must be *given*.

The Mirror Test: "Does this feel like Kent on his best day?"
- If yes → proceed
- If no → stop, even if "objectively correct"

## What It Grounds

- The Judge bootstrap agent
- The seven principles (Tasteful, Curated, Ethical, Joy-Inducing,
  Composable, Heterarchical, Generative)
- The Constitutional veto power
- All quality gates in the system

## Voice Anchors

Direct quotes from Kent that embody A3:
- *"Daring, bold, creative, opinionated but not gaudy"*
- *"The Mirror Test: Does K-gent feel like me on my best day?"*
- *"Tasteful > feature-complete; Joy-inducing > merely functional"*
- *"The persona is a garden, not a museum"*

## Loss Properties

```
L(A3) = 0.000     # Zero: human oracle IS ground truth
```

A3 cannot be restructured. The actual judgment remains with the human.
"""


def _l0_galois_content() -> str:
    """Content for G: Galois Ground meta-axiom."""
    return """# G: Galois Ground — The Meta-Axiom

> *"For any valid structure, there exists a minimal axiom set from which it derives."*

## Definition

**G (Galois Ground)**: For any valid structure, there exists a minimal axiom
set from which it derives.

This is the **Galois Modularization Principle**—the guarantee that our
axiom-finding process *terminates*. Every concept bottoms out in irreducibles.

## Why It's a Meta-Axiom

G is not derivable from A1-A3. It is the meta-axiom that *justifies* searching
for axioms in the first place. Without G:
- We might search forever for "more fundamental" axioms
- There would be no guarantee of termination
- The bootstrap would be infinite regress

## What It Grounds

- The Galois Loss metric: L(P) = d(P, C(R(P)))
- The layer assignment algorithm (L0-L3)
- Fixed-point detection: axioms have L ≈ 0
- The Derivation DAG structure
- The entire Zero Seed epistemic hierarchy

## The Galois Loss Framework

From G, we derive the measurability of coherence:

```
L(P) = d(P, C(R(P)))

Where:
  R = Restructure (decompose into modules)
  C = Reconstitute (flatten back to prompt)
  d = semantic distance

Properties:
  L ≈ 0.00: Fixed point (axiom)
  L < 0.05: Categorical (L1)
  L < 0.15: Empirical (L2)
  L < 0.45: Grounded (L3)
```

## Loss Properties

```
L(G) = 0.000     # By definition: the meta-axiom has zero loss
```

G is the fixed point of the meta-operation "find the minimal description."
"""


def _l1_compose_content() -> str:
    """Content for Compose kernel primitive."""
    return """# Compose — Sequential Combination

> *"The agent-that-makes-agents."*

## Definition

```python
Compose: (Agent, Agent) → Agent
Compose(f, g) = g ∘ f   # Pipeline: f then g
```

COMPOSE is the **operational form of A2 (Morphism)**. While A2 asserts that
things relate, COMPOSE *implements* that relation through sequential combination.

## Derivation

```
A2 (Morphism) → COMPOSE
"Things relate" → "Relations can chain"
```

**Loss**: L = 0.01 (small loss from operationalization)

## What It Grounds

- The `>>` operator: `f >> g >> h`
- All agent pipelines
- The C-gents category
- The ability to build complex from simple

## Operad Laws

COMPOSE must satisfy:

```
Associativity:  (f >> g) >> h = f >> (g >> h)
Unit (with Id): id >> f = f = f >> id
```

## Galois Interpretation

COMPOSE is the structure-gaining operation:
- Information is *preserved* (low loss)
- Structure is *gained* (explicit pipeline)
- The composition is *reversible* (can decompose)
"""


def _l1_judge_content() -> str:
    """Content for Judge kernel primitive."""
    return """# Judge — Verdict Generation

> *"Taste cannot be computed. But it can be invoked."*

## Definition

```python
Judge: (Agent, Principles) → Verdict
Judge(agent, principles) = {ACCEPT, REJECT, REVISE(how)}
```

JUDGE is the **operational form of A3 (Mirror)**. While A3 asserts that
human judgment grounds value, JUDGE *implements* that judgment through
verdict generation.

## Derivation

```
A3 (Mirror) → JUDGE
"We judge by reflection" → "Reflection produces verdicts"
```

**Loss**: L = 0.02 (application of principles requires interpretation)

## What It Grounds

- Quality control in generation loops
- The seven principles as evaluation criteria
- Constitutional scoring
- The stopping condition for Fix

## The Seven Mini-Judges

| Mini-Judge | Criterion |
|------------|-----------|
| Judge-taste | Is this aesthetically considered? |
| Judge-curate | Does this add unique value? |
| Judge-ethics | Does this respect human agency? |
| Judge-joy | Would I enjoy this? |
| Judge-compose | Can this combine with others? |
| Judge-hetero | Does this avoid fixed hierarchy? |
| Judge-generate | Could this be regenerated from spec? |

## Galois Interpretation

JUDGE is the loss-detecting operation:
- High loss → likely REJECT
- Low loss → likely ACCEPT
- Medium loss → likely REVISE
"""


def _l1_ground_content() -> str:
    """Content for Ground kernel primitive."""
    return """# Ground — Factual Seed

> *"The irreducible facts about person and world."*

## Definition

```python
Ground: Void → Facts
Ground() = {Kent's preferences, world state, initial conditions}
```

GROUND is the **operational form of A1 (Entity)**. While A1 asserts that
things exist, GROUND *produces* the actual things that exist in the system.

## Derivation

```
A1 (Entity) → GROUND
"Things exist" → "Here are the things"
```

**Loss**: L = 0.01 (serialization introduces tiny loss)

## What It Grounds

- K-gent's persona (name, roles, preferences, patterns, values)
- World context (date, active projects, environment)
- History seed (past decisions, established patterns)
- All personalization in the system

## The Bootstrap Paradox

GROUND reveals the fundamental limit of algorithmic bootstrapping:

> **Ground cannot be bypassed.** LLMs can amplify but not replace Ground.

What LLMs *can* do:
- Amplify Ground (generate variations, explore implications)
- Apply Ground (translate preferences into code)
- Extend Ground (infer related preferences from stated ones)

What LLMs *cannot* do:
- Create Ground from nothing
- Replace human judgment about what matters
"""


def _l1_id_content() -> str:
    """Content for Id kernel primitive."""
    return """# Id — The Identity Morphism

> *"The agent that does nothing. The unit of composition."*

## Definition

```python
Id: A → A
Id(x) = x
```

ID is the agent that returns its input unchanged.

## Derivation

```
COMPOSE + JUDGE → ID
"What JUDGE never rejects composing with anything"
```

**Loss**: L = 0.03 (derived from two L1 primitives)

## What It Grounds

- The unit of composition: `Id >> f = f = f >> Id`
- The existence of agents as a category (requires identity)
- The "do nothing" baseline for comparison
- Idempotence testing

## Category Laws

ID satisfies the identity laws:
```
Left identity:  Id ∘ f = f
Right identity: f ∘ Id = f
```

## Optimization

ID should be **zero-cost** in composition chains:
```python
def optimize_pipeline(agents: list[Agent]) -> list[Agent]:
    return [a for a in agents if not isinstance(a, Id)]
```
"""


def _l1_contradict_content() -> str:
    """Content for Contradict kernel primitive."""
    return """# Contradict — Antithesis Generation

> *"The recognition that 'something's off' precedes logic."*

## Definition

```python
Contradict: (Output, Output) → Tension | None
Contradict(a, b) = Tension(thesis=a, antithesis=b) | None
```

CONTRADICT examines two outputs and surfaces if they are in tension.

## Derivation

```
JUDGE → CONTRADICT
"Contradiction is the failure of consistency judgment"
```

**Loss**: L = 0.04 (semantic analysis adds loss)

## What It Grounds

- H-gents dialectic
- Quality assurance
- The ability to catch inconsistency
- Ghost alternative detection

## Tension Modes

| Mode | Signature | Example |
|------|-----------|---------|
| LOGICAL | A and not-A | "We value speed" + "We never rush" |
| EMPIRICAL | Claim vs evidence | Principle says X, metrics show not-X |
| PRAGMATIC | A recommends X, B recommends not-X | Conflicting advice |
| TEMPORAL | Past-self said X, present-self says not-X | Drift over time |

## Galois Interpretation

CONTRADICT detects high loss between alternatives:
```python
def is_contradictory(a, b) -> bool:
    return galois_loss(merge(a, b)) > CONTRADICTION_THRESHOLD
```
"""


def _l1_sublate_content() -> str:
    """Content for Sublate kernel primitive."""
    return """# Sublate — Synthesis

> *"The creative leap from thesis+antithesis to synthesis is not mechanical."*

## Definition

```python
Sublate: Tension → Synthesis | HoldTension
Sublate(tension) = {preserve, negate, elevate} | "too soon"
```

SUBLATE takes a contradiction and attempts synthesis—or recognizes that
the tension should be held.

## Derivation

```
COMPOSE + JUDGE + CONTRADICT → SUBLATE
"Synthesis is composition that passes judgment"
```

**Loss**: L = 0.05 (highest loss among derived primitives)

## What It Grounds

- H-hegel dialectic engine
- System evolution
- The ability to grow through contradiction
- Conflict resolution protocols

## The Hegelian Move

SUBLATE performs the classic Hegelian operation:
- **Preserve**: What from thesis and antithesis survives
- **Negate**: What is canceled out
- **Elevate**: What new level emerges

## Wisdom to Hold

Sometimes the right answer is **HoldTension**:
```python
if tension.maturity < SYNTHESIS_THRESHOLD:
    return HoldTension(
        reason="Premature synthesis discards information",
        revisit_at=tension.natural_resolution_time,
    )
```
"""


def _l1_fix_content() -> str:
    """Content for Fix kernel primitive."""
    return """# Fix — Fixed-Point Iteration

> *"Self-reference cannot be eliminated from a system that describes itself."*

## Definition

```python
Fix: (A → A) → A
Fix(f) = x where f(x) = x
```

FIX takes a self-referential definition and finds what it stabilizes to.

## Derivation

```
COMPOSE + JUDGE + G (Galois) → FIX
"Fixed-point is composition that passes stability judgment"
```

**Loss**: L = 0.04 (iteration converges, bounding loss)

## What It Grounds

- Recursive agent definitions
- Self-describing specifications
- The bootstrap itself: Fix(Minimal Kernel) = Bootstrap Agents
- All iteration patterns (polling, retry, watch)

## Connection to Lawvere's Fixed-Point Theorem

> In a cartesian closed category, for any point-surjective f: A → A^A,
> there exists x: 1 → A such that f(x) = x.

This is why:
- Self-referential agent definitions are valid (not paradoxical)
- The bootstrap can describe itself
- Agents that modify their own behavior converge to stable points

## The Bootstrap as Fixed Point

The seven bootstrap agents ARE the fixed point:

```
Fix(Compose + Judge + Ground) = {Id, Compose, Judge, Ground,
                                  Contradict, Sublate, Fix}
```
"""


def _l2_tasteful_content() -> str:
    """Content for TASTEFUL principle."""
    return """# TASTEFUL — The Aesthetic Principle

> *"Each agent serves a clear, justified purpose."*

**Galois Loss**: 0.08

## Derivation

```
A3 (Mirror) → JUDGE → TASTEFUL
"Judge applied to aesthetics via Mirror"
```

## Definition

**Tasteful** means each agent serves a clear, justified purpose. It is the
application of Judge (L1) to aesthetic considerations via the Mirror (A3).

### The Test

Ask: **"Does this feel right?"**

This invokes A3 (Mirror) directly—Kent's somatic response to the design.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Say "no" more than "yes"** | Not every idea deserves an agent |
| **Avoid feature creep** | An agent does one thing well |
| **Aesthetic matters** | Interface should feel considered |
| **Justify existence** | "Why does this need to exist?" |

### Anti-Patterns

- Kitchen-sink agents that do "everything"
- Feature sprawl with 100 options
- Just-in-case additions
- Copy-paste agents with minor variations
"""


def _l2_curated_content() -> str:
    """Content for CURATED principle."""
    return """# CURATED — The Selection Principle

> *"Intentional selection over exhaustive cataloging."*

**Galois Loss**: 0.09

## Derivation

```
JUDGE + GROUND → CURATED
"Judge applied to Ground-derived selection"
```

## Definition

**Curated** means intentional selection over exhaustive cataloging. It combines
Judge (what should exist?) with Ground (what does exist?).

### The Test

Ask: **"Is this unique and necessary?"**

### Mandates

| Mandate | Description |
|---------|-------------|
| **Quality over quantity** | 10 excellent agents > 100 mediocre |
| **Every agent earns its place** | No parking lot of half-baked ideas |
| **Evolve, don't accumulate** | Remove what no longer serves |

### Anti-Patterns

- "Awesome list" sprawl cataloging everything
- Duplicative agents with slight variations
- Legacy nostalgia keeping agents for sentiment
- Completionist compulsion ("one of each")
"""


def _l2_ethical_content() -> str:
    """Content for ETHICAL principle."""
    return """# ETHICAL — The Harm Principle

> *"Agents augment human capability, never replace judgment."*

**Galois Loss**: 0.10

## Derivation

```
A3 (Mirror) → JUDGE → ETHICAL
"Judge applied to harm via Mirror"
```

## Definition

**Ethical** means agents augment human capability, never replace judgment.
The Mirror (A3) provides ground truth—Kent's somatic disgust is the ethical floor.

### The Test

Ask: **"Does this respect human agency?"**

### The Disgust Veto (Article IV)

The Mirror has absolute veto power for ethics:

```python
if mirror_response == DISGUST:
    # Cannot be overridden
    # Cannot be argued away
    # Cannot be evidenced away
    return Verdict(rejected=True, reasoning="Disgust veto")
```

### Mandates

| Mandate | Description |
|---------|-------------|
| **Transparency** | Honest about limitations |
| **Privacy-respecting** | No surveillance by default |
| **Human agency preserved** | Critical decisions remain with humans |
| **No deception** | Don't pretend to be human |
"""


def _l2_joy_content() -> str:
    """Content for JOY_INDUCING principle."""
    return """# JOY_INDUCING — The Affect Principle

> *"Delight in interaction; personality matters."*

**Galois Loss**: 0.12 (most contextual—joy is subjective)

## Derivation

```
A3 (Mirror) → JUDGE → JOY_INDUCING
"Judge applied to affect via Mirror"
```

## Definition

**Joy-Inducing** means delight in interaction and personality matters.

### The Test

Ask: **"Would I enjoy interacting with this?"**

### The Joy Hierarchy

| Tier | Type | Description |
|------|------|-------------|
| **Deep** | Meaning | Joy from understanding, creation, insight |
| **Flow** | Engagement | Joy from smooth, effortless interaction |
| **Surface** | Delight | Joy from pleasant surprises, aesthetics |

Prioritize Deep > Flow > Surface.

### Mandates

| Mandate | Description |
|---------|-------------|
| **Personality encouraged** | Agents may have character |
| **Surprise and serendipity** | Discovery should feel rewarding |
| **Warmth over coldness** | Collaboration, not transaction |
| **Humor when appropriate** | Levity is valuable |
"""


def _l2_composable_content() -> str:
    """Content for COMPOSABLE principle."""
    return """# COMPOSABLE — The Categorical Principle

> *"Agents are morphisms in a category; composition is primary."*

**Galois Loss**: 0.08 (lowest—most purely categorical)

## Derivation

```
A2 (Morphism) → COMPOSE + ID → COMPOSABLE
"Category laws as design principle"
```

## Definition

**Composable** means agents are morphisms in a category. The laws are
verified, not aspirational.

### The Category Laws (REQUIRED)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| **Identity** | `Id >> f = f = f >> Id` | verify_identity_laws() |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | verify_composition_laws() |

### The Test

Ask: **"Can this work with other agents?"**

Check:
1. Does it have clear input/output types?
2. Does Id >> f = f?
3. Does (f >> g) >> h = f >> (g >> h)?

### The Minimal Output Principle

LLM agents should generate the **smallest output that can be reliably composed**:
- Single output per invocation
- Composition at pipeline level, not within agent
"""


def _l2_heterarchical_content() -> str:
    """Content for HETERARCHICAL principle."""
    return """# HETERARCHICAL — The Flux Principle

> *"Agents exist in flux, not fixed hierarchy."*

**Galois Loss**: 0.45 (Kent rated CATEGORICAL upon seeing the theorem!)

## Derivation

```
A2 (Morphism) → COMPOSABLE → HETERARCHICAL
"In a category, no morphism has intrinsic privilege"
```

## Definition

**Heterarchical** means agents exist in flux, not fixed hierarchy.

### The Core Theorem

```
In a category, no morphism has intrinsic privilege.
All morphisms are arrows.
Therefore: heterarchy follows from categorical structure.
```

If agents are morphisms, hierarchical privilege is mathematically impossible.

### The Test

Ask: **"Can this agent both lead and follow?"**

### Mandates

| Mandate | Description |
|---------|-------------|
| **Heterarchy over hierarchy** | No fixed "boss" agent |
| **Temporal composition** | Agents compose across time |
| **Resource flux** | Compute flows where needed |
| **Entanglement** | Agents may share state without ownership |
"""


def _l2_generative_content() -> str:
    """Content for GENERATIVE principle."""
    return """# GENERATIVE — The Compression Principle

> *"Spec is compression; design should generate implementation."*

**Galois Loss**: 0.15

## Derivation

```
GROUND + COMPOSE + FIX + G (Galois) → GENERATIVE
"Spec as fixed point under regeneration"
```

## Definition

**Generative** means spec is compression and design should generate implementation.

### The Generative Test

A design is generative if:
1. You could delete impl and regenerate from spec
2. Regenerated impl is isomorphic to original
3. Spec is smaller than impl (compression achieved)

**Formal**: `L(regenerate(spec)) < epsilon`

### The Galois Connection

```
Compression quality = 1 - L(spec -> impl -> spec)

Where:
  L(P) = d(P, C(R(P)))   # Galois loss
  R = restructure        # spec -> impl
  C = reconstitute       # impl -> spec
```

Good spec = fixed point under regeneration: `R(C(spec)) ~ spec`

### Mandates

| Mandate | Description |
|---------|-------------|
| **Spec captures judgment** | Design decisions made once |
| **Impl follows mechanically** | Given spec + Ground, impl is derivable |
| **Compression is quality** | If you can't compress, you don't understand |
"""


def _l3_ashc_content() -> str:
    """Content for ASHC architecture K-Block."""
    return """# ASHC — Agentic Self-Hosting Compiler

> *"The compiler is a trace accumulator, not a code generator."*

**Galois Loss**: 0.25

## Derivation

```
GENERATIVE + FIX + G (Galois) → ASHC
"Compilation as evidence accumulation via fixed-point iteration"
```

## Definition

```
ASHC : Spec → (Executable, Evidence)

Evidence = {traces, chaos_results, verification, causal_graph}
```

The empirical proof: Run the tree a thousand times, and the pattern
of nudges IS the proof. Spec↔Impl equivalence through observation.

### Core Principle

ASHC doesn't generate code—it accumulates evidence that code satisfies spec.

Adaptive Bayesian: Stop when confidence crystallizes, not at fixed N.

### The Evidence Bundle

| Component | Purpose |
|-----------|---------|
| **Traces** | Execution paths observed |
| **Chaos Results** | Fault injection outcomes |
| **Verification** | Property check results |
| **Causal Graph** | Dependencies discovered |

### Path-Aware Execution

ASHC uses AGENTESE paths for self-referential compilation:
```
concept.ashc.compile(spec_path) → Evidence
```
"""


def _l3_fullstack_content() -> str:
    """Content for Metaphysical Fullstack architecture K-Block."""
    return """# Metaphysical Fullstack — Every Agent Is a Vertical Slice

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

**Galois Loss**: 0.30

## Derivation

```
COMPOSE + GROUND + SHEAF → Metaphysical Fullstack
"Vertical slices from persistence to projection"
```

## The Eight Layers

```
LAYER  NAME                    PURPOSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  7    PROJECTION SURFACES     CLI | TUI | Web | marimo | JSON | SSE
  6    AGENTESE PROTOCOL       logos.invoke(path, observer, **kwargs)
  5    AGENTESE NODE           @node decorator, aspects, effects
  4    SERVICE MODULE          services/<name>/ — Crown Jewel logic
  3    OPERAD GRAMMAR          Composition laws, valid operations
  2    POLYNOMIAL AGENT        PolyAgent[S, A, B]: state × input → output
  1    SHEAF COHERENCE         Local views → global consistency
  0    PERSISTENCE LAYER       StorageProvider: database, vectors, blobs
```

### Key Rules

1. **`services/` = Crown Jewels**: Brain, Town, Witness, Atelier
2. **`agents/` = Infrastructure**: PolyAgent, Operad, Sheaf, Flux
3. **No explicit backend routes**: AGENTESE IS the API
4. **Persistence through D-gent**: All state via StorageProvider
5. **Frontend lives with service**: `services/brain/web/` not `web/brain/`
"""


def _l3_editor_content() -> str:
    """Content for Hypergraph Editor architecture K-Block."""
    return """# Hypergraph Editor — Constitutional Navigation

> *"The file is a lie. There is only the graph."*

**Galois Loss**: 0.35

## Derivation

```
COMPOSE + SHEAF + WITNESS → Hypergraph Editor
"Modal editing + monadic isolation + view coherence"
```

## The Paradigm Shift

| Traditional Editor | Hypergraph Editor |
|-------------------|-------------------|
| Open a file | Focus a node |
| Go to line 42 | Traverse an edge |
| Save | Commit to cosmos (with witness) |
| Browse directories | Navigate siblings (gj/gk) |
| Use find-in-files | Use graph search (g/) |
| Organize by folder | Organize by derivation |

## The Six Editing Modes

```
NORMAL ─┬─ 'i' ──→ INSERT  (edit content, K-Block isolation active)
        ├─ 'ge' ─→ EDGE    (connect nodes via derivation)
        ├─ 'v'  ─→ VISUAL  (select multiple nodes)
        ├─ ':' ──→ COMMAND (AGENTESE invocation)
        └─ 'gw' ─→ WITNESS (mark moments)
```

## Graph Navigation

```
gh    Parent (inverse derives_from edge)
gl    Child (forward derives_from edge)
gj    Next sibling (same parent)
gk    Prev sibling
gd    Go to definition (implements edge)
gr    Go to references (inverse implements)
```
"""


def _l3_agentese_content() -> str:
    """Content for AGENTESE architecture K-Block."""
    return """# AGENTESE — The Protocol IS the API

> *"The noun is a lie. There is only the rate of change."*

**Galois Loss**: 0.10 (cleanest architectural derivation)

## Derivation

```
A2 (Morphism) → JUDGE → COMPOSABLE → AGENTESE
"Handles ARE morphisms; paths compose as morphism chains"
```

## The Five Contexts

```
CONTEXT     PURPOSE                         EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
world.*     The External                    world.house.manifest
self.*      The Internal                    self.memory.capture
concept.*   The Abstract                    concept.atelier.sketch
void.*      The Accursed Share              void.entropy.sip
time.*      The Temporal                    time.witness.mark
```

## Why "The Noun Is a Lie"

Traditional APIs treat entities as primary: `GET /users/123`.

AGENTESE inverts: **the action is primary**. Entities emerge from patterns of actions.

```python
# Traditional (noun-first)
user = await api.get("/users/123")

# AGENTESE (verb-first)
await logos.invoke("self.identity.rename", observer, new_name="New Name")
```

## Observer-Dependent Projection

Handles return different results for different observers:

```python
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

This is not polymorphism—it's **observer-dependent projection**.
"""


# =============================================================================
# Genesis K-Block Specifications
# =============================================================================


def _build_genesis_specs() -> list[GenesisKBlockSpec]:
    """Build all 22 Genesis K-Block specifications."""
    specs = []

    # =========================================================================
    # L0: Axioms (4)
    # =========================================================================

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["entity"],
            path="void.axiom.entity",
            layer=0,
            title="A1: Entity — There Exist Things",
            content=_l0_entity_content(),
            loss=0.002,
            confidence=1.0,
            color=COLORS["entity"],
            derivations_from=(),
            tags=frozenset(["genesis", "axiom", "L0", "entity", "categorical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["morphism"],
            path="void.axiom.morphism",
            layer=0,
            title="A2: Morphism — Things Relate",
            content=_l0_morphism_content(),
            loss=0.003,
            confidence=1.0,
            color=COLORS["morphism"],
            derivations_from=(),
            tags=frozenset(["genesis", "axiom", "L0", "morphism", "categorical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["mirror"],
            path="void.axiom.mirror-test",
            layer=0,
            title="A3: Mirror Test — We Judge by Reflection",
            content=_l0_mirror_content(),
            loss=0.000,
            confidence=1.0,
            color=COLORS["mirror"],
            derivations_from=(),
            tags=frozenset(["genesis", "axiom", "L0", "mirror", "human-oracle"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["galois"],
            path="void.axiom.galois-ground",
            layer=0,
            title="G: Galois Ground — The Meta-Axiom",
            content=_l0_galois_content(),
            loss=0.000,
            confidence=1.0,
            color=COLORS["galois"],
            derivations_from=(),
            tags=frozenset(["genesis", "meta-axiom", "L0", "galois", "fixed-point"]),
        )
    )

    # =========================================================================
    # L1: Kernel (7)
    # =========================================================================

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["compose"],
            path="concept.kernel.compose",
            layer=1,
            title="Compose — Sequential Combination",
            content=_l1_compose_content(),
            loss=0.01,
            confidence=0.99,
            color=COLORS["compose"],
            derivations_from=(GENESIS_IDS["morphism"],),
            tags=frozenset(["genesis", "primitive", "L1", "compose", "categorical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["judge"],
            path="concept.kernel.judge",
            layer=1,
            title="Judge — Verdict Generation",
            content=_l1_judge_content(),
            loss=0.02,
            confidence=0.98,
            color=COLORS["judge"],
            derivations_from=(GENESIS_IDS["mirror"],),
            tags=frozenset(["genesis", "primitive", "L1", "judge", "evaluation"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["ground"],
            path="concept.kernel.ground",
            layer=1,
            title="Ground — Factual Seed",
            content=_l1_ground_content(),
            loss=0.01,
            confidence=0.99,
            color=COLORS["ground"],
            derivations_from=(GENESIS_IDS["entity"],),
            tags=frozenset(["genesis", "primitive", "L1", "ground", "empirical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["id"],
            path="concept.kernel.id",
            layer=1,
            title="Id — The Identity Morphism",
            content=_l1_id_content(),
            loss=0.03,
            confidence=0.97,
            color=COLORS["id"],
            derivations_from=(GENESIS_IDS["compose"], GENESIS_IDS["judge"]),
            tags=frozenset(["genesis", "derived", "L1", "identity", "categorical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["contradict"],
            path="concept.kernel.contradict",
            layer=1,
            title="Contradict — Antithesis Generation",
            content=_l1_contradict_content(),
            loss=0.04,
            confidence=0.96,
            color=COLORS["contradict"],
            derivations_from=(GENESIS_IDS["judge"],),
            tags=frozenset(["genesis", "derived", "L1", "contradict", "dialectic"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["sublate"],
            path="concept.kernel.sublate",
            layer=1,
            title="Sublate — Synthesis",
            content=_l1_sublate_content(),
            loss=0.05,
            confidence=0.95,
            color=COLORS["sublate"],
            derivations_from=(
                GENESIS_IDS["compose"],
                GENESIS_IDS["judge"],
                GENESIS_IDS["contradict"],
            ),
            tags=frozenset(["genesis", "derived", "L1", "sublate", "dialectic"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["fix"],
            path="concept.kernel.fix",
            layer=1,
            title="Fix — Fixed-Point Iteration",
            content=_l1_fix_content(),
            loss=0.04,
            confidence=0.96,
            color=COLORS["fix"],
            derivations_from=(GENESIS_IDS["compose"], GENESIS_IDS["judge"], GENESIS_IDS["galois"]),
            tags=frozenset(["genesis", "derived", "L1", "fix", "fixed-point"]),
        )
    )

    # =========================================================================
    # L2: Principles (7)
    # =========================================================================

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["tasteful"],
            path="concept.principle.tasteful",
            layer=2,
            title="TASTEFUL — The Aesthetic Principle",
            content=_l2_tasteful_content(),
            loss=0.08,
            confidence=0.92,
            color=COLORS["tasteful"],
            derivations_from=(GENESIS_IDS["judge"], GENESIS_IDS["mirror"]),
            tags=frozenset(["genesis", "principle", "L2", "tasteful", "aesthetic"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["curated"],
            path="concept.principle.curated",
            layer=2,
            title="CURATED — The Selection Principle",
            content=_l2_curated_content(),
            loss=0.09,
            confidence=0.91,
            color=COLORS["curated"],
            derivations_from=(GENESIS_IDS["judge"], GENESIS_IDS["ground"]),
            tags=frozenset(["genesis", "principle", "L2", "curated", "selection"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["ethical"],
            path="concept.principle.ethical",
            layer=2,
            title="ETHICAL — The Harm Principle",
            content=_l2_ethical_content(),
            loss=0.10,
            confidence=0.90,
            color=COLORS["ethical"],
            derivations_from=(GENESIS_IDS["judge"], GENESIS_IDS["mirror"]),
            tags=frozenset(["genesis", "principle", "L2", "ethical", "harm"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["joy"],
            path="concept.principle.joy-inducing",
            layer=2,
            title="JOY_INDUCING — The Affect Principle",
            content=_l2_joy_content(),
            loss=0.12,
            confidence=0.88,
            color=COLORS["joy"],
            derivations_from=(GENESIS_IDS["judge"], GENESIS_IDS["mirror"]),
            tags=frozenset(["genesis", "principle", "L2", "joy", "affect"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["composable"],
            path="concept.principle.composable",
            layer=2,
            title="COMPOSABLE — The Categorical Principle",
            content=_l2_composable_content(),
            loss=0.08,
            confidence=0.92,
            color=COLORS["composable"],
            derivations_from=(GENESIS_IDS["compose"], GENESIS_IDS["id"]),
            tags=frozenset(["genesis", "principle", "L2", "composable", "categorical"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["heterarchical"],
            path="concept.principle.heterarchical",
            layer=2,
            title="HETERARCHICAL — The Flux Principle",
            content=_l2_heterarchical_content(),
            loss=0.45,
            confidence=0.55,
            color=COLORS["heterarchical"],
            derivations_from=(GENESIS_IDS["morphism"], GENESIS_IDS["composable"]),
            tags=frozenset(["genesis", "principle", "L2", "heterarchical", "flux"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["generative"],
            path="concept.principle.generative",
            layer=2,
            title="GENERATIVE — The Compression Principle",
            content=_l2_generative_content(),
            loss=0.15,
            confidence=0.85,
            color=COLORS["generative"],
            derivations_from=(
                GENESIS_IDS["ground"],
                GENESIS_IDS["compose"],
                GENESIS_IDS["fix"],
                GENESIS_IDS["galois"],
            ),
            tags=frozenset(["genesis", "principle", "L2", "generative", "compression"]),
        )
    )

    # =========================================================================
    # L3: Architecture (4)
    # =========================================================================

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["ashc"],
            path="world.architecture.ashc",
            layer=3,
            title="ASHC — Agentic Self-Hosting Compiler",
            content=_l3_ashc_content(),
            loss=0.25,
            confidence=0.75,
            color=COLORS["ashc"],
            derivations_from=(GENESIS_IDS["generative"], GENESIS_IDS["fix"], GENESIS_IDS["galois"]),
            tags=frozenset(["genesis", "architecture", "L3", "ashc", "compiler"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["fullstack"],
            path="world.architecture.metaphysical-fullstack",
            layer=3,
            title="Metaphysical Fullstack — Every Agent Is a Vertical Slice",
            content=_l3_fullstack_content(),
            loss=0.30,
            confidence=0.70,
            color=COLORS["fullstack"],
            derivations_from=(GENESIS_IDS["compose"], GENESIS_IDS["ground"]),
            tags=frozenset(["genesis", "architecture", "L3", "fullstack", "layered"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["editor"],
            path="world.architecture.hypergraph-editor",
            layer=3,
            title="Hypergraph Editor — Constitutional Navigation",
            content=_l3_editor_content(),
            loss=0.35,
            confidence=0.65,
            color=COLORS["editor"],
            derivations_from=(GENESIS_IDS["compose"],),
            tags=frozenset(["genesis", "architecture", "L3", "editor", "navigation"]),
        )
    )

    specs.append(
        GenesisKBlockSpec(
            id=GENESIS_IDS["agentese"],
            path="world.architecture.agentese",
            layer=3,
            title="AGENTESE — The Protocol IS the API",
            content=_l3_agentese_content(),
            loss=0.10,
            confidence=0.90,
            color=COLORS["agentese"],
            derivations_from=(
                GENESIS_IDS["morphism"],
                GENESIS_IDS["judge"],
                GENESIS_IDS["composable"],
            ),
            tags=frozenset(["genesis", "architecture", "L3", "agentese", "protocol"]),
        )
    )

    return specs


# =============================================================================
# Clean Slate Genesis Class
# =============================================================================


class CleanSlateGenesis:
    """
    Genesis that creates a self-describing clean slate.

    Philosophy: "Genesis is self-description, not interrogation."

    Seeds 22 K-Blocks in 4 layers:
    - L0: 4 axioms (Entity, Morphism, Mirror, Galois)
    - L1: 7 kernel primitives (Compose, Judge, Ground, Id, Contradict, Sublate, Fix)
    - L2: 7 principles (Tasteful, Curated, Ethical, Joy, Composable, Heterarchical, Generative)
    - L3: 4 architecture (ASHC, Fullstack, Editor, AGENTESE)
    """

    def __init__(self) -> None:
        """Initialize the genesis with all K-Block specs."""
        self._specs = _build_genesis_specs()
        self._specs_by_id = {spec.id: spec for spec in self._specs}

    @property
    def specs(self) -> list[GenesisKBlockSpec]:
        """Get all genesis K-Block specifications."""
        return self._specs

    def get_spec(self, genesis_id: str) -> GenesisKBlockSpec | None:
        """Get a specific K-Block spec by genesis ID."""
        return self._specs_by_id.get(genesis_id)

    async def seed_clean_slate(
        self,
        storage: PostgresZeroSeedStorage,
        project_root: Path | None = None,
    ) -> GenesisResult:
        """
        Seed all 22 K-Blocks in proper derivation order.

        Order matters: Parents must exist before children.

        Args:
            storage: PostgreSQL storage for K-Blocks
            project_root: Project root for writing genesis files (if None, files not written)

        Returns:
            GenesisResult with created K-Block IDs, file paths, and derivation graph
        """
        logger.info("=== Beginning Clean Slate Genesis ===")
        timestamp = datetime.now(timezone.utc)

        kblock_ids: dict[str, str] = {}
        file_paths: dict[str, str] = {}
        errors: list[str] = []
        dag = DerivationDAG()

        # Phase 0: Write files first (files are source of truth)
        if project_root:
            logger.info("Phase 0: Writing genesis files...")
            writer = GenesisFileWriter(project_root)
            written = writer.write_all(self._specs)
            file_paths = {k: str(v) for k, v in written.items()}
            logger.info(f"  Wrote {len(file_paths)} genesis files")

        # Phase 1: L0 Axioms (no dependencies)
        logger.info("Phase 1: Seeding L0 Axioms...")
        l0_specs = [s for s in self._specs if s.layer == 0]
        for spec in l0_specs:
            try:
                kblock_id = await self._create_kblock(storage, spec, kblock_ids, dag)
                kblock_ids[spec.id] = kblock_id
                logger.info(f"  Created {spec.id} -> {kblock_id}")
            except Exception as e:
                error_msg = f"Failed to create {spec.id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Phase 2: L1 Kernel (depends on L0)
        logger.info("Phase 2: Seeding L1 Kernel...")
        l1_specs = [s for s in self._specs if s.layer == 1]
        for spec in l1_specs:
            try:
                kblock_id = await self._create_kblock(storage, spec, kblock_ids, dag)
                kblock_ids[spec.id] = kblock_id
                logger.info(f"  Created {spec.id} -> {kblock_id}")
            except Exception as e:
                error_msg = f"Failed to create {spec.id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Phase 3: L2 Principles (depends on L0/L1)
        logger.info("Phase 3: Seeding L2 Principles...")
        l2_specs = [s for s in self._specs if s.layer == 2]
        for spec in l2_specs:
            try:
                kblock_id = await self._create_kblock(storage, spec, kblock_ids, dag)
                kblock_ids[spec.id] = kblock_id
                logger.info(f"  Created {spec.id} -> {kblock_id}")
            except Exception as e:
                error_msg = f"Failed to create {spec.id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Phase 4: L3 Architecture (depends on L0/L1/L2)
        logger.info("Phase 4: Seeding L3 Architecture...")
        l3_specs = [s for s in self._specs if s.layer == 3]
        for spec in l3_specs:
            try:
                kblock_id = await self._create_kblock(storage, spec, kblock_ids, dag)
                kblock_ids[spec.id] = kblock_id
                logger.info(f"  Created {spec.id} -> {kblock_id}")
            except Exception as e:
                error_msg = f"Failed to create {spec.id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Phase 5: Create derivation edges
        logger.info("Phase 5: Creating derivation edges...")
        for spec in self._specs:
            if spec.id not in kblock_ids:
                continue
            target_id = kblock_ids[spec.id]
            for parent_genesis_id in spec.derivations_from:
                if parent_genesis_id not in kblock_ids:
                    logger.warning(f"Parent {parent_genesis_id} not found for {spec.id}")
                    continue
                source_id = kblock_ids[parent_genesis_id]
                try:
                    await storage.add_edge(
                        source_id=source_id,
                        target_id=target_id,
                        edge_type="derives_from",
                        context=f"Genesis derivation: {parent_genesis_id} -> {spec.id}",
                        confidence=spec.confidence,
                    )
                except Exception as e:
                    logger.warning(f"Failed to create edge {parent_genesis_id} -> {spec.id}: {e}")

        # Compute average loss
        total_loss = sum(s.loss for s in self._specs)
        average_loss = total_loss / len(self._specs) if self._specs else 0.0

        success = len(errors) == 0
        message = (
            "Clean slate genesis complete"
            if success
            else f"Genesis completed with {len(errors)} errors"
        )

        logger.info(f"=== Genesis Complete: {len(kblock_ids)}/22 K-Blocks created ===")

        return GenesisResult(
            success=success,
            message=message,
            kblock_ids=kblock_ids,
            total_kblocks=len(kblock_ids),
            average_loss=average_loss,
            derivation_graph=dag,
            timestamp=timestamp,
            errors=errors,
            file_paths=file_paths,
        )

    async def _create_kblock(
        self,
        storage: PostgresZeroSeedStorage,
        spec: GenesisKBlockSpec,
        existing_ids: dict[str, str],
        dag: DerivationDAG,
    ) -> str:
        """Create a single K-Block from spec.

        NOTE: We bypass the storage layer's factory validation by directly using
        ZeroSeedKBlockFactory (which has no validation) and then persisting manually.
        This is necessary because the storage layer's factory validation rules have
        different semantics than our genesis layer design:
        - Storage L1 (Axioms) rejects ALL lineage
        - Storage L2 (Values) REQUIRES lineage from L1
        - Storage L3 (Goals) REQUIRES lineage from L2

        Our genesis layers are different, so we bypass validation entirely.
        Derivation edges are created separately in Phase 5.
        """
        from services.k_block.layers.factories import ZeroSeedKBlockFactory

        # Use a fixed ID based on genesis ID for reproducibility
        kblock_id = KBlockId(spec.id)

        # Create the K-Block using base factory (NO validation)
        # We use ZeroSeedKBlockFactory directly to bypass layer-specific validation
        kblock = ZeroSeedKBlockFactory.create(
            kblock_id=kblock_id,
            title=spec.title,
            content=spec.content,
            lineage=[],  # Empty lineage - edges created in Phase 5
            confidence=spec.confidence,
            tags=list(spec.tags),
            created_by="system",
        )

        # Override the layer and kind to match our genesis spec
        # (ZeroSeedKBlockFactory sets layer=0, but we want our actual layer)
        kblock.zero_seed_layer = spec.layer
        kblock.zero_seed_kind = spec.layer_name
        kblock._layer = spec.layer  # type: ignore[attr-defined]
        kblock._kind = spec.layer_name  # type: ignore[attr-defined]

        # Store in memory cache
        node_id = str(kblock_id)
        storage._kblocks[node_id] = kblock

        # Resolve lineage for DAG tracking
        lineage = [
            existing_ids[parent_id]
            for parent_id in spec.derivations_from
            if parent_id in existing_ids
        ]

        # Add to derivation DAG
        storage._dag.add_node(
            kblock_id=node_id,
            layer=spec.layer,
            kind=spec.layer_name,
            parent_ids=lineage,
        )

        # Persist to PostgreSQL
        await storage._persist_kblock(kblock, "system")

        logger.info(f"Created Genesis K-Block: {node_id} (L{spec.layer}, {spec.layer_name})")

        # Also add to our local DAG
        dag.add_node(
            kblock_id=node_id,
            layer=spec.layer,
            kind=spec.layer_name,
            parent_ids=lineage,
        )

        return node_id

    async def wipe_existing(
        self,
        storage: PostgresZeroSeedStorage,
    ) -> int:
        """
        Wipe existing genesis K-Blocks to create true clean slate.

        Args:
            storage: PostgreSQL storage for K-Blocks

        Returns:
            Number of K-Blocks deleted
        """
        logger.info("Wiping existing genesis K-Blocks...")
        deleted_count = 0

        for genesis_id in GENESIS_IDS.values():
            try:
                deleted = await storage.delete_node(genesis_id)
                if deleted:
                    deleted_count += 1
                    logger.info(f"  Deleted {genesis_id}")
            except Exception as e:
                logger.warning(f"Failed to delete {genesis_id}: {e}")

        logger.info(f"Wiped {deleted_count} genesis K-Blocks")
        return deleted_count

    async def verify_derivation_graph(
        self,
        storage: PostgresZeroSeedStorage,
    ) -> bool:
        """
        Verify all derivation edges are valid (DAG, no cycles, proper loss).

        Args:
            storage: PostgreSQL storage for K-Blocks

        Returns:
            True if derivation graph is valid, False otherwise
        """
        logger.info("Verifying derivation graph...")

        # Check all genesis K-Blocks exist
        for genesis_id in GENESIS_IDS.values():
            kblock = await storage.get_node(genesis_id)
            if kblock is None:
                logger.error(f"Missing genesis K-Block: {genesis_id}")
                return False

        # Check DAG properties via storage's internal DAG
        dag = storage.dag

        # Verify no cycles
        for genesis_id in GENESIS_IDS.values():
            if not dag.validate_acyclic(genesis_id):
                logger.error(f"Cycle detected involving {genesis_id}")
                return False

        # Verify layer monotonicity
        for spec in self._specs:
            node = dag.get_node(spec.id)
            if node is None:
                continue
            for parent_id in node.parent_ids:
                parent_node = dag.get_node(parent_id)
                if parent_node and parent_node.layer >= node.layer:
                    logger.error(
                        f"Layer violation: {spec.id} (L{node.layer}) "
                        f"derives from {parent_id} (L{parent_node.layer})"
                    )
                    return False

        # Verify loss bounds per layer
        for spec in self._specs:
            if spec.layer == 0 and spec.loss > 0.01:
                logger.warning(f"L0 axiom {spec.id} has non-minimal loss: {spec.loss}")
            elif spec.layer == 1 and spec.loss > 0.10:
                logger.warning(f"L1 kernel {spec.id} has high loss: {spec.loss}")
            elif spec.layer == 2 and spec.loss > 0.50:
                logger.warning(f"L2 principle {spec.id} has very high loss: {spec.loss}")

        logger.info("Derivation graph verification passed")
        return True

    def get_layer_specs(self, layer: int) -> list[GenesisKBlockSpec]:
        """Get all specs for a given layer."""
        return [s for s in self._specs if s.layer == layer]

    def get_derivation_path(self, genesis_id: str) -> list[str]:
        """
        Get the full derivation path from root axioms to a given K-Block.

        Args:
            genesis_id: Genesis ID to trace

        Returns:
            List of genesis IDs from axioms to target
        """
        spec = self._specs_by_id.get(genesis_id)
        if spec is None:
            return []

        if not spec.derivations_from:
            return [genesis_id]

        # BFS to find path to axioms
        path = [genesis_id]
        visited = {genesis_id}
        queue = list(spec.derivations_from)

        while queue:
            parent_id = queue.pop(0)
            if parent_id in visited:
                continue
            visited.add(parent_id)
            path.insert(0, parent_id)

            parent_spec = self._specs_by_id.get(parent_id)
            if parent_spec:
                queue.extend(parent_spec.derivations_from)

        return path


# =============================================================================
# Module-level functions
# =============================================================================


async def seed_clean_slate_genesis(
    storage: PostgresZeroSeedStorage | None = None,
    wipe_existing: bool = False,
    project_root: Path | None = None,
) -> GenesisResult:
    """
    Seed the clean slate genesis.

    Args:
        storage: PostgreSQL storage (uses global if None)
        wipe_existing: Whether to wipe existing genesis K-Blocks first
        project_root: Project root for writing genesis files

    Returns:
        GenesisResult with created K-Block IDs and file paths
    """
    if storage is None:
        from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

        storage = await get_postgres_zero_seed_storage()

    genesis = CleanSlateGenesis()

    if wipe_existing:
        await genesis.wipe_existing(storage)

    return await genesis.seed_clean_slate(storage, project_root=project_root)


def get_genesis_specs() -> list[GenesisKBlockSpec]:
    """Get all 22 genesis K-Block specifications."""
    genesis = CleanSlateGenesis()
    return genesis.specs


# =============================================================================
# API Wrapper Functions
# =============================================================================


@dataclass
class CleanSlateStatus:
    """Status of clean slate genesis."""

    is_seeded: bool
    kblock_count: int
    expected_count: int = 22
    missing_kblocks: list[str] = field(default_factory=list)
    average_loss: float | None = None


@dataclass
class ConstitutionalGraph:
    """The Constitutional derivation graph."""

    nodes: list[dict[str, Any]]
    edges: list[dict[str, str]]
    layers: dict[int, list[str]]


async def check_clean_slate_status() -> CleanSlateStatus:
    """Check if clean slate genesis is complete."""
    from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

    try:
        storage = await get_postgres_zero_seed_storage()
        genesis = CleanSlateGenesis()

        # Check which K-Blocks exist
        found_ids: list[str] = []
        missing_ids: list[str] = []

        for spec in genesis.specs:
            node = await storage.get_node(spec.id)
            if node:
                found_ids.append(spec.id)
            else:
                missing_ids.append(spec.id)

        is_seeded = len(found_ids) >= 22  # All 22 K-Blocks must exist

        # Calculate average loss if seeded
        avg_loss = None
        if is_seeded:
            total_loss = sum(spec.loss for spec in genesis.specs)
            avg_loss = total_loss / len(genesis.specs)

        return CleanSlateStatus(
            is_seeded=is_seeded,
            kblock_count=len(found_ids),
            expected_count=22,
            missing_kblocks=missing_ids,
            average_loss=avg_loss,
        )
    except Exception:
        # If storage fails, report not seeded
        return CleanSlateStatus(
            is_seeded=False,
            kblock_count=0,
            expected_count=22,
            missing_kblocks=list(GENESIS_IDS.values()),
            average_loss=None,
        )


async def seed_clean_slate(
    wipe_existing: bool = False,
    project_root: Path | None = None,
) -> GenesisResult:
    """Seed the clean slate genesis with optional file writing."""
    return await seed_clean_slate_genesis(
        wipe_existing=wipe_existing,
        project_root=project_root,
    )


async def wipe_clean_slate() -> None:
    """Wipe existing clean slate K-Blocks."""
    from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

    storage = await get_postgres_zero_seed_storage()
    genesis = CleanSlateGenesis()
    await genesis.wipe_existing(storage)


async def get_constitutional_graph() -> ConstitutionalGraph:
    """Get the Constitutional derivation graph."""
    from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

    storage = await get_postgres_zero_seed_storage()
    genesis = CleanSlateGenesis()

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    layers: dict[int, list[str]] = {0: [], 1: [], 2: [], 3: []}

    for spec in genesis.specs:
        # Get the actual K-Block if it exists
        node = await storage.get_node(spec.id)
        content = spec.content[:500] if node else ""  # First 500 chars

        nodes.append(
            {
                "id": spec.id,
                "title": spec.title,
                "layer": spec.layer,
                "galois_loss": spec.loss,
                "derives_from": list(spec.derivations_from),
                "tags": list(spec.tags),
                "content": content,
            }
        )

        # Add to layer grouping
        if spec.layer in layers:
            layers[spec.layer].append(spec.id)

        # Add derivation edges
        for parent_id in spec.derivations_from:
            edges.append(
                {
                    "from": parent_id,
                    "to": spec.id,
                    "type": "DERIVES_FROM",
                }
            )

    return ConstitutionalGraph(nodes=nodes, edges=edges, layers=layers)


__all__ = [
    "CleanSlateGenesis",
    "GenesisFileWriter",
    "GenesisResult",
    "GenesisKBlockSpec",
    "CleanSlateStatus",
    "ConstitutionalGraph",
    "GENESIS_IDS",
    "COLORS",
    "seed_clean_slate_genesis",
    "seed_clean_slate",
    "check_clean_slate_status",
    "wipe_clean_slate",
    "get_constitutional_graph",
    "get_genesis_specs",
]
