# Work Betting: ASHC Economics Applied to Task Management

> *"If ASHC produces confident garbage, the penalty propagates up to Kent's reputation as developer."*
> — Applied reflexively: If Kent makes confident task estimates that fail, the penalty propagates to his work heuristics.

**Status:** Brainstorming
**Heritage:** ASHC Phase 2.75 (economy.py, adversary.py, causal_penalty.py)
**Session:** 2025-12-21

---

## The Insight

Every task you start is implicitly a bet. ASHC already has the machinery for:
- **Betting** on outcomes with confidence + stakes
- **Credibility tracking** that erodes with bullshit, recovers slowly
- **Adversarial accountability** — someone takes the other side
- **Causal penalty propagation** — blame flows to principles that misled

**The move:** Apply this to work management, not just compilation.

---

## Core Types (Adaptation from ASHC)

### WorkBet (analogous to ASHCBet)

```python
@dataclass(frozen=True)
class WorkBet:
    """A wager on task completion."""

    bet_id: str
    task_description: str

    # The wager
    estimated_hours: float      # My prediction
    confidence: float           # How sure am I? (0-1)
    stake: Decimal             # Focus tokens wagered

    # Causal attribution
    principles_cited: tuple[str, ...]  # e.g., ("depth_over_breadth", "tasteful")
    context_cited: tuple[str, ...]     # e.g., ("similar to ASHC Phase 2", "spec is clear")

    # Resolution
    actual_hours: float | None = None
    completed: bool = False

    @property
    def was_bullshit(self) -> bool:
        """High confidence + way off = bullshit"""
        if self.actual_hours is None:
            return False
        error_ratio = abs(self.actual_hours - self.estimated_hours) / max(self.estimated_hours, 0.1)
        return self.confidence >= 0.8 and error_ratio > 0.5  # 50%+ off despite being confident

    @property
    def calibration_error(self) -> float:
        """How far off was the estimate?"""
        if self.actual_hours is None:
            return 0.0
        return abs(self.actual_hours - self.estimated_hours) / max(self.estimated_hours, 0.1)
```

### WorkCredibility (analogous to ASHCCredibility)

```python
@dataclass
class WorkCredibility:
    """Kent's work estimation credibility."""

    credibility: float = 1.0  # 1.0 = trusted, 0.0 = "stop estimating"
    total_bets: int = 0
    successful_bets: int = 0  # Within 20% of estimate
    bullshit_count: int = 0   # High-confidence failures

    # Asymmetric penalties (from Taleb)
    BULLSHIT_PENALTY = 0.15   # One bullshit call
    SUCCESS_RECOVERY = 0.02   # One accurate estimate
    # Recovery cost: ~8 accurate estimates to recover from one bullshit

    def discount_estimate(self, raw_confidence: float) -> float:
        """
        Discount confidence claims by track record.

        If credibility = 0.7, a 90% confidence claim → 63% effective.
        """
        return raw_confidence * self.credibility
```

### PrincipleRegistry (reuse from causal_penalty.py)

The existing `PrincipleRegistry` already tracks:
- Which principles are cited for decisions
- Which principles lead to failures (blame)
- `is_predictive` — does this principle actually work?
- `is_discredited` — has this lost all credibility?

**For work:** Track heuristics like:
- "depth over breadth" — Does citing this predict task success?
- "tasteful > feature-complete" — Accurate or misleading?
- "quick wins first" — Does this help or just inflate scope?

---

## The Adversary

The adversary is time/opportunity cost. When you make a high-confidence estimate and miss badly:

```python
class WorkAdversary:
    """
    The implicit counterparty taking the other side of work bets.

    Adversary wins = focus tokens you could have spent elsewhere
    If adversary is getting rich, you're systematically overconfident
    """

    adversary_winnings: Decimal = Decimal("0")

    def settle_bet(self, bet: WorkBet) -> BetSettlement:
        if bet.was_bullshit:
            # High confidence + failure = adversary wins big
            payout = bet.stake * Decimal(str(bet.confidence))
            self.adversary_winnings += payout
            return BetSettlement(winner="adversary", payout=payout)
        # ...
```

---

## User Experience

### Session Start

```
📊 YOUR WORK CREDIBILITY: 0.78
   (Recovered from last week's bullshit on ASHC Phase 5 estimate)

🎯 PRINCIPLE HEALTH:
   ├── "depth over breadth": 0.92 (predictive)
   ├── "tasteful > complete": 0.85 (predictive)
   ├── "parallel work": 0.45 (often leads to context thrash)
   └── "quick wins first": 0.33 (discredited - usually inflates scope)

💰 ADVERSARY TRACKER:
   This week: adversary won 2/5 bets
   Your focus tokens: 12
   Adversary winnings: 8
```

### Starting a Task

```
🎲 TASK BET: "Wire ASHC betting to work management"

   Your estimate: 4 hours
   Your confidence: 75%

   ⚠️ CREDIBILITY ADJUSTMENT: 0.78 × 0.75 = 58% effective confidence

   Stakes:
   ├── If you finish in 4h: +3 focus tokens, +0.03 credibility
   ├── If you finish in 6h: -2 focus tokens, -0.05 credibility
   └── If you're >50% off at 75% confidence: BULLSHIT penalty (-0.15)

   Principles cited:
   ├── "depth over breadth" (0.92 credibility)
   └── "spec is clear" (0.71 credibility)

   [Proceed] [Adjust Estimate] [Lower Confidence]
```

### After Completion

```
📝 BET RESOLUTION: "Wire ASHC betting to work management"

   Estimate: 4h | Actual: 3.5h | Confidence: 75%

   ✅ WELL CALIBRATED (+0.01 bonus)
   ✅ Under estimate (conservative is fine)

   Credibility: 0.78 → 0.81
   Principles rewarded: "depth over breadth" (+0.01)

   Adversary status: Lost this round
```

---

## Integration Points

### 1. AGENTESE Paths

```
self.work.bet.*
  .start          # Place a bet on a task
  .resolve        # Resolve after completion
  .credibility    # View current credibility
  .principles     # View principle health
  .adversary      # View adversary status

time.trace.work.*
  .bets           # History of all work bets
  .calibration    # Am I getting better at estimates?
```

### 2. CLI Commands

```bash
kg work bet "Wire ASHC betting" --hours 4 --confidence 0.75
kg work resolve --actual 3.5
kg work status
kg work principles
```

### 3. Reuse from ASHC

| ASHC Module | Work Betting Reuse |
|-------------|-------------------|
| `economy.py` | ASHCBet → WorkBet, ASHCCredibility → WorkCredibility |
| `adversary.py` | AdversarialAccountability (nearly direct reuse) |
| `causal_penalty.py` | PrincipleRegistry (direct reuse for work heuristics) |
| `adaptive.py` | BetaPrior could inform "am I learning to estimate better?" |

---

## Why This Matters

### The Mirror Test Applied

*"Does K-gent feel like me on my best day?"*

On my best day:
- I'm honest about uncertainty
- I don't make promises I can't keep
- I learn from mistakes quickly
- I know which heuristics actually work

The betting system enforces this through skin in the game.

### Taleb's Asymmetry

> "Losing is fast, recovery is slow."

One bullshit estimate (-0.15 credibility) takes ~8 accurate estimates (+0.02 each) to recover from. This matches reality: one "I'll have it done in an hour" that takes 6 hours destroys trust faster than accurate estimates build it.

### Principle Accountability

*"Daring, bold, creative, opinionated but not gaudy"* — is this actually predictive of good work outcomes?

The PrincipleRegistry will tell you. If citing "bold" leads to scope explosions, its credibility erodes. If "depth over breadth" consistently predicts accurate estimates, it rises.

---

## Open Questions

1. **What currency?** Focus tokens? Hours? Reputation points?
2. **Session vs. all-time tracking?** Reset weekly or accumulate?
3. **UI surface?** CLI only? Web dashboard? AGENTESE node?
4. **Integration with existing todos?** TodoWrite? Separate system?
5. **Multi-task betting?** Portfolio of bets with risk allocation?

---

## Next Steps (If Proceeding)

1. [ ] Create `impl/claude/protocols/ashc/work_betting.py` with WorkBet, WorkCredibility
2. [ ] Wire to existing PrincipleRegistry from causal_penalty.py
3. [ ] Add AGENTESE node at `self.work.bet.*`
4. [ ] Create CLI commands (`kg work bet`, `kg work resolve`)
5. [ ] Build simple dashboard or status output

---

*"If you can't bet on it, you don't believe it."*

*"The adversary is always watching."*
