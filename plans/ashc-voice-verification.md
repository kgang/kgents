# ASHC Phase 5: Voice Enforcement & Verification Tower

> *"All emitted text is blocked or rewritten if Anti-Sausage fails."*

**Parent**: `plans/ashc-master.md`
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md` §Voice Enforcement, §Verification Tower
**Related**: `spec/services/verification.md`
**Phase**: PLAN
**Effort**: ~2 sessions

---

## Purpose

Voice Enforcement ensures all ASHC outputs maintain Kent's authentic voice. The Verification Tower validates all categorical laws and provides proof-carrying artifacts.

Together they close the loop:
- **VoiceGate** → outputs feel authored, not automated
- **Verification Tower** → outputs are provably correct

---

## Part 1: Voice Enforcement (VoiceGate)

### Core Types (From Spec)

```python
@dataclass(frozen=True)
class VoiceGateResult:
    """Result of voice check."""
    score: float  # 0.0-1.0, threshold is 0.7
    violations: tuple[VoiceViolation, ...]
    suggestions: tuple[str, ...]

@dataclass(frozen=True)
class VoiceViolation:
    """A specific voice violation."""
    anchor: str  # Which voice anchor was violated
    text: str    # The offending text
    reason: str  # Why it fails

VoiceGate: Output -> VoiceGateResult
```

### Voice Anchors

From CLAUDE.md Anti-Sausage Protocol:

| Anchor | Use When |
|--------|----------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making aesthetic decisions |
| *"The Mirror Test"* | Evaluating if something feels right |
| *"Tasteful > feature-complete"* | Scoping work |
| *"The persona is a garden, not a museum"* | Discussing evolution vs. preservation |
| *"Depth over breadth"* | Prioritizing work |

### Implementation Tasks

#### Task 1: Voice Anchor Registry
**Checkpoint**: Anchors loaded and searchable

```python
# impl/claude/protocols/ashc/voice/anchors.py

@dataclass(frozen=True)
class VoiceAnchor:
    """A voice anchor from Kent's intent."""
    phrase: str
    context: str  # When to apply
    weight: float  # Importance (0.0-1.0)

VOICE_ANCHORS = (
    VoiceAnchor(
        phrase="Daring, bold, creative, opinionated but not gaudy",
        context="aesthetic_decisions",
        weight=1.0,
    ),
    VoiceAnchor(
        phrase="The Mirror Test: Does K-gent feel like me on my best day?",
        context="evaluation",
        weight=1.0,
    ),
    VoiceAnchor(
        phrase="Tasteful > feature-complete",
        context="scoping",
        weight=0.9,
    ),
    VoiceAnchor(
        phrase="The persona is a garden, not a museum",
        context="evolution",
        weight=0.8,
    ),
    VoiceAnchor(
        phrase="Depth over breadth",
        context="prioritization",
        weight=0.8,
    ),
)

def get_anchors_for_context(context: str) -> tuple[VoiceAnchor, ...]:
    """Get relevant anchors for a given context."""
    return tuple(a for a in VOICE_ANCHORS if a.context == context or context == "all")
```

#### Task 2: Voice Checker
**Checkpoint**: Text scored against anchors

```python
# impl/claude/protocols/ashc/voice/checker.py

async def check_voice(
    text: str,
    context: str = "all",
) -> VoiceGateResult:
    """
    Check text against voice anchors.

    Returns score, violations, and suggestions.
    """
    anchors = get_anchors_for_context(context)
    violations = []
    suggestions = []

    # 1. Check for anti-patterns
    anti_patterns = detect_anti_patterns(text)
    for pattern in anti_patterns:
        violations.append(VoiceViolation(
            anchor="anti_sausage",
            text=pattern.matched_text,
            reason=pattern.reason,
        ))

    # 2. Check for missing positive signals
    missing = check_missing_signals(text, anchors)
    for signal in missing:
        suggestions.append(signal.suggestion)

    # 3. Calculate score
    score = calculate_voice_score(text, anchors, violations)

    return VoiceGateResult(
        score=score,
        violations=tuple(violations),
        suggestions=tuple(suggestions),
    )

def detect_anti_patterns(text: str) -> list[AntiPattern]:
    """Detect text that violates voice anchors."""
    patterns = [
        AntiPattern(
            regex=r"\bsynergize\b",
            reason="Corporate jargon (synergize)",
        ),
        AntiPattern(
            regex=r"\bleverage\b",
            reason="Corporate jargon (leverage)",
        ),
        AntiPattern(
            regex=r"\bparadigm shift\b",
            reason="Buzzword (paradigm shift)",
        ),
        AntiPattern(
            regex=r"\bholistic\b",
            reason="Overused word (holistic)",
        ),
        AntiPattern(
            regex=r"(?i)\bwe believe\b",
            reason="Corporate speak (we believe)",
        ),
    ]
    return [p for p in patterns if re.search(p.regex, text)]
```

#### Task 3: Voice Rewriter
**Checkpoint**: Failing text can be rewritten

```python
# impl/claude/protocols/ashc/voice/rewriter.py

async def rewrite_for_voice(
    text: str,
    violations: tuple[VoiceViolation, ...],
    anchors: tuple[VoiceAnchor, ...],
) -> str:
    """
    Rewrite text to pass voice check.

    Uses LLM with voice anchors as constraints.
    """
    prompt = f"""
You are rewriting text to match Kent's voice.

VOICE ANCHORS (quote these when relevant):
{format_anchors(anchors)}

VIOLATIONS TO FIX:
{format_violations(violations)}

ORIGINAL TEXT:
{text}

Rewrite to:
- Fix all violations
- Match the voice anchors
- Keep the same meaning
- Be daring, bold, creative—not corporate

REWRITTEN TEXT:
"""

    rewritten = await logos.invoke(
        "concept.kgent.generate",
        L0_UMWELT,
        prompt=prompt,
    )

    return rewritten
```

#### Task 4: VoiceGate Integration
**Checkpoint**: All ASHC outputs pass through gate

```python
# impl/claude/protocols/ashc/voice/gate.py

class VoiceGate:
    """
    Gate that all ASHC outputs must pass.

    Blocks or rewrites text that fails voice check.
    """

    def __init__(self, threshold: float = 0.7, auto_rewrite: bool = True):
        self.threshold = threshold
        self.auto_rewrite = auto_rewrite

    async def check(self, text: str, context: str = "all") -> VoiceGateResult:
        """Check text against voice anchors."""
        return await check_voice(text, context)

    async def enforce(self, text: str, context: str = "all") -> str:
        """Enforce voice compliance. Returns text or rewritten version."""
        result = await self.check(text, context)

        if result.score >= self.threshold:
            return text

        if self.auto_rewrite:
            return await rewrite_for_voice(
                text,
                result.violations,
                get_anchors_for_context(context),
            )

        raise VoiceViolationError(result)
```

---

## Part 2: Verification Tower

### Core Types (From Spec)

```python
@dataclass(frozen=True)
class TraceWitness:
    """Constructive proof of behavioral correctness."""
    agent_path: str
    input_data: Any
    output_data: Any
    trace: ExecutionTrace
    proof_term: HoTTProof

@dataclass(frozen=True)
class VerificationGraph:
    """Graph representing logical derivations from principles to impl."""
    nodes: frozenset[GraphNode]
    edges: frozenset[DerivationEdge]
```

### Integration with Existing Infrastructure

The Verification Tower exists at `services/verification/` with 164 tests. ASHC integrates with:

```python
# Existing components
from services.verification.topology import MindMapTopology
from services.verification.generative_loop import GenerativeLoop
from services.verification.categorical_checker import CategoricalLawsEngine
from services.verification.trace_witness import TraceWitnessSystem
from services.verification.graph_engine import VerificationGraph
```

### Implementation Tasks

#### Task 5: ASHC-Verification Bridge
**Checkpoint**: Passes emit TraceWitnesses via existing system

```python
# impl/claude/protocols/ashc/verification/bridge.py

class ASHCVerificationBridge:
    """
    Bridge between ASHC passes and Verification Tower.

    Every pass emits TraceWitness.
    Tower validates categorical laws.
    """

    def __init__(self):
        from services.verification.trace_witness import TraceWitnessSystem
        from services.verification.categorical_checker import CategoricalLawsEngine

        self.witness_system = TraceWitnessSystem()
        self.laws_engine = CategoricalLawsEngine()

    async def record_pass(
        self,
        pass_name: str,
        input_data: Any,
        output_data: Any,
        trace: ExecutionTrace,
    ) -> TraceWitness:
        """Record a pass execution as a witness."""
        witness = TraceWitness(
            agent_path=f"concept.compiler.pass.{pass_name}",
            input_data=input_data,
            output_data=output_data,
            trace=trace,
            proof_term=self._generate_proof_term(pass_name, input_data, output_data),
        )
        await self.witness_system.record(witness)
        return witness

    async def verify_laws(self) -> LawVerificationResult:
        """Verify all categorical laws hold."""
        return await self.laws_engine.verify_all()

    def _generate_proof_term(
        self,
        pass_name: str,
        input_data: Any,
        output_data: Any,
    ) -> HoTTProof:
        """Generate HoTT proof term for pass."""
        # Construct proof that pass preserved structure
        return HoTTProof(
            source=input_data,
            target=output_data,
            path_type="transformation",
            witness=f"{pass_name}_applied",
        )
```

#### Task 6: Proof-Carrying Artifacts
**Checkpoint**: All artifacts include proofs

```python
# impl/claude/protocols/ashc/verification/artifacts.py

@dataclass(frozen=True)
class ProofCarryingArtifact:
    """An artifact with attached proofs."""
    artifact: Artifact
    witnesses: tuple[TraceWitness, ...]
    verification_summary: VerificationSummary

@dataclass(frozen=True)
class VerificationSummary:
    """Summary of verification for an artifact."""
    laws_checked: int
    laws_passed: int
    voice_score: float
    overall_valid: bool

async def attach_proofs(
    artifact: Artifact,
    witnesses: list[TraceWitness],
    voice_result: VoiceGateResult,
) -> ProofCarryingArtifact:
    """Attach proofs to an artifact."""
    return ProofCarryingArtifact(
        artifact=artifact,
        witnesses=tuple(witnesses),
        verification_summary=VerificationSummary(
            laws_checked=len(witnesses),
            laws_passed=len([w for w in witnesses if w.valid]),
            voice_score=voice_result.score,
            overall_valid=all(w.valid for w in witnesses) and voice_result.score >= 0.7,
        ),
    )
```

---

## File Structure

```
impl/claude/protocols/ashc/voice/
├── __init__.py
├── anchors.py          # Voice anchor registry (Task 1)
├── checker.py          # Voice checking (Task 2)
├── rewriter.py         # Voice rewriting (Task 3)
├── gate.py             # VoiceGate (Task 4)
├── _tests/
│   ├── test_anchors.py
│   ├── test_checker.py
│   ├── test_rewriter.py
│   └── test_gate.py

impl/claude/protocols/ashc/verification/
├── __init__.py
├── bridge.py           # Tower bridge (Task 5)
├── artifacts.py        # Proof-carrying (Task 6)
├── _tests/
│   ├── test_bridge.py
│   └── test_artifacts.py
```

---

## Quality Checkpoints

| Checkpoint | Command | Expected |
|------------|---------|----------|
| Anchors | `pytest test_anchors.py` | All 5 anchors loaded |
| Checker | `pytest test_checker.py` | Violations detected |
| Rewriter | `pytest test_rewriter.py` | Text rewritten |
| Gate | `pytest test_gate.py` | Threshold enforced |
| Bridge | `pytest test_bridge.py` | Witnesses recorded |
| Artifacts | `pytest test_artifacts.py` | Proofs attached |
| E2E Voice | `kg self.voice.check "text"` | Score returned |
| E2E Laws | `kg self.verification.verify_laws` | All PASS |

---

## User Flows

### Flow: Check Voice on Text

```bash
$ kg self.voice.check "We believe in leveraging synergies..."

┌─ VOICE CHECK ──────────────────────────────────────────┐
│                                                         │
│ Score: 0.3 ████░░░░░░░░░░░░░░░░ FAIL                   │
│                                                         │
│ Violations:                                             │
│   ✗ "we believe" — Corporate speak                     │
│   ✗ "leveraging" — Corporate jargon                    │
│   ✗ "synergies" — Buzzword                             │
│                                                         │
│ Suggestions:                                            │
│   • Use direct, opinionated language                   │
│   • Quote voice anchors when relevant                  │
│   • Ask: "Does this feel like Kent on his best day?"   │
│                                                         │
│ Threshold: 0.7 | Your score: 0.3                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Auto-Rewrite Failing Text

```bash
$ kg self.voice.rewrite "We believe in leveraging synergies to drive value."

Original (score: 0.3):
  "We believe in leveraging synergies to drive value."

Rewritten (score: 0.85):
  "The pieces compose naturally. That's the whole point—
   tasteful > feature-complete."

Violations fixed: 3
Anchors quoted: 1 ("Tasteful > feature-complete")
```

### Flow: View Verification Status

```bash
$ kg self.verification.manifest

┌─ VERIFICATION TOWER ───────────────────────────────────┐
│                                                         │
│ Categorical Laws:                                       │
│   ✓ Identity       (verified: 2025-12-20 14:32)        │
│   ✓ Associativity  (verified: 2025-12-20 14:32)        │
│   ✓ Functor        (verified: 2025-12-20 14:32)        │
│   ✓ Operad         (verified: 2025-12-20 14:32)        │
│   ✓ Sheaf Gluing   (verified: 2025-12-20 14:32)        │
│                                                         │
│ Trace Witnesses: 127 recorded (last 24h)               │
│ Proof-Carrying Artifacts: 23 generated                 │
│                                                         │
│ Voice Compliance:                                       │
│   Average score: 0.82                                   │
│   Violations fixed: 14                                  │
│   Rewrites performed: 7                                 │
│                                                         │
│ Overall Status: HEALTHY                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Compile with Full Verification

```bash
$ kg concept.compiler.compile spec/agents/new.md --verify

Compiling spec/agents/new.md...

Pass 1/5: ground
  Executing...     ████████████████████ done
  Voice check...   ████████████████████ 0.88 ✓
  Witness...       recorded

Pass 2/5: judge
  Executing...     ████████████████████ done
  Voice check...   ████████████░░░░░░░░ 0.62 REWRITING
  Rewritten...     ████████████████████ 0.84 ✓
  Witness...       recorded

... (remaining passes) ...

Verification Summary:
  Laws verified: 5/5
  Witnesses: 5
  Voice rewrites: 1
  Final score: 0.85

Artifacts generated with proofs attached. ✓
```

---

## UI/UX Considerations

### Voice Score Visualization

Show score as both number and bar:

```
Voice Score: 0.73 ████████████████░░░░ PASS (threshold: 0.70)

Breakdown:
  Anti-patterns avoided:  ██████████████████░░ 90%
  Anchor alignment:       ████████████░░░░░░░░ 60%
  Authenticity:           ████████████████░░░░ 80%
```

### Violation Highlighting

In terminal, highlight violations in the original text:

```
Input text with violations:

  "We [believe] in [leveraging] [synergies] to drive value for stakeholders."
       ^^^^^^^     ^^^^^^^^^^^  ^^^^^^^^^
       │           │            └─ Buzzword
       │           └─ Corporate jargon
       └─ Corporate speak

3 violations found. Score: 0.3
```

### Error Messages

Warm, sympathetic, per project aesthetic:

```
┌─ VOICE GATE BLOCKED ───────────────────────────────────┐
│                                                         │
│ This text doesn't quite sound like us. Let me help:    │
│                                                         │
│ The phrase "synergize our capabilities" feels corporate│
│ and distant. Kent's voice is direct and warm.          │
│                                                         │
│ Voice anchors to remember:                              │
│   • "Daring, bold, creative, opinionated but not gaudy"│
│   • "The persona is a garden, not a museum"            │
│                                                         │
│ Would you like me to rewrite this? [Y/n]               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Laws/Invariants

### Voice Invariance (From Spec)
```
∀ generated text T:
  voice_gate(T).score >= 0.7
```

All outputs MUST pass voice check.

### Proof-Carrying Law (From Spec)
```
∀ pass P, input I:
  P(I) = (output O, witness W)
  verify(W) == true
```

Every pass emits a valid witness.

### Witness Completeness
```
∀ artifact A:
  A.witnesses.count >= 1
```

No artifact without at least one witness.

---

## Integration Points

| System | Integration |
|--------|-------------|
| **K-gent** | Voice anchors from persona |
| **Verification Tower** | Existing 164-test infrastructure |
| **Pass Operad** | Witnesses emitted per pass |
| **AGENTESE** | `self.voice.*`, `self.verification.*` |

---

## Flexibility Points

| Fixed | Flexible |
|-------|----------|
| 0.7 threshold | Adjustable per section |
| 5 core anchors | Additional custom anchors |
| Auto-rewrite option | Can be disabled |
| Witness format | Content details |

---

## Testing Strategy

### Unit Tests
- Each anchor detected correctly
- Anti-patterns caught
- Rewriter produces higher-scoring text
- Gate enforces threshold

### Property Tests
```python
@given(st.text())
async def test_rewrite_improves_score(text):
    """Rewriting never makes score worse."""
    original = await check_voice(text)
    if original.score < 0.7:
        rewritten = await rewrite_for_voice(text, original.violations, VOICE_ANCHORS)
        new_result = await check_voice(rewritten)
        assert new_result.score >= original.score
```

### Integration Tests
- Full pass with voice check
- Witness recording flow
- Proof-carrying artifact generation

---

## Success Criteria

✅ Voice anchors loaded from CLAUDE.md
✅ Anti-patterns detected in text
✅ Rewriter improves failing text
✅ Gate enforces 0.7 threshold
✅ Witnesses recorded for all passes
✅ Proofs attached to artifacts
✅ `kg self.voice.check` works
✅ `kg self.verification.verify_laws` shows all PASS

---

## Dependencies

### From Phase 4
- Bootstrap supplanting complete
- Artifacts being generated

### Existing Infrastructure
- `services/verification/` — 164 tests
- `protocols/agentese/contexts/self_voice.py` — VoiceGate stub
- CLAUDE.md — Voice anchors

---

## Full Loop Complete

After Phase 5, ASHC is complete:

```
Spec → L0 Parse → Pass Operad → Grammar Validate → Bootstrap Compile
    → VoiceGate → Verification → Proof-Carrying Artifacts
                                              ↓
    ←←←←←←←←←←← Traces ←←←←←←←←←←←←←←←←←←←←←←
```

The generative loop is closed. Kent writes intent, receives verified artifacts, traces refine the spec.

---

*"The voice that speaks itself is the voice that knows itself."*
