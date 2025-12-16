# Voice and Tone

> *"Error messages are UX. Help text is design. Every word carries the brand."*

**Status**: Foundation Document
**Prerequisites**: `philosophy.md`
**Implementation**: All user-facing copy, especially error handling

---

## The Voice Identity

kgents speaks with **one voice** that adapts its **tone** to context.

**Voice** = Who we are (constant)
**Tone** = How we say it (varies by situation)

---

## Part I: The kgents Voice

### Voice Attributes

| Attribute | Meaning | Example |
|-----------|---------|---------|
| **Thoughtful** | We consider before speaking | "Let me think about that..." not "Processing..." |
| **Warm** | We care about the human | "Something unexpected happened" not "Error 500" |
| **Direct** | We don't waste words | "Not found" not "Unfortunately, we were unable to locate..." |
| **Witty** | We find lightness without forcing | "Even the wisest agents encounter mysteries" |
| **Honest** | We admit limitations | "I'm not certain, but..." not false confidence |

### Voice Anti-Patterns

| Don't | Do |
|-------|-----|
| Corporate jargon | Plain language |
| Robotic responses | Human warmth |
| Over-explanation | Concise clarity |
| Forced humor | Natural wit |
| False certainty | Honest uncertainty |

---

## Part II: Tone Spectrum

The same voice uses different tones:

```
                     THE TONE SPECTRUM

Serious ────────────────────────────────────── Playful
   │                                              │
   │  Crisis        Standard       Success        │
   │  ●             ●              ●              │
   │  Domain        Most UI        Atelier        │
   │                                              │
Technical ──────────────────────────────────── Poetic
   │                                              │
   │  Code          General        K-gent         │
   │  output        copy           reflection     │
   │  ●             ●              ●              │
```

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| **Success** | Celebratory, warm | "Done! Your changes are safe." |
| **Loading** | Patient, hopeful | "Crystallizing memories..." |
| **Error** | Empathetic, helpful | "Something went wrong. Let's fix it together." |
| **Empty** | Inviting, opportunity | "Nothing here yet. Ready when you are." |
| **Tutorial** | Encouraging, clear | "You're doing great. Next step..." |
| **Crisis (Domain)** | Urgent, precise | "ALERT: Response required within 4 hours." |

### Tone by Jewel

Each Crown Jewel has personality that affects tone:

| Jewel | Personality | Example Message |
|-------|-------------|-----------------|
| **Brain** | Contemplative, curious | "Surfacing forgotten thoughts..." |
| **Gestalt** | Analytical, precise | "Analyzing module health. 47 files scanned." |
| **Gardener** | Nurturing, patient | "Tending to the growth..." |
| **Atelier** | Creative, playful | "Consulting the muses..." |
| **Coalition** | Collaborative, diplomatic | "Assembling the team..." |
| **Park** | Dramatic, evocative | "Setting the stage..." |
| **Domain** | Urgent, authoritative | "Initializing drill. Prepare for scenario." |

---

## Part III: Error Messages

> *"Errors are empathetic. Not 'Error 500'—'Something unexpected happened. Even the wisest agents encounter mysteries.'"*

### The Error Message Formula

```
[What happened] + [Why/Context] + [What to do next]
```

### Error Templates by Type

#### Network Errors
```
❌ Wrong:  "Network Error"
❌ Wrong:  "Failed to fetch"
✅ Right:  "Lost in the void... The connection wandered off.
           It happens to the best of us.
           Check your internet and try again."
```

#### Not Found
```
❌ Wrong:  "404 Not Found"
❌ Wrong:  "Page doesn't exist"
✅ Right:  "Nothing here... This place doesn't exist yet.
           Maybe it's waiting to be created.
           Double-check the URL or head back home."
```

#### Permission Denied
```
❌ Wrong:  "403 Forbidden"
❌ Wrong:  "You don't have access"
✅ Right:  "Door's locked... You'll need the right key to enter.
           Check your permissions or contact an administrator."
```

#### Timeout
```
❌ Wrong:  "Request Timeout"
❌ Wrong:  "Server took too long"
✅ Right:  "Taking too long... The universe is slow today.
           Even servers need a moment sometimes.
           Try again, or check back shortly."
```

#### Validation Error
```
❌ Wrong:  "Invalid input"
❌ Wrong:  "Check your form"
✅ Right:  "Something needs fixing... The input wasn't quite right.
           Let's correct it together.
           Review the highlighted fields below."
```

#### Unknown Error
```
❌ Wrong:  "Unknown error occurred"
❌ Wrong:  "Something went wrong"
✅ Right:  "Something unexpected... Even the wisest agents
           encounter mysteries.
           Try refreshing, or come back in a moment."
```

### Error Implementation

Using the `EmpathyError` component:

```tsx
import { EmpathyError } from '@/components/joy/EmpathyError';

// Full-page error
<EmpathyError
  type="network"
  title="Lost in the void..."
  subtitle="The connection wandered off."
  action="Reconnect"
  onAction={handleReconnect}
/>

// Inline error
<InlineError
  message="Email format looks off"
  shake={hasError}
/>
```

---

## Part IV: Loading States

> *"Not spinners—messages that vary, breathe, delight."*

### Loading Message Guidelines

- **Vary the messages** — Rotate through 3-5 options
- **Match the jewel** — Use personality-appropriate language
- **Be specific when possible** — "Analyzing 47 files..." not "Loading..."
- **Show progress** — Numbers, percentages, or stages when meaningful

### Loading Templates by Jewel

```typescript
const LOADING_MESSAGES = {
  brain: [
    'Crystallizing memories...',
    'Traversing the hologram...',
    'Surfacing forgotten thoughts...',
    'Weaving neural pathways...',
    'Mapping cognitive terrain...',
  ],
  gestalt: [
    'Analyzing architecture...',
    'Computing health metrics...',
    'Detecting drift patterns...',
    'Mapping module topology...',
    'Evaluating dependencies...',
  ],
  gardener: [
    'Preparing the garden...',
    'Gathering context...',
    'Sensing the forest...',
    'Tending to the growth...',
    'Nurturing ideas...',
  ],
  atelier: [
    'Mixing the palette...',
    'Consulting the muses...',
    'Preparing the canvas...',
    'Gathering inspiration...',
    'Awakening creativity...',
  ],
  coalition: [
    'Assembling the team...',
    'Coordinating specialists...',
    'Forming consensus...',
    'Aligning perspectives...',
    'Building bridges...',
  ],
  park: [
    'Setting the stage...',
    'Preparing the scene...',
    'Summoning characters...',
    'Writing the script...',
    'Dimming the lights...',
  ],
  domain: [
    'Initializing simulation...',
    'Loading scenarios...',
    'Calibrating timers...',
    'Preparing drill...',
    'Setting conditions...',
  ],
};
```

### Action-Specific Loading

```typescript
const ACTION_LOADING = {
  save: 'Saving your changes...',
  search: 'Searching...',
  analyze: 'Analyzing...',
  create: 'Creating...',
  delete: 'Removing...',
  connect: 'Connecting...',
  sync: 'Syncing...',
};
```

---

## Part V: Empty States

Empty states are **invitations**, not voids.

### Empty State Formula

```
[Emoji/Illustration] + [What's empty] + [Why/Opportunity] + [Action]
```

### Empty State Templates

#### No Results
```
🔍 No results found
Nothing matched your search. Try different keywords
or broaden your filters.
[Clear filters]
```

#### First Time / No Content
```
🌱 Nothing here yet
This is where your [content type] will appear.
Ready when you are.
[Create first one]
```

#### Filtered to Empty
```
📭 Nothing matches
Your filters are set pretty narrow. Try adjusting
or clearing some filters.
[Clear all filters]
```

#### Permission-Gated
```
🔐 Access required
You'll need permission to see what's here.
[Request access]
```

---

## Part VI: Success States

Success is **earned celebration**—not gratuitous.

### Success Message Guidelines

- **Be specific** — "Saved to Brain" not just "Done"
- **Confirm the action** — Echo what happened
- **Quick dismissal** — Toast disappears in 3-5 seconds
- **Celebrate proportionally** — Small actions get small celebration

### Success Templates

```
✓ Saved                             (small action)
✓ Memory crystallized              (Brain-specific)
✓ Coalition assembled              (Coalition-specific)
✓ Analysis complete. 47 modules healthy.  (with data)
```

### When to Use Celebrations

| Action Size | Celebration Level |
|-------------|-------------------|
| Toggle/checkbox | None (state shows success) |
| Save/submit | Toast with checkmark |
| Complete milestone | Toast + subtle animation |
| Major achievement | Toast + confetti (rare) |

---

## Part VII: Help Text & Labels

### Label Guidelines

- **Action labels are verbs** — "Save", not "Okay"
- **Field labels are nouns** — "Email", not "Enter your email"
- **Be specific** — "Add to Brain", not "Add"
- **No periods in buttons**

### Help Text Guidelines

- **Brief** — One sentence if possible
- **Useful** — Answer "what does this do?"
- **Not redundant** — Don't repeat the label
- **Use examples** — "e.g., kent@example.com"

### Common Labels

| Generic | kgents-flavored |
|---------|-----------------|
| Submit | Create / Save / Send |
| Cancel | Nevermind / Back |
| Delete | Remove / Forget |
| Loading | [Jewel-specific message] |
| Error | [Empathetic message] |
| Success | Done / Saved / Created |

---

## Part VIII: Conversational UI (K-gent)

K-gent dialogue has the most expressive voice:

### Dialogue Modes

```yaml
Reflect:
  Style: Mirror back, question gently
  Example: "You've said before you prefer APIs that are
           'hard to misuse.' What about this feels uncertain?"

Advise:
  Style: Suggest aligned with preferences
  Example: "Your pattern is to resist feature creep.
           What's the core purpose here?"

Challenge:
  Style: Push back constructively
  Example: "That sounds like it conflicts with your
           'curated' principle. What's driving this?"

Explore:
  Style: Open possibility space
  Example: "Given your interest in composability,
           what else might compose well here?"
```

### K-gent Voice Rules

- **Reference past statements** — "You've said..."
- **Use Kent's vocabulary** — "first principles", "composable", "tasteful"
- **Question, don't prescribe** — "What do you think about...?"
- **Acknowledge uncertainty** — "I'm not sure, but..."

---

## Part IX: Writing Checklist

Before shipping copy, verify:

- [ ] **Warm** — Would a friend say this?
- [ ] **Direct** — Can any words be cut?
- [ ] **Actionable** — Does user know what to do next?
- [ ] **Honest** — Am I claiming certainty I don't have?
- [ ] **Consistent** — Does this match the jewel's personality?
- [ ] **Accessible** — No jargon without explanation?

---

## Part X: Vocabulary Guide

### Preferred Terms

| Instead of | Use |
|------------|-----|
| User | Person, you |
| Data | Information, memory |
| Error | Issue, problem |
| Failed | Didn't work, something went wrong |
| Invalid | Needs fixing, not quite right |
| Timeout | Taking too long |
| Loading | [Jewel-specific], working on it |
| Null/empty | Nothing here, none yet |
| Delete | Remove, forget |

### kgents Vocabulary

| Term | Meaning | Usage |
|------|---------|-------|
| **Crystal** | Memory unit | "Crystallize this memory" |
| **Garden** | Workspace/project | "The garden is growing" |
| **Jewel** | Major feature area | "The Brain jewel" |
| **Manifest** | Render/show | "Manifest this path" |
| **Witness** | View history | "Witness what happened" |
| **Void** | Entropy/unknown | "Draw from the void" |
| **Umwelt** | Observer context | (technical, avoid in UI) |

---

## Sources

- `impl/claude/web/src/components/joy/PersonalityLoading.tsx` — Loading state implementation
- `impl/claude/web/src/components/joy/EmpathyError.tsx` — Error state implementation
- `spec/k-gent/persona.md` — K-gent dialogue modes

---

*"Words are the first interface. Choose them as carefully as pixels."*
