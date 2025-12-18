# Crown Jewel Frontend API Audit

> **Skill**: Auditing and fixing Crown Jewel frontend API requests
> **Created**: 2025-12-17
> **Phase**: REFLECT

## Context

The AGENTESE Universal Gateway (AD-009) migration has been largely **completed** in `client.ts`. This audit documents:
1. Current state per jewel (mostly migrated)
2. Remaining issues and patterns that deviate
3. Reusable patterns and isomorphisms
4. Page-level inconsistencies (where pages don't use client properly)

## The Metaphysical Fullstack Pattern

**Core Insight**: The protocol IS the API. All transports collapse to:

```typescript
// Old pattern (direct endpoints)
const response = await fetch('/v1/codebase/topology');

// New pattern (AGENTESE gateway)
const response = await fetch('/agentese/world/codebase/manifest', {
  headers: { 'X-Observer-Archetype': 'architect' }
});
```

### Gateway Response Envelope

All AGENTESE gateway responses follow this envelope:

```typescript
interface AGENTESEResponse<T> {
  path: string;      // e.g., "world.codebase"
  aspect: string;    // e.g., "manifest"
  result: T;         // The actual data
}
```

The `unwrapAgentese()` helper in `client.ts` handles this correctly.

---

## Jewel-by-Jewel Audit

### 1. Brain (`/brain`)

**Status**: ✅ **MIGRATED** - Uses AGENTESE patterns correctly

**Current API Client** (`brainApi`):
```typescript
capture: async (data) => unwrapAgentese(await axios.post('/agentese/self/memory/capture', data)),
ghost: async (data) => unwrapAgentese(await axios.post('/agentese/self/memory/ghost', data)),
getMap: async () => unwrapAgentese(await axios.get('/agentese/self/memory/manifest')),
getStatus: async () => unwrapAgentese(await axios.get('/agentese/self/memory/manifest')),
getTopology: async (threshold) => unwrapAgentese(await axios.post('/agentese/self/memory/topology', {...})),
```

**Page Status**: ✅ Brain.tsx uses `brainApi` correctly

**Notes**: Uses correct `self.memory.*` AGENTESE paths

---

### 2. Town (`/town`)

**Status**: ✅ **MIGRATED** - Reference implementation for AGENTESE patterns

**Current API Client** (`townApi`):
```typescript
create: async (data) => unwrapAgentese(await axios.post('/agentese/world/town/start', data)),
get: async () => unwrapAgentese(await axios.get('/agentese/world/town/manifest')),
getCitizens: async () => unwrapAgentese(await axios.post('/agentese/world/town/citizen/list', {})),
getCitizen: async (name, lod) => unwrapAgentese(await axios.post('/agentese/world/town/citizen/get', {...})),
getCoalitions: async () => unwrapAgentese(await axios.post('/agentese/world/town/coalitions', {})),
step: async (cycles) => unwrapAgentese(await axios.post('/agentese/world/town/step', { cycles })),
getMetrics: async (since) => unwrapAgentese(await axios.post('/agentese/world/town/metrics', {...})),
```

**Page Status**: ✅ Town.tsx uses `townApi` correctly

**Pattern**: Town is the **gold standard** for AGENTESE migration

---

### 3. Garden/Gardener (`/garden`, `/gardener`)

**Status**: ✅ **MIGRATED** (2025-12-17)

**All AGENTESE (client.ts)**:
```typescript
getSession: async () => unwrapAgentese(await axios.get('/agentese/concept/gardener/manifest')),
createSession: async (data) => unwrapAgentese(await axios.post('/agentese/concept/gardener/start', data)),
advanceSession: async () => unwrapAgentese(await axios.post('/agentese/concept/gardener/advance', {})),
getGarden: async () => unwrapAgentese(await axios.get('/agentese/self/garden/manifest')),
tend: async (verb, target, opts) => unwrapAgentese(await axios.post('/agentese/self/garden/nurture', {...})),
transitionSeason: async (season, reason) => unwrapAgentese(await axios.post('/agentese/self/garden/season', {...})),
focusPlot: async (name) => unwrapAgentese(await axios.post('/agentese/self/garden/focus', {...})),
acceptTransition: async (from, to) => unwrapAgentese(await axios.post('/agentese/self/garden/transition/accept', {...})),
dismissTransition: async (from, to) => unwrapAgentese(await axios.post('/agentese/self/garden/transition/dismiss', {...})),
surprise: async () => unwrapAgentese(await axios.post('/agentese/void/garden/sip', {})),
```

**Page Status**:
- Garden.tsx: ✅ Updated to use unwrapped responses
- Gardener.tsx: ⚠️ Still uses mock data (feature incomplete)

---

### 4. Gestalt (`/gestalt`)

**Status**: ✅ **MIGRATED** (2025-12-17)

**All AGENTESE (client.ts)**:
```typescript
getManifest: async () => unwrapAgentese(await axios.get('/agentese/world/codebase/manifest')),
getHealth: async () => unwrapAgentese(await axios.get('/agentese/world/codebase/health')),
getDrift: async () => unwrapAgentese(await axios.get('/agentese/world/codebase/drift')),
getModule: async (name) => unwrapAgentese(await axios.post('/agentese/world/codebase/module/get', { module_name: name })),
getTopology: async (maxNodes, minHealth, role) => unwrapAgentese(await axios.post('/agentese/world/codebase/topology', {...})),
scan: async (language, path) => unwrapAgentese(await axios.post('/agentese/world/codebase/scan', {...})),
```

**Page Status**:
- Gestalt.tsx: ✅ Updated to use unwrapped responses
- Crown.tsx: ✅ Updated to use unwrapped responses

---

### 5. Park (`/park`)

**Status**: ✅ **MIGRATED** - Uses AGENTESE patterns correctly

**Current API Client** (`parkApi`):
```typescript
getScenario: async () => unwrapAgentese(await axios.get('/agentese/world/park/manifest')),
startScenario: async (data) => unwrapAgentese(await axios.post('/agentese/world/park/scenario/start', data)),
tick: async (data) => unwrapAgentese(await axios.post('/agentese/world/park/scenario/tick', data)),
transitionPhase: async (data) => unwrapAgentese(await axios.post('/agentese/world/park/scenario/phase', data)),
maskAction: async (data) => unwrapAgentese(await axios.post('/agentese/world/park/mask/${action}', data)),
useForce: async () => unwrapAgentese(await axios.post('/agentese/world/park/force/use', {})),
completeScenario: async (data) => unwrapAgentese(await axios.post('/agentese/world/park/scenario/complete', data)),
getMasks: async () => { const r = unwrapAgentese(...); return r.masks || []; },
getStatus: async () => unwrapAgentese(await axios.get('/agentese/world/park/manifest')),
```

**Page Status**: ✅ ParkScenario.tsx uses `parkApi` correctly

---

### 6. Workshop/Atelier (`/workshop`, `/atelier`)

**Status**: ❌ **NOT MIGRATED** - Uses legacy `/v1/workshop/*`

**Current API Client** (`workshopApi`):
```typescript
get: () => axios.get('/v1/workshop'),
assignTask: (desc, priority) => axios.post('/v1/workshop/task', {...}),
getStatus: () => axios.get('/v1/workshop/status'),
getBuilders: () => axios.get('/v1/workshop/builders'),
// ... all legacy endpoints
```

**Page Issues**:
- Workshop.tsx uses **placeholder state** - no real API calls
- Should be `/agentese/world/atelier/*`

**Fix Priority**: Low (features incomplete)

---

### 7. Crown (`/crown`)

**Status**: ✅ **MIGRATED** (2025-12-17)

**Consistent Pattern**:
```typescript
const [gestaltRes, brainRes, gardenRes] = await Promise.allSettled([
  gestaltApi.getHealth(),      // Returns unwrapped data (AGENTESE)
  brainApi.getStatus(),        // Returns unwrapped data (AGENTESE)
  gardenerApi.getGarden(),     // Returns unwrapped data (AGENTESE)
]);

// Consistent access patterns - all use .value directly:
if (gestaltRes.value) { ... }
if (brainRes.value) { ... }
if (gardenRes.value) { ... }
```

**Notes**: Crown now benefits from all underlying APIs using consistent AGENTESE patterns

---

## Reusable Patterns & Isomorphisms

### Pattern 1: AGENTESE Client Factory

Create a unified client that handles the envelope unwrapping:

```typescript
// impl/claude/web/src/api/agentese-client.ts

interface InvokeOptions {
  archetype?: string;
  capabilities?: string[];
}

class AgenteseClient {
  private baseUrl = '/agentese';

  async invoke<T>(path: string, payload?: object, options?: InvokeOptions): Promise<T> {
    const url = `${this.baseUrl}/${path.replace(/\./g, '/')}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (options?.archetype) {
      headers['X-Observer-Archetype'] = options.archetype;
    }
    if (options?.capabilities?.length) {
      headers['X-Observer-Capabilities'] = options.capabilities.join(',');
    }

    const method = payload ? 'POST' : 'GET';
    const response = await fetch(url, {
      method,
      headers,
      body: payload ? JSON.stringify(payload) : undefined,
    });

    if (!response.ok) {
      throw new Error(`AGENTESE error: ${response.status}`);
    }

    const envelope = await response.json();
    return envelope.result as T;  // Unwrap envelope
  }

  manifest<T>(path: string, options?: InvokeOptions): Promise<T> {
    return this.invoke(`${path}/manifest`, undefined, options);
  }
}

export const agentese = new AgenteseClient();
```

### Pattern 2: Observer Context Provider

```typescript
// impl/claude/web/src/contexts/ObserverContext.tsx

interface ObserverState {
  archetype: string;
  capabilities: string[];
}

const ObserverContext = createContext<ObserverState>({
  archetype: 'guest',
  capabilities: [],
});

export function useObserver() {
  return useContext(ObserverContext);
}

// Usage in API calls
function useJewelManifest(path: string) {
  const observer = useObserver();

  return useQuery({
    queryKey: ['agentese', path, observer.archetype],
    queryFn: () => agentese.manifest(path, observer),
  });
}
```

### Pattern 3: Envelope Unwrapping Axios Interceptor

```typescript
// impl/claude/web/src/api/client.ts

// Add response interceptor to unwrap AGENTESE envelope
axiosInstance.interceptors.response.use((response) => {
  // If it's an AGENTESE response, unwrap it
  if (response.data?.path && response.data?.aspect && response.data?.result !== undefined) {
    return { ...response, data: response.data.result };
  }
  return response;
});
```

### Pattern 4: Dual-Mode API (Graceful Degradation)

```typescript
// Support both legacy and AGENTESE patterns during migration

const gestaltApi = {
  getTopology: async (params: TopologyParams) => {
    try {
      // Try AGENTESE first
      return await agentese.invoke('world.codebase.topology', params);
    } catch (e) {
      // Fall back to legacy
      console.warn('AGENTESE unavailable, using legacy endpoint');
      return axios.get('/v1/world/codebase/topology', { params });
    }
  },
};
```

---

## Isomorphism: CLI ↔ Web ↔ API

The same AGENTESE path works across all surfaces:

| Surface | Pattern |
|---------|---------|
| CLI | `kg query world.town.manifest` |
| Web | `agentese.invoke('world.town.manifest')` |
| API | `GET /agentese/world/town/manifest` |
| Python | `await logos.invoke("world.town.manifest", observer)` |

**The path IS the contract.**

---

## Migration Status Summary (2025-12-17)

| Jewel | Status | Notes |
|-------|--------|-------|
| Brain | ✅ Complete | `self.memory.*` paths |
| Town | ✅ Complete | Reference implementation |
| Garden | ✅ Complete | `self.garden.*` + `concept.gardener.*` paths |
| Gestalt | ✅ Complete | `world.codebase.*` paths |
| Park | ✅ Complete | `world.park.*` paths |
| Workshop | ❌ Not started | Feature incomplete, uses mock data |
| Crown | ✅ Complete | Aggregates other jewels |

---

## Remaining Work

### Immediate
- [ ] Gardener page: Replace mock data with real API calls

### Future
- [ ] Workshop/Atelier: Full AGENTESE integration when feature is complete
- [ ] Add `X-Observer-Archetype` headers globally (currently case-by-case)
- [ ] Create unified `AgenteseClient` class for cleaner ergonomics
- [ ] Add `ObserverContext` React provider

---

## Key Learnings

1. **Envelope unwrapping is essential**: Gateway wraps responses in `{ path, aspect, result }` - clients must use `unwrapAgentese()`
2. **Observer headers matter**: `X-Observer-Archetype` enables observer-dependent views
3. **Path is the contract**: Same path works across CLI/Web/API/Python - leverage this
4. **Town is the reference**: Town's API client was the gold standard for AGENTESE patterns
5. **Graceful degradation**: The `unwrapAgentese()` helper handles edge cases cleanly

---

## Changes Made (2025-12-17)

### `client.ts`
- Migrated `gestaltApi` from `/v1/world/codebase/*` → `/agentese/world/codebase/*`
- Migrated `gardenerApi` legacy endpoints:
  - `transitionSeason` → `/agentese/self/garden/season`
  - `focusPlot` → `/agentese/self/garden/focus`
  - `acceptTransition` → `/agentese/self/garden/transition/accept`
  - `dismissTransition` → `/agentese/self/garden/transition/dismiss`
- **CRITICAL FIX**: Migrated `townApi` from AGENTESE singleton to AUP multi-tenant routes:
  - `create` → `/api/v1/town/{town_id}/init`
  - `get` → `/api/v1/town/{town_id}/status`
  - `step` → `/api/v1/town/{town_id}/step`
  - SSE stream now uses `/api/v1/town/{town_id}/events`

### `useTownStreamWidget.ts`
- Fixed SSE URL from `/v1/town/{id}/live` (non-existent) to `/api/v1/town/{id}/events`
- Fixed SSE event names to match backend: `town.status`, `town.isometric`, `town.event`
- Added API key query param support for EventSource (can't send headers)
- Fixed ColonyDashboardJSON transformation with required fields

### `auth.py`
- Added query param support for API key authentication
- EventSource can now authenticate via `?api_key=...` query param

### `Gestalt.tsx`
- Updated `loadTopology()` to use unwrapped response
- Updated `handleNodeClick()` to use unwrapped module details

### `Crown.tsx`
- Updated `fetchStatus()` to use consistent unwrapped responses from all APIs

### `Garden.tsx`
- Updated `handleAcceptTransition()` to use unwrapped response

---

## Root Cause: Town Frontend Failure

The Town frontend was broken due to a **dual-API mismatch**:

1. **AGENTESE TownNode** (`/agentese/world/town/*`) - Singleton, in-memory town
2. **AUP Town Routes** (`/api/v1/town/{town_id}/*`) - Multi-tenant, has own `_town_fluxes` registry

The frontend was calling AGENTESE for `create`/`get` but expecting SSE from AUP.
These systems don't share state! A town created via AGENTESE wouldn't exist in AUP.

**Solution**: Migrated `townApi` to use AUP routes exclusively for consistent data flow.

---

*Audit and fixes completed 2025-12-17*
