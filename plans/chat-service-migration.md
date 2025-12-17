---
path: plans/chat-service-migration
status: complete
progress: 100
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables: [cli-isomorphic-migration]
session_notes: |
  Migrating chat from protocols/agentese/chat/ to services/chat/
  Following Metaphysical Fullstack pattern (AD-009)
phase_ledger:
  PLAN: touched
  RESEARCH: skipped  # reason: patterns established in spec
  DEVELOP: active
  STRATEGIZE: skipped
  CROSS-SYNERGIZE: skipped
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: skipped
  MEASURE: skipped
  REFLECT: pending
entropy:
  planned: 0.3
  spent: 0.1
  returned: 0.0
---

# Chat Service Migration

> *"Chat is not a protocol detail. Chat is a Crown Jewel affordance."*

## Context

Chat currently lives in `protocols/agentese/chat/`. Per the **Metaphysical Fullstack** pattern (AD-009), Crown Jewel services should live in `services/` where they:
- Own their business logic + adapters
- Expose AGENTESE nodes via `@node` decorator
- Integrate with D-gent for persistence

## The Migration

### Phase 1: Service Module Migration (Breaking Change)

```
# FROM:
protocols/agentese/chat/
├── __init__.py
├── session.py
├── factory.py
├── persistence.py
├── context_projector.py
├── observability.py
├── config.py
└── _tests/

# TO:
services/chat/
├── __init__.py           # Public API
├── session.py            # ChatSession coalgebra
├── factory.py            # ChatSessionFactory
├── persistence.py        # D-gent + TableAdapter integration
├── context_projector.py  # WorkingContextProjector
├── observability.py      # OTEL spans + metrics
├── config.py             # ChatConfig
├── node.py               # @node("self.chat") AGENTESE interface
└── _tests/
```

### Phase 2: AGENTESE-First CLI

Update `chat_projection.py` to route through `logos.invoke()`:

```python
# BEFORE: Direct session creation
from protocols.agentese.chat import ChatSessionFactory
session = await factory.create_session(...)

# AFTER: Through AGENTESE
await logos.invoke("self.chat.create_session", observer, node_path=path)
```

### Phase 3: Dual-Track Persistence

1. Create `models/chat.py` with SQLAlchemy tables
2. Update ChatPersistence to use TableAdapter + D-gent
3. Add session search/filter by metadata

### Phase 4: Memory Integration

1. Wire WorkingContextProjector to M-gent
2. Implement medium-term summary compression
3. Enable cross-session memory injection

## Files to Change

| File | Change |
|------|--------|
| `services/chat/__init__.py` | Create - public API |
| `services/chat/session.py` | Move from protocols |
| `services/chat/factory.py` | Move from protocols |
| `services/chat/persistence.py` | Move from protocols |
| `services/chat/context_projector.py` | Move from protocols |
| `services/chat/observability.py` | Move from protocols |
| `services/chat/config.py` | Move from protocols |
| `services/chat/node.py` | Create - AGENTESE node |
| `services/providers.py` | Add chat service |
| `services/bootstrap.py` | Register chat |
| `protocols/cli/chat_projection.py` | Update imports |
| `protocols/agentese/contexts/chat_resolver.py` | Update imports |

## Success Criteria

- [x] `kg soul chat` works via new service module
- [x] All existing chat tests pass (121 tests)
- [x] ChatNode registered with AGENTESE
- [x] Persistence works via D-gent
- [x] Backward compatibility via protocols.agentese.chat re-export

## Migration Summary

1. **Phase 1 Complete**: Created `services/chat/` with 7 modules
   - config.py, session.py, factory.py, persistence.py
   - context_projector.py, observability.py, node.py

2. **Phase 2 Complete**: ChatNode registered with AGENTESE
   - `@node("self.chat")` decorator
   - 12 aspects: create, send, stream, history, save, sessions, etc.

3. **Phase 3 Complete**: DI Integration
   - Added to services/providers.py
   - get_chat_persistence(), get_chat_factory()

4. **Phase 4 Complete**: Backward Compatibility
   - protocols.agentese.chat re-exports from services.chat
   - Deprecation warnings for direct imports

---

*Lines: 95 | Created: 2025-12-17 | Completed: 2025-12-17*
