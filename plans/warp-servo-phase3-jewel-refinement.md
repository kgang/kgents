---
path: warp-servo/phase3-jewel-refinement
status: dormant
progress: 0
last_touched: 2025-12-20
touched_by: claude-opus-4
blocking: [warp-servo/phase1-core-primitives, warp-servo/phase2-servo-integration]
enables: []
session_notes: |
  Initial creation. Crown Jewel B→A grade refinement.
  Depends on Phase 1 (primitives) and Phase 2 (Servo substrate).
phase_ledger:
  PLAN: complete
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  EDUCATE: pending
  REFLECT: pending
entropy:
  planned: 0.3
  spent: 0.0
  returned: 0.0
---

# Phase 3: Crown Jewel Refinement (B → A Grade)

> *"Current Crown Jewels feel like a 3.75/5 (B): solid foundations, but not yet inevitable, alive, or teaching-dense."*

**AGENTESE Context**: All Crown Jewel nodes
**Status**: Dormant (0 tests)
**Principles**: Joy-Inducing (alive, immersive), Tasteful (inevitable presence), Ethical (visible consent)
**Cross-refs**: `creative/crown-jewels-genesis-moodboard.md`, Phase 1/2 outputs

---

## Core Insight

The Servo rewrite is the moment to push Crown Jewels from B to A grade by implementing:
1. **Breathing surfaces** (alive, not static)
2. **Teaching-dense overlays** (visible laws)
3. **Immersive theater** (participant-as-actor)
4. **Living materials** (warm earth palette, textures)

---

## Jewel Visual Contracts

### Atelier (Copper / Creative Forge)

```python
@dataclass
class AtelierServoContract:
    """Visual identity for Atelier."""
    primary_color: Color = LivingEarthPalette.COPPER
    workshop_glow: GlowEffect = GlowEffect(color=COPPER, intensity=0.3)
    spectator_bids: list[LivingToken]  # Animated bid tokens
    creation_canvas: BreathingFrame    # 3-4s breathing
    forge_particles: ParticleSystem    # Sparks on creation
```

**Mood**: Workshop warmth, creative energy, spectator engagement.

### Park (Sage / Immersive Inhabit)

```python
@dataclass
class ParkServoContract:
    """Visual identity for Park."""
    primary_color: Color = LivingEarthPalette.SAGE
    theater_mode: FirstPersonTheater   # Sleep No More immersion
    consent_gauge: LivingGauge         # Visible consent balance
    character_masks: list[OrbitingMask]  # Characters as masks
    crisis_indicator: PulsingBorder    # Red pulse during crisis
```

**Mood**: First-person theater, participant agency, visible ethics.

### Coalition (Amber / Collaboration)

```python
@dataclass
class CoalitionServoContract:
    """Visual identity for Coalition."""
    primary_color: Color = LivingEarthPalette.AMBER_GLOW
    communal_glow: GlowEffect = GlowEffect(color=AMBER, warmth=0.8)
    turn_indicator: RotatingFocus      # Who's speaking
    contract_tablets: list[RitualTablet]  # Covenants as tablets
    coalition_weave: WeaveAnimation    # Threads connecting agents
```

**Mood**: Warmth, communal energy, visible agreements.

### Domain (Wood / Integration Hub)

```python
@dataclass
class DomainServoContract:
    """Visual identity for Domain."""
    primary_color: Color = LivingEarthPalette.SOIL
    connector_garden: GardenLayout     # Connectors as plants
    flow_vines: list[VinePath]         # Data flows like water
    sync_pulse: PulseIndicator         # Health as heartbeat, not bar
    integration_roots: RootSystem      # Deep connections
```

**Mood**: Grounded stability, organic growth, living infrastructure.

### Gestalt (Emerald / Living Code)

```python
@dataclass
class GestaltServoContract:
    """Visual identity for Gestalt."""
    primary_color: Color = LivingEarthPalette.LIVING_GREEN
    code_garden: GardenVisualization   # Existing component
    drift_indicators: list[LeafWilt]   # Unhealthy = wilting leaves
    dependency_vines: VineNetwork      # Dependencies as vines
    growth_animation: GrowthCycle      # New code = sprouting
```

**Mood**: Living garden, organic growth, visible health.

---

## Chunks

### Chunk 1: Breathing Surface System (2-3 hours)

**Goal**: Implement universal breathing surface for all jewels.

**Files**:
```
impl/claude/web/src/components/servo/BreathingSurface.tsx
impl/claude/web/src/hooks/useBreathingAnimation.ts
```

**Tasks**:
- [ ] Implement configurable breathing animation
- [ ] Support per-jewel color tinting
- [ ] Respect `prefers-reduced-motion`
- [ ] Wire to circadian modulation (Pattern 11)
- [ ] Apply to all jewel panels

**Exit Criteria**: Every jewel surface breathes subtly.

---

### Chunk 2: Teaching Overlay Density (3-4 hours)

**Goal**: Implement rich teaching overlays for all jewels.

**Files**:
```
impl/claude/web/src/components/teaching/TeachingLayer.tsx
impl/claude/web/src/components/teaching/LawCallout.tsx
impl/claude/web/src/components/teaching/OperadBadge.tsx
```

**Tasks**:
- [ ] Implement `TeachingLayer` wrapper
- [ ] Implement `LawCallout` for operad laws
- [ ] Implement `OperadBadge` with arity display
- [ ] Wire to Teaching Mode toggle (Pattern 14)
- [ ] Add per-jewel teaching content:
  - Atelier: Bid mechanics, creator royalties
  - Park: Consent debt, crisis phases
  - Coalition: Turn-taking, covenant negotiation
  - Gestalt: Drift detection, dependency health

**Exit Criteria**: Teaching mode reveals deep system mechanics.

---

### Chunk 3: Atelier Refinement (3-4 hours)

**Goal**: Upgrade Atelier from B to A grade.

**Files**:
```
impl/claude/web/src/components/atelier/AtelierCanvas.tsx
impl/claude/web/src/components/atelier/BidToken.tsx
impl/claude/web/src/components/atelier/ForgeParticles.tsx
```

**Tasks**:
- [ ] Implement `AtelierCanvas` with breathing frame
- [ ] Implement `BidToken` as living token (animated)
- [ ] Implement `ForgeParticles` on creation
- [ ] Apply copper workshop glow
- [ ] Wire to Offering for bid budgets
- [ ] Wire to Covenant for spectator permissions

**Exit Criteria**: Atelier feels like a living creative forge.

---

### Chunk 4: Park Refinement (3-4 hours)

**Goal**: Upgrade Park from B to A grade.

**Files**:
```
impl/claude/web/src/components/park/TheaterView.tsx
impl/claude/web/src/components/park/ConsentGauge.tsx
impl/claude/web/src/components/park/CharacterMask.tsx
```

**Tasks**:
- [ ] Implement `TheaterView` (first-person perspective)
- [ ] Implement `ConsentGauge` as living gauge
- [ ] Implement `CharacterMask` as orbiting elements
- [ ] Implement crisis pulsing border
- [ ] Wire to Covenant for consent tracking
- [ ] Wire to Ritual for scenario phases

**Exit Criteria**: Park feels like immersive theater.

---

### Chunk 5: Coalition Refinement (3-4 hours)

**Goal**: Upgrade Coalition from B to A grade.

**Files**:
```
impl/claude/web/src/components/coalition/CoalitionForge.tsx
impl/claude/web/src/components/coalition/TurnIndicator.tsx
impl/claude/web/src/components/coalition/RitualTablet.tsx
```

**Tasks**:
- [ ] Implement `CoalitionForge` with communal glow
- [ ] Implement `TurnIndicator` (rotating focus)
- [ ] Implement `RitualTablet` for covenant display
- [ ] Implement weave animation (threads connecting)
- [ ] Wire to Covenant for visible permissions
- [ ] Wire to Walk for turn history

**Exit Criteria**: Coalition feels warm and communal.

---

### Chunk 6: Domain Refinement (3-4 hours)

**Goal**: Upgrade Domain from B to A grade.

**Files**:
```
impl/claude/web/src/components/domain/DomainGarden.tsx
impl/claude/web/src/components/domain/ConnectorPlant.tsx
impl/claude/web/src/components/domain/SyncPulse.tsx
```

**Tasks**:
- [ ] Implement `DomainGarden` layout
- [ ] Implement `ConnectorPlant` for integrations
- [ ] Implement `SyncPulse` (heartbeat, not progress bar)
- [ ] Implement flow vines (data paths)
- [ ] Wire to Offering for integration budgets
- [ ] Wire to TraceNode for flow visualization

**Exit Criteria**: Domain feels like living infrastructure.

---

### Chunk 7: Gestalt Enhancement (2-3 hours)

**Goal**: Enhance existing Gestalt garden with WARP primitives.

**Files**:
```
impl/claude/web/src/components/garden/GardenVisualization.tsx  # Existing
impl/claude/web/src/components/garden/DriftLeaf.tsx
impl/claude/web/src/components/garden/GrowthSprout.tsx
```

**Tasks**:
- [ ] Add `DriftLeaf` (wilting = unhealthy deps)
- [ ] Add `GrowthSprout` (new code = sprouting)
- [ ] Wire to TraceNode for change history
- [ ] Enhance existing garden with WARP primitive hooks
- [ ] Apply living green palette consistently

**Exit Criteria**: Gestalt garden reflects live code health.

---

### Chunk 8: Rust Core Enforcement (4-5 hours)

**Goal**: Implement Rust enforcement for critical paths.

**Files**:
```
impl/rust/kgents-core/
├── Cargo.toml
├── src/
│   ├── lib.rs
│   ├── poly_agent.rs
│   ├── operad.rs
│   ├── trace_node.rs
│   └── covenant.rs
```

**Tasks**:
- [ ] Create `kgents-core` Rust crate
- [ ] Implement TraceNode ledger (append-only)
- [ ] Implement Operad law checking
- [ ] Implement Covenant enforcement
- [ ] Add PyO3 bindings
- [ ] Wire to Python services

**Decision Point**: Contingent on Phase 0 Rust strategy decision.

**Exit Criteria**: Critical paths enforced in Rust.

---

### Chunk 9: Education & Skills (2-3 hours)

**Goal**: Update skills and docs for WARP + Servo system.

**Files**:
```
docs/skills/warp-primitives.md
docs/skills/servo-projection.md
docs/skills/trace-first-development.md
```

**Tasks**:
- [ ] Create skill: WARP primitive usage
- [ ] Create skill: Servo projection patterns
- [ ] Create skill: Trace-first development
- [ ] Update metaphysical-fullstack.md with Servo layer
- [ ] Update projection-target.md with Servo examples

**Exit Criteria**: Developers can use new system via skills.

---

## N-Phase Position

This plan covers phases:
- **PLAN**: ✅ Complete (this document)
- **CROSS-SYNERGIZE**: Wire to all Crown Jewels
- **IMPLEMENT**: Visual refinements, Rust core
- **EDUCATE**: Skills and documentation
- **REFLECT**: Anti-Sausage check, Constitution review

---

## Total Estimates

| Chunk | Hours | Tests |
|-------|-------|-------|
| Breathing Surface | 2-3 | 5+ |
| Teaching Overlays | 3-4 | 10+ |
| Atelier | 3-4 | 5+ |
| Park | 3-4 | 5+ |
| Coalition | 3-4 | 5+ |
| Domain | 3-4 | 5+ |
| Gestalt | 2-3 | 5+ |
| Rust Core | 4-5 | 15+ |
| Education | 2-3 | 0 |
| **Total** | **27-34** | **55+** |

---

## A-Grade Outcome Criteria

When complete, Crown Jewels should feel:

| Criteria | Measurement |
|----------|-------------|
| **Alive** | Breathing surfaces, organic motion |
| **Teaching-dense** | Teaching mode reveals all laws |
| **Immersive** | Participant-as-actor, not observer |
| **Grounded** | Warm earth palette, tangible textures |
| **Inevitable** | "This is the only way it could be" |

---

## Anti-Sausage Check

Before marking complete, verify:
- ❓ Do jewels feel alive, not static?
- ❓ Are teaching overlays rich, not tokenistic?
- ❓ Is the aesthetic daring (Ghibli warmth, not corporate glass)?
- ❓ Does each jewel have distinct personality?
- ❓ Are Covenants visible, not hidden?

---

## Cross-References

- **Spec**: `spec/protocols/warp-primitives.md`, `spec/protocols/servo-substrate.md`
- **Plan**: `plans/warp-servo-phase1-core-primitives.md`, `plans/warp-servo-phase2-servo-integration.md`
- **Moodboard**: `creative/crown-jewels-genesis-moodboard.md`
- **Skills**: `docs/skills/crown-jewel-patterns.md`

---

*"The persona is a garden, not a museum."*
