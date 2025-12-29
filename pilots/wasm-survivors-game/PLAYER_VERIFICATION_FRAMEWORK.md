# PLAYER Verification Framework for Game Regenerations

> *"A player who cannot see cannot judge. A player who cannot judge must build eyes."*

**Purpose**: This framework provides tools and protocols for PLAYER agents to properly verify animations, effects, and interactive gameplay elements in game regenerations.

---

## The Core Problem

Run 034 revealed a critical gap: PLAYER certified a game as 8.5/10 without actually verifying:
- Whether dash ghost trails rendered
- Whether sprite rotation was perceptible
- Whether enemy attack telegraphs were visible
- Whether the game "felt" right

**Root Cause**: Automated tests can verify STATE but not FEEL.

---

## The Three Layers of Verification

### Layer 1: State Verification (Automated)

What it catches:
- Functions exist and are called
- State transitions occur
- Data flows correctly

What it misses:
- Whether visual effects render
- Whether animations are perceptible
- Whether gameplay feels responsive

**Tools**: Playwright tests with `DEBUG_GET_GAME_STATE()`

### Layer 2: Visual Verification (Semi-Automated)

What it catches:
- Whether visual elements appear in screenshots
- Whether state changes produce visible differences
- Frame-by-frame animation presence

What it misses:
- Whether effects are PERCEPTIBLE at game speed
- Whether animations feel GOOD
- Whether timing feels RIGHT

**Tools**: Screenshot comparison, video capture, visual diff

### Layer 3: Feel Verification (Manual Required)

What it catches:
- Whether gameplay feels responsive
- Whether feedback is satisfying
- Whether the game is FUN

What it misses:
- Nothing (but requires human judgment)

**Tools**: Human play sessions with timestamp notes

---

## Required Debug Infrastructure

Every game pilot MUST expose these for PLAYER verification:

### 1. Debug Mode (URL: `?debug=true`)

```typescript
// Minimum required debug display
- Enemy state labels (FSM state, attack phase)
- Player state (dashing, invincible, etc.)
- Hitbox visualization (optional but helpful)
- FPS/performance metrics
```

### 2. Window Debug API

```typescript
// MINIMUM REQUIRED API
window.DEBUG_GET_GAME_STATE()     // Full game state snapshot
window.DEBUG_GET_ENEMIES()        // Enemy array with states
window.DEBUG_GET_PLAYER()         // Player state
window.DEBUG_SET_INVINCIBLE(bool) // Toggle god mode
window.DEBUG_SPAWN(type, x, y)    // Spawn specific enemy
window.DEBUG_SKIP_WAVE()          // Advance to next wave

// NICE TO HAVE
window.DEBUG_GET_LAST_DAMAGE()    // Last damage source
window.DEBUG_FORCE_[MECHANIC]()   // Force specific mechanic
```

### 3. Keyboard Shortcuts (In Debug Mode)

```
I     = Toggle invincibility
N     = Skip to next wave
K     = Kill all enemies
L     = Trigger level-up
1-5   = Spawn enemy types
B     = Force boss/special mechanic
```

---

## Animation Verification Protocol

### For Each Animation Type:

| Animation | Verification Method | Pass Criteria |
|-----------|--------------------|--------------|
| **Movement** | Screenshot at cardinal directions | Sprite visibly rotates toward movement |
| **Dash** | Screenshot during dash state | Ghost trail visible behind player |
| **Attack** | Video + state log | Wind-up → Active → Recovery visible |
| **Damage** | Health log over time | Health decreases on contact |
| **Death** | Screenshot of death screen | Cause attribution is correct |
| **Special** | Force via debug API | All phases render correctly |

### The Animation Test Template

```typescript
test('VERIFY: [Animation Name] is visible', async ({ page }) => {
  // 1. Setup
  await startGameWithDebug(page);

  // 2. Capture PRE state
  await page.screenshot({ path: 'pre-[animation].png' });
  const preState = await getGameState(page);

  // 3. Trigger animation
  await page.keyboard.press('[trigger key]');
  await page.waitForTimeout(50); // Mid-animation

  // 4. Capture DURING state
  await page.screenshot({ path: 'mid-[animation].png' });
  const midState = await getGameState(page);

  // 5. Capture POST state
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'post-[animation].png' });

  // 6. Verify STATE changed
  expect(midState.[relevant_property]).not.toEqual(preState.[relevant_property]);

  // 7. Log for manual review
  console.log('MANUAL CHECK: Compare pre/mid/post screenshots for visible [animation]');
});
```

---

## Run 034 Findings Applied

### BUG-1: Ghost Trail Not Visible

**Evidence**: dash-2-mid.png shows "DASHING" label and green glow, but no afterimage trail.

**Code Location**: `GameCanvas.tsx:313-338`

**Root Cause**: Ghost trail may be rendering but with insufficient opacity or wrong position.

**Verification**:
```typescript
// The ghost trail code EXISTS but may not be visible:
for (let i = 0; i < ghostTrail.length; i++) {
  const ghost = ghostTrail[i];
  const alpha = 0.3 * (1 - i / ghostTrail.length); // May be too transparent
  // ...
}
```

### BUG-2: Sprite Rotation Too Subtle

**Evidence**: rotation-right.png vs rotation-left.png show nearly identical sprite orientation.

**Code Location**: `GameCanvas.tsx:308`
```typescript
ctx.rotate(moveAngle * 0.3); // 0.3x multiplier is TOO SUBTLE
```

**Fix**: Increase multiplier to 0.8 or 1.0 for perceptible rotation.

### BUG-3: Attack Telegraphs Not Triggering

**Evidence**: "No attack phases detected in 10 seconds" in test output.

**Possible Causes**:
1. Enemies not entering attack state
2. Attack phases exist but render incorrectly
3. FSM timing prevents attack in test duration

---

## PLAYER Certification Checklist

Before certifying ANY game:

### Automated Checks (Must Pass)
- [ ] Debug mode enables with `?debug=true`
- [ ] `DEBUG_GET_GAME_STATE()` returns valid data
- [ ] State transitions occur (dash, damage, death)
- [ ] No JavaScript errors in console

### Visual Checks (Screenshots Required)
- [ ] Movement shows sprite rotation
- [ ] Dash shows visible ghost trail or effect
- [ ] Enemies show attack wind-up indicators
- [ ] Death screen shows correct attribution
- [ ] Special mechanics render all phases

### Feel Checks (Manual Play Required)
- [ ] Input feels responsive (< perceived 100ms)
- [ ] Feedback feels satisfying (screen shake, particles)
- [ ] Deaths feel fair (could see it coming)
- [ ] Would keep playing for 5+ minutes
- [ ] Would tell a friend about it

### The Final Question
> "Would I keep playing? Why or why not?"

If the answer is "YES" with specific reasons → CERTIFY
If the answer is "HESITANT" → LIST BLOCKERS, DO NOT CERTIFY
If the answer is "NO" → FAIL with specific issues

---

## Evidence Directory Structure

```
screenshots/animation-evidence/
├── dash-1-pre.png           # Before dash
├── dash-2-mid.png           # During dash
├── dash-3-post.png          # After dash
├── rotation-{direction}.png # Each cardinal direction
├── attack-telegraph.png     # Enemy wind-up visible
├── damage-{n}.png           # Damage over time
├── ball-{phase}.png         # Special mechanic phases
├── gameplay-{n}s.png        # Every 5 seconds of play
├── state-log.json           # Full state history
└── VERIFICATION_REPORT.md   # Summary with verdicts
```

---

## Integration with Triad Protocol

### DREAM Phase (1-3)
PLAYER identifies what qualia need verification from PROTO_SPEC.

### BUILD Phase (4-7)
PLAYER requests debug infrastructure in `.needs.creative.md` and `.needs.adversarial.md`:
```markdown
## PLAYER Infrastructure Requirements

### Must Have (Blockers if Missing)
- [ ] DEBUG_GET_GAME_STATE() working
- [ ] Debug mode with state labels
- [ ] Spawn controls for testing

### Should Have
- [ ] Invincibility toggle
- [ ] Wave skip
- [ ] Force special mechanic
```

### WITNESS Phase (8-10)
PLAYER uses infrastructure to verify EVERY qualia claim:
```markdown
## Qualia Verification Results

| Qualia | Method | Evidence | Verdict |
|--------|--------|----------|---------|
| "Dash feels powerful" | Screenshot + play | dash-mid.png shows glow | ✅ PASS |
| "Rotation responsive" | Screenshot comparison | sprites look identical | ❌ FAIL |
| "Deaths feel fair" | 10 play sessions | 7/10 saw death coming | ⚠️ PARTIAL |
```

---

## Future Improvements

### 1. Visual Diff Automation

```typescript
const diff = await compareImages('pre.png', 'post.png');
expect(diff.percentChanged).toBeGreaterThan(5); // 5% visual change
```

### 2. Video Analysis

Record gameplay video, then analyze frames for:
- Animation presence
- Effect duration
- Visual consistency

### 3. Input Latency Measurement

```typescript
const start = performance.now();
await page.keyboard.press('d');
await page.waitForFunction(() =>
  window.DEBUG_GET_PLAYER().velocity.x !== 0
);
const latency = performance.now() - start;
expect(latency).toBeLessThan(50); // < 50ms perceived latency
```

---

*Framework Version: 1.0*
*Created: 2025-12-28 (Run 034 Post-Mortem)*
*Author: PLAYER Agent*
