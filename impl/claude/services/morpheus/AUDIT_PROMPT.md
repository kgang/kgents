# Morpheus Metaphysical Fullstack Audit Prompt

Use this prompt to audit the Morpheus implementation, ensure ecosystem alignment, and write the formal spec.

---

## Audit Prompt

```
You are auditing the Morpheus Crown Jewel implementation in kgents. Morpheus was transformed from an infrastructure router (infra/morpheus/) to a Metaphysical Fullstack Agent (services/morpheus/).

## Context

Read these files to understand the implementation:
- services/morpheus/__init__.py
- services/morpheus/node.py
- services/morpheus/persistence.py
- services/morpheus/gateway.py
- services/morpheus/types.py
- services/morpheus/adapters/

Read these files to understand kgents patterns:
- spec/principles.md
- spec/protocols/agentese.md
- docs/skills/metaphysical-fullstack.md
- docs/skills/crown-jewel-patterns.md
- services/brain/node.py (reference implementation)

## Audit Tasks

### 1. Pattern Compliance Audit

Check that Morpheus follows the Metaphysical Fullstack pattern (AD-009):

- [ ] Node uses @node decorator with correct path ("world.morpheus")
- [ ] Node inherits from BaseLogosNode
- [ ] All aspects use @aspect decorator with correct categories
- [ ] Persistence layer owns domain semantics (WHEN/WHY)
- [ ] Gateway is transport-agnostic (no HTTP coupling)
- [ ] Observer-dependent affordances implemented correctly
- [ ] Renderable types implement to_dict() and to_text()

### 2. AGENTESE Integration Audit

Verify proper AGENTESE integration:

- [ ] Node registered in NodeRegistry (check with get_registry().has("world.morpheus"))
- [ ] All aspects follow verb-first naming (manifest, complete, stream, providers)
- [ ] Effect types correct (PERCEPTION for reads, MUTATION for writes)
- [ ] Observer/Umwelt handling follows existing patterns
- [ ] Auto-exposure via AgenteseGateway works

### 3. Ecosystem Alignment Audit

Check alignment with other Crown Jewels:

- [ ] Import patterns match (services.X import style)
- [ ] Bootstrap integration correct (morpheus_persistence in ServiceRegistry)
- [ ] No circular dependencies
- [ ] Test patterns match other services (_tests/ directory, pytest-asyncio)
- [ ] Docstrings follow project conventions

### 4. Missing Features Audit

Identify gaps:

- [ ] Streaming support (world.morpheus.stream) - implemented?
- [ ] Telemetry integration (spans, metrics) - wired?
- [ ] Rate limiting - implemented?
- [ ] Multiple provider support beyond ClaudeCLI
- [ ] Effect composition (lens() method)

### 5. Spec Writing

After auditing, write `spec/infrastructure/morpheus.md` following spec/spec-template.md structure:

1. Purpose (1 paragraph)
2. Categorical Foundation (PolyAgent, Operad if applicable)
3. AGENTESE Paths (table of world.morpheus.*)
4. Observer-Dependent Behavior (archetype affordance matrix)
5. Integration Points (with other Crown Jewels)
6. Implementation Notes (key design decisions)
7. Future Work (streaming, telemetry, additional adapters)

## Deliverables

1. Audit report with checkboxes filled
2. List of issues found (if any)
3. Suggested fixes for issues
4. Complete spec file at spec/infrastructure/morpheus.md
5. Any necessary code fixes

## Success Criteria

- All pattern compliance checks pass
- AGENTESE integration verified working
- No ecosystem misalignment
- Spec written and matches implementation
- Tests pass (uv run pytest services/morpheus/_tests/ -v)
```

---

## Quick Verification Commands

```bash
# Verify tests pass
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest services/morpheus/_tests/ -v

# Verify node registration
uv run python -c "
from protocols.agentese.registry import get_registry
import services.morpheus  # trigger registration
print('Registered:', get_registry().has('world.morpheus'))
print('All paths:', get_registry().list_paths())
"

# Verify imports work
uv run python -c "
from services.morpheus import (
    MorpheusNode,
    MorpheusPersistence,
    MorpheusGateway,
    ChatRequest,
    ChatResponse,
)
print('All imports successful')
"

# Verify bootstrap integration
uv run python -c "
from services.bootstrap import ServiceRegistry
r = ServiceRegistry()
print('morpheus_persistence' in r.list_services())
"
```

---

## Known Implementation Decisions

1. **No database tables**: Morpheus doesn't persist state to SQLAlchemy - it's a stateless gateway
2. **Gateway owns routing**: MorpheusGateway handles model→provider routing
3. **Persistence owns semantics**: MorpheusPersistence adds timing, result types
4. **Node owns access control**: MorpheusNode filters based on observer archetype
5. **307 redirect**: Legacy /v1/chat/completions redirects to preserve POST body
