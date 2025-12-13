---
path: ideas/impl/quick-wins
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [ideas/impl/crown-jewels]
session_notes: |
  All 70+ Quick Wins from creative exploration sessions.
  Priority >= 7.0, Effort <= 2.
  Organized into 6 sprints for parallel execution.
---

# Quick Wins Implementation Plan

> *"The best ideas are trivial to implement and impossible to ignore."*

**Definition**: Priority ≥ 7.0, Effort ≤ 2
**Total Count**: 70+ ideas
**Estimated Time**: 4 weeks (parallel agents)

---

## Quick Wins by Priority Tier

### Tier S: Perfect 10.0 (Ship This Week)

| ID | Idea | Session | Agent | One-Liner | Files |
|----|------|---------|-------|-----------|-------|
| QW-S01 | `kg soul vibe` | S3 | K | "🎭 Playful, 🔬 Abstract, ✂️ Minimal" | handlers/soul.py |
| QW-S02 | `kg soul drift` | S3 | K | "0.03 more austere than yesterday" | handlers/soul.py |
| QW-S03 | `kg soul tense` | S3 | K | What tension am I holding? | handlers/soul.py |
| QW-S04 | `kg soul avoiding` | S3 | K | Surface avoidance patterns | handlers/soul.py |
| QW-S05 | `kg soul compare` | S3 | K | Similarity score for text | handlers/soul.py |
| QW-S06 | `kg soul minimum` | S3 | K | "What's the 80/20?" | handlers/soul.py |
| QW-S07 | `kg soul why` | S3 | K | Quick dialectical challenge | handlers/soul.py |
| QW-S08 | `kg whatif` | S2 | Uncertain | Show me 3 alternatives | handlers/whatif.py |
| QW-S09 | `kg parse` | S12 | P | Universal parser CLI | handlers/parse.py |
| QW-S10 | `kg reality` | S12 | J | Classify DET/PROB/CHAOTIC | handlers/reality.py |
| QW-S11 | `kg shadow` | S4 | H-jung | Show shadow content | handlers/shadow.py |
| QW-S12 | `kg dialectic` | S4 | H-hegel | Synthesize two concepts | handlers/dialectic.py |
| QW-S13 | `kg project` | S4 | H-jung | Where are you projecting? | handlers/shadow.py |
| QW-S14 | `kg gaps` | S4 | H-lacan | What can't be said? | handlers/gaps.py |
| QW-S15 | `kg feel` | S8 | Ω | How does my body feel? | handlers/feel.py |
| QW-S16 | `kg story` | S5 | N | Generate narrative | handlers/story.py |
| QW-S17 | `kg map` | S5 | M | Show memory HoloMap | handlers/map.py |
| QW-S18 | `kg oblique` | S6 | A | Brian Eno Oblique Strategies | handlers/oblique.py |
| QW-S19 | `kg budget` | S7 | B | Token budget dashboard | handlers/budget.py |
| QW-S20 | `kg roc` | S7 | B | Return on Compute | handlers/roc.py |
| QW-S21 | Dangerous Op Warning | S3 | K | Red flash for risky keywords | agents/k/gatekeeper.py |
| QW-S22 | Daily Tension | S3 | K | "minimalism vs completion" | agents/k/tension.py |
| QW-S23 | "Does This Sound Like Me?" | S3 | K | Paste text → match % | agents/k/similarity.py |
| QW-S24 | Shadow Scanner | S4 | H-jung | "You claim X, shadow Y" | agents/h/jung.py |
| QW-S25 | Slippage Detector | S4 | H-lacan | "That's aspirational, not factual" | agents/h/lacan.py |
| QW-S26 | "What Can't You Say?" | S4 | H-lacan | Surface unspeakable truths | agents/h/lacan.py |

### Tier A: Excellent 9.0-9.9 (Week 2)

| ID | Idea | Session | Agent | One-Liner | Files |
|----|------|---------|-------|-----------|-------|
| QW-A01 | `kg why` | S2 | Questioner | Recursive why until bedrock | handlers/why.py |
| QW-A02 | `kg tension` | S2 | Dialectician | List unresolved tensions | handlers/tension.py |
| QW-A03 | `kg challenge` | S2 | Questioner | Devil's Advocate mode | handlers/challenge.py |
| QW-A04 | `kg observe` | S13 | O | One-line health check | handlers/observe.py |
| QW-A05 | `kg panopticon` | S13 | O | Live ASCII dashboard | handlers/panopticon.py |
| QW-A06 | `kg execute` | S12 | U | One-liner tool execution | handlers/execute.py |
| QW-A07 | `kg stable?` | S12 | J | Quick stability check | handlers/stable.py |
| QW-A08 | `kg sparkline` | S11 | I | Numbers → `▁▂▃▄▅▆▇█` | handlers/sparkline.py |
| QW-A09 | `kg weather` | S11 | I | Agent activity summary | handlers/weather.py |
| QW-A10 | `kg body sense` | S8 | Ω | One-line proprioception | handlers/body.py |
| QW-A11 | Morphology REPL | S8 | Ω | Interactive composer | handlers/morphology.py |
| QW-A12 | Eigenvector Pulse | S3 | K | Live breathing bar chart | widgets/pulse.py |
| QW-A13 | Starter Roulette | S3 | K | Random profound prompt | agents/k/starters.py |
| QW-A14 | Garden Weather | S3 | K | "5 seeds, 3 saplings" | agents/k/garden.py |
| QW-A15 | `kg soul oracle` | S3 | K | Principle-aligned yes/no | handlers/soul.py |
| QW-A16 | `kg soul whisper` | S3 | K | WHISPER-tier nudge | handlers/soul.py |
| QW-A17 | `kg soul gratitude` | S3 | K | Daily gratitude practice | handlers/soul.py |
| QW-A18 | Shadow Confessional | S4 | H-jung | Safe shadow acknowledgment | agents/h/jung.py |
| QW-A19 | Imaginary Alert | S4 | H-lacan | Detect aspirational language | agents/h/lacan.py |
| QW-A20 | `kg mirror` | S4 | H-jung | Reflect on self-image | handlers/mirror.py |
| QW-A21 | Error Flash | S11 | I | Screen glitches on errors | widgets/glitch.py |
| QW-A22 | Memory Telescope | S5 | M | Zoom slider for resolution | widgets/telescope.py |
| QW-A23 | HoloMap Explorer | S5 | M | Interactive cartography | widgets/holomap.py |
| QW-A24 | Time Travel Debugger | S5 | M | Jump to any execution point | widgets/timetravel.py |

### Tier B: Strong 8.0-8.9 (Week 3)

| ID | Idea | Session | Agent | One-Liner | Files |
|----|------|---------|-------|-----------|-------|
| QW-B01 | `kg drift` | S13 | O | "Are we on topic?" | handlers/drift.py |
| QW-B02 | `kg roc` | S13 | O | Return on Compute | handlers/roc.py |
| QW-B03 | Bootstrap Witness CLI | S13 | O | "Do the laws hold?" | handlers/laws.py |
| QW-B04 | Circuit Breaker Dashboard | S12 | U | Live tool health (🟢🟡🔴) | widgets/circuit.py |
| QW-B05 | Confidence Thermometer | S12 | P | Emoji gradient 🥶→😐→🔥 | widgets/confidence.py |
| QW-B06 | Tool Capability Cards | S12 | U | Pretty tool docs | widgets/cards.py |
| QW-B07 | Entropy Budget Bar | S12 | J | Gamified resources | widgets/entropy.py |
| QW-B08 | Collapse Ceremony | S12 | J | Dramatic Ground fallback | handlers/collapse.py |
| QW-B09 | `kg secure` | S12 | U | Check elevated permissions | handlers/secure.py |
| QW-B10 | Child Mode | S2 | Questioner | "Why? Why? WHY?" | handlers/child.py |
| QW-B11 | Dynamic Prompt Character | S2 | Shapeshifter | ASCII that breathes | widgets/prompt.py |
| QW-B12 | Collapse Ceremony | S2 | Uncertain | Dramatic wave collapse | widgets/collapse.py |
| QW-B13 | "What Do I Look Like?" | S2 | Shapeshifter | Agent describes form | handlers/look.py |
| QW-B14 | `kg soul temperature` | S3 | K | How "warm" is your soul? | handlers/soul.py |
| QW-B15 | Principle Matcher | S3 | K | "Violates Heterarchy (88%)" | agents/k/principles.py |
| QW-B16 | `kg soul mood` | S3 | K | Emotional eigenvector summary | handlers/soul.py |
| QW-B17 | `kg soul calibrate` | S3 | K | "When did I last drift?" | handlers/soul.py |
| QW-B18 | Confidence Meter | S3 | K | Avg eigenvector confidence | widgets/confidence.py |
| QW-B19 | Sublation Explainer | S4 | H-hegel | What was preserved/negated? | agents/h/hegel.py |
| QW-B20 | Self Archetype Warning | S4 | H-jung | "Inflating into totality" | agents/h/jung.py |

### Tier C: Solid 7.0-7.9 (Week 4)

| ID | Idea | Session | Agent | One-Liner | Files |
|----|------|---------|-------|-----------|-------|
| QW-C01 | `kg tools` | S12 | U | MCP server browser | handlers/tools.py |
| QW-C02 | Repair Timeline | S12 | P | Show all fixes applied | widgets/repair.py |
| QW-C03 | Format Drift Detector | S12 | P | "JSON getting sloppier!" | agents/p/drift.py |
| QW-C04 | Streaming Parse Viz | S12 | P | Real-time stack balancing | widgets/parse.py |
| QW-C05 | Reflection Loop Viz | S12 | P | Watch LLM self-correct | widgets/reflection.py |
| QW-C06 | Stability Report Card | S12 | J | Cyclomatic + recursion risk | handlers/stability.py |
| QW-C07 | `kg compile` | S12 | J | JIT compile from intent | handlers/compile.py |
| QW-C08 | `kg hallucinate?` | S13 | O | Grounding check | handlers/hallucinate.py |
| QW-C09 | Design Dialectic | S4 | H-hegel | Surface requirement tensions | agents/h/hegel.py |
| QW-C10 | Projection Detector | S4 | H-jung | Find user projections | agents/h/jung.py |
| QW-C11 | "Touch the Real" | S4 | H-lacan | Force confrontation with limits | agents/h/lacan.py |
| QW-C12 | `kg sleep` | S2 | Consolidator | Trigger consolidation | handlers/sleep.py |
| QW-C13 | Crystal Gallery | S9 | D | Browse saved crystals | widgets/crystal.py |
| QW-C14 | Registry TUI | S9 | L | Browse registered agents | widgets/registry.py |
| QW-C15 | Lens Playground | S9 | D | Interactive lens composition | widgets/lens.py |
| QW-C16 | `kg viz` | S11 | I | Launch FluxScreen demo | handlers/viz.py |
| QW-C17 | `kg density` | S11 | I | Text as density weather | handlers/density.py |
| QW-C18 | `kg loom` | S11 | I | Show cognitive tree | handlers/loom.py |
| QW-C19 | Oblique Flash | S11 | I | High entropy → Oblique Strategy | widgets/oblique.py |
| QW-C20 | LOD Slider | S11 | I | Smooth zoom between levels | widgets/lod.py |

---

## Sprint Assignments

### Sprint 1: K-gent Soul (Week 1)

**Focus**: All K-gent soul commands
**Agent Count**: 2 parallel agents
**Target**: 15 commands

```
Agent 1: CLI Wiring
├── kg soul vibe
├── kg soul drift
├── kg soul tense
├── kg soul avoiding
├── kg soul compare
├── kg soul minimum
├── kg soul why
└── kg soul oracle

Agent 2: Agent Enhancements
├── Eigenvector Pulse widget
├── Starter Roulette
├── Garden Weather
├── Dangerous Op Warning
├── Daily Tension
└── "Does This Sound Like Me?"
```

**Exit Criteria**:
- All 15 commands runnable from CLI
- Tests for each command
- Documentation strings complete

---

### Sprint 2: Infrastructure (Week 2)

**Focus**: U-gent, P-gent, J-gent commands
**Agent Count**: 2 parallel agents
**Target**: 12 commands

```
Agent 1: Parsing & Reality
├── kg parse (universal parser)
├── kg reality (DET/PROB/CHAOTIC)
├── kg stable? (stability check)
├── kg compile (JIT from intent)
├── Confidence Thermometer
└── Collapse Ceremony

Agent 2: Tools & Execution
├── kg execute (one-liner tool)
├── kg tools (MCP browser)
├── kg secure (permission check)
├── Circuit Breaker Dashboard
├── Tool Capability Cards
└── Entropy Budget Bar
```

**Exit Criteria**:
- Parsing works on malformed input
- Reality classifier accurate
- Circuit breaker states visible

---

### Sprint 3: H-gent Thinking (Week 3)

**Focus**: H-hegel, H-jung, H-lacan commands
**Agent Count**: 2 parallel agents
**Target**: 14 commands

```
Agent 1: H-jung (Shadow)
├── kg shadow
├── kg project
├── Shadow Scanner
├── Shadow Confessional
├── Projection Detector
├── Self Archetype Warning
└── kg mirror

Agent 2: H-hegel + H-lacan
├── kg dialectic
├── kg gaps
├── Slippage Detector
├── "What Can't You Say?"
├── Imaginary Alert
├── Sublation Explainer
└── "Touch the Real"
```

**Exit Criteria**:
- Shadow analysis working
- Register triangulation functional
- Dialectic synthesis producing output

---

### Sprint 4: Observation & Visualization (Week 4)

**Focus**: O-gent, I-gent commands
**Agent Count**: 2 parallel agents
**Target**: 15 commands

```
Agent 1: Observation
├── kg observe
├── kg panopticon
├── kg drift
├── kg roc
├── kg hallucinate?
├── Bootstrap Witness CLI
└── Dimension Dance TUI (if time)

Agent 2: Visualization
├── kg sparkline
├── kg weather
├── kg viz
├── kg density
├── kg loom
├── Error Flash
├── LOD Slider
└── Oblique Flash
```

**Exit Criteria**:
- Health check in one command
- Sparklines rendering
- Live dashboards updating

---

## Implementation Patterns

### Pattern 1: CLI Handler Wiring

```python
# impl/claude/protocols/cli/handlers/soul.py

from agents.k import KgentAgent, PersonaQuery

@handler("soul", "vibe")
async def cmd_soul_vibe(ctx: Context) -> None:
    """One-liner soul state."""
    kgent = KgentAgent.from_context(ctx)
    vibe = await kgent.get_vibe()
    ctx.console.print(f"🎭 {vibe}")
```

### Pattern 2: Widget Integration

```python
# impl/claude/agents/i/widgets/sparkline.py

from textual.widget import Widget

class SparklineWidget(Widget):
    """Render numbers as sparkline: ▁▂▃▄▅▆▇█"""

    def __init__(self, values: list[float]):
        super().__init__()
        self.values = values

    def render(self) -> str:
        chars = "▁▂▃▄▅▆▇█"
        # Map values to chars
        ...
```

### Pattern 3: Agent Enhancement

```python
# impl/claude/agents/k/soul.py

class KgentAgent:
    async def get_vibe(self) -> str:
        """Return one-liner soul state."""
        eigens = await self.get_eigenvectors()
        return self._format_vibe(eigens)

    def _format_vibe(self, eigens: Eigenvectors) -> str:
        # Format as "🎭 Playful, 🔬 Abstract, ✂️ Minimal"
        ...
```

---

## Parallel Agent Coordination

### Daily Standup (Simulated)

```
Agent 1: "Finished kg soul vibe, starting kg soul drift"
Agent 2: "Eigenvector Pulse widget complete, testing"
Agent 3: "Writing tests for Sprint 1 commands"
Agent 4: "Updating documentation"
```

### Merge Strategy

```
1. Each agent works on feature branch
2. Tests must pass before merge
3. Review by another agent (simulated via self-check)
4. Merge to main after all checks
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Commands Implemented | 70+ |
| Test Coverage | 94%+ |
| Documentation Coverage | 100% |
| Average Response Time | <100ms |
| User Errors Handled | 100% graceful |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | High | Strict priority cutoff |
| Integration failures | Low | Medium | Early integration testing |
| Performance issues | Low | Medium | Benchmark critical paths |
| Missing dependencies | Medium | Low | Dependency analysis first |

---

## Next Steps

1. [ ] Begin Sprint 1: K-gent Soul commands
2. [ ] Set up test framework for new commands
3. [ ] Create documentation template
4. [ ] Establish CI/CD pipeline for new handlers

---

*"Quick wins build momentum. Momentum builds confidence. Confidence builds velocity."*
