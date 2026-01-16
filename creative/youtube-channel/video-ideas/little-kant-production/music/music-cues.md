# Music Cues

Music placement and Suno AI generation prompts for Little Kant pilot.

---

## Philosophy: Music Should Support, Not Dominate

This is dialogue-driven drama. Music should:
- Fill emotional space, not compete with words
- Enter and exit subtly
- Never tell the audience what to feel
- Complement the philosophical weight

---

## Music Cue Placement

### CUE 1: Opening Theme (0:00-1:00)
**Placement:** Under cold open, Germany to airplane
**Function:** Establish tone, melancholy, transition

**Suno Prompt:**
```
Minimalist piano, melancholic, sparse notes, European art film,
no drums, ambient pads underneath, 60 BPM, contemplative,
single piano with subtle electronic texture, introspective,
2 minutes
```

**Level:** -18dB, ducking under any dialogue
**Notes:** Should feel like a Haneke or Tarkovsky film

- [ ] Generated
- [ ] Edited to length
- [ ] Level set

---

### CUE 2: School Arrival (1:00-1:15)
**Placement:** Title card only
**Function:** Brief punctuation

**Option A:** Single sustained note/chord from Cue 1
**Option B:** Silence with just the tuning fork SFX

**Level:** -12dB if used
**Notes:** Keep it minimal - the title speaks for itself

- [ ] Decided: Option A / Option B
- [ ] Implemented

---

### CUE 3: Parking Lot Theme (2:00-3:55)
**Placement:** Under the van conversation
**Function:** Warmth, friendship beginning, casual philosophy

**Suno Prompt:**
```
Warm acoustic guitar, indie film soundtrack, gentle fingerpicking,
afternoon sunlight feeling, friendship beginning, hopeful but understated,
no drums, subtle bass, American indie, Wes Anderson meets Linklater,
2 minutes, loop-friendly ending
```

**Level:** -20dB, barely noticeable
**Notes:** Should feel like possibility, not resolution

- [ ] Generated
- [ ] Edited to length
- [ ] Level set

---

### CUE 4: The Demon Appears (4:20-4:45)
**Placement:** Lights flicker through reality warp
**Function:** Unease, transition to philosophical space

**Suno Prompt:**
```
Dark ambient, tension building, no melody, subtle dissonance,
single held notes with slight detune, growing unease,
horror adjacent but intellectual not jump-scare,
30 seconds, building
```

**Level:** -16dB, building with the scene
**Notes:** This transitions INTO the philosophy space

- [ ] Generated
- [ ] Edited to length
- [ ] Level set

---

### CUE 5: Philosophy Space (4:45-9:10)
**Placement:** Entire trolley problem sequence
**Function:** Existential dread, the weight of choice

**Suno Prompt:**
```
Dark ambient, industrial undertones, heartbeat rhythm at 60 BPM,
tension without jump scares, philosophical horror, no melody,
metallic textures, cathedral reverb, existential weight,
Ligeti meets industrial, 5 minutes, evolving texture
```

**Level:** -18dB, can swell to -12dB at climax (8:00)
**Notes:** This is the musical heart of the episode

- [ ] Generated
- [ ] Edited to length
- [ ] Tension build mapped
- [ ] Level automation set

---

### CUE 6: Aftermath Silence (9:10-9:15)
**Placement:** Immediately after the choice
**Function:** Weight of what happened

**Option:** Complete silence (recommended)
OR: Single held note, very low, fading

**Notes:** Let the silence do the work

- [ ] Decided approach
- [ ] Implemented

---

### CUE 7: Reunion/Van Return (9:30-10:55)
**Placement:** Walking to van through sunset ending
**Function:** Catharsis, friendship, hope, something beginning

**Suno Prompt:**
```
Warm acoustic guitar, sunset feeling, friendship theme,
hopeful but earned not saccharine, indie film closing credits,
subtle strings entering halfway through, building warmth,
coming of age resolution, 90 seconds
```

**Level:** -18dB, can rise slightly at end
**Notes:** This should feel like relief and possibility

- [ ] Generated
- [ ] Edited to length
- [ ] Level set

---

### CUE 8: Post-Credits Sting (11:00-11:10)
**Placement:** Office scene
**Function:** Ominous, questions, hook for next episode

**Option A:** No music - just SFX (recommended)
**Option B:** Single low drone, barely audible

**Notes:** The line "Subject identified. Tag him." should land in near-silence

- [ ] Decided approach
- [ ] Implemented

---

## Alternative: Licensed Music (Epidemic Sound)

If not using Suno, search Epidemic Sound for:

| Cue | Search Terms |
|-----|--------------|
| Opening | "minimal piano contemplative european" |
| Parking Lot | "indie acoustic warm afternoon" |
| Demon | "tension subtle horror ambient" |
| Philosophy Space | "dark ambient industrial drone" |
| Reunion | "hopeful acoustic sunset indie" |

---

## Files

Place music files here:

```
music/
├── music-cues.md (this file)
├── cue1-opening-theme.wav
├── cue3-parking-lot.wav
├── cue4-demon-transition.wav
├── cue5-philosophy-space.wav
├── cue7-reunion-sunset.wav
└── stems/ (if keeping separated elements)
```

---

## Master Checklist

- [ ] All cues generated/sourced
- [ ] All cues edited to proper length
- [ ] All levels set and tested against dialogue
- [ ] Transitions between cues planned
- [ ] Philosophy space tension automation mapped
- [ ] Final decision on silent moments
