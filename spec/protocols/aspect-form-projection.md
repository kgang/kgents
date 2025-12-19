# Aspect Form Projection Protocol

> *"A form is a conversation projected through structure."*
>
> *"Intelligent defaults are an act of hospitality."*
>
> *"The observer shapes the form as much as the schema."*

**Status:** Canonical Specification
**Date:** 2025-12-19
**Prerequisites:** `projection.md`, `agentese.md`, `umwelt.md`, `concept-home.md`
**Aligned With:** AD-008 (Simplifying Isomorphisms), AD-009 (Metaphysical Fullstack), AD-010 (Habitat Guarantee), AD-011 (Registry as Truth), AD-012 (Aspect Projection Protocol)

---

## Prologue: The Fallacy of the Form Library

Traditional form libraries commit a fundamental error: they treat forms as a **widget problem**—a matter of mapping JSON Schema to input components. This produces:

```
Schema → Widgets → User Input → Validation → Submit
```

This approach assumes forms are inert artifacts that exist independently of who is filling them out. It ignores that:

1. **Different observers see different forms** — Not permissions (what you *can* do), but perception (what you *experience*)
2. **Defaults are not static** — They flow from context, history, entropy, and time
3. **Validation has tone** — The same error can be expressed warmly or technically
4. **Submission is invocation** — Forms don't POST to endpoints; they invoke AGENTESE

**The Insight**: Forms are not UI components. They are **projections of Contracts through Observers**.

---

## Part I: The Form Bifunctor

### 1.1 Formal Definition

```
FormProjector : Aspect × Observer → Form
              (Contract, Umwelt) ↦ (Fields, Defaults, Validation, Submit)
```

This is a **bifunctor**—it varies in both arguments:

| Fix | Vary | Result |
|-----|------|--------|
| Observer | Contract | Different fields for different aspects |
| Contract | Observer | Different experience for different archetypes |

### 1.2 The Form Triangle

The Form Triangle visualizes the three-way relationship:

```
                    Contract (from @node)
                         ╱ ╲
                        ╱   ╲
                       ╱     ╲
              Fields  ◄───────► Defaults
                       ╲     ╱
                        ╲   ╱
                         ╲ ╱
                      Observer
```

- **Contract** defines WHAT fields exist (from `@node(contracts={})`)
- **Observer** determines HOW fields are presented and WHAT values they start with
- **Fields** are the visible inputs; **Defaults** are their initial values

### 1.3 Why Bifunctor?

A simple functor would be:

```
FormProjector : Contract → Form  (one form per schema)
```

This misses the AGENTESE insight: *there is no view from nowhere*. The form that a `guest` sees is categorically different from the form that a `developer` sees—not just hidden fields, but different defaults, different validation messages, different interaction patterns.

---

## Part II: Observer-Dependent Form Projection

### 2.1 The Archetype Dimension

Different archetypes experience genuinely different form projections:

| Archetype | Default Strategy | Field Visibility | Validation Tone | Auto-Actions |
|-----------|------------------|------------------|-----------------|--------------|
| `guest` | Conservative (schema only) | Hide advanced | Gentle, encouraging | None |
| `developer` | Generous (auto-gen UUIDs) | Show all + raw JSON toggle | Precise, technical | Auto-generate IDs |
| `creator` | Creative (void.* entropy) | Hide technical | Warm, inspiring | Suggest creative names |
| `admin` | Full (show metadata) | All + internal fields | Direct | Bulk operations |

### 2.2 Not Permissions—Perception

This is not access control. All archetypes may have the same *capabilities*. What differs is the *affordance*:

- **Guest** sees: "What shall we call it?" with an empty text field
- **Developer** sees: "name (required)" with type hint, JSON toggle, and debug info
- **Creator** sees: "What shall we call it?" with a suggested whimsical name from `void.entropy`

Same capability (fill in a name), different *perception* of the form.

### 2.3 Validation Tone

Errors adapt to the observer:

| Field Error | Guest | Developer | Creator |
|-------------|-------|-----------|---------|
| Required | "This field needs a value" | "Required: `name`" | "Every creation needs a name—what shall we call it?" |
| Invalid UUID | "That doesn't look quite right" | "Invalid UUID format: expected xxxxxxxx-xxxx-..." | "IDs are like fingerprints—unique and precise. Let me generate one for you." |
| Too long | "Please shorten this a bit" | `maxLength: 100, got: 150` | "That's wonderful, but we need to trim it a little" |

This is the **Validation Gravitational Field**—errors exert force, but the force has character.

---

## Part III: The Five Default Sources

### 3.1 The AGENTESE Contexts as Default Providers

Defaults don't come from just the schema. They flow from the five AGENTESE contexts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE FIVE DEFAULT SOURCES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. world.*   │ Entity context: editing? pre-populate from entity           │
│  2. self.*    │ User history: last used values, preferences, patterns       │
│  3. concept.* │ Schema: JSON Schema default, examples, constraints          │
│  4. void.*    │ Entropy: creative suggestions, serendipitous names          │
│  5. time.*    │ Temporal: today's date, session duration, deadlines         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Default Resolution Order

For each field, defaults resolve in priority order:

1. **world.***: If editing an entity, use the entity's current value
2. **self.***: User's last-used value for this field type (preference learning)
3. **concept.***: Schema default or example value
4. **void.***: For `creator` archetype, draw from entropy for creative suggestions
5. **time.***: Temporal defaults (today's date, session start, etc.)

### 3.3 The Entropy Default

The **void.*** source is special. It's the Accursed Share applied to form defaults:

```python
# For citizen names in creator mode
await logos.invoke("void.entropy.sip", observer, {
    "context": "citizen_name",
    "style": "whimsical"
})
# → "Zephyr Chen" not "John Doe"
```

This is **intelligent hospitality**—the form anticipates that a creator wants creative suggestions, not generic placeholders.

### 3.4 What We Don't Do

We do NOT:
- Cache defaults that include `void.*` or `time.*` (they're inherently fresh)
- Pre-generate all defaults on form load (lazy evaluation)
- Let server control defaults (observer determines perception)

---

## Part IV: The Field Projection Registry

### 4.1 Fields as Projection Targets

Just as the Projection Protocol maps widgets to targets (CLI, JSON, marimo), the Form Protocol maps **field descriptors to field components**:

```
FieldProjector : FieldDescriptor → FieldComponent

Where FieldProjector has:
- name: string (identifier)
- fidelity: float (0.0-1.0, higher = more information preserved)
- matches: (field) → boolean (selector)
- component: React.ComponentType (renderer)
```

### 4.2 Built-In Field Projectors

| Projector | Fidelity | Matches | Purpose |
|-----------|----------|---------|---------|
| `uuid` | 0.95 | `format === 'uuid'` | UUID with generate button |
| `slider` | 0.90 | `type === 'number' && min && max` | Bounded number |
| `enum` | 0.90 | `enum !== null` | Select from options |
| `date` | 0.85 | `format === 'date'` | Date picker |
| `boolean` | 0.85 | `type === 'boolean'` | Toggle |
| `textarea` | 0.80 | `type === 'string' && maxLength > 200` | Long text |
| `text` | 0.75 | `type === 'string'` | Single-line input |
| `number` | 0.75 | `type === 'number'` | Number input |
| `object` | 0.70 | `type === 'object'` | Recursive field group |
| `array` | 0.70 | `type === 'array'` | Repeatable fields |
| `json` | 1.00 | Always matches | Lossless JSON editor (fallback) |

### 4.3 AGENTESE-Specific Projectors

| Projector | Fidelity | Matches | Purpose |
|-----------|----------|---------|---------|
| `agentese-path` | 0.95 | `name === 'path'` | Path picker with autocomplete |
| `observer-archetype` | 0.95 | `name === 'archetype'` | Visual archetype selector |
| `aspect-picker` | 0.95 | `name === 'aspect'` | Dropdown from path's aspects |

### 4.4 Fidelity and Fallback

Higher fidelity projectors are tried first. The `json` projector (fidelity 1.0) is **lossless but not user-friendly**—it's the universal fallback that preserves all information at the cost of usability.

The Galois connection from `projection.md` applies:

```
compress ⊣ embed

compress(embed(view)) ≤ view  (lossy)
field ≤ embed(compress(field))  (recoverable)
```

A slider is a lossy projection of a number—it loses precision but gains affordance.

---

## Part V: Connection to Existing Protocols

### 5.1 Metaphysical Fullstack Position (AD-009)

Forms live at **Layer 7 (Projection Surface)** in the metaphysical stack:

```
┌─────────────────────────────────────────────────────────────────┐
│  7. FORM PROJECTION    AspectForm renders Contract → widgets    │ ← HERE
├─────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL  form.submit() → logos.invoke()           │
├─────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE      @node(contracts={...})                   │
├─────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE     services/town/ — business logic          │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: There are no backend routes for form submission. Forms invoke AGENTESE directly:

```python
await logos.invoke(f"{path}.{aspect}", observer, values)
```

### 5.2 Habitat Guarantee Extension (AD-010)

The Habitat Guarantee states every path projects into a meaningful experience. Forms extend this:

| Aspect Has | Form Experience |
|------------|-----------------|
| `Contract(Req, Resp)` | Full form with intelligent defaults |
| `Response(Resp)` only | "No input required" message + Invoke button |
| No contract | JSON textarea (graceful degradation) + teaching hint |

No aspect is un-invocable. Every aspect has a form experience, even if minimal.

### 5.3 Registry as Truth (AD-011)

Forms derive from `@node(contracts={})`. The Contract IS the form schema:

```python
@node(
    "world.town",
    contracts={
        "create": Contract(CreateTownRequest, CreateTownResponse),
        "manifest": Response(TownManifest),  # No request needed
    }
)
```

We do NOT:
- Fetch OpenAPI to discover schemas
- Maintain separate form schemas
- Allow frontend to define schema independently

The registry is truth. Forms are projections of that truth.

### 5.4 Aspect Projection Protocol (AD-012)

Forms render WITHIN aspects, not as separate destinations:

- You navigate to `world.town` (a path)
- You see the aspect buttons (`create`, `manifest`)
- You click `create` → Form appears for that aspect
- You submit → `logos.invoke("world.town.create", observer, values)`

Forms are not pages. They are aspect projections.

---

## Part VI: Schema Derivation

### 6.1 Contract-to-FieldDescriptor

Contracts are Python dataclasses. They derive to field descriptors:

```python
@dataclass
class FieldDescriptor:
    name: str
    type: Literal["string", "number", "boolean", "object", "array"]
    required: bool

    # From schema
    default: Any | None
    description: str | None
    format: str | None  # 'uuid', 'email', 'date', 'date-time'

    # Constraints
    min: float | None
    max: float | None
    min_length: int | None
    max_length: int | None
    pattern: str | None
    enum: list[str] | None

    # Nested
    children: list["FieldDescriptor"] | None

    # Context for defaults
    context: list[str]  # Path hints: ['citizen', 'name']
```

### 6.2 Schema Caching

Schema analysis is memoized by `(path, aspect, archetype)`:

- **Path + Aspect**: Which contract
- **Archetype**: Which fields to include (developer sees all, guest sees essential)

Defaults are NOT cached—they include live sources (`void.*`, `time.*`).

---

## Part VII: Anti-Patterns

### What This Is NOT

| Anti-Pattern | Why Wrong | Correct Pattern |
|--------------|-----------|-----------------|
| **UISchema system** | Separates presentation from schema | Observer umwelt IS the presentation |
| **react-jsonschema-form** | Renders arbitrary JSON Schema | We render AGENTESE Contracts |
| **Form-as-page** | Forms are destinations | Forms are aspect projections |
| **Static defaults** | Schema defaults only | Five sources including entropy |
| **Client-only validation** | Security theater | Client = UX, server = truth |
| **Server-controlled UI** | Violates observer-dependence | Server provides Contract, client projects |

### The UISchema Question

Traditional form libraries support `uiSchema`—a separate schema that controls presentation:

```json
{
  "ui:order": ["name", "email", "phone"],
  "name": {"ui:widget": "textarea"},
  "email": {"ui:disabled": true}
}
```

We reject this. The Observer's Umwelt IS the UI schema. There is no separate layer because:

1. **Observer determines perception** — Not a static schema
2. **Simplicity** — One source of truth (Contract + Observer)
3. **AGENTESE alignment** — "No view from nowhere"

---

## Part VIII: Voice and Copy

### 8.1 Labels as Questions

Forms are conversations. Labels are questions, not nouns:

| Generic | Kent's Voice |
|---------|-------------|
| "Name (required)" | "What shall we call it? *" |
| "Submit" | "Invoke" |
| "Reset" | "Start fresh" |
| "Loading..." | "Working..." |
| "Error: invalid input" | "That doesn't look quite right" |
| "Success" | "Done" |

### 8.2 Error Messages

Errors should feel helpful, not bureaucratic:

| Context | Message |
|---------|---------|
| Required field | "This field needs a value" |
| Name required | "Every creation needs a name" |
| Invalid UUID | "IDs are like fingerprints—unique and precise. Let me generate one for you." |
| Too long | `min`/`max` messages use natural language: "Needs to be at least 10" |

### 8.3 Teaching Hints

When Teaching Mode is enabled:

| Field Type | Teaching Hint |
|------------|---------------|
| UUID | "UUIDs are globally unique identifiers. Click 'Generate' to create one." |
| Enum | "These are the allowed values defined in the contract." |
| Required | "Fields marked with * must be filled before invoking." |
| Optional | "Optional fields have sensible defaults—you can skip them." |

---

## Part IX: Success Criteria

### Quantitative

| Metric | Target |
|--------|--------|
| Contract coverage | 80% of mutation aspects have contracts |
| Form generation time | <50ms for any contract |
| Client→server validation mismatch | <5% of submissions |

### Qualitative

- [ ] Invoking `world.town.create` succeeds on first try with defaults
- [ ] Developer can see raw JSON; guest cannot
- [ ] Creator gets creative default names
- [ ] Forms feel like conversations, not bureaucracy
- [ ] Teaching mode explains what's happening

---

## Part X: Connection to Principles

| Principle | How Forms Embody It |
|-----------|---------------------|
| **Tasteful** | No generic "Name" labels—each field is considered |
| **Curated** | Field projectors are intentionally ordered by fidelity |
| **Ethical** | Server validates; client validation is UX, not security |
| **Joy-Inducing** | Intelligent defaults, warm errors, entropy suggestions |
| **Composable** | FormProjector is a bifunctor; composes with Projection Protocol |
| **Heterarchical** | Observer determines experience, not fixed hierarchy |
| **Generative** | Forms derive from Contracts; implementation follows spec |

---

## Appendix A: The Form Functor Laws

### A.1 Naturality

For all Contract morphisms `f : C₁ → C₂` and Observer morphisms `g : O₁ → O₂`:

```
FormProjector(f, id) ∘ FormProjector(id, g) = FormProjector(f, g)
```

Varying Contract then Observer equals varying both together.

### A.2 Identity

```
FormProjector(id_C, id_O) = id_Form
```

No change to Contract or Observer means no change to form.

### A.3 Composition

```
FormProjector(f₂ ∘ f₁, g₂ ∘ g₁) = FormProjector(f₂, g₂) ∘ FormProjector(f₁, g₁)
```

Form projection respects composition in both dimensions.

---

## Appendix B: Implementation Reference

The following files implement this protocol:

| Concern | File |
|---------|------|
| Field Registry | `web/src/lib/form/FieldProjectionRegistry.ts` |
| Schema Analysis | `web/src/lib/schema/analyzeContract.ts` |
| Default Generation | `web/src/lib/schema/generateDefaults.ts` |
| Form Component | `web/src/components/forms/AspectForm.tsx` |
| Field Dispatch | `web/src/components/forms/ProjectedField.tsx` |
| Skill Guide | `docs/skills/aspect-form-projection.md` |

---

*"A form is a conversation projected through structure. The observer shapes the conversation as much as the schema. And intelligent defaults are an act of hospitality—welcoming the user into a world that anticipated their arrival."*

*Last updated: 2025-12-19*
