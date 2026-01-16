# Little Kant: Audio Production Guide
## From Script to Polished Podcast Pilot

---

## EXECUTIVE SUMMARY

**Goal:** Produce an 11-minute audio drama pilot with distinct character voices, ambient soundscapes, and professional sound design.

**Recommended Stack:**
- **Voices:** ElevenLabs Projects (best quality-to-effort ratio)
- **Sound Effects:** ElevenLabs Sound Effects + Freesound.org
- **Ambient/Music:** Suno AI or Epidemic Sound
- **Mixing:** Descript (easiest) or Audacity (free)

**Estimated Time:** 4-8 hours for polished result
**Estimated Cost:** $22-50 (ElevenLabs Pro month + optional sound subscriptions)

---

## PART 1: VOICE AI PLATFORM COMPARISON

### Tier 1: Best for This Project

| Platform | Pros | Cons | Cost | Verdict |
|----------|------|------|------|---------|
| **ElevenLabs** | Best voice quality, Projects feature handles multi-character scripts, sound effects built-in, voice cloning available | Can sound "too perfect" without direction | $22/mo Pro | **RECOMMENDED** |
| **Replica Studios** | Designed for dramatic content, game/film quality, emotion controls | Steeper learning curve, more expensive | $24/mo | Great alternative |

### Tier 2: Viable but Limited

| Platform | Pros | Cons | Cost | Verdict |
|----------|------|------|------|---------|
| **Play.ht** | Good quality, easy UI | Fewer voice options, less control | $39/mo | Decent backup |
| **Murf.ai** | Clean interface, good for narration | Less dramatic range, corporate feel | $29/mo | Not ideal for drama |
| **Speechify** | Fast, good for long-form | Not designed for character work | $139/yr | Skip for this |

### Tier 3: Not Recommended for This

| Platform | Why Not |
|----------|---------|
| **NotebookLM** | Designed for 2-host discussion format, not dramatic scripts. Can't do distinct characters or emotional range. Would flatten the material. |
| **ChatGPT Voice** | Single voice only, no character variety |
| **Basic TTS** (AWS Polly, Google TTS) | Robotic, no emotional range |

### My Recommendation: ElevenLabs

**Why:**
1. **Projects feature** - Upload script, assign voices to characters, export full audio
2. **Voice variety** - 100+ preset voices, many suitable for teen characters
3. **Sound effects** - Built-in AI sound effect generation (new feature)
4. **Quality** - Currently the best prosody and emotional range
5. **Projects preserve timing** - Natural pauses between lines

---

## PART 2: VOICE SETUP

### Character Voice Assignments (ElevenLabs)

Here are my recommended voice matches from ElevenLabs' library:

| Character | Recommended Voice | Backup Voice | Settings |
|-----------|-------------------|--------------|----------|
| **KANT** | "Antoni" (young, clear, slight accent possible) | "Daniel" (British, precise) | Stability: 65%, Similarity: 80%, Style: 30% |
| **DIOGENES** | "Josh" (casual, gravelly) | "Adam" (deeper, relaxed) | Stability: 50%, Similarity: 75%, Style: 45% |
| **CAROL** | "Rachel" (warm, American) | "Elli" (younger, empathetic) | Stability: 60%, Similarity: 80%, Style: 40% |
| **DEMON** | "Clyde" (layered, otherworldly) | Custom blend | Stability: 40%, Similarity: 60%, Style: 60% |
| **CHEERLEADER** | "Lily" (clear, direct) | — | Stability: 70%, Similarity: 80%, Style: 35% |
| **JOCK** | "Ethan" (frustrated energy) | "Arnold" | Stability: 55%, Similarity: 75%, Style: 50% |
| **ANOTHER KID** | "Charlie" (scared) | — | Stability: 45%, Similarity: 80%, Style: 55% |
| **UNKNOWN VOICE** | "Callum" (clinical) | — | Stability: 80%, Similarity: 85%, Style: 20% |

### Voice Direction Notes

**For ElevenLabs prompting (use in voice notes):**

**KANT:**
```
German teenager, 15 years old. Speaks precisely and deliberately with subtle Germanic cadence.
Pauses 1-2 seconds before responding. Never rushed. Flat affect that warms slightly during rare jokes.
Thoughtful, not robotic. Translating from German in his head.
```

**DIOGENES:**
```
16 years old, Greek-American. Rough, slightly gravelly voice. Casual about profound things.
Sounds like someone who has nothing to lose. Amused by absurdity. Barking laugh when noted.
Street-wise but not aggressive.
```

**CAROL:**
```
15 years old, American girl. Warm, therapeutic cadence - therapist's kid energy.
Notices things before speaking. Can shift from gentle to fierce in one line.
Empathetic but not weak.
```

**DEMON:**
```
Ageless, genderless. Unsettling but not scary. Curious more than cruel.
Speaks with layered quality - one clear voice with whispered undertones.
Patient. Never tells anyone what to do. Just asks questions.
```

---

## PART 3: SOUND DESIGN

### Sound Effects Cue List

Export this as your SFX shopping list:

#### COLD OPEN (0:00-1:00)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 0:00 | Clock ticking (multiple, slightly unsync) | Freesound: "clock tick room" |
| 0:05 | Pen adjusting on desk | ElevenLabs SFX: "pen plastic scrape desk" |
| 0:15 | Footsteps in hallway (woman's) | Freesound: "heels hallway" |
| 0:25 | Suitcase lifting, tags rustling | ElevenLabs SFX: "suitcase lift luggage tag" |
| 0:35 | Airport ambience (German announcements) | Freesound: "airport terminal Germany" |
| 0:45 | Jet engine, cabin hum | Freesound: "airplane cabin interior" |

#### TITLE (1:00-1:15)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 1:00 | Single clean tone (tuning fork) | ElevenLabs SFX or synth |

#### ACT ONE - SCHOOL (1:15-4:00)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 1:15 | School morning chaos (outdoor) | Freesound: "high school exterior crowd" |
| 1:20 | Footsteps on concrete (steady) | Freesound: "walking concrete shoes" |
| 1:35 | Locker slam, laughter, coach whistle | Layer from Freesound |
| 1:45 | Paper unfolding | ElevenLabs SFX: "paper unfold" |
| 2:00 | Outdoor lunch ambience | Freesound: "schoolyard lunch" |
| 2:10 | Book opening, pages turning | Freesound: "book pages flip" |
| 2:20 | Metal climbing (van) | ElevenLabs SFX: "climbing metal van roof" |
| 2:25 | Apple biting, chewing | Freesound: "apple bite crunch" |
| 3:30 | Crate dragging on asphalt | ElevenLabs SFX |
| 3:55 | School bell (distant) | Freesound: "school bell distant" |

#### ACT TWO - DEMON (4:00-5:30)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 4:00 | Empty hallway ambience | Freesound: "empty corridor echo" |
| 4:10 | Books being arranged in locker | Freesound: "locker books" |
| 4:20 | Lights flickering, electrical hum | Freesound: "fluorescent flicker buzz" |
| 4:45 | Reality warp/glitch sound | Custom: layer vinyl scratch + digital glitch + reverb swell |

#### ACT THREE - TROLLEY (5:30-9:15)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 5:30 | Industrial space ambience | Freesound: "factory warehouse echo" |
| 5:35 | Steam hissing | Freesound: "steam pipe" |
| 5:40 | Metal grinding (rhythmic, heartbeat-like) | Custom: slow metal scrape + heartbeat layer |
| 5:50 | Train approaching (Victorian, wrong) | Freesound: "steam train approach" + pitch shift |
| 6:00 | Mournful train whistle | Freesound: "train whistle haunting" |
| 6:30 | Chains rattling | Freesound: "chains metal" |
| 8:00 | Train accelerating | Freesound: "train wheels speeding" |
| 8:05 | Sudden stop silence | Hard cut to nothing |
| 9:10 | Reality dissolve (reverse of glitch) | Reverse the 4:45 glitch |

#### RESOLUTION & TAG (9:15-11:00)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 9:15 | Normal hallway ambience (return) | Same as 4:00 but warmer |
| 9:30 | Locker closing | Freesound |
| 9:45 | Three sets of footsteps | Layer |
| 10:00 | Climbing van roof | Repeat from earlier |
| 10:30 | Sunset ambience (birds, distant car) | Freesound: "evening suburb birds" |
| 10:55 | Apple bite (shared) | Repeat |

#### POST-CREDITS (5 seconds)
| Timestamp | SFX Needed | Source Suggestion |
|-----------|------------|-------------------|
| 11:00 | Office ambience (quiet) | Freesound: "office quiet room tone" |
| 11:02 | File folder opening, pages | Freesound: "manila folder papers" |
| 11:05 | File closing (finality) | Freesound |

### Ambient Beds (Background Loops)

Create or source these as looping beds:

1. **Germany/Airport** (0:00-1:00) - Muted, melancholic
2. **School Exterior** (1:15-2:00) - Chaotic energy
3. **Parking Lot** (2:00-4:00) - Relaxed, sunlit
4. **Empty Hallway** (4:00-4:30) - Uncanny quiet
5. **Philosophy Space** (4:30-9:15) - Industrial, cold, rhythmic heartbeat
6. **Return to Normal** (9:15-10:30) - Warmer version of hallway
7. **Sunset Van** (10:30-11:00) - Peaceful, something beginning

### Music Suggestions

**Option A: AI-Generated (Suno)**
```
Prompt for opening: "Minimalist piano, melancholic, sparse notes, European art film,
no drums, ambient pads underneath, 60 BPM"

Prompt for Demon scene: "Dark ambient, industrial undertones, heartbeat rhythm,
tension without jump scares, philosophical horror, no melody"

Prompt for closing: "Warm acoustic guitar, sunset feeling, friendship beginning,
hopeful but understated, indie film"
```

**Option B: Licensed (Epidemic Sound)**
- Search: "philosophical ambient," "coming of age indie," "dark minimal tension"

---

## PART 4: PRODUCTION WORKFLOW

### Step-by-Step Process

#### PHASE 1: Voice Generation (2-3 hours)

**Step 1: Set up ElevenLabs Project**
1. Go to ElevenLabs → Projects
2. Create new project: "Little Kant - Pilot"
3. Copy/paste the dialogue-only version of the script (I'll provide below)

**Step 2: Assign Voices**
1. For each character name, assign the recommended voice
2. Apply voice settings (stability, similarity, style)
3. Add voice notes for each character (from Part 2)

**Step 3: Generate & Review**
1. Generate full audio
2. Listen through, mark any lines that need regeneration
3. Regenerate problem lines (ElevenLabs allows per-line regen)
4. Export as separate tracks per character OR single mixed track

**Step 4: Export**
- Export as WAV (highest quality) or MP3 320kbps
- If possible, export character stems separately for mixing flexibility

#### PHASE 2: Sound Design (2-3 hours)

**Step 1: Gather SFX**
1. Create folder structure:
   ```
   /little-kant-audio/
     /voices/
     /sfx/
       /cold-open/
       /act-one/
       /act-two/
       /act-three/
       /resolution/
     /ambient/
     /music/
     /exports/
   ```
2. Download SFX from Freesound.org (free, attribution required)
3. Generate custom SFX in ElevenLabs Sound Effects
4. Organize by scene

**Step 2: Create Ambient Beds**
1. Find or generate 30-60 second loops for each scene type
2. Ensure they loop cleanly (fade ends)

**Step 3: Source/Create Music**
1. Generate via Suno or license from Epidemic Sound
2. Keep it minimal—music should support, not dominate

#### PHASE 3: Mixing (2-3 hours)

**Option A: Descript (Recommended for Ease)**

Descript lets you edit audio like a document—see the words, drag to rearrange.

1. Import voice track(s)
2. Create a new composition
3. Use the timeline to add:
   - SFX on track 2
   - Ambient on track 3
   - Music on track 4
4. Adjust levels:
   - Dialogue: 0dB (reference)
   - SFX: -6 to -12dB
   - Ambient: -18 to -24dB
   - Music: -12 to -18dB
5. Add fades between scenes
6. Export as MP3 or WAV

**Option B: Audacity (Free)**

1. Import voice track
2. Create additional tracks for SFX, ambient, music
3. Use the time shift tool to align
4. Apply:
   - Compression to dialogue (ratio 3:1, threshold -18dB)
   - EQ to warm up voices (slight boost at 2-4kHz for presence)
   - Reverb to ambient/SFX (room size to match scene)
5. Master with limiter (-1dB ceiling)
6. Export

**Option C: Professional (Adobe Audition, Logic Pro)**

For broadcast quality:
1. Multitrack session with proper routing
2. Dialogue editing (remove breaths, normalize)
3. ADR-style processing (subtle room reverb matching)
4. Stem mixing
5. Mastering chain

#### PHASE 4: Final Polish (30 min - 1 hour)

1. **Listen on multiple devices** - Headphones, car, phone speaker
2. **Check levels** - Use LUFS meter, target -16 LUFS for podcasts
3. **Add metadata** - Title, description, chapter markers
4. **Export final versions:**
   - Master WAV (archival)
   - MP3 320kbps (distribution)
   - MP3 128kbps (preview/sharing)

---

## PART 5: DIALOGUE-ONLY SCRIPT

Copy this into ElevenLabs Projects:

```
[SCENE: COLD OPEN]

KANT: There.

[SCENE: ACT ONE - PARKING LOT]

DIOGENES: The lacrosse guys are fighting again.

CAROL: Which ones?

DIOGENES: Does it matter?

CAROL: Not really.

DIOGENES: New kid.

CAROL: German.

DIOGENES: How do you know?

CAROL: The book. The posture. The way he's not trying to look busy.

DIOGENES: He's just sitting there. Reading.

CAROL: Yeah.

DIOGENES: That's kind of tight.

CAROL: Should we—

DIOGENES: Nah. If he's one of us, he'll find us.

CAROL: And if he's not?

DIOGENES: Then he won't.

[PAUSE - Kant approaches]

DIOGENES: You need something?

KANT: No.

DIOGENES: Then why are you here?

KANT: I don't know yet.

DIOGENES: You're not scared of us.

KANT: Should I be?

DIOGENES: He's not scared of us.

CAROL: I noticed.

DIOGENES: Most people don't come over.

KANT: I'm not most people.

CAROL: Obviously.

DIOGENES: You gonna stand there?

KANT: Is there somewhere else to sit?

[PAUSE - comfortable silence]

CAROL: What were you reading?

KANT: Kant.

CAROL: Any good?

KANT: He's very certain about things.

DIOGENES: Is that good or bad?

KANT: I haven't decided.

[PAUSE - bell rings in distance]

DIOGENES: We stay through sixth period. It's a free.

KANT: I have class.

CAROL: Tomorrow, then.

KANT: Maybe.

[PAUSE - Kant walks away]

DIOGENES: He'll be back.

CAROL: Yeah.

DIOGENES: How do you know?

CAROL: He sat down.

[SCENE: ACT TWO - HALLWAY]

DEMON: You made a choice today.

KANT: I sat with some people.

DEMON: Is that what you call it?

KANT: What would you call it?

DEMON: The beginning of something you can't take back.

KANT: What do you want?

DEMON: To show you what you're really choosing. Everyone thinks about the trolley problem. But nobody really chooses. Until now.

[SCENE: ACT THREE - THE TRACKS]

DEMON: The Greater Good Express. Fifteen on the main track. Two on the side. The lever is between.

KANT: This isn't real.

DEMON: Reality is what you choose to do.

KANT: That's not an answer.

DEMON: It's the only answer that matters. Fifteen. Or two. You know the math. What's the answer?

KANT: There's no right answer.

DEMON: There's always an answer. People just don't like admitting it.

[FROM THE MAIN TRACK]

CHEERLEADER: Pull the lever.

JOCK: Fifteen to two. That's not even a question.

ANOTHER KID: Please. I don't even know them.

[FROM THE SIDE TRACK]

DIOGENES: This is new.

CAROL: Yeah.

DIOGENES: You're not gonna pull it.

KANT: How do you know?

DIOGENES: Because you sat down.

CAROL: That doesn't make sense.

DIOGENES: It makes perfect sense.

[THE CHOICE]

DEMON: Clock's ticking.

KANT: If I pull the lever, I kill them.

DEMON: If you don't, they die.

KANT: There's a difference.

DEMON: Is there?

KANT: I didn't create this. You did. Whatever happens on that track—the train is killing them. Not me. But if I pull this lever... I'm the one who decides who dies. I become part of it.

DEMON: That's just philosophy.

KANT: It's all I have.

[PAUSE - screams, then silence]

DEMON: You'd let fifteen people die for two strangers.

KANT: I'd refuse to kill two people for fifteen strangers. It's not the same thing.

DEMON: Interesting.

[SCENE: RESOLUTION - HALLWAY]

DIOGENES: Oh. You again.

KANT: Me again.

CAROL: We're going to the van.

DIOGENES: You look weird.

KANT: I had a strange afternoon.

CAROL: Want to talk about it?

KANT: No.

DIOGENES: Good answer.

[SCENE: TAG - VAN ROOF]

CAROL: You ever think about the trolley problem?

DIOGENES: No.

CAROL: You?

KANT: Sometimes.

CAROL: What would you do?

KANT: Kill you both.

CAROL: What?

KANT: Fifteen is greater than two. The math is simple.

[LONG PAUSE]

KANT: That was a joke.

DIOGENES: Jesus.

CAROL: Your delivery is insane.

KANT: I'm working on it.

DIOGENES: Don't. Keep it exactly like that.

[SCENE: POST-CREDITS]

UNKNOWN VOICE: Subject identified. Tag him.
```

---

## PART 6: ATTRIBUTION & LICENSING

### If Using Free Resources

**Freesound.org** - Most sounds are Creative Commons. Keep a credits list:
```
Sound Design Credits:
- [Sound name] by [username] (freesound.org) - CC BY 3.0
- [Sound name] by [username] (freesound.org) - CC0
```

**ElevenLabs** - You own the generated audio if you have a paid subscription.

**Suno AI** - Check current terms; generally you own outputs on paid plans.

### For Public Release

Include in episode description:
```
Voice synthesis: ElevenLabs
Sound design: [Your name]
Sound effects: Freesound.org contributors (see full credits)
Written by: Kent Gang
Produced by: [Your name/studio]
```

---

## PART 7: QUICK START CHECKLIST

### Today (1 hour)
- [ ] Sign up for ElevenLabs Pro ($22/mo)
- [ ] Create new Project
- [ ] Paste dialogue script
- [ ] Assign voices to characters
- [ ] Generate first pass of audio

### Tomorrow (2-3 hours)
- [ ] Listen through, note problem lines
- [ ] Regenerate as needed
- [ ] Export voice tracks
- [ ] Download key SFX from Freesound

### Day 3 (2-3 hours)
- [ ] Import into Descript or Audacity
- [ ] Layer in ambient beds
- [ ] Add SFX at timestamps
- [ ] Add music (subtle)
- [ ] Mix levels
- [ ] Export draft

### Day 4 (1-2 hours)
- [ ] Listen on multiple devices
- [ ] Make adjustments
- [ ] Final master
- [ ] Add metadata
- [ ] Export final versions

---

## APPENDIX: ALTERNATIVE APPROACHES

### If Budget Is Zero

1. **Voices:** Use Coqui TTS (open source) or Bark (open source) - quality is lower but free
2. **SFX:** Freesound.org only (all CC0 sounds)
3. **Mixing:** Audacity (free)
4. **Music:** Use royalty-free from YouTube Audio Library

### If Quality Must Be Maximum

1. **Voices:** Hire voice actors on Fiverr/Voices.com ($50-200 per character)
2. **SFX:** License from Soundsnap or Boom Library ($100-300)
3. **Mixing:** Hire audio engineer on Fiverr ($50-150)
4. **Music:** Commission original score ($200-500)

### If Time Is Very Limited (2 hours total)

1. Use ElevenLabs Projects for voices (single export)
2. Skip most SFX—just use 2-3 ambient beds
3. No music
4. Quick mix in Descript
5. Export and ship

---

*Production Guide Version 1.0*
*Created: 2026-01-11*
*For: Little Kant Pilot - "A Life (Well) Lived"*
