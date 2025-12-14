---
path: impl/claude/plans/_epilogues/2025-12-14-soul-streaming-cp7
status: complete
progress: 100
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [C20, C21, C22]
session_notes: |
  CP7 Checkpoint achieved: End-to-end streaming from soul to CLI and WebSocket.
phase_ledger:
  PLAN: touched  # C17-C19 scope defined in prior session
  RESEARCH: touched  # soul.py, flux.py, server.py read
  DEVELOP: skipped  # reason: spec already defined contracts
  STRATEGIZE: touched  # C17 → C18 → C19 sequencing
  CROSS-SYNERGIZE: skipped  # reason: single-track implementation
  IMPLEMENT: touched  # core work
  QA: touched  # mypy passed, linter applied
  TEST: touched  # 39 tests passing
  EDUCATE: skipped  # reason: internal implementation
  MEASURE: deferred  # reason: token metrics via FluxEvent.metadata
  REFLECT: touched
entropy:
  planned: 0.10
  spent: 0.05
  returned: 0.05
---

# Epilogue: Soul Streaming CP7 (C17 → C18 → C19)

## Summary

Implemented end-to-end streaming for K-gent Soul dialogue:
1. **C17**: `KgentSoul.dialogue_flux()` now returns `FluxStream[str]` (was `AsyncIterator`)
2. **C18**: Terrarium server WebSocket endpoint `/ws/soul/stream` with rate limiting
3. **C19**: CLI `--stream` flag verified working with new FluxStream return type

## Artifacts Created

| File | Purpose |
|------|---------|
| `agents/k/soul.py:473-617` | `dialogue_flux()` → `FluxStream[str]` |
| `protocols/terrarium/server.py:338-495` | `/ws/soul/stream` WebSocket endpoint |
| `agents/k/_tests/test_soul_dialogue_flux.py` | 19 CP7 verification tests |

## Key Decisions

1. **FluxStream wrapper pattern**: Rather than changing the return type to a complex union, we wrapped the internal generator in `FluxStream` to preserve operator chaining (`.filter()`, `.take()`, `.map()`, `.collect()`)

2. **Rate limiting architecture**: Used closure-captured `active_streams: dict[str, int]` for per-IP rate limiting (default 10, configurable via `KGENT_WS_MAX_STREAMS`)

3. **Mode mapping**: WebSocket accepts lowercase mode strings ("reflect", "challenge", "advise", "explore") and maps to `DialogueMode` enum

## Learnings (One-Line Zettels)

- FluxStream operator chaining requires synchronous method returning new FluxStream, not async
- WebSocket rate limiting by IP address is simple but sufficient for development
- Existing CLI streaming handler (`_handle_streaming_dialogue`) worked without changes after FluxStream refactor

## Risks/Debt

- No authentication on WebSocket endpoint (acceptable for development)
- Rate limiting uses in-memory dict, not persistent (will reset on server restart)
- CLI doesn't distinguish TTY vs non-TTY for fallback behavior

## Metrics

- Tests: 39 passing (19 new + 20 existing)
- Mypy: Clean (strict mode)
- Files changed: 3 (soul.py, server.py, test_soul_dialogue_flux.py)
- Lines added: ~350

## Next Tracks (C20-C22 remaining)

From the original plan, remaining work:
- **C20**: FluxStream.pipe() composition operator
- **C21**: CLI pipe support (`kg soul dialogue --stream | kg transform`)
- **C22**: Full integration tests (WebSocket + CLI + operators)

---

*void.gratitude.tithe. The stream flows.*
