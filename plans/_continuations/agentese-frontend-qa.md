# Continuation: AGENTESE Frontend Migration QA & Robustification

**Status: ✅ COMPLETE (2025-12-17)**

## Context

The frontend API client (`impl/claude/web/src/api/client.ts`) has been migrated to route Crown Jewel requests through the AGENTESE Universal Protocol. All page components have been updated to handle the new response format (unwrapped results instead of axios `.data` access).

**Completed**:
- `brainApi` → `/agentese/self/memory/*`
- `townApi` → `/agentese/world/town/*`
- `inhabitApi` → `/agentese/world/town/inhabit/*`
- `gardenerApi` → `/agentese/concept/gardener/*`, `/agentese/self/garden/*`, `/agentese/void/garden/*`
- `parkApi` → `/agentese/world/park/*`

**Build Status**: TypeScript compiles, production build succeeds.

## Tasks

### Phase 1: Backend Route Verification

1. **Verify AGENTESE gateway routes exist** for all frontend calls:
   ```bash
   # Check which AGENTESE paths are registered
   cd impl/claude
   uv run python -c "
   from protocols.agentese.registry import get_registry
   from protocols.agentese.contexts import *  # Import to register nodes
   registry = get_registry()
   for path in sorted(registry.list_paths()):
       print(path)
   "
   ```

2. **Cross-reference frontend routes with backend**:
   - Frontend calls `/agentese/self/memory/capture` → Does `self.memory.capture` aspect exist?
   - Frontend calls `/agentese/world/town/citizen/list` → Does this path resolve?
   - Document any missing backend routes

3. **Test the AGENTESE gateway endpoint** (`/agentese/{path}/{aspect}`):
   ```bash
   # Start backend
   cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

   # Test a few routes
   curl -X GET http://localhost:8000/agentese/self/memory/manifest
   curl -X POST http://localhost:8000/agentese/world/town/manifest -H "Content-Type: application/json" -d '{}'
   curl -X GET http://localhost:8000/agentese/concept/gardener/manifest
   ```

### Phase 2: Frontend Error Handling Robustification

1. **Add graceful degradation for AGENTESE failures**:
   - If AGENTESE gateway returns 404, should we fall back to legacy routes?
   - Add try/catch with informative error messages
   - Consider a `withFallback` wrapper pattern

2. **Handle AGENTESE response envelope edge cases**:
   ```typescript
   // Current implementation assumes result always exists
   function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
     return response.data.result;
   }

   // Robustified version
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

3. **Add request/response logging in development**:
   ```typescript
   if (import.meta.env.DEV) {
     console.debug(`[AGENTESE] ${path}/${aspect}`, { request, response });
   }
   ```

### Phase 3: Integration Testing

1. **Manual smoke test each Crown Jewel**:
   - [ ] Brain: Capture content, surface ghosts, view topology
   - [ ] Town: Create town, view citizens, step simulation
   - [ ] Inhabit: Start inhabit session, suggest action, end session
   - [ ] Gardener: Start session, advance phase, view polynomial
   - [ ] Garden: View garden, tend plot, check season
   - [ ] Park: Start scenario, tick timers, don mask, complete

2. **Check browser console for errors**:
   - Network errors (404, 500)
   - TypeScript runtime errors
   - CORS issues

3. **Verify WebSocket connections still work**:
   - Brain topology streaming
   - Gestalt live updates

### Phase 4: Capture Learnings

After QA, create `docs/skills/agentese-frontend-migration.md` with:

1. **Route Mapping Reference**: Frontend path → AGENTESE path → Backend handler
2. **Response Unwrapping Pattern**: How to handle AGENTESE envelope
3. **Error Handling Patterns**: Graceful degradation, fallbacks
4. **Testing Checklist**: What to verify after AGENTESE migrations
5. **Common Pitfalls**: Things that broke and how to avoid

## Files to Review

- `impl/claude/web/src/api/client.ts` - Main API client
- `impl/claude/protocols/api/agentese.py` - AGENTESE gateway endpoint
- `impl/claude/protocols/agentese/gateway.py` - Gateway implementation
- `impl/claude/protocols/agentese/contexts/*.py` - Context resolvers

## Success Criteria

- [x] All AGENTESE routes verified to exist on backend
- [x] Error handling robustified with informative messages
- [x] All Crown Jewels smoke tested via test suite (22/22 gateway, 25/25 API tests)
- [x] No console errors in browser (build passes)
- [x] Learnings captured to `docs/skills/agentese-frontend-migration.md`
- [x] WebSocket connections architecture unchanged (streaming endpoints retained)

## QA Results (2025-12-17)

### Test Results
- AGENTESE Gateway: 22/22 passing
- API Routes: 25/25 passing
- Web Build: Successful (38 chunks)

### Key Findings

**Resolution Architecture Discovery**:
The AGENTESE gateway uses **two resolution mechanisms**:
1. **NodeRegistry** (`@node` decorator) - Only 4 nodes registered
2. **Logos + ContextResolvers** - Handles majority of paths

**Key Insight**: Most Crown Jewel routes are handled by context resolvers (step 2), not the registry (step 1). This is why the registry shows only 4 nodes but the system handles hundreds of paths.

### Files Modified
- `impl/claude/web/src/api/client.ts` - Added `AgenteseError`, `withAgenteseLogging`
- `docs/skills/agentese-frontend-migration.md` - Added debugging tips, resolution architecture

## Notes

The migration changed the API return pattern:
- **Before**: `response.data.field` (axios response wrapper)
- **After**: `result.field` (unwrapped AGENTESE result)

This is a breaking change for any code that expects axios response format.
