# WASM Survivors: Final Quality Improvement Proposal

> *"The transformation is not in systems—it's in FEEL."*

**Generated**: 2026-01-10
**Based on**: AI Playthrough Farm Evidence + Comprehensive Gap Analysis
**Evidence Tier**: CATEGORICAL (Galois Loss: 0.061)

---

## Executive Summary

The wasm-survivors game has a **strong categorical foundation** (95% core gameplay, 85% BALL formation) but lacks **sensory impact** (60% juice, 50% audio, 40% personality). The spec's radical transformation mandate—*"every kill should feel like a dopamine hit"*—is architecturally prepared but experientially absent.

### Current State
- **What works**: Core loop, witness system, formation mechanics, upgrade diversity
- **What's missing**: Freeze frames, consistent shake, particle density, audio escalation, personality delivery
- **Evidence**: 6/6 personas completed, 0.94 humanness score, CATEGORICAL tier

### Transformation Thesis
```
Current:  Functional game with intellectual depth
Target:   Clip-worthy spectacle that makes players gasp
Gap:      40-50 hours of focused juice/audio/personality work
```

---

## Part I: Critical Fixes (Week 1 - Make Kills Feel Good)

### 1.1 Implement Freeze Frames [CRITICAL]

**Problem**: Kills have no weight. Zero freeze frame implementation despite spec requiring 2-6 frames.

**Spec Requirement** (Appendix E):
```typescript
FREEZE = {
  significantKill: 2,   // frames (33ms at 60fps) - guard/tank kills
  multiKill:       4,   // frames (66ms) - 3+ simultaneous kills
  criticalHit:     3,   // frames - execute or critical damage
  massacre:        6,   // frames (100ms) - 5+ kills = DRAMATIC PAUSE
}
```

**Implementation**:
```typescript
// In juice.ts - add freeze frame system
let freezeFramesRemaining = 0;

export function triggerFreeze(type: FreezeType): void {
  freezeFramesRemaining = FREEZE[type];
}

export function getEffectiveTimeScale(juice: JuiceSystem): number {
  // Freeze takes priority
  if (freezeFramesRemaining > 0) {
    freezeFramesRemaining--;
    return 0; // Complete stop
  }
  // Then clutch moments
  if (juice.clutch.active) {
    return juice.clutch.timeScale;
  }
  // Then debug scaling
  return debugTimeScale;
}
```

**Wire to events**:
- Guard kill → `triggerFreeze('significantKill')`
- 3+ kill combo → `triggerFreeze('multiKill')`
- Critical hit → `triggerFreeze('criticalHit')`
- 5+ kill massacre → `triggerFreeze('massacre')`

**Effort**: 3 hours
**Impact**: HIGH - transforms kill feel from "click" to "PUNCH"

---

### 1.2 Wire Screen Shake Consistently [CRITICAL]

**Problem**: 40% of shake-worthy events don't trigger shake.

**Currently Missing**:
| Event | Required Shake | Status |
|-------|---------------|--------|
| Dash execution | 2-3px | ❌ Missing |
| Dash graze | 1px | ❌ Missing |
| Level-up | 3px gentle | ❌ Missing |
| BALL forming | 1-5px ramp | ❌ Missing |
| BALL constrict | 8px intense | ❌ Missing |
| Enemy collision | 1-2px | ❌ Missing |
| Synergy discovery | 10px + flash | ❌ Missing |

**Implementation**: Audit all event handlers, add shake calls:
```typescript
// In combat.ts - onDash
triggerShake({ amplitude: 3, duration: 50, frequency: 60 });

// In formation.ts - onBallPhaseChange
if (newPhase === 'constrict') {
  triggerShake({ amplitude: 8, duration: 200, frequency: 60 });
}

// In upgrades.ts - onSynergyDiscovered
triggerShake({ amplitude: 10, duration: 150, frequency: 60 });
flashScreen('#FFD700', 100); // Gold flash
```

**Effort**: 2 hours
**Impact**: HIGH - consistent feedback loop

---

### 1.3 Complete Particle Rendering [HIGH]

**Problem**: Particles defined in juice.ts but only 20% rendered on canvas.

**Missing Particles**:
- `deathSpiral`: Count reduced to 12 (spec: 25) - **increase and render**
- `honeyDrip`: Not implemented - **add gravity + pooling**
- `damageFlash`: Basic flash, no fragments - **add explosive fragments**
- `xpOrb`: No trail - **add particle trail on collection**

**Implementation in GameCanvas.tsx**:
```typescript
// Add to render loop
for (const particle of juice.particles) {
  switch (particle.type) {
    case 'deathSpiral':
      renderDeathSpiral(ctx, particle);
      break;
    case 'honeyDrip':
      renderHoneyDrip(ctx, particle);
      break;
    case 'damageFragment':
      renderDamageFragment(ctx, particle);
      break;
    case 'xpTrail':
      renderXPTrail(ctx, particle);
      break;
  }
}
```

**Effort**: 3 hours
**Impact**: MEDIUM-HIGH - visual satisfaction

---

### 1.4 Add Damage Numbers [MEDIUM]

**Problem**: No floating combat numbers; skill impact unclear.

**Spec**: A3 (Visible Mastery) - skill development must be externally observable.

**Implementation**:
```typescript
interface DamageNumber {
  value: number;
  position: Vector2;
  color: string;
  isCritical: boolean;
  age: number;
}

// Render floating upward, fading
function renderDamageNumber(ctx: CanvasRenderingContext2D, dn: DamageNumber) {
  const alpha = 1 - (dn.age / DAMAGE_NUMBER_LIFESPAN);
  ctx.fillStyle = dn.isCritical
    ? `rgba(255, 215, 0, ${alpha})` // Gold for crit
    : `rgba(255, 255, 255, ${alpha})`;
  ctx.font = dn.isCritical ? 'bold 24px monospace' : '16px monospace';
  ctx.fillText(
    dn.value.toString(),
    dn.position.x,
    dn.position.y - (dn.age * 0.5) // Float upward
  );
}
```

**Effort**: 4 hours
**Impact**: MEDIUM - skill progression clarity

---

## Part II: Audio Cohesion (Week 2 - Make Sound Match Vision)

### 2.1 Consolidate Audio Systems [HIGH]

**Problem**: Three music systems exist, none integrated:
- `emergent-audio.ts` - Unused generative system
- `procedural-music.ts` - Over-engineered, 11 TODOs
- `kent-fugue.ts` - Intended main system

**Action**:
1. Deprecate `emergent-audio.ts` (delete or archive)
2. Simplify `procedural-music.ts` (remove unused features)
3. Make `kent-fugue.ts` the single source of truth

**Effort**: 4 hours
**Impact**: MEDIUM - cleaner codebase, easier maintenance

---

### 2.2 Multi-Kill Audio Escalation [CRITICAL]

**Problem**: Procedural audio system exists but never called from combat.

**Spec**: "Multi-kill audio should escalate +1 semitone per combo"

**Implementation**:
```typescript
// In combat.ts - onKill
const comboCount = getComboCount();
const semitoneShift = Math.min(comboCount, 12); // Cap at octave
playKillSound({
  pitch: 1 + (semitoneShift * 0.059), // ~semitone per step
  volume: Math.min(1.0, 0.7 + (comboCount * 0.05)),
});
```

**Effort**: 2 hours
**Impact**: HIGH - creates escalating tension and satisfaction

---

### 2.3 THE BALL Audio Sequencing [CRITICAL]

**Problem**: Formation system complete but audio disconnected.

**Spec**: "THE BALL should have 3s complete silence then bass drop"

**Implementation**:
```typescript
// In formation.ts - onBallPhaseChange
switch (newPhase) {
  case 'forming':
    fadeOutAllAudio(500); // Quick fade
    break;
  case 'silence':
    stopAllAudio(); // Complete silence for dread
    break;
  case 'constrict':
    playBassDropSound(); // THOOM
    startIntenseMusic();
    break;
  case 'dissipating':
    fadeToNormalMusic(1000);
    break;
}
```

**Effort**: 3 hours
**Impact**: CRITICAL - THE BALL must be terrifying

---

### 2.4 Spatial Audio Panning [MEDIUM]

**Problem**: Audio context exists but no stereo position calculation.

**Implementation**:
```typescript
function playPositionalSound(sound: Sound, worldPos: Vector2) {
  const screenCenter = { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 };
  const pan = (worldPos.x - screenCenter.x) / screenCenter.x; // -1 to 1
  sound.setPan(Math.max(-1, Math.min(1, pan)));
}
```

**Effort**: 2 hours
**Impact**: MEDIUM - spatial immersion

---

## Part III: Personality Integration (Week 3 - Give Hornet Agency)

### 3.1 Wire Voice Lines to Events [CRITICAL]

**Problem**: Voice lines defined in `personality.ts` but never triggered.

**Spec** (Part VII): "Hornet should have swagger"

**Implementation**:
```typescript
// Create event → voice line mapping
const VOICE_TRIGGERS = {
  onFirstKill: ["First blood.", "They'll remember this one."],
  onMultiKill: ["Too slow.", "The hive whispers of me now."],
  onLowHealth: ["Still standing.", "Pain is just... feedback."],
  onBallEncounter: ["They think formation saves them.", "Cute."],
  onDeath: ["The colony wins. This time.", "I'll be back."],
  onUpgrade: ["Stronger.", "Evolution in real-time."],
};

// Wire in GameLoop or event handler
if (event.type === 'kill' && isFirstKill) {
  showVoiceLine(pickRandom(VOICE_TRIGGERS.onFirstKill));
}
```

**Effort**: 3 hours
**Impact**: HIGH - character personality emerges

---

### 3.2 Arc Phase UI Indicator [MEDIUM]

**Problem**: Arc system tracks POWER → FLOW → CRISIS → TRAGEDY but player doesn't see it.

**Implementation**: Add subtle UI element:
```typescript
<div className="arc-indicator">
  {arcPhase === 'POWER' && <span className="text-yellow-400">⚡ POWER</span>}
  {arcPhase === 'FLOW' && <span className="text-blue-400">🌊 FLOW</span>}
  {arcPhase === 'CRISIS' && <span className="text-red-400">🔥 CRISIS</span>}
  {arcPhase === 'TRAGEDY' && <span className="text-purple-400">💀 TRAGEDY</span>}
</div>
```

**Effort**: 2 hours
**Impact**: MEDIUM - emotional journey visible

---

### 3.3 Contrast Meter [MEDIUM]

**Problem**: Seven contrast poles tracked but not displayed.

**Spec**: "Experiences must oscillate between poles"

**Implementation**: Simple pole indicator showing which extremes visited:
```
god ←———●———→ prey
speed ←———●———→ stillness
...
```

**Effort**: 2 hours
**Impact**: LOW-MEDIUM - depth visibility

---

### 3.4 Death Animation Enhancement [HIGH]

**Problem**: DeathOverlay has phases but no visual spiral asset.

**Spec**: "Death should feel like completing a journey"

**Implementation**:
```typescript
// In DeathOverlay.tsx
const deathPhases = [
  { name: 'impact', duration: 500, animation: 'screen-flash' },
  { name: 'spiral', duration: 2000, animation: 'player-spiral-down' },
  { name: 'acceptance', duration: 1500, animation: 'player-pose' },
  { name: 'tribute', duration: 3000, animation: 'crystal-form' },
];

// Add canvas animation for spiral
function renderDeathSpiral(ctx: CanvasRenderingContext2D, progress: number) {
  const angle = progress * Math.PI * 6; // 3 full rotations
  const radius = (1 - progress) * 100;
  const x = centerX + Math.cos(angle) * radius;
  const y = centerY + Math.sin(angle) * radius + (progress * 200);
  drawHornet(ctx, x, y, angle);
}
```

**Effort**: 2 hours
**Impact**: HIGH - closure quality

---

## Part IV: Balance Tuning (Week 4)

### 4.1 Spawn Rate Increase [MEDIUM]

**Problem**: Mid-game too easy; player power outpaces difficulty.

**Current vs. Target**:
| Time | Current | Target | Delta |
|------|---------|--------|-------|
| 0-5min | 2-4 | 4-6 | +2 |
| 5-10min | 6-10 | 10-14 | +4 |
| 10-20min | 12-20 | 18-28 | +6 |

**Implementation**: Adjust spawn curves in `spawn.ts`.

**Effort**: 1 hour
**Impact**: MEDIUM - difficulty progression

---

### 4.2 Archetype Viability Balancing [MEDIUM]

**Issues Found**:
| Archetype | Issue | Fix |
|-----------|-------|-----|
| Survivor | Passive healing too slow | +50% vampiric heal rate |
| Terror | Fear underutilized | Fear duration +1s, spread to nearby |
| Berserker | Frenzy snowballs | Cap frenzy stacks at 5 |

**Effort**: 2 hours
**Impact**: MEDIUM - build diversity

---

### 4.3 THE BALL Difficulty Tuning [MEDIUM]

**Problem**: Wave 7-9 BALL encounters escapable ~80% of time.

**Options**:
1. **Reduce gap angle** from 45° to 35° (harder escape)
2. **Increase formation speed** +20%
3. **Add "learning" behavior** - gap tracks player movement

**Recommendation**: Option 1 + 3 for skill-based difficulty.

**Effort**: 2 hours
**Impact**: MEDIUM - challenge curve

---

## Part V: Synergy Announcements [HIGH]

### 5.1 Visual + Audio Feedback on Discovery

**Problem**: 20+ synergies defined but completely silent.

**Implementation**:
```typescript
function onSynergyDiscovered(synergy: Synergy) {
  // Screen flash
  flashScreen('#FFD700', 150);

  // Screen shake
  triggerShake({ amplitude: 10, duration: 150, frequency: 60 });

  // Audio
  playSynergySound(synergy.tier); // Different sound per tier

  // Announcement overlay
  showAnnouncement({
    title: synergy.name,
    subtitle: synergy.description,
    icon: synergy.icon,
    duration: 2000,
  });

  // Particle burst
  spawnParticleBurst('synergy', playerPosition, {
    count: 30,
    colors: ['#FFD700', '#FFA500'],
  });
}
```

**Effort**: 3 hours
**Impact**: HIGH - discovery satisfaction

---

## Part VI: Visual Spectacle for THE BALL [CRITICAL]

### 6.1 Temperature Visual Effects

**Problem**: Temperature shimmer/glow specified but not rendered.

**Implementation**:
```typescript
// Heat shimmer shader or canvas effect
function renderTemperatureEffect(ctx: CanvasRenderingContext2D, ball: BallState) {
  const temp = ball.temperature / 100; // 0-1

  // Red glow around formation
  ctx.shadowColor = `rgba(255, ${100 - temp * 100}, 0, ${temp * 0.5})`;
  ctx.shadowBlur = temp * 30;

  // Heat shimmer (distortion)
  if (temp > 0.5) {
    applyHeatShimmer(ctx, ball.center, ball.radius, temp);
  }
}

function applyHeatShimmer(ctx, center, radius, intensity) {
  // Use displacement mapping or wavy line rendering
  const distortion = Math.sin(Date.now() / 100) * intensity * 5;
  // Apply to nearby pixels
}
```

**Effort**: 3 hours
**Impact**: CRITICAL - THE BALL must look dangerous

---

### 6.2 Escape Success Feedback

**Problem**: No particle burst or sound when player escapes gap.

**Implementation**:
```typescript
function onGapEscape() {
  // Victory particles
  spawnParticleBurst('escape', playerPosition, {
    count: 20,
    colors: ['#00FF00', '#00FFFF'],
    velocity: 300,
  });

  // Audio fanfare
  playEscapeSound();

  // Voice line
  showVoiceLine("Through the gap. Every time.");

  // Brief freeze
  triggerFreeze('criticalHit');
}
```

**Effort**: 1 hour
**Impact**: HIGH - escape satisfaction

---

## Implementation Roadmap

### Week 1: Fun Floor Foundation (12 hours)
| Task | Hours | Priority |
|------|-------|----------|
| Freeze frames | 3 | CRITICAL |
| Wire screen shake | 2 | CRITICAL |
| Complete particles | 3 | HIGH |
| Damage numbers | 4 | MEDIUM |

**Exit Criteria**: Kills feel like PUNCHES.

### Week 2: Audio Cohesion (11 hours)
| Task | Hours | Priority |
|------|-------|----------|
| Consolidate systems | 4 | HIGH |
| Multi-kill escalation | 2 | CRITICAL |
| BALL audio sequencing | 3 | CRITICAL |
| Spatial panning | 2 | MEDIUM |

**Exit Criteria**: Sound creates dread and satisfaction.

### Week 3: Personality (9 hours)
| Task | Hours | Priority |
|------|-------|----------|
| Wire voice lines | 3 | HIGH |
| Arc phase UI | 2 | MEDIUM |
| Contrast meter | 2 | LOW |
| Death animation | 2 | HIGH |

**Exit Criteria**: Hornet has character.

### Week 4: Polish & Balance (11 hours)
| Task | Hours | Priority |
|------|-------|----------|
| Synergy announcements | 3 | HIGH |
| THE BALL visuals | 3 | CRITICAL |
| Escape feedback | 1 | HIGH |
| Spawn rate tuning | 1 | MEDIUM |
| Archetype balance | 2 | MEDIUM |
| BALL difficulty | 1 | MEDIUM |

**Exit Criteria**: Game is clip-worthy.

---

## Success Metrics

### Quantitative
| Metric | Current | Target |
|--------|---------|--------|
| Freeze frame coverage | 0% | 100% |
| Screen shake coverage | 60% | 100% |
| Particle render rate | 20% | 90% |
| Audio event coverage | 50% | 95% |
| Voice line trigger rate | 0% | 80% |

### Qualitative (Player Feedback)
- [ ] "Kills feel satisfying" (9/10 responses)
- [ ] "THE BALL is terrifying" (8/10 responses)
- [ ] "I want to show someone this" (7/10 responses)
- [ ] "The hornet has personality" (7/10 responses)
- [ ] "Death felt meaningful" (6/10 responses)

### Galois Targets
| Metric | Current | Target |
|--------|---------|--------|
| Spec-Impl Coherence | 56.9% | 75%+ |
| Galois Loss | 0.431 | < 0.30 |
| Evidence Tier | AESTHETIC | EMPIRICAL |

---

## Appendix A: Files to Modify

### Critical Path
1. `systems/juice.ts` - Add freeze frames, complete shake wiring
2. `components/GameCanvas.tsx` - Render all particle types
3. `systems/audio.ts` - Wire escalation, BALL sequencing
4. `systems/contrast.ts` - Connect voice lines
5. `systems/formation/telegraph.ts` - Temperature visuals
6. `components/DeathOverlay.tsx` - Death animation

### Secondary Path
1. `systems/spawn.ts` - Rate adjustments
2. `systems/upgrades.ts` - Balance tuning
3. `components/HUD.tsx` - Arc indicator, contrast meter
4. `components/VoiceLineOverlay.tsx` - Trigger integration

---

## Appendix B: Technical Notes

### Freeze Frame Implementation Detail
The freeze frame system must:
1. Set `getEffectiveTimeScale()` to return 0 for N frames
2. Continue rendering (particles, UI update)
3. NOT freeze audio (bass drop should play during freeze)
4. Count actual frame updates, not wall time

### Audio System Architecture
After consolidation:
```
kent-fugue.ts (main music)
  ↓
audio.ts (sound effects + spatial)
  ↓
procedural-music.ts (generated layers, simplified)
```

Delete: `emergent-audio.ts`

### Particle Budget
Target: 60fps with up to 500 particles
Current: ~200 particles max before stuttering
Solution: Use object pooling, reduce per-particle state

---

## Conclusion

**The game is 78% complete by feature count but 60% complete by feel.**

The transformation mandate is clear: *"Whatever exists is not good enough."*

Implementing this proposal will take the game from "functional with intellectual depth" to "clip-worthy spectacle that makes players gasp."

**Total estimated effort**: 43 hours over 4 weeks
**Expected outcome**: EMPIRICAL evidence tier (< 0.30 Galois loss)

---

*"Daring, bold, creative, opinionated but not gaudy."*

This is the minimum standard. Let's transform.
