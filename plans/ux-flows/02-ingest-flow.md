# UX Flow: Document Ingest & Annotation

> *"Every document is a compressed graph waiting to be revealed."*

**Status**: Active Plan
**Date**: 2026-01-17
**Specs**: k-block.md, genesis-clean-slate.md
**Principles**: Generative, Composable, Curated

---

## The Problem We're Solving

Documents are flat. They hide their structure. Reading a spec, you can't see:
- Which statements are axioms vs. derived claims
- What depends on what
- Where the gotchas are
- How this connects to implementation

**Ingest transforms documents into navigable K-Block graphs.**

---

## The Ingest Philosophy

| Traditional | kgents Ingest |
|-------------|---------------|
| Upload → Store | Upload → Propose structure → User confirms → Witness |
| Flat file | K-Block graph with derivation edges |
| Read-only | Annotatable, editable, extendable |
| Orphaned | Linked to Constitutional Graph |
| Anonymous | Every annotation witnessed |

---

## The Flow

### Phase 1: Upload (0-10 seconds)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ INGEST                                                                          │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                             │ │
│ │                                                                             │ │
│ │           Drop any document here                                            │ │
│ │           .md  .txt  .pdf  .py  .ts  .yaml                                  │ │
│ │                                                                             │ │
│ │           or paste text directly                                            │ │
│ │                                                                             │ │
│ │                                                                             │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ Recent ingests:                                                                 │
│ ├── spec/protocols/witness.md (14 K-Blocks)                                     │
│ ├── docs/skills/polynomial-agent.md (8 K-Blocks)                                │
│ └── impl/claude/services/brain/core.py (6 K-Blocks)                             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Supported formats**:
- Markdown (`.md`) — Primary format
- Plain text (`.txt`) — Minimal structure
- PDF (`.pdf`) — Extracted text
- Python (`.py`) — Docstrings, classes, functions
- TypeScript (`.ts`) — JSDoc, interfaces, types
- YAML (`.yaml`) — Hierarchical data

### Phase 2: Analysis (10-30 seconds)

The system analyzes the document and proposes K-Block decomposition:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ ANALYZING: spec/protocols/witness.md                                            │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 42%                     │
│                                                                                 │
│ Finding:                                                                        │
│ ├── [✓] Heading structure                                                       │
│ ├── [✓] Axiom candidates (claims with no derivation)                            │
│ ├── [▸] Derivation links (references between sections)                          │
│ ├── [ ] Implementation links (code references)                                  │
│ └── [ ] Gotcha candidates (warnings, anti-patterns)                             │
│                                                                                 │
│ Proposed K-Blocks: 14                                                           │
│ Proposed Edges: 23                                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: K-Block Proposal Review (30 seconds - 5 minutes)

The system presents its proposed decomposition:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ PROPOSED K-BLOCKS: spec/protocols/witness.md                                    │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ ┌─ AXIOM (3 proposed) ──────────────────────────────────────────────────────┐   │
│ │                                                                           │   │
│ │ ⚡ witness:axiom:mark                                        [✓ Accept]   │   │
│ │    "Every action leaves a mark"                              [✗ Reject]   │   │
│ │    Galois Loss: L = 0.02                                     [✎ Edit]    │   │
│ │                                                                           │   │
│ │ ⚡ witness:axiom:witness                                      [✓ Accept]   │   │
│ │    "The proof IS the decision"                               [✗ Reject]   │   │
│ │    Galois Loss: L = 0.03                                     [✎ Edit]    │   │
│ │                                                                           │   │
│ │ ⚡ witness:axiom:crystallize                                  [✓ Accept]   │   │
│ │    "Marks coalesce into crystals"                            [✗ Reject]   │   │
│ │    Galois Loss: L = 0.05                                     [✎ Edit]    │   │
│ │                                                                           │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ ┌─ PRINCIPLE (4 proposed) ──────────────────────────────────────────────────┐   │
│ │                                                                           │   │
│ │ ◉ witness:principle:trace-completeness                       [✓ Accept]   │   │
│ │    "No significant moment evaporates"                        [✗ Reject]   │   │
│ │    Derives from: [witness:axiom:mark]                        [✎ Edit]    │   │
│ │                                                                           │   │
│ │ ◉ witness:principle:query-freedom                            [✓ Accept]   │   │
│ │    "Any coherent question can be asked"                      [✗ Reject]   │   │
│ │    Derives from: [witness:axiom:witness]                     [✎ Edit]    │   │
│ │    ...                                                                    │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ ┌─ IMPLEMENTATION (5 proposed) ─────────────────────────────────────────────┐   │
│ │ ...                                                                       │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ ┌─ GOTCHA (2 proposed) ─────────────────────────────────────────────────────┐   │
│ │                                                                           │   │
│ │ ⚠ witness:gotcha:no-orphans                                  [✓ Accept]   │   │
│ │    "Marks without reasoning are noise"                       [✗ Reject]   │   │
│ │    From line 234                                             [✎ Edit]    │   │
│ │    ...                                                                    │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│ [Accept All (14)]  [Accept Selected (12)]  [Cancel]                             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**K-Block Types Detected**:

| Type | Icon | Galois Loss Range | Description |
|------|------|-------------------|-------------|
| AXIOM | ⚡ | L < 0.10 | Irreducible claims, fixed points |
| PRINCIPLE | ◉ | L < 0.38 | Derived guidelines |
| GOTCHA | ⚠ | varies | Warnings, anti-patterns |
| IMPLEMENTATION | 📦 | L < 0.45 | Code links |
| DERIVATION | → | n/a | Edges between K-Blocks |

### Phase 4: Derivation Linking (2-5 minutes)

After accepting K-Blocks, user reviews proposed derivation edges:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ DERIVATION GRAPH: spec/protocols/witness.md                                     │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│                        ┌──────────────────────┐                                 │
│                        │ witness:axiom:mark   │                                 │
│                        │ "Every action leaves │                                 │
│                        │  a mark"             │                                 │
│                        └──────────┬───────────┘                                 │
│                                   │                                             │
│                    ┌──────────────┴──────────────┐                              │
│                    │                             │                              │
│                    ▼                             ▼                              │
│     ┌────────────────────────┐    ┌────────────────────────┐                    │
│     │ witness:principle:     │    │ witness:principle:     │                    │
│     │ trace-completeness     │    │ query-freedom          │                    │
│     └────────────┬───────────┘    └────────────┬───────────┘                    │
│                  │                             │                                │
│                  ▼                             ▼                                │
│     ┌────────────────────────┐    ┌────────────────────────┐                    │
│     │ witness:impl:          │    │ witness:impl:          │                    │
│     │ mark_store.py          │    │ query_engine.py        │                    │
│     └────────────────────────┘    └────────────────────────┘                    │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ PROPOSED EDGES:                                                                 │
│ ┌───────────────────────────────────────────────────────────────────────────┐   │
│ │ witness:axiom:mark → witness:principle:trace-completeness    [✓ Accept]   │   │
│ │ witness:axiom:mark → witness:principle:query-freedom         [✓ Accept]   │   │
│ │ witness:principle:trace-completeness → witness:impl:mark_store [✓ Accept] │   │
│ │ witness:axiom:mark → genesis:L1:compose                      [+ Add]      │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ Link to Constitutional Graph:                                                   │
│ [+ Link to L0 Axiom]  [+ Link to L1 Primitive]  [+ Link to L2 Principle]        │
│                                                                                 │
│ [Confirm Graph]                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Constitutional Linking**:
The key innovation: link document K-Blocks to the Constitutional Graph.

- `witness:axiom:mark` derives from `genesis:L1:compose` (marks are composed traces)
- `witness:principle:trace-completeness` embodies `genesis:L2:generative`

### Phase 5: Annotation Mode (Ongoing)

After initial ingest, the document is now annotatable:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ self.witness │ EDIT                                           K-Block: 14/14   │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ # Witness Protocol                                                              │
│                                                                                 │
│ > ⚡"Every action leaves a mark. Every mark is witnessed."                       │
│                                                                                 │
│ ## Part I: The Mark                                                             │
│                                                                                 │
│ A Mark is the atomic unit of witnessed action:                                  │
│                                                                                 │
│ ```python                                                                       │
│ @dataclass(frozen=True)                                                         │
│ class Mark:                           📦 witness:impl:mark_dataclass            │
│     id: MarkId                                                                  │
│     action: str                                                                 │
│     reasoning: str | None                                                       │
│     timestamp: datetime                                                         │
│     tags: frozenset[str]                                                        │
│ ```                                                                             │
│                                                                                 │
│ ⚠ **Gotcha**: Marks without reasoning are noise, not signal.                    │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│ ANNOTATION PALETTE:                                                             │
│ [⚡ Axiom]  [◉ Principle]  [⚠ Gotcha]  [📦 Impl]  [→ Link]  [🔗 Const.]          │
│                                                                                 │
│ Select text → Choose annotation → Confirm                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Annotation Types**:

| Type | Shortcut | Creates |
|------|----------|---------|
| ⚡ Axiom | `Cmd+1` | New K-Block (type=axiom) |
| ◉ Principle | `Cmd+2` | New K-Block (type=principle) |
| ⚠ Gotcha | `Cmd+3` | New K-Block (type=gotcha) |
| 📦 Impl | `Cmd+4` | Link to implementation file |
| → Link | `Cmd+5` | Derivation edge to another K-Block |
| 🔗 Const. | `Cmd+6` | Link to Constitutional Graph |

---

## Implementation Notes

### Ingest Pipeline

```python
# services/ingest/pipeline.py

async def ingest_document(path: str, content: str) -> IngestResult:
    """Transform document into K-Block graph."""

    # 1. Parse structure
    structure = await parse_structure(content)

    # 2. Detect axiom candidates (Galois loss < 0.10)
    axioms = await detect_axioms(structure)

    # 3. Detect derivations (section references, "derives from" patterns)
    derivations = await detect_derivations(structure, axioms)

    # 4. Detect gotchas (warnings, anti-patterns, "DO NOT" patterns)
    gotchas = await detect_gotchas(structure)

    # 5. Detect implementation links (code blocks, file references)
    impl_links = await detect_implementations(structure)

    # 6. Propose K-Block graph
    proposed = KBlockGraph(
        nodes=axioms + derivations + gotchas + impl_links,
        edges=infer_edges(axioms, derivations, impl_links),
    )

    return IngestResult(
        source_path=path,
        proposed_graph=proposed,
        confidence=compute_confidence(proposed),
    )
```

### Galois Loss for Axiom Detection

```python
async def detect_axioms(structure: ParsedStructure) -> list[KBlockProposal]:
    """Find statements that are fixed points (axioms)."""
    candidates = []

    for block in structure.blocks:
        # Compute Galois loss
        loss = await galois_service.compute_loss(block.content)

        if loss < 0.10:  # CATEGORICAL tier
            candidates.append(KBlockProposal(
                type="axiom",
                content=block.content,
                galois_loss=loss,
                confidence=1 - loss,
                source_line=block.line,
            ))

    return candidates
```

### Frontend Components

```tsx
// components/ingest/IngestPage.tsx
export function IngestPage() {
  const [phase, setPhase] = useState<'upload' | 'analyzing' | 'review' | 'annotate'>('upload');
  const [proposed, setProposed] = useState<KBlockGraph | null>(null);

  return (
    <div className="ingest-page">
      {phase === 'upload' && <UploadZone onUpload={handleUpload} />}
      {phase === 'analyzing' && <AnalysisProgress />}
      {phase === 'review' && (
        <ProposalReview
          graph={proposed}
          onAccept={handleAccept}
          onModify={handleModify}
        />
      )}
      {phase === 'annotate' && <AnnotationEditor graph={proposed} />}
    </div>
  );
}
```

---

## Witnessing

Every ingest action is witnessed:

| Action | Mark Tag |
|--------|----------|
| Document upload | `ingest.upload` |
| Accept K-Block | `ingest.accept` |
| Reject K-Block | `ingest.reject` |
| Add derivation | `ingest.link` |
| Link to Constitution | `ingest.constitutional` |
| Manual annotation | `ingest.annotate` |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Axiom detection precision | > 80% |
| Derivation inference precision | > 70% |
| Time to first K-Block accepted | < 30 seconds |
| Time to complete ingest | < 10 minutes |

---

*"Every document is a compressed graph waiting to be revealed."*
