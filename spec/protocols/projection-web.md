# Web Projection Protocol

> *"AGENTESE paths become URLs; Contracts become Forms."*
>
> *"The route is a lie. There is only the AGENTESE path and its projection."*
>
> *"A form is a conversation projected through structure."*

**Status:** Canonical Specification
**Date:** 2025-12-24
**Consolidated from:** agentese-as-route.md (571 lines), aspect-form-projection.md (497 lines)
**Prerequisites:** `projection.md`, `agentese.md`, `umwelt.md`, `concept-home.md`
**Aligned With:** AD-008 (Simplifying Isomorphisms), AD-009 (Metaphysical Fullstack), AD-010 (Habitat Guarantee), AD-011 (Registry as Truth), AD-012 (Aspect Projection Protocol)

---

## Part I: Purpose

### 1.1 The Unified Insight

Web applications traditionally have three disconnected systems:

1. **API Routes**: `POST /api/town/citizen { id: "kent_001" }`
2. **UI Routes**: `GET /town/citizens/kent_001`
3. **Forms**: Generic schema-to-widget mapping

This protocol unifies them:

```
URL Projection:   /world.town.citizen.kent_001 → logos.invoke("world.town.citizen.kent_001", browser)
Form Projection:  Contract(CreateTownRequest) → Interactive form for browser observer
Navigation:       NavigationTree reads AGENTESE paths directly, no route mapping
```

**The URL IS the thought. The Form IS the conversation.**

### 1.2 Voice Anchors

This protocol embodies Kent's core principles:

| Principle | Application |
|-----------|-------------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Breaks web conventions but is simpler, not more complex |
| *"The Mirror Test"* | Unification that makes you say "why didn't we always do this?" |
| *"Depth over breadth"* | Eliminates routing and form libs as concepts |
| *"Tasteful > feature-complete"* | One grammar replaces three |

---

## Part II: URL Projection

### 2.1 URL Grammar

```
/{context}.{entity}.{sub}...[:aspect][?params]
```

| Component | Required | Examples |
|-----------|----------|----------|
| `context` | Yes | `world`, `self`, `concept`, `void`, `time` |
| `entity` | Yes | `town`, `memory`, `gardener`, `differance` |
| `sub` | Optional | `citizen`, `crystal`, `session` |
| `aspect` | Optional | `:manifest`, `:polynomial`, `:create` |
| `params` | Optional | `?limit=20`, `?member=kent_001` |

### 2.2 Examples

```
# Crown Jewel entry points
/self.memory                        → Brain overview (manifest aspect)
/world.town                         → Town overview
/time.differance                    → Différance timeline

# Entity views
/world.town.citizen.kent_001        → Kent's citizen profile
/self.memory.crystal.abc123         → Memory crystal detail

# Aspect variations
/world.town.citizen.kent_001:polynomial  → Kent's polynomial state
/self.memory.crystal.abc123:heritage     → Crystal's ghost heritage

# Mutation aspects (show forms)
/world.town:create                  → Form to create new town
/world.town.citizen:dialogue        → Dialogue with citizen

# Parameterized queries
/time.differance.recent?limit=50    → Last 50 traces
/world.town.coalition?member=kent   → Coalitions containing Kent
```

### 2.3 Formal Grammar (EBNF)

```ebnf
url        = "/" path [":" aspect] ["?" params]
path       = context "." segments
context    = "world" | "self" | "concept" | "void" | "time"
segments   = segment ("." segment)*
segment    = identifier | entity_id
identifier = [a-z][a-z0-9_]*
entity_id  = identifier "_" [a-z0-9]+
aspect     = identifier
params     = param ("&" param)*
param      = key "=" value
```

### 2.4 Reserved Prefixes

```
/_/       → System routes (login, settings, account)
/_shell/  → Shell UI components (observer, terminal, nav)
/_api/    → Raw JSON API for non-browser clients
```

### 2.5 Composition in URLs

Piped paths work in URLs:

```
/world.doc.manifest>>concept.summary.refine
→ Fetch document, summarize, render summary
```

---

## Part III: Universal URL Handler

### 3.1 The Handler

All non-reserved URLs are handled by `UniversalProjection`:

```tsx
<Routes>
  <Route path="/_/*" element={<SystemRoutes />} />
  <Route path="/*" element={<UniversalProjection />} />
</Routes>
```

### 3.2 Projection Flow

```
URL Entered
    │
    ▼
┌─────────────────────────────────────┐
│  parseAgentesePath(url)             │
│  → { path, aspect, params }         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  useAgentese(path, aspect, params)  │
│  → { data, isLoading, error }       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  resolveProjection(responseType)    │
│  → ProjectionComponent              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  <ProjectionComponent               │
│    context={path, aspect, data}     │
│  />                                 │
└─────────────────────────────────────┘
```

### 3.3 Projection Resolution

Resolution follows priority order:

1. **Exact response type** (from `@node(contracts={})`)
   - `CitizenManifest` → `CitizenProjection`
   - `MemoryCrystal` → `CrystalProjection`

2. **Path pattern match** (most specific first)
   - `world.town.citizen.*` → `CitizenProjection`
   - `world.town.*` → `TownProjection`

3. **Mutation aspect** (has Contract with request type)
   - Shows AspectForm instead of data view

4. **Generic fallback**
   - `GenericProjection` (renders JSON with teaching callouts)

### 3.4 Projection Component Interface

```typescript
interface ProjectionContext {
  path: string;
  aspect: string;
  params: Record<string, string>;
  response: unknown;
  responseType: string;
}

interface ProjectionProps {
  context: ProjectionContext;
}

// Example implementation
function CitizenProjection({ context }: ProjectionProps) {
  const citizen = context.response as Citizen;
  const { density } = useShell();

  return (
    <div>
      <CitizenCard citizen={citizen} density={density} />
    </div>
  );
}
```

---

## Part IV: Form Projection

### 4.1 The Form Bifunctor

Forms are not UI widgets. They are **projections of Contracts through Observers**:

```
FormProjector : Aspect × Observer → Form
              (Contract, Umwelt) ↦ (Fields, Defaults, Validation, Submit)
```

This is a **bifunctor**—it varies in both arguments:

| Fix | Vary | Result |
|-----|------|--------|
| Observer | Contract | Different fields for different aspects |
| Contract | Observer | Different experience for different archetypes |

### 4.2 The Form Triangle

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

### 4.3 Observer-Dependent Forms

Different archetypes experience genuinely different form projections:

| Archetype | Default Strategy | Field Visibility | Validation Tone | Auto-Actions |
|-----------|------------------|------------------|-----------------|--------------|
| `guest` | Conservative (schema only) | Hide advanced | Gentle, encouraging | None |
| `developer` | Generous (auto-gen UUIDs) | Show all + raw JSON toggle | Precise, technical | Auto-generate IDs |
| `creator` | Creative (void.* entropy) | Hide technical | Warm, inspiring | Suggest creative names |
| `admin` | Full (show metadata) | All + internal fields | Direct | Bulk operations |

**Not Permissions—Perception**: All archetypes may have the same capabilities. What differs is the *affordance*.

### 4.4 Validation Tone

Errors adapt to the observer:

| Field Error | Guest | Developer | Creator |
|-------------|-------|-----------|---------|
| Required | "This field needs a value" | "Required: `name`" | "Every creation needs a name—what shall we call it?" |
| Invalid UUID | "That doesn't look quite right" | "Invalid UUID format: expected xxxxxxxx-xxxx-..." | "IDs are like fingerprints—unique and precise. Let me generate one for you." |
| Too long | "Please shorten this a bit" | `maxLength: 100, got: 150` | "That's wonderful, but we need to trim it a little" |

---

## Part V: The Five Default Sources

### 5.1 AGENTESE Contexts as Default Providers

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

### 5.2 Default Resolution Order

For each field, defaults resolve in priority order:

1. **world.***: If editing an entity, use the entity's current value
2. **self.***: User's last-used value for this field type (preference learning)
3. **concept.***: Schema default or example value
4. **void.***: For `creator` archetype, draw from entropy for creative suggestions
5. **time.***: Temporal defaults (today's date, session start, etc.)

### 5.3 The Entropy Default

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

---

## Part VI: Field Projection Registry

### 6.1 Fields as Projection Targets

The Form Protocol maps **field descriptors to field components**:

```
FieldProjector : FieldDescriptor → FieldComponent

Where FieldProjector has:
- name: string (identifier)
- fidelity: float (0.0-1.0, higher = more information preserved)
- matches: (field) → boolean (selector)
- component: React.ComponentType (renderer)
```

### 6.2 Built-In Field Projectors

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

### 6.3 AGENTESE-Specific Projectors

| Projector | Fidelity | Matches | Purpose |
|-----------|----------|---------|---------|
| `agentese-path` | 0.95 | `name === 'path'` | Path picker with autocomplete |
| `observer-archetype` | 0.95 | `name === 'archetype'` | Visual archetype selector |
| `aspect-picker` | 0.95 | `name === 'aspect'` | Dropdown from path's aspects |

### 6.4 Fidelity and Fallback

Higher fidelity projectors are tried first. The `json` projector (fidelity 1.0) is **lossless but not user-friendly**—it's the universal fallback that preserves all information at the cost of usability.

A slider is a lossy projection of a number—it loses precision but gains affordance.

---

## Part VII: Contract-Driven Projections

### 7.1 Source of Truth

The `@node(contracts={})` decorator is the authority for:
- API response types (JSON Schema)
- Projection component selection
- Form field schemas

```python
@node(
    "world.town.citizen",
    description="Town citizen",
    contracts={
        "manifest": Response(CitizenManifest),
        "polynomial": Response(CitizenPolynomial),
        "dialogue": Contract(DialogueRequest, DialogueResponse),
        "create": Contract(CreateCitizenRequest, CreateCitizenResponse),
    }
)
@dataclass
class CitizenNode(BaseLogosNode):
    ...
```

### 7.2 Type Synchronization

Build-time sync generates TypeScript types:

```bash
npm run sync-types
# Fetches /agentese/discover?include_schemas=true
# Generates types in web/src/_generated/contracts/
```

### 7.3 Projection Registration

Projections are registered by response type:

```typescript
// shell/projections/registry.ts
const PROJECTIONS = new Map<string, ProjectionComponent>([
  // Response type → Component (auto-discoverable)
  ['CitizenManifest', CitizenProjection],
  ['CitizenPolynomial', CitizenPolynomialProjection],
  ['MemoryCrystal', CrystalProjection],

  // Path pattern → Component (fallback)
  ['world.town.*', TownProjection],
  ['self.memory.*', BrainProjection],
]);
```

---

## Part VIII: Navigation

### 8.1 NavigationTree Simplification

The NavigationTree becomes a pure AGENTESE browser:

```tsx
function NavigationTree() {
  const { paths } = useDiscovery();

  // NO routeToPath or pathToRoute mappings.
  // The path IS the route.

  return (
    <nav>
      {paths.map(path => (
        <AgentLink path={path}>
          {formatPathLabel(path)}
        </AgentLink>
      ))}
    </nav>
  );
}
```

### 8.2 AgentLink Component

```tsx
interface AgentLinkProps {
  path: string;
  aspect?: string;
  params?: Record<string, string>;
  children: React.ReactNode;
}

function AgentLink({ path, aspect, params, children }: AgentLinkProps) {
  const url = formatAgentesePath(path, aspect, params);

  // Prefetch for instant navigation
  usePrefetch(path, aspect);

  return <Link to={url}>{children}</Link>;
}
```

### 8.3 URL Formatting

```typescript
function formatAgentesePath(
  path: string,
  aspect?: string,
  params?: Record<string, string>
): string {
  let url = `/${path}`;
  if (aspect && aspect !== 'manifest') {
    url += `:${aspect}`;
  }
  if (params && Object.keys(params).length > 0) {
    url += '?' + new URLSearchParams(params).toString();
  }
  return url;
}
```

---

## Part IX: Observer Context

### 9.1 Browser as Observer

The browser is an AGENTESE observer with its own Umwelt:

```typescript
const browserUmwelt: Observer = {
  observer_id: `browser_${sessionId}`,
  archetype: 'browser',
  capabilities: frozenset(['visual', 'interactive', 'prefetch']),
  preferences: {
    density: shell.density,
    teachingMode: teachingEnabled,
    motionPreferences: prefersReducedMotion,
  },
};
```

### 9.2 Observer-Dependent Projections

Different observers get different projections of the same path:

```
/world.house.manifest
  + architect_observer → Blueprint view
  + browser_observer   → Visual card
  + cli_observer       → Table output
  + json_observer      → Raw JSON
```

This is handled at the AGENTESE layer, not the projection layer.

---

## Part X: Write Operations

### 10.1 Method Mapping

| HTTP Method | AGENTESE Semantics |
|-------------|-------------------|
| `GET` | Perception aspects (manifest, list, witness) |
| `POST` | Mutation aspects (capture, create, dialogue) |
| `PUT` | Update aspects (update, renovate) |
| `DELETE` | Removal aspects (delete, prune) |

### 10.2 Mutation Hooks

```tsx
// Read
const { data } = useAgentese('/world.town.citizen.kent_001');

// Write
const { mutate } = useAgenteseMutation('/world.town.citizen.kent_001:dialogue');

// Stream
const events = useAgentseStream('/world.town.simulation.sim_001:stream');
```

### 10.3 Form Submission

Forms invoke AGENTESE directly—no backend routes:

```tsx
function AspectForm({ path, aspect, contract }: AspectFormProps) {
  const { mutate } = useAgenteseMutation(`${path}:${aspect}`);
  const { observer } = useObserver();

  const handleSubmit = (values: unknown) => {
    mutate({ observer, values });
  };

  return <Form onSubmit={handleSubmit} contract={contract} observer={observer} />;
}
```

---

## Part XI: Error Handling

### 11.1 Error Projection

```tsx
function ProjectionError({ path, error }: ErrorProps) {
  return (
    <div className="bg-surface-error rounded-lg p-6">
      <h1>Path Not Found</h1>
      <code>{path}</code>
      <p>{error.message}</p>

      {/* Recovery suggestions */}
      <div>
        <h2>Did you mean?</h2>
        <SimilarPaths path={path} />
      </div>

      <AgentLink path="world.town">
        Return to Town
      </AgentLink>
    </div>
  );
}
```

### 11.2 404 vs Refusal

| HTTP Code | Meaning |
|-----------|---------|
| `404` | Path not registered in AGENTESE |
| `403` | Path exists but observer lacks capability |
| `451` | Path exists but refused (consent required) |

---

## Part XII: Voice and Copy

### 12.1 Labels as Questions

Forms are conversations. Labels are questions, not nouns:

| Generic | Kent's Voice |
|---------|-------------|
| "Name (required)" | "What shall we call it? *" |
| "Submit" | "Invoke" |
| "Reset" | "Start fresh" |
| "Loading..." | "Working..." |
| "Error: invalid input" | "That doesn't look quite right" |
| "Success" | "Done" |

### 12.2 Error Messages

Errors should feel helpful, not bureaucratic:

| Context | Message |
|---------|---------|
| Required field | "This field needs a value" |
| Name required | "Every creation needs a name" |
| Invalid UUID | "IDs are like fingerprints—unique and precise. Let me generate one for you." |
| Too long | Natural language: "Needs to be at least 10" |

### 12.3 Teaching Hints

When Teaching Mode is enabled:

| Field Type | Teaching Hint |
|------------|---------------|
| UUID | "UUIDs are globally unique identifiers. Click 'Generate' to create one." |
| Enum | "These are the allowed values defined in the contract." |
| Required | "Fields marked with * must be filled before invoking." |
| Optional | "Optional fields have sensible defaults—you can skip them." |

---

## Part XIII: Laws

### 13.1 URL Projection Laws

```
Law 1 (Preservation):
  formatAgentesePath(parseAgentesePath(url)) = url

Law 2 (Invocation):
  Navigate to /{path}[:{aspect}]
  ⟺ logos.invoke("{path}", browser, aspect=aspect)

Law 3 (Composition):
  URL /{path1}>>/{path2} invokes:
    result1 = logos.invoke(path1, browser)
    result2 = logos.invoke(path2, browser, input=result1)
```

### 13.2 Form Bifunctor Laws

```
Law 1 (Naturality):
  For all Contract morphisms f : C₁ → C₂ and Observer morphisms g : O₁ → O₂:
  FormProjector(f, id) ∘ FormProjector(id, g) = FormProjector(f, g)

Law 2 (Identity):
  FormProjector(id_C, id_O) = id_Form

Law 3 (Composition):
  FormProjector(f₂ ∘ f₁, g₂ ∘ g₁) = FormProjector(f₂, g₂) ∘ FormProjector(f₁, g₁)
```

### 13.3 Habitat Guarantee Extension

The Habitat Guarantee states every path projects into a meaningful experience. Forms extend this:

| Aspect Has | Form Experience |
|------------|-----------------|
| `Contract(Req, Resp)` | Full form with intelligent defaults |
| `Response(Resp)` only | "No input required" message + Invoke button |
| No contract | JSON textarea (graceful degradation) + teaching hint |

No aspect is un-invocable. Every aspect has a form experience, even if minimal.

---

## Part XIV: Synergies

### 14.1 Différance Integration

Every navigation creates a trace:

```typescript
// Navigation to /world.town.citizen.kent_001
DifferanceIntegration("navigation").trace({
  operation: "navigate",
  path: "world.town.citizen.kent_001",
  alternatives: [
    { path: "world.town.citizen.jane_002", reason: "Listed next" },
    { path: "world.town.manifest", reason: "Parent view" },
  ],
});
```

### 14.2 Teaching Mode

Projections show explanatory callouts when enabled:

```tsx
{teachingEnabled && (
  <TeachingCallout category="conceptual">
    This view is a projection of the AGENTESE path{' '}
    <code>{context.path}</code>. The polynomial state
    determines available affordances.
  </TeachingCallout>
)}
```

### 14.3 Elastic UI

Projections adapt to density:

```tsx
const { density } = useShell();

return density === 'compact'
  ? <CompactProjection {...props} />
  : <FullProjection {...props} />;
```

---

## Part XV: Anti-Patterns

### What This Is NOT

| Anti-Pattern | Why Wrong | Correct Pattern |
|--------------|-----------|-----------------|
| **UISchema system** | Separates presentation from schema | Observer umwelt IS the presentation |
| **react-jsonschema-form** | Renders arbitrary JSON Schema | We render AGENTESE Contracts |
| **Form-as-page** | Forms are destinations | Forms are aspect projections |
| **Static defaults** | Schema defaults only | Five sources including entropy |
| **Client-only validation** | Security theater | Client = UX, server = truth |
| **Server-controlled UI** | Violates observer-dependence | Server provides Contract, client projects |
| **Explicit route mapping** | Manual duplication | Path IS the route |
| **Separate API/UI routes** | Two grammars for same data | URL IS the invocation |

---

## Part XVI: Migration Strategy

### 16.1 Phase 1: Dual Mode

Both schemes work:

```tsx
<Routes>
  {/* Legacy redirects */}
  <Route path="/brain" element={<Navigate to="/self.memory" />} />
  <Route path="/town" element={<Navigate to="/world.town" />} />

  {/* Universal projection */}
  <Route path="/*" element={<UniversalProjection />} />
</Routes>
```

### 16.2 Phase 2: Deprecation

```tsx
function LegacyRedirect({ from, to }) {
  useEffect(() => {
    console.warn(`[Deprecated] ${from} → ${to}`);
  }, []);
  return <Navigate to={to} replace />;
}
```

### 16.3 Phase 3: Removal

Remove legacy routes. All navigation is AGENTESE.

---

## Appendix A: Implementation Files

### A.1 URL Projection

| File | Purpose |
|------|---------|
| `shell/projections/UniversalProjection.tsx` | Main handler |
| `shell/projections/registry.ts` | Type → Component mapping |
| `shell/projections/DynamicProjection.tsx` | Resolution logic |
| `shell/projections/GenericProjection.tsx` | JSON fallback |
| `shell/projections/ProjectionLoading.tsx` | Loading state |
| `shell/projections/ProjectionError.tsx` | Error state |
| `hooks/useAgentese.ts` | Path invocation |
| `hooks/useAgenteseMutation.ts` | Write operations |
| `hooks/useAgentseStream.ts` | SSE streams |
| `utils/parseAgentesePath.ts` | URL parsing |
| `components/AgentLink.tsx` | Navigation helper |

### A.2 Form Projection

| File | Purpose |
|------|---------|
| `lib/form/FieldProjectionRegistry.ts` | Field Registry |
| `lib/schema/analyzeContract.ts` | Schema Analysis |
| `lib/schema/generateDefaults.ts` | Default Generation |
| `components/forms/AspectForm.tsx` | Form Component |
| `components/forms/ProjectedField.tsx` | Field Dispatch |

---

## Appendix B: Path Mappings (Migration Reference)

| Legacy Route | AGENTESE Path |
|--------------|---------------|
| `/brain` | `/self.memory` |
| `/town` | `/world.town` |
| `/town/citizens` | `/world.town.citizen` |
| `/town/citizens/:id` | `/world.town.citizen.{id}` |
| `/differance` | `/time.differance` |

---

## Appendix C: Decision Log

| Decision | Alternatives | Rationale |
|----------|--------------|-----------|
| `.` separator in URLs | `/` separator | Matches AGENTESE grammar; avoids ambiguity |
| Aspect via `:` | Aspect via query param | Cleaner URLs; aspect is semantic, not a param |
| Universal catch-all | Explicit route per path | Single source of truth; eliminates mapping |
| Contract-driven | Manual registration | Type sync; no duplication |
| Observer in header | Observer in cookie | Stateless; debuggable |
| Bifunctor forms | Simple functor | Observer shapes experience, not just data |
| Five default sources | Schema only | Intelligent hospitality; contextual defaults |

---

*"The more fully defined, the more fully projected. AGENTESE paths become URLs. Contracts become Forms. The observer shapes the conversation as much as the schema. And intelligent defaults are an act of hospitality—welcoming the user into a world that anticipated their arrival."*

— AD-009 (Metaphysical Fullstack), AD-012 (Aspect Projection Protocol)

*Last updated: 2025-12-24*
