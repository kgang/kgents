# Chat Resolvers Implementation Summary

**Date:** 2025-12-25  
**Status:** Complete  
**Spec:** `spec/protocols/portal-resource-system.md`

## Overview

Implemented chat-related portal resolvers for the Portal Resource System. These resolvers enable universal resource addressing for chat sessions, turns, marks, traces, evidence, and constitutional scores.

## Components Implemented

### 1. Core Resolvers (5 new resolvers)

All resolvers follow the `PortalResolver` protocol and integrate with existing portal infrastructure:

#### `ChatResolver` (`services/portal/resolvers/chat.py`)
- **Resource type:** `chat`
- **URI patterns:**
  - `chat:session-abc123` → Full chat session
  - `chat:session-abc123#turn-5` → Specific turn
- **Features:**
  - Resolves chat sessions with metadata (turn count, flow state, branch name)
  - Resolves individual turns with user/assistant messages and tools used
  - Returns appropriate "not found" resources for missing sessions/turns
  - Includes actions: `["expand", "fork", "resume"]` for sessions, `["expand", "fork_from", "cite"]` for turns

#### `MarkResolver` (`services/portal/resolvers/mark.py`)
- **Resource type:** `mark`
- **URI pattern:**
  - `mark:session-abc123#turn-5` → ChatMark with constitutional scores
- **Features:**
  - Resolves ChatMarks from PolicyTrace
  - Includes constitutional scores if available
  - Returns score preview (e.g., "Score: 8.5")
  - Includes actions: `["expand", "view_constitutional"]`

#### `TraceResolver` (`services/portal/resolvers/trace.py`)
- **Resource type:** `trace`
- **URI pattern:**
  - `trace:session-abc123` → Full PolicyTrace
- **Features:**
  - Resolves complete conversation witness trail
  - Returns all marks with timestamps
  - Includes turn count and latest timestamp
  - Includes actions: `["expand", "export", "replay"]`

#### `EvidenceResolver` (`services/portal/resolvers/evidence.py`)
- **Resource type:** `evidence`
- **URI pattern:**
  - `evidence:session-abc123` → Evidence bundle
- **Features:**
  - Resolves Bayesian evidence state
  - Returns prior (alpha/beta), confidence, observations
  - Includes tool success/failure counts
  - Includes actions: `["expand", "view_posterior"]`

#### `ConstitutionalResolver` (`services/portal/resolvers/constitutional.py`)
- **Resource type:** `constitutional`
- **URI patterns:**
  - `constitutional:session-abc123` → Session aggregate scores
  - `constitutional:session-abc123#turn-5` → Turn-specific scores
- **Features:**
  - Resolves constitutional scores with radar visualization data
  - Aggregates scores across turns (mean)
  - Converts scores to radar chart format (7 axes)
  - Includes weighted total score
  - Includes actions: `["expand", "view_radar", "view_history"]`

### 2. Integration

Updated `services/portal/resolvers/__init__.py` to export all new resolvers:
```python
from .chat import ChatResolver
from .constitutional import ConstitutionalResolver
from .evidence import EvidenceResolver
from .mark import MarkResolver
from .trace import TraceResolver
```

Updated `services/portal/__init__.py` to expose resolvers at top level.

### 3. Key Design Decisions

1. **Dependency Injection:** All resolvers accept `session_store` parameter for storage integration
2. **Flexible Storage Interface:** Resolvers check for both `.get()` and `.load()` methods
3. **Graceful Degradation:** Returns "not found" resources instead of raising exceptions
4. **Observer Support:** All resolvers accept optional `observer` parameter for future access control
5. **can_resolve() Method:** Each resolver implements protocol method to check if it handles a URI type
6. **URI Rendering:** Uses `uri.render()` for consistent URI strings in responses

## Usage Examples

### Resolving a Chat Session

```python
from services.portal import ChatResolver, PortalURI

resolver = ChatResolver(session_store=storage)
uri = PortalURI.parse("chat:session-abc123")
resource = await resolver.resolve(uri, observer=None)

# resource.title → "Chat: Design Discussion"
# resource.preview → "12 turns"
# resource.actions → ["expand", "fork", "resume"]
```

### Resolving Constitutional Scores

```python
from services.portal import ConstitutionalResolver, PortalURI

resolver = ConstitutionalResolver(session_store=storage)
uri = PortalURI.parse("constitutional:session-abc123#turn-5")
resource = await resolver.resolve(uri, observer=None)

# resource.content["radar_data"] → [{"axis": "Tasteful", "value": 0.9}, ...]
# resource.content["weighted_total"] → 8.5
```

### Registry Integration

```python
from services.portal import PortalResolverRegistry
from services.portal.resolvers import (
    ChatResolver,
    MarkResolver,
    TraceResolver,
    EvidenceResolver,
    ConstitutionalResolver,
)

registry = PortalResolverRegistry()
registry.register(ChatResolver(session_store=storage))
registry.register(MarkResolver(session_store=storage))
registry.register(TraceResolver(session_store=storage))
registry.register(EvidenceResolver(session_store=storage))
registry.register(ConstitutionalResolver(session_store=storage))

# Resolve any URI
resource = await registry.resolve("chat:session-abc123#turn-5", observer)
```

## Architecture Notes

### Existing Infrastructure Used

- **PortalURI:** Existing URI parser from `services/portal/uri.py`
- **ResolvedResource:** Existing dataclass from `services/portal/resolver.py`
- **PortalResolver Protocol:** Existing protocol that all resolvers implement
- **PortalResolverRegistry:** Existing registry for resolver management

### Chat Infrastructure Used

- **ChatSession:** From `services/chat/session.py`
- **ChatMark:** From `services/chat/witness.py`
- **ChatPolicyTrace:** From `services/chat/witness.py`
- **ChatEvidence:** From `services/chat/evidence.py`
- **PrincipleScore:** From `services/chat/reward.py`

### Fragment Parsing

All resolvers parse `#turn-N` fragments consistently:
```python
def _parse_turn_number(self, fragment: str | None) -> int | None:
    if not fragment:
        return None
    if fragment.startswith("turn-"):
        try:
            return int(fragment[5:])
        except ValueError:
            return None
    return None
```

## Testing

Comprehensive test suite created in `services/portal/_tests/test_chat_resolvers.py` covering:

- ChatResolver: session and turn resolution
- MarkResolver: mark resolution with/without scores
- TraceResolver: trace resolution with empty/populated traces
- EvidenceResolver: evidence with observations
- ConstitutionalResolver: turn scores, session aggregation, radar data
- PortalURI parsing and roundtrip
- Integration tests across all resolvers

## Next Steps

1. **Storage Integration:** Wire up actual session storage (currently accepts mock stores)
2. **Observer Access Control:** Implement permission checking using observer parameter
3. **Crystal Resolver:** Implement remaining resource types (crystal, witness, node)
4. **Frontend Integration:** Create React components for resource-aware rendering
5. **Typeahead:** Implement resource type selection and search

## Files Created

- `/Users/kentgang/git/kgents/impl/claude/services/portal/resolvers/chat.py` (179 lines)
- `/Users/kentgang/git/kgents/impl/claude/services/portal/resolvers/mark.py` (167 lines)
- `/Users/kentgang/git/kgents/impl/claude/services/portal/resolvers/trace.py` (115 lines)
- `/Users/kentgang/git/kgents/impl/claude/services/portal/resolvers/evidence.py` (121 lines)
- `/Users/kentgang/git/kgents/impl/claude/services/portal/resolvers/constitutional.py` (243 lines)

**Total:** ~825 lines of production code implementing 5 resolvers

## Philosophy

> "Every kgents concept is addressable. Every address is expandable."

These resolvers embody the portal system's core insight: resources come to you through expansion, not navigation. Each resolver transforms a URI into an expandable preview with actions, enabling inline exploration of chat history, witness trails, evidence, and constitutional alignment—all without leaving the current context.

---

**Filed:** 2025-12-25  
**Implements:** `spec/protocols/portal-resource-system.md` §V (Part V: Resource Resolvers)
