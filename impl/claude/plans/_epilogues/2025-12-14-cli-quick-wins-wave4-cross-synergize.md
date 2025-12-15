# CLI Quick Wins Wave 4: CROSS-SYNERGIZE Phase

> *"Hunt compositions/entanglements; probe with hotdata; select law-abiding pipelines."*

**Phase**: CROSS-SYNERGIZE
**Date**: 2025-12-14
**Touched By**: claude-opus-4.5

---

## Overview

This document identifies pipeline compositions, cross-context bridges, and synergies between the 9 CLI Quick Wins Wave 4 commands and other active plans.

---

## Pipeline Compositions

### 1. Soul Inquiry Pipeline

**Composition**: `self.soul.manifest >> self.soul.tension >> world.viz.sparkline`

```
[soul state] → [tensions identified] → [severity sparkline]
```

**Law Check**:
- ✅ Identity: Id >> tension ≡ tension ≡ tension >> Id
- ✅ Associativity: (manifest >> tension) >> sparkline ≡ manifest >> (tension >> sparkline)
- ✅ Type compatibility: SoulManifest → Tension[] → Sparkline

**Use Case**: Quick visual scan of soul health before deep work.

**REPL Example**:
```
[self.soul] » manifest >> tension >> ../world.viz.sparkline
▅▂▁▃▅▆  (6 tensions, moderate severity)
```

---

### 2. Creative Ideation Pipeline

**Composition**: `void.serendipity.prompt >> concept.creativity.expand >> concept.creativity.constrain`

```
[random seed] → [yes-and expansion] → [productive constraints]
```

**Law Check**:
- ✅ Identity: preserved
- ✅ Associativity: preserved
- ✅ Type: CreativePrompt → CreativityResponse → CreativityResponse (homogeneous)

**Use Case**: Generate novel ideas with built-in constraints for implementation.

**REPL Example**:
```
[void] » serendipity.prompt >> ../concept.creativity.expand >> constrain
Seed: "What if tests could dream?"
Expansions: [dream-based fuzzing, hypnagogia test oracles, ...]
Constraints: [must complete in 100ms, no external deps, ...]
```

---

### 3. Shadow Analysis Pipeline

**Composition**: `self.soul.manifest >> void.shadow.project`

```
[current soul state] → [projection analysis]
```

**Law Check**:
- ✅ All laws preserved
- ✅ Type: SoulManifest → ProjectionAnalysis

**Use Case**: Analyze what the current soul state is projecting onto external targets.

**REPL Example**:
```
[self.soul] » manifest >> ../void.shadow.project
Shadow content: "perfectionism"
Projected onto: "code quality discussions"
Integration hint: "Acknowledge that good enough ships"
```

---

### 4. Recursive Why Pipeline

**Composition**: `self.soul.why >> world.viz.sparkline`

```
[why chain] → [depth visualization]
```

**Law Check**:
- ✅ All laws preserved
- ⚠️ Requires projection: WhyChain → float[] (extract depths)

**Use Case**: Visualize how deep the inquiry went.

**REPL Example**:
```
[self.soul] » why "We need microservices" >> ../world.viz.sparkline
▁▂▃▄▅▆  (6 levels deep, reached bedrock)
```

---

### 5. Dialectic Challenge Pipeline

**Composition**: `self.soul.challenge >> void.shadow.project`

```
[challenged claim] → [what shadow surfaced]
```

**Law Check**:
- ✅ All laws preserved
- ✅ Type compatible: ChallengeResponse → ProjectionAnalysis

**Use Case**: After challenging a claim, analyze what defending it reveals about shadow content.

---

## Cross-Context Bridges

### Bridge 1: `self.soul.*` ↔ `void.shadow.*`

**Connection**: Soul introspection naturally flows to shadow analysis.

| Soul Aspect | Shadow Aspect | Bridge |
|-------------|---------------|--------|
| `soul.manifest` | `shadow.project` | Soul state → Projection targets |
| `soul.tension` | `shadow.inventory` | Tensions → Shadow sources |
| `soul.challenge` | `shadow.integrate` | Challenge → Integration path |

**Implementation**: Add pipeline shortcut in soul handler:
```python
SOUL_SHADOW_BRIDGES = {
    "analyze-shadow": "self.soul.manifest >> void.shadow.project",
    "shadow-tensions": "self.soul.tension >> void.shadow.inventory",
}
```

---

### Bridge 2: `concept.creativity.*` ↔ `void.serendipity.*`

**Connection**: Creative tools compose with entropy sources.

| Creativity Aspect | Serendipity Aspect | Bridge |
|-------------------|-------------------|--------|
| `creativity.expand` | `serendipity.prompt` | Entropy seeds expansion |
| `creativity.constrain` | `serendipity.surprise` | Constraints surprise |
| `creativity.oblique` | `serendipity.tithe` | Oblique draws entropy |

**Implementation**: Oblique strategies should sip from `void.entropy`:
```python
async def cmd_oblique(...):
    entropy = await logos.invoke("void.entropy.sip", amount=0.01)
    strategy = select_strategy(seed=entropy.value)
```

---

### Bridge 3: `world.viz.*` ↔ (any numeric output)

**Connection**: Sparkline is a universal visualizer for any numeric sequence.

**Composable With**:
- `self.soul.tension` → severity[]
- `self.memory.usage` → allocation[]
- `time.trace.latencies` → latency[]
- `world.town.metrics` → citizen_counts[]

**Implementation**: Add `to_sparkline()` protocol:
```python
class Sparklinable(Protocol):
    def to_numeric_sequence(self) -> list[float]: ...
```

---

## Agent Town Synergies

### Synergy 1: Town Tension Visualization

**Composition**: `world.town.metrics >> self.soul.tension >> world.viz.sparkline`

**Rationale**: Town has `drama_potential` per operation (see `operad.py`). Visualizing tension_index over time shows narrative arc.

**Implementation Point**: `agents/town/visualization.py` already defines `ScatterPoint` with 7D eigenvectors. Add:
```python
async def get_tension_history() -> list[float]:
    """Return drama_potential over last N phases."""
    return [phase.drama_potential for phase in town.history]
```

**REPL Example**:
```
[world.town] » metrics >> ../self.soul.tension >> ../viz.sparkline
▁▃▅▇▆▄▂  (narrative arc: rising action, climax, falling)
```

---

### Synergy 2: Citizen Why Chains

**Composition**: `world.town.lens <citizen> >> self.soul.why`

**Rationale**: When inhabiting a citizen, ask "why" recursively about their motivations.

**Implementation Point**: `TownSession.inhabit()` sets perspective. Chain to soul.why with citizen context.

---

### Synergy 3: Shadow in Town

**Composition**: `world.town.observe >> void.shadow.collective`

**Rationale**: The town's collective shadow emerges from citizen interactions.

**Implementation Point**: `collective_shadow.py` already exists. Wire to town state.

---

## REPL Wave 4 Synergies

### Synergy 1: Oblique Easter Egg

**Already Aligned**: Wave 4 has `EASTER_EGGS` dict. Add:
```python
"concept.creativity.oblique.secret": "_easter_oblique_eno",
```

Hidden variant that plays a Brian Eno quote.

---

### Synergy 2: K-gent Triggers for New Commands

**Current Triggers** (from repl.py):
```python
KGENT_TRIGGERS = frozenset({
    "reflect", "advice", "feeling", "wisdom", "meaning", "help", "why"
})
```

**Proposed Additions**:
```python
KGENT_TRIGGERS |= {"tension", "challenge", "project", "shadow"}
```

**Rationale**: These commands are philosophical in nature and benefit from K-gent's personality.

---

### Synergy 3: Contextual Hints for New Commands

**Current Hints** (from repl.py):
```python
if state.path == ["void"]:
    return "Hint: 'entropy sip' draws from the Accursed Share"
```

**Proposed Additions**:
```python
if state.path == ["concept", "creativity"]:
    return "Hint: 'oblique' serves lateral thinking prompts"

if state.path == ["self", "soul"]:
    return "Hint: 'why <statement>' digs to bedrock assumptions"
```

---

## Standalone Commands (No Synergy)

The following commands are self-contained and don't benefit from composition:

| Command | Reason | Classification |
|---------|--------|----------------|
| `oblique` | Returns single strategy, not chainable | **Standalone** |
| `challenge` | Alias to existing soul command | **Alias only** |
| `sparkline` | Terminal output, not chainable | **Sink** (end of pipeline) |

**Note**: These are not defects—they serve as pipeline endpoints or utilities.

---

## Rejected Compositions

### 1. `oblique >> constrain` ❌

**Reason**: Oblique strategy is already a constraint. Constraining a constraint is redundant.

**Alternative**: Use `oblique` as seed for `yes-and`:
```
oblique >> yes-and  ✅ (strategy → expanded strategy)
```

---

### 2. `sparkline >> anything` ❌

**Reason**: Sparkline produces terminal output (string), not structured data. It's a sink.

---

### 3. `why >> why` ❌

**Reason**: Recursive why already goes to bedrock. Stacking is redundant.

**Alternative**: Increase depth parameter:
```
why --depth 7 <statement>  ✅
```

---

## Summary Table

| Composition | Contexts Bridged | Law Status | Priority |
|-------------|------------------|------------|----------|
| `manifest >> tension >> sparkline` | self ↔ world | ✅ | High |
| `serendipity >> expand >> constrain` | void ↔ concept | ✅ | High |
| `manifest >> shadow.project` | self ↔ void | ✅ | Medium |
| `why >> sparkline` | self ↔ world | ⚠️ (needs projection) | Low |
| `challenge >> shadow.project` | self ↔ void | ✅ | Medium |
| `town.metrics >> tension >> sparkline` | world ↔ self ↔ world | ✅ | High (Agent Town) |

---

## Implementation Hooks

### 1. hollow.py Registration (Verified)

From DEVELOP epilogue:
```python
COMMAND_REGISTRY = {
    # Wave 4 commands
    "project": "protocols.cli.handlers.project:cmd_project",
    "oblique": "protocols.cli.handlers.oblique:cmd_oblique",
    # ... etc
}
```

### 2. Context Router Updates

**void.py**: Add `serendipity` holon with `prompt` aspect
**concept.py**: Add `creativity` holon with `oblique`, `constrain`, `expand` aspects
**self.py**: Add `soul.why`, `soul.tension` aspects

### 3. Pipeline Registration

Add to repl.py or dedicated pipeline registry:
```python
PIPELINE_PRESETS = {
    "soul-health": "self.soul.manifest >> self.soul.tension >> world.viz.sparkline",
    "creative-ideation": "void.serendipity.prompt >> concept.creativity.expand >> concept.creativity.constrain",
    "shadow-analysis": "self.soul.manifest >> void.shadow.project",
}
```

---

## Phase Ledger

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # This session
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.10
  remaining: 0.05
```

---

## Exit Criteria Status

- [x] Pipeline compositions identified (5 major pipelines)
- [x] Cross-context bridges documented (3 bridges)
- [x] Synergies with Agent Town noted (3 synergies)
- [x] Synergies with REPL Wave 4 noted (3 synergies)
- [x] Explicit "no synergy" noted for standalone commands (3 commands)
- [x] Rejected compositions with rationale (3 rejections)

---

## Learnings (for meta.md)

```
2025-12-14  Sparkline is a "sink"—composes on left only, never on right
2025-12-14  Soul+Shadow bridge natural: introspection → projection analysis
2025-12-14  Pipeline presets reduce cognitive load for common patterns
```

---

## Next Phase: IMPLEMENT

Continuation prompt:

```
⟿[IMPLEMENT]

This is the *IMPLEMENT* phase for **CLI Quick Wins Wave 4**.

/hydrate
handles: pipelines=5; bridges=3; synergies=6; standalone=3; ledger={CROSS-SYNERGIZE:touched}; entropy=0.05
mission: Implement 9 handlers following contracts from DEVELOP; wire pipelines; add context routers.
actions:
  - Create handler files (sparkline first, zero-dep)
  - Register in hollow.py
  - Add context router entries (void, concept, self)
  - Wire pipeline presets
  - Add REPL shortcuts
exit: All 9 commands work via CLI and REPL; pipelines execute; tests green; ledger.IMPLEMENT=touched; continuation → QA.

Sprint Order (from STRATEGIZE):
1. Track A: sparkline + challenge (parallel, zero-dep)
2. Track B: oblique → constrain → yes-and (concept.creativity holon)
3. Track C: surprise-me → project (void holons)
4. Track D: why → tension (soul extensions)
```

---

*"Composition is not optional—it is the grammar that generates meaning."*
