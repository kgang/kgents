# Rename WARP/Servo: Conceptual Rebranding

**Goal:** Replace research-artifact naming with intuitive, tasteful names that feel like Kent's voice.

---

## Current Names (The Problem)

| Current | Origin | Why It's Awkward |
|---------|--------|------------------|
| **WARP** | Windsurf reference | Acronym (Walk, Audit, Ritual, Primitives) is forced; "warp" means nothing to newcomers |
| **Servo** | Mozilla's browser engine | Confusing—we're not embedding a browser; it's a projection layer |
| **TraceNode** | Generic CS term | "Trace" is overloaded (debugging, logging); "Node" is vague |
| **Walk** | Metaphor for journey | Decent, but clashes with "tree walk" in CS |
| **Ritual** | Religious/ceremonial | Too mystical; doesn't convey "orchestrated workflow" |
| **Offering** | Religious again | "Context bundle" would be clearer |
| **Covenant** | Biblical | "Permission contract" is what it is |
| **Terrace** | Geological metaphor | Too abstract; "versioned knowledge" is the concept |
| **TerrariumView** | Terrarium = enclosed ecosystem | Cute but unclear; it's a "lens over execution history" |
| **SceneGraph** | 3D graphics term | Accurate but feels technical; it's really "renderable structure" |
| **VoiceGate** | Invented | Actually decent—"Anti-Sausage checkpoint" |

---

## Naming Constraints (Kent's Voice)

From `_focus.md` voice anchors:

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"Tasteful > feature-complete"*
> *"The persona is a garden, not a museum"*

**Good names should be:**
- Intuitive to newcomers (no need to explain the metaphor)
- Evocative but not precious (avoid over-metaphoring)
- Consistent with existing kgents naming (Crown Jewels, AGENTESE, Umwelt)
- Short enough to type frequently

**Avoid:**
- Acronyms that require expansion
- Names that reference other products (WARP → Windsurf, Servo → Mozilla)
- Names that require metaphor explanation ("Terrace is like geological layers...")
- Generic CS terms (Node, Graph, Tree, etc.)

---

## Brainstorming Prompts

For each concept, consider:

### 1. What does it actually DO?

| Concept | What It Does |
|---------|--------------|
| TraceNode | Records a single stimulus→response exchange |
| Walk | Groups traces into a durable work session |
| Ritual | Orchestrates multi-phase workflows with gates |
| Offering | Bundles context with explicit budget |
| Covenant | Grants permissions with review checkpoints |
| Terrace | Stores versioned knowledge documents |
| TerrariumView | Projects execution data into visual form |
| SceneGraph | Defines renderable structure for UI |
| VoiceGate | Enforces Anti-Sausage voice rules |

### 2. What mental model should users have?

- **Trace primitives**: "Every action leaves a mark"
- **Session management**: "Work is organized into focused sessions"
- **Workflow orchestration**: "Complex tasks follow explicit phases"
- **Context management**: "Context is priced and scoped"
- **Permission management**: "Capabilities require explicit grants"
- **Knowledge evolution**: "What we learn persists and evolves"
- **Visualization**: "Execution becomes visible"

### 3. What vocabulary fits the kgents aesthetic?

kgents uses:
- **Crown Jewels** (core services)
- **AGENTESE** (protocol)
- **Umwelt** (observer context)
- **Garden** (growth/cultivation)
- **Living Earth** (organic theme)
- **Witness** (observation/trust)
- **Forest** (plan hierarchy)

Names should feel cohesive with this vocabulary.

---

## Candidate Alternatives (Brainstorm)

### For the Overall System (currently "WARP")

| Candidate | Rationale |
|-----------|-----------|
| **Witness** | Already the Crown Jewel name; "the Witness primitives" |
| **Chronicle** | Emphasizes history/recording |
| **Lineage** | Emphasizes causal chains |
| **Provenance** | Emphasizes origin tracking |
| **Audit** | Direct and clear |

### For TraceNode (atomic execution artifact)

| Candidate | Rationale |
|-----------|-----------|
| **Mark** | "Every action leaves a mark" — short, evocative |
| **Footprint** | Fits "Walk" if we keep that |
| **Echo** | Stimulus echoes to response |
| **Artifact** | Clear but generic |
| **Record** | Simple and direct |
| **Event** | Standard but overloaded |
| **Step** | Fits workflow framing |

### For Walk (durable work session)

| Candidate | Rationale |
|-----------|-----------|
| **Session** | Most intuitive, but generic |
| **Journey** | Evocative but flowery |
| **Sprint** | Scrum connotation |
| **Run** | Simple, fits "running a task" |
| **Arc** | Story arc—captures multi-phase nature |
| **Quest** | Too game-y |

### For Ritual (orchestrated workflow)

| Candidate | Rationale |
|-----------|-----------|
| **Pipeline** | Technical but clear |
| **Protocol** | Already used for AGENTESE |
| **Procedure** | Bureaucratic |
| **Workflow** | Generic but universally understood |
| **Process** | Too generic |
| **Recipe** | Cooking metaphor—steps with gates |
| **Playbook** | Clear, action-oriented |

### For Offering (priced context bundle)

| Candidate | Rationale |
|-----------|-----------|
| **Context** | Direct but overloaded |
| **Bundle** | Simple |
| **Package** | npm connotation |
| **Scope** | OAuth-adjacent |
| **Frame** | Fits "framing the context" |
| **Window** | Context window reference |
| **Budget** | Already a field; could be promoted |

### For Covenant (permission contract)

| Candidate | Rationale |
|-----------|-----------|
| **Grant** | OAuth-like, clear |
| **Permit** | Simple |
| **License** | Software connotation |
| **Trust** | Fits trust-level framing |
| **Charter** | Formal but clear |
| **Clearance** | Security-level framing |

### For Terrace (versioned knowledge)

| Candidate | Rationale |
|-----------|-----------|
| **Page** | Wiki-like, simple |
| **Note** | Too casual |
| **Entry** | Clear but generic |
| **Crystal** | Already used in Brain (conflict) |
| **Lesson** | Captures "what we learned" |
| **Insight** | Evocative |
| **Learning** | Direct |

### For TerrariumView (projection lens)

| Candidate | Rationale |
|-----------|-----------|
| **Lens** | Already in the codebase (LensMode) |
| **View** | Standard, generic |
| **Pane** | WARP terminology |
| **Panel** | Simple |
| **Surface** | Fits "projection surface" |
| **Canvas** | Already used elsewhere |

### For SceneGraph (renderable structure)

| Candidate | Rationale |
|-----------|-----------|
| **Layout** | More intuitive |
| **Frame** | Simple |
| **Render** | Too verb-like |
| **View** | Overloaded |
| **Scene** | Keep but drop "Graph" |
| **Surface** | Fits Living Earth |

### For Servo (projection layer)

| Candidate | Rationale |
|-----------|-----------|
| **Surface** | "Projection surface" |
| **Render** | Direct |
| **Canvas** | Already used (conflict) |
| **Display** | Generic |
| **Projection** | Already the concept name |
| **Living** | "Living components" fits theme |

---

## Decision Framework

When choosing names, ask:

1. **Can a newcomer guess what it does?** (No metaphor explanation needed)
2. **Is it consistent with kgents vocabulary?** (Garden, Witness, Crown Jewels)
3. **Is it short enough to type 100 times?** (≤10 chars ideal)
4. **Does it conflict with existing terms?** (Python stdlib, React, etc.)
5. **Does it feel like Kent?** ("Daring, bold, creative, opinionated but not gaudy")

---

## Proposed Rename Map

**COMPLETED** — See `spec/protocols/witness-primitives.md` for full spec.

| Current | Proposed | Rationale |
|---------|----------|-----------|
| WARP | **Witness Primitives** | Already the Crown Jewel name; no acronym needed |
| Servo | **Surface** | "Projection surface" — fits Living Earth, clear purpose |
| TraceNode | **Mark** | "Every action leaves a mark" — short, evocative, intuitive |
| Walk | **Walk** | Keep it — intuitive "going for a walk" feeling works |
| Ritual | **Playbook** | Clear, action-oriented; what a coach follows, not a ceremony |
| Offering | **Scope** | OAuth-adjacent; "what's in scope" is immediately understood |
| Covenant | **Grant** | OAuth/permission terminology; short, verb-derived |
| Terrace | **Lesson** | "What we learned" — direct, no metaphor needed |
| TerrariumView | **Lens** | Already used in codebase (LensMode); fits projection vocabulary |
| SceneGraph | **Scene** | Drop the "Graph" — it's clear enough |
| VoiceGate | **VoiceGate** | Actually good — keep it |

### The Core Insight

> **Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook.**

This gives us three levels of granularity:
- **Mark** — atomic execution artifact
- **Walk** — durable work stream (unchanged, it's already good!)
- **Playbook** — orchestrated workflow

Plus two contracts:
- **Grant** — permission contract
- **Scope** — resource contract

---

## Implementation Plan (After Naming Decisions)

### Phase 0: Scope Audit (ALREADY DONE)

**Token Occurrences:**
| Token | Occurrences |
|-------|-------------|
| TraceNode | 773 |
| Walk | 1,002 |
| Ritual | 480 |
| Offering | 381 |
| Covenant | 493 |
| Terrace | 591 |
| SceneGraph | 288 |
| VoiceGate | 246 |
| WARP | 296 |
| Servo | 456 |
| **TOTAL** | **~5,000** |

**Files Affected:**
- Python: 64 files
- TypeScript: 51 files
- Markdown: 78 files
- **Total: ~193 files**

⚠️ **This is a significant refactor.** Recommend:
1. Do it in one focused session
2. Run tests after each phase
3. Single atomic commit

### Phase 2: Rename Order (Dependency-Aware)

1. **Core types first** (TraceNode, Walk, etc.)
2. **AGENTESE paths second** (time.walk.* → time.?.*)
3. **Stores/Services third** (TraceNodeStore → ?Store)
4. **React components fourth** (WalkCard → ?Card)
5. **Docs/specs last**

### Phase 3: Verification

```bash
# After each phase:
uv run pytest -q  # Python tests pass
npm run typecheck  # TypeScript compiles
npm run lint       # No lint errors
```

### Phase 4: Migration Commit

Single atomic commit with:
- All renames
- Updated imports
- Updated docs
- Updated AGENTESE paths

---

## Questions for Kent

1. **Which names feel most "you"?** (Quote the voice anchors if helpful)
2. **Are any current names actually good?** (Walk? VoiceGate?)
3. **Is the overall "Witness" framing working?** (Or should the Crown Jewel also rename?)
4. **How important is newcomer clarity vs. kgents aesthetic cohesion?**

---

*"The name is not the thing, but a good name makes the thing findable."*
