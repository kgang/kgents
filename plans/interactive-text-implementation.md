---
path: plans/interactive-text-implementation
status: active
progress: 25
last_touched: 2025-12-21
touched_by: claude-opus-4
blocking: []
enables: [living-docs, teaching-mode, spec-as-interface]
session_notes: |
  Created from spec/protocols/interactive-text.md.
  A Crown Jewel that collapses the boundary between documentation and interface.
  Follows AD-009 (Metaphysical Fullstack) with full vertical slice architecture.

  Session 1 (2025-12-21): Phase 1 COMPLETE
  - Discovered existing implementation in services/interactive_text/
  - 211 tests passing (171 existing + 40 new parser tests)
  - Added test_parser.py with roundtrip fidelity verification
  - Pattern deviation noted: [P1] and [R7.1] instead of (AD-009) and _Requirements:_
    This is intentional—simpler, more consistent bracket notation preferred
phase_ledger:
  PLAN: complete
  PHASE_1: complete
---

# Interactive Text Protocol Implementation

> *"The spec is not description—it is generative. The text is not passive—it is interface."*

**Spec**: `spec/protocols/interactive-text.md`
**Service**: `services/interactive-text/`
**AGENTESE**: `self.document.interactive`

---

## Purpose

The Interactive Text Protocol collapses the boundary between documentation and interface. Text files become live control surfaces while remaining valid markdown readable anywhere.

**Core Insight**:
```
Text File ──Projection Functor──▶ Interactive Surface
```

The same insight that drives AGENTESE ("observation is interaction") extended to documents themselves.

---

## Architecture (AD-009 Metaphysical Fullstack)

```
┌────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES                                             │
│     CLI (Rich) │ Web │ marimo │ JSON                                │
├────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL                                               │
│     logos.invoke("self.document.interactive.*", observer)           │
├────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE                                                   │
│     @node("self.document.interactive")                              │
│     aspects: manifest, toggle_task, analyze_image                   │
├────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE (Crown Jewel)                                    │
│     services/interactive-text/                                      │
│     parser.py + tokens/ + sheaf.py + polynomial.py                  │
├────────────────────────────────────────────────────────────────────┤
│  3. CATEGORICAL INFRASTRUCTURE                                      │
│     DocumentPolynomial (state machine: VIEWING → EDITING → ...)     │
│     DocumentSheaf (multi-view coherence)                            │
├────────────────────────────────────────────────────────────────────┤
│  2. TOKEN LAYER                                                     │
│     Six token types (curated, not catalogued):                      │
│     AGENTESEPath, TaskCheckbox, Image, CodeBlock,                   │
│     PrincipleRef, RequirementRef                                    │
├────────────────────────────────────────────────────────────────────┤
│  1. PERSISTENCE (File System)                                       │
│     File is the single source of truth                              │
│     StorageProvider for metadata caching                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## Phases (from spec Part VI)

### Phase 1: Recognition Layer ✅ COMPLETE

**Goal**: Markdown parser extension recognizing six token types

**Deliverables**:
- [x] `services/interactive_text/__init__.py` — Public API
- [x] `services/interactive_text/parser.py` — Markdown parser with token extraction
- [x] `services/interactive_text/tokens/` — Token type implementations
  - [x] `base.py` — BaseMeaningToken protocol with trace witness capture
  - [x] `agentese_path.py` — Pattern: `` `world.*.* `` (all 5 contexts)
  - [x] `task_checkbox.py` — Pattern: `- [ ] Task` / `- [x] Task`
  - [x] `image.py` — Pattern: `![alt](path)`
  - [x] `code_block.py` — Pattern: ` ```lang ... ``` `
  - [x] `principle_ref.py` — Pattern: `[P1]` (simplified from spec)
  - [x] `requirement_ref.py` — Pattern: `[R7.1]` (simplified from spec)
- [x] `services/interactive_text/_tests/test_parser.py` — 40 roundtrip fidelity tests

**Pattern Design Decision**: The implementation uses `[P1]` and `[R7.1]` instead of the spec's `(AD-009)` and `_Requirements: 7.1_`. This is intentional—bracket notation is more consistent, compact, and aligns with common markdown conventions. Per *"Tasteful > feature-complete"*.

**Verification Criteria** (all passing):
```python
def test_roundtrip():
    doc = load("test.md")
    ast = parse(doc)
    rendered = render(ast)
    reparsed = parse(rendered)
    assert ast == reparsed  # Structure preserved ✅
```

**Test Count**: 211 tests passing (171 property + 40 parser roundtrip)

---

### Phase 2: Projection Layer

**Goal**: Multi-target projection (CLI, Web) with density-awareness

**Deliverables**:
- [ ] `services/interactive-text/polynomial.py` — DocumentPolynomial (VIEWING, EDITING, SYNCING, CONFLICTING)
- [ ] `services/interactive-text/projectors/`
  - [ ] `cli.py` — Rich terminal rendering with hover affordances
  - [ ] `web.py` — React component projection interface
  - [ ] `json.py` — Semantic JSON output for agents
- [ ] `services/interactive-text/_tests/test_projectors.py`

**Key Pattern**: Observer-dependent rendering per AGENTESE principle
```python
# Different observers, different affordances
await render(doc, developer_observer)  # → Full interactive
await render(doc, reader_observer)     # → Minimal affordances
```

**Verification Criteria**:
```python
def test_observer_dependent():
    doc = load("spec.md")
    dev_view = render(doc, developer)
    reader_view = render(doc, reader)
    # Same content, different affordance density
    assert dev_view.affordance_count > reader_view.affordance_count
```

---

### Phase 3: Interaction Layer

**Goal**: File mutation, sheaf coherence, trace integration

**Deliverables**:
- [ ] `services/interactive-text/sheaf.py` — DocumentSheaf for multi-view coherence
- [ ] `services/interactive-text/mutations.py` — File mutation protocol
- [ ] `services/interactive-text/node.py` — AGENTESE node registration
- [ ] Wire to `world.trace.capture` for task completion witnesses
- [ ] Wire to DataBus for file change events
- [ ] `services/interactive-text/_tests/test_sheaf.py`

**Sheaf Condition**: Changes in any view MUST reflect in all others within 100ms. File is the single source of truth.

**Verification Criteria**:
```python
async def test_sheaf_coherence():
    doc = DocumentSheaf("test.md")
    view1 = doc.open_view("cli")
    view2 = doc.open_view("web")

    view1.toggle_task("task-1")
    await asyncio.sleep(0.1)

    assert view2.task_state("task-1") == "checked"
```

---

### Phase 4: Multimodal Layer

**Goal**: Image analysis, code execution, drag-drop protocols

**Deliverables**:
- [ ] `services/interactive-text/tokens/image.py` — LLM-assisted image analysis
- [ ] `services/interactive-text/sandbox.py` — Code block execution sandbox
- [ ] Graceful degradation for offline mode
- [ ] `services/interactive-text/_tests/test_multimodal.py`

**Graceful Degradation Pattern**:
```python
async def analyze_image(path: Path, observer: Observer) -> ImageAnalysis:
    try:
        return await llm_analyze(path, observer)
    except LLMUnavailable:
        return ImageAnalysis(
            rendered=True,
            analysis=None,
            hover_text="Analysis requires connection"
        )
```

**Verification Criteria**:
```python
def test_offline_image_analysis():
    with mock_llm_unavailable():
        doc = InteractiveDocument("doc_with_image.md")
        img = doc.tokens[0]

        assert img.rendered  # Image still shows
        assert img.analysis is None
        assert "requires connection" in img.hover_text
```

---

## Directory Structure

```
services/interactive-text/
├── __init__.py                 # Public API: InteractiveTextService
├── parser.py                   # Markdown → AST with token extraction
├── polynomial.py               # DocumentPolynomial (AD-002 pattern)
├── sheaf.py                    # DocumentSheaf coherence
├── mutations.py                # File mutation protocol
├── node.py                     # AGENTESE @node("self.document.interactive")
├── contracts.py                # Request/Response frozen dataclasses
├── tokens/                     # Six token types
│   ├── __init__.py
│   ├── base.py                 # SemanticToken protocol
│   ├── agentese_path.py
│   ├── task_checkbox.py
│   ├── image.py
│   ├── code_block.py
│   ├── principle_ref.py
│   └── requirement_ref.py
├── projectors/
│   ├── cli.py                  # Rich terminal rendering
│   ├── web.py                  # React interface
│   └── json.py                 # Semantic JSON
├── sandbox.py                  # Code execution sandbox
├── web/                        # Frontend components (if needed)
│   ├── components/
│   │   ├── InteractiveDocument.tsx
│   │   ├── TokenRenderer.tsx
│   │   └── AffordanceOverlay.tsx
│   └── hooks/
│       └── useInteractiveText.ts
└── _tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_tokens.py
    ├── test_polynomial.py
    ├── test_sheaf.py
    ├── test_projectors.py
    └── test_multimodal.py
```

---

## Dependencies

**Built Infrastructure (check before building)**:
- `agents/poly/` — PolyAgent for DocumentPolynomial
- `agents/sheaf/` — Sheaf for DocumentSheaf
- `protocols/agentese/` — For node registration
- `protocols/synergy/` — For DataBus events
- `services/witness/` — For trace capture

**DI Registration** (in `services/providers.py`):
```python
async def get_interactive_text_service() -> InteractiveTextService:
    return InteractiveTextService()

# Register in container:
container.register("interactive_text_service", get_interactive_text_service, singleton=True)
```

---

## Anti-Patterns (from spec Part VII)

| Anti-Pattern | Why Wrong | Correct Approach |
|--------------|-----------|------------------|
| Interactive-only content | File unreadable in plain editors | All content is valid markdown |
| Breaking markdown validity | Other tools can't parse | Use standard syntax only |
| Over-tokenization | Noise drowns signal | Tasteful > feature-complete |
| Stateful tokens | File not source of truth | State lives in file, not DB |
| Observer-independent rendering | Violates AGENTESE principle | Observer determines affordances |

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Roundtrip fidelity | 100% | `parse(render(parse(doc))) ≡ parse(doc)` |
| Sheaf coherence latency | < 100ms | Multi-view sync tests |
| Token recognition precision | 100% | No false positives in test corpus |
| Graceful degradation coverage | 100% | All LLM features have fallbacks |
| Polynomial law compliance | Pass | Identity and valid transitions |

---

## Voice Anchors

> *"Daring, bold, creative, opinionated but not gaudy"*

> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

> *"The persona is a garden, not a museum"*

Six tokens. No more. Curated, not catalogued.

---

## Next Steps

1. **Phase 1 First**: Recognition layer is foundational
2. **Test-First**: Write verification criteria tests before implementation
3. **Wire DI Early**: Register in providers.py during Phase 3
4. **CLI Projection First**: Aligns with Claude Code philosophy

---

*Plan created: 2025-12-21 | From spec: spec/protocols/interactive-text.md*
