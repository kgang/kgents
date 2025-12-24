# Inbound Sovereignty Protocol

> *"Data enters. Data is witnessed. Data never leaves without explicit consent."*

**Why This Exists**: Traditional systems scan filesystems repeatedly—4000+ files every time, 30 seconds of waste, results evaporating. This protocol transforms batch analysis violence into witnessed accumulation. We don't reference external data; we possess sovereign copies with provenance. The specgraph becomes instant (10ms queries vs 30s scans) because it's a materialized view of witnessed events, not a runtime computation.

**The Taste**: A single, tasteful abstraction—"data enters once, is witnessed, never leaves without consent"—replaces the chaos of polling, scanning, caching, invalidation, and eventual consistency. The sovereign copy IS the cache, the witness mark IS the invalidation signal, the overlay IS the annotation layer. Three concepts, infinite use cases.

**Joy in Practice**:
```python
# Before: pray the file still exists, scan every time
edges = scan_filesystem()  # 30s, fingers crossed

# After: query your memory, instant
edges = await sovereign.get_edges("spec/k-block.md")  # 10ms, guaranteed

# Even better: your annotations persist
await sovereign.annotate(
    "spec/k-block.md",
    Annotation(line=42, note="This is the key insight!")
)
# Tomorrow, it's still there. Next week, still there. The system remembers.
```

No more waiting for scans. No more "did I lose that analysis?" No more external changes breaking your flow. Just query your memory—it remembers everything you witnessed. **This is joy-inducing infrastructure.**

Heritage (Curated Dependencies):
  - **spec/protocols/witness-primitives.md** - witness marks as existence proofs, the foundation for "no entity without witness" (Law 1)
  - **spec/protocols/k-block.md** - versioned content with edit trails, inspired our versioned sovereign copies (v1/, v2/, ...) and overlay pattern
  - **spec/principles/constitution.md** - Article IV: Disgust Veto, enforced via Law 3 (export requires consent)
  - **spec/agents/d-gent.md** - storage abstraction patterns (StorageProvider interface), influenced our integration with witness persistence
  - **Evolved from**: Context Sovereignty v3.1 (plans/_archive/2025-12-pre-week50/), which attempted "context boundaries" but lacked witness integration—we learned that boundaries without provenance are brittle
  - **Prior Art Influences**:
    - Git's object store → content-addressable storage with hashing
    - SQLite's WAL mode → write-ahead logging for crash safety
    - ZFS snapshots → immutable versioning
    - CRDT theory → conflict-free replicated data (future phase 4)

Status: IMPLEMENTED (services/sovereign/)
Confidence: 0.85
Filed: 2024-12-22

Evolution Strategy (Intentional Roadmap):
  - **Phase 1 (DONE)**: File-based sovereign store with witness integration
    - Deliverables: SovereignStore, ingest protocol, export with Law 3 compliance
    - Decision: fuse-b84b63c7 (chose filesystem over DB for visibility + git compatibility)
  - **Phase 2 (CURRENT)**: Graph materialization from witness marks
    - services/sovereign/analyzer.py - edge extraction and trust computation
    - services/sovereign/verification.py - law enforcement checks
  - **Phase 3 (PLANNED Q1 2025)**: Conflict resolution for multi-writer scenarios
    - When two ingests happen simultaneously, merge strategies
  - **Phase 4 (RESEARCH)**: Distributed sovereignty (sovereign copies across machines)
    - CRDT-based merge for multi-replica scenarios
    - Cross-machine witness synchronization

Related Specs:
  - spec/protocols/sovereign-data-guarantees.md - formal proofs of the four laws
  - services/sovereign/EXPORT_EXAMPLES.md - practical export patterns

---

## Ethical Foundations

**Privacy & Data Sovereignty**:
- **Consent-Based Export**: Data never leaves without explicit witness mark (Law 3)
- **Local-First**: Your sovereign copies stay in `.kgents/sovereign/` under your control
- **Audit Trail**: Every ingest, sync, and export is witnessed—full transparency
- **Right to Delete**: `SovereignStore.delete()` with reference checking prevents broken links
- **Right to Rename**: `SovereignStore.rename()` updates metadata and witnesses the change

**Data Minimization**: We only ingest what you explicitly request. No background scanning of your filesystem without permission.

**Transparency**: The witness trail IS the audit log. Query `witness.query(action="entity.export")` to see every export.

**Limitations**:
- File system storage: not encrypted by default (use OS encryption if needed)
- Git sync: assumes you trust the git repository source
- Export bundle: contains full content + metadata (review before sharing)

See: spec/principles/constitution.md (Article IV: Disgust Veto)

---

## The Problem (A Story)

Picture this: You're working on a large codebase. 4000+ files. You run an analysis—"find all the references to this spec file." 30 seconds later, you get results. Great!

Five minutes later, you want to check again. Another 30 seconds. Same files. Same results. But the system doesn't *know* they're the same—it scans everything again.

Now imagine: You analyzed a spec yesterday, found 47 references, made some notes. Today, you want to continue. But the system forgot. The analysis evaporated. You start from scratch.

Worse: A colleague deletes a file that 12 other specs reference. Your analysis breaks—it was pointing to external files, not to knowledge you possessed.

**This is the violence of hot analysis:**
```
Files exist → We scan them → We analyze them → Results evaporate
            ↑
     4000+ files, every time
     No memory of the scan
     External changes break us
```

Every batch scan:
- Assumes files might have changed (distrust)
- Recomputes what we already knew (waste)
- Produces ephemeral results (amnesia)
- Lets data "escape" without witnessing (leakage)

It's like having a brilliant analyst who forgets everything they learned each night. Groundhog Day for your data infrastructure.

---

## The Sovereign Copy

> *"We don't reference. We possess."*

When a document enters, we keep an **exact copy** under our control:

```
EXTERNAL                         SOVEREIGN MEMBRANE
────────                         ──────────────────

┌─────────────┐                  ┌─────────────────────────────┐
│ spec/foo.md │ ───INGEST───►   │ .kgents/sovereign/          │
│ (git repo)  │                  │   spec/foo.md               │
└─────────────┘                  │     ├── content (exact copy)│
      │                          │     ├── .meta.json          │
      │                          │     │    ├── ingest_mark    │
      │                          │     │    ├── edges[]        │
      │                          │     │    ├── our_annotations│
      │                          │     │    └── sync_history   │
      │                          │     └── .overlay/           │
      │                          │          └── (our changes)  │
      │                          └─────────────────────────────┘
      │                                       │
      └──── SYNC (receive) ───────────────────┘
                │
                ▼
         We compare, decide,
         maybe re-ingest
```

### Why Keep a Copy?

| Without Copy | With Sovereign Copy |
|--------------|---------------------|
| Reference to external file | We own the bytes |
| External deletion breaks us | We still have it |
| Can't annotate the source | Overlay with our marks |
| Edges point to moving target | Edges point to our copy |
| History depends on git | Our own version history |

### The Sovereign Copy Structure

```
.kgents/sovereign/
├── spec/
│   └── protocols/
│       └── k-block.md/                    # Directory per entity
│           ├── v1/                        # Version 1 (first ingest)
│           │   ├── content.md             # Exact copy at ingest
│           │   └── meta.json              # Ingest mark, edges
│           ├── v2/                        # Version 2 (after sync)
│           │   ├── content.md
│           │   └── meta.json
│           ├── current -> v2/             # Symlink to latest
│           └── overlay/                   # OUR modifications
│               ├── annotations.json       # Our marks on this doc
│               ├── corrections.md         # Our fixes/additions
│               └── derived/               # Generated content
│                   └── edges.json
└── impl/
    └── claude/
        └── services/
            └── witness/
                └── crystal.py/
                    ├── v1/
                    │   ├── content.py
                    │   └── meta.json
                    └── current -> v1/
```

---

## The Paradigm Shift

```
                    INBOUND SOVEREIGNTY

    ┌─────────────────────────────────────────────────┐
    │                  THE MEMBRANE                    │
    │                                                  │
    │   OUTSIDE          │          INSIDE            │
    │                    │                            │
    │   Files            │    Witnessed Entities      │
    │   URLs             │    Evidence Marks          │
    │   APIs         ────┼───►  Materialized Edges    │
    │   Humans           │    Accumulated Knowledge   │
    │                    │                            │
    │              INGEST WITNESS                     │
    │              (one-time, permanent)              │
    │                    │                            │
    │                    │◄─── SYNC (inbound only)    │
    │                    │                            │
    │              EXPORT ────► (explicit, witnessed) │
    │                    │                            │
    └─────────────────────────────────────────────────┘
```

### Core Principles

1. **INGEST = WITNESS**
   - Every document entering the system is a witnessed event
   - The witness mark IS the entity's existence proof
   - No document exists without a birth certificate

2. **EDGES ARE COMPUTED ONCE**
   - At ingest, we extract all references
   - Edges are stored as evidence, not recomputed
   - The graph is a materialized view of witnessed events

3. **SYNC IS RECEIVE-ONLY**
   - External changes come TO us
   - We decide whether to accept (new witness mark)
   - We never poll—we subscribe or are notified

4. **EXPORT IS EXPLICIT**
   - Nothing leaves without a command
   - Every export is witnessed (who, what, when, why)
   - Default: closed. Open by consent.

---

## The Ingest Protocol

### Phase 1: Entity Arrives

**Composable Type Signatures**:

```python
@dataclass
class IngestEvent:
    """
    A document crosses the membrane.

    Composition: IngestEvent >> ingest >> IngestedEntity
    Flow: External source → Witness boundary → Sovereign membrane
    """

    source: str              # Where it came from
    content_hash: str        # SHA256 of content
    content: bytes           # The actual data
    claimed_path: str        # Where it wants to live

    # Metadata
    source_timestamp: datetime | None  # When source says it changed
    source_author: str | None          # Who source says wrote it


# Composition operators
IngestOp = Callable[[IngestEvent], Awaitable[IngestedEntity]]
SyncOp = Callable[[ChangeNotification], Awaitable[SyncResult]]
ExportOp = Callable[[str, str, str, str], Awaitable[ExportReceipt]]

# Composable pipeline: watch >> ingest >> analyze >> materialize
sovereign_pipeline: Pipeline = (
    GitWatcher()
    >> IngestWitness()
    >> EdgeExtractor()
    >> GraphMaterializer()
)
```

### Phase 2: Witness the Arrival

```python
async def ingest(event: IngestEvent) -> IngestedEntity:
    """
    Ingest = Witness + Copy + Extract + Store

    This is THE moment of truth. After this, we own it.
    """

    # 1. Create the birth certificate
    mark = await witness.mark(
        action="entity.ingest",
        target=event.claimed_path,
        evidence={
            "source": event.source,
            "content_hash": event.content_hash,
            "source_timestamp": event.source_timestamp,
            "source_author": event.source_author,
        },
        reasoning="Document crossed the membrane",
    )

    # 2. STORE THE SOVEREIGN COPY (exact bytes, versioned)
    version = await sovereign.store_version(
        path=event.claimed_path,
        content=event.content,
        ingest_mark=mark.id,
        metadata={
            "source": event.source,
            "content_hash": event.content_hash,
            "ingested_at": mark.timestamp,
        },
    )
    # Now we have: .kgents/sovereign/{path}/v{N}/content.{ext}

    # 3. Extract edges AT INGEST TIME (not later!)
    edges = extract_edges(event.content, event.claimed_path)

    # 4. Store edges as evidence (in overlay)
    edge_marks = []
    for edge in edges:
        edge_mark = await witness.mark(
            action="edge.discovered",
            target=event.claimed_path,
            evidence={
                "edge_type": edge.type,
                "edge_target": edge.target,
                "line": edge.line,
                "context": edge.context,
            },
            parent=mark.id,  # Link to ingest mark
        )
        edge_marks.append(edge_mark)

    # 5. Store derived data in overlay
    await sovereign.store_overlay(
        path=event.claimed_path,
        overlay_type="edges",
        data={"edges": [e.to_dict() for e in edge_marks]},
    )
    # Now we have: .kgents/sovereign/{path}/overlay/derived/edges.json

    return IngestedEntity(
        path=event.claimed_path,
        version=version,
        ingest_mark=mark,
        edge_marks=edge_marks,
    )
```

### Phase 3: The Entity Exists

After ingest, we have:
- **Birth mark**: Witness record of arrival
- **Edge marks**: All references extracted and witnessed
- **Content**: Stored locally, keyed by our path
- **Trust**: Accumulated from evidence

**We never scan again.** The entity IS its witness trail.

---

## The Sync Protocol

Sync is NOT "check if changed." Sync is "receive notification of change."

### Inbound Sync (Receive Changes)

```python
async def sync_inbound(notification: ChangeNotification) -> SyncResult:
    """
    External source notifies us of a change.
    We decide whether to accept.
    """

    # 1. Witness the notification (even if we reject)
    mark = await witness.mark(
        action="sync.notification_received",
        target=notification.path,
        evidence={
            "source": notification.source,
            "old_hash": notification.old_hash,
            "new_hash": notification.new_hash,
            "change_type": notification.change_type,
        },
    )

    # 2. Decide: accept or reject?
    if should_accept(notification):
        # Fetch new content
        new_content = await fetch_from_source(notification)

        # Re-ingest (creates new witness trail)
        return await ingest(IngestEvent(
            source=notification.source,
            content_hash=notification.new_hash,
            content=new_content,
            claimed_path=notification.path,
        ))
    else:
        # Witness the rejection
        await witness.mark(
            action="sync.rejected",
            target=notification.path,
            evidence={"reason": "..."},
            parent=mark.id,
        )
        return SyncResult.REJECTED
```

### Git as Sync Source

```python
class GitSyncProvider:
    """
    Git commits become ingest events.
    We don't poll—we watch.
    """

    async def watch(self, repo_path: Path):
        """Watch for git changes, emit ingest events."""

        # Use filesystem watcher or git hooks
        async for change in self.watch_changes(repo_path):
            if change.type == "modified":
                content = (repo_path / change.path).read_bytes()
                await ingest(IngestEvent(
                    source=f"git:{repo_path}",
                    content_hash=sha256(content),
                    content=content,
                    claimed_path=change.path,
                ))
```

---

## The Export Protocol

**Nothing leaves without consent.**

```python
async def export(
    path: str,
    destination: str,
    reason: str,
    authorized_by: str,
) -> ExportReceipt:
    """
    Explicitly export data outside the membrane.

    This is a significant event—always witnessed.
    """

    # 1. Get the entity
    entity = await storage.get(path)
    if not entity:
        raise EntityNotFound(path)

    # 2. Witness the export decision
    mark = await witness.mark(
        action="entity.export",
        target=path,
        evidence={
            "destination": destination,
            "reason": reason,
            "authorized_by": authorized_by,
            "content_hash": entity.content_hash,
        },
        reasoning=f"Explicit export: {reason}",
    )

    # 3. Perform the export
    await send_to_destination(entity.content, destination)

    # 4. Return receipt (proof of export)
    return ExportReceipt(
        mark_id=mark.id,
        path=path,
        destination=destination,
        timestamp=mark.timestamp,
    )
```

### Auto-Export (With Consent)

```python
@dataclass
class ExportPolicy:
    """Pre-authorized export rules."""

    pattern: str          # e.g., "spec/**/*.md"
    destination: str      # e.g., "github:kgents/kgents"
    trigger: str          # e.g., "on_commit", "daily"
    authorized_by: str    # Who approved this policy
    authorized_at: datetime

    # Still witnessed!
    witness_each: bool = True  # Mark each export
```

---

## The Graph IS The Witness Trail

No more batch scanning. The specgraph is a **materialized view** of witnessed events:

```python
class WitnessedGraph:
    """
    The graph is not computed—it's accumulated.
    Every edge is a witness mark.
    """

    async def get_edges(self, path: str) -> list[Edge]:
        """Get edges from witness trail, not file scan."""

        # Query witness marks of type "edge.discovered"
        marks = await witness.query(
            action="edge.discovered",
            target=path,
        )

        return [
            Edge(
                source=path,
                target=m.evidence["edge_target"],
                type=m.evidence["edge_type"],
                discovered_at=m.timestamp,
                mark_id=m.id,
            )
            for m in marks
        ]

    async def get_all_edges(self) -> list[Edge]:
        """
        Get ALL edges.

        This is fast because it's a DB query,
        not a filesystem scan.
        """
        marks = await witness.query(action="edge.discovered")
        return [self._mark_to_edge(m) for m in marks]

    async def get_entity(self, path: str) -> WitnessedEntity:
        """
        Get entity with full provenance.

        Returns: content + complete witness trail
        """
        # Get ingest mark
        ingest_mark = await witness.query(
            action="entity.ingest",
            target=path,
            limit=1,
            order="desc",  # Most recent
        )

        # Get all edge marks
        edge_marks = await witness.query(
            action="edge.discovered",
            target=path,
        )

        # Get content
        content = await storage.get(path)

        return WitnessedEntity(
            path=path,
            content=content,
            ingest_mark=ingest_mark,
            edge_marks=edge_marks,
            trust=compute_trust(ingest_mark, edge_marks),
        )
```

---

## Migration: From Hot Analysis to Witnessed Entities

### One-Time Bootstrap

```python
async def bootstrap_from_filesystem(root: Path):
    """
    Convert existing files to witnessed entities.

    Run ONCE. After this, we never scan again.
    """

    for path in root.rglob("*"):
        if path.is_file():
            content = path.read_bytes()

            await ingest(IngestEvent(
                source=f"bootstrap:{root}",
                content_hash=sha256(content),
                content=content,
                claimed_path=str(path.relative_to(root)),
            ))

    # After bootstrap, install watchers
    await install_file_watchers(root)
```

### After Bootstrap

```python
# OLD (never again)
edges = scan_filesystem_for_edges()  # 4000 files, 30 seconds

# NEW (instant)
edges = await witnessed_graph.get_all_edges()  # DB query, 10ms
```

---

## Integration Points

### K-Block

```python
# When K-Block commits, it's a modification event
async def kblock_commit(kblock: KBlock):
    # K-Block commit = new entity version
    await ingest(IngestEvent(
        source="kblock",
        content_hash=kblock.content_hash,
        content=kblock.content.encode(),
        claimed_path=kblock.path,
    ))
```

### AGENTESE

```python
@node("concept.specgraph")
class SpecGraphNode:
    """
    SpecGraph now queries witness trail, not filesystem.
    """

    @aspect
    async def query(self, path: str) -> dict:
        entity = await witnessed_graph.get_entity(path)
        return {
            "path": entity.path,
            "edges": [e.to_dict() for e in entity.edge_marks],
            "trust": entity.trust,
            "ingest_mark": entity.ingest_mark.id,
        }
```

### Derivation Framework

```python
# Evidence from witnessed entities
evidence = Evidence(
    source="ingest_mark",
    mark_id=entity.ingest_mark.id,
    confidence=0.9,  # We witnessed it ourselves
)
```

---

## The Sovereign Store API

```python
class SovereignStore:
    """
    Manages sovereign copies of ingested entities.

    Structure:
      .kgents/sovereign/{path}/
        ├── v{N}/content.{ext}    # Versioned copies
        ├── current -> v{N}/      # Symlink to latest
        └── overlay/              # Our modifications
    """

    def __init__(self, root: Path = Path(".kgents/sovereign")):
        self.root = root

    async def store_version(
        self,
        path: str,
        content: bytes,
        ingest_mark: str,
        metadata: dict,
    ) -> int:
        """
        Store a new version of the entity.
        Returns the version number.
        """
        entity_dir = self.root / path
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Find next version number
        existing = [d for d in entity_dir.iterdir() if d.name.startswith("v")]
        version = len(existing) + 1

        # Create version directory
        version_dir = entity_dir / f"v{version}"
        version_dir.mkdir()

        # Store content with original extension
        ext = Path(path).suffix or ".bin"
        content_file = version_dir / f"content{ext}"
        content_file.write_bytes(content)

        # Store metadata
        meta_file = version_dir / "meta.json"
        meta_file.write_text(json.dumps({
            **metadata,
            "ingest_mark": ingest_mark,
            "version": version,
        }, indent=2))

        # Update current symlink
        current_link = entity_dir / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(f"v{version}")

        return version

    async def get_current(self, path: str) -> SovereignEntity | None:
        """Get the current version of an entity."""
        entity_dir = self.root / path
        current = entity_dir / "current"

        if not current.exists():
            return None

        version_dir = current.resolve()
        content_files = list(version_dir.glob("content.*"))
        if not content_files:
            return None

        return SovereignEntity(
            path=path,
            content=content_files[0].read_bytes(),
            metadata=json.loads((version_dir / "meta.json").read_text()),
            overlay=await self.get_overlay(path),
        )

    async def store_overlay(
        self,
        path: str,
        overlay_type: str,
        data: dict,
    ) -> None:
        """
        Store data in the overlay (our modifications).

        overlay_type: "annotations", "corrections", "edges", etc.
        """
        overlay_dir = self.root / path / "overlay"
        if overlay_type == "edges":
            overlay_dir = overlay_dir / "derived"
        overlay_dir.mkdir(parents=True, exist_ok=True)

        overlay_file = overlay_dir / f"{overlay_type}.json"
        overlay_file.write_text(json.dumps(data, indent=2))

    async def get_overlay(self, path: str) -> dict:
        """Get all overlay data for an entity."""
        overlay_dir = self.root / path / "overlay"
        if not overlay_dir.exists():
            return {}

        result = {}
        for f in overlay_dir.rglob("*.json"):
            key = f.stem
            result[key] = json.loads(f.read_text())

        return result

    async def annotate(
        self,
        path: str,
        annotation: Annotation,
    ) -> None:
        """
        Add an annotation to an entity.

        Annotations are stored in overlay, linked to witness marks.
        """
        annotations = (await self.get_overlay(path)).get("annotations", [])
        annotations.append(annotation.to_dict())

        await self.store_overlay(path, "annotations", annotations)

    async def diff_with_source(
        self,
        path: str,
        source_content: bytes,
    ) -> Diff:
        """
        Compare our sovereign copy with external source.

        Used during sync to see what changed.
        """
        current = await self.get_current(path)
        if not current:
            return Diff(type="new", source_content=source_content)

        if current.content == source_content:
            return Diff(type="unchanged")

        return Diff(
            type="modified",
            our_content=current.content,
            source_content=source_content,
            our_hash=sha256(current.content),
            source_hash=sha256(source_content),
        )

    async def list_all(self) -> list[str]:
        """List all sovereign entities."""
        paths = []
        for entity_dir in self.root.rglob("current"):
            rel_path = entity_dir.parent.relative_to(self.root)
            paths.append(str(rel_path))
        return paths
```

### Annotation Flow

```python
# When we discover something about a document
await sovereign.annotate(
    path="spec/protocols/k-block.md",
    annotation=Annotation(
        type="insight",
        line=42,
        content="This law is also enforced by the Cosmos",
        mark_id=witness_mark.id,  # Link to witness
    ),
)

# When we correct an error in the source
await sovereign.annotate(
    path="spec/protocols/k-block.md",
    annotation=Annotation(
        type="correction",
        line=100,
        original="monad law 3",
        corrected="monad law 2",
        reasoning="The code shows this is actually law 2",
        mark_id=witness_mark.id,
    ),
)
```

---

## The Laws

### Law 0: No Entity Without Copy
```
∀ entity ∈ System: ∃ copy ∈ Sovereign where copy.path = entity.path
```
We don't reference—we possess. Every entity has a sovereign copy.

### Law 1: No Entity Without Witness
```
∀ entity ∈ System: ∃ mark ∈ Witness where mark.target = entity
```

### Law 2: No Edge Without Witness
```
∀ edge ∈ Graph: ∃ mark ∈ Witness where mark.action = "edge.discovered"
```

### Law 3: No Export Without Witness
```
∀ export ∈ Exports: ∃ mark ∈ Witness where mark.action = "entity.export"
```

### Law 4: Sync is Ingest
```
sync(entity) = ingest(entity') where entity' is the new version
```

---

## Benefits

| Before | After |
|--------|-------|
| Scan 4000 files | Query witness DB |
| 30 second batch job | 10ms query |
| Results evaporate | Results accumulated |
| No provenance | Full audit trail |
| External changes break us | We control our membrane |
| Data can leak | Export is explicit |
| Reference external files | Own sovereign copies |
| Can't annotate source | Overlay with our marks |
| External deletion breaks us | We still have our copy |
| History depends on git | Our own version history |

---

## Philosophy

> *"The file is a lie. There is only the witnessed entity."*
> *"We don't reference. We possess."*

We don't have files. We have **sovereign copies with provenance**.
We don't scan. We **query our memory**.
We don't sync. We **receive, compare, and decide**.
We don't leak. We **export with consent**.
We don't reference. We **possess and annotate**.

The membrane is not a wall—it's a witness station.
Everything that crosses is marked.
Everything that enters is copied.
Everything inside is ours.

### Heterarchy & Flux

**No Fixed Hierarchy**: Entities aren't organized in a tree—they exist in a graph of witnessed relationships. An entity can be referenced by many, reference many, exist in multiple "categories" simultaneously.

**Dynamic Trust**: Trust scores flow from witness marks, not static declarations. As you annotate, correct, and derive, trust accumulates. An entity's trust is a function of its witness trail, not its position in a hierarchy.

**Emergence**: The graph materializes from local witness events. No global coordinator dictates structure—it emerges from bottom-up witnessing. Each ingest is a local event; the graph is the global coherence (sheaf property).

**Flux-Compatible**: Sovereign entities can be projected through Flux agents for streaming analysis. The discrete witness events become continuous data flows when needed:

```python
# Discrete: witness marks accumulate
await sovereign.ingest(event)  # Point-in-time

# Continuous: stream witness events through Flux
sovereign_flux = Flux(
    source=sovereign_store.watch_ingests(),
    transform=edge_extractor,
    sink=graph_materializer,
)
```

The sovereign store is a fixed point in the data flow—a lens that both accumulates (ingest) and projects (query).

### Generative Compression

This spec compresses a complex pattern into executable laws:

**The Pattern**: Every data system faces the same tension—how to remember without becoming ossified, how to sync without becoming enslaved to external sources, how to share without leaking.

**The Compression**: Four laws capture it all:
1. No entity without copy (possession)
2. No entity without witness (provenance)
3. No edge without witness (materialization)
4. No export without witness (consent)

From these four laws, the entire system unfolds. The `SovereignStore` API, the ingest protocol, the sync strategy, the export guarantees—all derivable from the laws.

**Teaching Moment**: Notice how the spec gives you the laws first (compression), then expands them into protocols (decompression). You could rebuild the implementation from the laws alone. That's generative specification—the laws generate the system.

### The Three Layers of an Entity

```
┌─────────────────────────────────────────┐
│           OVERLAY (ours)                │
│  annotations, corrections, insights     │
│  edges, derived data, marks             │
├─────────────────────────────────────────┤
│         SOVEREIGN COPY                  │
│  exact bytes from source                │
│  versioned, immutable per version       │
├─────────────────────────────────────────┤
│           WITNESS TRAIL                 │
│  ingest mark, edge marks                │
│  sync marks, export marks               │
└─────────────────────────────────────────┘
```

The copy is the foundation.
The witness trail is the history.
The overlay is our contribution.

---

*Filed: 2024-12-22*
*Status: PROPOSED*
*Confidence: 0.75 — needs implementation to validate*
*Decision: fuse-b84b63c7*
