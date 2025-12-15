---
path: plans/devex/cli-quick-wins-wave4
status: active
progress: 60
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables:
  - k-gent-ambient
  - pedagogical-cli
  - joy-inducing-polish
session_notes: |
  Synthesized from docs/ideas-synthesis/crown-jewels.md, quick-wins.md, medium-complexity.md.
  Contains LOW EFFORT, HIGH IMPACT CLI commands not yet implemented.
  Parent plans complete: Agent Town Phase 4, REPL Wave 3.
  IMPLEMENT phase complete: 9 commands, 50 tests. Ready for QA.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
---

# CLI Quick Wins: Wave 4 Joy-Inducing

> *"The best ideas are trivial to implement and impossible to ignore."*

**Source**: Synthesized from 15 creative exploration sessions (2025-12-13)
**Status**: Extracted from idea inventory; ready for implementation
**Effort**: All items are effort 1-2 (implementable in 1 session each)

---

## Priority 1: H-gent Thinking Commands (CJ-12 to CJ-18)

These integrate the H-gent (Hegel/Jung/Lacan) philosophy agents into CLI commands.

| ID | Command | Agent | One-Liner | Effort |
|----|---------|-------|-----------|--------|
| CJ-12 | `kg shadow <target>` | H-jung | Show shadow content being repressed | 1 |
| CJ-13 | `kg dialectic <thesis> <antithesis>` | H-hegel | Synthesize two concepts instantly | 1 |
| CJ-14 | `kg project <text>` | H-jung | Where are you projecting? | 1 |
| CJ-15 | `kg gaps <text>` | H-lacan | What can't be said? (representational gaps) | 1 |
| CJ-16 | Shadow Scanner (in soul) | H-jung | "You claim X, shadow Y" | 1 |
| CJ-17 | Slippage Detector | H-lacan | "That's aspirational, not factual" | 1 |
| CJ-18 | "What Can't You Say?" | H-lacan | Surface unspeakable truths | 1 |

**Dependencies**: `agents/h/` (Jung, Hegel, Lacan implementations)
**Exit Criteria**: Each command works from CLI, produces thoughtful output

---

## Priority 2: Creative Commands (CJ-24 to CJ-28)

| ID | Command | Agent | One-Liner | Effort |
|----|---------|-------|-----------|--------|
| CJ-24 | `kg oblique` | A-gent | Brian Eno Oblique Strategies | 1 |
| CJ-25 | `kg constrain <topic>` | A-gent | Generate productive constraints | 1 |
| CJ-26 | `kg yes-and <idea>` | A-gent | Improv-style expansion | 1 |
| CJ-27 | `kg surprise-me` | A-gent | Random creative prompt | 1 |

**Implementation Pattern**:
```python
@handler("oblique")
async def cmd_oblique(ctx: Context) -> None:
    """Channel Brian Eno: serve a lateral thinking prompt."""
    coach = CreativityCoach()
    strategy = await coach.get_oblique_strategy()
    ctx.console.print(f"[bold magenta]{strategy}[/bold magenta]")
```

---

## Priority 3: Infrastructure Commands (CJ-35, CJ-36)

| ID | Command | Agent | One-Liner | Effort |
|----|---------|-------|-----------|--------|
| CJ-35 | `kg parse <input>` | P-gent | Universal parser CLI (show all strategies) | 2 |
| CJ-36 | `kg reality <task>` | J-gent | Classify DET/PROB/CHAOTIC | 1 |

---

## Priority 4: Cross-Pollination (CJ-37 to CJ-42)

| ID | Command | Agents | One-Liner | Effort |
|----|---------|--------|-----------|--------|
| CJ-37 | `kg approve <action>` | K + Judge | "Would Kent approve this?" | 2 |
| CJ-40 | Soul Tension Detector | K + Contradict | Detect held tensions | 1 |
| CJ-41 | Circuit Breaker Dashboard | U + Circuit + I | Live tool health | 2 |

---

## Quick Win Commands from Tier A (Priority 9.0+)

| ID | Command | One-Liner | Effort |
|----|---------|-----------|--------|
| QW-A01 | `kg why <statement>` | Recursive why until bedrock | 1 |
| QW-A02 | `kg tension` | List unresolved tensions | 1 |
| QW-A03 | `kg challenge <claim>` | Devil's Advocate mode | 1 |
| QW-A08 | `kg sparkline <numbers>` | `47 20 15 30` → `▅▂▁▃` | 1 |

---

## Wave 4 IMPLEMENT Complete (2025-12-14)

The following 9 commands were implemented in the IMPLEMENT phase:

| Command | Handler | Tests | Status |
|---------|---------|-------|--------|
| `kg sparkline` | `sparkline.py` | 7 | ✅ |
| `kg challenge` | `challenge.py` | 1 | ✅ |
| `kg oblique` | `oblique.py` | 5 | ✅ |
| `kg constrain` | `constrain.py` | 6 | ✅ |
| `kg yes-and` | `yes_and.py` | 4 | ✅ |
| `kg surprise-me` | `surprise_me.py` | 5 | ✅ |
| `kg project` | `project.py` | 5 | ✅ |
| `kg why` | `why.py` | 5 | ✅ |
| `kg tension` | `tension.py` | 4 | ✅ |

**Total Tests**: 50 passing
**REPL Shortcuts**: 11 (`/oblique`, `/constrain`, etc.)

---

## Already Implemented (DO NOT DUPLICATE)

The following ideas from the original docs are COMPLETE:

| Idea | Where Implemented | Tests |
|------|-------------------|-------|
| `kg soul vibe/drift/tense` | `handlers/soul.py` | K-gent 88 tests |
| Agent Town 7 citizens | `agents/town/` | 437 tests |
| AGENTESE REPL | `protocols/cli/repl.py` | 97 tests |
| Fuzzy matching | `repl_fuzzy.py` | Wave 3 |
| Session persistence | `repl_session.py` | Wave 3 |
| Pipeline composition | `repl.py:handle_composition` | Wave 2 |
| Observer/Umwelt | REPL Wave 2 | 7 tests |

---

## Sprint Suggestions

### Sprint A: Thinking Commands (1-2 days)
```
kg shadow, kg dialectic, kg project, kg gaps
```

### Sprint B: Creative Commands (1 day)
```
kg oblique, kg constrain, kg yes-and, kg surprise-me
```

### Sprint C: Infrastructure (1 day)
```
kg parse, kg reality, kg why, kg sparkline
```

### Sprint D: Cross-Pollination (2 days)
```
kg approve, Soul Tension Detector, Circuit Breaker Dashboard
```

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Commands Shipped | 15+ from this list |
| Test Coverage | Each command has unit tests |
| Effort Match | No command > 2 effort units |
| Joy Factor | Commands produce delightful output |

---

*"Quick wins build momentum. Momentum builds confidence. Confidence builds velocity."*
