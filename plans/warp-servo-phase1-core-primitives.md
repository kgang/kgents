---
path: warp-servo/phase1-core-primitives
status: complete
progress: 100
last_touched: 2025-12-20
touched_by: claude-opus-4-5
blocking: []
enables: [warp-servo/phase2-servo-integration, warp-servo/phase3-jewel-refinement]
session_notes: |
  2025-12-20: All 8 primitives implemented and tested.
  - TraceNode: services/witness/trace_node.py + time_trace_warp.py (AGENTESE)
  - Walk: services/witness/walk.py + time_trace_warp.py (AGENTESE)
  - Offering: services/witness/offering.py + concept_offering.py (AGENTESE)
  - Covenant: services/witness/covenant.py + self_covenant.py (AGENTESE)
  - Ritual: services/witness/ritual.py + self_ritual.py (AGENTESE)
  - IntentTree: services/witness/intent.py + concept_intent.py (AGENTESE)
  - VoiceGate: services/witness/voice_gate.py + self_voice.py (AGENTESE)
  - Terrace: services/brain/terrace.py + brain_terrace.py (AGENTESE)
  66+ WARP tests passing. Sessions 3-6 completion documented.
phase_ledger:
  PLAN: complete
  DEVELOP: complete
  STRATEGIZE: complete
  IMPLEMENT: complete
  TEST: complete
entropy:
  planned: 0.3
  spent: 0.28
  returned: 0.0
---

# Phase 1: Core WARP Primitives Implementation

> *"Every action is a TraceNode. Every session is a Walk. Every workflow is a Ritual."*

**AGENTESE Context**: `time.trace.*`, `time.walk.*`, `self.ritual.*`, `concept.offering.*`
**Status**: Dormant (0 tests)
**Principles**: Composable (single outputs, category laws), Generative (spec-first)
**Cross-refs**: `spec/protocols/warp-primitives.md`, Phase 0 research outputs

---

## Core Insight

Implement the **minimum viable primitive set** that enables trace-first history. Start with TraceNode and Walk, as they provide the foundation for all other primitives.

**Priority Order**:
1. TraceNode (atom)
2. Walk (session)
3. Offering (context)
4. Covenant (permissions)
5. Ritual (workflow)
6. IntentTree (tasks)
7. VoiceGate (Anti-Sausage)
8. Terrace (knowledge)

---

## Chunks

### Chunk 1: TraceNode Foundation (3-4 hours)

**Goal**: Implement TraceNode as the atomic unit of execution.

**Files**:
```
impl/claude/services/witness/trace_node.py
impl/claude/services/witness/_tests/test_trace_node.py
impl/claude/protocols/agentese/contexts/time_trace.py
```

**Tasks**:
- [x] Implement `TraceNode` dataclass (frozen=True)
- [x] Implement `TraceLink` for causal edges
- [x] Implement `TraceNodeStore` (append-only)
- [x] Wire to existing Witness event system
- [x] Add AGENTESE node: `time.trace.node.*`
- [x] Aspects: `manifest`, `capture`, `query`, `replay`

**Laws to Verify**:
```python
def test_tracenode_immutability():
    """Law 1: TraceNodes are frozen after creation."""
    node = TraceNode(...)
    with pytest.raises(FrozenInstanceError):
        node.timestamp = datetime.now()

def test_tracenode_causality():
    """Law 2: target.timestamp > source.timestamp."""
    link = TraceLink(source=node_a.id, target=node_b.id, ...)
    assert node_b.timestamp > node_a.timestamp
```

**Exit Criteria**: 15+ tests pass, TraceNodes emit on every AGENTESE invocation.

---

### Chunk 2: Walk Session (2-3 hours)

**Goal**: Implement Walk as durable work stream.

**Files**:
```
impl/claude/services/witness/walk.py
impl/claude/services/witness/_tests/test_walk.py
impl/claude/protocols/agentese/contexts/time_walk.py
```

**Tasks**:
- [x] Implement `Walk` dataclass
- [x] Implement `WalkStore` (persistence)
- [x] Wire Walk to Forest plan files
- [x] Add AGENTESE node: `time.walk.*`
- [x] Aspects: `manifest`, `create`, `advance`, `pause`, `complete`

**Laws to Verify**:
```python
def test_walk_monotonicity():
    """Law 1: trace_nodes only grows."""
    walk.advance(trace_node_1)
    walk.advance(trace_node_2)
    assert len(walk.trace_nodes) == 2
    # Cannot remove trace_nodes

def test_walk_plan_binding():
    """Law 3: root_plan must exist in Forest."""
    with pytest.raises(PlanNotFoundError):
        Walk(root_plan="nonexistent.md", ...)
```

**Exit Criteria**: 10+ tests pass, CLI sessions create Walks.

---

### Chunk 3: Offering Context (2-3 hours)

**Goal**: Implement Offering as explicit context contract.

**Files**:
```
impl/claude/services/witness/offering.py
impl/claude/services/witness/_tests/test_offering.py
impl/claude/protocols/agentese/contexts/concept_offering.py
```

**Tasks**:
- [x] Implement `Offering` dataclass
- [x] Implement `Budget` constraints
- [x] Implement `OfferingStore`
- [x] Wire to AGENTESE invocation (every call references Offering)
- [x] Add AGENTESE node: `concept.offering.*`
- [x] Aspects: `manifest`, `create`, `consume`, `extend`, `expire`

**Laws to Verify**:
```python
def test_offering_budget_enforcement():
    """Law 1: Exceeding budget triggers review."""
    offering = Offering(budget=Budget(tokens=100))
    with pytest.raises(BudgetExceededError):
        offering.consume(tokens=150)

def test_offering_expiry():
    """Law 3: Expired Offerings deny access."""
    expired = Offering(expires_at=past_time)
    assert not expired.is_valid()
```

**Exit Criteria**: 10+ tests pass, every AGENTESE invocation references an Offering.

---

### Chunk 4: Covenant Permissions (2-3 hours)

**Goal**: Implement Covenant as negotiated permission contract.

**Files**:
```
impl/claude/services/witness/covenant.py
impl/claude/services/witness/_tests/test_covenant.py
impl/claude/protocols/agentese/contexts/self_covenant.py
```

**Tasks**:
- [x] Implement `Covenant` dataclass
- [x] Implement `ReviewGate` checkpoints
- [x] Implement `DegradationTier` fallbacks
- [x] Add AGENTESE node: `self.covenant.*`
- [x] Aspects: `manifest`, `propose`, `negotiate`, `grant`, `amend`

**Integration**: Covenant required for Ritual (Phase 1.5).

**Exit Criteria**: 10+ tests pass, Covenants gate sensitive operations.

---

### Chunk 5: Ritual Workflow (3-4 hours)

**Goal**: Implement Ritual as lawful workflow orchestration.

**Files**:
```
impl/claude/services/conductor/ritual.py
impl/claude/services/conductor/_tests/test_ritual.py
impl/claude/protocols/agentese/contexts/self_ritual.py
```

**Tasks**:
- [x] Implement `Ritual` dataclass
- [x] Implement `RitualPhase` state machine
- [x] Implement `SentinelGuard` checks
- [x] Wire to Covenant + Offering (required dependencies)
- [x] Add AGENTESE node: `self.ritual.*`
- [x] Aspects: `manifest`, `begin`, `advance`, `guard`, `complete`

**Laws to Verify**:
```python
def test_ritual_requires_covenant():
    """Law 1: Every Ritual has exactly one Covenant."""
    with pytest.raises(RitualValidationError):
        Ritual(covenant=None, ...)

def test_ritual_phase_ordering():
    """Law 4: Phase transitions follow directed cycle."""
    # Pattern 9 from crown-jewel-patterns.md
    assert ritual.can_transition(Phase.PLAN, Phase.RESEARCH)
    assert not ritual.can_transition(Phase.PLAN, Phase.REFLECT)
```

**Exit Criteria**: 15+ tests pass, CLI Conductor orchestrates Rituals.

---

### Chunk 6: IntentTree Tasks (2-3 hours)

**Goal**: Implement IntentTree as typed task decomposition.

**Files**:
```
impl/claude/services/gardener/intent_tree.py
impl/claude/services/gardener/_tests/test_intent_tree.py
impl/claude/protocols/agentese/contexts/concept_intent.py
```

**Tasks**:
- [x] Implement `Intent` dataclass with type enum
- [x] Implement `IntentTree` graph structure
- [x] Implement `IntentEdge` dependencies
- [x] Add AGENTESE node: `concept.intent.*`
- [x] Aspects: `manifest`, `create`, `decompose`, `fulfill`

**Exit Criteria**: 10+ tests pass, task decomposition uses IntentTrees.

---

### Chunk 7: VoiceGate Anti-Sausage (2-3 hours)

**Goal**: Implement VoiceGate as runtime Anti-Sausage enforcement.

**Files**:
```
impl/claude/services/voice/voice_gate.py
impl/claude/services/voice/_tests/test_voice_gate.py
impl/claude/protocols/agentese/contexts/self_voice.py
```

**Tasks**:
- [x] Implement `VoiceGate` with rules
- [x] Load voice anchors from `_focus.md`
- [x] Implement denylist patterns
- [x] Wire to CLI v7 prompt parsing
- [x] Add AGENTESE node: `self.voice.gate.*`
- [x] Aspects: `check`, `enforce`, `report`

**Voice Anchors to Encode**:
```python
VOICE_ANCHORS = [
    "Daring, bold, creative, opinionated but not gaudy",
    "The Mirror Test",
    "Tasteful > feature-complete",
    "The persona is a garden, not a museum",
    "Depth over breadth",
]
```

**Exit Criteria**: 10+ tests pass, entrypoints pass VoiceGate.

---

### Chunk 8: Terrace Knowledge (2-3 hours)

**Goal**: Implement Terrace as curated knowledge layer.

**Files**:
```
impl/claude/services/brain/terrace.py
impl/claude/services/brain/_tests/test_terrace.py
impl/claude/protocols/agentese/contexts/brain_terrace.py
```

**Tasks**:
- [x] Implement `Terrace` dataclass
- [x] Wire to existing Brain crystal system
- [x] Implement versioning
- [x] Add AGENTESE node: `brain.terrace.*`
- [x] Aspects: `manifest`, `curate`, `version`, `retrieve`

**Exit Criteria**: ✅ 10+ tests pass, Terraces store reusable knowledge.

---

## N-Phase Position

This plan covers phases:
- **PLAN**: ✅ Complete (this document)
- **DEVELOP**: Chunks 1-8 (type definitions, contracts)
- **STRATEGIZE**: Wire to CLI v7, Witness, Brain, Gardener
- **IMPLEMENT**: Code implementation
- **TEST**: Law verification, SpecGraph drift check

---

## Total Estimates

| Chunk | Hours | Tests |
|-------|-------|-------|
| TraceNode | 3-4 | 15+ |
| Walk | 2-3 | 10+ |
| Offering | 2-3 | 10+ |
| Covenant | 2-3 | 10+ |
| Ritual | 3-4 | 15+ |
| IntentTree | 2-3 | 10+ |
| VoiceGate | 2-3 | 10+ |
| Terrace | 2-3 | 10+ |
| **Total** | **19-26** | **90+** |

---

## Anti-Sausage Check

Before marking complete, verify:
- ❓ Do TraceNodes preserve causality, not smooth over gaps?
- ❓ Do Covenants require explicit human gates, not implied permissions?
- ❓ Does VoiceGate reject corporate tone, not let it slide?
- ❓ Are Rituals opinionated about phase order, not fully-connected?

---

## Cross-References

- **Spec**: `spec/protocols/warp-primitives.md`
- **Plan**: `plans/warp-servo-phase0-research.md`
- **Skills**: `docs/skills/crown-jewel-patterns.md` (Pattern 9: Directed Cycle)
- **Skills**: `docs/skills/agentese-node-registration.md`

---

*"Tasteful > feature-complete; Joy-inducing > merely functional"*
