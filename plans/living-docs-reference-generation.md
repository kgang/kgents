# Living Docs Reference Generation Plan

> *"Docs are not description—they are projection. Now we project for the public."*

**Goal**: Use the Living Docs infrastructure to generate comprehensive, public-ready reference documentation for kgents.

**Observer**: Human (spacious) — maximum detail, all teaching moments, all examples
**Output**: Dynamically generated markdown suitable for public presentation

---

## Audit Results (2025-12-21)

| Category | Files | Symbols | RICH | Gotchas |
|----------|-------|---------|------|---------|
| Crown Jewels | 2,477 | 9,317 | 1,791 | 2 |
| Categorical Foundation | 108 | 1,925 | 0 | 0 |
| AGENTESE Protocol | 133 | 2,581 | 0 | 0 |
| Verification | 45 | 770 | 219 | 0 |
| **Total** | **2,763** | **14,593** | **2,010** | **2** |

**RICH Coverage**: 13.8%

### Updated Results (2025-12-21 Session)

After Phase 0 implementation:
- **Symbols**: 3,065 (documented with summaries)
- **Teaching Moments**: 23 (8 critical, 15 info)
- **Test exclusion**: Working (`_tests/`, `conftest.py` excluded)
- **RICH tier**: Now includes `agents/`, `protocols/`

---

## Phase 0: Quick Wins ✅ COMPLETE

### 0.1 Fix Tier Determination

```python
# extractor.py - expand RICH tier
def _determine_tier(self, symbol: str, module: str) -> Tier:
    if symbol.startswith("_") and not symbol.startswith("__"):
        return Tier.MINIMAL

    # Expand RICH to include all core paths
    rich_patterns = ["services/", "services.", "agents/", "agents.", "protocols/", "protocols."]
    if any(p in module for p in rich_patterns):
        return Tier.RICH

    return Tier.STANDARD
```

### 0.2 Add File Exclusion

```python
# extractor.py - skip non-source files
EXCLUDE_PATTERNS = [
    "node_modules",
    "__pycache__",
    ".pyc",
    "dist/",
    "build/",
    "_tests/",
]

def should_extract(self, path: Path) -> bool:
    return not any(p in str(path) for p in self.EXCLUDE_PATTERNS)
```

### 0.3 Teaching Moment Seeding

Add `Teaching:` sections to key files:
- `agents/poly/agent.py` — PolyAgent gotchas
- `protocols/agentese/logos.py` — Logos invocation gotchas
- `services/brain/persistence.py` — Crystal handling gotchas
- `services/witness/playbook.py` — Grant/Scope requirement gotchas

---

## Phase 1: Inventory & Coverage Audit

**Goal**: Map all documentable surfaces in the codebase

### 1.1 Crown Jewels (Priority 1)
These are the showcase features—document completely:

| Jewel | Location | Status |
|-------|----------|--------|
| Brain | `services/brain/` | 100% |
| Gardener | `services/gardener/` | 100% |
| Gestalt | `services/gestalt/` | 100% |
| Witness | `services/witness/` | 98% |
| Conductor | `services/conductor/` | 92% |
| ASHC | `protocols/ashc/` | 95% |
| Living Docs | `services/living_docs/` | NEW |
| Town | `services/town/` | 70% |
| Park | `services/park/` | 60% |
| Forge | `services/forge/` | 85% |

### 1.2 Categorical Foundation (Priority 2)
The mathematical substrate:

| Component | Location | Purpose |
|-----------|----------|---------|
| PolyAgent | `agents/poly/` | Polynomial functor state machines |
| Operad | `agents/operad/` | Composition grammar |
| Sheaf | `agents/sheaf/` | Global coherence from locals |
| Flux | `agents/flux/` | Event-driven streaming |
| D-gent | `agents/d/` | Persistence layer |

### 1.3 AGENTESE Protocol (Priority 3)
The universal API:

| Component | Location | Purpose |
|-----------|----------|---------|
| Logos | `protocols/agentese/logos.py` | Path invocation |
| Nodes | `protocols/agentese/node.py` | BaseLogosNode |
| Affordances | `protocols/agentese/affordances.py` | @aspect decorator |
| Gateway | `protocols/agentese/gateway.py` | HTTP/WS exposure |
| Contexts | `protocols/agentese/contexts/` | world.*, self.*, concept.*, time.*, void.* |

### 1.4 Specs (Priority 4)
Conceptual documentation:

| Spec | Location | Purpose |
|------|----------|---------|
| Principles | `spec/principles.md` | The 7 immutable principles |
| AGENTESE | `spec/protocols/agentese.md` | Verb-first ontology |
| Living Docs | `spec/protocols/living-docs.md` | This system's spec |
| Projection | `spec/protocols/projection.md` | Multi-surface rendering |

---

## Phase 2: Enhance Living Docs Infrastructure ✅ COMPLETE

### 2.1 Add Module-Level Extraction ✅ DONE
Module docstrings are now extracted and projected.

### 2.2 Add Cross-Reference Linking ✅ DONE
Added `agentese_path` and `related_symbols` fields to DocNode.
- 104 AGENTESE paths now extracted from docstrings
- Pattern: `AGENTESE: <path>` in docstrings

### 2.3 Spec Markdown Extraction ✅ DONE (2025-12-21)
Added `SpecExtractor` for markdown specification files.

**New Files**:
- `spec_extractor.py` — Markdown parser for spec/ files
- `_tests/test_spec_extractor.py` — 17 tests

**Capabilities**:
- Parse ## headers as DocNode symbols
- Extract code blocks as examples
- Parse Anti-patterns sections as warning teaching moments
- Parse Laws tables as critical teaching moments
- Integrated with ReferenceGenerator

**Metrics**:
- Spec files processed: 201
- Spec DocNodes: 634
- Spec examples: 352
- Spec teaching moments: 51 (16 critical laws, 35 anti-pattern warnings)

**Combined totals**:
- Total DocNodes: 8,243 (7,609 code + 634 spec)
- Total teaching: 79 (28 code + 51 spec)
- Total examples: 937 (585 code + 352 spec)

---

## Phase 2 (Original - For Reference)

### 2.1 Add Module-Level Extraction
Currently we extract from functions/classes. Extend to capture:
- Module docstrings (the Teaching: sections at file level)
- Package docstrings (`__init__.py`)
- Spec files (markdown → structured extraction)

```python
# New extractor method
def extract_module_docstring(self, path: Path) -> DocNode | None:
    """Extract module-level docstring as a DocNode."""
    source = path.read_text()
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree)
    if docstring:
        summary, examples, teaching = self._parse_docstring(docstring)
        return DocNode(
            symbol=path.stem,  # File name as symbol
            signature=f"module {path.stem}",
            summary=summary,
            examples=examples,
            teaching=teaching,
            tier=Tier.RICH,
            module=self._path_to_module(path),
        )
    return None
```

### 2.2 Add Cross-Reference Linking
Link symbols to their AGENTESE paths:

```python
@dataclass(frozen=True)
class DocNode:
    # ... existing fields ...
    agentese_path: str | None = None  # e.g., "self.memory.capture"
    related_symbols: tuple[str, ...] = ()  # Cross-references
```

### 2.3 Add Spec Extraction
Parse markdown specs into DocNodes:

```python
def extract_spec(self, path: Path) -> list[DocNode]:
    """Extract documentation from spec markdown files."""
    # Parse ## headers as symbols
    # Extract code blocks as examples
    # Parse Laws tables as teaching moments
```

---

## Phase 3: Documentation Generator ✅ COMPLETE (2025-12-21)

### 3.1 Reference Generator Service ✅ DONE

Implemented `generate_to_directory()` method with full manifest tracking:

```python
from services.living_docs import generate_to_directory
from pathlib import Path

manifest = generate_to_directory(Path("docs/reference"), overwrite=True)
print(f"Generated {manifest.file_count} files, {manifest.total_symbols} symbols")
```

**New Types**:
- `GeneratedFile` — Metadata for each generated file
- `GenerationManifest` — Tracks all generated files with totals

**New Methods**:
- `generate_to_directory(output_dir, overwrite=False)` — Main entry point
- `_generate_category_page()` — Generates single category file
- `_generate_index()` — Generates index.md with navigation

### 3.2 Output Structure ✅ DONE

Generated structure:
```
docs/reference/
├── index.md                         # Overview + navigation
├── crown-jewels/
│   └── crown-jewels.md             # 2,020 symbols, 20 gotchas
├── categorical-foundation/
│   └── categorical-foundation.md   # 1,776 symbols, 4 gotchas
├── agentese-protocol/
│   └── agentese-protocol.md        # 1,879 symbols, 5 gotchas
├── ashc-compiler/
│   └── ashc-compiler.md            # 404 symbols
├── specs/
│   ├── core-specifications.md      # 49 symbols, 11 gotchas
│   ├── agent-specifications.md     # 83 symbols, 10 gotchas
│   └── protocol-specifications.md  # 206 symbols, 23 gotchas
└── teaching/
    └── gotchas.md                  # 80 teaching moments by severity
```

### 3.3 Navigation Index ✅ DONE

Each category page includes:
- Header with description
- Grouped by module (## headers)
- Symbol signature with code block
- Summary
- AGENTESE path (if applicable)
- Examples
- Teaching moments with evidence
- Footer with counts and generation date

**Metrics**:
- 9 files generated
- 6,417 total symbols
- 73 teaching moments
- 16 tests passing

---

## Phase 4: Teaching Moments Database

### 4.1 Aggregate All Gotchas

```python
# services/living_docs/teaching_db.py

class TeachingDatabase:
    """Aggregated teaching moments across the codebase."""

    def collect_all(self, paths: list[Path]) -> list[TeachingMoment]:
        """Collect all teaching moments from all files."""
        ...

    def by_severity(self) -> dict[str, list[TeachingMoment]]:
        """Group by severity: critical, warning, info."""
        ...

    def by_module(self) -> dict[str, list[TeachingMoment]]:
        """Group by module path."""
        ...

    def verify_evidence(self) -> list[TeachingMoment]:
        """Find teaching moments with missing evidence."""
        ...
```

### 4.2 Teaching Moments Page

Generate a dedicated page:

```markdown
# Teaching Moments (Gotchas)

> *"Gotchas live in docstrings, not wikis."*

## 🚨 Critical (Must Know)

### Brain
- **Crystal merging is NOT commutative**
  Evidence: `test_brain_crystal.py::test_merge_order`

### Witness
- **Always check Grant before invoking Playbook**
  Evidence: `test_playbook.py::test_grant_required`

## ⚠️ Warnings

...

## ℹ️ Info

...
```

---

## Phase 5: CLI Integration

### 5.1 Generator Commands

```bash
# Generate full reference docs
kg docs generate --output docs/reference/

# Generate single file
kg docs generate services/brain/persistence.py

# Generate gotchas page
kg docs gotchas --output docs/reference/teaching/gotchas.md

# Verify all evidence links exist
kg docs verify-evidence

# Find stale docs (code changed, docs not regenerated)
kg docs stale --days 7
```

### 5.2 CI Integration

```yaml
# .github/workflows/docs.yml
- name: Generate Reference Docs
  run: kg docs generate --output docs/reference/

- name: Verify Evidence Links
  run: kg docs verify-evidence --strict

- name: Check for Stale Docs
  run: kg docs stale --days 7 --fail-on-stale
```

---

## Phase 6: Public Presentation Polish

### 6.1 Add Metadata for Each Page

```python
@dataclass
class PageMetadata:
    title: str
    description: str  # For SEO/social
    status: str  # "stable", "beta", "experimental"
    last_updated: datetime
    authors: list[str]
    tags: list[str]
```

### 6.2 Add Visual Elements

- Mermaid diagrams from specs
- Architecture diagrams for Crown Jewels
- State machine diagrams for PolyAgents
- Dependency graphs from Gestalt

### 6.3 Versioning

Track doc versions alongside code:

```python
@dataclass
class DocVersion:
    code_sha: str
    doc_sha: str
    generated_at: datetime
    coverage: float  # % of symbols documented
```

---

## Implementation Order

| Phase | Deliverable | Estimated Effort |
|-------|-------------|------------------|
| 1 | Inventory audit | 1 session |
| 2.1 | Module-level extraction | 1 session |
| 2.2 | Cross-reference linking | 1 session |
| 3 | Reference generator | 2 sessions |
| 4 | Teaching database | 1 session |
| 5 | CLI commands | 1 session |
| 6 | Public polish | 2 sessions |

**Total**: ~9 sessions for complete reference documentation system

---

## Success Criteria

1. **Coverage**: 100% of Crown Jewels documented
2. **Teaching**: All gotchas have evidence links
3. **Navigation**: Every symbol reachable in 2 clicks
4. **Freshness**: Docs regenerate on code change
5. **Verification**: Evidence links verified in CI
6. **Public Ready**: Metadata, styling, SEO

---

## Immediate Next Step

Run the inventory audit to see current coverage:

```bash
uv run python -c "
from services.living_docs import DocstringExtractor
from pathlib import Path

extractor = DocstringExtractor()

# Audit Crown Jewels
jewels = [
    'services/brain/',
    'services/witness/',
    'services/conductor/',
    'services/living_docs/',
    'services/town/',
    'services/gestalt/',
]

for jewel in jewels:
    path = Path(jewel)
    if not path.exists():
        continue

    py_files = list(path.glob('**/*.py'))
    total_nodes = 0
    total_teaching = 0

    for f in py_files:
        if '_tests' in str(f):
            continue
        nodes = extractor.extract_file(f)
        total_nodes += len(nodes)
        total_teaching += sum(len(n.teaching) for n in nodes)

    print(f'{jewel}: {total_nodes} symbols, {total_teaching} gotchas')
"
```

---

*"The proof is not in the prose. The proof is in the functor."*
