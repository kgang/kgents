# AGENTESE-as-Route Protocol

**Status:** Canonical Specification
**Date:** 2025-12-18
**Implementation:** `impl/claude/web/src/shell/projections/`

---

## Epigraph

> *"The route is a lie. There is only the AGENTESE path and its projection."*
>
> *"The URL IS the thought. The page IS the answer."*
>
> *"Define a node, get a URL. No glue required."*

---

## Part I: Design Philosophy

### 1.1 The Problem

Web applications have two disconnected systems for referencing data:

1. **API Routes**: `POST /api/town/citizen { id: "kent_001" }`
2. **UI Routes**: `GET /town/citizens/kent_001`

This creates:
- Manual mapping between paths
- Two grammars for the same data
- Routes that don't know about AGENTESE semantics
- URLs that are just human-readable database queries in disguise

### 1.2 The Solution

**The URL IS the AGENTESE invocation.**

```
/world.town.citizen.kent_001        → logos.invoke("world.town.citizen.kent_001", browser)
/self.memory.crystal.abc123:heritage → logos.invoke("self.memory.crystal.abc123", browser, aspect="heritage")
/time.differance.recent?limit=20    → logos.invoke("time.differance.recent", browser, limit=20)
```

A single universal route handler parses the URL, invokes AGENTESE, and projects the response.

### 1.3 Voice Anchors

This protocol embodies Kent's core principles:

| Principle | Application |
|-----------|-------------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Breaks web conventions but is simpler, not more complex |
| *"The Mirror Test"* | Unification that makes you say "why didn't we always do this?" |
| *"Depth over breadth"* | Eliminates routing as a concept rather than building more infrastructure |
| *"Tasteful > feature-complete"* | One grammar replaces two |

---

## Part II: URL Grammar

### 2.1 Basic Structure

```
/{context}.{entity}.{sub}...[:aspect][?params]
```

| Component | Required | Examples |
|-----------|----------|----------|
| `context` | Yes | `world`, `self`, `concept`, `void`, `time` |
| `entity` | Yes | `town`, `memory`, `gardener`, `differance` |
| `sub` | Optional | `citizen`, `crystal`, `session` |
| `aspect` | Optional | `:manifest`, `:polynomial`, `:stream` |
| `params` | Optional | `?limit=20`, `?member=kent_001` |

### 2.2 Examples

```
# Crown Jewel entry points
/self.memory                        → Brain overview
/world.town                         → Town overview
/world.atelier                      → Atelier commission panel
/time.differance                    → Différance timeline

# Entity views
/world.town.citizen.kent_001        → Kent's citizen profile
/self.memory.crystal.abc123         → Memory crystal detail
/world.forge.commission.comm_001    → Commission status

# Aspect variations
/world.town.citizen.kent_001:polynomial  → Kent's polynomial state
/world.town.citizen.kent_001:trace       → Kent's activity trace
/self.memory.crystal.abc123:heritage     → Crystal's ghost heritage

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
/_public/ → Static marketing pages (if ever needed)
```

### 2.5 Composition Syntax

Piped paths work in URLs:

```
/world.doc.manifest>>concept.summary.refine
→ Fetch document, summarize, render summary
```

---

## Part III: Universal Projection

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
   - `self.memory.*` → `BrainProjection`

3. **Generic fallback**
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
  const { enabled: teachingEnabled } = useTeachingModeSafe();

  return (
    <div>
      <CitizenCard citizen={citizen} density={density} />
      {teachingEnabled && (
        <TeachingCallout>
          This citizen's polynomial state determines available affordances.
        </TeachingCallout>
      )}
    </div>
  );
}
```

---

## Part IV: Contract-Driven Projections

### 4.1 Source of Truth

The `@node(contracts={})` decorator is the authority for both:
- API response types (JSON Schema)
- Projection component selection

```python
@node(
    "world.town.citizen",
    description="Town citizen",
    contracts={
        "manifest": Response(CitizenManifest),
        "polynomial": Response(CitizenPolynomial),
        "dialogue": Contract(DialogueRequest, DialogueResponse),
    }
)
@dataclass
class CitizenNode(BaseLogosNode):
    ...
```

### 4.2 Type Synchronization

Build-time sync generates TypeScript types:

```bash
npm run sync-types
# Fetches /agentese/discover?include_schemas=true
# Generates types in web/src/_generated/contracts/
```

### 4.3 Projection Registration

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

## Part V: Observer Context

### 5.1 Browser as Observer

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

### 5.2 Observer-Dependent Projections

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

## Part VI: Navigation

### 6.1 NavigationTree Simplification

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

### 6.2 AgentLink Component

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

### 6.3 URL Formatting

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

## Part VII: Write Operations

### 7.1 Method Mapping

| HTTP Method | AGENTESE Semantics |
|-------------|-------------------|
| `GET` | Perception aspects (manifest, list, witness) |
| `POST` | Mutation aspects (capture, create, dialogue) |
| `PUT` | Update aspects (update, renovate) |
| `DELETE` | Removal aspects (delete, prune) |

### 7.2 Mutation Hooks

```tsx
// Read
const { data } = useAgentese('/world.town.citizen.kent_001');

// Write
const { mutate } = useAgenteseMutation('/world.town.citizen.kent_001:dialogue');

// Stream
const events = useAgentseStream('/world.town.simulation.sim_001:stream');
```

---

## Part VIII: Error Handling

### 8.1 Error Projection

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

### 8.2 404 vs Refusal

| HTTP Code | Meaning |
|-----------|---------|
| `404` | Path not registered in AGENTESE |
| `403` | Path exists but observer lacks capability |
| `451` | Path exists but refused (consent required) |

---

## Part IX: Migration Strategy

### 9.1 Phase 1: Dual Mode

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

### 9.2 Phase 2: Deprecation

```tsx
function LegacyRedirect({ from, to }) {
  useEffect(() => {
    console.warn(`[Deprecated] ${from} → ${to}`);
  }, []);
  return <Navigate to={to} replace />;
}
```

### 9.3 Phase 3: Removal

Remove legacy routes. All navigation is AGENTESE.

---

## Part X: Synergies

### 10.1 Différance Integration

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

### 10.2 Teaching Mode

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

### 10.3 Elastic UI

Projections adapt to density:

```tsx
const { density } = useShell();

return density === 'compact'
  ? <CompactProjection {...props} />
  : <FullProjection {...props} />;
```

---

## Appendix A: Implementation Files

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
| `.` separator | `/` separator | Matches AGENTESE grammar; avoids ambiguity |
| Aspect via `:` | Aspect via query param | Cleaner URLs; aspect is semantic, not a param |
| Universal catch-all | Explicit route per path | Single source of truth; eliminates mapping |
| Contract-driven | Manual registration | Type sync; no duplication |
| Observer in header | Observer in cookie | Stateless; debuggable |

---

*"The more fully defined, the more fully projected."* — AD-009

*Last updated: 2025-12-18*
