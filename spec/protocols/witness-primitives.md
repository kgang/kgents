# Witness Primitives: The Audit Core

> *"Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook."*

**Status**: Approved Spec (Rename from WARP/Servo)
**Replaces**: `spec/protocols/warp-primitives.md`
**Implementation**: Phased migration planned (5 sessions)

---

## Purpose

The Witness primitives form the audit and traceability foundation of kgents. They answer:

1. **What happened?** — Every action is recorded
2. **Why did it happen?** — Causal links trace back to intent
3. **Who allowed it?** — Permission contracts are explicit
4. **What could it cost?** — Resource budgets are priced

**Why "Witness" over "WARP"?**

WARP was an acronym (Walk, Audit, Ritual, Primitives) — forced, requires explanation, references another product. "Witness" is already the Crown Jewel name and captures the core insight: *to observe is to participate*.

---

## The Core Insight

The Witness primitives embody a simple truth:

> **Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook.**

This gives us three levels of granularity:

| Level | Primitive | What It Captures |
|-------|-----------|------------------|
| **Atomic** | Mark | Single stimulus → response |
| **Session** | Walk | Durable work stream |
| **Workflow** | Playbook | Orchestrated multi-phase process |

Plus two contracts that enable the workflow:

| Contract | Primitive | What It Governs |
|----------|-----------|-----------------|
| **Permission** | Grant | What operations are permitted |
| **Resource** | Scope | What resources can be consumed |

---

## The Rename Map

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| **WARP** | **Witness Primitives** | Already the Crown Jewel name; no acronym needed |
| **TraceNode** | **Mark** | "Every action leaves a mark" — short, evocative, intuitive |
| **Walk** | **Walk** | Keep it — intuitive "going for a walk" feeling works |
| **Ritual** | **Playbook** | Clear, action-oriented; what a coach follows, not a ceremony |
| **Offering** | **Scope** | OAuth-adjacent; "what's in scope" is immediately understood |
| **Covenant** | **Grant** | OAuth/permission terminology; short, verb-derived |
| **Terrace** | **Lesson** | "What we learned" — direct, no metaphor needed |
| **TerrariumView** | **TerrariumView** | Keep — the terrarium metaphor is established and tests pass |
| **SceneGraph** | **Scene** | Drop the "Graph" — it's clear enough |
| **VoiceGate** | **VoiceGate** | Actually good — keep it |
| **Servo (webview)** | **Surface** | "Projection surface" — the embedding layer (Phase 2) |
| **LensMode** | **LensMode** | Keep — already clear; TIMELINE, GRAPH, SUMMARY, DETAIL |

---

## Formal Definitions

### Mark (formerly TraceNode)

```
Mark : Origin × Stimulus × Response × Umwelt × Time → Artifact

Laws:
- Law 1 (Immutability): Mark is frozen after creation
- Law 2 (Causality): target.timestamp > source.timestamp for all links
- Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark
```

A Mark is the atomic unit of execution history. It records:
- **WHAT** triggered it (stimulus)
- **WHAT** it produced (response)
- **WHO** observed it (umwelt snapshot)
- **WHEN** it happened (timestamp)
- **WHERE** in workflow (phase, if any)

### Walk (unchanged)

```
Walk : Goal × Plan × Mark* × Participant* × Phase × Status → Session

Laws:
- Law 1 (Monotonicity): Mark list only grows, never shrinks
- Law 2 (Phase Coherence): Phase transitions follow N-Phase grammar
- Law 3 (Plan Binding): root_plan must exist in Forest
```

A Walk is a durable work stream. It:
- Binds to a Forest plan file
- Accumulates Marks over time
- Tracks N-Phase workflow position
- Manages participant Umwelts

### Playbook (formerly Ritual)

```
Playbook : Grant × Scope × Phase* × Guard* → Workflow

Laws:
- Law 1 (Grant Required): Every Playbook has exactly one Grant
- Law 2 (Scope Required): Every Playbook has exactly one Scope
- Law 3 (Guard Transparency): Guards emit Marks on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle
```

A Playbook is a curator-orchestrated workflow. It requires:
- **Grant**: Permission contract
- **Scope**: Resource contract
- **Phases**: State machine following N-Phase cycle
- **Guards**: Checks at phase boundaries

### Grant (formerly Covenant)

```
Grant : Permission* × ReviewGate* × Expiry → Contract

Laws:
- Law 1 (Required): Sensitive operations require a granted Grant
- Law 2 (Revocable): Grants can be revoked at any time
- Law 3 (Gated): Review gates trigger on threshold
```

A Grant is a negotiated permission contract. It can be:
- Proposed, negotiated, granted, revoked
- Expired (unless renewed)
- Reinstated after revocation

### Scope (formerly Offering)

```
Scope : Handle* × Budget × Expiry → Context

Laws:
- Law 1 (Budget Enforcement): Exceeding budget triggers review
- Law 2 (Immutability): Scopes are frozen after creation
- Law 3 (Expiry Honored): Expired Scopes deny access
```

A Scope defines:
- What handles are accessible
- What resources can be consumed (tokens, time, operations, capital, entropy)
- When access expires

### Lesson (formerly Terrace)

```
Lesson : Topic × Content × Version × History → Knowledge

Laws:
- Law 1 (Immutability): Lessons are frozen after creation
- Law 2 (Supersession): New versions explicitly supersede old
- Law 3 (History Preserved): All versions kept for reference
- Law 4 (Topic Uniqueness): One current version per topic
```

A Lesson is curated knowledge with versioning. It:
- Crystallizes what we've learned
- Tracks evolution over time
- Never loses history

### TerrariumView (kept)

```
TerrariumView : SelectionQuery × LensMode × ProjectionTarget → Scene

Laws:
- Law 1 (Fault Isolation): Crashed view doesn't affect other views
- Law 2 (Observer Dependence): Same traces + different lens = different scene
- Law 3 (Selection Monotonicity): Narrower query ⊂ wider query results
```

A TerrariumView is the compositional lens between TraceNodes and projection surfaces.

### LensMode (kept)

```
LensMode : enum { TIMELINE, GRAPH, SUMMARY, DETAIL }
```

LensMode controls how the TerrariumView projects Marks/TraceNodes.

### Scene (formerly SceneGraph)

```
Scene : Element* × Layout × Density → Render

Laws:
- Scenes are density-aware (AD-008)
- Scenes compose vertically
- Scenes project to multiple surfaces (CLI, Web, marimo)
```

A Scene is the renderable structure for UI projection.

### Surface (formerly Servo)

```
Surface : Scene × Target → Projection

Laws:
- Surfaces are orthogonal to domain logic
- Surfaces compose with content (not vice versa)
- Same Scene → multiple Surfaces possible
```

A Surface is the projection layer that renders Scenes to targets.

---

## Integration

### AGENTESE Paths

| Old Path | New Path |
|----------|----------|
| `time.walk.*` | `time.walk.*` | (unchanged)
| `time.trace.*` | `time.mark.*` |
| `self.ritual.*` | `self.playbook.*` |
| `self.covenant.*` | `self.grant.*` |
| `self.offering.*` | `self.scope.*` |
| `self.terrace.*` | `self.lesson.*` |

### Module Paths

| Old Path | New Path |
|----------|----------|
| `services/witness/trace_node.py` | `services/witness/mark.py` |
| `services/witness/walk.py` | `services/witness/walk.py` | (unchanged)
| `services/witness/ritual.py` | `services/witness/playbook.py` |
| `services/witness/covenant.py` | `services/witness/grant.py` |
| `services/witness/offering.py` | `services/witness/scope.py` |
| `services/witness/terrace.py` | `services/witness/lesson.py` |

### Type Aliases

| Old | New |
|-----|-----|
| `TraceNodeId` | `MarkId` |
| `WalkId` | `WalkId` | (unchanged)
| `RitualId` | `PlaybookId` |
| `CovenantId` | `GrantId` |
| `OfferingId` | `ScopeId` |
| `TerraceId` | `LessonId` |

---

## Examples

### Before (WARP vocabulary)

```python
# Create a Ritual with Covenant and Offering
covenant = Covenant.propose(
    name="Implement Feature",
    permissions=["write_code", "run_tests"],
)
offering = Offering.create(
    scope=["world.codebase.*"],
    budget=Budget(tokens=10000, operations=50),
)
ritual = Ritual.create(
    name="Implement Feature",
    covenant=covenant,
    offering=offering,
)

# Start a Walk
walk = Walk.create(
    goal="Implement TraceNode primitive",
    root_plan=PlanPath("plans/warp-phase1.md"),
)

# Emit TraceNodes
trace = TraceNode.from_agentese(
    path="world.file",
    aspect="write",
    response_content="Wrote trace_node.py",
)
walk.advance(trace)
```

### After (Witness vocabulary)

```python
# Create a Playbook with Grant and Scope
grant = Grant.propose(
    name="Implement Feature",
    permissions=["write_code", "run_tests"],
)
scope = Scope.create(
    handles=["world.codebase.*"],
    budget=Budget(tokens=10000, operations=50),
)
playbook = Playbook.create(
    name="Implement Feature",
    grant=grant,
    scope=scope,
)

# Start a Walk
walk = Walk.create(
    goal="Implement Mark primitive",
    root_plan=PlanPath("plans/witness-phase1.md"),
)

# Emit Marks
mark = Mark.from_agentese(
    path="world.file",
    aspect="write",
    response_content="Wrote mark.py",
)
walk.advance(mark)
```

---

## Why These Names?

Applying the naming criteria from the plan:

| Name | Can newcomer guess? | Consistent with kgents? | Short enough? | Conflicts? | Feels like Kent? |
|------|---------------------|-------------------------|---------------|------------|------------------|
| **Mark** | ✓ "leaves a mark" | ✓ action-oriented | ✓ 4 chars | No | ✓ evocative |
| **Walk** | ✓ "going for a walk" | ✓ journey metaphor | ✓ 4 chars | No | ✓ intuitive |
| **Playbook** | ✓ what you follow | ✓ action-oriented | ✓ 8 chars | No | ✓ clear |
| **Grant** | ✓ OAuth-like | ✓ permission language | ✓ 5 chars | No | ✓ direct |
| **Scope** | ✓ OAuth-like | ✓ context language | ✓ 5 chars | No | ✓ precise |
| **Lesson** | ✓ what we learned | ✓ growth metaphor | ✓ 6 chars | No | ✓ humble |
| **Lens** | ✓ projection | ✓ already used | ✓ 4 chars | No | ✓ elegant |
| **Scene** | ✓ UI structure | ✓ projection target | ✓ 5 chars | No | ✓ familiar |
| **Surface** | ✓ where things render | ✓ Living Earth | ✓ 7 chars | No | ✓ organic |

---

## Anti-patterns

**What these primitives are NOT:**

- **Mark** is not a log entry — it has causal links and umwelt context
- **Walk** is not just a session — it binds to plans and tracks N-Phase
- **Playbook** is not a pipeline — it has guards and requires contracts
- **Grant** is not an API key — it's negotiated and revocable
- **Scope** is not a context dump — it has explicit budget constraints
- **Lesson** is not documentation — it's versioned knowledge that evolves

---

## Implementation Plan

### Phase 1: Core Types (1 session)

1. Rename type aliases and IDs
2. Rename classes and constructors
3. Update all imports
4. Run tests to verify

### Phase 2: AGENTESE Paths (1 session)

1. Update `@node` decorators with new paths
2. Update context files
3. Verify discovery
4. Run tests

### Phase 3: Stores and Services (1 session)

1. Rename store classes
2. Update persistence paths
3. Migrate any existing data
4. Run tests

### Phase 4: React Components (1 session)

1. Rename components
2. Update imports
3. Update routes
4. Run typecheck and lint

### Phase 5: Docs and Specs (1 session)

1. Rename spec files
2. Update references
3. Update CLAUDE.md
4. Update skills

### Verification After Each Phase

```bash
uv run pytest -q           # Python tests
npm run typecheck          # TypeScript
npm run lint              # Frontend lint
```

---

## Migration Notes

### Backwards Compatibility

For a transition period, type aliases can preserve old names:

```python
# Temporary aliases during migration
TraceNode = Mark
TraceNodeId = MarkId
Ritual = Playbook
RitualId = PlaybookId
Covenant = Grant
CovenantId = GrantId
Offering = Scope
OfferingId = ScopeId
Terrace = Lesson
TerraceId = LessonId
# Note: Walk stays Walk (no alias needed)
```

These should be removed after all callers are updated.

### Data Migration

If any persisted data uses old type names, a migration script should:

1. Read old format
2. Transform to new format
3. Write new format
4. Verify data integrity

---

*"The name is not the thing, but a good name makes the thing findable."*

— from the original plan, and still true.
