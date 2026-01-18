# Calibration Corpus Management

> *"Evidence over intuition. Real work over synthetic examples."*

**Purpose**: Guide for populating and managing the Galois Loss calibration corpus with authentic examples derived from actual kgents work.

---

## The Problem: LLM Tautologies

When we generate synthetic examples like "Write a haiku about rain" and then ask an LLM to classify them, we're often measuring the LLM's ability to pattern-match on surface features — not genuine semantic depth.

**The Solution**: Use verbatim examples from actual work:
- Git commit messages (L5 Execution)
- Plan decisions (L3-L4 Goals/Specs)
- Meta.md learnings (L1-L6 across all layers)
- Kent's voice anchors (L1-L2 Axioms/Values)
- Witness marks (all layers, ground truth)

---

## Corpus Files

| File | Purpose | Source |
|------|---------|--------|
| `calibration_corpus.json` | Original synthetic corpus | LLM-generated examples |
| `calibration_corpus_real.json` | **USE THIS** — Real examples | Extracted from repo |

Always prefer `calibration_corpus_real.json` for validation work.

---

## Three Ways to Populate

### 1. Extract from Git History (One-time)

Already done. See `calibration_corpus_real.json` with 67 verbatim entries.

To add more:
```bash
# Find relevant commits
git log --oneline --all --format="%s" | grep -i "feat\|fix\|refactor"

# Add to corpus as L5 entries
```

### 2. Interview Kent for Axioms (Monthly)

Use the interview protocol at `docs/skills/axiom-interview-protocol.md`.

**Key questions**:
- "What principle would you never violate?"
- "When you feel disgust at code, what triggers it?"
- "What decision do you wish you'd written down?"

After interview, transcribe verbatim quotes to `calibration_corpus_real.json` with:
```json
{
  "id": "INTERVIEW-L1-XXX",
  "content": "[verbatim Kent quote]",
  "expected_layer": 1,
  "source": "axiom-interview-session-YYYY-MM-DD",
  "extraction_method": "interview"
}
```

### 3. Automatic Contribution from Witness Marks (Ongoing)

The `CalibrationContributor` service listens for marks with qualifying tags:

**Qualifying tags**:
- `axiom-interview` → L1 (Axiom)
- `eureka` → L1-L2 (Breakthrough)
- `veto` → L1-L2 (Somatic rejection)
- `taste` → L2 (Aesthetic judgment)
- `gotcha` → L6 (Discovered trap)
- `lesson` → L6 (Learned pattern)
- `calibration` → Any layer (explicit)

**Usage**:
```bash
# During work, tag significant moments
km "Discovered that @node runs at import time" --tag gotcha --tag calibration

# The contributor auto-adds to calibration_corpus_real.json
```

**Starting the contributor**:
```python
from services.zero_seed.galois.calibration_contributor import get_calibration_contributor

contributor = get_calibration_contributor()
await contributor.start()
```

Or run standalone:
```bash
python -m services.zero_seed.galois.calibration_contributor
```

---

## Layer Reference

| Layer | Name | Loss Range | Example Content |
|-------|------|------------|-----------------|
| 1 | Axiom | 0.00-0.05 | "Agency requires justification" |
| 2 | Value | 0.05-0.15 | "Tasteful > feature-complete" |
| 3 | Goal | 0.15-0.30 | "Ship trail-to-crystal by Week 6" |
| 4 | Spec | 0.30-0.45 | "Mark creation < 50ms (P95)" |
| 5 | Execution | 0.45-0.60 | "feat(witness): Add Crystal Compression" |
| 6 | Reflection | 0.60-0.75 | "SSE stale closures: use refs for fresh handlers" |
| 7 | Representation | 0.75-1.00 | "This README documents the API endpoints..." |

---

## Validation Protocol

Before using corpus for G1 Calibration:

1. **Check authenticity**: Every entry should trace to a real source
2. **Verify extraction_method**: Should be `verbatim`, `interview`, or `automatic`
3. **No synthetic examples**: Remove entries with generic content
4. **Layer distribution**: Ensure coverage across all 7 layers

**Current distribution** (calibration_corpus_real.json):
- L1: 10 entries
- L2: 13 entries
- L3: 8 entries
- L4: 11 entries
- L5: 12 entries
- L6: 10 entries
- L7: 3 entries

**Target**: 100+ entries with balanced distribution.

---

## Anti-Patterns

1. **Synthetic inflation**: Adding LLM-generated "example" content
2. **Paraphrasing early**: Losing Kent's exact words
3. **Over-curating**: Smoothing rough edges (Anti-Sausage violation)
4. **Skipping sources**: Entries without traceable origins
5. **Layer guessing**: Assigning layers without justification

---

*Last Updated: 2026-01-17*
