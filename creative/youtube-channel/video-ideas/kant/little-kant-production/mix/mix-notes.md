# Mix Notes

Mixing instructions and level guidance for Little Kant pilot.

---

## Reference Levels

| Element | Level (dB) | Notes |
|---------|------------|-------|
| **Dialogue** | 0dB (reference) | All other levels relative to this |
| **SFX (foreground)** | -6 to -12dB | Sounds that punctuate action |
| **SFX (background)** | -12 to -18dB | Environmental sounds |
| **Ambient beds** | -18 to -24dB | Should be felt, not heard |
| **Music** | -12 to -18dB | Support, not compete |

---

## Scene-by-Scene Mix Notes

### Cold Open (0:00-1:00)
- Dialogue is minimal (just "There.")
- Clock ticking can be prominent (-6dB)
- Music carries the emotional weight
- Build from intimate (room) to expansive (airport, plane)
- Use panning: clocks left/right, centered on Kant's voice

### Act One - School (1:15-4:00)
- School chaos loud at first (-6dB), then duck under dialogue
- Van scene: ambient at -22dB, very subtle
- Footsteps should match pace of dialogue rhythm
- Apple bite: close-mic'd, satisfying crunch (-8dB)
- Slight room reverb on van dialogue (they're outside, metal surface)

### Act Two - Demon (4:00-5:30)
- Start with unsettling quiet
- Fluorescent flicker should make you uncomfortable (-10dB)
- Reality warp: LOUD moment (-3dB), then quick duck
- Demon voice: add slight delay (20-40ms), very subtle chorus effect
- Transition INTO philosophy space should be jarring

### Act Three - Trolley (5:30-9:15)
- Industrial ambient starts low (-24dB), builds to (-12dB) at climax
- Train sounds follow same build pattern
- Voices from the tracks: slight distance reverb, desperate quality
- Kant's voice: dry, present, no effects (he's grounded)
- The SILENCE at 8:05 must be HARD CUT - no fade
- Post-silence: tinnitus ring, then slow ambient return

### Resolution (9:15-10:30)
- Return to normal should feel WARMER
- Same hallway ambience but roll off high frequencies (less harsh)
- Three footsteps: give each character distinct pan position
- Van sunset: wide stereo, birds L/R, traffic center
- Music can breathe here, slightly louder (-14dB)

### Post-Credits (11:00-11:10)
- Extremely intimate, close
- Office ambience barely audible (-28dB)
- SFX close-mic'd, dry
- Voice dry, present, clinical
- Hard cut to silence at the end

---

## Processing Chain

### Dialogue Processing
1. **Noise reduction** (if needed) - light touch
2. **EQ**: High-pass at 80Hz, slight presence boost at 2-4kHz
3. **Compression**: Ratio 3:1, threshold -18dB, soft knee
4. **De-essing**: If sibilance issues, gentle at 6-8kHz

### SFX Processing
1. **EQ**: Shape to fit scene (roll off competing frequencies)
2. **Reverb**: Match the space (short for hallway, long for industrial)
3. **Pan**: Place in stereo field appropriately

### Ambient Processing
1. **Loop seamlessly**: Crossfade ends
2. **EQ**: Roll off highs for warmth, lows for clarity
3. **Compression**: Gentle, keep dynamics but control peaks

### Music Processing
1. **EQ**: Carve out space for dialogue (duck 1-4kHz slightly)
2. **Sidechain compression**: Duck under dialogue (subtle, 2-3dB)
3. **Stereo width**: Keep wide but not competing

---

## Mastering

### Target Specs
- **Loudness**: -16 LUFS (podcast standard)
- **True Peak**: -1dB ceiling
- **Dynamic Range**: 8-12 dB (preserve dynamics for drama)

### Mastering Chain
1. **EQ**: Subtle tonal balance
2. **Multiband compression**: Gentle, control low end
3. **Limiter**: -1dB ceiling, transparent
4. **Loudness meter**: Verify -16 LUFS

---

## Automation Notes

Key moments requiring level automation:

| Timestamp | Automation |
|-----------|------------|
| 1:15 | School chaos fade in over 3 seconds |
| 4:20-4:45 | Tension build: ambient +6dB over 25 seconds |
| 5:50-8:00 | Train build: +12dB over 2+ minutes |
| 8:05 | HARD CUT to silence (no automation, just cut) |
| 9:10 | Ambient fade back in over 5 seconds |
| 10:30-11:00 | Music gentle swell +3dB for ending |

---

## Listening Checklist

Before final export, listen on:

- [ ] Studio headphones (detail check)
- [ ] Consumer earbuds (how most will hear it)
- [ ] Phone speaker (worst case scenario)
- [ ] Car stereo (if possible)
- [ ] Laptop speakers (common listening)

### What to Check
- [ ] Dialogue always intelligible
- [ ] No frequency buildup in busy sections
- [ ] Transitions smooth (or intentionally jarring where needed)
- [ ] Emotional beats land
- [ ] Hard silence at 8:05 is actually silent
- [ ] Post-credits sting is clear and ominous

---

## Software Settings

### If Using Descript
- Project sample rate: 48kHz
- Bit depth: 24-bit
- Export: WAV for master, MP3 320kbps for distribution

### If Using Audacity
- Project rate: 48000Hz
- Default sample format: 32-bit float
- Export: WAV (signed 24-bit PCM) for master

### If Using Logic/Audition
- Sample rate: 48kHz
- Bit depth: 24-bit
- Dithering: On for final export to 16-bit

---

## Files

```
mix/
├── mix-notes.md (this file)
├── mix-session-v1.descript (or .aup3, .sesx, etc.)
├── mix-session-v2.descript
├── mix-FINAL.descript
└── stems/
    ├── dialogue-stem.wav
    ├── sfx-stem.wav
    ├── ambient-stem.wav
    └── music-stem.wav
```

---

## Master Checklist

- [ ] All elements imported and organized
- [ ] Dialogue levels consistent throughout
- [ ] SFX placed and leveled
- [ ] Ambient beds looping cleanly
- [ ] Music cues placed and automated
- [ ] Key transitions tested
- [ ] Full playthrough completed
- [ ] Listening check on multiple devices
- [ ] Mastering chain applied
- [ ] LUFS verified at -16
- [ ] Export stems for future flexibility
