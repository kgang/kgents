# Living Docs: Documentation as Projection

**Status:** Emerging Standard
**Implementation:** `impl/claude/services/living_docs/`
**AGENTESE:** `concept.docs.*`, `self.docs.*`

> *"Docs are not description—they are projection."*

---

## Heritage

| Source | Insight | How We Extend It |
|--------|---------|------------------|
| **Literate Programming (Knuth)** | Weave (human) and Tangle (machine) from same source | Observer-dependent projection replaces two static outputs |
| **DSPy** | Prompts are programs, not strings | Docs are typed, composable, verifiable programs |
| **FastAPI OpenAPI** | Type hints + docstrings → rich API docs | Structured docstrings → observer-specific surfaces |
| **Python doctest** | Examples in docstrings are executable tests | Teaching moments in docstrings are traceable gotchas |

---

## The Functor

```
LivingDocs : (Source × Spec) → Observer → Surface

where:
  Source   = Code + Docstrings + Types + Tests
  Spec     = Intent + Principles (from spec/ files)
  Observer = Human(density) | Agent | IDE
  Surface  = Markdown | Structured | Tooltip
```

The same source projects differently to different observers. There is no canonical "documentation"—only projections.

---

## Core Types (5 Only)

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

---

## Extraction Tiers

Not every function needs full extraction. Match effort to importance:

| Tier | When | What's Extracted |
|------|------|------------------|
| **Minimal** | Private helpers, simple functions | Signature only |
| **Standard** | Public API | Signature + summary + examples |
| **Rich** | Crown Jewels, complex APIs | Full teaching moments + verification |

```python
def extraction_tier(symbol: str, module: str) -> Tier:
    if symbol.startswith("_"):
        return Tier.MINIMAL
    if module.startswith("services/"):
        return Tier.RICH
    return Tier.STANDARD
```

---

## Inline Truth Pattern

> *"Gotchas live in docstrings, not wikis."*

Like FastAPI derives OpenAPI from code, we extract from structured docstrings:

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

---

## Projection

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

---

## Verification (ASHC Integration)

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

## Git Context

Git blame enriches teaching moments. **Delegate to Repo Archaeology** (see `spec/protocols/repo-archaeology.md`) for full git analysis. Living Docs consumes:

```python
# From Repo Archaeology
blame: dict[int, CommitInfo]  # line → commit info

# Convert bug fixes to teaching moments
for fix in archaeology.bug_fixes(path):
    node.teaching += TeachingMoment(
        insight=f"Previous bug: {fix.description}",
        severity="warning",
        evidence=fix.commit,
        commit=fix.sha,
    )
```

---

## Laws

| Law | Statement | Witness |
|-----|-----------|---------|
| **Functor** | `project(compose(a, b)) ≡ compose(project(a), project(b))` | `LivingDocsWitness.verify_functor()` |
| **Freshness** | Claims re-verified within 7 days are valid | CI job: `kg docs verify --stale-days=7` |
| **Provenance** | `∀ TeachingMoment: evidence ≠ None → test exists` | `LivingDocsWitness.verify_provenance()` |
| **Preservation** | `extract(source).summary ≡ normalize(docstring.first_line)` | `test_extractor.py::TestPropertyBased` |

Laws are verified, not aspirational. No witness = no law.

---

## Law Domains (When Laws Hold)

> *"A law without its domain is a lie."*

Laws are not universal truths—they hold within precisely defined domains. Documenting domain boundaries is as important as documenting the law itself.

### Preservation Law Domain

**Law:** Extracted summary equals normalized original content.

**Domain of Validity:**
```
Valid(text) ≡ text ∈ Unicode ∧ ¬contains_escape_sequences(text)
```

**Specifically valid:**
- All Unicode categories except surrogates (Cs)
- Multi-line content (normalized via `" ".join(s.split())`)
- Whitespace variations

**Explicitly invalid (law does NOT hold):**
- Python escape sequences: `\0`, `\n`, `\t`, `\x00`, `\u0000`, etc.
- Backslash followed by interpretable characters

**Why the boundary exists:**

```
Input:       "\\0"              (2 chars: backslash, zero)
Source:      f'"""{text}"""'   → '"""\0"""'
AST parse:   \0 interpreted    → null character
Output:      "\x00"             (1 char: null)
```

Python's AST parser interprets escape sequences *before* we can extract them. This is Python's contract, not ours to override. The extractor correctly returns what Python parsed.

**Generalized Pattern:**

When a law fails at a boundary, ask:
1. **Is the boundary in our control?** (No—Python parser)
2. **Can we extend validity?** (Only by reimplementing Python's parser—violates taste)
3. **Is the boundary fundamental?** (Yes—escape sequences are inherently interpretive)

If (1)=No, (2)=costly, (3)=Yes → **Document the boundary, don't paper over it.**

### Boundary Documentation Template

```markdown
**Law:** [Statement]
**Domain:** [Formal predicate or set description]
**Boundary:** [What's excluded and why]
**Evidence:** [Test that verifies both validity and boundary]
```

---

## AGENTESE Paths

```
concept.docs.extract     # Source → DocNode
concept.docs.project     # DocNode × Observer → Surface
concept.docs.verify      # DocNode × Path → Verification

self.docs.for_file       # Get docs for current file
self.docs.gotchas        # Teaching moments in scope
```

---

## CLI

```bash
# Extract and project
kg docs extract impl/claude/services/brain/persistence.py
kg docs project services/brain/ --observer agent --density compact

# Verify round-trip
kg docs verify spec/services/brain.md impl/claude/services/brain/
# → Score: 0.87 | Missing: error handling for stale crystals

# Find stale docs
kg docs stale --days 30
# → 5 files diverged from impl
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Docs in wikis | Diverges from code; no provenance |
| Unverified claims | Claims without test evidence rot |
| One projection | Agents ≠ humans ≠ IDEs |
| Manual maintenance | Docs should be extracted, not written |
| Over-extraction | Not every helper needs teaching moments |

---

## Implementation Phases

| Phase | Deliverable | Dependency |
|-------|-------------|------------|
| **1. Extraction** | DocNode parser, docstring sections | None |
| **2. Projection** | Human/Agent/IDE surfaces | Phase 1 |
| **3. Verification** | Round-trip via ASHC, CI integration | Phase 1, ASHC |
| **4. Git Enrichment** | TeachingMoments from blame | Phase 1, Repo Archaeology |

Interactive Text integration deferred—will import from Living Docs when ready.

---

## Connection to Principles

| Principle | Embodiment |
|-----------|------------|
| **Tasteful** | Curated projections, not dumps |
| **Curated** | Extraction tiers match importance |
| **Generative** | Docs can regenerate impl (ASHC) |
| **Composable** | Functor law verified |
| **Joy-Inducing** | IDE hovers surface gotchas before bugs |

---

*"The proof is not in the prose. The proof is in the functor."*
