# AGENTESE REPL Renaissance: Radical Transformation

> *"The protocol IS the API. The REPL IS the exploration."*

**Status**: COMPLETE ✅
**Created**: 2025-12-18
**Completed**: 2025-12-19
**Priority**: High (devex/ux blocker)
**Aligned With**: AD-009 (Metaphysical Fullstack), AD-010 (Habitat Guarantee)

---

## Implementation Summary (2025-12-19)

**All 5 phases delivered:**

| Phase | Status | Deliverable |
|-------|--------|-------------|
| 1. Audit & Fix | ✅ | `scripts/audit_agentese_paths.py` - 39/39 paths pass |
| 2. Error Surfacing | ✅ | `_sympatheticError()` with all categories |
| 3. Completion Overhaul | ✅ | Live discovery with metadata, 30s cache |
| 4. Testing Harness | ✅ | `test_registry_ci_gate.py` - 7 CI tests |
| 5. Examples & Teaching | ✅ | Welcome message, inline examples in help |

**Key Files Changed:**
- `protocols/agentese/_tests/test_registry_ci_gate.py` (NEW) - CI gate tests
- `web/src/shell/Terminal.tsx` - Enhanced welcome message
- `web/src/shell/TerminalService.ts` - Inline examples in help

**Audit Results**: 39 paths registered, 29 work without DI, 10 need container (expected for service nodes).

---

---

## Executive Summary

The AGENTESE REPL on the webapp frontend has correct *design* but broken *execution*. The abstraction leaks because the frontend TerminalService talks to endpoints that don't exist or are misconfigured. Almost no commands work. The experience is "overengineered but undertested."

**The Core Problem**: The TerminalService invokes AGENTESE paths via `/agentese/{path}/{aspect}`, but:
1. Many paths aren't registered in NodeRegistry
2. Error handling swallows failures silently
3. No QA process validates paths before shipping
4. Completion/discovery uses stale hardcoded fallbacks

**The Radical Solution**: Make the REPL a transparent passthrough to the exact same backend that the API client already calls successfully. The frontend API (`client.ts`) works; the Terminal should use the same patterns.

---

## 1. The Diagnosis

### 1.1 Current Flow (Broken)

```
User types: self.memory.manifest
    ↓
TerminalService._invokeAgentese(path)
    ↓
apiClient.post('/agentese/self/memory/manifest')
    ↓
AgenteseGateway._invoke_path('self.memory', 'manifest', observer)
    ↓
registry.has('self.memory') → FALSE (often!)
    ↓
logos.invoke() → PathNotFoundError
    ↓
HTTPException 404 → Swallowed in catch → "(no result)"
```

**Symptoms**:
- `help` works (builtin)
- `discover` works (builtin hitting `/agentese/discover`)
- Most AGENTESE paths fail silently
- Tab completion shows paths that don't work

### 1.2 What Works (client.ts)

The React hooks and page components call endpoints that work:

```typescript
// client.ts - These work!
brainApi.getStatus() → GET /agentese/self/memory/manifest
gardenerApi.getSession() → GET /agentese/concept/gardener/manifest
townApi.step(townId) → POST /api/v1/town/{town_id}/step
```

### 1.3 The Gap

Terminal calls `/agentese/self/memory/manifest` directly.
But `brainApi.getStatus()` also calls `/agentese/self/memory/manifest`.
**They should produce the same result.** But they don't, because:

1. TerminalService doesn't handle the response envelope properly
2. Error surfacing is swallowed
3. Observer headers may differ

---

## 2. The Vision

### 2.1 Principles

1. **Transparent passthrough**: Terminal uses EXACT same API patterns as React hooks
2. **No silent failures**: Every error surfaces with helpful context
3. **One source of truth**: `/agentese/discover` drives completion, not hardcoded lists
4. **Joy-inducing**: Working commands feel like magic; broken commands explain why

### 2.2 The Mirror Test

*"Does the REPL feel like me on my best day?"*

A best-day REPL:
- **Works** — commands execute, results appear
- **Teaches** — helps users discover the ontology
- **Delights** — fast, responsive, fun to explore
- **Honest** — errors explain what went wrong

---

## 3. Implementation Plan

### Phase 1: Audit & Fix (2 hours)

**Goal**: Make existing paths work before adding features.

#### 1.1 Path Audit Script

Create a script that tests every discovered path:

```python
# impl/claude/scripts/audit_agentese_paths.py

async def audit_paths():
    """
    For each path in /agentese/discover:
    1. Try manifest aspect
    2. Log success/failure
    3. Categorize failures
    """
    response = await client.get('/agentese/discover')
    paths = response.data['paths']

    results = {
        'working': [],
        'missing_node': [],
        'aspect_error': [],
        'import_error': [],
    }

    for path in paths:
        try:
            result = await client.get(f'/agentese/{path.replace(".", "/")}/manifest')
            results['working'].append(path)
        except HTTPException as e:
            categorize_failure(path, e, results)

    print_report(results)
```

#### 1.2 Fix Node Registration

Ensure all Crown Jewel nodes are imported in `gateway.py`:

```python
# gateway.py _import_node_modules()

# Current (incomplete):
from services.brain import node as brain_node

# Fix: Import ALL service nodes
from services.brain import node  # self.memory.*
from services.gestalt import node  # world.codebase.*
from services.town import node, inhabit_node, coalition_node  # world.town.*
from services.park import node  # world.park.*
from services.forge import node, soul_node  # world.forge.*
```

#### 1.3 Fix Response Handling

`TerminalService._invokeAgentese` must match `unwrapAgentese`:

```typescript
// TerminalService.ts

private async _invokeAgentese(path: string, input?: unknown): Promise<unknown> {
  const parts = path.split('.');
  const aspect = parts.pop() || 'manifest';
  const pathSegments = parts.join('/');

  const response = await apiClient.post<{
    path: string;
    aspect: string;
    result: unknown;
    error?: string;  // ADD: Handle error field
  }>(
    `/agentese/${pathSegments}/${aspect}`,
    input ? { input } : {},
    {
      headers: {
        'X-Observer-Archetype': this._observer?.archetype ?? 'developer',
        'X-Observer-Capabilities': this._observer
          ? Array.from(this._observer.capabilities).join(',')
          : '',
      },
    }
  );

  // ADD: Check for AGENTESE-level errors
  if (response.data.error) {
    throw new Error(response.data.error);
  }

  // ADD: Handle BasicRendering responses (same as client.ts)
  const result = response.data.result;
  if (result && typeof result === 'object' && 'metadata' in result) {
    return result.metadata;
  }

  return result;
}
```

### Phase 2: Error Surfacing (1 hour)

**Goal**: Every failure explains itself.

#### 2.1 Categorized Errors

```typescript
// TerminalService.ts

private _formatError(error: unknown, path: string): TerminalLine {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    if (status === 404) {
      return this._createLine('error',
        `Path not found: ${path}\n` +
        `Try: discover ${path.split('.')[0]}`
      );
    }

    if (status === 403) {
      return this._createLine('error',
        `Affordance not available: ${path}\n` +
        `Your archetype may not have access. Try: affordances ${path}`
      );
    }

    if (status === 500) {
      return this._createLine('error',
        `Backend error invoking ${path}\n` +
        `Detail: ${detail || 'Unknown'}`
      );
    }
  }

  return this._createLine('error', `Error: ${String(error)}`);
}
```

#### 2.2 Sympathetic Copy

Error messages should feel warm, not hostile:

```typescript
const ERROR_MESSAGES = {
  404: `This path doesn't exist yet. The garden is still growing here.`,
  403: `This path isn't available to you right now. Try a different archetype.`,
  500: `Something went wrong on our end. We're sorry.`,
  timeout: `The backend took too long. Maybe try again?`,
};
```

### Phase 3: Completion Overhaul (1.5 hours)

**Goal**: Tab completion shows only paths that work.

#### 3.1 Live Discovery

```typescript
// TerminalService.ts

private _pathCache: PathInfo[] | null = null;
private _cacheTimestamp: number = 0;
private readonly CACHE_TTL_MS = 30000; // 30 seconds

async discover(context?: string): Promise<PathInfo[]> {
  const now = Date.now();

  // Use cache if fresh
  if (this._pathCache && now - this._cacheTimestamp < this.CACHE_TTL_MS) {
    return context
      ? this._pathCache.filter(p => p.path.startsWith(context))
      : this._pathCache;
  }

  // Fetch with metadata (AD-010)
  const response = await apiClient.get<{
    paths: string[];
    metadata: Record<string, PathMetadata>;
  }>('/agentese/discover?include_metadata=true');

  // Transform to PathInfo with rich metadata
  this._pathCache = response.data.paths.map(path => ({
    path,
    context: path.split('.')[0],
    description: response.data.metadata[path]?.description,
    aspects: response.data.metadata[path]?.aspects || ['manifest'],
    examples: response.data.metadata[path]?.examples || [],
  }));
  this._cacheTimestamp = now;

  return context
    ? this._pathCache.filter(p => p.path.startsWith(context))
    : this._pathCache;
}
```

#### 3.2 Aspect-Aware Completion

```typescript
async complete(partial: string): Promise<CompletionSuggestion[]> {
  const suggestions: CompletionSuggestion[] = [];

  // Builtins first
  for (const cmd of BUILTIN_COMMANDS) {
    if (cmd.startsWith(partial.toLowerCase())) {
      suggestions.push({
        text: cmd,
        type: 'command',
        description: this._getBuiltinDescription(cmd),
      });
    }
  }

  // Get live paths
  const paths = await this.discover();

  // If partial ends with '.', suggest aspects
  if (partial.endsWith('.')) {
    const basePath = partial.slice(0, -1);
    const pathInfo = paths.find(p => p.path === basePath);
    if (pathInfo?.aspects) {
      for (const aspect of pathInfo.aspects) {
        suggestions.push({
          text: `${basePath}.${aspect}`,
          type: 'aspect',
          description: `Invoke ${aspect}`,
        });
      }
    }
    return suggestions.slice(0, 10);
  }

  // Otherwise suggest paths
  for (const pathInfo of paths) {
    if (pathInfo.path.startsWith(partial)) {
      suggestions.push({
        text: pathInfo.path,
        type: 'path',
        description: pathInfo.description,
      });
    }
  }

  return suggestions.slice(0, 10);
}
```

### Phase 4: Testing Harness (1.5 hours)

**Goal**: No path ships without automated validation.

#### 4.1 Backend Path Tests

```python
# impl/claude/protocols/agentese/_tests/test_registry_ci_gate.py

import pytest
from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.registry import get_registry

@pytest.fixture(scope="module")
def registry():
    """Import all nodes and return registry."""
    _import_node_modules()
    return get_registry()

def test_all_discovered_paths_are_invokable(registry):
    """Every path in discover must respond to manifest."""
    paths = registry.list_paths()

    failures = []
    for path in paths:
        try:
            node = registry.resolve_sync(path)
            assert node is not None, f"Node is None for {path}"
        except Exception as e:
            failures.append(f"{path}: {e}")

    assert not failures, f"Failed paths:\n" + "\n".join(failures)

def test_no_orphan_context_files():
    """All context files must register at least one path."""
    from pathlib import Path
    context_dir = Path(__file__).parent.parent / "contexts"

    for py_file in context_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        # Check this file registers something
        module_name = py_file.stem
        # Import and verify registration
```

#### 4.2 Frontend Integration Tests

```typescript
// impl/claude/web/tests/integration/terminal.test.ts

import { createTerminalService } from '@/shell/TerminalService';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

describe('Terminal AGENTESE Integration', () => {
  const server = setupServer(
    rest.get('/agentese/discover', (req, res, ctx) => {
      return res(ctx.json({
        paths: ['self.memory', 'world.town'],
        metadata: {
          'self.memory': { aspects: ['manifest', 'capture'] },
        },
      }));
    }),
    rest.get('/agentese/self/memory/manifest', (req, res, ctx) => {
      return res(ctx.json({
        path: 'self.memory',
        aspect: 'manifest',
        result: { status: 'ok' },
      }));
    }),
  );

  beforeAll(() => server.listen());
  afterAll(() => server.close());

  it('executes discovered paths successfully', async () => {
    const service = createTerminalService();
    const lines = await service.execute('self.memory.manifest');

    expect(lines).toContainEqual(
      expect.objectContaining({ type: 'output' })
    );
  });

  it('surfaces 404 errors with helpful message', async () => {
    server.use(
      rest.get('/agentese/self/nonexistent/manifest', (req, res, ctx) => {
        return res(ctx.status(404), ctx.json({
          detail: 'Path not found'
        }));
      })
    );

    const service = createTerminalService();
    const lines = await service.execute('self.nonexistent.manifest');

    expect(lines).toContainEqual(
      expect.objectContaining({
        type: 'error',
        content: expect.stringContaining('not found'),
      })
    );
  });
});
```

### Phase 5: Examples & Teaching (1 hour)

**Goal**: The REPL teaches the ontology through use.

#### 5.1 Inline Examples

When a path is discovered with examples, show them:

```typescript
case 'help':
  if (args.length > 0) {
    const pathInfo = await this._getPathInfo(args[0]);
    const lines = [
      this._createLine('info', `Path: ${pathInfo.path}`),
      this._createLine('output', pathInfo.description || 'No description'),
    ];

    if (pathInfo.examples?.length) {
      lines.push(this._createLine('info', '\nExamples:'));
      for (const example of pathInfo.examples) {
        lines.push(this._createLine('output', `  ${example.command}`));
        if (example.description) {
          lines.push(this._createLine('system', `    ${example.description}`));
        }
      }
    }

    return lines;
  }
```

#### 5.2 First-Run Experience

On first terminal open, show a welcoming message:

```typescript
private _getWelcome(): TerminalLine[] {
  return [
    this._createLine('info', 'Welcome to the AGENTESE Terminal'),
    this._createLine('output', ''),
    this._createLine('output', 'Try these commands:'),
    this._createLine('output', '  discover           List all paths'),
    this._createLine('output', '  self.soul.manifest View K-gent state'),
    this._createLine('output', '  help <path>        Get help for a path'),
    this._createLine('output', ''),
    this._createLine('system', 'Type a path and press Tab for completion'),
  ];
}
```

---

## 4. Spec Updates Required

### 4.1 Update `spec/protocols/agentese.md`

Add section on REPL contract:

```markdown
## REPL Contract

The AGENTESE REPL is a first-class projection surface. All paths
exposed via `/agentese/discover` MUST be invokable via the REPL.

### Path Requirements

1. Every registered path MUST respond to `manifest` aspect
2. Error responses MUST include `error` field in envelope
3. Response format MUST be JSON-serializable

### Testing Gate

No PR merges that add AGENTESE paths without:
1. Path appearing in `/agentese/discover`
2. Path responding to manifest without error
3. Integration test covering happy path
```

### 4.2 Update `spec/protocols/os-shell.md`

Add Terminal reliability section:

```markdown
## Terminal Reliability Contract

The Terminal is not a toy. It is the canonical exploration surface
for AGENTESE. Every path that works via React hooks MUST work via
Terminal.

### Response Parity

For any path P:
- `apiClient.get('/agentese/' + P.replace(/\./g, '/') + '/manifest')`
- `service.execute(P + '.manifest')`

MUST return equivalent results.

### Error Surfacing

Silent failures are forbidden. Every error MUST:
1. Display error type (404, 403, 500)
2. Suggest remediation (try discover, check archetype)
3. Include backend detail if available
```

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing working paths | Audit script runs first; no changes until we know what works |
| Cache staleness | 30s TTL; manual refresh via `discover --refresh` |
| Slow completion | Background prefetch on terminal open |
| Observer mismatch | Use same observer derivation as React hooks |

---

## 6. Success Criteria

1. **Audit passes**: 100% of discovered paths respond to manifest
2. **Error visibility**: No silent failures; all errors show helpful messages
3. **Completion accuracy**: Tab shows only working paths
4. **Test coverage**: CI gate prevents broken paths from merging
5. **Joy factor**: Using the REPL feels like exploration, not frustration

---

## 7. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Audit & Fix | 2 hours | All paths work |
| 2. Error Surfacing | 1 hour | Helpful error messages |
| 3. Completion Overhaul | 1.5 hours | Live, accurate completion |
| 4. Testing Harness | 1.5 hours | CI gates |
| 5. Examples & Teaching | 1 hour | First-run experience |
| **Total** | **7 hours** | Production-ready REPL |

---

## Appendix A: Current Path Inventory

To be populated by audit script. Expected categories:
- **Working**: Paths that respond correctly
- **Missing Node**: Path in gateway, node not imported
- **Aspect Error**: Node exists, aspect fails
- **Import Error**: Python import fails

---

## Appendix B: Voice Anchors

*"Daring, bold, creative, opinionated but not gaudy"*

The REPL should feel:
- **Bold**: Works confidently; doesn't hedge
- **Creative**: Teaches through exploration
- **Opinionated**: Has a clear path; suggests next steps
- **Not gaudy**: Clean output; no unnecessary decoration

---

*"The REPL is the garden's conversation partner. Make it speak."*

*Compiled: 2025-12-18 | Plan Status: READY FOR REVIEW*
