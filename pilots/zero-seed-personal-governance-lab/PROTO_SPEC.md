# Zero Seed Personal Governance Lab

Status: **production**

> *"Your axioms are not what you think they are. Galois loss reveals them."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L9)** — complete set
- **Implement ALL QAs (QA-1 through QA-9)** — complete set
- **Real Galois fixed-point detection** — actual semantic analysis, not mock
- **Real amendment process** — functional constitutional evolution
- **Emit actual witness marks** — not just capture intent

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact |
|-----------|--------|
| **FC-1** Axiom discovery returns empty for valid corpus | Core feature broken |
| **FC-2** Universal values (love, courage) rejected by threshold | L7 violated |
| **FC-3** API errors display as raw JSON objects | L9 violated |
| **FC-4** Frontend/backend contract mismatch at runtime | L8 violated |
| **FC-5** Amendment process doesn't persist changes | Evolution impossible |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Demo corpus produces 3-5 discoverable axioms | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | Contract coherence tests pass (L8) | Yes |
| **QG-5** | Error normalization verified (no raw objects) | Yes |
| **QG-6** | Universal values passlist functional (L7) | Yes |

---

## Narrative

Most people have never articulated their core values. They operate from implicit axioms—beliefs so fundamental they're invisible. This pilot makes value discovery accessible: the system surfaces your actual fixed points (what survives restructuring unchanged) and helps you evolve them intentionally through a personal constitution.

## Personality Tag

*Value articulation as archaeology, not construction. You're not creating values—you're discovering what was already there, then choosing whether to keep it.*

## Objectives

- Surface **implicit axioms** from personal writings, decisions, and witness traces without forcing premature articulation.
- Enable **constitutional evolution** through a formal amendment process that respects the Disgust Veto.
- Provide **coherence feedback** via Galois loss, showing where stated values and witnessed behavior diverge.
- Democratize **principled self-governance** to anyone, not just philosophers.

## Epistemic Commitments

- Axioms are **discovered, not declared**. Fixed-point detection (L < 0.05) identifies what you actually believe, not what you say you believe.
- Personal constitutions are **living documents**. Amendment G grammar applies: coherent evolution, not arbitrary change.
- The system **augments judgment, never replaces it**. ETHICAL floor (Amendment A) is non-negotiable.
- Contradictions are **surfaced without shame**. Super-additive loss detection shows conflicts; the user decides resolution.
- The Disgust Veto is **absolute**. If it feels wrong, no argument or evidence can override.

## Laws

- **L1 Axiom Discovery Law**: Fixed points (L < 0.05) must surface before constitution drafting begins. Discovery precedes articulation.
- **L2 Amendment Coherence Law**: Any constitutional change must pass through the pilot law grammar (Amendment G schemas). No arbitrary edits.
- **L3 Drift Visibility Law**: When Galois loss between stated values and witnessed behavior exceeds threshold, the drift must surface. No hiding from yourself.
- **L4 Veto Preservation Law**: The Disgust Veto cannot be argued away. Somatic rejection is an absolute floor.
- **L5 Evolution Traceability Law**: Every constitutional amendment links to witness marks that justify the change. No orphan amendments.
- **L6 Request Model Law**: All API endpoints accepting complex inputs MUST use Pydantic request models. No bare parameters for JSON bodies. This prevents FastAPI validation errors from leaking as unhandled objects.
- **L7 Semantic Baseline Law**: Universal human values (love, honesty, courage, compassion, integrity, etc.) MUST always qualify as acceptable axiom candidates regardless of Galois loss. The loss threshold gates "true fixed points" but basic values are pre-approved for constitution inclusion.
- **L8 Contract Coherence Law**: API contracts have a single source of truth in `shared-primitives/contracts/`. Both frontend and backend verify against it. See `pilots/CONTRACT_COHERENCE.md`.
- **L9 Error Normalization Law**: API error responses MUST be normalized to strings before rendering. FastAPI validation errors (`{type, loc, msg}[]`) must be extracted into human-readable messages.

## Qualitative Assertions

- **QA-1** Value discovery should feel like **recognition, not invention**. "Oh, that's what I actually believe."
- **QA-2** The amendment process should feel **ceremonial but not burdensome**. Important enough to take seriously, light enough to actually do.
- **QA-3** Contradiction surfacing should feel **clarifying, not judgmental**. The system is a mirror, not a critic.
- **QA-4** Using this for a month should produce a **shareable personal constitution** you'd show to someone you trust.
- **QA-5** The system should **never tell you what to value**. It surfaces, it doesn't prescribe.
- **QA-6** API contracts must have a **single source of truth** in `shared-primitives/contracts/`. No dual definitions.
- **QA-7** API errors must render as **readable messages**, not raw objects. Users never see `{type, loc, msg}`.
- **QA-8** Basic human values (love, courage, honesty) should **always be addable** to a constitution, even if they don't meet the strict L < 0.05 threshold. The system shouldn't gatekeep universal values.
- **QA-9** The pilot should be **self-contained with demo data**. A first-time user can experience the full flow without providing their own corpus.

## Anti-Success (Failure Modes)

The system fails if:

- **Value imposition**: The system suggests what the user "should" believe. Discovery becomes prescription.
- **Coherence worship**: Users change values just to improve their Galois score. Goodhart's Law takes over.
- **Amendment theater**: The formal process becomes bureaucratic ritual without genuine reflection.
- **Contradiction shame**: Users feel bad about having conflicting values instead of curious about resolving them.
- **Philosophical gatekeeping**: The system feels like it's only for people who already think about ethics.
- **Technical gatekeeping**: Universal values like "love" or "honesty" are rejected because they don't meet arbitrary loss thresholds.
- **Raw error exposure**: Users see `{type: "list_type", loc: ["body"], msg: "Input should be..."}` instead of human-readable messages.
- **Contract drift at runtime**: Frontend expects one shape, backend returns another, user sees blank screens or crashes.
- **Cold start friction**: New users stare at empty screens with no guidance on what to enter.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Galois Fixed-Point** | Surface axioms from corpus | `corpus → detect_fixed_point() → axioms` |
| **Galois Loss** | Measure value-behavior drift | `(stated_values, witnessed_behavior) → L(P)` |
| **Contradiction Detection** | Surface value conflicts | `super_additive_loss(A, B) → conflict` |
| **Pilot Law Grammar** | Govern amendment process | `amendment → verify_schema_laws(COHERENCE_GATE)` |
| **Witness Mark** | Evidence for amendments | `change → Mark.emit(reasoning, principle_weights)` |
| **K-Block Lineage** | Trace constitutional evolution | `constitution_v1 → amendment → constitution_v2` |
| **Trust Gradient** | Track self-alignment over time | `TrustState.update_aligned() / update_misaligned()` |

**Composition Chain** (axiom discovery → constitution):
```
Personal Corpus (writings, decisions, traces)
  → Galois.detect_fixed_point(corpus)
  → Axiom candidates (L < 0.05)
  → User validation (Disgust Veto gate)
  → Initial Constitution draft
  → Amendment process (via pilot law grammar)
  → Living Constitution (versioned K-Block)
  → Drift monitoring (Galois loss on behavior)
```

## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*

This pilot instantiates the Experience Quality Operad via `ZERO_SEED_QUALITY_ALGEBRA`:

| Dimension | Instantiation |
|-----------|---------------|
| **Contrast** | discovery_depth, reflection_quality, evolution_pace |
| **Arc** | excavation → recognition → articulation → evolution |
| **Voice** | discovery ("Found not invented?"), ceremony ("Amendment process meaningful?"), mirror ("Not prescriptive?") |
| **Floor** | no_value_imposition, no_coherence_worship, universal_values_accepted, error_messages_readable |

**Weights**: C=0.25, A=0.40, V=0.35

**Implementation**: `impl/claude/services/experience_quality/algebras/zero_seed.py`

**Domain Spec**: `spec/theory/domains/zero-seed-quality.md`

## Canary Success Criteria

- A user with no philosophy background can **articulate 3-5 personal axioms** within the first session.
- The user **recognizes** at least one axiom they hadn't consciously articulated before.
- The amendment process produces **at least one constitutional evolution** over 30 days.
- Contradiction surfacing leads to **synthesis, not suppression**—the user resolves or consciously accepts the tension.
- The user would **share their constitution** with a trusted friend without embarrassment.

## Out of Scope

- Prescriptive ethics or moral recommendations.
- Comparison to other users' constitutions.
- Gamification of value alignment (no scores to optimize).
- Team/organizational governance (that's a different pilot).

## Mathematical Grounding

This pilot operationalizes several theoretical constructs:

| Theory | Application |
|--------|-------------|
| **Galois Modularization** | Fixed-point detection reveals axioms |
| **Toulmin Argument Structure** | Amendments require data, warrant, backing |
| **Living Constitution (Amendment F)** | Evolution through formal process |
| **Pilot Law Grammar (Amendment G)** | COHERENCE_GATE, DRIFT_ALERT schemas |
| **Trust Polynomial (Amendment E)** | Self-alignment tracking |
| **ETHICAL Floor (Amendment A)** | Values cannot offset ethical violations |

## Joy Dimension

**Primary**: SURPRISE — "Oh, that's what I actually believe."
**Secondary**: RECOGNITION — "I knew this, but I'd never said it."

The pilot should create moments where users discover patterns they hadn't consciously articulated. The joy is in revelation, not creation.

## Semantic Baseline Values

The following universal values MUST always be acceptable as axiom candidates, regardless of Galois loss score. These represent the baseline of human values that should never be gatekept:

| Category | Values |
|----------|--------|
| **Love & Connection** | love, compassion, empathy, kindness, loyalty, family, friendship |
| **Strength & Courage** | courage, strength, resilience, perseverance, determination, grit |
| **Character** | honesty, integrity, authenticity, humility, patience, gratitude |
| **Growth** | curiosity, wisdom, learning, growth, creativity, innovation |
| **Justice** | fairness, justice, equality, freedom, responsibility, accountability |
| **Spirit** | faith, hope, joy, peace, presence, mindfulness |

**Implementation**: When a user enters any of these words (or close synonyms), the system should:
1. Still compute Galois loss (for informational purposes)
2. Mark the value as "Baseline Value" rather than "Axiom" if L > 0.05
3. Allow addition to constitution regardless of loss score
4. Display: "This is a universal value. While it may not be a unique fixed point for you specifically, it's always valid to include in your constitution."

## Demo Corpus (Self-Contained Experience)

New users should see pre-filled example data to experience the full flow without providing their own corpus. The demo should feel like a guided archaeological dig.

### Demo Decisions

```
"I stayed late to help my colleague finish their project, even though I was exhausted."

"When they offered me the promotion, I turned it down because it would mean less time with my kids."

"I told them the truth about the mistake, even though I knew it would make me look bad."

"I chose the smaller apartment in the neighborhood where I knew people, over the bigger one across town."

"I returned the extra change the cashier gave me, even though no one would have noticed."

"I quit the job that paid well but made me miserable."

"I apologized first, even though I still think I was right about the facts."

"I gave up the window seat so the kid could watch the clouds."
```

### Expected Discoveries

From the demo corpus, the system should surface patterns like:
- "Relationships over personal gain" (multiple decisions prioritize connection)
- "Honesty even at personal cost" (truth-telling pattern)
- "Presence over acquisition" (choosing smaller/closer/simpler)

### Demo Mode Behavior

1. **First Visit**: Show "Try with example decisions?" prompt
2. **Demo Load**: Pre-fill the demo corpus, auto-run discovery
3. **Results**: Show 3-5 discovered patterns with explanations
4. **Invitation**: "These patterns emerged from example decisions. Want to discover your own?"
5. **Clear Path**: Button to clear demo and start fresh

## API Contract Requirements

To prevent the issues encountered in run-001, ALL API interactions MUST follow these patterns:

### Request Models (L6)

```python
# WRONG - bare parameters cause FastAPI validation errors
@router.post("/discover-axioms")
async def discover(decisions: list[str]):  # ❌ Bare list parameter
    ...

# RIGHT - Pydantic model for JSON body
class DiscoverAxiomsRequest(BaseModel):
    decisions: list[str]
    min_pattern_occurrences: int = 2

@router.post("/discover-axioms")
async def discover(request: DiscoverAxiomsRequest):  # ✅ Request model
    ...
```

### Error Handling (L9)

```typescript
// Frontend MUST normalize errors before rendering
function extractErrorMessage(error: unknown, fallback: string): string {
  if (!error || typeof error !== 'object') return fallback;
  const e = error as Record<string, unknown>;

  // String detail (normal error)
  if (typeof e.detail === 'string') return e.detail;

  // Array detail (FastAPI validation errors)
  if (Array.isArray(e.detail)) {
    return e.detail
      .map(item => item.msg || JSON.stringify(item))
      .join('; ');
  }

  return fallback;
}
```

## Pricing Context

Target: $15/month consumer subscription

Value proposition: "Know thyself—computationally." The only tool that surfaces your actual axioms rather than asking you to declare them.

Differentiation: Most journaling/reflection apps ask "what do you value?" This asks "what do your choices reveal you value?" and shows the delta.

---

## Regeneration

**Use the meta-prompt**: `pilots/REGENERATE_META.md`

This pilot requires no additional notes beyond the meta-prompt. Fill variables and execute.

See `runs/` for regeneration history.
