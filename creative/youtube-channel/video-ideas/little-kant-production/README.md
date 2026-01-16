# Little Kant Audio Production

Quick start guide for producing the audio drama pilot "A Life (Well) Lived"

---

## Reference Documents

All source materials are in the parent folder (`../`):

| Document | Purpose |
|----------|---------|
| `little-kant-pilot-v5.md` | **Latest teleplay** - the script with stage directions |
| `little-kant-production-guide.md` | **Full production guide** - workflow, tools, mixing notes |
| `little-kant-characters.md` | Character backgrounds and voice direction |
| `little-kant.md` | Original series bible and world-building |

---

## Folder Structure

```
little-kant-production/
├── voices/           # Voice actor files & assignments
├── sfx/              # Sound effects organized by scene
│   ├── cold-open/
│   ├── act-one/
│   ├── act-two/
│   ├── act-three/
│   ├── resolution/
│   └── post-credits/
├── ambient/          # Background ambient loops
├── music/            # Music cues and generated tracks
├── mix/              # Working mix files
└── exports/          # Final exported versions
```

---

## Quick Start Checklist

### Day 1: Voice Generation (1 hour)
- [ ] Sign up for ElevenLabs Pro ($22/mo)
- [ ] Create new Project: "Little Kant - Pilot"
- [ ] Paste dialogue script (see production guide Part 5)
- [ ] Assign voices per `voices/voice-assignments.md`
- [ ] Generate first pass of audio

### Day 2: Voice Polish + SFX (2-3 hours)
- [ ] Listen through, note problem lines
- [ ] Regenerate as needed
- [ ] Export voice tracks to `voices/`
- [ ] Download SFX from Freesound per sfx lists
- [ ] Generate custom SFX via ElevenLabs

### Day 3: Assembly + Mix (2-3 hours)
- [ ] Import into Descript or Audacity
- [ ] Layer in ambient beds from `ambient/`
- [ ] Add SFX at timestamps
- [ ] Add music (subtle) from `music/`
- [ ] Mix levels per `mix/mix-notes.md`
- [ ] Export draft to `exports/`

### Day 4: Final Polish (1-2 hours)
- [ ] Listen on multiple devices
- [ ] Make adjustments
- [ ] Final master
- [ ] Add metadata
- [ ] Export final versions per `exports/export-checklist.md`

---

## Recommended Stack

| Purpose | Tool | Cost |
|---------|------|------|
| Voices | ElevenLabs Projects | $22/mo |
| Sound Effects | ElevenLabs SFX + Freesound.org | Free |
| Ambient/Music | Suno AI | $10/mo |
| Mixing | Descript (easiest) or Audacity (free) | $0-15/mo |

**Estimated Total Time:** 4-8 hours for polished result
**Estimated Cost:** $22-50

---

## Key Files in This Folder

| File | What It Contains |
|------|------------------|
| `voices/voice-assignments.md` | ElevenLabs voice selection per character |
| `sfx/*/sfx-list.md` | Timestamped SFX needs per scene |
| `ambient/ambient-beds.md` | Required ambient loop descriptions |
| `music/music-cues.md` | Suno prompts and music placement |
| `mix/mix-notes.md` | Level guidance and mixing instructions |
| `exports/export-checklist.md` | Final export formats and metadata |

---

*Production folder created: 2026-01-11*
