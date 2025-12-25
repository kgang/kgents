# Living Specification Protocol

> *"Specifications that verify themselves through evidence accumulation."*

**Status:** Production Standard
**Consolidated from:** living-docs.md, living-spec-evidence.md, living-spec-ui-strategy.md, SYNTHESIS-living-spec.md
**Date:** 2025-12-24
**Heritage:** Literate Programming (Knuth) × DSPy × FastAPI × Python doctest

---

## Part I: Core Insight

Living Specifications are **documents that verify their own truth claims through evidence**:

```
Living Spec = Claims × Evidence × Proofs × Ledger
            = Hypergraph × Tokens × Monad × Witness

where:
  Claims    = Assertions extracted from spec text
  Evidence  = Implementation/test/usage that validates claims
  Proofs    = Executable demonstrations (tests, ASHC round-trips)
  Ledger    = Accounting system tracking spec health
```

### The Three Revelations

1. **Documentation as Projection** — Specs aren't description, they're projections. The same source renders differently for different observers (human/agent/IDE).

2. **Evidence IS Marks** — Evidence isn't a separate concept. It's witness marks with specific tags. No new systems needed.

3. **Specs as Accounting** — Treat specs like a ledger: claims are assets, evidence are transactions, contradictions are liabilities, harmonies compound interest.

---

## Part II: Evidence Model

> *"The mark IS the witness. Evidence emerges from activity."*

### Evidence as Tagged Marks

Evidence integrates with the existing witness infrastructure. Every piece of evidence is a mark with structured tags:

```
Tag Taxonomy:
  spec:{path}        — Mark relates to a spec (e.g., spec:principles.md)
  evidence:impl      — Declares implementation evidence
  evidence:test      — Declares test evidence
  evidence:usage     — Declares usage evidence
  evidence:run       — Records a test run
  evidence:pass      — Test passed
  evidence:fail      — Test failed
  file:{path}        — Path to the evidence file
  first-evidence     — First evidence for an orphan spec
```

### Declaring Evidence

```python
# When declaring "this implements that"
await ledger.evidence_add(
    spec_path="principles.md",
    evidence_path="impl/claude/agents/operad.py",
    evidence_type="implementation",
    author="kent",
    reasoning="Operad implements composition laws from principles.md"
)

# Creates mark with tags:
# ["spec:principles.md", "evidence:impl", "file:impl/claude/agents/operad.py"]
```

### Querying Evidence

```python
# Get all evidence for a spec
evidence = await ledger.evidence_query("principles.md")

# Get only implementation evidence
evidence = await ledger.evidence_query("principles.md", evidence_type="impl")

# Verify evidence is not stale
result = await ledger.evidence_verify("principles.md")
# → { valid: 3, stale: 0, broken: 1, results: [...] }
```

### Why This Matters

**Composability** — Evidence uses existing witness infrastructure. No new tables.

**Generativity** — Evidence emerges from activity. Tests running emit marks automatically.

**Auditability** — Every piece of evidence has timestamp, author, reasoning built-in.

**Query Power** — All mark query capabilities available: time range, author, semantic search via D-gent.

---

## Part III: Documentation as Projection

> *"Docs are not description—they are projection."*

### The Functor

```
LivingDocs : (Source × Spec) → Observer → Surface

where:
  Source   = Code + Docstrings + Types + Tests
  Spec     = Intent + Principles (from spec/ files)
  Observer = Human(density) | Agent | IDE
  Surface  = Markdown | Structured | Tooltip
```

The same source projects differently to different observers. There is no canonical "documentation"—only projections.

### Core Types

```python
@dataclass(frozen=True)
class DocNode:
    """Atomic documentation primitive extracted from source."""
    symbol: str                    # Function/class name
    signature: str                 # Type signature
    summary: str                   # First line of docstring
    examples: tuple[str, ...]      # From doctest or Example: sections
    teaching: tuple[TeachingMoment, ...]
    evidence: tuple[str, ...]      # Test refs that verify behavior


@dataclass(frozen=True)
class TeachingMoment:
    """A gotcha with provenance. The killer feature."""
    insight: str                   # What to know
    severity: Literal["info", "warning", "critical"]
    evidence: str | None           # test_file.py::test_name
    commit: str | None             # Git SHA where learned


@dataclass(frozen=True)
class Observer:
    """Who's reading determines what they see."""
    kind: Literal["human", "agent", "ide"]
    density: Literal["compact", "comfortable", "spacious"] = "comfortable"


@dataclass(frozen=True)
class Surface:
    """Projected output for an observer."""
    content: str
    format: Literal["markdown", "structured", "tooltip"]


@dataclass(frozen=True)
class Verification:
    """Round-trip verification result."""
    equivalent: bool
    score: float                   # 0.0-1.0 semantic similarity
    missing: tuple[str, ...]       # What docs don't capture
```

### Extraction Tiers

Not every function needs full extraction. Match effort to importance:

| Tier | When | What's Extracted |
|------|------|------------------|
| **Minimal** | Private helpers, simple functions | Signature only |
| **Standard** | Public API | Signature + summary + examples |
| **Rich** | Crown Jewels, complex APIs | Full teaching moments + verification |

### Inline Truth Pattern

Gotchas live in docstrings, not wikis:

```python
class BrainCrystal:
    """
    Crystallized memory with semantic embeddings.

    Teaching:
        gotcha: Always check `crystal.is_active` before accessing embeddings.
                (Evidence: test_brain_persistence.py::test_stale_crystal)

        gotcha: Crystal merging is NOT commutative. Order matters.
                (Evidence: test_brain_crystal.py::test_merge_order)

    Example:
        >>> crystal = await brain.capture("insight")
        >>> assert crystal.is_active
    """
```

The parser extracts `Teaching:` and `Example:` sections into `DocNode`.

### Projection Function

```python
def project(node: DocNode, observer: Observer) -> Surface:
    """Single function, not class hierarchy."""

    if observer.kind == "agent":
        # Dense, structured—no prose
        return Surface(
            content=f"## {node.symbol}\n{node.signature}\n"
                    f"Gotchas: {[t.insight for t in node.teaching]}\n"
                    f"Examples: {node.examples[:2]}",
            format="structured"
        )

    elif observer.kind == "ide":
        # Minimal—signature + one gotcha
        gotcha = next((t for t in node.teaching if t.severity == "critical"), None)
        return Surface(
            content=f"{node.signature}\n{gotcha.insight if gotcha else ''}",
            format="tooltip"
        )

    else:  # human
        # Narrative with density adaptation
        return _human_projection(node, observer.density)
```

### Verification (ASHC Integration)

> *"If you can't regenerate impl from docs, docs don't capture essence."*

```python
async def verify_roundtrip(doc: DocNode, impl_path: Path) -> Verification:
    """Can ASHC regenerate equivalent impl from docs alone?"""

    generated = await ashc.compile(doc.to_spec(), variations=5)
    actual = impl_path.read_text()

    score = await semantic_similarity(generated.best, actual)

    return Verification(
        equivalent=score > 0.8,
        score=score,
        missing=find_undocumented_behavior(generated.best, actual),
    )
```

**Compression Metric**: `len(impl) / len(doc)` should be > 5:1 for mature code.

---

## Part IV: Ledger UI Strategy

> *"Upload spec → Parse → Accumulate evidence → Brilliant executions"*
> *"If proofs valid, supported. If not used, dead."*

### Core Philosophy

Living Spec UI is an **accounting ledger for specifications**:

1. **Spec = Asset** — Claims that can accrue evidence
2. **Evidence = Transactions** — Implementations, tests, usage that prove specs
3. **Contradictions = Liabilities** — Conflicts that drain value
4. **Harmonies = Compound Interest** — Reinforcements that multiply value
5. **Orphans = Dead Weight** — Specs with no evidence, candidates for deprecation

**Symmetric Harness**: The UI is the same interface agents use. Every Kent action is an AGENTESE call. Agents make identical calls.

### Bootstrap Results (Example)

```
Total specs:      198
Active:           165
Orphans:           86  ← 43% have NO evidence
Deprecated:        22
Archived:          11
Total claims:     255
Contradictions:     0
Harmonies:        313
```

### Screen 1: Ledger Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  LIVING SPEC LEDGER                              [Scan Corpus]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── ASSETS ────────┐  ┌─── LIABILITIES ──────┐               │
│  │                   │  │                      │               │
│  │  198 Total Specs  │  │  86 Orphans          │               │
│  │  165 Active       │  │  22 Deprecated       │               │
│  │  255 Claims       │  │   0 Contradictions   │               │
│  │  313 Harmonies    │  │                      │               │
│  │                   │  │                      │               │
│  └───────────────────┘  └──────────────────────┘               │
│                                                                 │
│  ┌─── RECENT ACTIVITY ─────────────────────────────────────┐   │
│  │ 2m ago   spec/protocols/living-spec.md  +3 claims       │   │
│  │ 1h ago   spec/agents/d-gent.md          +1 impl         │   │
│  │ 3h ago   spec/services/witness.md       +2 tests        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 2: Spec Detail

```
┌─────────────────────────────────────────────────────────────────┐
│  spec/protocols/k-block.md                          [Edit] [⋮] │
├─────────────────────────────────────────────────────────────────┤
│  Status: ACTIVE    Claims: 3    Evidence: 5    Harmonies: 8    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── CLAIMS ──────────────────────────────────────────────┐   │
│  │ ▸ ASSERTION: K-Block should provide monadic isolation   │   │
│  │   Evidence: services/k_block/core/kblock.py ✓           │   │
│  │             _tests/test_kblock.py ✓                     │   │
│  │                                                         │   │
│  │ ▸ CONSTRAINT: K-Block must not lose data                │   │
│  │   Evidence: [NONE] ⚠ Add evidence...                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─── EVIDENCE ────────────────────────────────────────────┐   │
│  │ Implementation:                                         │   │
│  │   • services/k_block/core/kblock.py                     │   │
│  │                                                         │   │
│  │ Tests:                                                  │   │
│  │   • _tests/test_kblock.py (12 tests, 100% pass)         │   │
│  │                                                         │   │
│  │ [+ Add Evidence]  [Run Tests]  [Validate Claims]        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Symmetric Harness: Agent Actions = Kent Actions

| Kent Action | AGENTESE Call | Agent Can Do? |
|-------------|---------------|---------------|
| Upload spec | `self.spec.upload(path, content)` | ✓ |
| Scan corpus | `self.spec.scan()` | ✓ |
| View ledger | `self.spec.ledger()` | ✓ |
| Add evidence | `self.spec.evidence.add(spec, impl)` | ✓ |
| Run tests | `self.spec.proof.run(spec)` | ✓ |
| Deprecate spec | `self.spec.deprecate(path, reason)` | ✓ |
| Resolve conflict | `self.spec.resolve(spec_a, spec_b, resolution)` | ✓ |
| Find contradictions | `self.spec.contradictions()` | ✓ |
| Find orphans | `self.spec.orphans()` | ✓ |

**Implementation**: Every button click calls the same AGENTESE endpoint an agent would use.

---

## Part V: Integration

### AGENTESE Paths

```
# Documentation extraction/projection
concept.docs.extract     # Source → DocNode
concept.docs.project     # DocNode × Observer → Surface
concept.docs.verify      # DocNode × Path → Verification

# Spec ledger operations
self.spec.scan()         # Scan corpus, populate ledger
self.spec.ledger()       # Get ledger data
self.spec.get(path)      # Get one spec detail

# Evidence operations
self.spec.evidence.add(spec, path, type)
self.spec.evidence.verify(spec)
self.spec.proof.run(spec)

# Spec health queries
self.spec.orphans()      # Specs without evidence
self.spec.contradictions()  # Conflicting claims
self.spec.harmonies()    # Reinforcing relationships

# Context queries
self.docs.for_file       # Get docs for current file
self.docs.gotchas        # Teaching moments in scope
```

### Data Model (Postgres)

```sql
CREATE TABLE spec_ledger (
    id UUID PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    title TEXT,
    status TEXT DEFAULT 'active',  -- active, orphan, deprecated, archived
    content_hash TEXT,
    claim_count INT DEFAULT 0,
    impl_count INT DEFAULT 0,
    test_count INT DEFAULT 0,
    ref_count INT DEFAULT 0,
    last_scanned TIMESTAMP,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE spec_claims (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES spec_ledger(id),
    claim_type TEXT,  -- assertion, constraint, definition
    subject TEXT,
    predicate TEXT,
    line_number INT,
    raw_text TEXT
);

CREATE TABLE spec_evidence (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES spec_ledger(id),
    evidence_type TEXT,  -- implementation, test, usage
    path TEXT,
    last_verified TIMESTAMP,
    status TEXT  -- valid, stale, broken
);

CREATE TABLE spec_relations (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES spec_ledger(id),
    target_id UUID REFERENCES spec_ledger(id),
    relation_type TEXT,  -- references, extends, contradicts, harmonizes
    strength FLOAT
);
```

### Unified Hydration (AD-017)

> *"One truth. One store. The soil remembers."*

**Anti-Pattern**: Re-extracting docstrings on every `hydrate()` call.

**Fix**: Crystallize teaching moments to Brain once. Query Brain for hydration.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  UNIFIED FLOW                                                               │
│                                                                             │
│  Docstrings ───crystallize──▶ Brain (Single Source) ───query──▶ Hydration  │
│       │                           │                                         │
│       │                           ├── alive teaching                        │
│       │                           ├── extinct teaching (ghosts)             │
│       │                           └── prior evidence (ASHC)                 │
│       │                                                                     │
│       └───(CI/bootstrap crystallizes once)                                  │
│                                                                             │
│  One truth. One store. Reactive invalidation.                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**: Brain stores TeachingCrystals. Hydrator queries Brain, not TeachingCollector.

---

## Part VI: Laws

> *"A law without its domain is a lie."*

Laws are verified, not aspirational. No witness = no law.

### Documentation Laws

| Law | Statement | Witness |
|-----|-----------|---------|
| **Functor** | `project(compose(a, b)) ≡ compose(project(a), project(b))` | `LivingDocsWitness.verify_functor()` |
| **Freshness** | Claims re-verified within 7 days are valid | CI job: `kg docs verify --stale-days=7` |
| **Provenance** | `∀ TeachingMoment: evidence ≠ None → test exists` | `LivingDocsWitness.verify_provenance()` |
| **Preservation** | `extract(source).summary ≡ normalize(docstring.first_line)` | `test_extractor.py::TestPropertyBased` |

### Evidence Laws

| Law | Statement | Witness |
|-----|-----------|---------|
| **Crystallization** | `∀ TeachingMoment T: crystallize(T) → Brain.TeachingCrystal` | `test_crystallization.py` |
| **Unified Query** | `hydrate(task) → Brain.query(task)` (not re-extract) | `test_unified_hydration.py` |
| **Ghost Inclusion** | `hydrate(task) includes extinct teaching when keywords match` | `test_ghost_hydration.py` |

### Law Domains (When Laws Hold)

Laws are not universal truths—they hold within precisely defined domains.

**Example: Preservation Law**

**Law:** Extracted summary equals normalized original content.

**Domain of Validity:**
```
Valid(text) ≡ text ∈ Unicode ∧ ¬contains_escape_sequences(text)
```

**Valid:**
- All Unicode categories except surrogates (Cs)
- Multi-line content (normalized via `" ".join(s.split())`)

**Invalid (law does NOT hold):**
- Python escape sequences: `\0`, `\n`, `\t`, `\x00`, `\u0000`
- Reason: Python's AST parser interprets escape sequences *before* extraction

**Why the boundary exists:**

```
Input:       "\\0"              (2 chars: backslash, zero)
Source:      f'"""{text}"""'   → '"""\0"""'
AST parse:   \0 interpreted    → null character
Output:      "\x00"             (1 char: null)
```

Python's AST parser interprets escape sequences before we can extract them. This is Python's contract, not ours to override.

**Boundary Documentation Template:**

```markdown
**Law:** [Statement]
**Domain:** [Formal predicate or set description]
**Boundary:** [What's excluded and why]
**Evidence:** [Test that verifies both validity and boundary]
```

---

## Part VII: CLI

```bash
# Documentation extraction/projection
kg docs extract impl/claude/services/brain/persistence.py
kg docs project services/brain/ --observer agent --density compact

# Verify round-trip
kg docs verify spec/services/brain.md impl/claude/services/brain/
# → Score: 0.87 | Missing: error handling for stale crystals

# Find stale docs
kg docs stale --days 30
# → 5 files diverged from impl

# Spec ledger operations
kg spec scan          # Scan all specs in spec/
kg spec ledger        # Show ledger dashboard
kg spec detail spec/protocols/k-block.md

# Evidence operations
kg spec evidence add spec/protocols/k-block.md impl/claude/services/k_block/
kg spec evidence verify spec/protocols/k-block.md

# Spec health queries
kg spec orphans       # List specs without evidence
kg spec contradictions  # Find conflicting claims
```

---

## Part VIII: Implementation Phases

### Phase 1: Extraction (Week 1)

**Deliverable**: DocNode parser, docstring sections extraction
- Parse `Teaching:` and `Example:` sections from docstrings
- Extract function/class signatures
- Build DocNode data structure

### Phase 2: Projection (Week 1)

**Deliverable**: Human/Agent/IDE surfaces
- Implement `project()` function for three observer types
- Density-aware rendering for humans
- Structured output for agents
- Minimal tooltips for IDEs

### Phase 3: Ledger Core (Week 2)

**Deliverable**: Spec ledger backend + UI
- Spec corpus scanner
- Postgres tables for ledger/claims/evidence/relations
- Dashboard UI showing assets/liabilities
- Table view with sorting/filtering

### Phase 4: Evidence Tracking (Week 2)

**Deliverable**: Evidence accumulation system
- `/api/spec/evidence/add` endpoint
- Evidence verification (file existence check)
- Integration with witness marks (tags)
- Test runner integration

### Phase 5: Verification (Week 3)

**Deliverable**: Round-trip via ASHC, CI integration
- ASHC regeneration from docs
- Semantic similarity scoring
- CI job for freshness checks
- Compression metric tracking

### Phase 6: Git Enrichment (Week 3)

**Deliverable**: TeachingMoments from blame
- Integration with Repo Archaeology service
- Bug fix → teaching moment conversion
- Commit SHA provenance tracking

---

## Part IX: Anti-Patterns

| Anti-Pattern | Why It's Wrong | Instead |
|--------------|----------------|---------|
| Docs in wikis | Diverges from code; no provenance | Inline docstrings with extraction |
| Unverified claims | Claims without test evidence rot | Link to test evidence |
| One projection | Agents ≠ humans ≠ IDEs | Observer-dependent projection |
| Manual maintenance | Doesn't scale | Auto-extract + crystallize |
| Over-extraction | Not every helper needs teaching moments | Use extraction tiers |
| Document viewer | Specs aren't documents, they're claims | Ledger with evidence |
| Kent-only actions | Breaks symmetric harness | Every action = AGENTESE |
| Ignore orphans | Dead weight accumulates | Surface and triage |

---

## Part X: Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Orphan rate | < 20% | Specs should have evidence |
| Contradiction count | 0 hard, < 10 soft | Corpus should be coherent |
| Evidence coverage | > 80% | Claims should be proven |
| Proof pass rate | 100% | All proofs should be valid |
| Agent action parity | 100% | Symmetric harness complete |
| Compression ratio | > 5:1 | Docs are spec, not prose |

---

## Connection to Principles

| Principle | Embodiment |
|-----------|------------|
| **Tasteful** | Curated projections, not dumps; extraction tiers match importance |
| **Curated** | Ledger surfaces orphans for deprecation |
| **Generative** | Docs can regenerate impl (ASHC); specs are compression |
| **Composable** | Functor law verified; evidence uses witness marks |
| **Joy-Inducing** | IDE hovers surface gotchas before bugs; symmetric harness empowers agents |
| **Ethical** | Full audit trail; every claim has provenance |

---

## Related Specs

- `spec/protocols/witness.md` — Witness mark infrastructure
- `spec/protocols/repo-archaeology.md` — Git blame analysis
- `spec/protocols/ASHC-agentic-self-hosting.md` — Round-trip verification
- `spec/services/brain.md` — TeachingCrystal storage

---

*"The proof is not in the prose. The proof is in the functor."*
*"Upload spec → Parse → Accumulate evidence → Brilliant executions"*
*"If proofs valid, supported. If not used, dead."*

**Consolidated**: 2025-12-24
**Implementation**: `impl/claude/services/living_spec/`, `impl/claude/services/living_docs/`
