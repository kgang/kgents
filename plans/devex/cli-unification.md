---
path: plans/devex/cli-unification
status: active
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [agent-town-cli, k-gent-ambient, unified-streaming]
session_notes: |
  CLI has grown organically to 17,967 lines across 40+ handlers.
  soul.py alone is 2019 lines. Time to unify, simplify, and refactor.
  Crown Jewel: Full 11-phase ceremony.
phase_ledger:
  PLAN: pending
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.00
  returned: 0.00
---

# CLI Unification: Simplify, Refactor, Unify

> *"The CLI is the soul's voice. It should be as clear as the soul itself."*

**Trigger**: K-Terrarium LLM Agents complete — revealed CLI sprawl (2019-line soul.py).
**Process**: Full 11-phase ceremony (AD-005) — architectural refactor.
**North Star**: A CLI that composes like agents compose.

---

## Current State (The Problem)

### Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total handler lines | 17,967 | < 8,000 |
| Largest handler (soul.py) | 2,019 | < 300 |
| Number of handlers | 40+ | ~15 command groups |
| Streaming implementations | 4+ variants | 1 unified |
| Context handling patterns | 6+ variants | 1 unified |

### Symptoms

1. **Monolithic handlers**: soul.py has 20+ subcommands
2. **Inconsistent async**: Some handlers use `asyncio.run()`, some are sync
3. **Duplicated infrastructure**: JSON output formatting repeated everywhere
4. **Streaming variants**: `--stream`, `--pipe`, `--json` each implemented differently
5. **No composition**: Can't easily `kgents soul reflect | kgents soul challenge`
6. **Testing friction**: Large files = slow test cycles

### File Size Analysis

```
2019  soul.py          # Largest — needs breaking up
1110  a_gent.py        # Large — many subcommands
 892  turns.py         # Medium — could be smaller
 842  infra.py         # Medium — K8s operations
 674  trace.py         # Medium
 664  status.py        # Medium
 606  telemetry.py     # Medium
 573  flinch.py        # Medium
...
Total: 17,967 lines
```

---

## North Star & Design Principles

### The Unified CLI Vision

```bash
# Every command follows the same pattern:
kgents <noun> <verb> [args] [--flags]

# Every command supports:
--json           # Structured output (default for pipes)
--stream         # Token/chunk streaming
--quiet          # Minimal output
--context <id>   # Session context

# Commands compose via Unix pipes:
kgents soul reflect "question" | kgents soul challenge | kgents soul advise

# Or via explicit pipelines:
kgents flow run reflect >> challenge >> advise
```

### Design Principles

1. **One file per command** — `soul/reflect.py`, `soul/challenge.py`, not monolith
2. **Shared infrastructure** — Context, output, streaming in `cli/shared/`
3. **Composition-first** — Every command is a pipeline stage
4. **Auto-detect pipes** — NDJSON when stdout is not a tty
5. **Progressive disclosure** — Simple usage, advanced via flags

---

## Architecture

### Directory Structure (Target)

```
impl/claude/protocols/cli/
├── hollow.py                    # Entry point (stays small)
├── shared/
│   ├── context.py               # InvocationContext, session handling
│   ├── output.py                # OutputFormatter (json/text/stream)
│   ├── streaming.py             # Unified streaming infrastructure
│   ├── pipe.py                  # Pipe detection, NDJSON I/O
│   └── decorators.py            # @async_handler, @streaming_handler
├── commands/
│   ├── soul/
│   │   ├── __init__.py          # `kgents soul` entry
│   │   ├── reflect.py           # `kgents soul reflect`
│   │   ├── challenge.py         # `kgents soul challenge`
│   │   ├── advise.py            # `kgents soul advise`
│   │   ├── explore.py           # `kgents soul explore`
│   │   ├── status.py            # `kgents soul status`
│   │   ├── vibe.py              # `kgents soul vibe`
│   │   └── stream.py            # `kgents soul stream` (live)
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── list.py
│   │   ├── run.py
│   │   └── status.py
│   ├── flow/                    # Pipeline composition
│   ├── observe/                 # Terrarium TUI
│   ├── infra/                   # K8s operations
│   └── dev/                     # Developer tools
└── handlers/                    # Legacy (migrate from)
```

### Shared Infrastructure

#### 1. OutputFormatter

```python
class OutputFormatter:
    """Unified output handling for all CLI commands."""

    def __init__(self, json_mode: bool, stream_mode: bool, pipe_mode: bool):
        self.json_mode = json_mode or self._is_pipe()
        self.stream_mode = stream_mode
        self.pipe_mode = pipe_mode

    def emit(self, text: str, data: dict | None = None) -> None:
        """Emit output in appropriate format."""
        if self.json_mode:
            print(json.dumps(data or {"text": text}), flush=True)
        else:
            print(text)

    def stream_chunk(self, chunk: str, index: int) -> None:
        """Emit a streaming chunk."""
        if self.pipe_mode:
            print(json.dumps({"type": "chunk", "index": index, "data": chunk}))
        else:
            sys.stdout.write(chunk)
            sys.stdout.flush()
```

#### 2. Command Decorators

```python
@async_handler
async def reflect(args: list[str], ctx: InvocationContext) -> int:
    """Handle soul reflect command."""
    ...

@streaming_handler
async def stream_reflect(args: list[str], ctx: InvocationContext) -> AsyncIterator[str]:
    """Handle soul reflect with streaming."""
    ...
```

#### 3. Pipe Composition

```python
class PipeReader:
    """Read NDJSON from stdin when piped."""

    @classmethod
    def read_input(cls) -> str | None:
        """Read and parse piped input."""
        if sys.stdin.isatty():
            return None
        return sys.stdin.read().strip()

    @classmethod
    def read_stream(cls) -> Iterator[dict]:
        """Read NDJSON stream from stdin."""
        for line in sys.stdin:
            yield json.loads(line.strip())
```

---

## Implementation Phases

### Phase 1: Shared Infrastructure (Foundation)

**Deliverables**:
- `cli/shared/context.py` — Unified InvocationContext
- `cli/shared/output.py` — OutputFormatter
- `cli/shared/streaming.py` — StreamingHandler
- `cli/shared/pipe.py` — PipeReader/PipeWriter

**Exit Criterion**: One handler migrated using new infrastructure.

### Phase 2: Soul Command Refactor

**Deliverables**:
- Break `soul.py` (2019 lines) into `commands/soul/` (10+ files)
- Each dialogue mode is its own command file
- Shared streaming extracted to `streaming.py`

**Target**: Each file < 300 lines.

### Phase 3: Agent Command Refactor

**Deliverables**:
- Break `a_gent.py` (1110 lines) into `commands/agent/`
- Unified agent lifecycle management
- Composition with flow engine

### Phase 4: Infra & DevEx Consolidation

**Deliverables**:
- Consolidate `infra.py`, `daemon.py`, `telemetry.py` → `commands/infra/`
- Consolidate `flinch.py`, `trace.py`, `status.py` → `commands/dev/`
- Reduce duplication

### Phase 5: Flow Composition

**Deliverables**:
- `commands/flow/` — Pipeline composition engine
- `kgents flow run X >> Y >> Z` syntax
- Automatic pipe detection and NDJSON handling

### Phase 6: Testing & Polish

**Deliverables**:
- Test coverage for all new command structure
- Migration guide for old patterns
- Updated help text and examples

---

## Cross-Synergies

| Project | Integration Point |
|---------|------------------|
| **K-gent Soul** | Unified streaming for dialogue modes |
| **Agent Town** | CLI as agent control plane |
| **Terrarium Dashboard** | CLI observability via `observe` |
| **HotData** | Demo fixtures use CLI commands |
| **N-Phase Cycle** | CLI commands for phase transitions |

---

## Success Criteria

| Criterion | Measure |
|-----------|---------|
| **Size reduction** | Total lines < 8,000 (55% reduction) |
| **No file > 300 lines** | Largest handler < 300 lines |
| **Unified streaming** | One implementation, many commands |
| **Pipe composition** | `kgents X | kgents Y` works for all |
| **Tests pass** | All existing tests still pass |
| **Zero regressions** | All commands work as before |

---

## Non-Goals

- **New features**: This is refactor, not feature work
- **Breaking changes**: Existing commands must work
- **API redesign**: Keep `kgents <noun> <verb>` pattern
- **Performance optimization**: Focus on structure first

---

## Attention Budget

| Activity | Budget |
|----------|--------|
| Infrastructure design | 15% |
| Soul refactor | 30% |
| Agent refactor | 20% |
| Infra/DevEx consolidation | 15% |
| Flow composition | 10% |
| Testing & polish | 10% |

---

## References

- `plans/skills/cli-command.md` — CLI command patterns
- `plans/skills/n-phase-cycle/README.md` — Process discipline
- `plans/_archive/cli-hollowing-v1.0-complete.md` — Previous CLI work
- `impl/claude/plans/_epilogues/2025-12-14-k-terrarium-llm-agents-complete.md` — Trigger

---

*"Compose commands like you compose agents: lawfully, joyfully, and with minimal ceremony."*
