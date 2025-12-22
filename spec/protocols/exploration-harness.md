# Exploration Harness

**Status:** Active Development (Phases 1-6 complete, 75 tests passing)
**Date:** 2025-12-22
**Derives From:** `brainstorming/context-management-agents.md` Parts 1-3, 8
**Implementation:** `impl/claude/protocols/exploration/`

---

## Epigraph

> *"Every trail is evidence. Every exploration creates proof obligations."*
>
> *"The harness doesn't constrain—it witnesses."*

---

## 1. Overview

The exploration harness provides **safety guarantees** and **evidence integration** for agents navigating the typed-hypergraph. It combines:

- **Navigation budget** — bounded exploration
- **Loop detection** — prevent trivially bad loops
- **Trail as evidence** — exploration creates proof
- **Commitment protocol** — claims require evidence

The harness doesn't prevent exploration—it **witnesses** it.

---

## 2. Navigation Budget

Agents have bounded resources for exploration:

```python
@dataclass
class NavigationBudget:
    """Resource limits for hypergraph navigation."""

    max_steps: int = 100       # Total hyperedge traversals
    max_depth: int = 10        # Maximum nesting depth
    max_nodes: int = 50        # Nodes in focus set
    time_budget_ms: int = 30000  # Wall clock limit

    # Current usage
    steps_taken: int = 0
    current_depth: int = 0
    nodes_visited: set[str] = field(default_factory=set)
    start_time: datetime = field(default_factory=datetime.now)

    def can_navigate(self) -> bool:
        """Check if we have budget remaining."""
        elapsed = (datetime.now() - self.start_time).total_seconds() * 1000
        return (
            self.steps_taken < self.max_steps
            and self.current_depth < self.max_depth
            and len(self.nodes_visited) < self.max_nodes
            and elapsed < self.time_budget_ms
        )

    def consume(self, node: ContextNode, depth: int) -> "NavigationBudget":
        """Record a navigation step."""
        return replace(
            self,
            steps_taken=self.steps_taken + 1,
            current_depth=max(self.current_depth, depth),
            nodes_visited=self.nodes_visited | {node.path},
        )
```

### 2.1 Budget Exhaustion

When budget is exhausted, the agent receives a signal:

```python
@dataclass
class BudgetExhausted:
    reason: str  # "steps", "depth", "nodes", or "time"
    remaining: NavigationBudget
    trail: Trail  # What was explored
```

The agent can then:
1. Return findings from exploration so far
2. Request budget extension (with justification)
3. Backtrack to a productive node

---

## 3. Loop Detection

### 3.1 Three Types of Loops

| Loop Type | Description | Detection |
|-----------|-------------|-----------|
| **Exact** | Same node visited twice | State hash match |
| **Semantic** | Visiting similar nodes | Embedding similarity > 0.95 |
| **Structural** | Repeating navigation pattern | Pattern detection (A→B→A→B) |

### 3.2 Loop Detector

```python
class LoopDetector:
    """Detect trivially bad loops in navigation."""

    def __init__(self, history_size: int = 100):
        self.path_history: deque[str] = deque(maxlen=history_size)
        self.embeddings: deque[np.ndarray] = deque(maxlen=history_size)
        self.edge_pattern: deque[str] = deque(maxlen=20)

    def check(self, node: ContextNode, edge: str) -> LoopStatus:
        # 1. Exact loop
        if node.path in self.path_history:
            return LoopStatus.EXACT_LOOP

        # 2. Semantic loop
        embedding = embed(node)
        for prev in self.embeddings:
            if cosine_similarity(embedding, prev) > 0.95:
                return LoopStatus.SEMANTIC_LOOP

        # 3. Structural loop
        self.edge_pattern.append(edge)
        if self._is_repeating_pattern():
            return LoopStatus.STRUCTURAL_LOOP

        # Record for future checks
        self.path_history.append(node.path)
        self.embeddings.append(embedding)

        return LoopStatus.OK

    def _is_repeating_pattern(self) -> bool:
        """Detect A→B→A→B patterns."""
        pattern = "".join(self.edge_pattern)
        for period in range(1, len(pattern) // 2 + 1):
            base = pattern[:period]
            if pattern == (base * (len(pattern) // period + 1))[:len(pattern)]:
                return True
        return False
```

### 3.3 Loop Response

When a loop is detected:

| Response | When | Action |
|----------|------|--------|
| **Warn** | First occurrence | Log, continue |
| **Backtrack** | Second occurrence | Auto-backtrack to last non-looping node |
| **Halt** | Third occurrence | Stop exploration, return findings |

---

## 4. Trail as Evidence

### 4.1 The Insight

Exploration is not just navigation—it's **evidence gathering**. Every trail can support or refute claims:

```python
class TrailAsEvidence:
    """A trail IS evidence for claims."""

    async def to_evidence(self, trail: Trail, claim: str) -> Evidence:
        return Evidence(
            claim=claim,
            source="exploration_trail",
            content=trail.serialize(),
            strength=self._compute_strength(trail),
            metadata={
                "trail_id": trail.id,
                "steps": len(trail.steps),
                "nodes_visited": [s.node for s in trail.steps],
                "edges_followed": [s.edge_taken for s in trail.steps],
            },
        )

    def _compute_strength(self, trail: Trail) -> str:
        """Longer, more varied trails = stronger evidence."""
        if len(trail.steps) < 3:
            return "weak"
        if len(set(s.edge_taken for s in trail.steps)) < 2:
            return "weak"  # Only followed one edge type
        if len(trail.steps) > 10:
            return "strong"
        return "moderate"
```

### 4.2 Evidence from Exploration

| Exploration Action | Evidence Created |
|--------------------|------------------|
| Follow hyperedge | "Agent explored [edge] from [source]" |
| Visit node | "Agent examined [node]" |
| Backtrack | "Agent found dead end at [node]" |
| Find relevant content | "Agent found evidence at [node]" |
| Complete trail | "Agent completed investigation via [trail]" |

---

## 5. ASHC Commitment Protocol

Before an agent can commit a claim, the harness enforces:

### 5.1 Requirements

| Requirement | Description |
|-------------|-------------|
| **Evidence Quantity** | Minimum N evidence items |
| **Evidence Quality** | At least M "strong" evidence items |
| **No Counterevidence** | All counterevidence addressed |
| **Trail Exists** | Exploration trail supporting claim |

### 5.2 Commitment Check

```python
class ASHCCommitment:
    """
    Agentic Self-Hosted Compiler commitment protocol.

    Claims require evidence from exploration.
    """

    def can_commit(self, claim: Claim, trail: Trail) -> CommitmentResult:
        # 1. Evidence from trail
        evidence = self._extract_evidence(trail, claim)
        if len(evidence) < self.min_evidence_count:
            return CommitmentResult.INSUFFICIENT_QUANTITY

        # 2. Quality check
        strong = [e for e in evidence if e.strength == "strong"]
        if len(strong) < self.min_strong_count:
            return CommitmentResult.INSUFFICIENT_QUALITY

        # 3. Counterevidence
        counter = self._find_counterevidence(claim)
        unaddressed = [c for c in counter if not c.addressed]
        if unaddressed:
            return CommitmentResult.UNADDRESSED_COUNTEREVIDENCE

        # 4. Trail coherence
        if not self._trail_supports_claim(trail, claim):
            return CommitmentResult.TRAIL_DOES_NOT_SUPPORT

        return CommitmentResult.APPROVED
```

### 5.3 Commitment Levels

| Level | Requirements | Can Claim |
|-------|--------------|-----------|
| **Tentative** | Any evidence | "I observed X" |
| **Moderate** | 3+ evidence, 1+ strong | "Evidence suggests X" |
| **Strong** | 5+ evidence, 2+ strong, no counter | "X is likely true" |
| **Definitive** | 10+ evidence, 5+ strong, all counter addressed | "X is true" |

---

## 6. The Harness Integration

### 6.1 Wrapping Navigation

```python
class ExplorationHarness:
    """Wraps hypergraph navigation with safety and evidence."""

    def __init__(self, graph: ContextGraph):
        self.graph = graph
        self.budget = NavigationBudget()
        self.loop_detector = LoopDetector()
        self.evidence_collector = EvidenceCollector()

    async def navigate(self, edge: str) -> NavigationResult:
        # 1. Check budget
        if not self.budget.can_navigate():
            return NavigationResult.BUDGET_EXHAUSTED

        # 2. Navigate
        new_graph = await self.graph.navigate(edge)

        # 3. Check for loops
        for node in new_graph.focus:
            loop_status = self.loop_detector.check(node, edge)
            if loop_status != LoopStatus.OK:
                return NavigationResult.LOOP_DETECTED(loop_status)

        # 4. Record evidence
        await self.evidence_collector.record_navigation(
            source=self.graph.focus,
            edge=edge,
            destinations=new_graph.focus,
        )

        # 5. Consume budget
        for node in new_graph.focus:
            self.budget = self.budget.consume(node, len(new_graph.trail))

        # 6. Update graph
        self.graph = new_graph

        return NavigationResult.OK(new_graph)

    async def commit(self, claim: Claim) -> CommitmentResult:
        """Attempt to commit a claim based on exploration."""
        trail = self.graph.trail
        evidence = await self.evidence_collector.for_claim(claim)

        return self.ashc.can_commit(claim, trail, evidence)
```

---

## 7. Evidence Scope

Only relevant evidence is accessible—scoped by exploration:

### 7.1 Accessibility Rules

Evidence is accessible if:
1. It's about a node the agent has visited
2. It's about a claim the agent is investigating
3. It's reachable via `evidence` hyperedges from visited nodes

### 7.2 Evidence Scope

```python
class EvidenceScope:
    """Scopes evidence to exploration context."""

    def __init__(self, trail: Trail):
        self.visited_nodes = {s.node for s in trail.steps}
        self._build_accessibility()

    def accessible(self) -> list[Evidence]:
        """Only evidence reachable from exploration."""
        return [e for e in self.all_evidence if e.id in self.accessible_ids]

    def _build_accessibility(self):
        self.accessible_ids = set()

        # Evidence about visited nodes
        for node in self.visited_nodes:
            self.accessible_ids.update(self._evidence_about(node))

        # Evidence reachable via evidence edges
        for node in self.visited_nodes:
            evidence_nodes = await node.follow("evidence", self.observer)
            for en in evidence_nodes:
                self.accessible_ids.add(en.path)
```

---

## 8. Guarantees

The exploration harness guarantees:

| Guarantee | Mechanism |
|-----------|-----------|
| **Termination** | Navigation budget (steps, time) |
| **Progress** | Loop detection prevents spinning |
| **Evidence** | Every navigation creates evidence |
| **Scope** | Only relevant evidence accessible |
| **Commitment** | Claims require trail-based evidence |

---

## 9. CLI Integration

```bash
# Check budget
kg explore budget
# → Steps: 45/100, Depth: 3/10, Time: 12s/30s

# View evidence from exploration
kg explore evidence
# → 7 items collected, 2 strong, 5 moderate

# Attempt commitment
kg explore commit "Auth middleware validates tokens correctly"
# → INSUFFICIENT_QUALITY: Need 2 strong evidence, have 1

# Continue exploration to gather more evidence
kg context navigate tests
kg context navigate covers
kg explore commit "Auth middleware validates tokens correctly"
# → APPROVED: Trail supports claim with 3 strong evidence
```

---

## 10. Reframing Parts 1-8

The exploration harness reframes the original concepts:

| Original (Parts 1-8) | Reframe (Exploration Harness) |
|----------------------|-------------------------------|
| Lens (slice extraction) | Subgraph reachable via hyperedges |
| Portal (projection) | Portal tokens + harness |
| Harness (guarantees) | Navigation budget + loop detection |
| Evidence Scope | Evidence reachable from trail |
| Token State Machine | Portal token state machine |
| ASHC Commitment | Trail-based commitment protocol |
| Coherence Guarantee | Graph + harness consistency |

---

## 11. Laws

### 11.1 Evidence Monotonicity

Evidence can only grow during exploration:
```
evidence(trail ++ step) ⊇ evidence(trail)
```

### 11.2 Commitment Irreversibility

Once committed at a level, cannot downgrade:
```
commit(claim, "strong") → cannot later commit(claim, "weak")
```

### 11.3 Trail Determines Scope

Evidence scope is determined by trail:
```
scope(trail₁) ∩ scope(trail₂) = scope(trail₁ ∩ trail₂)
```

---

## 12. Related Specs

- `spec/protocols/typed-hypergraph.md` — The conceptual model
- `spec/protocols/portal-token.md` — UX layer
- `spec/services/witness.md` — Decision witnessing
- `spec/protocols/agentese.md` — The verb-first ontology

---

*"The harness doesn't constrain—it witnesses. Every trail is evidence. Every exploration creates proof obligations."*

---

## 13. Implementation Phases

### Phase 1: Core Types ✅ (2025-12-22)
- [x] `types.py`: ContextNode, Trail, TrailStep, Evidence, Observer
- [x] `types.py`: Claim, Counterevidence, CommitmentLevel, EvidenceStrength
- [x] `types.py`: NavigationResult, PortalExpansionResult
- [x] 12 tests for core types

**Location:** `impl/claude/protocols/exploration/types.py`

### Phase 2: Budget & Loops ✅ (2025-12-22)
- [x] `budget.py`: NavigationBudget (immutable, consume returns new)
- [x] `budget.py`: BudgetExhausted, ExhaustionReason enum
- [x] `budget.py`: Presets (quick, standard, thorough, unlimited)
- [x] `loops.py`: LoopDetector (exact, semantic, structural)
- [x] `loops.py`: LoopResponse escalation (warn → backtrack → halt)
- [x] `loops.py`: Portal-specific loop detection
- [x] `loops.py`: cosine_similarity for semantic detection
- [x] 10 tests for budget, 7 tests for loops

**Location:** `impl/claude/protocols/exploration/budget.py`, `loops.py`

### Phase 3: Evidence & Commitment ✅ (2025-12-22)
- [x] `evidence.py`: TrailAsEvidence (trail → evidence conversion)
- [x] `evidence.py`: EvidenceCollector (navigation recording)
- [x] `evidence.py`: EvidenceScope (accessibility rules)
- [x] `evidence.py`: PortalExpansionEvidence (weak evidence from portals)
- [x] `commitment.py`: ASHCCommitment (4-level protocol)
- [x] `commitment.py`: CommitmentRequirements per level
- [x] `commitment.py`: Irreversibility law enforcement
- [x] 18 tests for evidence and commitment

**Location:** `impl/claude/protocols/exploration/evidence.py`, `commitment.py`

### Phase 4: Harness Integration ✅ (2025-12-22)
- [x] `harness.py`: ExplorationHarness main class
- [x] `harness.py`: `navigate()` with budget, loop, evidence integration
- [x] `harness.py`: `expand_portal()` with safety checks
- [x] `harness.py`: `commit_claim()` and `can_commit()`
- [x] `harness.py`: SynergyBus context event emission
- [x] `harness.py`: Factory functions (create_harness, quick_harness, thorough_harness)
- [x] `__init__.py`: Comprehensive exports
- [x] Integration tests (harness + portal expansion)

**Location:** `impl/claude/protocols/exploration/harness.py`

### Phase 5: Derivation Bridge ✅ (2025-12-22)
- [x] `derivation/exploration_bridge.py`: TrailEvidence type
- [x] `derivation/exploration_bridge.py`: Trail patterns → principle signals
- [x] `derivation/exploration_bridge.py`: `apply_trail_evidence()`
- [x] Tests integrated with derivation framework

**Location:** `impl/claude/protocols/derivation/exploration_bridge.py`

### Phase 6: CLI Integration ✅ (2025-12-22)

**Target Location:** `impl/claude/protocols/cli/handlers/explore.py`

#### 6.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  kg explore <subcommand>                                        │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐                                            │
│  │  explore.py     │  ← Thin routing shim (Hollow Shell pattern)│
│  │  cmd_explore()  │                                            │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  protocols/exploration/                                      ││
│  │  ├── harness.py      → ExplorationHarness                   ││
│  │  ├── budget.py       → NavigationBudget                     ││
│  │  ├── loops.py        → LoopDetector                         ││
│  │  ├── evidence.py     → TrailAsEvidence, EvidenceCollector   ││
│  │  └── commitment.py   → ASHCCommitment                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2 Subcommands

| Subcommand | Description | Maps To |
|------------|-------------|---------|
| `kg explore` | Show current exploration state | `harness.get_state()` |
| `kg explore start <path>` | Start new exploration at path | `create_harness(start_node)` |
| `kg explore navigate <edge>` | Navigate via hyperedge | `harness.navigate(edge)` |
| `kg explore budget` | Show budget breakdown | `harness.budget.to_dict()` |
| `kg explore evidence` | Show collected evidence | `harness.evidence_collector.all()` |
| `kg explore trail` | Show navigation trail | `harness.trail` |
| `kg explore commit <claim>` | Attempt to commit claim | `harness.commit_claim(claim, level)` |
| `kg explore loops` | Show loop detection status | `harness.loop_detector.status()` |
| `kg explore reset` | Reset to fresh state | Clear singleton |

#### 6.3 State Management

The harness maintains state across commands via a module-level singleton:

```python
# Singleton pattern for session persistence
_active_harness: ExplorationHarness | None = None

def get_or_create_harness(start_path: str | None = None) -> ExplorationHarness:
    global _active_harness
    if _active_harness is None or start_path:
        from protocols.exploration import create_harness
        _active_harness = create_harness(start_node=ContextNode(path=start_path or "root"))
    return _active_harness
```

#### 6.4 Output Formats

- **Rich Console**: Styled tables, progress bars for budget, color-coded evidence
- **JSON**: `--json` flag for agent consumption
- **Plain**: Fallback when Rich unavailable

#### 6.5 Implementation Checklist

- [x] `explore.py`: Main handler with subcommand routing
- [x] `cmd_explore()`: Entry point registered in hollow.py
- [x] `_handle_status()`: Default view showing state snapshot
- [x] `_handle_start()`: Initialize harness at given path
- [x] `_handle_navigate()`: Navigate via hyperedge
- [x] `_handle_budget()`: Detailed budget display with progress bars
- [x] `_handle_evidence()`: Evidence collection display with strength grouping
- [x] `_handle_trail()`: Trail visualization with step tree
- [x] `_handle_commit()`: Attempt commitment with level
- [x] `_handle_loops()`: Loop detection status
- [x] `_handle_reset()`: Clear harness state
- [x] Register in COMMAND_REGISTRY (hollow.py)
- [x] Help text with examples (HELP_TEXT constant)
- [x] Tests for each subcommand (28 tests passing)

#### 6.6 Example Outputs

**`kg explore`** (status):
```
🔍 Exploration State
─────────────────────────────────────────────────

  Focus:       world.brain.core
  Trail:       4 steps (root → brain → core → tests)
  Evidence:    7 items (2 strong, 5 weak)
  Budget:      62% remaining (nodes: 38/100, depth: 3/10)
  Loops:       0 detected

  Affordances:
    [tests]    → world.brain.core._tests
    [imports]  → 3 modules
    [parent]   → world.brain
```

**`kg explore budget`**:
```
📊 Navigation Budget
─────────────────────────────────────────────────

  Nodes Visited:  38 / 100      [████████░░] 38%
  Max Depth:      3 / 10        [███░░░░░░░] 30%
  Time Used:      2.3s / 30s    [█░░░░░░░░░] 8%
  Portals:        2 / 5         [████░░░░░░] 40%

  Exhaustion Risk: LOW
  Preset: standard

  Use --preset thorough to expand limits
```

**`kg explore evidence`**:
```
📋 Evidence (7 items)
─────────────────────────────────────────────────

  STRONG (2):
    ✓ test_harness.py exists at world.brain.core._tests
      └─ from trail step 3, metadata: {test_count: 19}
    ✓ imports 'PolyAgent' from agents.polynomial
      └─ from trail step 2, metadata: {import_type: direct}

  WEAK (5):
    ○ Contains 4 submodules
    ○ Has docstring describing purpose
    ○ Uses dataclass pattern
    ○ Exports 6 public symbols
    ○ Last modified 2025-12-20

  Commitment Potential:
    TENTATIVE: ✓ (1+ evidence)
    MODERATE:  ✓ (3+ evidence, 1+ strong)
    STRONG:    ✗ (need 5+ evidence, 2+ strong, no counter)
```

**`kg explore commit "brain.core implements PolyAgent pattern" --level moderate`**:
```
✓ Claim Committed: MODERATE

  Claim: "brain.core implements PolyAgent pattern"
  Level: MODERATE
  Evidence: 3 items (1 strong)
  Trail: 4 steps supporting claim

  The claim is now recorded with commitment level MODERATE.
  Use 'kg explore evidence' to see supporting evidence.
```

### Phase 7: AGENTESE Paths ✅ (2025-12-22)
- [x] `self.explore.manifest` — Current exploration state
- [x] `self.explore.start` — Start new exploration
- [x] `self.explore.navigate` — Navigate via hyperedge
- [x] `self.explore.expand` — Expand a portal with safety
- [x] `self.explore.budget` — Budget breakdown
- [x] `self.explore.evidence` — Evidence summary
- [x] `self.explore.trail` — Navigation trail
- [x] `self.explore.commit` — Commit a claim
- [x] `self.explore.loops` — Loop detection status
- [x] `self.explore.reset` — Reset exploration state
- [x] 35 tests passing

**Location:** `impl/claude/protocols/agentese/contexts/self_explore.py`

**Note:** Originally planned as `self.context.*` but implemented as `self.explore.*` to
avoid collision with existing `self.context.*` typed-hypergraph paths. The separation
is semantically cleaner: `self.context` is about hypergraph navigation, `self.explore`
is about harnessed exploration with safety guarantees.

---

## 14. Teaching Notes (Gotchas from Implementation)

### Gotcha: NavigationBudget is Immutable

```python
# Budget is frozen—consume() returns a NEW budget
budget = NavigationBudget()
budget.consume(node_path, depth)  # WRONG: Returns new, doesn't mutate

# Correct:
budget = budget.consume(node_path, depth)  # Capture the return value
```

### Gotcha: Time Budget is Wall-Clock

```python
# Time budget counts wall-clock time, not CPU time
# Long I/O operations (network, disk) count against it
budget = NavigationBudget(time_budget_ms=5000)  # 5 seconds

# If you do:
await slow_network_call()  # Takes 3 seconds
# → Only 2 seconds remain, even if CPU was idle
```

### Gotcha: Semantic Loop Detection Requires Embeddings

```python
# Without embed_fn, semantic loops are NOT detected
detector = LoopDetector()  # embed_fn is None
# → Only detects EXACT and STRUCTURAL loops

# With embeddings:
detector = LoopDetector(embed_fn=my_embed_function)
# → Detects all three loop types
```

### Gotcha: Portal Loops are Namespaced Separately

```python
# Portal and navigation loops tracked separately
detector.check(node, edge)       # Navigation check
detector.check_portal(portal_key)  # Portal check

# "portal:tests" won't conflict with "world.tests" node path
```

### Gotcha: Evidence Strength is Computed, Not Set

```python
# DON'T set strength manually:
evidence = Evidence(strength=EvidenceStrength.STRONG)  # Wrong approach

# DO use TrailAsEvidence which computes it:
trail_evidence = trail_as_evidence.to_evidence(trail, claim)
# → Strength computed from trail length and edge diversity
```

### Gotcha: Commitment Irreversibility

```python
# Law 11.2: Once committed, cannot downgrade
ashc.commit(claim, CommitmentLevel.STRONG, trail, evidence)
# → Claim is now STRONG

# Later attempt to commit as MODERATE fails:
result = ashc.commit(claim, CommitmentLevel.MODERATE, trail, evidence)
# → result.result == "TRAIL_DOES_NOT_SUPPORT"
# → result.message == "Cannot downgrade from strong to moderate"
```

### Gotcha: Harness is Stateful—Create New for Each Exploration

```python
# DON'T reuse harness across explorations
harness = create_harness(start_node)
await explore_topic_a(harness)
await explore_topic_b(harness)  # Budget/loop state polluted!

# DO create fresh harness
harness_a = create_harness(start_node)
await explore_topic_a(harness_a)

harness_b = create_harness(start_node)  # Fresh state
await explore_topic_b(harness_b)
```

### Gotcha: NavigationResult vs ContextGraph

```python
# navigate() returns NavigationResult, NOT ContextGraph
result = await harness.navigate("tests")

# DON'T access graph directly:
result.focus  # AttributeError!

# DO check success first:
if result.success:
    new_graph = result.graph  # Safe access
    focus = new_graph.focus
```

---

## 15. Module Map

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `types.py` | Core types | `ContextNode`, `Trail`, `Evidence`, `Observer`, `Claim` |
| `budget.py` | Resource limits | `NavigationBudget`, `BudgetExhausted`, presets |
| `loops.py` | Loop detection | `LoopDetector`, `LoopResponse`, `LoopStatus` |
| `evidence.py` | Evidence gathering | `TrailAsEvidence`, `EvidenceCollector`, `EvidenceScope` |
| `commitment.py` | ASHC protocol | `ASHCCommitment`, `CommitmentRequirements` |
| `harness.py` | Main integration | `ExplorationHarness`, factory functions |

---

## 16. Test Summary

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_harness.py` | 19 | Budget, loops, trails, evidence, commitment, harness |
| `test_portal_evidence.py` | 12 | PortalExpansionEvidence properties |
| `test_portal_harness.py` | 16 | Portal expansion with harness safety |
| `test_explore.py` | 28 | CLI handler subcommands |
| `test_self_explore.py` | 35 | AGENTESE ExploreNode aspects |
| **Total** | **110** | All phases 1-7 |

---

**Filed:** 2025-12-22
**Updated:** 2025-12-22
**Voice anchor:** *"Daring, bold, creative, opinionated but not gaudy"*
