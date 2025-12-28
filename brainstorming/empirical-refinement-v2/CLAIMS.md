# Bold Claims (Falsifiable)

> *"A claim without a number is just an opinion."*

---

## Claim 1: Galois Correlation 🎲

**The Bet**: Galois loss L(P) predicts task failure rate with **r > 0.6**

- Status: `PARTIALLY_CONFIRMED`
- Evidence: `discoveries/01-galois-bet.md`
- Falsification: r < 0.4 would break the theory
- **Actual Result**: r = 0.5624 (meaningful signal, but below threshold)

**Key Finding**: The correlation is real but the loss proxy confuses syntactic complexity with semantic difficulty. State machines scored high loss but low difficulty because the PATTERN is well-known.

---

## Claim 2: Bounded Associativity 🔧

**The Bet**: Quality composition deviation **< 0.05** for all realistic inputs

- Status: `FALSIFIED` ❌
- Evidence: `discoveries/02-associativity-fix.md`
- **Actual Result**: Maximum deviation = **0.25** (5x higher than claimed!)

**Key Finding**: Averaging composition `(a+b)/2` is mathematically proven non-associative. Deviation formula: `|c - a| / 4`. **Recommended fix**: Use product composition `a * b` which is strictly associative.

---

## Claim 3: Mirror Thresholds 🪞

**The Bet**: Kent's felt thresholds match theory within **±0.1**

- Status: `PENDING_KENT` ⏳
- Evidence: `discoveries/03-mirror-calibration.md`
- Falsification: Kent's intuitions systematically diverge from numbers

**Ready**: 20 test items prepared, awaiting Kent's ratings.

---

## Claim 4: 200-Line Kernel 💎

**The Bet**: The full kgents system derives from **<200 lines** of axioms

- Status: `CONFIRMED` ✅
- Evidence: `discoveries/04-minimal-kernel.md`
- **Actual Result**: 77 lines (38.5% of 200-line budget!)

**Key Finding**: Compression ratio 58:1. All 7 design principles and 7 governance articles derive from just 3 irreducible axioms (Entity, Morphism, Mirror).

---

## Scoreboard

| Claim | Predicted | Actual | Verdict |
|-------|-----------|--------|---------|
| Galois r | > 0.6 | **0.5624** | PARTIAL ⚠️ |
| Assoc ε | < 0.05 | **0.25** | FALSE ❌ |
| Threshold δ | < 0.1 | _pending_ | AWAITING 🕐 |
| Kernel size | < 200 | **77** | TRUE ✅ |

---

## Summary

**2 claims tested with data:**
- 1 CONFIRMED (Minimal Kernel - dramatically under budget)
- 1 FALSIFIED (Associativity - 5x worse than claimed, fix proposed)

**1 claim partially confirmed:**
- Galois correlation is meaningful (r = 0.56) but below bold threshold

**1 claim awaiting human input:**
- Mirror calibration ready for Kent

---

*Updated: 2025-12-28*
