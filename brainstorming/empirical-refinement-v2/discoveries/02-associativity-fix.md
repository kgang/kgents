# Discovery 2: The Associativity Fix

> *"The spec claims associativity. The math says otherwise."*

**Date**: 2025-12-28
**Status**: Critical Bug Identified, Fix Proposed
**Impact**: Experience Quality Operad composition laws are incorrect as stated

---

## The Bug

The Experience Quality Operad claims associativity for sequential and parallel composition:

```
Law: "(A >> B) >> C = A >> (B >> C)" [Associative]
```

However, the implementation uses **averaging** for arc_coverage composition:

```python
# parallel_compose (line 116 in composition.py)
combined_arc = (q_a.arc_coverage + q_b.arc_coverage) / 2
```

**Averaging is NOT associative.**

### Mathematical Proof

Let `compose(a, b) = (a + b) / 2`

```
Left  = compose(compose(a, b), c)
      = ((a + b)/2 + c) / 2
      = (a + b + 2c) / 4
      = a/4 + b/4 + c/2

Right = compose(a, compose(b, c))
      = (a + (b + c)/2) / 2
      = (2a + b + c) / 4
      = a/2 + b/4 + c/4

DEVIATION = Left - Right
          = (a/4 + b/4 + c/2) - (a/2 + b/4 + c/4)
          = -a/4 + c/4
          = (c - a) / 4
```

**Key Insight**: The deviation depends ONLY on `a` and `c`, not on `b`. The "middle" element is irrelevant to the associativity violation.

---

## Worst Case Analysis

**Maximum theoretical deviation**: 0.25

Achieved at: `a = 0, c = 1` (or `a = 1, c = 0`)

```
Example: a=0.0, b=0.5, c=1.0
  Left  = ((0 + 0.5)/2 + 1)/2 = 0.625
  Right = (0 + (0.5 + 1)/2)/2 = 0.375
  Deviation = 0.25 (maximum possible)
```

**Formula**: `|deviation| = |c - a| / 4`

This is a closed-form result, not a heuristic.

---

## Empirical Results (10,000 samples)

### Full Range [0, 1]

| Statistic | Value |
|-----------|-------|
| Max deviation | 0.247039 |
| Mean deviation | 0.083347 |
| Std deviation | 0.058834 |
| Median | 0.073770 |
| 99th percentile | 0.224443 |
| 95th percentile | 0.193064 |

### Distribution

| Range | Count | Percentage |
|-------|-------|------------|
| [0.00, 0.01) | 753 | 7.5% |
| [0.01, 0.05) | 2,828 | 28.3% |
| [0.05, 0.10) | 2,794 | 27.9% |
| [0.10, 0.15) | 2,017 | 20.2% |
| [0.15, 0.20) | 1,218 | 12.2% |
| [0.20, 0.25) | 390 | 3.9% |

**36% of random triplets have deviation > 0.10**

---

## Realistic Range Analysis

In practice, quality scores cluster in narrower ranges:

### Arc Coverage [0.3, 0.8] (typical game runs)

| Statistic | Value |
|-----------|-------|
| Max deviation | 0.111719 |
| Mean deviation | 0.031942 |
| 99th percentile | 0.092682 |

**Maximum possible in this range**: `|0.8 - 0.3| / 4 = 0.125`

### Contrast Scores [0.4, 0.8] (narrower typical range)

| Statistic | Value |
|-----------|-------|
| Max deviation | 0.089010 |
| Mean deviation | 0.022970 |
| 99th percentile | 0.068023 |

**Maximum possible in this range**: `|0.8 - 0.4| / 4 = 0.100`

---

## Fix Comparison

### Alternative Compositions Tested

| Composition | Formula | Max Dev | Mean Dev | Associative? | Has Identity? |
|-------------|---------|---------|----------|--------------|---------------|
| **Average** | (a+b)/2 | 0.247 | 0.083 | NO | None |
| **Geometric Mean** | sqrt(ab) | 0.248 | 0.078 | NO | 1.0 (approx) |
| **Minimum** | min(a,b) | 0.000 | 0.000 | YES | 1.0 |
| **Maximum** | max(a,b) | 0.000 | 0.000 | YES | 0.0 |
| **Product** | a*b | 0.000 | 0.000 | YES | 1.0 |
| **Harmonic Mean** | 2ab/(a+b) | 0.169 | 0.054 | NO | None |

### Semantic Analysis

| Composition | Preserves Range | Zero Absorbing | Interpretation |
|-------------|-----------------|----------------|----------------|
| Average | Yes | No | "Quality blends" |
| Minimum | Yes | Yes | "Weakest link" |
| Maximum | Yes | No (1 absorbs) | "Best component" |
| Product | Yes | Yes | "Multiplicative degradation" |

---

## The Fix

### Option A: Switch to Product (Recommended)

**Rationale**: Product composition `a * b` is:
- Strictly associative: `(a*b)*c = a*(b*c)`
- Has identity element: `a * 1 = a`
- Floor-compatible: `a * 0 = 0` (aligns with floor gate semantics)
- Semantically sound: quality degrades multiplicatively
- Preserves range: `[0,1] * [0,1] = [0,1]`

**Trade-off**: Values drift toward zero faster. A sequence of 0.8 qualities:
- Average: 0.8, 0.8, 0.8 -> final 0.8
- Product: 0.8 * 0.8 * 0.8 = 0.512

This is actually desirable: it means "consistently good" matters.

### Option B: Switch to Minimum

**Rationale**: Minimum composition `min(a, b)` is:
- Strictly associative
- Has identity: `min(a, 1) = a`
- "Weakest link" semantics
- Floor-compatible: `min(a, 0) = 0`

**Trade-off**: May be too pessimistic. One bad segment tanks everything.

### Option C: Keep Average with Honest Tolerance

If average is preferred for its "blending" semantics, update the spec to be honest:

```
Law: "assoc_par"
     "(A || B) || C ≈ A || (B || C)"
     "Parallel composition is approximately associative"
     "Deviation bounded by |c - a| / 4"
     "For typical quality ranges [0.3, 0.8], max deviation is 0.125"
```

**Trade-off**: Not truly associative. Composition order matters.

---

## Recommendation

**Use Product for sequential composition**, keeping current strategies for others:

```python
# Sequential: Product (multiplicative degradation)
def sequential_compose(q_a, q_b):
    combined_contrast = q_a.contrast * q_b.contrast  # Was: average
    combined_arc = q_a.arc_coverage * q_b.arc_coverage  # Was: chain

# Parallel: Maximum for contrast (dominant), Product for arc
def parallel_compose(q_a, q_b):
    combined_contrast = max(q_a.contrast, q_b.contrast)  # Keep: max
    combined_arc = q_a.arc_coverage * q_b.arc_coverage   # Was: average

# Nested: Weighted blend (intentionally non-associative for nesting)
# Keep current weighted blend - nesting is different semantically
```

This gives:
- **Sequential**: Associative, floor-compatible, "earn your quality"
- **Parallel**: Associative, "best of both worlds" for contrast
- **Nested**: Weighted (different semantics, not meant to be iterated)

---

## Spec Update

Replace in `spec/theory/experience-quality-operad.md`:

**BEFORE** (Lines 448-449):
```python
# Arc: Weighted mean (both contribute)
combined_arc = (q_a.arc_coverage + q_b.arc_coverage) / 2
```

**AFTER**:
```python
# Arc: Product (multiplicative, associative)
# Both experiences must contribute to arc coverage
combined_arc = q_a.arc_coverage * q_b.arc_coverage
```

**Add note after line 463**:
```python
# NOTE: Product composition ensures strict associativity
# while preserving floor gate semantics (0 * x = 0).
# See: brainstorming/empirical-refinement-v2/discoveries/02-associativity-fix.md
```

Update law section (line 547-551):
```python
Law(
    "assoc_par",
    "(A || B) || C = A || (B || C)",  # Remove "approximately"
    "Parallel composition is strictly associative (product semantics)",
),
```

---

## Verdict

The claim "deviation < 0.05" is **FALSE**.

- **Maximum deviation**: 0.25 (proven mathematically)
- **Mean deviation**: 0.083 (empirically verified)
- **99th percentile**: 0.224

The spec must either:
1. **Fix the composition** (use product) - RECOMMENDED
2. **Update the tolerance claim** to 0.25 and acknowledge non-associativity

Current spec law `"(A || B) || C = A || (B || C)"` is provably false for averaging composition.

---

## Data Files

- Raw deviation data: `data/associativity-deviations.csv`
- Contains 10,000 rows: `a, b, c, left, right, deviation`

---

*"The proof IS the deviation. The fix IS the product."*
