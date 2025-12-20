# Oblique Crown Jewels: The Daemon's Orchestra

> *"What lies adjacent to the path is often more interesting than the path itself."*
> *"The persona is a garden, not a museum."* — Kent's standing intent

**Date**: 2025-12-19
**Context**: Brainstorming session for CLI v7 enabling functionality
**Constraint**: Must be Metaphysical Crown Jewels following AD-009
**Enhancement**: kgentsd integration for "set it and forget it" passive operation

---

## 🎯 Grounding in Kent's Intent

*"Daring, bold, creative, opinionated but not gaudy"*
*"Tasteful > feature-complete; Joy-inducing > merely functional"*
*"Depth over breadth"*

### The Mirror Test

Does this feel like Kent on his best day? A great developer environment doesn't just track—it **cultivates**:
- Notices patterns before they become problems
- Builds trust through consistent, valuable observations
- Earns the right to act autonomously through track record
- Knows when NOT to intervene (the Sommelier whispers, never shouts)

---

## The Oblique Principle

These aren't features OF the CLI—they're features that make the CLI **worth having**. Each is a full Crown Jewel with:
- **Polynomial state machine** (mode-dependent behavior per AD-002)
- **Operad grammar** (composition laws, inheritance from DESIGN_OPERAD)
- **Sheaf coherence** (local views → global consistency)
- **AGENTESE nodes** (five contexts, observer-dependent)
- **D-gent integration** (causal memory, stigmergic surface)
- **Flux lifting** (event-driven, never timer-driven)
- **kgentsd wiring** (passive daemon enables "set and forget")

---

## The kgentsd Symbiosis

> *"The Witness is not a replacement—it's an amplification."*

Every Oblique Crown Jewel hooks into **kgentsd** (the 8th Crown Jewel) for passive, event-driven operation. No timers. No polling. The daemon watches; the jewels react.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         kgentsd EVENT SOURCES                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │Filesystem│ │   Git   │ │  Tests  │ │AGENTESE │ │   CI    │               │
│  │ inotify  │ │  hooks  │ │ pytest  │ │SynergyBus│ │webhook │               │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘               │
└───────┼──────────┼──────────┼──────────┼──────────┼────────────────────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OBLIQUE JEWEL REACTORS                                  │
│                                                                              │
│  Scribe ←── FileChanged, GitCommit → auto-record sessions                   │
│  Chronicler ←── SessionComplete → auto-narrate chapters                     │
│  Cartographer ←── FileChanged → auto-update maps                            │
│  Librarian ←── ArtifactCreated → auto-index                                 │
│  Synthesizer ←── PlanComplete → auto-weave synthesis                        │
│  Dramaturg ←── MilestoneReached → auto-detect act transitions               │
│  Sommelier ←── PatternDetected → auto-suggest                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Set-It-And-Forget-It Promise

Once enabled, these jewels **just work**. You don't invoke them—they invoke themselves:

```bash
# Enable once
$ kg self.witness.enable --jewels="scribe,chronicler,cartographer"
Witness enabled. The daemon watches. The jewels respond.

# Forget about it. Work normally.
$ kg world.file.edit path="..."  # Scribe auto-records
$ git commit -m "feat: ..."       # Chronicler auto-narrates
$ npm test                        # Cartographer notes the hot zone

# Later, discover what grew
$ kg self.chronicler.timeline
  → A living story of your work session
```

---

## Categorical Foundation: The Unified Stack

Every Oblique Jewel instantiates the **same three-layer pattern** (AD-006):

| Layer | Purpose | What It Does |
|-------|---------|--------------|
| **PolyAgent** | State machine with mode-dependent inputs | Each jewel has states (DORMANT, LISTENING, ACTIVE, SYNTHESIZING) |
| **Operad** | Composition grammar | How jewel operations combine; laws that guarantee validity |
| **Sheaf** | Global coherence from local views | Distributed observations → unified output |

**The Flux Lifting** (from `spec/agents/flux.md`):

> *"Agents are corpses. They only move when poked. Flux lifts agents from discrete transformations to continuous flow."*

```python
# Static: Agent that responds when called
result = await chronicler.invoke(event)  # Discrete: twitch, return, die

# Dynamic: FluxAgent that lives in the event stream
async for narrative in chronicler_flux.start(events):  # Continuous: live, respond, flow
    yield narrative
```

---

## Crown Jewel 1: The Scribe

> *"Every keystroke is history. The Scribe captures it—without being asked."*

### The Vision

**Passive, event-driven session recording.** The Scribe doesn't wait for `record`—it listens to kgentsd and captures automatically. Court stenographer mode: always on, never intrusive.

### kgentsd Integration (The Magic)

```python
# In services/scribe/flux.py
class ScribeFlux(FluxAgent[ScribeState, SystemEvent, TranscriptChunk]):
    """
    Event-driven scribe using Flux lifting.

    Reacts passively to:
    - Terminal commands (via AGENTESE invocation events)
    - File operations (via filesystem watcher)
    - Git operations (via git watcher)

    NO TIMERS. Set it and forget it.
    """

    async def react(self, event: SystemEvent) -> AsyncGenerator[TranscriptChunk, None]:
        match event:
            case AgenteseInvocation(path=path, observer=obs):
                yield TranscriptChunk(
                    type="command",
                    content=f"$ kg {path}",
                    observer=obs.archetype,
                    timestamp=event.timestamp,
                )
            case FileModified(path=path) if self._is_session_relevant(path):
                yield TranscriptChunk(
                    type="edit",
                    content=f"Edited: {path}",
                    diff_summary=await self._get_diff_summary(path),
                    timestamp=event.timestamp,
                )
            case GitCommit(sha=sha, message=msg):
                yield TranscriptChunk(
                    type="commit",
                    content=f"Committed: {msg[:50]}",
                    sha=sha,
                    timestamp=event.timestamp,
                )
```

### Metaphysical Fullstack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   Live transcript │ Session replay │ Shareable HTML │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     time.scribe.manifest, .annotate, .export          │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node("time.scribe", contracts={...})             │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/scribe/ — Passive transcription engine   │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        SCRIBE_OPERAD ← extends TEMPORAL_OPERAD           │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      ScribePolynomial[DORMANT|LISTENING|RECORDING]     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. FLUX + kgentsd        ScribeFlux reacts to daemon events                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Polynomial States

```python
SCRIBE_POLYNOMIAL = PolyAgent[ScribeState, ScribeEvent, TranscriptChunk](
    positions=frozenset({
        ScribeState.DORMANT,      # Installed but not listening
        ScribeState.LISTENING,    # Passive recording (default after enable)
        ScribeState.ANNOTATING,   # Human is adding notes
        ScribeState.EXPORTING,    # Generating output
    }),
    directions=lambda state: {
        ScribeState.DORMANT: {"enable", "configure"},
        ScribeState.LISTENING: {"annotate", "mark", "export", "disable"},
        ScribeState.ANNOTATING: {"save_annotation", "cancel"},
        ScribeState.EXPORTING: {"complete", "cancel"},
    }[state],
    transition=scribe_transition,
)
```

### Visual Projection: Auto-Updating Timeline

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📝 SCRIBE: Session "2025-12-19-morning"               ● LISTENING  01:47:23 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  09:15:23  ┌──────────────────────────────────────────────────────────────┐  ║
║            │ $ kg self.forest.manifest                                    │  ║
║            └──────────────────────────────────────────────────────────────┘  ║
║            → Forest health: 12 active plans, 789 tests passing              ║
║                                                                               ║
║  09:18:45  🔧 Edited: protocols/cli/hollow.py (+15/-3 lines)                ║
║            ├─ Added: path-first routing dispatch                            ║
║            └─ Removed: legacy fallback handler                              ║
║                                                                               ║
║  09:23:12  ⚡ Committed: "feat(cli): Add path-first routing"                ║
║            └─ sha: a7b3c2d                                                   ║
║                                                                               ║
║  09:25:00  💬 Auto-annotation: "Entering deep focus on routing logic"       ║
║            └─ (detected: 3+ consecutive edits to same module)               ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║  🎯 The Scribe listens. The Scribe records. The Scribe never interrupts.    ║
║   [A]nnotate  [M]ark  [E]xport  [Esc] Just keep working                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 2: The Chronicler

> *"Every great project has a story. The Chronicler writes it while you work."*
> *"The Scribe records events. The Chronicler finds the meaning."*

### The Vision

**Passive narrative synthesis.** The Chronicler watches session patterns and auto-generates chapter narratives. When the Scribe detects a natural break (long pause, branch switch, session end), the Chronicler awakens to weave the story.

### kgentsd Integration

```python
class ChroniclerFlux(FluxAgent[ChroniclerState, SystemEvent, NarrativeChunk]):
    """
    Narrative synthesis via Flux.

    Triggers on:
    - Session breaks (15+ min pause detected by kgentsd)
    - Git branch switches
    - Phase transitions (SENSE → ACT, etc.)
    - Manual chapter markers

    Uses LLM to synthesize Scribe transcripts into narrative.
    """

    async def react(self, event: SystemEvent) -> AsyncGenerator[NarrativeChunk, None]:
        match event:
            case SessionBreak(duration_minutes=dur) if dur > 15:
                # Auto-chapter on long breaks
                transcript = await self._get_recent_transcript()
                yield await self._narrate_chapter(
                    transcript,
                    trigger="pause",
                    title=f"Chapter: Work session ({dur}min)"
                )
            case GitBranchSwitch(from_branch=old, to_branch=new):
                yield await self._narrate_transition(old, new)
            case NPhaseTransition(from_phase=old, to_phase=new):
                yield await self._narrate_phase_shift(old, new)
```

### The Narrative Engine

```python
class NarrativeEngine:
    """
    Transforms raw events into story.

    Uses K-gent's personality space navigation to write in
    Kent's voice (per spec/principles.md §Personality Space).
    """

    async def synthesize(
        self,
        transcript: list[TranscriptChunk],
        style: Literal["diary", "technical", "retrospective"] = "diary"
    ) -> str:
        # Navigate to appropriate personality coordinates
        personality = {
            "diary": {"warmth": 0.7, "directness": 0.8, "technical_depth": 0.5},
            "technical": {"warmth": 0.3, "directness": 0.9, "technical_depth": 0.9},
            "retrospective": {"warmth": 0.5, "directness": 0.7, "technical_depth": 0.6},
        }[style]

        return await self.llm.synthesize(
            transcript=transcript,
            persona=personality,
            template=NARRATIVE_TEMPLATES[style],
        )
```

### Visual Projection: The Chronicle

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📖 THE CHRONICLE OF CLI v7                                  3 chapters told ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  CHAPTER I: "The Discovery" (09:00 - 10:30)                                  ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  │ Kent began by surveying the forest—twelve active plans, a testament      │
║  │ to weeks of cultivation. The infra/ghost/ directory caught his eye:      │
║  │ a timer-driven daemon from an earlier era. "No more timers," he          │
║  │ decided. "Events only."                                                   │
║  │                                                                           │
║  │ The hollow.py file revealed the architecture: path-first dispatch,       │
║  │ exactly what CLI v7 needed. A motto emerged: "Wire, don't build."        │
║  └───────────────────────────────────────────────────────────────────────   ║
║                                                                               ║
║  CHAPTER II: "The Three Pillars" (10:30 - 12:15)                             ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  │ File I/O Primitives, Deep Conversation, Collaborative Canvas—three       │
║  │ pillars crystallized from scattered ideas. The Synthesizer gathered      │
║  │ 47 fragments from memory, chats, and plans...                            │
║  └───────────────────────────────────────────────────────────────────────   ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   [P]ublish to docs/  [E]dit chapter  [C]ontinue story  [Q]uit               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 3: The Cartographer

> *"A map is not the territory, but a good map makes the territory navigable."*
> *"Static diagrams rot immediately. Living maps evolve with the codebase."*

### The Vision

**Passive codebase visualization.** The Cartographer maintains a live map that updates as files change. No manual "generate diagram"—the map is always current because kgentsd feeds it file events.

### kgentsd Integration

```python
class CartographerFlux(FluxAgent[CartoState, FileEvent, MapUpdate]):
    """
    Living map via Flux.

    Maintains incremental map state that updates on:
    - File creation/deletion (structure changes)
    - File modification (heat map updates)
    - Import changes (dependency graph updates)

    Uses Sheaf gluing to maintain coherence across views.
    """

    async def react(self, event: FileEvent) -> AsyncGenerator[MapUpdate, None]:
        match event:
            case FileCreated(path=path):
                yield await self._add_to_map(path)
                yield await self._update_dependencies(path)
            case FileModified(path=path):
                yield await self._increment_heat(path)
                yield await self._check_import_changes(path)
            case FileDeleted(path=path):
                yield await self._remove_from_map(path)
```

### The Cartographic Sheaf

```python
class CartographySheaf(Sheaf[Territory, LocalView, GlobalMap]):
    """
    Coherent maps from local observations.

    Local views:
    - Directory structure (from filesystem watcher)
    - Dependency graph (from import analysis)
    - Heat map (from modification frequency)
    - Attention focus (from recent file accesses)

    Gluing condition: All views agree on file existence and modification times.
    Global section: Unified map with structure + dependencies + heat + focus.
    """

    def glue(self, views: dict[str, LocalView]) -> GlobalMap:
        structure = views["structure"]
        deps = views["dependencies"]
        heat = views["heat"]
        focus = views["attention"]

        return GlobalMap(
            nodes=[self._merge_node(f, deps, heat, focus) for f in structure.files],
            edges=deps.edges,
            hot_zones=heat.top_k(10),
            current_focus=focus.active_file,
        )
```

### Visual Projection: The Living Map

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🗺️  CARTOGRAPHER: impl/claude/                          Live • Updated 3s  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                        ┌─────────────┐                                       ║
║                   ┌────│  protocols/ │────┐                                  ║
║                   │    └─────────────┘    │                                  ║
║                   │    ↑ YOU ARE HERE ↑   │                                  ║
║           ┌───────▼───────┐       ┌───────▼───────┐                         ║
║           │  agentese/    │       │     cli/      │  ← 🔥 BLAZING           ║
║           │  ○○○○○○○○○    │       │  ●●●●●●●●●●  │    (23 changes today)   ║
║           │  steady       │       │  ACTIVE ZONE  │                         ║
║           └───────┬───────┘       └───────┬───────┘                         ║
║                   │  imports              │ imports                          ║
║           ┌───────▼───────┐       ┌───────▼───────┐                         ║
║           │   services/   │◄──────│    agents/    │                         ║
║           │  ○○●●●○○○○    │  uses │  ○○○○○○○○○    │                         ║
║           │  moderate     │       │  cool         │                         ║
║           └───────────────┘       └───────────────┘                         ║
║                                                                               ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ 💡 Insight: protocols/cli/ is 73% of this week's activity.            │  ║
║  │    Consider extracting shared patterns to services/cli_patterns/.     │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
║  Legend: ○ cool  ● warm  ●● hot  🔥 blazing                                 ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   [F]ocus on path  [H]eat mode  [D]ependencies  [E]xport SVG  [Q]uit        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 4: The Librarian

> *"Every artifact has a place. The Librarian knows where."*
> *"Chaos → Order, but never at the cost of serendipity."*

### The Vision

**Passive semantic indexing.** The Librarian listens to all artifact creation events and maintains a semantic index. No manual "reindex"—new artifacts are indexed as they appear.

### kgentsd Integration

```python
class LibrarianFlux(FluxAgent[LibrarianState, ArtifactEvent, IndexUpdate]):
    """
    Passive indexing via Flux.

    Watches for:
    - D-gent artifact creation (crystals, sessions, etc.)
    - File creation (new markdown, code files)
    - Plan completions (from forest protocol)

    Maintains:
    - Semantic embeddings for search
    - Relationship graph (what relates to what)
    - Staleness tracking (what needs attention)
    """

    async def react(self, event: ArtifactEvent) -> AsyncGenerator[IndexUpdate, None]:
        match event:
            case DgentWrite(key=key, value=value):
                embedding = await self._embed(value)
                relations = await self._find_relations(embedding)
                yield IndexUpdate(
                    artifact_id=key,
                    embedding=embedding,
                    relations=relations,
                    indexed_at=datetime.now(),
                )
            case PlanComplete(plan_id=pid, outcomes=outcomes):
                yield await self._index_plan_completion(pid, outcomes)
```

### The Taxonomy Operad

```python
TAXONOMY_OPERAD = Operad(
    name="TAXONOMY",
    operations={
        # Classification operations
        "categorize": Operation(arity=1, output="Category"),
        "relate": Operation(arity=2, output="Relationship"),
        "cluster": Operation(arity="*", output="Cluster"),

        # Search operations
        "find": Operation(arity=1, output="Results", requires="embedding_index"),
        "similar": Operation(arity=1, output="SimilarArtifacts"),

        # Maintenance operations
        "prune_stale": Operation(arity=0, output="PruneResult", effects=["writes"]),
        "reindex": Operation(arity=1, output="IndexResult"),
    },
    laws=[
        Law(name="categorization_stability",
            description="Recategorizing an artifact produces same category"),
        Law(name="relation_symmetry",
            description="If A relates to B, B relates to A"),
    ],
    # Inherit from base operad
    **TAXONOMY_BASE_OPERAD.operations,
)
```

### Visual Projection: The Living Catalog

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📚 LIBRARIAN                                             1,247 artifacts    ║
║     Auto-indexing: ON                               Last indexed: 3 min ago  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  SHELVES                        │  RECENT (auto-indexed)                     ║
║  ─────────────────────────────  │  ─────────────────────────────             ║
║  📁 Crystals (memory)     342   │  ✨ cli-v7-synthesis.md       just now     ║
║  📁 Plans (forest)        127   │  ✨ session-2025-12-19.json   2 min ago    ║
║  📁 Sessions (gardener)    89   │  ✨ chronicler-ch2.md         5 min ago    ║
║  📁 Chats (soul)          156   │                                            ║
║  📁 Code artifacts        234   │  NEEDS ATTENTION                           ║
║  📁 Exports               145   │  ─────────────────────────────             ║
║  📁 Orphaned              12    │  ⚠️ 7 plans untouched 30+ days             ║
║                                 │  ⚠️ 3 orphaned crystals (no refs)          ║
║  SEARCH: [                  ]   │  ⚠️ 12 artifacts missing embeddings        ║
║                                 │                                            ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ 💡 The Librarian notices: You've written about "routing" 12 times     │  ║
║  │    this week. Consider creating a synthesis document.                  │  ║
║  │    [Create synthesis] [Dismiss for 4h]                                │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   [F]ind  [S]helf  [R]elate  [P]rune stale  [Q]uit                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 5: The Synthesizer

> *"Scattered notes become coherent documents. Fragments become wholes."*
> *"The opposite of analysis—creative aggregation."*

### The Vision

**Passive synthesis on triggers.** The Synthesizer awakens when patterns suggest synthesis is valuable: topic mentioned 10+ times, plan completed, week boundary crossed.

### kgentsd Integration

```python
class SynthesizerFlux(FluxAgent[SynthState, TriggerEvent, Synthesis]):
    """
    Pattern-triggered synthesis via Flux.

    Awakens on:
    - Topic frequency threshold (10+ mentions in 24h)
    - Plan completion (synthesize outcomes)
    - Week boundary (weekly digest)
    - Manual request

    Uses Librarian's index for fragment gathering.
    Uses Chronicler's narrative engine for weaving.
    """

    async def react(self, event: TriggerEvent) -> AsyncGenerator[Synthesis, None]:
        match event:
            case TopicThreshold(topic=topic, mentions=n):
                fragments = await self.librarian.gather(topic)
                yield await self._weave(fragments, style="emergence")
            case WeekBoundary():
                all_fragments = await self.librarian.gather("*", since="week")
                yield await self._weave(all_fragments, style="digest")
```

### The Sheaf of Understanding

```python
class SynthesisSheaf(Sheaf[Topic, Fragment, UnifiedDocument]):
    """
    Coherent documents from scattered fragments.

    Local sections (from different sources):
    - Crystals (self.memory)
    - Session notes (gardener)
    - Chat turns (soul)
    - Plan fragments (forest)
    - Code comments (files)

    Gluing: Fragments about same concept are compatible.
    Global section: Unified document with clear structure.
    """

    def glue(self, sections: dict[str, list[Fragment]]) -> UnifiedDocument:
        # Sort by timestamp, deduplicate by semantic similarity
        all_fragments = self._merge_and_dedupe(sections)

        # Use SYNTHESIS_OPERAD to determine structure
        outline = self.operad.outline(all_fragments)

        # Weave with LLM
        return self._weave_with_outline(all_fragments, outline)
```

### Visual Projection: The Weaving

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🧵 SYNTHESIZER: Weaving "CLI v7 Architecture"                               ║
║     Triggered by: 23 mentions of "routing" in last 24h                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║       crystals (12)        sessions (8)         chats (15)                   ║
║       ◦ ◦ ◦ ◦              ◦ ◦ ◦ ◦              ◦ ◦ ◦ ◦ ◦                   ║
║       ◦ ◦ ◦ ◦              ◦ ◦ ◦ ◦              ◦ ◦ ◦ ◦ ◦                   ║
║       ◦ ◦ ◦ ◦                                   ◦ ◦ ◦ ◦ ◦                   ║
║           │                    │                     │                       ║
║           └────────────────────┼─────────────────────┘                       ║
║                                │                                             ║
║                                ▼                                             ║
║              ╔══════════════════════════════════╗                            ║
║              ║   WEAVING IN PROGRESS...         ║                            ║
║              ║   ████████████░░░░░░░  65%       ║                            ║
║              ║                                  ║                            ║
║              ║   Structure detected:            ║                            ║
║              ║   1. Vision (6 fragments)        ║                            ║
║              ║   2. Path-first routing (8)      ║                            ║
║              ║   3. AGENTESE integration (5)    ║                            ║
║              ║   4. Open questions (4)          ║                            ║
║              ╚══════════════════════════════════╝                            ║
║                                │                                             ║
║                                ▼                                             ║
║                       📄 cli-v7-synthesis.md                                 ║
║                          (auto-saved to docs/)                               ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   Weaving automatically. [V]iew preview  [P]ause  [Q]uit                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 6: The Dramaturg

> *"Work has narrative structure. The Dramaturg reveals it."*
> *"Tasks become stories. Sprints become acts. Projects become epics."*

### The Vision

**Passive story arc detection.** The Dramaturg watches event patterns and detects dramatic structure: rising action, complications, climaxes, resolution. Makes work feel like a story you're living.

### The Dramatic Polynomial

```python
DRAMATURG_POLYNOMIAL = PolyAgent[DramaState, WorkEvent, ArcUpdate](
    positions=frozenset({
        DramaState.EXPOSITION,      # Setting up context
        DramaState.RISING_ACTION,   # Building complexity
        DramaState.CLIMAX,          # Peak tension
        DramaState.FALLING_ACTION,  # Resolution in progress
        DramaState.DENOUEMENT,      # Reflection phase
    }),
    directions=lambda state: {
        DramaState.EXPOSITION: {"begin_act", "add_context"},
        DramaState.RISING_ACTION: {"complicate", "escalate", "reveal"},
        DramaState.CLIMAX: {"resolve", "twist"},
        DramaState.FALLING_ACTION: {"tie_loose_ends", "reflect"},
        DramaState.DENOUEMENT: {"conclude", "set_up_sequel"},
    }[state],
    transition=drama_transition,
)

# Transition rules detect dramatic moments
def drama_transition(state: DramaState, event: WorkEvent) -> tuple[DramaState, ArcUpdate]:
    """
    Signal aggregation (Pattern 4 from crown-jewel-patterns.md).

    Multiple signals → confidence + transition decision.
    """
    signals = [
        event.test_failures_resolved > 5,      # Major breakthrough
        event.files_changed > 20,               # Significant refactor
        event.commit_messages_contain("fix:"),  # Resolution indicators
        event.time_since_last_commit > hours(4), # Deep work session ending
    ]

    confidence, reasons = aggregate_signals(signals)

    if confidence > 0.8 and state == DramaState.RISING_ACTION:
        return DramaState.CLIMAX, ArcUpdate(
            type="climax_detected",
            reasons=reasons,
            dramatic_question="Can this architecture actually work?",
        )
    # ... more transitions
```

### Visual Projection: The Story Arc

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎭 DRAMATURG: The Story of kgentsd                                          ║
║     Current Act: II "Complication"    Tension: ████████░░ 80%               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                                          ╱╲                                  ║
║                                         ╱  ╲  CLIMAX (predicted)            ║
║                                        ╱    ╲ "The vertical slice works"    ║
║                                       ╱      ╲                              ║
║                              ╱╲      ╱        ╲                              ║
║                             ╱  ╲    ╱          ╲                             ║
║                            ╱    ╲  ╱            ╲                            ║
║             ╱╲            ╱      ╲╱              ╲                           ║
║            ╱  ╲          ╱         ← YOU ARE HERE ╲                         ║
║           ╱    ╲        ╱                          ╲                         ║
║          ╱      ╲      ╱                            ╲                        ║
║  ───────╱        ╲────╱                              ╲───────────────        ║
║                                                                               ║
║   ACT I              ACT II                ACT III                           ║
║   "Discovery"        "Complication"        "Resolution"                      ║
║   Ghost → Witness    Event architecture    Production-ready                  ║
║   Trust model        Cross-jewel wiring    8th Jewel crowned                 ║
║                                                                               ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║  Current dramatic question: "Can passive event-driven agents replace        ║
║  the timer-driven ghost without losing reliability?"                         ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   [A]rc view  [T]ension graph  [P]redict climax  [D]enouement  [Q]uit       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Crown Jewel 7: The Sommelier

> *"The right tool at the right moment. I know what you need before you ask."*
> *"Whispers, never shouts. Suggestions, never commands."*

### The Vision

**Passive, context-aware suggestions.** The Sommelier observes work patterns and surfaces relevant capabilities at the right moment. Uses dismissal memory (Pattern 5) to avoid nagging.

### The Sommelier Polynomial

```python
SOMMELIER_POLYNOMIAL = PolyAgent[SommelierState, ContextEvent, Suggestion](
    positions=frozenset({
        SommelierState.OBSERVING,       # Watching, not suggesting
        SommelierState.CONSIDERING,     # Pattern detected, evaluating
        SommelierState.WHISPERING,      # Showing a suggestion
        SommelierState.DORMANT,         # User dismissed, cooling down
    }),
    directions=lambda state: {
        SommelierState.OBSERVING: {"pattern_detected"},
        SommelierState.CONSIDERING: {"suggest", "suppress"},
        SommelierState.WHISPERING: {"accept", "dismiss", "timeout"},
        SommelierState.DORMANT: {"cooldown_complete"},
    }[state],
    transition=sommelier_transition,
)
```

### The Pairing Operad

```python
PAIRING_OPERAD = Operad(
    name="PAIRING",
    operations={
        # Context analysis
        "read_context": Operation(arity=0, output="Context"),
        "detect_pattern": Operation(arity=1, output="Pattern"),

        # Pairing (the core operation)
        "pair": Operation(arity=2, output="Suggestion"),

        # Filtering
        "check_dismissal": Operation(arity=1, output="bool"),
        "check_relevance": Operation(arity=2, output="float"),
    },
    laws=[
        Law(name="dismissal_respected",
            description="Dismissed suggestions have 4h cooldown"),
        Law(name="whisper_not_shout",
            description="Max 1 suggestion visible at a time"),
        Law(name="context_relevance",
            description="Suggestion relevance > 0.7 to surface"),
    ],
)
```

### Visual Projection: The Whisper

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🍷 The Sommelier whispers:                                                 │
│                                                                             │
│  "You've been exploring routing for 47 minutes. Based on your pattern,     │
│  you might enjoy:                                                           │
│                                                                             │
│    → kg time.scribe.export          Save this exploration as a session     │
│    → kg concept.synthesizer.weave   Crystallize your discoveries           │
│    → kg self.chronicler.chapter     Mark this as "The Routing Chapter"     │
│                                                                             │
│  [1] Export  [2] Synthesize  [3] Chapter  [Esc] Not now (4h cooldown)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration: The Daemon's Orchestra

```
                              kgentsd
                         (the conductor)
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
     FILESYSTEM           GIT/TESTS           AGENTESE
     EVENTS               EVENTS              EVENTS
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────────────────────────────────────────────┐
    │                  EVENT BUS (Priority Queue)           │
    └──────────────────────────────────────────────────────┘
                               │
     ┌─────────────────────────┼─────────────────────────┐
     │                         │                         │
     ▼                         ▼                         ▼
┌─────────┐              ┌─────────┐              ┌─────────┐
│ SCRIBE  │              │LIBRARIAN│              │  CARTO  │
│ records │              │ indexes │              │  maps   │
└────┬────┘              └────┬────┘              └────┬────┘
     │                        │                        │
     ▼                        ▼                        ▼
┌─────────┐              ┌─────────┐              ┌─────────┐
│CHRONICLR│              │SYNTHESZR│              │DRAMATURG│
│narrates │              │ weaves  │              │ arcs    │
└────┬────┘              └────┬────┘              └────┬────┘
     │                        │                        │
     └────────────────────────┼────────────────────────┘
                              │
                              ▼
                        ┌─────────┐
                        │SOMMELIR │
                        │whispers │
                        └─────────┘
```

**The Data Flow** (all passive, event-driven):
1. **kgentsd** watches filesystem, git, tests, AGENTESE events
2. **Scribe** captures terminal events → D-gent transcripts
3. **Librarian** indexes all artifacts → Semantic index
4. **Cartographer** updates maps → Live territory visualization
5. **Chronicler** narrates significant events → Story chapters
6. **Synthesizer** weaves fragments → Coherent documents
7. **Dramaturg** detects story structure → Dramatic arcs
8. **Sommelier** observes patterns → Contextual whispers

---

## Implementation Priority

| Crown Jewel | Priority | Why | kgentsd Integration |
|-------------|----------|-----|---------------------|
| **Scribe** | P0 | Foundation—captures data for all others | FileEvent, GitEvent, AgenteseEvent |
| **Librarian** | P0 | Indexes everything—enables search | DgentWrite, FileCreated |
| **Cartographer** | P1 | Visual territory map | FileEvent (structure + heat) |
| **Chronicler** | P1 | Uses Scribe data | SessionBreak, GitBranchSwitch |
| **Synthesizer** | P2 | Uses Librarian + Chronicler | TopicThreshold, PlanComplete |
| **Dramaturg** | P2 | Pattern recognition | AggregatedEvents (tension curve) |
| **Sommelier** | P3 | Requires all others | PatternDetected |

---

## The Joy Test

> *"Does this make work feel more meaningful, not just more tracked?"*

Each Crown Jewel should pass the joy test:

| Jewel | Transformation | Joy Factor |
|-------|----------------|------------|
| **Scribe** | Sessions become reproducible | "I can show someone exactly what I did" |
| **Librarian** | Chaos becomes order | "I can always find what I'm looking for" |
| **Cartographer** | Codebase becomes navigable | "I understand where everything lives" |
| **Chronicler** | Work becomes story | "My work has narrative meaning" |
| **Synthesizer** | Fragments become understanding | "Scattered ideas crystallize into insight" |
| **Dramaturg** | Tasks become narrative | "I'm living a story, not grinding tickets" |
| **Sommelier** | Confusion becomes guidance | "The right tool appears when I need it" |

---

## The Mirror Test (Final Check)

*Does this feel like Kent on his best day?*

- ✅ **Daring**: Passive, event-driven agents that work without being invoked
- ✅ **Bold**: A daemon orchestra that makes work feel like a story
- ✅ **Creative**: Narrative synthesis, dramatic arcs, whispered suggestions
- ✅ **Opinionated**: No timers. Events only. Whispers, never shouts.
- ✅ **Not gaudy**: Clean polynomial states, coherent operads, sheaf gluing

*"The persona is a garden, not a museum."* — These jewels cultivate, they don't catalog.

---

*"The oblique path often leads to the most interesting destinations."*
*"Set it and forget it. The daemon watches. The jewels respond."*

---

*Brainstormed: 2025-12-19 | Enhanced with kgentsd integration | Seven Oblique Crown Jewels*
