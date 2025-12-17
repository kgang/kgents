# Chat Protocol Implementation Plan

**Status**: Complete
**Priority**: High
**Progress**: 100%
**Parent**: `plans/cli-isomorphic-migration.md`
**Spec**: `spec/protocols/chat.md`
**Last Updated**: 2025-12-17

---

## Objective

Implement the AGENTESE Chat Protocol as specified in `spec/protocols/chat.md`. This enables native chat affordances for any AGENTESE node, with K-gent Soul and Town Citizens as the primary use cases.

---

## Overview

The chat protocol provides:
1. **Universal Chat Affordances**: `<node>.chat.send`, `.history`, `.context`, etc.
2. **Session Management**: Stateful coalgebra over F-gent ChatFlow
3. **CLI Interactive Mode**: REPL for `Interactivity.INTERACTIVE` dimensions
4. **D-gent Persistence**: Cross-session memory and recall

---

## Implementation Phases

### Phase 1: Core ChatSession (Days 1-2)

**Files to Create:**

| File | Purpose | Lines Est. |
|------|---------|------------|
| `protocols/agentese/chat/__init__.py` | Module exports | ~20 |
| `protocols/agentese/chat/session.py` | ChatSession wrapping F-gent | ~250 |
| `protocols/agentese/chat/factory.py` | ChatSessionFactory | ~150 |
| `protocols/agentese/chat/context.py` | Working context projection | ~100 |
| `protocols/agentese/chat/config.py` | ChatConfig dataclass | ~80 |

**Tasks:**

- [x] Create `ChatSession` class
  - [x] Wrap F-gent `ChatFlow`
  - [x] Implement state machine (DORMANT → READY → STREAMING → WAITING → COLLAPSED)
  - [x] Turn protocol with atomic turns
  - [x] Budget tracking

- [x] Create `ChatSessionFactory`
  - [x] System prompt generation from node metadata
  - [x] Config resolution (node config → defaults)
  - [x] LLM agent selection
  - [x] Session ID generation

- [x] Create `WorkingContextProjector`
  - [x] Hierarchical memory integration
  - [x] Context strategy application (sliding/summarize)
  - [x] Token budget enforcement

- [x] Tests
  - [x] `test_chat_session.py` - 37 tests for state machine, turns, metrics
  - [x] `test_chat_factory.py` - 23 tests for factory, prompts, caching

**Files Created:**
- `protocols/agentese/chat/__init__.py`
- `protocols/agentese/chat/config.py`
- `protocols/agentese/chat/session.py`
- `protocols/agentese/chat/factory.py`
- `protocols/agentese/chat/context_projector.py`
- `protocols/agentese/chat/_tests/test_chat_session.py`
- `protocols/agentese/chat/_tests/test_chat_factory.py`

**Test Count:** 60 tests passing

### Phase 2: AGENTESE Integration (Days 3-4)

**Files to Create/Modify:**

| File | Action | Lines Est. |
|------|--------|------------|
| `protocols/agentese/affordances.py` | Add `@chatty` decorator | +150 |
| `protocols/agentese/contexts/chat_resolver.py` | Chat sub-resolver | ~320 |
| `protocols/agentese/contexts/self_soul.py` | Add chat affordances | ~320 |
| `protocols/agentese/contexts/self_.py` | Add soul resolver integration | +30 |
| `protocols/agentese/contexts/town_citizen.py` | (Future - Phase 2.5) | ~200 |

**Tasks:**

- [x] Create `@chatty` decorator
  - [x] Adds `chat.*` affordances to decorated node
  - [x] Configures ChatSession factory
  - [x] `ChattyConfig` dataclass for decorator config
  - [x] `is_chatty()` and `get_chatty_config()` helpers
  - [x] `to_chat_config()` converter

- [x] Create chat sub-resolver
  - [x] Resolves `<node>.chat.<aspect>` paths
  - [x] Creates/retrieves sessions by (node, observer)
  - [x] Session lifecycle management
  - [x] Global ChatResolver with caching
  - [x] `ChatNode` with all chat affordances

- [x] Add chat to K-gent Soul
  - [x] `self.soul.chat.send`
  - [x] `self.soul.chat.history`
  - [x] `self.soul.chat.stream`
  - [x] System prompt with personality eigenvectors
  - [x] `SoulNode` decorated with `@chatty`
  - [x] Integration with `SelfContextResolver`

- [x] Create TownCitizenNode (Phase 2.5 - COMPLETE)
  - [x] `world.town.citizen.<name>.chat.*`
  - [x] Archetype-based system prompts (5 archetypes: Builder, Trader, Healer, Scholar, Watcher)
  - [x] Eigenvector personality injection (7D eigenvectors in prompts)

- [x] Tests
  - [x] `test_chat_resolver.py` - 22 tests covering decorator, ChatNode, ChatResolver, SoulNode
  - [x] `test_town_citizen.py` - 35 tests covering TownCitizenNode, prompts, resolver

**Files Created:**
- `protocols/agentese/contexts/chat_resolver.py`
- `protocols/agentese/contexts/self_soul.py`
- `protocols/agentese/contexts/_tests/test_chat_resolver.py`
- `protocols/agentese/contexts/town_citizen.py` (Phase 2.5)
- `protocols/agentese/contexts/_tests/test_town_citizen.py` (Phase 2.5)

**Test Count:** 117 tests passing (60 Phase 1 + 22 Phase 2 + 35 Phase 2.5)

### Phase 3: CLI Projection (Days 5-6) - COMPLETE

**Files Created/Modified:**

| File | Action | Lines |
|------|--------|-------|
| `protocols/cli/chat_projection.py` | Interactive REPL + ChatRenderer | ~450 |
| `protocols/cli/projection.py` | Route to chat mode | +50 |
| `protocols/cli/handlers/soul.py` | Add chat command | +50 |
| `protocols/cli/commands/soul/__init__.py` | Add chat to modes | +3 |

**Tasks:**

- [x] Create ChatProjection (REPL)
  - [x] Interactive input loop
  - [x] Streaming response display
  - [x] Context/metrics indicators
  - [x] Session commands (/history, /metrics, /reset, /context, /persona, /help, /exit)

- [x] Create ChatRenderer (merged into chat_projection.py)
  - [x] Message bubble styling
  - [x] Streaming progress indicator
  - [x] Context utilization gauge
  - [x] Cost display
  - [x] Status bar with turn/cost/entropy

- [x] Update CLIProjection
  - [x] Route INTERACTIVE paths to ChatProjection
  - [x] Handle `--message` override for one-shot mode
  - [x] Route `.chat` paths automatically

- [x] Update handlers
  - [x] `kg soul chat` - K-gent chat REPL
  - [x] `kg soul chat --message "..."` - one-shot mode
  - [x] Town handler already has chat command (Phase 2)

- [x] Tests
  - [x] `test_chat_projection.py` - 29 tests covering:
    - ChatRenderer formatting (11 tests)
    - ChatProjection lifecycle (7 tests)
    - CLI integration (3 tests)
    - Entry points (2 tests)
    - Gauge rendering (4 tests)
    - Context panel (2 tests)

**Test Count:** 146 tests passing (117 Phase 1-2.5 + 29 Phase 3)

### Phase 4: Persistence (Days 7-8) - COMPLETE

**Files Created/Modified:**

| File | Action | Lines |
|------|--------|-------|
| `protocols/agentese/chat/persistence.py` | D-gent integration + MemoryInjector | ~680 |
| `protocols/cli/commands/chat/__init__.py` | Chat command group | ~45 |
| `protocols/cli/commands/chat/sessions.py` | List sessions | ~100 |
| `protocols/cli/commands/chat/resume.py` | Resume session | ~150 |
| `protocols/cli/commands/chat/search.py` | Search sessions | ~120 |
| `protocols/cli/handlers/chat.py` | CLI handler routing | ~120 |
| `protocols/cli/chat_projection.py` | Added /save, /load commands | +100 |
| `protocols/cli/hollow.py` | Registered chat command | +5 |

**Tasks:**

- [x] Create persistence layer
  - [x] `ChatSessionPersistence` class
  - [x] `PersistedSession` dataclass (on-disk representation)
  - [x] `save_session(session)` → D-gent Datum
  - [x] `load_session(session_id)` → PersistedSession
  - [x] `load_by_name(name)` → PersistedSession
  - [x] `list_sessions(node_path?, observer?)` → List
  - [x] `search_sessions(query)` → List (searches names, tags, content)
  - [x] `delete_session(session_id)` → bool
  - [x] `count_sessions()` → int
  - [x] `get_recent_sessions()` → List

- [x] Create session management CLI
  - [x] `kg chat sessions [--node PATH]` - List saved sessions
  - [x] `kg chat resume <name|id>` - Resume session
  - [x] `kg chat search <query>` - Search sessions
  - [x] `kg chat delete <id>` - Delete session

- [x] Update ChatProjection REPL
  - [x] `/save [name]` - Save current session
  - [x] `/load <name|id>` - Load saved session

- [x] Memory injection
  - [x] `MemoryInjector` class
  - [x] `inject_context(node_path, observer_id, message)` - Build context from past sessions
  - [x] `get_entity_memory(node_path)` - Aggregate entity stats
  - [x] Relevance ranking with recency decay + content overlap

- [x] Tests
  - [x] `test_chat_persistence.py` - 25 tests covering:
    - PersistedSession serialization (3 tests)
    - ChatSessionPersistence CRUD (11 tests)
    - Singleton pattern (2 tests)
    - Edge cases (4 tests)
    - MemoryInjector (5 tests)

**Test Count:** 171 tests passing (146 Phase 1-3 + 25 Phase 4)

### Phase 5: Observability (Days 9-10) - COMPLETE

**Files Created:**

| File | Purpose | Lines |
|------|---------|-------|
| `protocols/agentese/chat/observability.py` | OTEL spans + metrics | ~680 |
| `protocols/agentese/chat/_tests/test_chat_observability.py` | Observability tests | ~450 |

**Tasks:**

- [x] Add OTEL spans
  - [x] `chat.session` span for full conversation
  - [x] `chat.turn` span for each turn
  - [x] `chat.context_render` for context computation
  - [x] `chat.llm_call` with token counts

- [x] Add metrics
  - [x] `chat_turns_total` counter
  - [x] `chat_sessions_total` counter
  - [x] `chat_turn_duration_seconds` histogram
  - [x] `chat_tokens_per_turn` histogram
  - [x] `chat_context_utilization` histogram

- [x] Add in-memory metrics state
  - [x] `get_chat_metrics_summary()` for dashboards
  - [x] `get_active_session_count()` for gauges
  - [x] Thread-safe aggregation

- [x] Tests
  - [x] `test_chat_observability.py` - 36 tests covering:
    - Tracer/meter singletons (2 tests)
    - record_turn function (6 tests)
    - record_session_event function (4 tests)
    - record_error function (2 tests)
    - get_active_session_count function (3 tests)
    - Metrics summary (3 tests)
    - reset_chat_metrics (1 test)
    - ChatTelemetry context managers (7 tests)
    - Utility functions (3 tests)
    - Attribute constants (3 tests)
    - Thread safety (2 tests)

**Test Count:** 207 tests passing (171 Phase 1-4 + 36 Phase 5)

---

## Acceptance Criteria

### Functional

- [x] `kg soul chat` enters interactive REPL with K-gent
- [x] `kg town chat elara` enters interactive REPL with citizen
- [x] `kg soul chat --message "..."` returns one-shot response
- [x] Sessions persist to D-gent memory
- [x] `kg chat sessions` lists saved sessions
- [x] `kg chat resume <name>` restores session
- [x] Context summarization works when threshold exceeded
- [x] Budget tracking shows accurate token counts and costs

### Non-Functional

| Metric | Target |
|--------|--------|
| First response latency | < 2s |
| Streaming first token | < 500ms |
| Context rendering | < 100ms |
| Session save | < 200ms |
| Session load | < 200ms |

### UX

- [x] Streaming shows progressive tokens
- [x] Context utilization displayed
- [x] Turn number visible
- [x] Cost estimates shown
- [x] Graceful entropy depletion
- [x] Clear error messages

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| F-gent ChatFlow | ✅ Exists | `agents/f/modalities/chat.py` |
| D-gent Memory | ✅ Exists | Crystal storage available |
| CLI Dimensions | ✅ Done | `Interactivity.INTERACTIVE` dimension exists |
| CLI Projection | ✅ Done | Routes INTERACTIVE to ChatProjection |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing `kg soul` | Feature flag, progressive rollout |
| ChatFlow API changes | Wrap in adapter layer |
| LLM cost overruns | Budget tracking, warnings, limits |
| Session bloat | Periodic cleanup, size limits |

---

## Success Metrics (from Spec)

| Metric | Target | Status |
|--------|--------|--------|
| Chat paths registered | 100% of @chatty nodes | ✅ Done |
| Interactive mode working | Soul, Citizens | ✅ Done |
| Persistence working | Save/load/resume | ✅ Done |
| Observability coverage | All spans and metrics | ✅ Done |

---

## Summary

**All Phases Complete (2025-12-17)**

The AGENTESE Chat Protocol is fully implemented with all 5 phases:

### Phase 1-2: Core + AGENTESE Integration
- `ChatSession` with state machine, turn protocol, budget tracking
- `ChatSessionFactory` for session creation
- `@chatty` decorator for exposing chat affordances
- `SoulNode` and `TownCitizenNode` with chat capabilities

### Phase 3: CLI Projection
- Interactive REPL with streaming, metrics, commands
- One-shot mode for scripting
- `/history`, `/metrics`, `/reset`, `/save`, `/load`, `/help` commands

### Phase 4: Persistence
- `ChatSessionPersistence` with CRUD operations, search, filtering
- `MemoryInjector` for cross-session context
- `kg chat sessions/resume/search/delete` CLI commands

### Phase 5: Observability
- OTEL spans: `chat.session`, `chat.turn`, `chat.context_render`, `chat.llm_call`
- Metrics: `chat_turns_total`, `chat_sessions_total`, `chat_turn_duration_seconds`, etc.
- Thread-safe in-memory aggregation with `get_chat_metrics_summary()`
- `ChatTelemetry` class with async context managers

**Files Created:**
- `protocols/agentese/chat/` - 10 files (session, factory, config, context_projector, persistence, observability, tests)
- `protocols/cli/chat_projection.py` - Interactive REPL
- `protocols/cli/commands/chat/` - CLI commands
- `protocols/cli/handlers/chat.py` - Handler routing
- `protocols/agentese/contexts/chat_resolver.py` - AGENTESE resolution
- `protocols/agentese/contexts/self_soul.py` - Soul chat node
- `protocols/agentese/contexts/town_citizen.py` - Citizen chat nodes

**Total: 207 tests passing** across all chat protocol phases.

---

*Forest Protocol Plan - COMPLETE*
