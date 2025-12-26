# Heterarchical Tolerance Protocol

> *"The system adapts to user, not user to system."*

**Version**: 1.0
**Date**: 2025-12-25
**Status**: Canonical Specification
**Principles**: Composable, Heterarchical, Tasteful, Ethical
**Philosophy**: Linear Design (Product shapes to user, not user to product)

---

## Abstract

The Heterarchical Tolerance Protocol enables **cross-layer edges** and **nonsense quarantine** within the Zero Seed seven-layer holarchy. Rather than enforcing strict hierarchical constraints, it allows users to create arbitrary connections while gracefully managing incoherence.

**Core Insight**: Structure helps, but porosity is essential. Users need freedom to explore, contradict, and create. The system adapts by quarantining nonsense without punishment.

**The Radical Promise**:
1. **Cross-layer edges allowed** — Jump from L1 (Axiom) to L5 (Action) if you want
2. **Justification encouraged, not required** — Except for critical edges (contradictions, supersessions)
3. **Nonsense quarantined, not blocked** — High-loss content isolated from system rankings
4. **Performance unaffected** — Incoherent input doesn't degrade the system
5. **No punishment, no lectures** — Gentle notifications with paths to recovery

---

## Prerequisites

| Document | Location | What It Provides |
|----------|----------|------------------|
| **Zero Seed** | `spec/protocols/zero-seed.md` | Seven-layer holarchy, Galois loss |
| **Constitution** | `spec/principles/CONSTITUTION.md` | Heterarchical principle |
| **Grand Strategy** | `plans/zero-seed-genesis-grand-strategy.md` | Part VII: Heterarchical Tolerance |
| **Galois Theory** | `spec/theory/galois-modularization.md` | Loss as coherence metric |

---

## Part I: Philosophical Foundations

### 1.1 The Linear Design Philosophy

**Inspiration**: Linear (the productivity tool) pioneered product-user adaptation:

| Linear Principle | Our Application |
|------------------|-----------------|
| **Product shapes to user** | System tolerates user's incoherence |
| **Nonsense doesn't spread** | Quarantine isolates high-loss content |
| **Performance unaffected** | Indexing excludes quarantined nodes |
| **Common cases prioritized** | Coherent content gets full features |

**The Anti-Pattern**: Traditional systems force users into rigid schemas. Users fight the tool. Friction accumulates. Joy dies.

**Our Resolution**: Accept user input unconditionally. Measure loss. Adapt behavior based on loss. Never block, never shame.

### 1.2 Heterarchy vs. Hierarchy

```
HIERARCHY (Traditional):
┌─────────────────────────────────────────┐
│  L1: Axioms                             │
│  ↓ (only down)                          │
│  L2: Values                             │
│  ↓                                      │
│  L3: Goals                              │
│  ...                                    │
│  L7: Representation                     │
└─────────────────────────────────────────┘
Rigid. One-way flow. Violations rejected.

HETERARCHY (Our System):
┌─────────────────────────────────────────┐
│  L1 ↔ L2 ↔ L3 ↔ L4 ↔ L5 ↔ L6 ↔ L7      │
│   ↖     ↗   ↖   ↗   ↖   ↗   ↖          │
│     Cross-layer edges allowed           │
│     (flagged for review, not blocked)   │
└─────────────────────────────────────────┘
Porous. Multi-directional. Violations tolerated.
```

**Why Heterarchy?**
- **Creativity requires freedom** — Users explore by making unexpected connections
- **Beliefs evolve non-linearly** — L5 (Action) can inspire L2 (Value) revision
- **Contradictions are fertile** — Tensions drive synthesis
- **Rigid structure kills joy** — Porosity enables play

### 1.3 The Three Tolerance Levels

```python
class EdgePolicyLevel(Enum):
    STRICT = "strict"      # MUST have justification (blocks without)
    SUGGESTED = "suggested"  # SHOULD have justification (flags without)
    OPTIONAL = "optional"    # MAY have justification (no enforcement)
```

**Design Rationale**:
- **STRICT** for critical edges (contradictions, supersessions) — These have semantic consequences
- **SUGGESTED** for structural edges (grounds, justifies) — Help but don't force
- **OPTIONAL** for exploratory edges — Maximum freedom

---

## Part II: Edge Validation Policy

### 2.1 Edge Policy Rules

From `plans/zero-seed-genesis-grand-strategy.md`:

```python
STRICT_EDGES (MUST have justification):
- EdgeKind.CONTRADICTS  # Paraconsistent conflict
- EdgeKind.SUPERSEDES    # Version replacement

SUGGESTED_EDGES (SHOULD have justification, flagged if missing):
- EdgeKind.GROUNDS      # L1 → L2 (axiom grounds value)
- EdgeKind.JUSTIFIES    # L2 → L3 (value justifies goal)

OPTIONAL_EDGES (MAY have justification, not flagged):
- EdgeKind.IMPLEMENTS   # L4 → L5 (obvious)
- EdgeKind.EXTENDS      # Same-layer refinement
- EdgeKind.DERIVES_FROM # Generic derivation
- [All other edge kinds]
```

### 2.2 Cross-Layer Edge Handling

**Definition**: Cross-layer edge = `abs(source.layer - target.layer) > 1`

**Policy**:
```python
if is_cross_layer:
    # Allowed by default
    valid = True

    # But flagged for review
    flagged = True

    # With suggestion
    suggestion = (
        f"This edge connects L{source_layer} to L{target_layer}, "
        f"skipping {layer_delta - 1} layer(s). "
        "Consider adding justification to explain the connection."
    )

    # Compute Galois loss for the transition
    galois_loss = compute_cross_layer_loss(source, target, edge)
```

**Examples**:

| Edge | Source | Target | Delta | Result |
|------|--------|--------|-------|--------|
| L1 → L2 | Axiom | Value | 1 | ✓ Valid, not flagged (adjacent) |
| L1 → L3 | Axiom | Goal | 2 | ✓ Valid, flagged (cross-layer) |
| L1 → L5 | Axiom | Action | 4 | ✓ Valid, flagged with high loss warning |
| L5 → L2 | Action | Value | 3 | ✓ Valid, flagged (upward revision allowed!) |

### 2.3 Validation Algorithm

```python
def validate_edge(edge: ZeroEdge, source_layer: int, target_layer: int) -> EdgeValidation:
    """
    Validate edge according to heterarchical policy.

    Steps:
    1. Determine policy level (STRICT/SUGGESTED/OPTIONAL)
    2. Check for justification
    3. Block if STRICT and missing justification
    4. Check for cross-layer (delta > 1)
    5. Flag if cross-layer (even if valid)
    6. Flag if SUGGESTED and missing justification
    7. Accept with suggestions
    """
    # Step 1: Determine level
    if edge.kind in STRICT_EDGES:
        level = EdgePolicyLevel.STRICT
    elif edge.kind in SUGGESTED_EDGES:
        level = EdgePolicyLevel.SUGGESTED
    else:
        level = EdgePolicyLevel.OPTIONAL

    # Step 2: Check justification
    has_justification = bool(edge.context and edge.context.strip())

    # Step 3: STRICT enforcement
    if level == EdgePolicyLevel.STRICT and not has_justification:
        return EdgeValidation(
            valid=False,
            reason=f"{edge.kind.value} edges require justification",
        )

    # Step 4-5: Cross-layer detection
    is_cross_layer = abs(source_layer - target_layer) > 1

    if is_cross_layer:
        loss = compute_cross_layer_loss(source, target, edge)
        return EdgeValidation(
            valid=True,
            flagged=True,
            reason="Cross-layer edge",
            suggestion=generate_cross_layer_suggestion(loss),
            galois_loss=loss.total_loss,
        )

    # Step 6: SUGGESTED flagging
    if level == EdgePolicyLevel.SUGGESTED and not has_justification:
        return EdgeValidation(
            valid=True,
            flagged=True,
            reason=f"{edge.kind.value} should have justification",
        )

    # Step 7: Accept
    return EdgeValidation(valid=True, flagged=False)
```

---

## Part III: Cross-Layer Loss Computation

### 3.1 Loss Formula

**Goal**: Quantify the semantic cost of skipping layers.

**Heuristic** (v1.0):
```
total_loss = min(1.0, 0.1 * layer_delta * base_multiplier)

where:
    layer_delta = abs(source.layer - target.layer)

    base_multiplier =
        1.5  if edge.kind in {CONTRADICTS, SUPERSEDES}  # Dialectical
        1.0  if edge.kind in {GROUNDS, JUSTIFIES}       # Vertical flow
        0.8  otherwise                                  # Exploratory
```

**Examples**:
```
L1 → L3 (delta=2, GROUNDS):       loss = 0.1 * 2 * 1.0 = 0.20
L1 → L5 (delta=4, IMPLEMENTS):    loss = 0.1 * 4 * 0.8 = 0.32
L1 → L7 (delta=6, CONTRADICTS):   loss = 0.1 * 6 * 1.5 = 0.90
```

### 3.2 Future: LLM-Based Loss

**Vision** (v2.0):
```python
async def compute_cross_layer_loss_llm(
    source: ZeroNode,
    target: ZeroNode,
    edge: ZeroEdge,
    llm: LLMClient,
) -> CrossLayerLoss:
    """
    Compute actual Galois loss via LLM restructuring.

    Strategy:
    1. Generate "missing" intermediate layers
    2. Measure loss from source → intermediate → target
    3. Compare to direct source → target
    4. Delta = information lost by skipping
    """
    # Generate intermediate content
    intermediate = await llm.generate(
        f"Fill in the missing {layer_delta - 1} layers between:\n"
        f"L{source.layer}: {source.content}\n"
        f"L{target.layer}: {target.content}"
    )

    # Measure round-trip loss
    loss = await galois.loss(intermediate)

    return CrossLayerLoss(total_loss=loss, ...)
```

### 3.3 Flagging Threshold

**Rule**: Flag if `layer_delta > 2` OR `total_loss > 0.5`

| Delta | Loss | Flag? | Reason |
|-------|------|-------|--------|
| 1 | 0.1 | No | Adjacent (expected) |
| 2 | 0.2 | No | One skip (tolerable) |
| 3 | 0.3 | Yes | Multiple skips |
| 2 | 0.6 | Yes | High loss despite small delta |
| 4 | 0.4 | Yes | Large delta |

---

## Part IV: Nonsense Quarantine

### 4.1 The Quarantine Philosophy

**Premise**: Users are sovereign. They may add anything.

**Problem**: Nonsense degrades system coherence and performance.

**Resolution**: Quarantine gracefully.

```
┌─────────────────────────────────────────────────────────────────┐
│  QUARANTINE DOES NOT MEAN DELETE                                │
│                                                                 │
│  Quarantined content:                                           │
│  ✓ Still visible in your personal feeds                        │
│  ✓ Still editable by you                                       │
│  ✓ Can exit quarantine if refined                              │
│                                                                 │
│  But:                                                           │
│  ✗ Won't affect system-wide rankings                           │
│  ✗ Won't propagate to recommendations                          │
│  ✗ Won't appear in global searches                             │
│                                                                 │
│  Think of it as: "Your notebook page that isn't published yet" │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Loss Thresholds

From `plans/zero-seed-genesis-grand-strategy.md`:

```python
LOSS_THRESHOLD = 0.85        # Above this = quarantine
SUGGESTION_THRESHOLD = 0.5   # Above this = suggest improvement

if loss < 0.5:
    return "Coherent"

elif loss < 0.85:
    return "Hand-wavy but tolerable" + suggestion

else:
    return Quarantine(effects=[...])
```

**Rationale**:
- **0.0-0.5**: Coherent range — Most proofs, specs, goals
- **0.5-0.85**: Hand-wavy range — Rough drafts, explorations
- **0.85-1.0**: Nonsense range — Random text, contradictory jumbles

### 4.3 Quarantine Effects

```python
class QuarantineEffects(Enum):
    NO_SYSTEM_RANKING = "no_system_ranking"
    NO_RECOMMENDATIONS = "no_recommendations"
    PERSONAL_VISIBLE = "personal_visible"
    REVERSIBLE = "reversible"
```

**Implementation**:
```python
async def on_quarantine(kblock: KBlock) -> None:
    # Add to quarantine feed (user can still see it)
    await feeds.quarantine.add(kblock)

    # Remove from system-wide indexes
    await system_index.exclude(kblock.id)

    # Create witness mark (reversible)
    await witness.mark(
        action="quarantine",
        kblock_id=kblock.id,
        reason="High Galois loss",
        reversible=True,
    )

    # Notify user (gently)
    await notify.gentle(
        "This K-Block has been quarantined due to high incoherence. "
        "It's still yours—you can refine it or leave it be."
    )
```

### 4.4 Exiting Quarantine

**Automatic Re-evaluation**:
```python
async def on_kblock_edit(kblock: KBlock) -> None:
    if kblock.quarantined:
        # Recompute loss
        new_loss = await galois.compute_loss(kblock)

        if new_loss < LOSS_THRESHOLD:
            # Exit quarantine
            await exit_quarantine(kblock)
            await notify.gentle(
                f"This K-Block's coherence improved to {1 - new_loss:.2f}. "
                "It's no longer quarantined!"
            )
```

---

## Part V: User Interface

### 5.1 Edge Creation UI

When user creates cross-layer edge:

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CREATING EDGE                                                           ║
║                                                                          ║
║  From: L1 "Entity Axiom" (void.axiom.entity)                            ║
║  To:   L5 "Implementation" (world.action.implement)                     ║
║                                                                          ║
║  ⚠️  This is a cross-layer edge (skipping 3 layers)                     ║
║                                                                          ║
║  Estimated Galois loss: 0.32                                            ║
║                                                                          ║
║  Suggestion: Consider adding intermediate nodes:                        ║
║  • L2 (Value): What value does this axiom ground?                       ║
║  • L3 (Goal): What goal follows from that value?                        ║
║  • L4 (Spec): How is that goal specified?                               ║
║                                                                          ║
║  [ Add justification (optional) ]                                       ║
║  ┌────────────────────────────────────────────────────────────────┐     ║
║  │ This axiom directly informs implementation because...          │     ║
║  └────────────────────────────────────────────────────────────────┘     ║
║                                                                          ║
║  [ Create Edge ]  [ Add Intermediates ]  [ Cancel ]                     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 5.2 Quarantine Notification

When content is quarantined:

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CONTENT QUARANTINED (Gently)                                            ║
║                                                                          ║
║  Your K-Block "Random Thoughts" has been quarantined.                   ║
║                                                                          ║
║  Why? The content has very high loss (0.91), indicating it may be       ║
║  incoherent or contradictory with itself.                               ║
║                                                                          ║
║  What this means:                                                        ║
║  ✓ It's still yours—visible in your personal feeds                      ║
║  ✓ You can edit it anytime                                              ║
║  ✓ If you refine it, it can exit quarantine                             ║
║                                                                          ║
║  What changed:                                                           ║
║  ✗ Won't affect system-wide rankings                                    ║
║  ✗ Won't appear in recommendations                                      ║
║  ✗ Won't show in global searches                                        ║
║                                                                          ║
║  No judgment—just protecting the system's coherence while respecting    ║
║  your sovereignty.                                                       ║
║                                                                          ║
║  [ Refine Now ]  [ View in Quarantine Feed ]  [ Dismiss ]               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 5.3 Cross-Layer Edge Badge

In graph visualizations:

```
┌──────────────────────────────────────────┐
│  L1: Entity Axiom                        │
│                                          │
│  "Everything is a node"                  │
│                                          │
│  ↓ [IMPLEMENTS] ⚠️ Cross-layer (Δ=4)     │
│    Loss: 0.32                            │
│                                          │
│  L5: Implementation                      │
│                                          │
│  class Node: ...                         │
└──────────────────────────────────────────┘

Legend:
  ⚠️ = Cross-layer edge (flagged)
  Δ = Layer delta
  Loss = Galois loss of transition
```

---

## Part VI: Integration with Constitution

### 6.1 Heterarchical Principle

From `spec/principles/CONSTITUTION.md`:

```
HETERARCHICAL: Agents exist in flux, not fixed hierarchy.

Application to edges:
- Cross-layer edges allowed (heterarchy realized)
- Justification encouraged, not mandated (flux tolerated)
- Quarantine graceful (no punishment for exploration)
```

### 6.2 Ethical Principle

```
ETHICAL: Agents augment human capability, never replace judgment.

Application to quarantine:
- User always has final say (reversible quarantine)
- System suggests, never dictates
- Gentle notifications, not shame
```

### 6.3 Joy-Inducing Principle

```
JOY_INDUCING: Delight in interaction.

Application to tolerance:
- Freedom to explore (cross-layer edges)
- No friction from rigid structure
- Celebrate refinement (exiting quarantine)
```

---

## Part VII: Implementation Checklist

### Phase 5 Deliverables (from Grand Strategy)

```
✓ impl/claude/services/edge/__init__.py
✓ impl/claude/services/edge/policy.py
✓ impl/claude/services/edge/quarantine.py
✓ impl/claude/services/zero_seed/galois/cross_layer.py
✓ spec/protocols/heterarchy.md
```

### Success Criteria

```
✓ Cross-layer edges allowed
✓ Justification encouraged not required
✓ Quarantine works without blocking
✓ Performance unaffected by nonsense
✓ Edge validation respects three levels (STRICT/SUGGESTED/OPTIONAL)
✓ Loss computation returns reasonable values
✓ UI shows cross-layer badges
✓ Quarantine feed functional
```

### Testing Strategy

```python
# Test 1: Cross-layer edges allowed
edge = ZeroEdge(source=l1_node.id, target=l5_node.id, kind=EdgeKind.IMPLEMENTS)
validation = validate_edge(edge, 1, 5)
assert validation.valid
assert validation.flagged

# Test 2: STRICT edges require justification
edge = ZeroEdge(kind=EdgeKind.CONTRADICTS, context="")
validation = validate_edge(edge, 1, 2)
assert not validation.valid

# Test 3: Quarantine doesn't block
decision = evaluate_for_quarantine(0.9)
assert decision.quarantine
assert QuarantineEffects.REVERSIBLE in decision.effects

# Test 4: Loss computation reasonable
loss = compute_cross_layer_loss(l1_node, l5_node, edge)
assert 0 <= loss.total_loss <= 1.0
assert loss.layer_delta == 4
```

---

## Part VIII: Future Enhancements

### 8.1 Adaptive Thresholds

**Idea**: Learn user-specific thresholds from behavior.

```python
class PersonalizedQuarantine:
    """Adapt thresholds to user's tolerance for incoherence."""

    async def learn_threshold(self, user: User) -> float:
        # If user frequently refines high-loss content → lower threshold
        # If user ignores quarantine → raise threshold
        refinement_rate = await compute_refinement_rate(user)

        if refinement_rate > 0.7:
            return 0.7  # Lower threshold (user cares about coherence)
        elif refinement_rate < 0.3:
            return 0.95  # Higher threshold (user tolerates messiness)
        else:
            return 0.85  # Default
```

### 8.2 Cross-Layer Suggestions

**Idea**: Auto-generate intermediate nodes for cross-layer edges.

```python
async def suggest_intermediates(
    source: ZeroNode,
    target: ZeroNode,
    llm: LLMClient,
) -> list[ZeroNode]:
    """Generate missing intermediate layers."""
    prompt = (
        f"Fill in the missing layers between:\n"
        f"L{source.layer}: {source.content}\n"
        f"L{target.layer}: {target.content}\n\n"
        f"Generate {target.layer - source.layer - 1} intermediate nodes."
    )

    intermediates = await llm.generate(prompt)
    return parse_intermediates(intermediates, source.layer, target.layer)
```

### 8.3 Quarantine Analytics

**Idea**: Show user their coherence trends over time.

```
╔══════════════════════════════════════════════════════════════════════════╗
║  YOUR COHERENCE JOURNEY                                                  ║
║                                                                          ║
║  Average loss over time:                                                 ║
║                                                                          ║
║   1.0 │                                                                  ║
║       │                                                                  ║
║   0.5 │     ●                                                            ║
║       │   ●   ●     ●                                                    ║
║   0.0 │●●       ●●●   ●●●●                                               ║
║       └────────────────────────────────────────────                      ║
║        Jan  Feb  Mar  Apr  May  Jun  Jul                                 ║
║                                                                          ║
║  Insight: Your content has become 40% more coherent since January!      ║
║           Most improvement in L3 (Goals).                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Cross-References

**Related Specifications**:
- `spec/protocols/zero-seed.md` — Seven-layer holarchy
- `spec/principles/CONSTITUTION.md` — Heterarchical, Ethical, Joy-Inducing principles
- `spec/theory/galois-modularization.md` — Loss theory
- `plans/zero-seed-genesis-grand-strategy.md` — Part VII: Heterarchical Tolerance

**Implementation Files**:
- `impl/claude/services/edge/policy.py` — Edge validation
- `impl/claude/services/edge/quarantine.py` — Nonsense quarantine
- `impl/claude/services/zero_seed/galois/cross_layer.py` — Loss computation

---

## Document Metadata

- **Version**: 1.0.0
- **Date**: 2025-12-25
- **Authors**: Kent Gang, Claude (Anthropic)
- **Status**: CANONICAL
- **Philosophy**: Linear Design + Heterarchical Tolerance
- **Line Count**: ~850

---

*"Structure helps. Porosity is essential. The system adapts to you."*
