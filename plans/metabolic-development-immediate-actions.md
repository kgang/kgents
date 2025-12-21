# Metabolic Development: Immediate Next Steps

> *"Daring, bold, creative, opinionated but not gaudy"*

**Status:** Ready for Implementation
**Canonical Spec:** `spec/protocols/metabolic-development.md`
**Priority:** HIGH — Transforms daily development experience

---

## What Just Happened

Four brainstorming streams synthesized into **Metabolic Development Protocol**:

1. ✅ Created `spec/protocols/metabolic-development.md` (canonical spec)
2. ✅ Archived source brainstorms to `brainstorming/_archive/2025-12-week51-synthesized-metabolic/`
3. ✅ Defined T-shaped architecture: lateral infra + vertical journeys
4. ✅ Integrated with existing implementations (ASHC, Living Docs, Interactive Text)

---

## Immediate Actions (This Week)

### Action 1: Morning Coffee D-gent Migration (Day 1-2)

**Why First:** Foundation for all metabolic features. No stigmergy without persistence.

```bash
# Files to create
impl/claude/models/voice.py          # VoiceCapture SQLAlchemy model
impl/claude/services/liminal/coffee/persistence.py  # VoicePersistence class

# Files to modify
impl/claude/services/providers.py    # DI wiring
impl/claude/services/liminal/coffee/core.py  # Inject new persistence
```

**Success:** `kg coffee begin` persists via D-gent, not JSON files.

### Action 2: Living Docs Hydrator Wiring (Day 2-3)

**Why Second:** Hydrator exists but isn't wired to CLI or skill.

```bash
# Create CLI handler
impl/claude/protocols/cli/handlers/docs_hydrate.py

# Wire to skill
.claude/commands/hydrate.md
```

**Commands:**
- `kg docs hydrate "implement verification"` → outputs context
- `/hydrate` skill in Claude Code → injects into session

**Success:** Hydration context appears in Claude Code session start.

### Action 3: Session State Machine (Day 3-4)

**Why Third:** Enables the metabolic polynomial—state-dependent behavior.

```bash
# Create session service
impl/claude/services/metabolism/__init__.py
impl/claude/services/metabolism/session.py
impl/claude/services/metabolism/polynomial.py
```

**Success:** `kg metabolism status` shows current state (DORMANT, FLOWING, etc.)

### Action 4: Cross-System Event Wiring (Day 4-5)

**Why Fourth:** Connects the pipeline. Without events, systems are silos.

```python
# In services/metabolism/events.py
METABOLIC_EVENTS = {
    "voice.captured": [stigmergy_handler, brain_handler],
    "context.hydrated": [session_handler],
    "session.ended": [crystallize_handler],
}

# Wire to SynergyBus
wire_metabolic_to_global_synergy()
```

**Success:** Voice capture triggers Brain crystal creation automatically.

---

## Quick Wins (Can Be Done Today)

### Win 1: `/hydrate` Skill Registration

Takes 15 minutes. Creates immediate value.

```markdown
# .claude/commands/hydrate.md
You are helping hydrate context for: $ARGUMENTS

1. Run `kg docs hydrate "$ARGUMENTS"`
2. Read the output
3. Surface the top 3 gotchas before proceeding
4. Keep voice anchors visible in your responses
```

### Win 2: Morning Coffee → Brain Wiring

Wire existing implementations. The code exists; just connect it.

```python
# In services/liminal/coffee/core.py
async def capture_voice(self, voice: MorningVoice) -> CaptureResult:
    # Existing capture logic...

    # NEW: Create Brain crystal
    if self._brain:
        await self._brain.capture(
            content=voice.raw_text,
            metadata={"type": "morning_voice", "date": voice.date}
        )
```

### Win 3: `kg coffee end` Reinforcement

Add pheromone reinforcement to existing end-of-session flow.

```python
# In services/liminal/coffee/ritual.py
async def complete_ritual(self, accomplished: bool) -> None:
    if accomplished:
        # Reinforce pheromones for today's concepts
        for concept in self._extract_concepts(self.morning_voice):
            await self._stigmergy.reinforce(concept, intensity=1.5)
```

---

## Not Now (Phase 2+)

These are valuable but not immediate:

- **Archaeology Full Implementation** — Stratum classification is useful but not blocking
- **Circadian Resonance** — Weekly patterns need data; build after 2+ weeks of captures
- **Interactive Text Task Completion** — Depends on verification integration
- **Evidence Reports in Commits** — Nice to have, not critical path

---

## Success Criteria

### By End of Week

- [ ] `kg coffee begin` persists to D-gent (not JSON)
- [ ] `kg docs hydrate "task"` returns focused context
- [ ] `/hydrate` skill works in Claude Code
- [ ] Voice capture → Brain crystal (automatic)
- [ ] Session state visible via `kg metabolism status`

### By End of Next Week

- [ ] Full morning start journey works end-to-end
- [ ] Hydration context injected into Claude Code sessions
- [ ] Evidence accumulates during editing
- [ ] Voice anchors preserved across sessions

---

## Anti-Patterns to Avoid

| Anti-Pattern | Instead |
|--------------|---------|
| Build all four systems in parallel | Start with persistence, layer up |
| Perfect stigmergy before shipping | Ship keyword matching, add vectors later |
| Delay until ASHC is complete | Wire what exists, enhance incrementally |
| Over-engineer session state | Start with 3 states: DORMANT, FLOWING, CRYSTALLIZING |

---

## Voice Anchors for This Work

*"Tasteful > feature-complete"* — Ship working hydration before perfect archaeology.

*"The persona is a garden, not a museum"* — Metabolic development grows with use.

*"Depth over breadth"* — Focus on the morning start journey before expanding.

---

*Created: 2025-12-21*
*Ready for implementation.*
