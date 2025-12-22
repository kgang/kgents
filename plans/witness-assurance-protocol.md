# Witness Assurance Protocol: Total Provenance from Prompt to Proof

> *"The proof IS the decision. The mark IS the witness. Every line of code has a genealogy."*

**Status:** Ready for Implementation
**Priority:** High
**Estimated Effort:** 8-10 sessions
**Dependencies:** Witness (98%), Typed-Hypergraph (100%), Trail Protocol (64 tests)
**Heritage:** GSN, Toulmin, PROV-O, IBIS, Tufte, TextGRAD, DSPy, Promptbreeder

---

## Executive Summary

This plan synthesizes three visions:
1. **Witness Self-Correction** (plans/witness-self-correction.md) — supersedes, decay, conflict detection, reflection loops
2. **Spec Witness Assurance Graph** (brainstorming/2025-12-22-spec-witness-vision-refined.md) — evidence ladder, PROV-O provenance, ledger-first UI
3. **Prompt Archaeology** (brainstorming/2025-12-22-prompt-archaeology.md) — total provenance from prompt to artifact, prompt evolution, self-improvement loops

**The Synthesis:** Spec Witness is not a dashboard. It's a living assurance case with **total provenance**—from the prompt that generated code to the proof that verifies it. We don't build a new SpecGraph—we project the Typed-Hypergraph with Witness marks AND prompt lineage as evidence nodes.

**The Core Insight:** Evidence is stratified. Marks are not proofs. Tests are not proofs. TraceWitness is the runtime proof primitive. ASHC provides the confidence economics. **And beneath it all: the prompts that generated every artifact.** The Typed-Hypergraph already has the edges—we just need to make them visible AND traceable to their generative origins.

---

## Critical Audit of Component Plans

### From witness-self-correction.md (Preserved)
| Strength | Gap Identified | Resolution |
|----------|----------------|------------|
| SUPERSEDES relation | No evidence stratification | Add Evidence Ladder (L-2 to L3) |
| Confidence decay | Decay without economic grounding | Integrate ASHC bet/settlement |
| Conflict detection | Keyword-only, no semantic | Use embeddings + LLM reranking |
| Reflection loop | Meta-marks without structure | Use Toulmin argument structure |
| Teaching promotion | Crystal→Brain only | Trail→Witness→Crystal→Teaching chain |

### From Spec Witness Assurance Graph (Preserved)
| Strength | Gap Identified | Resolution |
|----------|----------------|------------|
| Evidence Ladder | No generative provenance | Add L-2 PromptAncestor |
| PROV-O alignment | Missing prompt entities | Extend Entity/Activity vocabulary |
| Ledger-first UI | Static view | Add evolution tracking |
| WITNESSED criteria | Implementation-focused | Add prompt lineage requirement |

### From Prompt Archaeology (NEW)
| Strength | Gap Identified | Resolution |
|----------|----------------|------------|
| Total provenance | No existing infrastructure | Build PromptAncestor model |
| Prompt evolution | Standalone concept | Integrate with confidence decay |
| Fitness metrics | Unclear | Use test pass rate + correction rate + crystal formation |
| Self-improvement | Manual | Automatic TextGRAD-style evolution |

---

## The Evidence Ladder (Complete)

Evidence is stratified. Each level unlocks trust:

| Level | Name | Source | Meaning | kgents Artifact |
|------:|------|--------|---------|-----------------|
| **L-2** | **PromptAncestor** | LLM invocation | The generative thought | `PromptAncestor` (NEW) |
| L-1 | TraceWitness | Runtime trace | Actual behavior observed | `TraceWitness` from verification |
| L0 | Mark | Human attention | "This matters" | `WitnessMark` via `km` |
| L1 | Test | Automated check | Repeatable claim | Test artifact + hash |
| L2 | Proof | Formal discharge | Law verified | ASHC proof ID |
| L3 | Economic Bet | Credibility stake | Confidence calibration | ASHC bet + settlement |

### Evidence Rules

1. **Prompt Lineage Required for Proofs:** An artifact cannot reach L2 (Proof) status unless its prompt lineage is fully captured.

2. **WITNESSED Requirements:** A spec cannot be WITNESSED without:
   - ≥1 L-1 TraceWitness OR ≥1 L1 test artifact
   - ≥1 L0 mark or decision referencing the spec
   - ≥1 `implements` hyperedge to implementation file
   - ≥1 L-2 PromptAncestor for AI-generated implementations

3. **Evolution Requirement:** A prompt with fitness < 0.7 must be evolved or justified.

---

## The Unified Provenance Model (PROV-O Extended)

Instead of bespoke node types, use the PROV-O core extended with prompt lineage:

```
Entity:   Spec, ImplementationFile, TestArtifact, ProofArtifact, Crystal, Mark, PromptAncestor
Activity: Decision, TestRun, TraceCapture, Crystallize, Compile, PromptInvocation, PromptEvolution
Agent:    HumanObserver, LLM, ToolingAgent, Service, ClaudeSession
```

### Typed-Hypergraph Edge Extensions

| Edge Type | From | To | Already In Hypergraph |
|-----------|------|----|-----------------------|
| `implements` | ImplementationFile | Spec | ✅ Yes |
| `tests` | TestFile | ImplementationFile | ✅ Yes |
| `supports` | Evidence | Claim | ✅ Yes (§4.4) |
| `refutes` | Evidence | Claim | ✅ Yes (§4.4) |
| `derived_from` | Crystal | Mark/Trace | ✅ Yes (§4.5) |
| `supersedes` | Mark | Mark | ⚠️ Add to Trail |
| **`generated_by`** | Artifact | PromptAncestor | 🆕 NEW |
| **`evolved_from`** | PromptAncestor | PromptAncestor | 🆕 NEW |
| **`contributed_to`** | PromptAncestor | Crystal | 🆕 NEW |

**Key Decision:** Spec Witness is a **projection** of the Typed-Hypergraph. Prompt lineage extends the graph downward (L-2) without breaking the existing structure.

---

## The Unified Loop

```
Prompt ──► Invocation ──► Artifact ──► Mark ──► Crystal ──► Teaching
   ↑                                                              ↓
   └──────────────────── Feedback/Evolution ──────────────────────┘
```

**Key Insight:** Self-correction becomes *self-improvement* when prompts evolve based on the correction history.

---

## Implementation Phases

### Phase 1: Evidence Ladder Infrastructure (1 session)

**File:** `impl/claude/services/witness/evidence.py` (NEW)

```python
from enum import IntEnum
from dataclasses import dataclass
from datetime import datetime
from typing import Any

class EvidenceLevel(IntEnum):
    """Evidence stratification levels."""
    PROMPT = -2      # L-2: PromptAncestor (generative origin)
    TRACE = -1       # L-1: TraceWitness (runtime observation)
    MARK = 0         # L0: Human attention mark
    TEST = 1         # L1: Automated test
    PROOF = 2        # L2: Formal proof (ASHC)
    BET = 3          # L3: Economic stake (ASHC bet)

@dataclass(frozen=True)
class Evidence:
    """Unified evidence artifact."""
    id: str
    level: EvidenceLevel
    source_type: str  # "prompt", "trace", "mark", "test", "proof", "bet"
    target_spec: str | None
    content_hash: str
    created_at: datetime
    created_by: str
    metadata: dict[str, Any]

    @property
    def is_generative(self) -> bool:
        return self.level == EvidenceLevel.PROMPT

    @property
    def is_runtime(self) -> bool:
        return self.level <= EvidenceLevel.MARK

    @property
    def is_automated(self) -> bool:
        return self.level >= EvidenceLevel.TEST
```

**File:** `impl/claude/services/witness/status.py` (NEW)

```python
from enum import Enum

class SpecStatus(Enum):
    """Status of a spec in the assurance case."""
    UNWITNESSED = "unwitnessed"
    IN_PROGRESS = "in_progress"
    WITNESSED = "witnessed"
    CONTESTED = "contested"
    SUPERSEDED = "superseded"

async def compute_status(
    spec_path: str,
    evidence: list[Evidence],
    hypergraph: ContextGraph,
) -> SpecStatus:
    """Compute the witness status of a spec."""
    has_trace_or_test = any(
        e.level in (EvidenceLevel.TRACE, EvidenceLevel.TEST)
        for e in evidence
    )
    has_mark = any(e.level == EvidenceLevel.MARK for e in evidence)
    has_refutation = any(e.metadata.get("relation") == "refutes" for e in evidence)

    node = ContextNode(path=f"world.spec.{spec_path}")
    implements = await hypergraph.follow_edge(node, "implemented_by")
    has_implementation = len(implements) > 0

    if has_refutation:
        return SpecStatus.CONTESTED
    if has_trace_or_test and has_mark and has_implementation:
        return SpecStatus.WITNESSED
    if has_mark or has_implementation:
        return SpecStatus.IN_PROGRESS
    return SpecStatus.UNWITNESSED
```

### Phase 2: SUPERSEDES and Self-Correction (0.5 session)

From witness-self-correction.md — add SUPERSEDES link relation and WitnessSupersession model.

### Phase 3: Prompt Archaeology — Data Model (1.5 sessions)

**File:** `impl/claude/models/prompt_archaeology.py` (NEW)

```python
class PromptAncestor(Base):
    """The generative prompt that created artifacts."""
    __tablename__ = "prompt_ancestors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(32))
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    context_hash: Mapped[str] = mapped_column(String(64))
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    parent_prompts: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    artifacts_generated: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    marks_emitted: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    crystals_contributed: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    fitness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fitness_computed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ArtifactProvenance(Base):
    """Provenance record for each artifact."""
    __tablename__ = "artifact_provenance"

    id: Mapped[int] = mapped_column(primary_key=True)
    artifact_path: Mapped[str] = mapped_column(String(512), index=True, unique=True)
    primary_prompt_id: Mapped[str] = mapped_column(String(64), ForeignKey("prompt_ancestors.id"))
    contributing_prompts: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    generation_ratio: Mapped[float] = mapped_column(Float, default=1.0)
    human_edits: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_prompt_touch: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PromptEvolution(Base):
    """Tracks prompt improvement via TextGRAD/DSPy."""
    __tablename__ = "prompt_evolutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_prompt_id: Mapped[str] = mapped_column(String(64), ForeignKey("prompt_ancestors.id"))
    evolved_prompt_id: Mapped[str] = mapped_column(String(64), ForeignKey("prompt_ancestors.id"))
    fitness_delta: Mapped[float] = mapped_column(Float)
    evolution_method: Mapped[str] = mapped_column(String(32))  # "textgrad" | "manual" | "compression"
    feedback_source: Mapped[str] = mapped_column(Text)
    evolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

### Phase 4: Prompt Capture Service (1.5 sessions)

**File:** `impl/claude/services/witness/prompt_capture.py` (NEW)

```python
class PromptCaptureService:
    """Automatically capture prompts during AGENTESE invocations."""

    async def capture_prompt(
        self,
        content: str,
        model: str,
        temperature: float,
        context: str | None = None,
    ) -> str:
        """Capture a prompt invocation, return prompt_id."""
        prompt_id = f"prompt-{hashlib.sha256(content.encode()).hexdigest()[:12]}"
        # ... persist and return prompt_id

    async def link_artifact(self, prompt_id: str, artifact_path: str) -> None:
        """Link an artifact to its generating prompt."""
        # ... create or update artifact provenance
```

### Phase 5: Confidence Decay with Prompt Fitness (1 session)

Extend confidence decay to include prompt fitness:

```python
def decayed_confidence(
    crystal: Crystal,
    now: datetime | None = None,
    contradiction_count: int = 0,
    reference_count: int = 0,
    ashc_resolution: float | None = None,
    has_proof: bool = False,
    prompt_fitness: float | None = None,  # NEW
    config: DecayConfig = DEFAULT_DECAY_CONFIG,
) -> float:
    """Calculate confidence with decay and prompt fitness."""
    if has_proof and config.proof_lock:
        return 1.0

    # ... base decay ...

    # Prompt fitness adjustment (NEW)
    if prompt_fitness is not None:
        decayed = decayed * (0.7 + 0.3 * prompt_fitness)

    # ASHC bet resolution
    if ashc_resolution is not None:
        decayed = decayed * (1 - config.bet_resolution_weight) + ashc_resolution * config.bet_resolution_weight

    return max(config.floor, min(1.0, decayed))
```

### Phase 6: Prompt Evolution Service (1.5 sessions)

**File:** `impl/claude/services/witness/prompt_evolution.py` (NEW)

```python
class PromptEvolutionService:
    """Evolve prompts based on feedback."""

    async def compute_fitness(self, prompt_id: str) -> float:
        """
        Compute fitness = weighted combination of:
        - Test pass rate (40%)
        - Correction rate (30%) — lower is better
        - Crystal formation (20%)
        - Time stability (10%)
        """

    async def evolve_prompt(self, prompt_id: str) -> str | None:
        """Apply TextGRAD-style evolution to a prompt."""
        fitness = await self.compute_fitness(prompt_id)
        if fitness >= 0.8:
            return None  # No evolution needed

        feedback = await self._gather_feedback(prompt_id)
        gradient = await self._llm_invoke("Analyze prompt problems", ...)
        evolved_content = await self._llm_invoke("Improve based on analysis", ...)

        return await self._save_evolved_prompt(evolved_content, prompt_id)
```

### Phase 7: Hypergraph Projection & Ledger UI (1.5 sessions)

**File:** `impl/claude/protocols/cli/handlers/spec_witness.py` (NEW)

```python
def cmd_ledger(args: list[str]) -> int:
    """Show spec assurance ledger with evidence ladder columns."""
    # Dense table: Spec | L-2 | L-1 | L0 | L1 | L2 | Status | Rebuttals
```

**File:** `impl/claude/protocols/cli/handlers/prompt_archaeology.py` (NEW)

```python
def cmd_show(args: list[str]) -> int:
    """Show prompt lineage for an artifact."""

def cmd_orphans(args: list[str]) -> int:
    """List artifacts without prompt lineage."""

def cmd_fitness(args: list[str]) -> int:
    """Show fitness scores for recent prompts."""

def cmd_evolve(args: list[str]) -> int:
    """Trigger evolution for a low-fitness prompt."""
```

### Phase 8: Semantic Conflict Detection (1 session)

Upgrade conflict detection to use embeddings + LLM reranking (from witness-self-correction.md).

### Phase 9: Toulmin Reflection Structure (0.5 session)

Crystallization reflection with Claim/Warrant/Evidence/Qualifier/Rebuttal structure.

### Phase 10: Agent Training & Documentation (0.5 session)

Update CLAUDE.md and create slash commands.

---

## Implementation Order Summary

| Phase | Description | Sessions | Dependencies |
|-------|-------------|----------|--------------|
| **1** | Evidence Ladder Infrastructure | 1 | None |
| **2** | SUPERSEDES Self-Correction | 0.5 | None |
| **3** | Prompt Archaeology Data Model | 1.5 | Phase 1 |
| **4** | Prompt Capture Service | 1.5 | Phase 3 |
| **5** | Confidence Decay + Prompt Fitness | 1 | Phase 1, 4 |
| **6** | Prompt Evolution Service | 1.5 | Phase 4, 5 |
| **7** | Hypergraph Projection & Ledger UI | 1.5 | Phase 1, 4 |
| **8** | Semantic Conflict Detection | 1 | Phase 2 |
| **9** | Toulmin Reflection | 0.5 | Phase 2 |
| **10** | Agent Training | 0.5 | All |

**Total:** 8-10 sessions

---

## Verification Checklist

**Evidence Ladder:**
- [ ] `EvidenceLevel` enum with L-2 to L3
- [ ] `compute_status()` returns WITNESSED correctly
- [ ] WITNESSED requires prompt lineage for AI-generated code

**Self-Correction:**
- [ ] `km --supersedes` creates SUPERSEDES link
- [ ] `kg witness show --exclude-superseded` works
- [ ] Conflict detection uses embeddings

**Prompt Archaeology:**
- [ ] `PromptAncestor` model with all fields
- [ ] `ArtifactProvenance` tracks generation ratio
- [ ] `kg prompt show <artifact>` shows lineage
- [ ] `kg prompt orphans` lists untracked artifacts
- [ ] `kg prompt evolve <prompt-id>` triggers evolution

**Integration:**
- [ ] Confidence decay includes prompt fitness
- [ ] Crystals include `prompt_ancestry`
- [ ] Ledger shows L-2 column
- [ ] ASHC proofs include prompt lineage

---

## Files Summary

| File | Type | Phase |
|------|------|-------|
| `services/witness/evidence.py` | **NEW** | 1 |
| `services/witness/status.py` | **NEW** | 1 |
| `services/witness/mark.py` | Modify | 2 |
| `models/witness.py` | Modify | 2 |
| `models/prompt_archaeology.py` | **NEW** | 3 |
| `services/witness/prompt_capture.py` | **NEW** | 4 |
| `services/witness/crystal.py` | Modify | 5 |
| `services/witness/prompt_evolution.py` | **NEW** | 6 |
| `services/witness/spec_projection.py` | **NEW** | 7 |
| `protocols/cli/handlers/spec_witness.py` | **NEW** | 7 |
| `protocols/cli/handlers/prompt_archaeology.py` | **NEW** | 7 |
| `services/witness/conflict.py` | Modify | 8 |
| `services/witness/crystallizer.py` | Modify | 9 |
| `CLAUDE.md` | Modify | 10 |
| `.claude/commands/correct.md` | **NEW** | 10 |

---

## Constitutional Alignment

| Article | How This Plan Embodies It |
|---------|---------------------------|
| **I. Symmetric Agency** | Same evidence protocol for Kent and AI |
| **II. Adversarial Cooperation** | Conflict detection enables challenge |
| **III. Supersession Rights** | SUPERSEDES with evidence trail |
| **V. Trust Accumulation** | Evidence ladder = earned trust |
| **VI. Fusion as Goal** | Toulmin reflection captures synthesis |
| **VII. Amendment** | Prompt evolution = self-improvement |

---

## The Mirror Test

> *"Does this make kgents more honest, or just more impressive?"*

**Honest if:**
- We can trace any line of code to the thought that created it
- We can see when prompts degrade and need evolution
- We can prove artifact quality with prompt lineage
- We surface orphans (untracked code) as a problem, not hide them

**Impressive but dishonest if:**
- We only capture prompts for new code, not existing
- We hide low-fitness prompts instead of evolving them
- We treat prompt archaeology as decorative rather than functional

---

*"The proof IS the decision. The mark IS the witness. The prompt IS the genealogy."*

**Filed:** 2025-12-22
**Supersedes:** plans/witness-self-correction.md (preserves all, extends with Prompt Archaeology)
**Heritage:** Agent-as-Witness, Typed-Hypergraph, Trail Protocol, Toulmin, GSN, PROV-O, ASHC, TextGRAD, DSPy, Promptbreeder
