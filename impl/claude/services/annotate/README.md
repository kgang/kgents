# Annotation Service: Spec ↔ Implementation Mapping

> *"Every spec section should trace to implementation. Every gotcha should be captured."*

## Overview

The Annotation service implements Phase 2 of the Claude Code CLI Integration Strategy, providing bidirectional tracing between specifications and implementation code.

## Architecture

```
services/annotate/
├── __init__.py          # Public API exports
├── types.py             # Core types (SpecAnnotation, AnnotationKind, ImplGraph)
├── store.py             # Database persistence (AnnotationStore)
└── graph.py             # Graph building (spec ↔ impl mapping)

models/annotation.py     # SQLAlchemy model (SpecAnnotationRow)

protocols/cli/handlers/
└── annotate.py          # CLI command handler
```

## Core Types

### AnnotationKind

Five types of annotations:

1. **PRINCIPLE**: Links section to constitutional principle (tasteful, composable, etc.)
2. **IMPL_LINK**: Direct pointer from spec section to implementing code
3. **GOTCHA**: Trap to avoid (learned the hard way)
4. **TASTE**: Aesthetic judgment (why we chose X over Y)
5. **DECISION**: Design decision (links to `kg decide` fusion record)

### SpecAnnotation

```python
@dataclass
class SpecAnnotation:
    id: str                        # Unique annotation identifier
    spec_path: str                 # Path to spec file
    section: str                   # Section/heading in spec
    kind: AnnotationKind           # Type of annotation

    # Kind-specific fields
    principle: str | None          # For PRINCIPLE annotations
    impl_path: str | None          # For IMPL_LINK annotations
    decision_id: str | None        # For DECISION annotations

    note: str                      # Human-readable content
    created_by: str                # Author
    created_at: datetime           # Timestamp
    mark_id: str                   # Witness trace
    status: AnnotationStatus       # Lifecycle
```

### ImplGraph

Bidirectional graph of spec ↔ impl relationships:

```python
@dataclass
class ImplGraph:
    spec_path: str                           # The spec file
    edges: list[ImplEdge]                    # All spec → impl edges
    coverage: float                          # % of sections with impl links
    uncovered_sections: list[str]            # Sections without links
```

## CLI Usage

### Add Annotations

```bash
# Add principle annotation
kg annotate spec/protocols/witness.md \
  --principle composable \
  --section "Mark Structure" \
  --note "Single output per mark"

# Add implementation link
kg annotate spec/protocols/witness.md \
  --impl \
  --section "MarkStore" \
  --link "services/witness/store.py:MarkStore"

# Add gotcha
kg annotate spec/protocols/witness.md \
  --gotcha \
  --section "Event Emission" \
  --note "Bus publish is fire-and-forget"

# Add taste annotation
kg annotate spec/protocols/witness.md \
  --taste \
  --section "API Design" \
  --note "Chose async API for consistency with other services"

# Link to fusion decision
kg annotate spec/protocols/witness.md \
  --decision fusion-abc123 \
  --section "Storage Backend" \
  --note "Decision to use PostgreSQL"
```

### Query Annotations

```bash
# Show all annotations for a spec
kg annotate spec/protocols/witness.md --show

# Show annotations in verbose mode
kg annotate spec/protocols/witness.md --show --verbose

# Export as JSON
kg annotate spec/protocols/witness.md --export --json
```

### Build Implementation Graph

```bash
# Build graph with coverage metrics
kg annotate spec/protocols/witness.md --graph

# Export graph as JSON
kg annotate spec/protocols/witness.md --graph --json
```

## Database Schema

```sql
CREATE TABLE spec_annotations (
    id VARCHAR(64) PRIMARY KEY,
    spec_path VARCHAR(512) NOT NULL,
    section VARCHAR(256) NOT NULL,
    kind ENUM('principle', 'impl_link', 'gotcha', 'taste', 'decision') NOT NULL,

    -- Kind-specific fields
    principle VARCHAR(64),
    impl_path VARCHAR(512),
    decision_id VARCHAR(64),

    note TEXT NOT NULL,
    created_by VARCHAR(64) NOT NULL DEFAULT 'kent',
    mark_id VARCHAR(64) NOT NULL,
    status ENUM('active', 'superseded', 'archived') NOT NULL DEFAULT 'active',

    -- Additional metadata
    annotation_meta JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX idx_spec_annotations_spec_section ON spec_annotations(spec_path, section);
CREATE INDEX idx_spec_annotations_spec_kind ON spec_annotations(spec_path, kind);
CREATE INDEX idx_spec_annotations_kind_status ON spec_annotations(kind, status);
CREATE INDEX idx_spec_annotations_spec_status ON spec_annotations(spec_path, status);
CREATE INDEX idx_spec_annotations_metadata ON spec_annotations USING gin(annotation_meta);
```

## Witness Integration

Every annotation creates a witness mark:

```python
# Save annotation
ann = await store.save_annotation(
    spec_path="spec/protocols/witness.md",
    section="Mark Structure",
    kind=AnnotationKind.PRINCIPLE,
    principle="composable",
    note="Single output per mark",
    created_by="kent",
    witness=witness_persistence,  # Creates mark automatically
)

# Mark is linked via mark_id field
print(ann.mark_id)  # → "mark-abc123"
```

## Graph Building

```python
from pathlib import Path
from services.annotate.graph import build_impl_graph
from services.annotate.store import AnnotationStore

store = AnnotationStore()
graph = await build_impl_graph(
    spec_path="spec/protocols/witness.md",
    store=store,
    repo_root=Path.cwd(),
)

# Coverage metrics
print(f"Coverage: {graph.coverage:.1%}")
print(f"Edges: {len(graph.edges)}")
print(f"Uncovered: {graph.uncovered_sections}")

# Query edges
for edge in graph.edges:
    print(f"{edge.spec_section} → {edge.impl_path}")
    print(f"  Verified: {edge.verified}")
```

## Reverse Lookup

```python
from services.annotate.graph import find_specs_for_impl

# Find all specs that link to an implementation file
specs = await find_specs_for_impl(
    impl_path="services/witness/store.py",
    store=store,
)

for spec_path, sections in specs.items():
    print(f"{spec_path}:")
    for section in sections:
        print(f"  - {section}")
```

## Testing

```bash
# Run all annotation tests
cd impl/claude
uv run pytest protocols/cli/handlers/_tests/test_annotate.py -v

# Run tier1 tests only (fast)
uv run pytest protocols/cli/handlers/_tests/test_annotate.py -m tier1

# Run tier2 integration tests (requires Postgres)
uv run pytest protocols/cli/handlers/_tests/test_annotate.py -m tier2
```

## Teaching Notes

### Gotcha: SQLAlchemy Reserved Keywords

`metadata` is reserved in SQLAlchemy. We use `annotation_meta` instead:

```python
# WRONG
class SpecAnnotationRow(Base):
    metadata: Mapped[dict] = mapped_column(JSONBCompat, ...)

# RIGHT
class SpecAnnotationRow(Base):
    annotation_meta: Mapped[dict] = mapped_column(JSONBCompat, ...)
```

### Principle: Composable

Annotations are first-class values that compose:

```python
# Query annotations
result = await store.query_annotations(spec_path="spec/protocols/witness.md")

# Compose with graph building
graph = await build_impl_graph(spec_path, store)

# Compose queries
gotchas = await store.get_gotchas(spec_path)
principles = await store.get_principles(spec_path)
```

### Principle: Generative

The annotation system is self-describing:

- Each annotation type has clear semantics (PRINCIPLE, IMPL_LINK, GOTCHA, etc.)
- The database schema mirrors the type structure
- Tests verify the type-to-database mapping

## Future Work

### Inline YAML in Spec Files

Currently annotations are database-only. Future: Optional inline YAML in spec files for visibility:

```markdown
---
annotations:
  - section: "Mark Structure"
    principle: composable
    note: "Single output per mark"
    mark_id: "mark-abc123"
---

# Mark Structure

...
```

### AST-Based Impl Verification

Currently we verify file existence only. Future: Parse Python AST to verify class/function existence:

```python
# Current: File exists?
verify_impl_path("services/witness/store.py:MarkStore")  # → True

# Future: Class exists?
verify_impl_path("services/witness/store.py:MarkStore")  # → True (verified in AST)
verify_impl_path("services/witness/store.py:Missing")    # → False (not in AST)
```

## See Also

- [brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md](../../../../../../brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md) - Phase 2 strategy
- [spec/protocols/witness-supersession.md](../../../../../../spec/protocols/witness-supersession.md) - Witness protocol
- [docs/skills/metaphysical-fullstack.md](../../../../../../docs/skills/metaphysical-fullstack.md) - Service architecture

---

*Compiled: 2025-12-23 | Phase 2: Annotate*
