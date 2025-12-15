---
path: plans/ideas/master-plan-current
status: active
progress: 35
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [reactive-substrate, soul-quick-wins]
session_notes: |
  Cycle 1 HARVEST & TRIAGE complete. Ideas mapped to architecture.
  Cycle 2 (K-gent + I-gent Quick Wins) COMPLETE: 7 commands, 25 tests.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  STRATEGIZE: touched
  ACT: touched
  IMPLEMENT: touched
  REFLECT: touched
---

# Master Plan: Idea Cultivation — Current Capabilities

> *"The noun is a lie. There is only the rate of change."*

**Created**: 2025-12-14
**Source**: Grand Initiative Idea Cultivation Cycle 1
**Focus**: Map 700+ brainstorm ideas to what EXISTS now

---

## Executive Summary

After reviewing 15 creative sessions (700+ ideas), kentspicks.md, and the current implementation, here is the synthesis:

### What EXISTS (Ready to Wire)

| Component | Location | Status | Test Coverage |
|-----------|----------|--------|---------------|
| **K-gent Soul** | `agents/k/` | Complete | 389+ tests |
| **Reactive Primitives** | `agents/i/reactive/` | Wave 1-2 done | SparklineWidget, BarWidget, DensityField |
| **CLI Handlers** | `protocols/cli/handlers/` | 30+ commands | soul, approve, dashboard |
| **YIELD Governance** | `weave/yield_handler.py` | Working | Turn-gents Phase 5 |
| **H-gents (Introspection)** | `agents/h/` | Impl exists | Hegel, Jung, Lacan |
| **Flux Streams** | `agents/k/flux.py` | Working | KgentFlux |

### Gap Analysis: Ideas vs Reality

| Idea Category | Ideas Count | % Implemented | Gap |
|---------------|-------------|---------------|-----|
| K-gent Soul Commands | 73 | 60% | Quick CLI wrappers needed |
| I-gent Visualization | 60 | 40% | Reactive primitives exist, screens need wiring |
| H-gent Introspection | 55 | 30% | Core agents exist, CLI missing |
| Cross-Pollination | 62 | 5% | Most require composition work |
| U-gent Tools | 50 | 20% | MCP exists, dashboard missing |

---

## Tier 1: IMMEDIATE (1-2 hours each)

These are **CLI wrappers around existing code**.

### K-gent Soul Quick Wins

| Priority | Idea | Implementation | Status |
|----------|------|----------------|--------|
| **10.0** | `kg soul vibe` | One-liner eigenvector summary | **DONE** (2 tests) |
| **10.0** | `kg soul drift` | Compare eigenvectors vs yesterday | **DONE** (2 tests) |
| **10.0** | `kg soul compare <text>` | Text similarity to eigenvectors | Pending |
| **10.0** | `kg soul why` | Quick CHALLENGE mode | **DONE** (1 test) |
| **10.0** | `kg soul tense` | Current tension detection | **DONE** (2 tests) |

**Implementation pattern**:
```python
# In soul.py, add subcommand handlers:
async def _handle_vibe(soul, json_mode, ctx):
    """kg soul vibe - One-liner eigenvector summary."""
    brief = soul.manifest_brief()
    # Format: "🎭 Playful (0.75), 🔬 Abstract (0.92), ✂️ Minimal (0.15)"
    ...
```

### I-gent CLI Wrappers

| Priority | Idea | Implementation | Status |
|----------|------|----------------|--------|
| **9.3** | `kg sparkline <nums>` | SparklineWidget.project(CLI) | **DONE** (6 tests) |
| **9.3** | `kg weather` | Agent density summary | **DONE** (4 tests) |
| **8.7** | `kg density <text>` | Text as density field | Pending |
| **8.0** | `kg glitch <text>` | GlyphWidget with high entropy | **DONE** (5 tests) |

**Implementation pattern**:
```python
# New file: handlers/igent.py already exists, add commands:
def cmd_sparkline(args, ctx):
    values = [float(x) for x in args]
    spark = SparklineWidget(SparklineState(values=tuple(values)))
    print(spark.project(RenderTarget.CLI))
```

### H-gent CLI Quick Wins

| Priority | Idea | Implementation | Exists? |
|----------|------|----------------|---------|
| **10.0** | `kg shadow` | JungAgent shadow analysis | JungAgent exists |
| **10.0** | `kg dialectic <a> <b>` | HegelAgent synthesis | HegelAgent exists |
| **10.0** | `kg gaps` | LacanAgent gap surfacing | LacanAgent exists |
| **9.3** | `kg mirror` | Full introspection | FullIntrospection exists |

**Implementation pattern**:
```python
# New file: handlers/hgent.py
async def cmd_shadow(args, ctx):
    from agents.h import JungAgent
    agent = JungAgent()
    result = await agent.analyze(target_text)
    print(result.shadow_inventory)
```

---

## Tier 2: THIS WEEK (1-2 days each)

These require **wiring existing components together**.

### Cross-Pollination: K + I

| Priority | Combo | What to Build | Components |
|----------|-------|---------------|------------|
| **10.0** | C03 | Living Garden Visualization | Flux events → DensityField |
| **9.3** | C26 | Soul-Aware Garden | KgentFlux + DensityField + eigenvectors |

**Implementation**:
```python
# agents/i/screens/garden.py
class GardenScreen:
    def __init__(self, soul: KgentSoul, flux: KgentFlux):
        self.field = DensityField(width=80, height=40)
        self.soul = soul
        flux.subscribe(self._on_event)

    async def _on_event(self, event: SoulEvent):
        # Update density field based on soul health
        ...
```

### Cross-Pollination: K + Judge

| Priority | Combo | What to Build | Components |
|----------|-------|---------------|------------|
| **10.0** | C01 | "Would Kent Approve?" | Judge + PersonaQuery |
| **9.3** | C04 | Soul Tension Detector | Contradict + eigenvectors |

**Implementation**: The approve.py handler exists but is for YIELD turns. Add:
```python
# handlers/soul.py or new handlers/judge.py
async def cmd_would_kent_approve(args, ctx):
    """kg approve <action> - Check if Kent would approve."""
    from agents.a import JudgeAgent
    from agents.k import KgentSoul

    soul = _get_soul()
    judge = JudgeAgent(ground=soul.eigenvectors)
    verdict = await judge.invoke(action)
    ...
```

### Dashboard Integration

| Priority | Idea | What to Build | Components |
|----------|------|---------------|------------|
| **9.3** | Circuit Breaker Dashboard | Health visualization | U-gent + BarWidget |
| **8.7** | Eigenvector Pulse | Live breathing chart | SparklineWidget + soul.eigenvectors |

---

## Tier 3: PORTFOLIO PIECES (1 week each)

These are **showcase-worthy demos**.

### The Ultimate Dashboard (C37)

```
╭────────────────────────────────────────────────────────────────────╮
│ KGENTS SYSTEM DASHBOARD                                            │
├────────────────────────────────────────────────────────────────────┤
│ ┌─ Tool Health (U-gent + Circuit) ─────────────────────────────┐  │
│ │ 🟢 web_search    🟢 db_query    🟡 payment    🔴 legacy      │  │
│ └───────────────────────────────────────────────────────────────┘  │
│ ┌─ Soul State (K-gent) ──────────────────────────────────────────┐ │
│ │ Aesthetic: ▁▁▁▁░░░░░░ 0.15                                   │ │
│ │ Abstract:  █████████░ 0.92                                   │ │
│ │ Joy:       ████████░░ 0.75                                   │ │
│ └───────────────────────────────────────────────────────────────┘  │
╰────────────────────────────────────────────────────────────────────╯
```

### Voice Calibration (Session 3)

Train eigenvectors on writing samples:
1. User pastes text samples
2. System analyzes for eigenvector coordinates
3. Adjusts PersonaGarden based on evidence

---

## Architecture Alignment

### What the Ideas Want vs What Exists

| Idea Pattern | Architectural Reality |
|--------------|----------------------|
| "Live dashboard" | Reactive primitives (Signal, Widget) exist |
| "Entropy distortion" | entropy_to_distortion() in reactive/entropy.py |
| "CLI one-liners" | Handler pattern in protocols/cli/handlers/ |
| "Cross-pollination" | Agent composition via functors |
| "Soul governance" | KgentSoul + SemanticGatekeeper + YIELD |

### Key Files to Wire

1. **handlers/soul.py** (1500 lines) - Add subcommands: vibe, drift, compare, tense
2. **handlers/igent.py** - Add: sparkline, density, glitch, weather
3. **handlers/hgent.py** (NEW) - Add: shadow, dialectic, gaps, mirror
4. **agents/i/screens/garden.py** (NEW) - Living garden visualization

---

## Recommended Execution Order

### Week 1: Soul Quick Wins
1. `kg soul vibe` - 2 hours
2. `kg soul drift` - 2 hours
3. `kg soul compare` - 4 hours
4. `kg soul tense` - 2 hours
5. `kg soul why` - 1 hour (already works, just add alias)

### Week 2: I-gent CLI
1. `kg sparkline` - 2 hours
2. `kg weather` - 4 hours
3. `kg density` - 2 hours
4. `kg glitch` - 1 hour

### Week 3: H-gent CLI
1. `kg shadow` - 4 hours
2. `kg dialectic` - 4 hours
3. `kg gaps` - 4 hours
4. `kg mirror` - 4 hours

### Week 4: Cross-Pollination
1. C01: Would Kent Approve - 8 hours
2. C03: Living Garden - 8 hours
3. C04: Soul Tension Detector - 8 hours

---

## Metrics to Track

| Metric | Current | Target | Why |
|--------|---------|--------|-----|
| CLI commands | **37+** | 50+ | More accessible surface area |
| Quick wins implemented | **7** | 20 | From session Crown Jewels |
| Cross-pollinations | 0 | 5 | Composition proves the architecture |
| Demo-worthy screens | 1 | 5 | Portfolio pieces |

### Cycle 2 Progress (2025-12-14)
- **Soul commands**: +4 (vibe, drift, tense, why)
- **I-gent commands**: +3 (sparkline, weather, glitch)
- **New tests**: +25 (8 in soul, 17 in igent)
- **Entropy spent**: 0.08

---

## Crown Jewels Summary (Priority 10.0)

From all sessions, these are the **perfect 10s**:

| ID | Project | Session | Status |
|----|---------|---------|--------|
| S3-2 | `kg soul vibe` | K-gent | **SHIPPED** |
| S3-3 | `kg soul drift` | K-gent | **SHIPPED** |
| S3-51 | `kg soul compare` | K-gent | Pending |
| S4-11 | Shadow Scanner (`kg shadow`) | H-gent | **NEXT CYCLE** |
| S4-42 | `kg dialectic` | H-gent | **NEXT CYCLE** |
| S12-P01 | `kg parse` | P-gent | Needs P-gent wiring |
| S12-J01 | `kg reality` | J-gent | Needs J-gent wiring |
| C01 | Would Kent Approve | Cross | Week 4 |
| C03 | Living Garden | Cross | Week 4 |

---

## The 60-Second Demo (Session 15 Vision)

```
$ kg soul vibe
🎭 Playful (0.75), 🔬 Abstract (0.92), ✂️ Minimal (0.15)

$ kg soul drift
Since yesterday: Joy +0.02, Aesthetic -0.01. You're loosening up.

$ kg shadow
Your system claims "helpful" but shadows "capacity to obstruct."
Integration path: Acknowledge when NOT helping is the right choice.

$ kg dialectic "move fast" "be thorough"
Synthesis: "Iterative depth" - fast first pass, thorough where it matters.

$ kg garden --live
[Animated: agents breathing, events flowing, health pulsing]
```

---

## Next Steps

1. **Today**: Implement `kg soul vibe` as proof of concept
2. **This week**: Complete Tier 1 quick wins
3. **Next week**: Wire cross-pollinations
4. **Portfolio deadline**: Have 5 demo-worthy screens

---

*"Individual agents are interesting. Agents together? That's where the magic happens."*

— Session 14 closing thought, now operationalized
