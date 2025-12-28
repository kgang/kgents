# Disney Portal Planner: Itinerary as Proof

Status: **production**
**Implementation Scope: full**

> *"The day is the proof. The portal is the commitment. Joy is transparent."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L20)** — complete set
- **Implement ALL QAs (QA-1 through QA-11)** — complete set
- **Wire ALL API calls to real endpoints** — no mocks in production
- **Emit actual witness marks** — not just capture intent
- **Live data is mandatory** — see Data Source Contract below

The "Phased Delivery" section is a **product roadmap for user rollout**, not a scope limiter. The system is complete; phasing controls user exposure.

---

## Narrative
A trip plan is not a list—it is a series of commitments. Every portal expansion is a witnessed act, every tradeoff is surfaced, and each day becomes a crystal of intent, energy, and joy. The system makes planning feel like narrative design, not logistics.

## Personality Tag
*A day should feel earned, not accidental. Planning is adventure, not spreadsheet labor.*

## Objectives
- Turn itinerary construction into a chain of **justified decisions**. Every expansion is a mark; every collapse is a choice.
- Make tradeoffs **explicit** through constitutional scoring: where joy was traded for composability, where ethics constrained logistics.
- Produce daily crystals that compress the plan into a **portable memory artifact**—a story of the day, not a schedule.

## Epistemic Commitments
- Portal expansion and collapse are **state transitions that require marks**. Opening a portal is a commitment.
- Every itinerary node has a **derivation trail** with visible reasons and constraints. The lineage is traceable.
- Daily crystals must show **why the day exists**, not only what it contains. The crystal is warm—it remembers the intent.
- Constitutional scores must be **explainable in natural language** per day: "Joy was traded for walkability here."
- The shareable artifact (link, export) is **ceremonial**, not transactional. The artifact deserves a moment.

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
- **QA-4** Sharing must feel like a **ceremonial handoff**, not a system action. The artifact (URL, PDF, print) arrives with weight.

## Anti-Success (Failure Modes)

The system fails if:

- **Logistics takeover**: The interface looks like a project management tool—timelines, Gantt charts, optimization metrics. The magic is replaced by efficiency theater.
- **Joy burial**: Tradeoffs happen but are invisible. The user can't see where joy was sacrificed or why. The constitutional scoring is there but not *felt*.
- **Decision fog**: The user can't trace why a day is shaped the way it is. The derivation trail is too complex or too hidden. The plan feels arbitrary.
- **Cold handoff**: Sharing feels like a system notification—no personality, no ceremony, no sense that this is a *gift* to future-self or travel companions.
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
  → [on share] Handoff.ceremony(crystal, destination)
```

## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*

This pilot instantiates the Experience Quality Operad via `DISNEY_PORTAL_QUALITY_ALGEBRA`:

| Dimension | Instantiation |
|-----------|---------------|
| **Contrast** | variety, pacing, surprise, tradeoff_clarity |
| **Arc** | anticipation → exploration → peak_experience → resolution → memory |
| **Voice** | joyful ("Was it fun?"), practical ("Was it doable?"), ethical ("Were tradeoffs transparent?") |
| **Floor** | no_logistics_takeover, no_joy_burial, constraint_visible, crystal_readable |

**Weights**: C=0.30, A=0.40, V=0.30

**Implementation**: `impl/claude/services/experience_quality/algebras/disney_portal.py`

**Domain Spec**: `spec/theory/domains/disney-portal-quality.md`

## Success Criteria

- A user can justify the schedule of a day **using only the trail and crystal**: "We hit Space Mountain early because crowd levels spike after 11am, and we traded the Haunted Mansion for a sit-down lunch because joy > exhaustion."
- The system surfaces a **tradeoff explanation** for any change with one click. Nothing is hidden.
- A crystal can be **shared externally** without loss of meaning—a friend or family member understands the day from the crystal alone.
- The user **looks forward to sharing**. The handoff feels like a gift, not a chore.

---

## Consumer-Grade Amendment (v2)

> *"The park is alive. The plan breathes. The party moves as one."*

This amendment extends the core system with live data, party dynamics, and physical reality modeling.

---

### Laws (L6–L12)

- **L6 Liveness Law**: Data shown must declare its freshness. Stale data (>5min for wait times, >1hr for hours) must visually distinguish itself. The system never lies about what it knows.

- **L7 Graceful Degradation Law**: When live data is unavailable, the system falls back to historical patterns with explicit uncertainty. "Typically 45min at this hour" ≠ "45min now."

- **L8 Party Coherence Law**: A trip belongs to a party. Individual preferences are captured; the plan reflects **fused** preferences, not one person's override. Conflicts surface, not hide.

- **L9 Physical Constraint Law**: Bodies have limits. Energy budgets, walking distances, height requirements, and accessibility needs are first-class constraints that appear in trails, not afterthoughts.

- **L10 Reservation Commitment Law**: A reservation (dining, Lightning Lane, show) is a **harder** commitment than a portal expansion. It anchors the day's structure. Moving it requires explicit acknowledgment of cascade effects.

- **L11 Trip Integrity Law**: A multi-day trip is coherent. Days reference each other. "We're saving EPCOT for day 3" is captured, not lost. The trip crystal summarizes the arc, not just the days.

- **L12 Adaptation Law**: When reality diverges from plan (ride closure, weather, fatigue), the system proposes adaptations with transparent reasoning. It never silently reorders.

---

### Epistemic Commitments (Extended)

- Live data is **witnessed infrastructure**: Uses `WitnessMark.domain="disney-portal"` for all state changes. Marks flow through existing trace/crystal pipeline.
- Party preferences use **Fusion dialectic**: Individual → Synthesis → Fused plan. Leverages existing `FusionService` patterns.
- Reservations use **sealed marks**: Once confirmed, reservation marks are immutable (`sealed_by_crystal_id`). Cancellation creates new mark, not edit.
- Offline state uses **D-gent local-first**: Sync when connected, operate when not. Conflicts resolve via mark timestamps.

---

### Qualitative Assertions (QA-5 through QA-9)

- **QA-5** The system must feel **alive**—wait times pulse, hours update, closures appear. Static screens signal broken, not stable.

- **QA-6** Party members must feel **heard**. When preferences conflict, both sides see their input acknowledged in the fusion. No silent overrides.

- **QA-7** Physical limits must feel **respected**, not punishing. "You've walked 4 miles—consider a sit-down break" is care, not constraint.

- **QA-8** Multi-day planning must feel like **narrative arc**, not repeated daily planning. Day 3 knows about Day 1.

- **QA-9** Offline mode must feel **trustworthy**. User knows what's cached vs. what needs connection. No false confidence.

---

### Anti-Success (Extended Failure Modes)

- **Stale masquerade**: Live data ages silently. User sees "15min wait" that was true an hour ago. Trust collapses.

- **Preference tyranny**: One party member's choices dominate. Others feel like passengers, not planners.

- **Body blindness**: System suggests back-to-back attractions across the park. User exhausted by noon. Joy sacrificed to "optimization."

- **Reservation amnesia**: Dinner reservation exists but plan doesn't route toward it. Panic at 5:45pm.

- **Day isolation**: Each day planned in vacuum. User manually remembers "we did Haunted Mansion yesterday."

- **Offline panic**: Connection drops. User stares at spinner. Cached data exists but isn't surfaced.

- **Adaptation whiplash**: Ride closes, system silently reorders everything. User confused why plan changed.

---

### Success Criteria (Consumer-Grade)

| Criterion | Evidence |
|-----------|----------|
| **Liveness visible** | Wait time badges show "live" vs "typical" indicator. Stale data grays. |
| **Degradation graceful** | API down → historical fallback with uncertainty band. No blank screens. |
| **Party fusion working** | 2+ party members with different preferences → fused plan shows compromise reasoning. |
| **Physical limits honored** | 8-hour day with reasonable walk distances. Energy model visible in trail. |
| **Reservations anchor** | ADR at 6pm → afternoon plan routes toward restaurant. Visible in day shape. |
| **Trip coherence** | Day 3 crystal references Day 1 memories. Trip crystal tells 3-day story. |
| **Adaptation transparent** | Ride closure → system proposes alternatives with reasoning. User approves. |
| **Offline functional** | Airplane mode → cached park data, today's plan accessible. Sync indicator. |

---

### kgents Infrastructure Dependencies

| Need | Existing Infra | Extension Required |
|------|----------------|-------------------|
| Live data | `DisneyDataSource` protocol | Adapter for themeparks.wiki API |
| Domain filtering | `WitnessMark.domain` | Added in v2 schema |
| Crystal sealing | `sealed_by_crystal_id` | Added in v2 schema |
| Party fusion | `FusionService` | Apply to preference vectors |
| Offline sync | D-gent local-first | Already supported |
| AGENTESE exposure | `@node("world.disney-portal")` | New Crown Jewel service |
| Trail visualization | `CrystalTrailAdapter` | Wire to frontend |

---

### Phased Delivery (User Rollout Roadmap)

> **Note**: This phasing is for **user-facing feature rollout**, NOT implementation scope.
> The regeneration agent implements ALL phases. Feature flags control user exposure.

**Phase 1 (Foundation)**: Single-day, single-user, live wait times, crystallization. Laws L1–L5.

**Phase 2 (Party)**: Multi-person preferences, fusion, shared crystals. Laws L6–L8.

**Phase 3 (Trip)**: Multi-day coherence, reservations, trip crystals. Laws L9–L11.

**Phase 4 (Adaptation)**: Real-time replanning, offline resilience. Law L12.

**Implementation Requirement**: All phases are implemented. `FEATURE_FLAGS` control which capabilities are exposed to users at any given time.

---

## Comprehensive World Model Amendment (v3)

> *"The map IS the territory. Every nook has a name."*

---

### Laws (L13–L16)

- **L13 Total Coverage Law**: The model includes ALL park elements: attractions, dining (table/quick/snack), shows, parades, fireworks, character meets, play areas, hidden details, photo spots, restrooms, first aid. If a guest can experience it, it exists in the model.

- **L14 Real-Time Pulse Law**: Wait times, show times, parade routes, character locations, dining availability, and ride status update in real-time via live data feeds. The model breathes with the park.

- **L15 Temporal Event Law**: Scheduled events (parades, fireworks, stage shows, character appearances) are first-class portals with start times, durations, and viewing locations. "Happily Ever After at 9pm from the hub" is a plannable commitment.

- **L16 Hidden Magic Law**: Easter eggs, hidden Mickeys, insider tips, and "locals know" spots are modeled as discoverable portals. The system rewards curiosity—"Did you know there's a secret menu item at Dole Whip?"

---

### Portal Taxonomy (Required Coverage)

| Category | Examples | Real-Time Data |
|----------|----------|----------------|
| **Attractions** | Rides, dark rides, coasters, shows | Wait time, status, LL return |
| **Dining** | Table service, quick service, snacks, lounges | Availability, mobile order status |
| **Entertainment** | Parades, fireworks, stage shows, street performers | Start time, route, viewing spots |
| **Characters** | Meet & greets, cavalcades, dining appearances | Location, wait, next appearance |
| **Experiences** | Play areas, interactive quests, photo ops | Availability, crowd level |
| **Services** | Restrooms, first aid, baby care, lockers | Wait, availability |
| **Hidden** | Easter eggs, insider tips, secret menus, hidden Mickeys | Discovery status |

---

### Anti-Success (World Model Failures)

- **Incomplete map**: User asks "where can I get a Dole Whip?" and the system doesn't know. The park knows more than the planner.

- **Stale world**: Parade was rerouted, system still shows old path. Reality and model diverge.

- **Event blindness**: User misses fireworks because the system didn't surface "Happily Ever After starts in 30 minutes."

- **Hidden nothing**: The system is purely functional—no delight, no secrets, no "did you know?" moments. It's a map, not a guide.

- **Character ghost**: "Meet Elsa" shows 10min wait but she left 20 minutes ago. Trust destroyed.

---

### Data Source Requirements

| Data Type | Source | Refresh Rate |
|-----------|--------|--------------|
| Wait times | ThemeParks.wiki API / Disney API | 1-5 min |
| Show times | Park calendar feed | Daily + live updates |
| Dining | Disney reservation API | Real-time |
| Characters | Location services / crowd reports | 5-10 min |
| Hidden gems | Curated database | Static + community |

---

---

## Production Amendment (v4)

> *"No known issues. No fallbacks. Real data or nothing."*

---

### Philosophical Stance

This is a **production system**, not a prototype. Every endpoint works. Every data source is live. Every failure mode is handled gracefully. The system is complete and polished.

---

### Laws (L17–L20)

- **L17 Zero Broken Law**: Every API endpoint must work. Every component must render. "Known issue" is a bug, not a status.

- **L18 Map Planning Law**: A spatial map view must exist for planning. Attractions plotted. Walking routes calculated. Clustering visible. The map is for *before* the park, not wayfinding inside.

- **L19 Data Integrity Law**: All park data comes from live sources. Stale data is marked. Missing data surfaces uncertainty. Never show false confidence.

- **L20 Comprehensive Coverage Law**: The portal database covers ALL Disney parks in scope. Every attraction, every height requirement, every coordinate. Real data, not illustrative samples.

---

### Map Visualizer Requirements

| Feature | Description |
|---------|-------------|
| **Portal Plotting** | All attractions positioned on park map (SVG/Canvas) |
| **Route Visualization** | Walking path between planned portals, with distance/time |
| **Cluster Suggestion** | Visual grouping: "these 3 are close, do together" |
| **Day Playback** | Animate the planned route as temporal sequence |
| **Drag Planning** | Reorder portals by dragging on map; auto-recalculate route |

**Constraint**: Map is a planning tool only. In-park wayfinding deferred to native apps.

---

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | All API endpoints return 200 within 5s | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | Live data sources respond | Yes |
| **QG-5** | Map view renders with ≥10 plotted portals | Yes |
| **QG-6** | At least one park has complete attraction coverage | Yes |

---

### Anti-Success (Production Failures)

- **Mock permanence**: Any mock data persisting in production. Real data or explicit error.
- **Silent degradation**: Data source fails, UI shows nothing. Must degrade gracefully with explanation.
- **Incomplete coverage**: User asks about an attraction that exists but isn't in the system.
- **Known issues list**: Anything on this list is a bug, not documentation.

---

## Data Source Contract

> *"Real data is the price of admission. The system knows what the park knows."*

### Live Data Sources (Required)

| Data Type | Primary Source | Fallback | Refresh |
|-----------|---------------|----------|---------|
| **Wait times** | ThemeParks.wiki API | Queue-Times.com | 1-5 min |
| **Park hours** | Disney official calendar | ThemeParks.wiki | Daily |
| **Show times** | Disney official schedule | Community feeds | 6 hours |
| **Dining availability** | Disney reservation API | Manual entry | Real-time |
| **Character locations** | ThemeParks.wiki / community | Historical patterns | 5-10 min |
| **Attraction status** | ThemeParks.wiki | Disney app scrape | 1 min |
| **Weather** | OpenWeatherMap / NWS | Weather.gov | 30 min |
| **Crowd levels** | Touring Plans / historical | Computed from wait times | Hourly |

### Static Data Sources (Required)

| Data Type | Source | Maintenance |
|-----------|--------|-------------|
| **Attraction database** | ThemeParks.wiki + manual curation | Quarterly audit |
| **Park maps** | OpenStreetMap + Disney official | On park change |
| **Height requirements** | Disney official | On policy change |
| **Coordinates** | OpenStreetMap / surveyed | Static |
| **Hidden gems** | Community-curated + editorial | Rolling |

### Qualitative Assertions (Data)

- **QA-10** Data freshness must be **visible and honest**. A wait time shows "5 min ago" not "current" if stale.
- **QA-11** Data gaps must be **acknowledged, not hidden**. "We don't have dining data for this location" is better than silence.

### Failure Conditions (Data Contract)

The system is **broken** (not degraded) if:

| Condition | Impact | Resolution |
|-----------|--------|------------|
| **FC-1** ThemeParks.wiki API unavailable for >1hr | Wait times unavailable | Surface "live wait times unavailable" with historical fallback |
| **FC-2** Zero parks have complete attraction data | Planning impossible | Block deployment until fixed |
| **FC-3** Weather API fails | Outdoor planning unreliable | Show "weather unavailable" badge |
| **FC-4** Stale data shown as fresh | Trust violation | Mark data age visually; refuse to display >24hr stale as current |
| **FC-5** Attraction in reality not in system | User confusion | Log gap, add to backlog, show "attraction not yet mapped" |

### Data Integrity Laws

- **DI-1**: Every displayed wait time must have a `fetched_at` timestamp. UI must show relative age.
- **DI-2**: Every attraction must have: name, coordinates, category, status. Missing fields = incomplete.
- **DI-3**: Park hours must update on calendar change. Outdated hours = system failure.
- **DI-4**: Graceful degradation must be **visually distinct** from live data. Gray vs. color, uncertainty bands, "(typically)" prefix.

---

## Out of Scope

- **Booking automation**: We plan, we don't transact. Reservations are *recorded*, not *made*.
- **Budget tracking**: Money is out of scope. Joy is the currency.
- **Multi-resort**: Single Disney complex per trip. No Universal crossovers.
- **Transportation logistics**: We plan the park, not the commute.
- **In-park wayfinding**: Map is for planning. GPS navigation deferred to native apps.
