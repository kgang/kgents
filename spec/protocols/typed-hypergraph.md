# The Typed-Hypergraph

**Status:** ✅ Complete (81 tests passing, CLI functional, integrated into Portal)
**Date:** 2025-12-22
**Derives From:** `brainstorming/context-management-agents.md` Part 9
**Implementation:** `impl/claude/protocols/agentese/contexts/self_context.py`

---

## Epigraph

> *"The lens was a lie. There is only the link."*
>
> *"The noun is a lie. There is only the rate of change."* — AGENTESE Principle

---

## 1. Overview

The typed-hypergraph is kgents' model for agent context. Instead of pre-composing "views" or "lenses" for agents, we give them a **navigable graph** where:

- **Nodes** are holons (files, functions, claims, evidence, concepts)
- **Hyperedges** are AGENTESE aspects that connect one node to *many* nodes
- **Traversal** is lazy and observer-dependent
- **Trails** persist navigation history as replayable, shareable artifacts

### 1.1 Why "Hypergraph"?

A regular graph has binary edges: A → B.

A **hypergraph** has edges that connect one node to many nodes simultaneously:

```
A ──[tests]──→ {B₁, B₂, B₃}
```

This is exactly what AGENTESE aspects return—sets, not singletons.

### 1.2 The Paradigm Shift

| Lens Paradigm | Typed-Hypergraph Paradigm |
|---------------|---------------------------|
| Extract slice from whole | Navigate to related node(s) |
| Pre-compose views | Lazy traversal on demand |
| Agent receives static view | Agent navigates live graph |
| Orchestrator decides focus | Agent decides where to go |
| Files as nouns | **Links as verbs** |
| Binary edges | **Hyperedges** (one → many) |

---

## 2. The Core Insight

**AGENTESE aspects ARE hyperedge types.**

```python
# These are the SAME thing:
await logos("world.auth_middleware.tests", observer)     # AGENTESE invocation
auth_middleware ──[tests]──→ {test_auth, test_auth_edge, ...}  # Graph traversal
```

Every AGENTESE path is a graph query:
- `world.auth_middleware` — a node
- `.tests` — a hyperedge type
- The result — destination nodes

---

## 3. Data Structures

### 3.1 ContextNode

```python
@dataclass
class ContextNode:
    """A node in the typed-hypergraph."""

    path: str           # AGENTESE path (e.g., "world.auth_middleware")
    holon: str          # Entity name
    _content: str | None = None  # Lazy-loaded

    def edges(self, observer: Observer) -> dict[str, list["ContextNode"]]:
        """
        Available hyperedges from this node.

        Observer-dependent: different observers see different edges.
        Returns: {aspect_name: [destination_nodes]}
        """

    async def content(self) -> str:
        """Load content only when needed."""

    async def follow(self, aspect: str, observer: Observer) -> list["ContextNode"]:
        """
        Traverse a hyperedge.

        Equivalent to: logos(f"{self.path}.{aspect}", observer)
        """
```

### 3.2 ContextGraph

```python
@dataclass
class ContextGraph:
    """
    The navigable typed-hypergraph.

    Not a pre-loaded structure—a navigation protocol.
    """

    focus: set[ContextNode]    # Current position(s)
    trail: list[TrailStep]     # Navigation history
    observer: Observer         # Determines edge visibility

    async def navigate(self, aspect: str) -> "ContextGraph":
        """Follow a hyperedge from all focused nodes."""

    async def affordances(self) -> dict[str, int]:
        """What hyperedges can we follow? {aspect: destination_count}"""

    def backtrack(self) -> "ContextGraph":
        """Go back along the trail."""
```

### 3.3 Trail

```python
@dataclass
class Trail:
    """
    Replayable path through the hypergraph.

    Inspired by Vannevar Bush's Memex trails.
    """

    id: str
    name: str
    created_by: Observer
    steps: list[TrailStep]
    annotations: dict[int, str]  # step_index → annotation

    async def replay(self, observer: Observer) -> ContextGraph:
        """Replay this trail, ending at final position."""

    def annotate(self, step_index: int, text: str) -> "Trail":
        """Add annotation at a step."""
```

---

## 4. Standard Hyperedge Types

Every holon supports these standard aspects (hyperedges):

### 4.1 Structural

| Hyperedge | Description | Reverse |
|-----------|-------------|---------|
| `contains` | Submodules/children | `contained_in` |
| `parent` | Parent module | — |
| `imports` | Dependencies | `imported_by` |
| `calls` | Functions called | `called_by` |

### 4.2 Testing

| Hyperedge | Description | Reverse |
|-----------|-------------|---------|
| `tests` | Test files | `tested_by` |
| `covers` | Code paths covered | `covered_by` |

### 4.3 Specification

| Hyperedge | Description | Reverse |
|-----------|-------------|---------|
| `implements` | Specs implemented | `implemented_by` |
| `derives_from` | Parent specs | `derived_by` |

### 4.4 Evidence (ASHC Integration)

| Hyperedge | Description | Reverse |
|-----------|-------------|---------|
| `evidence` | Supporting evidence | `evidences` |
| `supports` | Claims supported | `supported_by` |
| `refutes` | Claims contradicted | `refuted_by` |

### 4.5 Temporal

| Hyperedge | Description | Reverse |
|-----------|-------------|---------|
| `evolved_from` | Previous version | `evolved_to` |
| `supersedes` | What this replaces | `superseded_by` |

### 4.6 Semantic

| Hyperedge | Description |
|-----------|-------------|
| `related` | Loose semantic similarity |
| `similar` | High embedding similarity |
| `contrasts` | Semantic opposition |

---

## 5. Observer-Dependent Edges

The same node has different affordances for different observers:

```python
match observer.archetype:
    case "developer":
        # tests, imports, callers, implements

    case "security_auditor":
        # auth_flows, data_flows, vulnerabilities, evidence

    case "architect":
        # dependencies, dependents, patterns, violations

    case "newcomer":
        # docs, examples, related
```

This is the phenomenological insight: **what exists depends on who's looking.**

---

## 6. Bidirectional Hyperedges

Unlike the web's unidirectional links, every hyperedge has a reverse:

```
A ──[tests]──→ B    implies    B ──[tested_by]──→ A
```

This enables navigation in both directions—crucial for understanding "what uses this?" and "what does this use?"

---

## 7. AGENTESE Integration

The context graph is exposed as an AGENTESE holon at `self.context`:

```bash
kg context manifest        # Where am I?
kg context navigate tests  # Follow [tests] hyperedge
kg context backtrack       # Go back
kg context trail save "investigation"  # Save trail
```

### 7.1 Aspects

| Aspect | Category | Description |
|--------|----------|-------------|
| `manifest` | PERCEPTION | Current focus, trail length, affordances |
| `navigate` | MUTATION | Follow a hyperedge |
| `focus` | MUTATION | Jump to a specific node |
| `backtrack` | MUTATION | Go back one step |
| `trail` | PERCEPTION | Get current trail |
| `subgraph` | COMPOSITION | Extract reachable subgraph |

---

## 8. The Minimal Output Principle

The typed-hypergraph respects the Constitution's minimal output principle:

```python
# WRONG: Return everything upfront
def get_context() -> AgentCoherentView:
    return AgentCoherentView(
        documents=[...],   # Megabytes
        evidence=[...],    # Entire scope
    )

# RIGHT: Return a handle
def get_context() -> ContextNode:
    return ContextNode(path="world.auth_middleware")
    # Content not loaded!
    # Edges not traversed!
    # Agent decides what to load.
```

The agent receives **a handle, not a haystack**.

---

## 9. Historical Lineage

| System | Insight | Our Contribution |
|--------|---------|------------------|
| Memex (Bush, 1945) | Associative trails | Trail persistence |
| Hypertext (Nelson, 1965) | Typed bidirectional links | Bidirectional hyperedges |
| Zettelkasten (Luhmann) | Atomic notes with connections | Nodes as holons |
| The Web | Universal hyperlinks | Typed, not untyped |
| Semantic Web (W3C) | RDF predicates | AGENTESE aspects |
| Roam/Obsidian | Backlinks | Observer-dependent edges |

---

## 10. Laws

### 10.1 Hyperedge Associativity

```
(A ──[e1]──→ B) ──[e2]──→ C  ≡  A ──[e1]──→ (B ──[e2]──→ C)
```

Navigation order doesn't affect reachability.

### 10.2 Bidirectional Consistency

```
A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A
```

Every forward edge implies a reverse edge.

### 10.3 Observer Monotonicity

If observer O₁ ⊆ O₂ in capabilities, then:
```
edges(node, O₁) ⊆ edges(node, O₂)
```

More capable observers see more edges.

---

## 11. Implementation Status

### What's Built (81 tests across 2 test files)

| Component | Status | Location |
|-----------|--------|----------|
| `ContextNode` | ✅ Complete | `self_context.py` |
| `ContextGraph` | ✅ Complete | `self_context.py` |
| `Trail` / `TrailStep` | ✅ Complete | `self_context.py` |
| Resolver Registry | ✅ Complete | `hyperedge_resolvers.py` |
| 15 Standard Resolvers | ✅ Complete | `hyperedge_resolvers.py` |
| 6 Reverse Resolvers | ✅ Complete | `hyperedge_resolvers.py` |
| CLI Handler | ✅ Complete | `handlers/context.py` |
| Law Verification Tests | ✅ Complete | `_tests/test_*.py` |

### Implemented Hyperedge Resolvers

| Resolver | Finds | Reverse | Reverse Impl |
|----------|-------|---------|--------------|
| `contains` | Submodules/children | `contained_in` | ✅ |
| `parent` | Parent module | `children` | — |
| `imports` | Dependencies (AST parsed) | `imported_by` | ⚠️ placeholder |
| `calls` | Functions called | `called_by` | ⚠️ placeholder |
| `tests` | Test files (`_tests/test_*.py`) | `tested_by` | ✅ |
| `covers` | Code covered by test | `covered_by` | — |
| `implements` | Spec files | `implemented_by` | ✅ |
| `derives_from` | Parent specs | `derived_by` | ⚠️ placeholder |
| `related` | Sibling modules | — | — |

### Robustness Guarantees

The implementation includes defensive handling for:

- **Syntax errors**: Resolvers handle malformed Python files gracefully
- **Missing files**: Return empty list instead of raising
- **Deep paths**: Correctly resolve paths like `world.a.b.c.d.e`
- **Empty paths**: Handle edge cases without crashing
- **Complex AST**: Call resolver handles lambdas, comprehensions, method chains

### Law Verification Coverage

| Law | Tests | Status |
|-----|-------|--------|
| 10.1 Associativity | 3 tests | ✅ Basic + chain + multi-focus |
| 10.2 Bidirectionality | 10 tests | ✅ Forward + reverse resolvers |
| 10.3 Monotonicity | 4 tests | ✅ Full observer ordering |

### Not Yet Implemented

The following spec features have placeholder implementations:

| Feature | Status | Notes |
|---------|--------|-------|
| `evidence`, `supports`, `refutes` | ❌ Missing | Requires ASHC integration |
| `evolved_from`, `supersedes` | ❌ Missing | Requires git/temporal index |
| `similar`, `contrasts` | ❌ Missing | Requires embedding vectors |
| `imported_by`, `called_by` | ⚠️ Placeholder | Requires project-wide index |
| `security_auditor` edges | ❌ Missing | `auth_flows`, `data_flows`, etc. |
| `architect` edges | ❌ Missing | `patterns`, `violations`, etc. |

These are documented to prevent spec drift. Implementation priority follows user demand.

### CLI Usage

```bash
# Show current position and available edges
kg context

# Jump to a node (shorthand paths work)
kg context focus brain           # world.brain
kg context focus agentese.parser # world.agentese.parser

# Follow hyperedges
kg context navigate tests        # Find test files
kg context navigate imports      # Find dependencies

# Navigation
kg context backtrack             # Go back
kg context trail                 # Show navigation history
kg context subgraph --depth 3    # Extract reachable subgraph
```

### Path Resolution

Shorthand paths are automatically resolved:

```
brain           → impl/claude/services/brain/node.py
brain.persistence → impl/claude/services/brain/persistence.py
agentese        → impl/claude/protocols/agentese/__init__.py
poly            → impl/claude/agents/poly/__init__.py
```

---

## 12. Related Specs

- `spec/protocols/portal-token.md` — UX layer for hypergraph navigation
- `spec/protocols/exploration-harness.md` — Safety and evidence layer
- `spec/protocols/agentese.md` — The verb-first ontology
- `spec/services/witness.md` — Trail as evidence

---

*"The file is a lie. The lens is a lie. There is only the typed-hypergraph."*
