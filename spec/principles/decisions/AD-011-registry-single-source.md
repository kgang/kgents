# AD-011: Registry as Single Source of Truth

**Date**: 2025-12-19

> The AGENTESE registry (`@node` decorator) SHALL be the single source of truth for all paths. Frontend, backend, CLI, and documentation MUST derive from it—never the reverse.

---

## Context

A pattern emerged where frontend code referenced AGENTESE paths that weren't registered in the backend. NavigationTree had paths like `world.town.simulation` and `world.domain` that didn't exist as `@node` registrations. Aliases were proposed as a workaround. This was wrong. Workarounds obscure the underlying model.

## The Discovery

The problem wasn't missing paths—it was that the frontend was making claims the backend couldn't support. The solution isn't to patch the frontend with aliases; it's to enforce strict adherence to the registry.

## Decision

The registry is truth. Everything else adapts.

```
SINGLE SOURCE OF TRUTH

    @node("world.town")           ◄─── This is the ONLY place a path is defined
           │
           ▼
    ┌──────────────────────────────────────────────────────┐
    │              AGENTESE Registry                        │
    │   get_registry().list_paths() → ["world.town", ...]   │
    └──────────────────────────────────────────────────────┘
           │
           ├──────────────► NavigationTree.tsx (MUST match)
           ├──────────────► Cockpit.tsx (MUST match)
           ├──────────────► CLI handlers (MUST match)
           ├──────────────► API routes (auto-generated)
           └──────────────► Documentation (derived)
```

## The Strict Protocol

1. **No aliases**: If a path doesn't exist as `@node`, it doesn't exist. Period.
2. **No workarounds**: Frontend can only reference paths that are registered.
3. **CI validation**: `scripts/validate_path_alignment.py` fails if frontend references unregistered paths.
4. **Warnings are failures**: `logger.warning` for import failures, not `logger.debug`.

## The Validation Script

```bash
cd impl/claude
uv run python scripts/validate_path_alignment.py
```

Output:
```
PASSED: All frontend paths are registered in backend
Backend registry: 39 paths
Frontend references: 17 paths
Valid: 17
```

## Consequences

1. **Frontend is derivative**: NavigationTree, Cockpit, etc. are projections of the registry
2. **Dead links are bugs**: If a frontend path isn't registered, fix the frontend or add the node
3. **No hardcoded paths in frontend**: Use discovery, not static arrays
4. **Import failures surface**: `logger.warning` ensures broken nodes are visible
5. **Registration is the API**: The `@node` decorator is where paths come to life

## The Philosophical Insight

> *"The map must never claim territories that don't exist. When the map diverges from the territory, fix the map—not the territory."*

The registry IS the territory. Frontend paths are claims about that territory. Claims must be verified.

## Anti-patterns

- Aliases that map non-existent paths to existing ones (obscures truth)
- Frontend paths that "will be implemented later" (claims without backing)
- Silent import failures that leave paths unregistered (hidden failures)
- Hardcoded path arrays that drift from registry (source confusion)

## Implementation

See `scripts/validate_path_alignment.py`, `docs/skills/agentese-node-registration.md`

*Zen Principle: The territory doesn't negotiate with the map.*
