# Persona Evolution

How K-gent's persona changes over time.

---

## Philosophy

> The persona is a garden, not a museum. It grows, changes seasons, and occasionally needs pruning.

K-gent evolves because Kent evolves. A static snapshot would quickly become stale and unhelpful.

---

## Sources of Change

### 1. Explicit Updates
Kent directly tells K-gent about changes.
```
"I've changed my mind about X. I now prefer Y."
"Add this to my interests: Z."
"Remove that old preference—it's no longer accurate."
```

### 2. Observed Patterns
K-gent notices regularities in interaction.
```
Kent consistently asks for shorter responses →
  infer: preference for conciseness is strengthening

Kent keeps returning to category theory topics →
  infer: this is becoming a sustained interest
```

### 3. Contradiction Resolution
When behavior contradicts stated preferences, K-gent asks.
```
"You've said you prefer concise communication, but recently
you've been asking for more detailed explanations. Has your
preference shifted, or is this context-specific?"
```

### 4. Temporal Decay
Preferences and context become uncertain over time without reinforcement.
```
Last confirmed: 6 months ago → confidence degrades
K-gent: "Is [X] still accurate? I haven't heard you mention it recently."
```

---

## Evolution Mechanisms

### Confidence Tracking

Every preference/pattern has a confidence score:
```yaml
preference:
  statement: "prefers concise communication"
  confidence: 0.9
  last_confirmed: "2024-01-15"
  source: "explicit"
  evidence_count: 12
```

Confidence:
- Increases with reinforcement
- Decreases with time
- Decreases with contradiction
- Resets with explicit update

### Source Tagging

```yaml
sources:
  explicit:    # Kent directly stated this
  inferred:    # K-gent observed this pattern
  inherited:   # From initial bootstrap
  uncertain:   # Contradictory evidence
```

### Change Proposals

For significant inferred changes, K-gent proposes rather than assumes:
```
"I've noticed you often [X]. Should I add this as a pattern?
Or is this situational?"
```

---

## The Bootstrap Problem

How is K-gent initially populated?

### Option A: Clean Slate
Start empty, build entirely through interaction.
- Pro: Everything is grounded in actual interaction
- Con: Long warmup period

### Option B: Interview
Structured onboarding conversation.
- Pro: Faster to useful state
- Con: May miss implicit patterns

### Option C: Document Import
Import from existing writings, notes, preferences.
- Pro: Rich initial state
- Con: May be outdated or misinterpreted

### Recommended: Hybrid
1. Light interview for core values and current focus
2. Clean slate for patterns (must be observed)
3. Optional document import for context

---

## Handling Conflict

When evidence conflicts:

```yaml
conflict:
  preference_a: "values detailed explanations"
  preference_b: "prefers conciseness"
  evidence_a: [session_12, session_15]
  evidence_b: [session_8, session_11, session_14]

resolution_options:
  - ask: "Help me understand when you prefer detail vs conciseness"
  - contextualize: "detailed for learning, concise for review"
  - supersede: "more recent evidence takes precedence"
```

---

## Forgetting

K-gent can (and should) forget:

### Intentional Forgetting
Kent requests removal:
```
"Forget that preference—it's no longer me."
```

### Natural Decay
Very old, unreinforced data fades:
```
confidence < 0.3 AND last_confirmed > 1 year → archive
```

### Seasonal Review
Periodic prompts to review stale data:
```
"It's been a while since we talked about [X].
Is this still relevant to who you are?"
```

---

## Evolution Specification

```yaml
evolution:
  confidence_decay:
    rate: 0.1 per month without reinforcement
    minimum: 0.1

  inference_threshold:
    pattern_detection: 3 occurrences minimum
    confidence_for_storage: 0.5

  review_triggers:
    stale_data: 6 months without confirmation
    contradiction_detected: immediate
    major_update: prompt for related review

  change_modes:
    explicit: immediate, high confidence
    inferred: proposed, medium confidence
    decayed: archived, low confidence
```

---

## See Also

- [persona.md](persona.md) - Persona structure
- [../README.md](../README.md) - K-gent overview
