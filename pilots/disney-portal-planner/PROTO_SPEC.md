# Disney Portal Planner: Itinerary as Proof

Status: proto-spec

> *"The day is the proof. The portal is the commitment. Joy is transparent."*

## Narrative
A trip plan is not a list—it is a series of commitments. Every portal expansion is a witnessed act, every tradeoff is surfaced, and each day becomes a crystal of intent, energy, and joy. The system makes planning feel like narrative design, not logistics.

## Personality Tag
*This pilot believes a day should feel earned, not accidental. Planning is adventure, not spreadsheet labor.*

## Objectives
- Turn itinerary construction into a chain of **justified decisions**. Every expansion is a mark; every collapse is a choice.
- Make tradeoffs **explicit** through constitutional scoring: where joy was traded for composability, where ethics constrained logistics.
- Produce daily crystals that compress the plan into a **portable memory artifact**—a story of the day, not a schedule.

## Epistemic Commitments
- Portal expansion and collapse are **state transitions that require marks**. Opening a portal is a commitment.
- Every itinerary node has a **derivation trail** with visible reasons and constraints. The lineage is traceable.
- Daily crystals must show **why the day exists**, not only what it contains. The crystal is warm—it remembers the intent.
- Constitutional scores must be **explainable in natural language** per day: "Joy was traded for walkability here."
- The final handoff (email, share) is **ceremonial**, not transactional. The artifact deserves a moment.

## Laws

- **L1 Portal Commitment Law**: A portal expansion is a commitment. It must emit a mark with intent and constraint.
- **L2 Day Integrity Law**: A day is valid only if its trail preserves the ordering logic that created it. The sequence is justified.
- **L3 Joy Transparency Law**: The system must surface where joy was traded for composability or ethics. No hidden sacrifices.
- **L4 Constraint Disclosure Law**: Any high-friction constraint (crowd levels, distance, dining windows) appears in the trail within one edge of its effects.
- **L5 Crystal Legibility Law**: A daily crystal must be readable as a **standalone narrative** without the itinerary. The day tells its own story.

## Qualitative Assertions

- **QA-1** Planning must feel like **narrative design**, not logistics spreadsheeting. The planner is an author, not an accountant.
- **QA-2** The portal interface must invite **curiosity** while preserving clarity. Wonder is encouraged; confusion is not.
- **QA-3** A day should feel **earned**, not accidental. The system defends the shape of the day.
- **QA-4** Email delivery must feel like a **ceremonial handoff**, not a notification. The artifact arrives with weight.

## Anti-Success (Failure Modes)

This pilot fails if:

- **Logistics takeover**: The interface looks like a project management tool—timelines, Gantt charts, optimization metrics. The magic is replaced by efficiency theater.
- **Joy burial**: Tradeoffs happen but are invisible. The user can't see where joy was sacrificed or why. The constitutional scoring is there but not *felt*.
- **Decision fog**: The user can't trace why a day is shaped the way it is. The derivation trail is too complex or too hidden. The plan feels arbitrary.
- **Cold handoff**: The email or share feels like a system notification—no personality, no ceremony, no sense that this is a *gift* to future-self or travel companions.
- **Overwhelm cascade**: The portal metaphor becomes confusing—too many layers, too much nesting, unclear what's expanded and what's collapsed. The map is scarier than the territory.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Portal Token** | Primary interaction surface | `user → Portal.expand(park, time)` |
| **Witness Mark** | Captures expansion, collapse, reschedule | `Portal.change → Mark.emit(intent, constraint)` |
| **Witness Trace** | Derivation lineage per day/location | `Mark[] → Trace.seal(day_id)` |
| **Witness Crystal** | Daily summary as narrative | `Trace → Crystal.compress(day_story)` |
| **ValueCompass** | Constitutional tradeoffs by day | `Crystal.weights → Compass.render()` |
| **Trail** | Derivation lineage navigation | `Trace → Trail.navigate(nodes)` |

**Composition Chain** (day construction):
```
PortalExpand(park, time)
  → Mark.emit(intent, constraint)
  → Trace.append(expansion_event)
  → [on reschedule] Mark.emit(reason)
  → [on day_complete] Crystal.compress(trace, story)
  → Compass.render(crystal.tradeoffs)
  → Trail.display(crystal, trace)
  → [on share] Handoff.ceremony(crystal, recipients)
```

## Canary Success Criteria

- A user can justify the schedule of a day **using only the trail and crystal**: "We hit Space Mountain early because crowd levels spike after 11am, and we traded the Haunted Mansion for a sit-down lunch because joy > exhaustion."
- The system surfaces a **tradeoff explanation** for any change with one click. Nothing is hidden.
- At least one crystal can be **shared externally** without loss of meaning—a friend or family member understands the day from the crystal alone.
- The user **looks forward to receiving the email**. The handoff feels like a gift, not a chore.

## Out of Scope

- Booking automation, ticketing, or real-time availability.
- Multi-destination planning (single park complex only).
- Budget tracking or expense management.
