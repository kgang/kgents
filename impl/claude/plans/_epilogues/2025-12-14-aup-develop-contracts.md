---
session: 2025-12-14-aup-develop-contracts
phase: DEVELOP
plan: plans/agentese-universal-protocol.md
touched_by: opus-4.5
entropy_spent: 0.02
---

# AUP DEVELOP Phase: Contract Layer

## What Was Done

Designed the **contract layer** for the AGENTESE Universal Protocol (AUP):

### 1. Pydantic Models (`protocols/api/serializers.py`)

**Observer Context** (no view from nowhere):
- `ObserverContext` - archetype, id, capabilities

**Request/Response Types**:
- `AgenteseRequest` / `AgenteseResponse` - standard envelope
- `CompositionRequest` / `CompositionResponse` - pipeline execution
- `ResponseMeta` - span_id, timestamp, laws_verified
- `LawVerificationResult` - identity_holds, associativity_holds

**Streaming Types**:
- `SSEChunk` / `SSECompleteEvent` - Server-Sent Events
- `WSSubscribeMessage` / `WSInvokeMessage` - WebSocket client→server
- `WSStateUpdate` / `WSInvokeResult` - WebSocket server→client
- `WSDialecticEvent` - dialectic phase events

**Garden/Town Types**:
- `EntityState` / `PheromoneState` / `GardenState`

### 2. Bridge Protocol (`protocols/api/bridge.py`)

**AgenteseBridgeProtocol** - abstract interface with:
- `invoke()` - single path invocation
- `compose()` - pipeline composition with law verification
- `stream()` - SSE streaming for long operations
- `subscribe()` - WebSocket channel subscription
- `verify_laws()` - category law verification
- `resolve()` / `affordances()` - path introspection

**Law Assertions**:
- `assert_identity_law()` - verify Id >> f ≡ f
- `assert_associativity_law()` - verify (f >> g) >> h ≡ f >> (g >> h)
- `assert_observer_polymorphism()` - verify different observers, different results

**Error Taxonomy** (sympathetic):
| Code | HTTP | Suggestion Template |
|------|------|---------------------|
| PATH_NOT_FOUND | 404 | "Check path spelling..." |
| AFFORDANCE_DENIED | 403 | "Requires different archetype..." |
| OBSERVER_REQUIRED | 401 | "Include X-Observer headers..." |
| SYNTAX_ERROR | 400 | "Expected format: context.holon.aspect" |
| LAW_VIOLATION | 422 | "Composition violates laws..." |
| BUDGET_EXHAUSTED | 402 | "Accursed Share depleted..." |

### 3. Contract Tests (`protocols/api/_tests/test_aup_contracts.py`)

**33 tests** covering:
- Serializer contracts (8 tests)
- Error taxonomy (4 tests)
- SSE types (3 tests)
- WebSocket types (5 tests)
- Garden state types (3 tests)
- Bridge protocol (6 tests)
- Law assertions (3 tests)
- Error helpers (1 test)

## Files Created

- `impl/claude/protocols/api/serializers.py` - Pydantic models
- `impl/claude/protocols/api/bridge.py` - Protocol + law assertions
- `impl/claude/protocols/api/_tests/test_aup_contracts.py` - Contract tests

## Exit Criteria Met

- [x] All Pydantic models defined with docstrings
- [x] AgenteseBridgeProtocol defined with law documentation
- [x] Error taxonomy complete with suggestions
- [x] Contract stub tests created (33 tests)
- [x] No implementation code (contracts only)
- [x] Ledger updated: `DEVELOP: touched`

## Key Insights

1. **Protocol > ABC**: Using `typing.Protocol` with `@runtime_checkable` allows duck typing without inheritance coupling
2. **Frozen observer**: `ObserverContext` is frozen for immutability guarantees
3. **SSEEvent.serialize()**: Utility for SSE wire format
4. **StubAgenteseBridge**: Enables contract testing without full Logos

## Next Phase

Ready for **CROSS-SYNERGIZE** to:
1. Identify composition opportunities with marimo, SaaS API, TUI
2. Ensure AgenteseBridge unifies all clients
3. Surface parallel tracks for implementation

---

*"The contract is the promise. The implementation is the keeping."*
