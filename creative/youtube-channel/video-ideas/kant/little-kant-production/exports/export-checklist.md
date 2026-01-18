# Export Checklist

Final export formats and metadata for Little Kant pilot.

---

## Required Exports

### 1. Master WAV (Archival)
**Filename:** `little-kant-pilot-master.wav`
**Specs:**
- Format: WAV
- Sample rate: 48kHz
- Bit depth: 24-bit
- Channels: Stereo
- Loudness: -16 LUFS

**Purpose:** Archive, future remasters, stems extraction

- [ ] Exported
- [ ] Specs verified
- [ ] Backed up to cloud

---

### 2. Distribution MP3 (Primary)
**Filename:** `little-kant-pilot.mp3`
**Specs:**
- Format: MP3
- Bitrate: 320kbps CBR
- Sample rate: 48kHz
- Channels: Stereo

**Purpose:** Podcast distribution, YouTube upload, sharing

- [ ] Exported
- [ ] Specs verified
- [ ] Metadata embedded

---

### 3. Preview MP3 (Sharing)
**Filename:** `little-kant-pilot-preview.mp3`
**Specs:**
- Format: MP3
- Bitrate: 128kbps
- Sample rate: 44.1kHz
- Channels: Stereo

**Purpose:** Quick shares, email, low-bandwidth preview

- [ ] Exported
- [ ] File size acceptable (<15MB)

---

### 4. Stems (Future Flexibility)
**Folder:** `stems/`
**Files:**
- `dialogue-stem.wav`
- `sfx-stem.wav`
- `ambient-stem.wav`
- `music-stem.wav`

**Specs:** Same as Master WAV (48kHz/24-bit)

**Purpose:** Re-mixing, translations, accessibility versions

- [ ] All 4 stems exported
- [ ] Stems sync when layered
- [ ] Backed up

---

## Metadata

### ID3 Tags (for MP3s)
```
Title: Little Kant - Pilot: A Life (Well) Lived
Artist: Kent Gang
Album: Little Kant (Audio Drama)
Year: 2026
Genre: Audio Drama / Podcast
Track: 1
Comment: Philosophical audio drama. Three teens. One demon. A trolley problem.
```

### Podcast Metadata
```
Episode Title: Pilot - A Life (Well) Lived
Episode Number: 1
Season: 1
Description: 
Immanuel Kant arrives at an American high school. He meets Diogenes and Carol.
A demon poses the trolley problem. Philosophy becomes real.

Duration: ~11 minutes
Explicit: No
```

- [ ] ID3 tags embedded
- [ ] Podcast metadata prepared

---

## Chapter Markers (Optional)

If your platform supports chapters:

| Chapter | Timestamp | Title |
|---------|-----------|-------|
| 1 | 0:00 | Cold Open |
| 2 | 1:00 | Title |
| 3 | 1:15 | Act One: The Parking Lot |
| 4 | 4:00 | Act Two: The Demon |
| 5 | 5:30 | Act Three: The Tracks |
| 6 | 9:15 | Resolution |
| 7 | 10:30 | Tag |
| 8 | 11:00 | Post-Credits |

- [ ] Chapter markers added (if using)

---

## Platform-Specific Exports

### YouTube
**Filename:** `little-kant-pilot-youtube.mp3`
- Same as Distribution MP3
- Will need to pair with static image or video

- [ ] YouTube version ready
- [ ] Thumbnail/static image prepared

### Podcast Hosts (Spotify, Apple, etc.)
**Filename:** `little-kant-pilot.mp3`
- Distribution MP3 is correct format
- Verify meets host requirements (usually <200MB, <4 hours)

- [ ] File size verified
- [ ] RSS feed updated (if applicable)

### SoundCloud / Bandcamp
- Distribution MP3 or WAV accepted
- May want to include artwork

- [ ] Platform-specific upload ready

---

## Quality Verification

Before calling it done:

### Technical
- [ ] No clipping (true peak under -1dB)
- [ ] No DC offset
- [ ] Proper fade in/out (no clicks)
- [ ] Consistent loudness (-16 LUFS ± 1)
- [ ] Stereo image balanced

### Content
- [ ] All dialogue audible
- [ ] SFX properly timed
- [ ] Music not overpowering
- [ ] Emotional beats land
- [ ] Cold open hooks
- [ ] Ending satisfies but hooks

### Playback Test
- [ ] Full playthrough without interruption
- [ ] No glitches or artifacts
- [ ] Transitions smooth
- [ ] Silence at 8:05 is truly silent

---

## File Organization

Final export folder structure:

```
exports/
├── export-checklist.md (this file)
├── little-kant-pilot-master.wav
├── little-kant-pilot.mp3
├── little-kant-pilot-preview.mp3
├── little-kant-pilot-youtube.mp3
├── stems/
│   ├── dialogue-stem.wav
│   ├── sfx-stem.wav
│   ├── ambient-stem.wav
│   └── music-stem.wav
└── artwork/
    ├── cover-3000x3000.png (podcast)
    ├── cover-1280x720.png (youtube thumbnail)
    └── cover-1400x1400.png (soundcloud)
```

---

## Attribution Credits

Include in show notes / description:

```
LITTLE KANT - PILOT: "A LIFE (WELL) LIVED"

Written by Kent Gang
Produced by [Your Name]

Voice Synthesis: ElevenLabs
Sound Design: [Your Name]
Sound Effects: Freesound.org contributors (CC BY 3.0)
Music: Suno AI / [Source]

CAST:
Kant - ElevenLabs (Antoni)
Diogenes - ElevenLabs (Josh)
Carol - ElevenLabs (Rachel)
The Demon - ElevenLabs (Clyde)

---
A kgents production
```

- [ ] Credits written
- [ ] Attribution list complete
- [ ] Freesound credits documented

---

## Master Checklist

- [ ] Master WAV exported and verified
- [ ] Distribution MP3 exported and tagged
- [ ] Preview MP3 exported
- [ ] All stems exported and synced
- [ ] Metadata embedded
- [ ] Quality verification complete
- [ ] Files backed up (local + cloud)
- [ ] Credits prepared
- [ ] Ready for distribution
