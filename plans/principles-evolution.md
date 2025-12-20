# Principles Evolution: Follow-Up Plan

> *Loose ends and future enhancements from the principles.md stratification.*

**Date**: 2025-12-19
**Status**: Phase 2 Complete (Cross-References Verified)

---

## What Was Done

### Phase 1: Stratification (Complete)

The 1718-line `spec/principles.md` was stratified into a hierarchical structure:

| File | Lines | Purpose |
|------|-------|---------|
| `spec/principles.md` | ~180 | Projection/index for quick reference |
| `spec/principles/CONSTITUTION.md` | ~145 | The 7 core principles (immutable) |
| `spec/principles/meta.md` | ~180 | Accursed Share, AGENTESE, Personality Space |
| `spec/principles/operational.md` | ~100 | Transparent Infrastructure, Graceful Degradation |
| `spec/principles/puppets.md` | ~115 | Puppet Constructions |
| `spec/principles/decisions/INDEX.md` | ~70 | AD summary table and reading guide |
| `spec/principles/decisions/AD-*.md` | ~50 each | 13 individual AD files |

**Compression achieved**: 1718 → 180 lines for daily consumption (10:1 ratio)

### Phase 2: Cross-Reference Verification (Complete)

Verified and fixed all cross-references to principles across the codebase using parallel agents:

| Category | Updated | Skipped | Notes |
|----------|---------|---------|-------|
| **Spec files** | 17 | 24 | All §1-§7 → CONSTITUTION.md, AD-XXX → decisions/ |
| **Docs/Skills** | 5 | 6 | AD references and §7 Generative updated |
| **Impl files** | 33 | ~18 | Python + TypeScript, preserved file path defaults |
| **Plans/Config** | 20 | ~12 | Including CLAUDE.md, NOW.md, config/*.yaml |

**Total**: 75 files updated, ~60 files correctly skipped (general references preserved)

**Change patterns applied**:
- `principles.md` + §1-§7 → `principles/CONSTITUTION.md`
- `principles.md` + AD-XXX → `principles/decisions/AD-XXX-*.md`
- `principles.md` + Accursed Share/AGENTESE → `principles/meta.md`
- `principles.md` + Graceful Degradation → `principles/operational.md`
- `principles.md` + Puppet/Holon → `principles/puppets.md`
- General references → Kept as `principles.md` or `principles/` directory

**Verification passed**: `grep -r "principles\.md#" ... | grep -v decisions` returns empty.

---

## Follow-Up Tasks

### Priority 1: Integration ✅ COMPLETE

- [x] **Update CLAUDE.md session start ritual** to context-aware Four Stances (Genesis/Poiesis/Krisis/Therapeia)
- [x] **Verify cross-references** in 75+ files across spec/, docs/, impl/, plans/ (see Phase 2 above)
- [x] **Update docs/skills/spec-hygiene.md** line counts and cross-references

### Priority 2: AGENTESE Node ✅ SPEC COMPLETE

**Spec created**: `spec/principles/node.md` (~230 lines)

Defines `concept.principles` node with aspects:
- `manifest` — Stance-aware principle projection
- `constitution`, `meta`, `operational`, `ad` — Direct file access
- `check` — Validate artifact against principles (Krisis)
- `teach` — Interactive principle teaching
- `heal` — Therapeia: diagnose violation and prescribe restoration

**Implementation**: Future work in `impl/claude/protocols/agentese/contexts/concept/principles.py`

### Priority 3: Consumption Model ✅ SPEC COMPLETE

**Spec created**: `spec/principles/consumption.md` (~190 lines)

The Four Stances (Tetrad):
- **Genesis** (γένεσις) — Becoming: Which principles apply?
- **Poiesis** (ποίησις) — Making: How do I build according to principles?
- **Krisis** (κρίσις) — Judgment: Does this embody the principles?
- **Therapeia** (θεραπεία) — Healing: Which principle was violated?

Replaces the ad-hoc `read_principles(mode)` helper with a categorical consumption polynomial.

### Priority 4: Validation

- [ ] **Add link checker** to CI that validates all relative links in principles/ work
- [ ] **Cross-reference check** that AD files reference implementation paths that exist

---

## Future Considerations

### Rate of Change

The stratified structure has different stability characteristics:

| Layer | Rate of Change | Governance |
|-------|----------------|------------|
| CONSTITUTION.md | Immutable (years) | Kent-voice only |
| meta.md | Slow (months) | Requires deep thinking |
| operational.md | Medium (weeks) | Tactical updates OK |
| decisions/AD-*.md | Fast (sessions) | Accumulates from learnings |

**Implication**: New ADs are expected and easy to add. Core principle changes are rare and significant.

### Adding New ADs

When a session produces a new architectural decision:

1. Create `AD-0XX-name.md` in `spec/principles/decisions/`
2. Add entry to `INDEX.md` table
3. Add entry to `spec/principles.md` AD table
4. Optionally update CLAUDE.md if it's a common-use pattern

### The Polynomial Consumption Model

The brainstorm proposed a polynomial model for principles consumption:

```python
PRINCIPLES_POLYNOMIAL = PolyAgent(
    positions=frozenset(["onboarding", "implementing", "designing", "debugging", "philosophizing"]),
    directions=lambda mode: RELEVANT_SECTIONS[mode],
    transition=context_aware_transition
)
```

This remains a future enhancement. The current stratification is the first step toward mode-dependent consumption.

---

## Anti-Sausage Check

Before merging this stratification:

- ❓ *Did I smooth anything that should stay rough?*
  → No. Preserved Kent's voice anchors and opinionated stances.

- ❓ *Did I add words Kent wouldn't use?*
  → Used existing kgents vocabulary throughout.

- ❓ *Did I lose any opinionated stances?*
  → No. All content preserved, just reorganized.

- ❓ *Is this still daring, bold, creative—or did I make it safe?*
  → Daring: Significant structural change to the constitution.
  → Creative: Eigendecomposition of stable/evolving content.
  → Opinionated: Clear hierarchy and consumption patterns.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Total lines in principles.md | 1718 | 180 |
| Lines for session start | 1718 | 145 (CONSTITUTION.md) |
| AD files | 1 (inline) | 13 (individual) |
| Compression ratio (daily use) | 1:1 | 10:1 |
| Searchability | Low (monolith) | High (named files) |
| Cross-refs verified | 0 | 75 updated, 60 preserved |

---

## What Remains (Priorities 3-4)

### Still Open

| Task | Effort | Value | Notes |
|------|--------|-------|-------|
| **Add link checker to CI** | Low | Medium | Validates all relative links in principles/ |
| **AD→impl path validation** | Low | Medium | Ensures AD files reference existing code paths |
| **AGENTESE node impl** | Medium | High | `concept.principles` node in `protocols/agentese/` |

### Implementation Details for AGENTESE Node

The spec (`spec/principles/node.md`) defines the node. Implementation path:

```
impl/claude/protocols/agentese/contexts/concept/principles.py
```

Key aspects to implement:
- `manifest(stance)` — Returns stance-appropriate principles subset
- `constitution`, `meta`, `operational`, `ad(number)` — Direct file access
- `check(artifact)` — Krisis: validate against principles
- `teach(principle)` — Interactive teaching mode
- `heal(violation)` — Therapeia: diagnose and prescribe

---

## What Can Be Built On Top

### Enabled by Stratification

The completed work unlocks several opportunities:

| Opportunity | Description | Prerequisites Met |
|-------------|-------------|-------------------|
| **Stance-aware prompts** | LLM sessions auto-load relevant principles based on detected stance | ✅ CONSTITUTION.md + consumption.md |
| **Principle linting** | CI check that validates new code against §1-§7 | ✅ CONSTITUTION.md machine-readable |
| **AD accumulation** | Easy to add new ADs as learnings emerge | ✅ decisions/ directory + INDEX.md |
| **Observer-dependent views** | Different principles projections for different roles | ✅ Stratified structure |
| **Principle teaching agent** | Interactive P-gent that teaches kgents philosophy | ✅ consumption.md Four Stances |

### The Polynomial Consumption Model (Future)

The stratification is the foundation for mode-dependent consumption:

```python
# Future: context-aware principle loading
PRINCIPLES_POLYNOMIAL = PolyAgent(
    positions=frozenset(["genesis", "poiesis", "krisis", "therapeia"]),
    directions=lambda stance: STANCE_SECTIONS[stance],
    transition=detect_stance_from_context
)
```

**Current state**: The polynomial spec exists in `consumption.md`. Implementation would:
1. Detect stance from user intent (e.g., "help me build" → Poiesis)
2. Load stance-appropriate subset (e.g., Poiesis → §5, §7, operational.md)
3. Surface relevant ADs based on task type

### Suggested Next Steps

1. **Quick wins** (can do now):
   - Add link checker to `scripts/validate.sh`
   - Add AD→impl path check to CI

2. **Medium effort** (next session):
   - Implement `concept.principles` AGENTESE node
   - Wire to Logos for `concept.principles.manifest` invocations

3. **Larger scope** (future planning):
   - Build stance detection into session start
   - Implement principle linting for PRs

---

*"The persona is a garden, not a museum. The principles are the soil; the ADs are the seasons."*
