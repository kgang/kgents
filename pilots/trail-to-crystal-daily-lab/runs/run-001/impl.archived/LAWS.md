# Pilots Webapp Laws

> *Precise, dense, minimal. These laws govern all pilot implementations.*

---

## Universal Laws (All Pilots)

| Law | Statement | Enforcement |
|-----|-----------|-------------|
| **U1** | No shame mechanics | UI never penalizes gaps, failures, or absence |
| **U2** | Witnessed, not surveilled | System collaborates; never judges |
| **U3** | Compression preserves meaning | Artifacts are memory, not summary |
| **U4** | Transparency over opacity | All transformations are explainable |
| **U5** | Ritual over metric | Closure is ceremony, not measurement |

---

## Daily Lab Laws (L1-L5)

| Law | Name | Statement | UI Binding |
|-----|------|-----------|------------|
| **L1** | Day Closure | A day completes only when a crystal is produced | `DayClosurePrompt` appears after 6 PM |
| **L2** | Intent First | Actions without declared intent are provisional | `MarkCaptureInput` prompts for tag/reason |
| **L3** | Noise Quarantine | High-loss marks cannot define narrative | Crystal drops noise, keeps signal |
| **L4** | Compression Honesty | All crystals disclose what was dropped | `CompressionHonesty` component, warm messaging |
| **L5** | Provenance | Every crystal statement links to marks | `source_marks` array required |

### Daily Lab Quality Attributes (QA)

| QA | Assertion | Measurement |
|----|-----------|-------------|
| **QA-1** | Lighter than to-do list | Mark capture < 5 seconds |
| **QA-2** | Honest gaps, no shame | `GapDetail` uses warm messaging |
| **QA-3** | Witnessed, not surveilled | Capture is voluntary, review is opt-in |
| **QA-4** | Crystal is memory artifact | Insight + significance, not bullet list |

---

## Zero Seed Laws (Z1-Z5)

| Law | Name | Statement | UI Binding |
|-----|------|-----------|------------|
| **Z1** | Axiom Immutability | Fixed points (loss < 1%) cannot be amended | `LayerPyramid` locks L1 entries |
| **Z2** | Derivation Chain | Higher layers derive from lower | Layer assignment via Galois loss |
| **Z3** | Contradiction Surfacing | Conflicts must be resolved, not hidden | Amendment history shows synthesis |
| **Z4** | Loss IS Layer | Galois loss determines epistemic tier | `assignLayer` API binding |
| **Z5** | Fixed Point IS Axiom | Semantic stability survives R/C cycles | `detectFixedPoint` API binding |

### Zero Seed Layer Structure

| Layer | Name | Loss Range | Description |
|-------|------|------------|-------------|
| L1 | Axiom | < 0.01 | Self-evident, survives all R/C |
| L2 | Value | 0.01-0.05 | Derives from axioms |
| L3 | Goal | 0.05-0.15 | Translates values to outcomes |
| L4 | Strategy | 0.15-0.30 | Approaches to achieve goals |
| L5 | Tactic | 0.30-0.50 | Specific implementation choices |
| L6 | Action | 0.50-0.70 | Concrete steps |
| L7 | Representation | > 0.70 | Surface-level expression |

---

## WARMTH Calibration

All pilots must implement WARMTH:

```
W - Witnessed (not surveilled)
A - Acknowledged (gaps are data)
R - Respectful (no shame mechanics)
M - Meaningful (artifacts over metrics)
T - Transparent (compression is honest)
H - Human-first (ritual over automation)
```

### Anti-Patterns (Violations)

| Pattern | Violation | Law Broken |
|---------|-----------|------------|
| Hustle theater | Optimizing for "more marks" | U5, QA-1 |
| Gap shame | Treating untracked time as error | U1, QA-2 |
| Surveillance drift | Behavior changes due to tracking | U2, QA-3 |
| Summary flatness | Compression erases meaning | U3, QA-4 |
| Ritual burden | Closure feels like homework | U5, L1 |

---

## Implementation Checklist

For each pilot feature, verify:

- [ ] Does not introduce shame mechanics (U1)
- [ ] Supports opt-in interaction only (U2)
- [ ] Preserves meaning in compression (U3)
- [ ] Explains all transformations (U4)
- [ ] Feels like closure, not measurement (U5)

---

*"The proof IS the decision. The mark IS the witness."*
