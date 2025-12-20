# AGENTESE Aspect Form Projection

> *"A form is a conversation projected through structure."*
>
> *"Intelligent defaults are an act of hospitality."*
>
> *"The observer shapes the form as much as the schema."*

**Status**: 🌿 IMPLEMENTING (Spec Complete, Implementation Ready)
**Spec**: `spec/protocols/aspect-form-projection.md` ✅
**Skill**: `docs/skills/aspect-form-projection.md` ✅
**Supersedes**: `plans/umwelt-v2-expansion.md` (✅ Phase 1 Complete)
**Last Updated**: 2025-12-19
**Priority**: P0 (Core UX, AD-012 Layer 4)

---

## Continuation Prompt

```
Implement the Aspect Form Projection Protocol for kgents.

CONTEXT:
- Spec complete: spec/protocols/aspect-form-projection.md
- Skill guide: docs/skills/aspect-form-projection.md
- This plan: plans/agentese-dynamic-forms.md (implementation details below)

CORE INSIGHT:
Forms are bifunctors: FormProjector(Contract, Observer) → Form
The same schema yields different forms for different observers—not permissions, but perception.

START WITH Phase 0 (Foundation):
1. Create web/src/lib/form/FieldProjectionRegistry.ts
2. Create web/src/lib/schema/analyzeContract.ts
3. Create web/src/lib/schema/generateDefaults.ts
4. Write unit tests

KEY PATTERNS:
- Field Projection Registry with fidelity ordering (spec §IV)
- Five Default Sources: world/self/concept/void/time (spec §III)
- Archetype-aware validation tone (spec §II.3)
- Direct AGENTESE invocation on submit (spec §V.1)

VOICE ANCHORS:
- Labels as questions: "What shall we call it?" not "Name (required)"
- Submit button: "Invoke" not "Submit"
- Errors: "That doesn't look quite right" not "Invalid input"

Read the spec first. It's generative—implementation follows mechanically.
```

---

## What's Done

| Artifact | Status | Location |
|----------|--------|----------|
| Canonical Spec | ✅ Complete | `spec/protocols/aspect-form-projection.md` |
| Implementation Skill | ✅ Complete | `docs/skills/aspect-form-projection.md` |
| Protocol README Update | ✅ Complete | `spec/protocols/README.md` |

---

## What's Next: Implementation Phases

### Phase 0: Foundation (2-3 sessions) ← START HERE

**Goal**: Core infrastructure without UI

- [ ] `web/src/lib/form/FieldProjectionRegistry.ts` — Field projector registry
- [ ] `web/src/lib/schema/analyzeContract.ts` — Contract → FieldDescriptor
- [ ] `web/src/lib/schema/generateDefaults.ts` — Five-source default generation
- [ ] Unit tests for all above

**Exit Criteria**:
- `analyzeSchema()` handles dataclass-derived JSON Schema
- `generateDefaults()` uses all five sources
- Registry resolves appropriate projectors

**Key Implementation Notes**:
```typescript
// FieldProjectionRegistry pattern (from skill)
interface FieldProjector {
  name: string;
  fidelity: number;  // 0.0-1.0, higher = more specific
  matches: (field: FieldDescriptor) => boolean;
  component: React.ComponentType<FieldProps>;
}

// Fidelity ordering: uuid(0.95) > slider(0.9) > enum(0.9) > text(0.75) > json(1.0 fallback)
```

### Phase 1: Core Components (3-4 sessions)

**Goal**: AspectForm renders and submits

- [ ] `web/src/components/forms/AspectForm.tsx` — Main orchestrator
- [ ] `web/src/components/forms/ProjectedField.tsx` — Field dispatcher
- [ ] `web/src/components/forms/FieldWrapper.tsx` — Label, description, error
- [ ] Primitive field components (TextInput, NumberInput, Select, Toggle, etc.)
- [ ] Integration with AspectPanel

**Exit Criteria**:
- AspectPanel renders AspectForm for contracted aspects
- Submission invokes AGENTESE directly (`logos.invoke()`)
- Validation errors appear inline with appropriate tone

### Phase 2: Observer Integration (2-3 sessions)

**Goal**: Forms adapt to observer

- [ ] Archetype-aware field filtering
- [ ] Archetype-aware default generation (including void.* entropy)
- [ ] Archetype-aware validation tone
- [ ] Teaching mode integration

**Exit Criteria**:
- Guest sees simplified form
- Developer sees all fields + raw JSON toggle
- Creator gets entropy-sourced creative defaults

### Phase 3: Pilots & Polish (2-3 sessions)

**Goal**: Showcase in Gallery

- [ ] Town Creation Wizard (multi-step operad)
- [ ] Aspect Playground (split view)
- [ ] Citizen Profile Editor
- [ ] Gallery page integration

**Exit Criteria**:
- Three working pilots in Gallery
- Each demonstrates different patterns

---

## Quick Reference

### The Form Triangle

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

### The Five Default Sources

```
1. world.*   — Entity context (editing? use current value)
2. self.*    — User history (last used values)
3. concept.* — Schema defaults
4. void.*    — Entropy (creator archetype gets whimsical suggestions)
5. time.*    — Temporal (today's date, session start)
```

### Archetype Behaviors

| Archetype | Default Strategy | Field Visibility | Validation Tone |
|-----------|------------------|------------------|-----------------|
| `guest` | Conservative | Hide advanced | Gentle |
| `developer` | Generous (auto-gen UUIDs) | Show all + JSON toggle | Technical |
| `creator` | Creative (void.* entropy) | Hide technical | Warm, inspiring |
| `admin` | Full | All + internal | Direct |

### Built-in Field Projectors (by fidelity)

| Projector | Fidelity | Matches |
|-----------|----------|---------|
| `uuid` | 0.95 | `format === 'uuid'` |
| `agentese-path` | 0.95 | `name === 'path'` |
| `slider` | 0.90 | `type === 'number' && min && max` |
| `enum` | 0.90 | `enum !== null` |
| `date` | 0.85 | `format === 'date'` |
| `boolean` | 0.85 | `type === 'boolean'` |
| `textarea` | 0.80 | `maxLength > 200` |
| `text` | 0.75 | `type === 'string'` |
| `number` | 0.75 | `type === 'number'` |
| `json` | 1.00 | Always (fallback) |

---

## Anti-Patterns (What This Is NOT)

1. **NOT UISchema** — Observer umwelt IS the UI schema
2. **NOT react-jsonschema-form** — We render AGENTESE Contracts
3. **NOT form-as-page** — Forms render WITHIN aspects
4. **NOT static defaults** — Five sources including entropy
5. **NOT client-only validation** — Server validates via AGENTESE

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `spec/protocols/aspect-form-projection.md` | Canonical specification |
| `docs/skills/aspect-form-projection.md` | Implementation patterns |
| `spec/protocols/projection.md` | Projection Protocol (fidelity, Galois connection) |
| `spec/protocols/agentese.md` | Contract Protocol (Appendix D) |
| `docs/skills/elastic-ui-patterns.md` | Density adaptation |

---

*Updated: 2025-12-19*
*Status: Spec complete, ready for implementation*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
