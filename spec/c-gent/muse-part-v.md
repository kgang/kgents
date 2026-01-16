# Creative Muse Protocol: Part V — Collaboration & Constraints

> **DEPRECATED**: This document has been superseded by the Muse v2.0 rewrite.

**Status:** DEPRECATED (2025-01-11)
**Superseded By:** `muse.md` v2.0 (The Co-Creative Engine)
**Reason:** Core paradigm shift from multi-human collaboration to AI-Kent dialectic

---

## Deprecation Notice

The v2.0 rewrite of the Creative Muse Protocol fundamentally changed the model:

| v1.x (This Document) | v2.0 (New Core) |
|---------------------|-----------------|
| Multiple humans in writers rooms | Kent + AI dialectic |
| Consensus and voting | Kent's taste as sole arbiter |
| Scheduled sync points | Rapid 30-50 iteration cycles |
| Collaborative flow preservation | Individual flow maximization |
| Team-scale creativity | Kent-at-10x creativity |

**The core insight**: Breakthrough creative work emerges from *dialectical tension between human taste and AI generation*, not from orchestrating human collaboration. The 30-50 iteration principle is incompatible with multi-human consensus—you cannot iterate 50 times with a committee.

---

## What Happened to This Content?

### Writers Rooms — REMOVED

The Writers Room model assumed multiple human creators collaborating. The v2.0 model replaces this with:

- **AI as Amplifier**: Generates 50 variations (replaces multiple writers pitching)
- **AI as Contradictor**: Challenges choices (replaces creative debate)
- **AI as Memory**: Remembers all prior decisions (replaces collective memory)
- **Kent as Sole Selector**: Final taste authority (replaces showrunner + consensus)

If multi-human collaboration is needed for a specific project (e.g., TV production after initial creation), that belongs in domain-specific documentation, not the core Muse protocol.

### Constraint Envelopes — MOVED TO DOMAIN APPENDICES

The four-layer constraint model (Regulatory → Platform → Audience → Creative) remains valid but is domain-specific:

```
See:
- spec/c-gent/domains/youtube.md (for YouTube constraints)
- spec/c-gent/domains/childrens-tv.md (for FCC/COPPA constraints)
- spec/c-gent/domains/publishing.md (for book constraints)
```

The core v2.0 spec includes `constraint_tightness` as a factor in the breakthrough formula—tighter constraints force innovation. But the *specific* constraints are domain knowledge, not core protocol.

### Age-Band Calibration — MOVED TO DOMAIN APPENDIX

Children's content constraints (COPPA, developmental appropriateness, cognitive requirements) are highly specialized. They belong in:

```
See: spec/c-gent/domains/childrens-tv.md
```

### Collaborative Flow — SUBSUMED

The concern about "maintaining individual flow in group work" is obviated by the new model:

- **Problem (v1.x)**: How do multiple humans collaborate without breaking each other's flow?
- **Solution (v2.0)**: There is only one human. Kent's flow is maximized because the AI handles volume generation asynchronously.

The AI never interrupts—Kent requests amplification, contradiction, or critique when ready.

---

## Migration Guide

If you're implementing Muse functionality:

1. **Ignore this document** — It's preserved only for historical reference
2. **Read `muse.md` v2.0** — The authoritative spec
3. **For domain constraints**, check if domain-specific appendices exist
4. **For collaboration needs**, consider if v2.0's AI roles can substitute:
   - Need multiple perspectives? → AI Amplifier generates 50+
   - Need creative debate? → AI Contradictor challenges
   - Need editorial feedback? → AI Critic applies Kent's taste

---

## Archived Content Reference

The original content is preserved below in collapsed form for reference. DO NOT implement from this—it represents a deprecated paradigm.

<details>
<summary>ARCHIVED: Writers Room Model (do not implement)</summary>

```python
# This model assumed multiple human creators collaborating
# The v2.0 model replaces this with AI roles

class RoomRole(Enum):
    SHOWRUNNER = auto()       # → Kent (sole creative authority)
    HEAD_WRITER = auto()      # → AI Amplifier
    WRITER = auto()           # → AI Amplifier (generates options)
    PUNCH_UP = auto()         # → AI Amplifier (variation generation)
    RESEARCHER = auto()       # → AI Memory (fact-checking, consistency)
    SENSITIVITY = auto()      # → Constraint Envelope
    PRODUCTION = auto()       # → Constraint Envelope

# The Yes-And protocol becomes:
# - AI amplifies (Yes-And default)
# - AI contradicts (productive challenge)
# - Kent defends or discovers
```

</details>

<details>
<summary>ARCHIVED: Constraint Envelope Types (move to domain docs)</summary>

The four-layer model remains valid:

1. **REGULATORY** — Legal: FCC, COPPA, copyright
2. **PLATFORM** — Platform: YouTube algo, Netflix format
3. **AUDIENCE** — Audience: age, culture, expectations
4. **CREATIVE** — Self-imposed: artistic choices (this is Kent's taste)

Outer layers (regulatory) are hard constraints; inner layers (creative) are Kent's taste operationalized. This maps to v2.0's `TasteVector.never` (hard avoidances) and domain-specific constraint checks.

</details>

<details>
<summary>ARCHIVED: Age-Band Requirements (move to children's domain doc)</summary>

```python
# Still valid for children's content, but domain-specific

class AgeBand(Enum):
    PRESCHOOL = "preschool"       # 2-5 years
    EARLY_ELEMENTARY = "early_elementary"  # 5-7 years
    ELEMENTARY = "elementary"      # 7-10 years
    TWEEN = "tween"               # 10-13 years
    TEEN = "teen"                 # 13-17 years

# Cognitive requirements, content restrictions, regulatory requirements
# all remain valid but belong in domain-specific documentation
```

</details>

---

## Laws (Historical)

These laws were valid for the multi-human collaboration model:

| # | Law | v2.0 Status |
|---|-----|-------------|
| 1 | showrunner_final | → Kent's taste is final (same principle) |
| 2 | yes_and_default | → AI Amplifier generates, doesn't block |
| 3 | constraint_layers | → Preserved in domain appendices |
| 4 | age_band_strict | → Domain-specific (children's content) |
| 5 | coppa_hard | → Domain-specific (children's content) |
| 6 | flow_respecting | → Obviated (only Kent's flow matters) |
| 7 | sync_scheduled | → Obviated (no team to sync) |

---

*"Constraints are the banks of the river—they give the water its power."*

This insight survives. The mechanism changed.

*Part V of Creative Muse Protocol | DEPRECATED 2025-01-11*
*Superseded by: muse.md v2.0 (The Co-Creative Engine)*
