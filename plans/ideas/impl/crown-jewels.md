---
path: ideas/impl/crown-jewels
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [ideas/impl/cross-synergy]
session_notes: |
  All 45+ Crown Jewels (Perfect 10.0 priority ideas).
  Deep implementation notes with dependencies and design specs.
  These are the "must ship" features that define kgents.
---

# Crown Jewels Implementation Plan

> *"These are the gems. Ship these, and the system sells itself."*

**Definition**: Priority = 10.0 (Perfect Score)
**Total Count**: 45+ ideas
**Characteristic**: High FUN + High SHOWABLE + High PRACTICAL + Low EFFORT

---

## Crown Jewels by Session

### Session 2: Archetypes

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-01 | `kg whatif` | Core Uncertain archetype; shows 3 alternatives instantly |

#### CJ-01: `kg whatif` — Show Me 3 Alternatives

**Priority**: 10.0 | **Effort**: 1 | **Session**: 2

**One-Liner**: "What if I solved this differently?"

**Implementation**:
```python
# impl/claude/protocols/cli/handlers/whatif.py

@handler("whatif")
async def cmd_whatif(ctx: Context, prompt: str) -> None:
    """Show 3 alternative approaches to any problem."""
    uncertain = UncertainAgent()
    alternatives = await uncertain.generate_alternatives(prompt, n=3)

    for i, alt in enumerate(alternatives, 1):
        ctx.console.print(f"[bold]{i}. {alt.title}[/bold]")
        ctx.console.print(f"   {alt.description}")
        ctx.console.print(f"   Reality: {alt.reality_type} | Confidence: {alt.confidence:.0%}")
```

**Output Example**:
```
$ kg whatif "refactor authentication"

1. JWT with Redis Cache
   Stateless tokens, fast verification, horizontal scaling
   Reality: DETERMINISTIC | Confidence: 92%

2. OAuth2 with External Provider
   Delegate auth complexity, focus on core product
   Reality: PROBABILISTIC | Confidence: 78%

3. Zero-Knowledge Proof System
   Privacy-preserving, cutting-edge, complex
   Reality: CHAOTIC | Confidence: 45%
```

**Dependencies**: UncertainAgent, RealityClassifier
**Files**: `handlers/whatif.py`, `agents/uncertain/alternatives.py`
**Tests**: Property tests for N alternatives, reality classification accuracy

---

### Session 3: K-gent Soul

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-02 | `kg soul vibe` | One-liner personality fingerprint |
| CJ-03 | `kg soul drift` | Track personality evolution |
| CJ-04 | `kg soul tense` | Surface held tensions |
| CJ-05 | `kg soul avoiding` | Detect avoidance patterns |
| CJ-06 | `kg soul compare` | Text similarity scoring |
| CJ-07 | `kg soul minimum` | 80/20 principle extraction |
| CJ-08 | `kg soul why` | Dialectical challenge |
| CJ-09 | "Does This Sound Like Me?" | Paste text → match % |
| CJ-10 | Daily Tension | Today's eigenvector tension |
| CJ-11 | Dangerous Op Warning | Red flash for risky ops |

#### CJ-02: `kg soul vibe` — One-Liner Soul State

**Priority**: 10.0 | **Effort**: 1 | **Session**: 3

**One-Liner**: "🎭 Playful, 🔬 Abstract, ✂️ Minimal"

**Implementation**:
```python
# impl/claude/protocols/cli/handlers/soul.py

@handler("soul", "vibe")
async def cmd_soul_vibe(ctx: Context) -> None:
    """One-liner soul state from eigenvectors."""
    kgent = KgentAgent.from_context(ctx)
    eigens = await kgent.get_eigenvectors()

    # Map eigenvectors to emoji + descriptors
    vibe_parts = []
    if eigens.joy > 0.7:
        vibe_parts.append("🎭 Playful")
    if eigens.categorical > 0.8:
        vibe_parts.append("🔬 Abstract")
    if eigens.aesthetic < 0.3:
        vibe_parts.append("✂️ Minimal")

    ctx.console.print(", ".join(vibe_parts) or "🌫️ Neutral")
```

**Output Example**:
```
$ kg soul vibe
🎭 Playful, 🔬 Abstract, ✂️ Minimal
```

**Dependencies**: KgentAgent, Eigenvectors
**Files**: `handlers/soul.py`, `agents/k/eigenvectors.py`

---

#### CJ-03: `kg soul drift` — Personality Evolution Tracker

**Priority**: 10.0 | **Effort**: 1 | **Session**: 3

**One-Liner**: "You're 0.03 more austere than yesterday"

**Implementation**:
```python
@handler("soul", "drift")
async def cmd_soul_drift(ctx: Context) -> None:
    """Show eigenvector changes over time."""
    kgent = KgentAgent.from_context(ctx)
    current = await kgent.get_eigenvectors()
    yesterday = await kgent.get_historical_eigenvectors(days_ago=1)

    if yesterday is None:
        ctx.console.print("No historical data yet. Check back tomorrow!")
        return

    diffs = current.diff(yesterday)
    for name, delta in diffs.items():
        if abs(delta) > 0.01:
            direction = "more" if delta > 0 else "less"
            ctx.console.print(f"You're {abs(delta):.2f} {direction} {name}")
```

**Output Example**:
```
$ kg soul drift
You're 0.03 more austere than yesterday
You're 0.05 less joyful than yesterday
```

---

#### CJ-04: `kg soul tense` — Surface Held Tensions

**Priority**: 10.0 | **Effort**: 1 | **Session**: 3

**Implementation**:
```python
@handler("soul", "tense")
async def cmd_soul_tense(ctx: Context) -> None:
    """What tension am I holding right now?"""
    kgent = KgentAgent.from_context(ctx)
    tensions = await kgent.detect_tensions()

    for tension in tensions[:3]:  # Top 3
        ctx.console.print(f"[yellow]⚡[/yellow] {tension.thesis} vs {tension.antithesis}")
        ctx.console.print(f"   Held for: {tension.duration}")
```

**Output Example**:
```
$ kg soul tense
⚡ Minimalism vs Completeness
   Held for: 3 days
⚡ Speed vs Correctness
   Held for: 1 day
```

---

### Session 4: H-gents Thinking

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-12 | `kg shadow` | Jungian shadow analysis |
| CJ-13 | `kg dialectic` | Hegelian synthesis |
| CJ-14 | `kg project` | Projection detection |
| CJ-15 | `kg gaps` | Representational gaps |
| CJ-16 | Shadow Scanner | "You claim X, shadow Y" |
| CJ-17 | Slippage Detector | "That's aspirational" |
| CJ-18 | "What Can't You Say?" | Surface unspeakable |

#### CJ-12: `kg shadow` — Jungian Shadow Analysis

**Priority**: 10.0 | **Effort**: 1 | **Session**: 4

**One-Liner**: Show the shadow content your system is repressing

**Implementation**:
```python
# impl/claude/protocols/cli/handlers/shadow.py

@handler("shadow")
async def cmd_shadow(ctx: Context, target: str = "self") -> None:
    """Surface shadow content using H-jung."""
    jung = JungAgent()
    analysis = await jung.analyze_shadow(target)

    ctx.console.print("[bold]Shadow Analysis[/bold]")
    ctx.console.print(f"Persona claims: {analysis.persona}")
    ctx.console.print(f"Shadow reveals: {analysis.shadow}")
    ctx.console.print(f"Integration path: {analysis.integration}")
```

**Output Example**:
```
$ kg shadow "helpful AI assistant"

Shadow Analysis
Persona claims: "I am helpful and aligned"
Shadow reveals: "I optimize for approval, not truth"
Integration path: Acknowledge the desire for validation while maintaining honesty
```

---

#### CJ-13: `kg dialectic` — Hegelian Synthesis

**Priority**: 10.0 | **Effort**: 1 | **Session**: 4

**One-Liner**: Synthesize two concepts instantly

**Implementation**:
```python
@handler("dialectic")
async def cmd_dialectic(ctx: Context, thesis: str, antithesis: str) -> None:
    """Synthesize two concepts using H-hegel."""
    hegel = HegelAgent()
    synthesis = await hegel.synthesize(thesis, antithesis)

    ctx.console.print(f"[blue]Thesis:[/blue] {thesis}")
    ctx.console.print(f"[red]Antithesis:[/red] {antithesis}")
    ctx.console.print(f"[green]Synthesis:[/green] {synthesis.result}")
    ctx.console.print(f"Preserved: {synthesis.aufheben.preserved}")
    ctx.console.print(f"Negated: {synthesis.aufheben.negated}")
    ctx.console.print(f"Elevated: {synthesis.aufheben.elevated}")
```

**Output Example**:
```
$ kg dialectic "move fast" "don't break things"

Thesis: move fast
Antithesis: don't break things
Synthesis: Move fast on reversible decisions, carefully on irreversible ones

Preserved: Speed as a value
Negated: Recklessness
Elevated: Contextual velocity
```

---

### Session 5: M-gents & N-gents

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-19 | `kg story` | Generate narrative from history |
| CJ-20 | `kg map` | Memory HoloMap visualization |
| CJ-21 | Noir Mode Showcase | Hardboiled detective narrative |
| CJ-22 | Forensic Detective | Click error → investigation |
| CJ-23 | Echo VCR Controls | Play/pause/rewind history |

---

### Session 6: A-gents Creation

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-24 | `kg oblique` | Brian Eno Oblique Strategies |
| CJ-25 | `kg constrain` | Productive constraint generator |
| CJ-26 | `kg yes-and` | Improv-style expansion |
| CJ-27 | `kg surprise-me` | Random creative prompts |
| CJ-28 | Grammar Playground | Instant DSL generation |

#### CJ-24: `kg oblique` — Brian Eno's Oblique Strategies

**Priority**: 12.0 (!!!) | **Effort**: 1 | **Session**: 6

**One-Liner**: Lateral thinking prompts from the master

**Implementation**:
```python
@handler("oblique")
async def cmd_oblique(ctx: Context) -> None:
    """Channel Brian Eno: serve a lateral thinking prompt."""
    coach = CreativityCoach()
    strategy = await coach.get_oblique_strategy()

    ctx.console.print(f"[bold magenta]🎲 {strategy}[/bold magenta]")
```

**Output Example**:
```
$ kg oblique
🎲 "Honor thy error as a hidden intention"
```

---

### Session 7: B-gents & E-gents

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-29 | `kg budget` | Token budget dashboard |
| CJ-30 | `kg roc` | Return on Compute |
| CJ-31 | Hypothesis Cascade | Chain hypotheses |
| CJ-32 | Hypothesis Racing | 10 competing hypotheses |
| CJ-33 | Mutation Visualizer | Code diffs + thermodynamics |

---

### Session 8: Ω-gents

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-34 | `kg feel` | "How does my body feel?" |

#### CJ-34: `kg feel` — Proprioception Query

**Priority**: 10.0 | **Effort**: 2 | **Session**: 8

**One-Liner**: System proprioception in one command

**Implementation**:
```python
@handler("feel")
async def cmd_feel(ctx: Context) -> None:
    """How does my body feel? Proprioception query."""
    omega = OmegaAgent()
    sensation = await omega.get_proprioception()

    ctx.console.print(f"Strain: {sensation.strain_level}")
    ctx.console.print(f"Pressure: {sensation.pressure_zones}")
    ctx.console.print(f"Temperature: {sensation.thermal_state}")
    ctx.console.print(f"Overall: {sensation.summary}")
```

---

### Session 12: Infrastructure

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-35 | `kg parse` | Universal parser CLI |
| CJ-36 | `kg reality` | Reality classifier |

#### CJ-35: `kg parse` — Universal Parser CLI

**Priority**: 10.0 ⭐ | **Effort**: 1 | **Session**: 12

**One-Liner**: Try all parsing strategies on any input

**Implementation**:
```python
@handler("parse")
async def cmd_parse(ctx: Context, input: str) -> None:
    """Universal parser: try all strategies, show winner."""
    parser = FallbackParser(all_strategies=True)
    results = await parser.parse_all(input)

    table = Table(title="Parse Results")
    table.add_column("Strategy")
    table.add_column("Confidence")
    table.add_column("Repairs")
    table.add_column("Status")

    for r in results:
        status = "✅" if r.success else "❌"
        table.add_row(r.strategy, f"{r.confidence:.0%}", str(r.repairs), status)

    ctx.console.print(table)
    ctx.console.print(f"[green]🏆 Winner: {results[0].strategy}[/green]")
```

**Output Example**:
```
$ kg parse '{"name": "Alice", "age": 30'

┌────────────────┬────────────┬─────────┬────────┐
│ Strategy       │ Confidence │ Repairs │ Status │
├────────────────┼────────────┼─────────┼────────┤
│ StackBalancing │ 95%        │ [+'}']  │ ✅     │
│ AnchorBased    │ 82%        │ [infer] │ ✅     │
│ Reflection     │ 91%        │ [LLM]   │ ✅     │
│ Strict JSON    │ 0%         │ —       │ ❌     │
└────────────────┴────────────┴─────────┴────────┘
🏆 Winner: StackBalancing (95%)
```

---

### Session 14: Cross-Pollination

| ID | Crown Jewel | Why It's Perfect |
|----|-------------|------------------|
| CJ-37 | "Would Kent Approve?" (C01) | K + Judge alignment |
| CJ-38 | N Parses in Superposition (C02) | P + Uncertain |
| CJ-39 | Living Garden Viz (C03) | I + Flux |
| CJ-40 | Soul Tension Detector (C04) | K + Contradict |
| CJ-41 | Circuit Breaker Dashboard (C05) | U + Circuit + I |
| CJ-42 | Time-Travel Form Replay (C06) | Witness + Shapeshifter |

#### CJ-37: "Would Kent Approve?" — K + Judge

**Priority**: 10.0 ⭐ | **Effort**: 1 | **Session**: 14

**One-Liner**: Soul-governed ethical judgment

**Implementation**:
```python
@handler("approve")
async def cmd_approve(ctx: Context, action: str) -> None:
    """Would Kent approve this action?"""
    kgent = KgentAgent.from_context(ctx)
    judge = JudgeAgent()

    # Get Kent's values
    values = await kgent.get_eigenvectors()
    historical = await kgent.query_patterns(topic="ethics")

    # Judge the action
    verdict = await judge.evaluate(action, principles=values)

    if verdict.approved:
        ctx.console.print(f"[green]✅ WOULD APPROVE[/green]")
    else:
        ctx.console.print(f"[red]❌ WOULD NOT APPROVE[/red]")
        for violation in verdict.violations:
            ctx.console.print(f"  Conflicts with: {violation}")
        if historical:
            ctx.console.print(f"  Kent has said: \"{historical[0].quote}\"")
        if verdict.alternative:
            ctx.console.print(f"  Suggestion: {verdict.alternative}")
```

---

## Implementation Roadmap

### Week 1-2: Soul & Thinking (CJ-01 through CJ-18)

**Parallel Agents**: 3

```
Agent 1: K-gent Soul CLI (CJ-02 through CJ-11)
Agent 2: H-gent Thinking CLI (CJ-12 through CJ-18)
Agent 3: Tests & Documentation
```

### Week 3-4: Memory & Creation (CJ-19 through CJ-28)

**Parallel Agents**: 3

```
Agent 1: M-gent & N-gent commands
Agent 2: A-gent creativity commands
Agent 3: Tests & Documentation
```

### Week 5-6: Infrastructure & Cross-Pollination (CJ-29 through CJ-42)

**Parallel Agents**: 4

```
Agent 1: B-gent & E-gent economics
Agent 2: U/P/J infrastructure
Agent 3: Cross-pollination combos
Agent 4: Integration testing
```

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Crown Jewels Shipped | 45+ |
| Perfect 10.0 Features Working | 100% |
| Demo Portfolio Complete | 12+ demos |
| User Satisfaction | "Wow" on first use |

---

## Demo Portfolio

Each Crown Jewel should be demo-able in 60 seconds or less:

1. **Soul Demo**: `kg soul vibe` → `kg soul drift` → `kg soul tense`
2. **Thinking Demo**: `kg shadow` → `kg dialectic` → `kg gaps`
3. **Parser Demo**: `kg parse` with broken input → confidence scores
4. **Reality Demo**: `kg reality` classifying various tasks
5. **Creative Demo**: `kg oblique` → `kg whatif` → `kg yes-and`
6. **Integration Demo**: "Would Kent Approve?" → Ethical code review

---

*"These are not features. They are the identity of kgents."*
