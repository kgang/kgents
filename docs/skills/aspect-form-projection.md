---
path: docs/skills/aspect-form-projection
status: active
progress: 100
last_touched: 2025-12-19
touched_by: claude-opus-4
blocking: []
enables: [umwelt-v2, dynamic-forms]
session_notes: |
  Companion skill for spec/protocols/projection-web.md (Part IV: Form Projection).
  Provides implementation patterns for the Form Bifunctor.
phase_ledger:
  PLAN: complete
  IMPLEMENT: pending
---

# Skill: Aspect Form Projection

> *"Forms are projections, not pages. The observer shapes the form as much as the schema."*

**Difficulty**: Intermediate
**Prerequisites**: `agentese-node-registration.md`, `projection-target.md`
**Spec**: `spec/protocols/projection-web.md` (Part IV: Form Projection)

---

## Overview

This skill teaches how to implement observer-dependent forms that derive from AGENTESE Contracts. The core insight: **Forms are bifunctors** that vary in both Contract (what fields exist) and Observer (how fields are presented).

---

## The Form Triangle

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

Contract defines WHAT fields. Observer determines HOW they appear and WHAT values start in them.

---

## Pattern 1: Contract-First Registration

**Problem**: Forms need schema, but we don't want to duplicate type definitions.

**Wrong**: Define schema in frontend
```typescript
// Duplicates Python dataclass, drifts over time
const townSchema = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    region: { type: 'string' },
  }
};
```

**Right**: Derive from @node contracts
```python
# Python: Single source of truth
@dataclass
class CreateTownRequest:
    name: str
    region: str
    population_cap: int = 500

@node(
    "world.town",
    contracts={
        "create": Contract(CreateTownRequest, CreateTownResponse),
    }
)
class TownNode: ...
```

```typescript
// TypeScript: Fetch schema at runtime
const { schema } = useContract(path, aspect);
const fields = analyzeSchema(schema);
```

**Benefits**:
- Single source of truth (Python dataclass)
- No type drift
- Schema changes propagate automatically

---

## Pattern 2: Observer-Aware Field Filtering

**Problem**: Different observers should see different fields.

**Wrong**: Permission-based hiding
```typescript
// Only hides, doesn't adapt
if (observer.capabilities.has('admin')) {
  fields.push(internalField);
}
```

**Right**: Archetype-aware projection
```typescript
function filterForArchetype(
  fields: FieldDescriptor[],
  archetype: string
): FieldDescriptor[] {
  const VISIBILITY = {
    guest: ['name', 'region'],  // Essential only
    developer: '*',              // All fields
    creator: ['name', 'region', 'description'],  // Creative fields
    admin: '*',                  // All fields + metadata
  };

  const allowed = VISIBILITY[archetype];
  if (allowed === '*') return fields;
  return fields.filter(f => allowed.includes(f.name));
}
```

**Benefits**:
- Observer shapes perception, not just access
- Different archetypes have genuinely different experiences
- Graceful degradation (guest sees simpler form)

---

## Pattern 3: Five-Source Default Resolution

**Problem**: Defaults should be intelligent, not static.

**Wrong**: Schema-only defaults
```typescript
const defaults = fields.reduce((acc, f) => ({
  ...acc,
  [f.name]: f.default ?? null
}), {});
```

**Right**: Five-source cascade
```typescript
async function generateDefaults(
  fields: FieldDescriptor[],
  observer: Observer,
  context: { path: string; aspect: string; entity?: unknown }
): Promise<Record<string, unknown>> {
  const defaults: Record<string, unknown> = {};

  for (const field of fields) {
    defaults[field.name] =
      // 1. world.* — If editing, use entity value
      context.entity?.[field.name] ??
      // 2. self.* — User's last used value
      await getFromHistory(observer, field) ??
      // 3. concept.* — Schema default
      field.default ?? field.placeholder ??
      // 4. void.* — Creative entropy (creator archetype)
      (observer.archetype === 'creator' ? await sipEntropy(field) : null) ??
      // 5. time.* — Temporal defaults
      getTemporalDefault(field);
  }

  return defaults;
}

// Example void.* entropy for names
async function sipEntropy(field: FieldDescriptor): Promise<unknown> {
  if (field.name === 'name' && field.context?.includes('citizen')) {
    return await logos.invoke('void.entropy.sip', null, {
      context: 'citizen_name',
      style: 'whimsical'
    });
    // → "Zephyr Chen" not "John Doe"
  }
  return null;
}
```

**Benefits**:
- Intelligent hospitality (anticipate user needs)
- Context-aware (editing pre-fills, creating suggests)
- Entropy for creativity (creator archetype gets suggestions)

---

## Pattern 4: Validation Tone Adaptation

**Problem**: Errors should match observer's expectations.

**Wrong**: One-size-fits-all errors
```typescript
// Cold, technical error
throw new Error(`Required: ${field.name}`);
```

**Right**: Archetype-aware tone
```typescript
const VALIDATION_TONES = {
  guest: {
    required: (e) => `This field needs a value`,
    pattern: (e) => `That doesn't look quite right`,
    range: (e) => `Please adjust this value`,
  },
  developer: {
    required: (e) => `Required: \`${e.field}\``,
    pattern: (e) => `Pattern mismatch: expected ${e.constraint}`,
    range: (e) => `Value ${e.value} outside range [${e.min}, ${e.max}]`,
  },
  creator: {
    required: (e) => `Every creation needs a ${e.field}—what shall we call it?`,
    pattern: (e) => `Let's make sure this fits the shape we need`,
    range: (e) => `That's wonderful, but we need to adjust it a little`,
  },
};

function formatError(error: ValidationError, archetype: string): string {
  const tone = VALIDATION_TONES[archetype] ?? VALIDATION_TONES.guest;
  return tone[error.type]?.(error) ?? error.message;
}
```

**Benefits**:
- Errors feel appropriate to context
- Developer gets precision, guest gets warmth
- Creator gets encouragement

---

## Pattern 5: Field Projection Registry

**Problem**: Different field types need different widgets.

**Wrong**: Giant switch statement
```typescript
switch (field.type) {
  case 'string':
    if (field.format === 'uuid') return <UuidField />;
    if (field.maxLength > 200) return <TextArea />;
    return <TextInput />;
  // ... 50 more cases
}
```

**Right**: Registry with fidelity ordering
```typescript
interface FieldProjector {
  name: string;
  fidelity: number;  // 0.0-1.0
  matches: (field: FieldDescriptor) => boolean;
  component: React.ComponentType<FieldProps>;
}

const FieldProjectionRegistry = {
  projectors: [] as FieldProjector[],

  register(projector: FieldProjector) {
    this.projectors.push(projector);
    this.projectors.sort((a, b) => b.fidelity - a.fidelity);
  },

  resolve(field: FieldDescriptor): FieldProjector {
    return this.projectors.find(p => p.matches(field)) ?? JSON_FALLBACK;
  }
};

// Registration (specific → general)
FieldProjectionRegistry.register({
  name: 'uuid',
  fidelity: 0.95,
  matches: (f) => f.format === 'uuid',
  component: UuidField,
});

FieldProjectionRegistry.register({
  name: 'text',
  fidelity: 0.75,
  matches: (f) => f.type === 'string',
  component: TextInput,  // Fallback for strings
});
```

**Benefits**:
- Extensible (add projectors without touching core code)
- Fidelity ordering (most specific wins)
- Graceful fallback (JSON editor always matches)

---

## Pattern 6: Direct AGENTESE Invocation

**Problem**: Forms submit to endpoints, but we want forms to invoke AGENTESE.

**Wrong**: REST endpoint submission
```typescript
const handleSubmit = async (values) => {
  await fetch('/api/town/create', {
    method: 'POST',
    body: JSON.stringify(values),
  });
};
```

**Right**: Direct AGENTESE invocation
```typescript
const handleSubmit = async (values) => {
  // No /api route—AGENTESE IS the API
  await logos.invoke(`${path}.${aspect}`, observer, values);
};
```

**Benefits**:
- No route proliferation
- AGENTESE handles authorization, validation, tracing
- Consistent with Metaphysical Fullstack (AD-009)

---

## Pattern 7: Habitat-Integrated Forms

**Problem**: Forms should integrate with the Habitat experience.

**Component Structure**:
```
AspectPanel
├── ReferencePanel (left sidebar)
│   ├── Description
│   ├── AspectButtons ← clicking opens form
│   └── Effects
└── PlaygroundArea
    └── AspectForm ← form lives here
        ├── FieldGroup (required)
        ├── Collapsible (optional fields)
        └── FormActions (Reset, Invoke)
```

**Integration**:
```typescript
function AspectPanel({ path, aspect, observer, density }) {
  const { contract } = useContract(path, aspect);

  // No contract? Graceful degradation
  if (!contract?.request) {
    return (
      <NoInputForm
        path={path}
        aspect={aspect}
        observer={observer}
        onInvoke={() => logos.invoke(`${path}.${aspect}`, observer)}
      />
    );
  }

  return (
    <AspectForm
      path={path}
      aspect={aspect}
      observer={observer}
      density={density}
    />
  );
}
```

---

## Schema Caching Strategy

**Memoize by**: `(path, aspect, archetype)`

**DO cache**:
- Schema analysis (fields don't change per-session)
- Field filtering (archetype-specific views)

**DON'T cache**:
- Defaults (include time.* and void.*)
- Validation state (per-interaction)

```typescript
const schemaCache = new Map<string, FieldDescriptor[]>();

function getCacheKey(path: string, aspect: string, archetype: string): string {
  return `${path}:${aspect}:${archetype}`;
}

export function useAspectForm(path: string, aspect: string, observer: Observer) {
  const cacheKey = getCacheKey(path, aspect, observer.archetype);

  // Fields ARE cached (schema + archetype don't change)
  const fields = useMemo(() => {
    if (schemaCache.has(cacheKey)) {
      return schemaCache.get(cacheKey)!;
    }
    const contract = getContract(path, aspect);
    const analyzed = analyzeSchema(contract.request);
    const filtered = filterForArchetype(analyzed, observer.archetype);
    schemaCache.set(cacheKey, filtered);
    return filtered;
  }, [cacheKey]);

  // Defaults are NOT cached (include live sources)
  const defaults = useMemo(() =>
    generateDefaults(fields, observer, { path, aspect }),
    [fields, observer, path, aspect]
  );

  return { fields, defaults };
}
```

---

## Anti-Pattern Checklist

| Anti-Pattern | Why Wrong | Fix |
|--------------|-----------|-----|
| Schema in frontend | Drifts from Python | Use `useContract()` hook |
| Permission-only field hiding | Misses perception difference | Archetype-aware filtering |
| Schema-only defaults | Misses context, history, entropy | Five-source cascade |
| Cold error messages | Doesn't match observer | Tone adaptation |
| Giant switch for widgets | Unmaintainable | Field Projection Registry |
| REST submission | Bypasses AGENTESE | Direct `logos.invoke()` |
| Caching defaults | time.* and void.* are live | Cache schema, not defaults |

---

## Quick Reference

### Add a New Field Projector

```typescript
FieldProjectionRegistry.register({
  name: 'my-custom-field',
  fidelity: 0.9,  // Higher = more specific
  matches: (f) => f.format === 'my-format',
  component: MyCustomField,
});
```

### Add a New Archetype Tone

```typescript
VALIDATION_TONES.my_archetype = {
  required: (e) => `Custom message for ${e.field}`,
  pattern: (e) => `Custom pattern message`,
};
```

### Add a New Default Source

```typescript
// In generateDefaults(), add a new step in the cascade:
defaults[field.name] =
  context.entity?.[field.name] ??
  await getFromHistory(observer, field) ??
  await myNewSource(field) ??  // ← NEW
  field.default ?? ...
```

---

## Connection to Other Skills

| Skill | Relationship |
|-------|--------------|
| `agentese-node-registration.md` | Contracts come from `@node` |
| `projection-target.md` | Forms are projection targets |
| `elastic-ui-patterns.md` | Density affects form layout |
| `crown-jewel-patterns.md` | Teaching Mode integration |

---

*"The form that anticipated your arrival is an act of hospitality. The form that surprises you is an act of creativity. The form that respects your expertise is an act of trust."*
