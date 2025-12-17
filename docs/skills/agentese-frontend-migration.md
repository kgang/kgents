# Skill: AGENTESE Frontend Migration

Migrating frontend API calls to route through the AGENTESE Universal Protocol gateway.

## When to Use

- Adding new Crown Jewel frontend integrations
- Migrating existing API calls to AGENTESE
- Debugging AGENTESE gateway issues

## Core Pattern: Response Unwrapping

AGENTESE wraps all responses in an envelope:

```typescript
// AGENTESE response envelope
interface AgenteseResponse<T> {
  path: string;      // e.g., "self.memory"
  aspect: string;    // e.g., "capture"
  result: T;         // The actual payload
  error?: string;    // Optional error message
}

// Helper to extract result
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  if (!response.data) {
    throw new Error('AGENTESE response missing data envelope');
  }
  if (response.data.error) {
    throw new Error(`AGENTESE error: ${response.data.error}`);
  }
  return response.data.result;
}
```

## Route Mapping Reference

| Frontend Method | AGENTESE Path | Backend Context |
|-----------------|---------------|-----------------|
| `brainApi.capture` | `/agentese/self/memory/capture` | `SelfContextResolver.memory.capture` |
| `brainApi.ghost` | `/agentese/self/memory/ghost` | `SelfContextResolver.memory.ghost` |
| `brainApi.getStatus` | `/agentese/self/memory/manifest` | `SelfContextResolver.memory.manifest` |
| `brainApi.getTopology` | `/agentese/self/memory/topology` | `SelfContextResolver.memory.topology` |
| `townApi.create` | `/agentese/world/town/start` | `TownNode.start` |
| `townApi.get` | `/agentese/world/town/manifest` | `TownNode.manifest` |
| `townApi.step` | `/agentese/world/town/step` | `TownNode.step` |
| `gardenerApi.getSession` | `/agentese/concept/gardener/manifest` | `GardenerNode.manifest` |
| `gardenerApi.createSession` | `/agentese/concept/gardener/start` | `GardenerNode.start` |
| `gardenerApi.getGarden` | `/agentese/self/garden/manifest` | `GardenNode.manifest` |
| `parkApi.startScenario` | `/agentese/world/park/scenario/start` | `ScenarioNode.start` |
| `parkApi.getMasks` | `/agentese/world/park/mask/manifest` | `MaskNode.manifest` |

## Migration Checklist

### 1. Update API Client Method

**Before** (direct axios):
```typescript
export const brainApi = {
  capture: (data: BrainCaptureRequest) =>
    apiClient.post<BrainCaptureResponse>('/v1/brain/capture', data),
};
```

**After** (AGENTESE):
```typescript
export const brainApi = {
  capture: async (data: BrainCaptureRequest): Promise<BrainCaptureResponse> => {
    const response = await apiClient.post<AgenteseResponse<BrainCaptureResponse>>(
      '/agentese/self/memory/capture',
      data
    );
    return unwrapAgentese(response);
  },
};
```

### 2. Update Consumers (Remove `.data`)

**Before**:
```typescript
const response = await brainApi.capture({ content });
setResult(response.data.concept_id);  // axios .data access
```

**After**:
```typescript
const result = await brainApi.capture({ content });
setResult(result.concept_id);  // Direct access
```

### 3. Verify Backend Route Exists

Check that the AGENTESE path resolves:
```python
from protocols.agentese.logos import Logos
from bootstrap.umwelt import Umwelt

logos = Logos()
observer = Umwelt.guest()

# This should not raise
result = await logos.invoke("self.memory.capture", observer, content="test")
```

## Common Pitfalls

### 1. Forgetting to Remove `.data`

The most common error after migration:
```
TypeError: Cannot read property 'concept_id' of undefined
```

**Cause**: Code still accessing `response.data.field` instead of `result.field`.

**Fix**: Search for `.data.` in page components and remove the `.data` part.

### 2. Wrong HTTP Method

AGENTESE aspects are typically:
- `GET` for perception aspects (`manifest`, `witness`)
- `POST` for mutation aspects (`capture`, `start`, `step`)

Check the `@aspect` decorator in the backend to confirm.

### 3. Missing Request Body

POST requests to AGENTESE require a body even if empty:
```typescript
// Wrong - will fail
await apiClient.post('/agentese/world/town/step');

// Correct
await apiClient.post('/agentese/world/town/step', {});
```

### 4. Path Segments vs Dots

AGENTESE paths use dots (`self.memory.capture`) but HTTP routes use slashes (`/agentese/self/memory/capture`).

The gateway at `/agentese/{context}/{holon}/{aspect}` handles the translation.

## Error Handling Pattern (Robustified)

Use the `AgenteseError` class for typed error handling:

```typescript
// Error type for AGENTESE-specific failures
export class AgenteseError extends Error {
  constructor(
    message: string,
    public readonly path: string,
    public readonly aspect?: string,
    public readonly suggestion?: string
  ) {
    super(message);
    this.name = 'AgenteseError';
  }
}

// Robustified unwrapper
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  // Check for missing data envelope
  if (!response.data) {
    throw new AgenteseError(
      'AGENTESE response missing data envelope',
      'unknown',
      undefined,
      'Check backend logs for route handler errors'
    );
  }

  // Check for AGENTESE-level errors
  if (response.data.error) {
    throw new AgenteseError(
      response.data.error,
      response.data.path || 'unknown',
      response.data.aspect,
      'Check /agentese/discover for available paths'
    );
  }

  return response.data.result;
}

// Development logging helper
export async function withAgenteseLogging<T>(
  path: string,
  call: () => Promise<T>
): Promise<T> {
  if (import.meta.env.DEV) {
    console.debug(`[AGENTESE] Calling: ${path}`);
  }
  try {
    const result = await call();
    if (import.meta.env.DEV) {
      console.debug(`[AGENTESE] ${path} succeeded:`, result);
    }
    return result;
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error(`[AGENTESE] ${path} failed:`, error);
    }
    throw error;
  }
}
```

## Backend Resolution Architecture

The AGENTESE gateway uses two resolution mechanisms:

1. **NodeRegistry** (`@node` decorator) - For services layer nodes
2. **Logos + ContextResolvers** - For agent layer nodes (majority)

The resolution order in `Logos._resolve_context()`:
1. Check NodeRegistry for `@node` decorated classes
2. Use context-specific resolvers from `create_context_resolvers()`
3. Check SimpleRegistry (legacy)
4. JIT generate from spec files

**Key Insight**: Most Crown Jewel routes are handled by context resolvers (step 2), not the registry (step 1). This is why the registry shows only 4 nodes but the system handles hundreds of paths.

## Debugging Tips

### List All Registered Paths

```python
# Check what's available
from protocols.agentese.registry import get_registry
registry = get_registry()
print(f"Registered nodes: {registry.stats()['registered_nodes']}")
for path in sorted(registry.list_paths()):
    print(f"  {path}")
```

### Verify Path Resolution

```python
from protocols.agentese.logos import create_logos
logos = create_logos()

# Test resolution (will raise if path doesn't exist)
node = logos.resolve("self.memory")
print(f"Resolved: {node.handle}")
print(f"Affordances: {node.affordances(AgentMeta(archetype='user'))}")
```

### Trace Gateway Request

Add `X-Observer-Archetype` header to see what affordances are available:
```bash
curl -H "X-Observer-Archetype: developer" http://localhost:8000/agentese/self/memory/affordances
```

## Testing After Migration

1. **TypeScript compilation**: `npx tsc --noEmit`
2. **Production build**: `npm run build`
3. **Manual smoke test**: Exercise each API call in the browser
4. **Check browser console**: No 404s, no TypeScript errors
5. **Verify response shape**: Log and inspect actual responses

## Files Modified in Typical Migration

- `impl/claude/web/src/api/client.ts` - API method updates
- `impl/claude/web/src/pages/*.tsx` - Remove `.data` access
- `impl/claude/web/src/components/**/*.tsx` - Remove `.data` access
- `impl/claude/web/src/hooks/*.ts` - If hooks wrap API calls

## Related Skills

- `agentese-path.md` - Adding new AGENTESE paths
- `handler-patterns.md` - CLI handler patterns (similar concepts)
- `crown-jewel-patterns.md` - Crown Jewel implementation patterns
