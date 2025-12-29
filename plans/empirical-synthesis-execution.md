# Empirical Synthesis Execution Plan

> *"The experiment IS the research. The kernel IS the system. The Mirror IS the ground truth."*

**Created**: 2025-12-28
**Status**: Ready for execution
**Pilot**: trail-to-crystal (simplest pilot)
**Priority**: P0 items first, then P1

---

## Context: What We Learned

Four empirical experiments tested bold claims about kgents. Here's what we found:

### Experiment Results Summary

| Claim | Predicted | Actual | Verdict |
|-------|-----------|--------|---------|
| Galois correlation | r > 0.6 | **r = 0.5624** | ⚠️ PARTIAL |
| Associativity deviation | ε < 0.05 | **ε = 0.25** | ❌ FALSE |
| Mirror thresholds | δ < 0.1 | **ρ = 0.83, δ = 0.17** | ⚠️ PARTIAL |
| Minimal kernel | < 200 lines | **77 lines** | ✅ TRUE |

### Key Discoveries

1. **Associativity is BROKEN**: The averaging composition `(a+b)/2` is mathematically non-associative. Deviation formula: `|c - a| / 4`, max = 0.25. This breaks categorical foundations. **Fix: Use product composition `a * b`.**

2. **Kent's epistemology is MORE FORMAL**: He sees derivation paths where heuristics see only prose. His CATEGORICAL zone extends to L < 0.45 (theory said L < 0.10). He rated "Heterarchy" as CATEGORICAL because he saw the theorem: if agents are morphisms, no morphism has intrinsic privilege.

3. **The 77-line kernel generates everything**: All 7 design principles and 7 governance articles derive from just 3 axioms:
   - L0.1 ENTITY: There exist things
   - L0.2 MORPHISM: Things relate
   - L0.3 MIRROR: We judge by reflection (Kent's somatic oracle)

4. **Galois loss needs augmentation**: Syntactic complexity ≠ semantic difficulty. State machines look complex but are solved patterns. Need: `Difficulty = α·Loss + β·Novelty + γ·Dependency`

### Full Evidence

All experimental data and analysis is in:
- `brainstorming/empirical-refinement-v2/CLAIMS.md` — scoreboard
- `brainstorming/empirical-refinement-v2/SURPRISES.md` — 7 surprises documented
- `brainstorming/empirical-refinement-v2/discoveries/01-galois-bet.md` — r = 0.5624
- `brainstorming/empirical-refinement-v2/discoveries/02-associativity-fix.md` — CRITICAL BUG + fix
- `brainstorming/empirical-refinement-v2/discoveries/03-mirror-calibration.md` — ρ = 0.83, Kent's thresholds
- `brainstorming/empirical-refinement-v2/discoveries/04-minimal-kernel.md` — 77-line kernel

---

## Why trail-to-crystal as Pilot

The trail-to-crystal pilot is ideal because:

1. **Simplest pilot**: Only 9 laws (L1-L9) vs. 20+ in other pilots
2. **Uses composition heavily**: Day → Marks → Crystal is sequential composition
3. **Has quality metrics**: Crystal compression quality is measurable
4. **Clear success criteria**: "Day closure" is binary — crystal produced or not
5. **Existing implementation**: Already has code to modify, not greenfield

**Location**: `pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md`

---

## Execution Plan

### Phase 1: Fix Associativity (P0, ~2 hours)

**Goal**: Replace averaging with product composition in Experience Quality Operad.

**Files to modify**:
1. `spec/theory/experience-quality-operad.md`
2. `impl/claude/services/experience_quality/composition.py` (if exists)
3. `impl/claude/services/experience_quality/domains/wasm_survivors.py`

**Changes**:

```python
# BEFORE (line ~448 in spec)
combined_arc = (q_a.arc_coverage + q_b.arc_coverage) / 2

# AFTER
combined_arc = q_a.arc_coverage * q_b.arc_coverage
```

**Update the law claim**:
```python
# BEFORE
Law("assoc_par", "(A || B) || C ≈ A || (B || C)", "Approximately associative")

# AFTER
Law("assoc_par", "(A || B) || C = A || (B || C)", "Strictly associative (product)")
```

**Verification**:
```python
# Test that associativity now holds
def test_associativity():
    for _ in range(1000):
        a, b, c = random.random(), random.random(), random.random()
        left = (a * b) * c
        right = a * (b * c)
        assert abs(left - right) < 1e-10, f"Associativity violated: {left} != {right}"
```

### Phase 2: Create Kernel Spec (P0, ~1 hour)

**Goal**: Create `spec/kernel.md` as the 77-line canonical ground truth.

**Content** (copy from `discoveries/04-minimal-kernel.md`):

```markdown
# kgents Minimal Kernel v1.0

> *"77 lines. Everything else derives from this."*

## Layer 0: Irreducibles (3 axioms)

L0.1 ENTITY:   There exist things.
L0.2 MORPHISM: Things relate.
L0.3 MIRROR:   We judge by reflection. (Kent's somatic oracle)

## Layer 1: Primitives (8 derived)

L1.1 COMPOSE:    (f >> g)(x) = g(f(x))
L1.2 JUDGE:      Claim -> Verdict
L1.3 GROUND:     Query -> {grounded, content}
L1.4 ID:         f >> Id = f = Id >> f
L1.5 CONTRADICT: Thesis -> Antithesis
L1.6 SUBLATE:    (Thesis, Antithesis) -> Synthesis
L1.7 FIX:        Iterate until stable
L1.8 GALOIS:     L(P) = d(P, C(R(P)))

## Layer 2: Derived (19 derivations)

[Design Principles, Governance Articles, Structural derivations]
See: discoveries/04-minimal-kernel.md for full content
```

**Verification**: Every spec should trace back to kernel axioms.

### Phase 3: Kent-Calibrate Thresholds (P1, ~1 hour)

**Goal**: Update `spec/protocols/zero-seed.md` with Kent-calibrated thresholds.

**Files to modify**:
1. `spec/protocols/zero-seed.md`
2. Any implementation that uses tier thresholds

**Changes**:

```python
# BEFORE (theoretical)
TIER_THRESHOLDS = {
    "CATEGORICAL": 0.10,
    "EMPIRICAL": 0.30,
    "AESTHETIC": 0.50,
    "SOMATIC": 0.70,
}

# AFTER (Kent-calibrated)
TIER_THRESHOLDS = {
    "CATEGORICAL": 0.45,  # Kent sees more as provable
    "EMPIRICAL": 0.38,
    "AESTHETIC": 0.65,
    "SOMATIC": 0.70,
}
```

**Add calibration note**:
```markdown
## Threshold Calibration

These thresholds are calibrated to Kent's actual epistemology (2025-12-28).
Kent's CATEGORICAL zone is larger than structural analysis predicts because
he can see derivation paths in prose that heuristics miss.

Evidence: brainstorming/empirical-refinement-v2/discoveries/03-mirror-calibration.md
Correlation: ρ = 0.8346
```

### Phase 4: Apply to trail-to-crystal (P1, ~4 hours)

**Goal**: Update trail-to-crystal pilot to use new composition and kernel derivation.

**Files**:
- `pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md`

**Changes**:

#### 4.1: Add Kernel Derivation Section

Add to PROTO_SPEC.md:
```markdown
## Kernel Derivation

This pilot derives from the 77-line kernel:

| Law | Derives From | Derivation |
|-----|--------------|------------|
| L1 Day Closure | L1.7 (Fix) | Day is a fixed point of mark accumulation |
| L2 Intent First | L1.2 (Judge) | Actions without intent fail judgment |
| L3 Noise Quarantine | L1.8 (Galois) | High-loss marks are unstable |
| L4 Compression Honesty | L1.8 (Galois) | Crystal = minimal-loss representation |
| L5 Provenance | L0.2 (Morphism) | Every output traces to input |
| L6 Contract Coherence | L1.4 (Id) | Single source = identity preserved |
| L7 Request Model | L1.1 (Compose) | Composition requires typed interfaces |
| L8 Error Normalization | L1.6 (Sublate) | Errors synthesize to strings |
| L9 Trail Continuity | L1.1 (Compose) | Days compose into trails |
```

#### 4.2: Update Composition Semantics

If the pilot uses quality composition, ensure it uses product:
```markdown
## Crystal Quality Composition

When multiple marks contribute to a crystal:
- Quality compounds multiplicatively: Q_crystal = Π Q_mark
- This is strictly associative: (a·b)·c = a·(b·c)
- Floor gate preserved: any Q=0 mark zeros the crystal quality
```

#### 4.3: Add Loss Tiers to Laws

Annotate each law with its tier:
```markdown
| Law | Tier | Loss | Justification |
|-----|------|------|---------------|
| L1 Day Closure | CATEGORICAL | 0.12 | Derivable from Fix |
| L2 Intent First | CATEGORICAL | 0.15 | Derivable from Judge |
| L3 Noise Quarantine | EMPIRICAL | 0.22 | Testable threshold |
| L4 Compression Honesty | CATEGORICAL | 0.18 | Derivable from Galois |
| L5 Provenance | CATEGORICAL | 0.08 | Derivable from Morphism |
| L6 Contract Coherence | CATEGORICAL | 0.10 | Derivable from Id |
| L7 Request Model | EMPIRICAL | 0.25 | Implementation choice |
| L8 Error Normalization | EMPIRICAL | 0.28 | Implementation choice |
| L9 Trail Continuity | CATEGORICAL | 0.12 | Derivable from Compose |
```

### Phase 5: Add Derivation Traces to Constitution (P1, ~4 hours)

**Goal**: Add derivation proofs to at least 3 principles as proof of concept.

**File**: `spec/principles/CONSTITUTION.md`

**Example for Composable**:
```markdown
## 5. Composable

> Agents are morphisms in a category; composition is primary.

### Derivation from Kernel

1. Agents are things that relate (L0.1 + L0.2)
2. Relations compose: if f: A→B and g: B→C, then g∘f: A→C (L1.1)
3. Identity exists: Id: A→A such that f∘Id = f = Id∘f (L1.4)
4. Associativity holds: (f∘g)∘h = f∘(g∘h) (categorical axiom)
5. Therefore: agents form a category, composition is the structure ∎

**Loss**: L = 0.08 (CATEGORICAL)
**Kent Rating**: CATEGORICAL (confirmed 2025-12-28)
```

**Do this for**:
1. Composable (above)
2. Heterarchical (Kent saw this as CATEGORICAL)
3. Generative (derives from Ground + Compose)

### Phase 6: Verification (P1, ~2 hours)

**Goal**: Verify all changes maintain coherence.

**Tests to run**:

```bash
# 1. Type check
cd impl/claude && uv run mypy .

# 2. Run existing tests
cd impl/claude && uv run pytest -q

# 3. Verify associativity fix
cd impl/claude && uv run pytest -k associativity

# 4. Check trail-to-crystal pilot loads
# (implementation-specific)
```

**Manual verification**:
1. Read `spec/kernel.md` — can you derive all principles from it?
2. Read trail-to-crystal PROTO_SPEC — do derivation traces make sense?
3. Check that no spec claims averaging composition anymore

---

## Success Criteria

### P0 Complete When:
- [ ] Associativity bug fixed (product composition)
- [ ] `spec/kernel.md` exists with 77 lines
- [ ] All tests pass

### P1 Complete When:
- [ ] Zero-seed thresholds are Kent-calibrated
- [ ] trail-to-crystal has kernel derivation section
- [ ] trail-to-crystal laws annotated with tiers
- [ ] 3 Constitution principles have derivation proofs
- [ ] Verification passes

### Full Vision Complete When:
- [ ] All pilots have kernel derivation sections
- [ ] All Constitution principles have derivation proofs
- [ ] `kg difficulty` tool exists (3-signal predictor)
- [ ] `kg regenerate` tool exists (regeneration test)
- [ ] Quarterly Mirror calibration ritual documented

---

## Anti-Patterns to Avoid

1. **Don't average**: Never use `(a+b)/2` for composition. Always product.
2. **Don't assume low loss = categorical**: Kent's zone is larger. Trust the calibrated thresholds.
3. **Don't skip derivation traces**: Every law should trace to kernel.
4. **Don't break existing tests**: All changes must be backwards compatible.

---

## trail-to-crystal Pilot Deep Dive

The pilot already integrates with the Experience Quality Operad (lines 130-145 of PROTO_SPEC):

```
Quality Algebra: DAILY_LAB_QUALITY_ALGEBRA
Implementation: impl/claude/services/experience_quality/algebras/daily_lab.py
Domain Spec: spec/theory/domains/daily-lab-quality.md
Weights: C=0.25, A=0.30, V=0.45
```

### Composition Chain (Affected by Fix)

The pilot uses this composition chain:
```
Action → Mark.emit → Trace.append → Crystal.compress → Trail.display
```

**Where associativity matters**: When multiple marks compose into a crystal, their quality scores combine. Currently uses averaging (broken). Must use product (fixed).

### Laws → Kernel Mapping (To Add)

| Law | Kernel | Derivation Path |
|-----|--------|-----------------|
| L1 Day Closure | L1.7 Fix | Day = fixed point where crystal exists |
| L2 Intent First | L1.2 Judge | Actions judged against declared intent |
| L3 Noise Quarantine | L1.8 Galois | High L(mark) → quarantine |
| L4 Compression Honesty | L1.8 Galois | Crystal = argmin L(representation) |
| L5 Provenance | L0.2 Morphism | Output morphism traces to input |
| L6 Contract Coherence | L1.4 Id | Single source = identity law |
| L7 Request Model | L1.1 Compose | Typed composition |
| L8 Error Normalization | L1.6 Sublate | Error → string synthesis |
| L9 Trail Continuity | L1.1 Compose | Days compose into trail |

### Specific File Changes for trail-to-crystal

1. **PROTO_SPEC.md** (add after line 145):
```markdown
## Kernel Derivation

All 9 laws derive from the 77-line kernel (`spec/kernel.md`):

| Law | Tier | L | Derivation |
|-----|------|---|------------|
| L1 Day Closure | CATEGORICAL | 0.12 | L1.7 (Fix): Day = fixed point |
| L2 Intent First | CATEGORICAL | 0.15 | L1.2 (Judge): Intent judges action |
| L3 Noise Quarantine | EMPIRICAL | 0.22 | L1.8 (Galois): High loss → quarantine |
| L4 Compression Honesty | CATEGORICAL | 0.18 | L1.8 (Galois): Crystal minimizes loss |
| L5 Provenance | CATEGORICAL | 0.08 | L0.2 (Morphism): Traces compose |
| L6 Contract Coherence | CATEGORICAL | 0.10 | L1.4 (Id): Single source |
| L7 Request Model | EMPIRICAL | 0.25 | L1.1 (Compose): Typed interfaces |
| L8 Error Normalization | EMPIRICAL | 0.28 | L1.6 (Sublate): Error synthesis |
| L9 Trail Continuity | CATEGORICAL | 0.12 | L1.1 (Compose): Day composition |
```

2. **Quality Algebra section** (update line 130):
```markdown
## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*
> *Note: Composition uses PRODUCT (not averaging) for strict associativity*

This pilot instantiates the Experience Quality Operad via `DAILY_LAB_QUALITY_ALGEBRA`:
[rest unchanged]

**Composition Law**: Quality compounds multiplicatively:
- Q(mark₁ >> mark₂) = Q(mark₁) × Q(mark₂)
- Strictly associative: (a×b)×c = a×(b×c)
- Floor gate: any Q=0 zeros the crystal
```

3. **daily_lab.py** (if it exists, update composition):
```python
# BEFORE
combined_quality = (q_a + q_b) / 2

# AFTER
combined_quality = q_a * q_b  # Multiplicative, associative
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `brainstorming/empirical-refinement-v2/discoveries/02-associativity-fix.md` | Full proof of associativity bug |
| `brainstorming/empirical-refinement-v2/discoveries/04-minimal-kernel.md` | 77-line kernel to copy |
| `brainstorming/empirical-refinement-v2/discoveries/03-mirror-calibration.md` | Kent's actual thresholds |
| `pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md` | Pilot to modify |
| `spec/theory/experience-quality-operad.md` | Composition spec to fix |
| `spec/theory/domains/daily-lab-quality.md` | Domain-specific quality spec |
| `impl/claude/services/experience_quality/algebras/daily_lab.py` | Implementation to fix |
| `spec/protocols/zero-seed.md` | Thresholds to calibrate |
| `spec/principles/CONSTITUTION.md` | Principles to add derivations |

---

## The One Sentence Goal

**Make trail-to-crystal the first pilot where every law traces to a 77-line kernel through strictly associative composition.**

---

*"The proof IS the decision. The mark IS the witness. The kernel IS the garden's seed."*
