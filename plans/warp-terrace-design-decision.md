# WARP Terrace Design Decision

**Task**: Assess the spec-vs-implementation divergence for Terrace and recommend a path forward.

**Status**: ✅ EXECUTED — Spec updated to match implementation

---

## Context

WARP Phase 1 implements 8 primitives for trace-first, lawful workflow orchestration. Chunk 8 (Terrace) has significant divergence between spec and implementation.

**Core Question**: *Did the implementation smooth something that should stay rough, or did it find a better compression?*

---

## The Spec Vision

From `spec/protocols/warp-primitives.md`:

```python
@dataclass
class Terrace:
    """Curated, versioned knowledge layer."""
    id: TerraceId
    name: str
    ritual_templates: list[RitualTemplateId]
    intent_trees: list[IntentTreeId]
    canonical_traces: list[TraceNodeId]
    version: int
    created_at: datetime
    curated_by: CuratorId
```

**Spec's Intent**: Terrace is a *container for structured knowledge artifacts*. It bundles:
- Ritual templates (reusable workflows)
- Intent trees (goal decompositions)
- Canonical traces (exemplar execution histories)

**AGENTESE Path**: `brain.terrace.*`

**Spec Philosophy**: "WARP Drive" — curated knowledge that can be versioned, shared, and replayed.

---

## The Implementation

From `impl/claude/services/witness/terrace.py`:

```python
@dataclass(frozen=True)
class Terrace:
    """Curated knowledge with versioning."""
    id: TerraceId
    topic: str              # e.g., "AGENTESE registration"
    content: str            # The curated knowledge (text)
    version: int = 1
    supersedes: TerraceId | None = None
    status: TerraceStatus = TerraceStatus.CURRENT
    tags: tuple[str, ...] = ()
    source: str = ""
    confidence: float = 1.0
```

**Implementation's Intent**: Terrace is a *versioned text document*. It stores:
- A topic name
- Text content
- Version history via supersession chain
- Metadata (tags, source, confidence)

**Philosophy**: Simple knowledge versioning, like a wiki with history.

---

## Key Differences

| Aspect | Spec | Implementation |
|--------|------|----------------|
| **Content** | References to other primitives | Plain text |
| **Structure** | Container of artifacts | Single document |
| **Complexity** | High (requires RitualTemplate, IntentTree to exist) | Low (standalone) |
| **Use Case** | "Install this Terrace to get these workflows" | "Read this knowledge about topic X" |
| **Dependencies** | RitualTemplateId, IntentTreeId, TraceNodeId | None |

---

## Evidence to Consider

### 1. What Problems Does Each Solve?

**Spec Version**:
- "I want to share my debugging workflow with others"
- "I want to version-control a complete knowledge package"
- "I want to replay canonical traces as training data"

**Implementation Version**:
- "I want to capture what I learned about AGENTESE registration"
- "I want to see how this knowledge evolved over sessions"
- "I want to search my curated learnings by topic"

### 2. What Exists Already?

Read these files for context:
- `impl/claude/services/witness/ritual.py` — Ritual exists (29 tests)
- `impl/claude/services/witness/intent.py` — IntentTree exists (31 tests)
- `impl/claude/services/witness/trace_node.py` — TraceNode exists
- `impl/claude/services/witness/workflows.py` — **WorkflowTemplate exists** (7 templates, composable)

**Critical Question**: Is the spec's Terrace duplicating WorkflowTemplate?

WorkflowTemplate already provides:
- Bundled pipelines (actual `Pipeline` objects, not references)
- Category taxonomy (REACTIVE, PROACTIVE, DIAGNOSTIC, DOCUMENTATION)
- Trust levels and time estimates
- Composable via `extend_workflow()` and `chain_workflows()`

If Terrace-as-container adds `ritual_templates: list[RitualTemplateId]`, how is that different from (and better than) WorkflowTemplate?

### 3. Constitution Alignment

From the kgents Constitution:

> **Tasteful**: Each agent serves a clear, justified purpose.
> **Curated**: Intentional selection over exhaustive cataloging.
> **Composable**: Agents are morphisms in a category; composition is primary.
> **Generative**: Spec is compression; design should generate implementation.

**Question**: Which design is more tasteful? More composable? Does either violate "generative" (spec should generate impl)?

### 4. Anti-Sausage Check

> *"Did I smooth anything that should stay rough?"*

The simpler implementation might be "smoothing" an intentionally rough/ambitious spec vision. Or the spec might be over-engineered and the implementation is the right level of roughness.

---

## Options

### Option A: Update Spec to Match Implementation (Recommended)

**Action**: Rewrite `spec/protocols/warp-primitives.md` Terrace section to describe versioned text documents. Note that WorkflowTemplate serves the "workflow bundle" role.

**Pros**:
- Spec matches reality
- Simpler mental model
- No additional implementation work
- 58 tests already passing
- **Non-duplicative**: Terrace (knowledge) ≠ WorkflowTemplate (pipelines) — each serves distinct purpose
- **Composable**: If you need "knowledge + workflows," compose them at usage site

**Cons**:
- Loses the "WARP Drive" metaphor (installable capability packages)
- May need richer design later
- Could feel like retreat (but "Tasteful > feature-complete")

**Why This Might Be Right**: The implementation found that "versioned knowledge document" is a distinct, useful primitive that nothing else provides. The spec's "container of artifacts" is served by WorkflowTemplate. Two primitives, each doing one thing well, is more Constitutional than one monolithic primitive.

### Option B: Update Implementation to Match Spec

**Action**: Rewrite `impl/claude/services/witness/terrace.py` to store ritual/intent/trace references instead of text.

**Pros**:
- Spec-implementation alignment
- Richer capability (bundled workflows)
- Enables "install this Terrace" use case
- Preserves "WARP Drive" metaphor

**Cons**:
- Requires RitualTemplate, IntentTree, TraceNode to be mature first
- More complex (is the complexity justified?)
- Throws away 58 passing tests
- **Duplicates WorkflowTemplate** — both would be "containers of workflow artifacts"
- May be over-engineering

**Why This Might Be Wrong**: If Terrace-as-container is just WorkflowTemplate with extra fields, we violate "Curated" (two things doing similar jobs).

### Option C: Two-Layer Design

**Action**: Keep current Terrace as "TerraceNote" (simple text), add "TerraceDrive" (spec's bundle) as separate primitive.

**Pros**:
- Both use cases served
- No breaking changes
- Can evolve independently

**Cons**:
- Two concepts where one might suffice
- Naming confusion (Terrace vs TerraceNote vs TerraceDrive)
- May violate "curated" principle (two things doing similar jobs)

### Option D: Defer Decision

**Action**: Mark spec as "aspirational", implementation as "v1", revisit when use cases are clearer.

**Pros**:
- No wasted work
- Reality will clarify needs
- Ship what works now

**Cons**:
- Spec rot continues
- Technical debt accumulates
- Violates "generative" principle

---

## Files to Read

Before deciding, read:

1. `spec/protocols/warp-primitives.md` — Full spec context
2. `impl/claude/services/witness/terrace.py` — Current implementation
3. `impl/claude/services/witness/_tests/test_terrace.py` — Test coverage
4. `impl/claude/services/witness/workflows.py` — Existing WorkflowTemplate (overlap?)
5. `plans/warp-phase1-reflection.md` — Implementer's concerns
6. `CLAUDE.md` — Project principles and voice

---

## Deliverable

Provide:

1. **Recommendation** (A, B, C, D, or other)
2. **Reasoning** (3-5 sentences grounded in evidence)
3. **Risks** of the chosen path
4. **Next Action** (specific file/code change if applicable)

---

## Grounding

Before answering, quote one of Kent's voice anchors:

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"The Mirror Test: Does K-gent feel like me on my best day?"*
> *"Tasteful > feature-complete"*
> *"The persona is a garden, not a museum"*
> *"Depth over breadth"*

Use this to calibrate your recommendation.

---

*"Spec is compression; design should generate implementation."* — But what if the implementation found a better compression?

---

## Assessment Record

**Reviewed by**: Claude Opus 4
**Date**: 2025-12-20

### Grounding
> *"Tasteful > feature-complete"*

The spec's Terrace is more feature-complete (bundles workflows + intents + traces). The implementation's Terrace is more tasteful (does one thing: versioned knowledge documents).

### Recommendation
**Choice**: A — Update Spec to Match Implementation

### Reasoning

1. **Non-duplication**: `WorkflowTemplate` in `workflows.py` already serves the "installable workflow bundle" role with 7 templates, category taxonomy, trust levels, and composition via `extend_workflow()` / `chain_workflows()`. The spec's Terrace-as-container would duplicate this.

2. **Distinct value**: The implementation's Terrace (versioned knowledge documents) fills a gap nothing else addresses — crystallizing "what we learned" across sessions with topic-based retrieval, evolution tracking, and supersession chains. This is genuinely useful.

3. **Composition over aggregation**: The Constitution's **Composable** principle says primitives should combine at the usage site. If you need "knowledge + workflows," compose `Terrace` + `WorkflowTemplate`. Don't bundle them into one monolithic primitive.

4. **Evidence of maturity**: 58 tests validate four clear laws (Immutability, Supersession, History Preserved, Topic Uniqueness). This is a complete, coherent abstraction — not a half-baked simplification.

5. **Generative principle satisfied**: The implementation *is* a valid compression of "curated, versioned knowledge layer" — just a different (and arguably better) compression than the spec proposed.

### Risks

| Risk | Mitigation |
|------|------------|
| Loss of "WARP Drive" metaphor | Document that WorkflowTemplate serves this role |
| Future need for richer Terrace | Can always add `TerraceBundle` later if use case emerges |
| Spec authority erosion | Add "Refinement Note" explaining the design decision |

### Next Action

1. **Edit `spec/protocols/warp-primitives.md`** — Update Terrace section:

```python
@dataclass(frozen=True)
class Terrace:
    """Curated, versioned knowledge document."""
    id: TerraceId
    topic: str                    # e.g., "AGENTESE registration"
    content: str                  # The curated knowledge
    version: int
    supersedes: TerraceId | None  # Previous version this replaces
    status: TerraceStatus         # CURRENT, SUPERSEDED, DEPRECATED, ARCHIVED
    tags: tuple[str, ...]
    source: str                   # Where this knowledge came from
    confidence: float             # 0.0-1.0
    created_at: datetime
```

2. **Add refinement note** to spec:
> *Design Refinement*: The original vision of Terrace as a container for workflow artifacts was refined during implementation. The "installable workflow bundle" use case is served by `WorkflowTemplate` (see `impl/claude/services/witness/workflows.py`). Terrace focuses on versioned knowledge documents — capturing learnings that evolve across sessions.

3. **Update AGENTESE path** in spec: Keep `brain.terrace.*` but update aspects to reflect document operations (manifest, create, evolve, search, history).

### Anti-Sausage Self-Check

- **Did I smooth anything that should stay rough?**
  No — the implementation is intentionally simpler but not dumbed-down. It serves a distinct purpose (knowledge crystallization) that the spec's container vision would have obscured by bundling too many concerns.

- **Did I add words Kent wouldn't use?**
  No — stayed within established vocabulary (Terrace, crystallize, supersession, laws).

- **Is this still daring, bold, creative?**
  Yes — the decision to let implementation refine spec (rather than treating spec as sacred) is itself a bold move. It honors the Constitution's **Generative** principle: *"If you can't compress, you don't understand."* The implementation found a better compression.

---

## Execution Log

**Date**: 2025-12-20

### Changes Made to `spec/protocols/warp-primitives.md`:

1. **Updated Terrace section** (lines 185-219):
   - Changed title from "WARP Drive" to "Versioned Knowledge"
   - Added Design Refinement note explaining the decision
   - Updated dataclass to match implementation (topic, content, supersedes, status, tags, source, confidence)
   - Added TerraceStatus enum
   - Added Philosophy and Use Cases sections
   - Added note pointing to WorkflowTemplate for bundle use case

2. **Added Terrace Laws** (lines 291-298):
   - Law 1 (Immutability)
   - Law 2 (Supersession)
   - Law 3 (History Preserved)
   - Law 4 (Topic Uniqueness)

3. **Updated AGENTESE Paths table** (line 314):
   - Changed aspects from `manifest, curate, version, retrieve` to `manifest, create, evolve, search, history`

4. **Updated Implementation Reference** (lines 349-351):
   - Fixed Terrace path: `impl/claude/services/witness/terrace.py`
   - Fixed VoiceGate path: `impl/claude/services/witness/voice_gate.py`
   - Added WorkflowTemplate reference with note about bundled pipelines

### Result

Spec and implementation are now aligned. The "Generative" principle is satisfied: the spec compresses the implementation's design faithfully.
