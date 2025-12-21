# Executable Specifications: Specs That Verify Themselves

> *"A spec that can't run itself is just a wish."*

---

## The Vision

Specifications contain **runnable assertions** that verify themselves against the implementation. The gap between "what we said" and "what we built" becomes measurable, traceable, and self-healing.

```markdown
## Requirement [R2.1]: Brain Capture

Given a memory string, `self.brain.capture` should:
- [x] Store in vector database        <!-- ✅ test_brain.py::test_capture_stores -->
- [x] Return a MemoryID               <!-- ✅ Type verified: MemoryID -->
- [ ] Emit MEMORY_CAPTURED event      <!-- ❌ No evidence found -->

### Verification Block

```python
# EXECUTABLE: This block runs against the live system
from services.brain import Brain

async def verify_r2_1():
    brain = Brain()
    result = await brain.capture("test memory")

    assert result.id is not None, "Must return MemoryID"
    assert await brain.exists(result.id), "Must persist to storage"

    # Returns: ✅ PASS (0.003s)
```

### Laws (Auto-Extracted)

```
Law 1: capture(x).id ≠ capture(y).id for x ≠ y  <!-- Uniqueness -->
Law 2: surface(capture(x).id) ≈ x               <!-- Roundtrip -->
```
```

---

## Synergies with Recent Work

### 1. ASHC (Agentic Self-Hosting Compiler)

**Location**: `spec/agents/ashc/`, `services/verification/`

ASHC Phase 5 already has:
- **SpecParser**: Extracts laws from markdown via pattern matching
- **Bootstrap Verification**: Compares generated code against spec
- **Isomorphism Checking**: Behavioral equivalence, not textual

**Synergy**: SpecParser can extract verification blocks. ASHC's law verification becomes spec verification.

```python
# From services/verification/ashc/bootstrap.py
class SpecParser:
    """Extracts laws and requirements from spec markdown."""

    def extract_laws(self, spec_text: str) -> list[Law]:
        # Pattern: "Law N: <expression>"
        ...

    # NEW: Extract verification blocks
    def extract_verification_blocks(self, spec_text: str) -> list[VerificationBlock]:
        # Pattern: ```python\n# EXECUTABLE: ...```
        ...
```

### 2. Living Docs Reference Generation

**Location**: `services/living_docs/`, `plans/living-docs-reference-generation.md`

Living Docs Phase 4-5 already has:
- **TeachingCollector**: Extracts "gotchas" from code
- **Evidence Verification**: Links to test files
- **HydrationContext**: Surfaces relevant gotchas for tasks

**Synergy**: Living Docs evidence linking + executable specs = bi-directional traceability.

```
Spec [R2.1] ────evidence────▶ test_brain.py::test_capture
    │                              │
    │                              │
    └───────verifies───────────────┘
```

### 3. Witness Service

**Location**: `services/witness/`, `spec/agents/witness.md`

Witness already has:
- **Mark**: Atomic audit unit (every action traceable)
- **Walk**: Session trace (anchored to Forest plans)
- **Playbook**: Lawful workflow (gated by Grant)

**Synergy**: Verification runs create Marks. Spec status is a Walk. Requirement satisfaction is a Playbook.

```python
# Verification creates audit trail
@playbook("spec.verify")
async def verify_requirement(req_id: str) -> VerificationResult:
    mark = Mark.create(origin="spec.verify", payload={"req": req_id})

    result = await run_verification_block(req_id)

    mark.complete(status="pass" if result.passed else "fail")
    return result
```

### 4. Interactive Text (This Session)

**Location**: `services/interactive_text/`, `protocols/agentese/projection/tokens_to_scene.py`

Interactive Text provides:
- **RequirementRef token**: `[R2.1]` recognized and interactive
- **TaskCheckbox token**: `- [x]` with toggle affordance
- **CodeBlock token**: With "run" affordance

**Synergy**: Requirement badges show verification status. Code blocks execute. Task checkboxes update on verification.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXECUTABLE SPECIFICATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  spec/requirements/brain.md                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ ## [R2.1] Brain Capture                                             │    │
│  │                                                                      │    │
│  │ - [x] Store in vector database     ◀── Evidence: test_capture.py   │    │
│  │ - [ ] Emit MEMORY_CAPTURED         ◀── No evidence found           │    │
│  │                                                                      │    │
│  │ ```python                                                           │    │
│  │ # EXECUTABLE                                                        │    │
│  │ result = await brain.capture("test")                                │    │
│  │ assert result.id is not None                                        │    │
│  │ ```                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  SpecParser (from ASHC)                                             │    │
│  │  - Extract requirements                                              │    │
│  │  - Extract verification blocks                                       │    │
│  │  - Extract laws                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│              ┌───────────────┼───────────────┐                              │
│              ▼               ▼               ▼                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │ Evidence      │  │ Verification  │  │ Law           │                   │
│  │ Linker        │  │ Runner        │  │ Checker       │                   │
│  │ (Living Docs) │  │ (WASM/Local)  │  │ (ASHC)        │                   │
│  └───────────────┘  └───────────────┘  └───────────────┘                   │
│              │               │               │                              │
│              └───────────────┼───────────────┘                              │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Witness (Mark/Walk/Playbook)                                        │    │
│  │  - Audit trail for every verification                                │    │
│  │  - Walk shows spec evolution                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Interactive Text Tokens                                             │    │
│  │  - [R2.1] badge: ✅ 2/3 verified                                     │    │
│  │  - [ ] checkbox: updates on verification                            │    │
│  │  - Code block: "Run" button executes                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Verification Block Extraction
- Extend SpecParser to recognize `# EXECUTABLE` code blocks
- Create `VerificationBlock` dataclass with code, requirements, expected outcome
- Store in verification registry

### Phase 2: Evidence Linking
- Extend Living Docs to link `[RX.Y]` to test files
- Bidirectional: spec → tests, tests → spec
- Surface in `kg docs hydrate` output

### Phase 3: Verification Runner
- WASM sandbox for untrusted code (from Foundry)
- Local runner for trusted code
- Results stored as Marks

### Phase 4: Interactive Rendering
- RequirementRef token shows verification status
- Code blocks have "Run" affordance
- Real-time updates via SSE

### Phase 5: Continuous Verification
- CI runs all verification blocks
- Spec drift detection (impl changed, spec didn't)
- Auto-generated PR comments with status

---

## Open Questions

1. **Sandboxing**: How to safely run verification blocks? WASM? Docker? Restricted Python?

2. **Staleness**: How often should verification run? On every view? Cached with TTL?

3. **Partial Verification**: What if only some assertions pass? Show partial status?

4. **Human vs Machine**: Should humans be able to mark requirements as verified manually?

5. **Versioning**: When spec changes, do old verifications invalidate?

---

## Research Cues

### Literate Programming
- **Knuth's WEB**: Original vision of code + documentation interleaved
- **Jupyter Notebooks**: Executable documents, but not specs
- **Org-mode Babel**: Emacs literate programming with execution
- 🔍 *Search: "literate programming modern implementations 2024"*

### Specification by Example
- **Cucumber/Gherkin**: Given/When/Then executable specs
- **Concordion**: Specs in HTML that run
- **Gauge**: Markdown-based executable specs
- 🔍 *Search: "specification by example tools comparison"*

### Property-Based Testing
- **Hypothesis**: Generate test cases from properties
- **QuickCheck**: Original Haskell implementation
- **Laws as Properties**: Category laws as testable properties
- 🔍 *Search: "property based testing specifications"*

### Formal Methods (Lightweight)
- **Alloy**: Lightweight formal modeling
- **TLA+**: Temporal logic specs (used by AWS)
- **Design by Contract**: Eiffel's approach
- 🔍 *Search: "lightweight formal methods industry adoption"*

---

## Maximum Value Opportunities

### 1. Spec Coverage Metrics
Like code coverage, but for specs. "80% of requirements have verified evidence."

### 2. Spec Drift Detection
CI detects when implementation changes but spec doesn't update. "Warning: `brain.capture` signature changed but [R2.1] not updated."

### 3. Onboarding Acceleration
New developers read specs that prove themselves. No "is this still accurate?" anxiety.

### 4. Audit Compliance
Witness trail proves when/how each requirement was verified. Compliance as a side effect.

### 5. AI Spec Generation
LLM generates verification blocks from natural language requirements. Human reviews, system executes.

---

## Voice Anchors

> *"Daring, bold, creative, opinionated but not gaudy"* — Executable specs are bold. They make claims and prove them.

> *"The Mirror Test"* — Does the spec reflect reality? Now we can measure.

> *"Tasteful > feature-complete"* — Start with Phase 1-2. Don't boil the ocean.

---

*Created: 2025-12-21 | Building on: ASHC, Living Docs, Witness, Interactive Text*
*Next: Research Cucumber/Gauge patterns, prototype SpecParser extension*
