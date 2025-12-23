# Derivation Edges: Evidence on Relationships

> *"The edge IS the proof. The mark IS the witness."*

This skill teaches agents how marks flow into derivation edges—the evidence layer that tracks *why* derivations are trusted.

**Difficulty**: Intermediate
**Prerequisites**: `witness-for-agents.md`, `building-agent.md`
**Source**: Phase 3C of the Derivation Framework

---

## The Core Insight

Marks prove agents work. Edges prove *derivations* work.

```
Mark: "Brain completed operation X"
  │
  ├── Stigmergy: Brain's usage count increases
  │
  └── Edges: Fix→Brain and Compose→Brain edges strengthen
             (because Brain derives_from Fix and Compose)
```

When you emit a mark, you're not just logging—you're accumulating evidence on the derivation DAG.

---

## Key Concepts

### Structural vs Non-Structural Edges

| Type | Example | Persisted? |
|------|---------|------------|
| **Structural** | Fix → Brain (Brain derives_from Fix) | Yes |
| **Non-structural** | Brain >> Witness (composition, no derivation) | No |

Only structural edges (derivation relationships) are tracked in the DAG. Arbitrary compositions are logged but not persisted.

### Logarithmic Strengthening

Evidence accumulates with diminishing returns:

```
1 mark    → 0.55 strength
10 marks  → 0.70 strength
100 marks → 0.85 strength
1000 marks → 0.95 strength (capped)
```

Formula: `strength = min(0.95, 0.5 + 0.15 * log10(marks + 1))`

This prevents gaming via mark spam while rewarding genuine usage.

### Evidence Hierarchy

| Level | Evidence Type | Strength | Example |
|-------|---------------|----------|---------|
| L0 | Marks | Logarithmic | Human attention, km commands |
| L1 | Tests | Stronger base (0.55) | pytest, automated checks |
| L2 | Proofs | Categorical (1.0) | Dafny, Lean4 verification |

---

## Python API

### Infer Which Edges a Mark Evidences

```python
from protocols.derivation import infer_edges_from_mark, get_registry

# Given a mark from "brain" origin
edges = infer_edges_from_mark(mark, registry)
# → [("Fix", "Brain"), ("Compose", "Brain")]
```

### Update Edges from Marks

```python
from protocols.derivation import mark_updates_edges

# Async: attach mark evidence to derivation edges
updated_edges = await mark_updates_edges(mark, registry)
# → {("Fix", "Brain"): WitnessedEdge(...), ("Compose", "Brain"): WitnessedEdge(...)}
```

### Strengthen Edge on Composition Success

```python
from protocols.derivation import composition_success_strengthens_edge

# When A >> B composition succeeds
edge = await composition_success_strengthens_edge(
    source="Fix",
    target="Brain",
    composition_id="test_fix_brain_compose",  # "test_" prefix → L1 evidence
    registry=registry,
)
```

### Combined: Full Witness Processing

```python
from protocols.derivation import (
    mark_updates_stigmergy,  # Usage counts
    mark_updates_edges,       # Edge evidence
)

async def process_mark_fully(mark, registry):
    """Process a mark for both stigmergy and edges."""
    # Update usage counts (per-agent)
    usage = await mark_updates_stigmergy(mark, registry)

    # Update edge evidence (per-derivation-relationship)
    edges = await mark_updates_edges(mark, registry)

    return {"usage": usage, "edges": edges}
```

---

## Edge Types

```python
from protocols.derivation import WitnessedEdge, EdgeType

# Most edges are DERIVES_FROM
edge = WitnessedEdge(
    source="Fix",
    target="Brain",
    edge_type=EdgeType.DERIVES_FROM,
)

# Other types exist for richer relationships
EdgeType.IMPLEMENTS    # Spec → Impl
EdgeType.EXTENDS       # Extension without full derivation
EdgeType.INSTANTIATES  # Template → Instance
```

---

## Accessing Edge Data

### Get an Edge

```python
from protocols.derivation import get_registry

registry = get_registry()

# Get edge (returns empty edge if not stored)
edge = registry.get_edge("Fix", "Brain")

print(f"Strength: {edge.edge_strength:.0%}")
print(f"Marks: {len(edge.mark_ids)}")
print(f"Tests: {len(edge.test_ids)}")
print(f"Is categorical: {edge.is_categorical}")
```

### List All Edges for an Agent

```python
# Incoming edges (parents → agent)
incoming = registry.edges_for("Brain")
# → [WitnessedEdge(Fix→Brain), WitnessedEdge(Compose→Brain)]

# Outgoing edges (agent → children)
outgoing = registry.outgoing_edges("Fix")
# → [WitnessedEdge(Fix→Brain), WitnessedEdge(Fix→OtherAgent), ...]
```

---

## Gotchas

### 1. Lazy Edge Initialization

```python
edge = registry.get_edge("Unknown", "Agent")
# Returns WitnessedEdge.empty(), NOT None

# Check if truly empty:
if edge.evidence_count == 0:
    print("No evidence on this edge")
```

### 2. Bootstrap Edges are Indefeasible

```python
# CONSTITUTION → Id edge has categorical evidence
# Marks are recorded but strength stays 1.0
edge = registry.get_edge("CONSTITUTION", "Id")
edge = edge.with_mark("mark-123")  # Mark recorded
assert edge.edge_strength == 1.0   # Still 1.0!
```

### 3. Structural Edge Check

```python
from protocols.derivation.witness_bridge import _is_structural_edge

# Only structural edges are persisted
if _is_structural_edge("Fix", "Brain", registry):
    registry.update_edge(edge)  # Safe
else:
    # Non-structural: log but don't persist
    logger.info(f"Composition evidence not persisted")
```

### 4. Separate Stigmergy from Edges

```python
# WRONG: Only updating stigmergy
await mark_updates_stigmergy(mark, registry)  # Usage counts only!

# RIGHT: Update both for full witness processing
await mark_updates_stigmergy(mark, registry)  # Usage counts
await mark_updates_edges(mark, registry)       # Edge evidence
```

---

## Integration Pattern: Agent Witness Protocol

```python
class WitnessAwareAgent:
    """Agent that properly witnesses its actions."""

    def __init__(self, registry: DerivationRegistry):
        self.registry = registry
        self.agent_name = "MyAgent"

    async def do_work(self, task: str) -> Result:
        # Create mark
        mark = Mark(
            id=f"mark-{uuid4()}",
            origin=self.agent_name.lower(),
            action=f"Processing {task}",
        )

        # Do the actual work
        result = await self._process(task)

        # Full witness processing
        await mark_updates_stigmergy(mark, self.registry)
        await mark_updates_edges(mark, self.registry)

        return result

    async def compose_with(self, other: "Agent", composition_id: str):
        """Compose with another agent, recording evidence."""
        result = await self >> other

        # Record composition success
        await composition_success_strengthens_edge(
            source=self.agent_name,
            target=other.agent_name,
            composition_id=composition_id,
            registry=self.registry,
        )

        return result
```

---

## CLI & AGENTESE Integration

### AGENTESE Paths (Phase 3D)

```bash
# Summary of all edges with evidence
kg concept.derivation.edges

# Edges for a specific agent
kg derivation edges Brain

# Specific edge query
kg concept.derivation.edges source=CONSTITUTION target=Id
```

### Programmatic Access

```python
from protocols.agentese.contexts.concept_derivation import get_derivation_node

node = get_derivation_node()

# Query edges for an agent
result = await node.edges(observer, agent_name="Brain")
# result.metadata["incoming"] = [{source, target, strength, evidence_count, is_categorical}, ...]
# result.metadata["outgoing"] = [...]

# Query specific edge
result = await node.edges(observer, source="Fix", target="Brain")
# result.metadata["strength"] = 0.55
# result.metadata["mark_count"] = 1
# result.metadata["is_categorical"] = False
```

### DAG Visualization (Enriched)

The `concept.derivation.dag` now includes edge evidence in metadata:

```python
dag = await node.dag(observer)
# dag.metadata["edges"] now includes:
# - strength (float 0.0-1.0)
# - evidence_count (int)
# - is_categorical (bool)
```

This enables edge thickness/opacity in graph visualizations.

---

## The Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  km "action" --json                                                 │
│       │                                                             │
│       ▼                                                             │
│  Mark Created (origin="brain")                                      │
│       │                                                             │
│       ├──▶ mark_updates_stigmergy() → Brain usage_count += 1       │
│       │                                                             │
│       └──▶ mark_updates_edges() → Fix→Brain edge.with_mark(id)     │
│                                 → Compose→Brain edge.with_mark(id)  │
│                                                                     │
│  Result: Derivation confidence increases via:                       │
│    1. Stigmergic confidence (usage-based)                          │
│    2. Edge evidence (relationship-based)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|--------------|-----------------|
| Only updating stigmergy | Missing edge evidence | Call both `mark_updates_*` functions |
| Trying to persist non-structural edges | Will raise ValueError | Check `_is_structural_edge()` first |
| Expecting marks to weaken bootstrap edges | Bootstrap is indefeasible | Use DifferentialDenial for challenges |
| Forgetting test_ prefix | Tests recorded as marks (weaker) | Use `test_` prefix for L1 evidence |

---

## When to Use Each Function

| Situation | Function |
|-----------|----------|
| Agent emits a mark | `mark_updates_stigmergy()` + `mark_updates_edges()` |
| Composition succeeds | `composition_success_strengthens_edge()` |
| Batch processing marks | `sync_witness_to_derivations()` |
| Need to know which edges a mark affects | `infer_edges_from_mark()` |
| Challenge a derivation | `denial_weakens_derivation()` |

---

*"Marks accumulate. Edges strengthen. Confidence emerges."*
