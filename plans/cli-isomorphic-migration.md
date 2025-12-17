# CLI Isomorphic Migration Master Plan

**Status**: Active
**Priority**: High
**Progress**: 85%
**Last Updated**: 2025-12-17 (Waves 0-3 + Chat Complete)

---

## Vision

> *"The CLI is not a separate interface. It is a projection of AGENTESE onto the terminal."*

This master plan orchestrates the complete migration of kgents CLI from the current handler-based architecture to the **Isomorphic CLI** vision defined in `spec/protocols/cli.md`. Every CLI command becomes a projection of an AGENTESE path, with behavior derived entirely from aspect metadata.

---

## Gap Analysis: Spec vs Implementation

### What Exists

| Component | Status | Location |
|-----------|--------|----------|
| Hollow Shell (lazy loading) | ✅ Complete | `hollow.py` |
| AGENTESE Router | ✅ Partial | `agentese_router.py` |
| `@aspect` decorator | ✅ Exists | `affordances.py` |
| Effect types | ✅ Defined | `affordances.py` |
| AspectCategory enum | ✅ Complete | `affordances.py` |
| Shortcut expansion | ✅ Working | `shortcuts.py` |
| Legacy command expansion | ✅ Working | `legacy.py` |
| Query system | ✅ Basic | `logos.py` query() |
| Composition (`>>`) | ✅ Working | `logos.py` |

### What's Missing (Spec Gaps) - Updated 2025-12-17

| Spec Section | Gap | Severity |
|--------------|-----|----------|
| **Command Dimensions** | ✅ Complete (Wave 0) - `dimensions.py` | 🟢 Done |
| **CLIProjection functor** | ✅ Complete (Wave 1) - `projection.py` | 🟢 Done |
| **Registration validation** | ✅ Complete (Wave 1) - `validation.py` | 🟢 Done |
| **Dimension-driven UX** | ✅ Complete (Wave 1) - Pre/Post UX handlers | 🟢 Done |
| **Help as affordances** | ✅ Complete (Wave 3) - `help_projector.py`, `completions.py` | 🟢 Done |
| **Chat Protocol** | ✅ Complete (Chat Wave) - 207 chat tests | 🟢 Done |
| **OTEL integration** | Partial - router has it, handlers don't | 🟠 Medium |
| **Sympathetic errors** | Basic error handling exists | 🟠 Medium |
| **Startup < 50ms** | ✅ Achieved via Hollow Shell | 🟢 Done |

### Handler Migration Status - Updated 2025-12-17

Current handlers (44 files) fall into categories:

| Category | Handlers | Status |
|----------|----------|--------|
| **Crown Jewels** | brain, soul | ✅ @aspect coverage + chat (Wave 1 + Chat) |
| **Crown Jewels** | town, atelier, park | ✅ @aspect + chat (Wave 3 + Chat) |
| **Crown Jewels** | gardener | ✅ @aspect coverage (Wave 3) |
| **Forest Protocol** | forest, grow, tend, garden | ✅ Migrated (Wave 2) |
| **Joy Commands** | challenge, oblique, surprise, flinch | ✅ Migrated (Wave 2) |
| **Soul Extensions** | why, tension | ✅ Added to SoulNode (Wave 2) |
| **Query/Subscribe** | query, subscribe | ✅ Via router |
| **DevEx** | debug, trace, ghost | 🟡 Partial OTEL coverage |
| **Bootstrap** | init, wipe, migrate | 🟡 Special cases |

---

## Migration Strategy

### Principle: Progressive Enhancement

1. **Don't break existing CLI** - All commands continue to work
2. **Migrate from inside out** - Start with handlers that already call Logos
3. **Add dimensions incrementally** - Build derivation infrastructure first
4. **Validate via tests** - Each migration wave has verification

### Wave Structure

| Wave | Focus | Duration | Dependencies |
|------|-------|----------|--------------|
| **0** | Dimension System | 2 days | None |
| **1** | Crown Jewels | 3 days | Wave 0 |
| **2** | Forest + Joy | 2 days | Wave 0 |
| **3** | Help/Affordances | 2 days | Waves 1-2 |
| **4** | Observability | 2 days | Waves 1-3 |
| **5** | Cleanup + Validation | 2 days | All |

---

## Child Plans

This master plan coordinates the following child plans:

| Wave | Plan | Duration | Status |
|------|------|----------|--------|
| 0 | [`wave0-dimension-system.md`](cli/wave0-dimension-system.md) | 2 days | ✅ **Complete** |
| 1 | [`wave1-crown-jewels.md`](cli/wave1-crown-jewels.md) | 3 days | ✅ **Complete** |
| 2 | [`wave2-forest-joy.md`](cli/wave2-forest-joy.md) | 2 days | ✅ **Complete** |
| 3 | [`wave3-help-projection.md`](cli/wave3-help-projection.md) | 2 days | ✅ **Complete** |
| 4 | `wave4-observability.md` | 2 days | 🔴 Not created |
| 5 | `wave5-cleanup-validation.md` | 2 days | 🔴 Not created |
| Chat | [`chat-protocol-implementation.md`](cli/chat-protocol-implementation.md) | 10 days | ✅ **Complete** (207 tests) |

**Spec**: [`spec/protocols/chat.md`](../spec/protocols/chat.md) - AGENTESE Chat Protocol

**Total Estimated Duration**: ~13 days | **Actual**: Waves 0-3 + Chat complete, Wave 4-5 remaining

---

## Success Metrics (From Spec §11)

| Metric | Target | Current |
|--------|--------|---------|
| Handlers with full aspect metadata | 100% | **~85%** |
| Behavioral conditionals in handlers | 0 | ~20 (reduced from 50+) |
| Dimension derivation coverage | 100% | **100%** |
| Help text coverage | 100% | **~90%** |
| OTEL trace coverage | 100% | ~30% |
| AI registration validation | All paths pass | ✅ Implemented in `validation.py` |
| Startup time | <50ms | ✅ <50ms |
| CLI tests | — | **581 tests** |

---

## Key Files

### Created ✅
- `impl/claude/protocols/cli/dimensions.py` - Dimension derivation (~477 lines)
- `impl/claude/protocols/cli/projection.py` - CLIProjection functor (~543 lines)
- `impl/claude/protocols/cli/validation.py` - Registration validation (~230 lines)
- `impl/claude/protocols/cli/help_projector.py` - Help projection (~350 lines)
- `impl/claude/protocols/cli/help_renderer.py` - Help rendering (~200 lines)
- `impl/claude/protocols/cli/help_global.py` - Global help (~200 lines)
- `impl/claude/protocols/cli/completions.py` - Shell completions (~350 lines)
- `impl/claude/protocols/cli/chat_projection.py` - Chat REPL (~500 lines)
- `impl/claude/protocols/agentese/chat/` - Full chat module (~2000 lines)
- `impl/claude/protocols/agentese/contexts/self_soul.py` - Soul chat node (~400 lines)
- `impl/claude/protocols/agentese/contexts/town_citizen.py` - Town citizen chat (~200 lines)

### Modified ✅
- `impl/claude/protocols/agentese/affordances.py` - Extended `@aspect` + `@chatty`
- `impl/claude/protocols/cli/hollow.py` - Route through projection + help
- `impl/claude/protocols/cli/handlers/*_thin.py` - 6 Crown Jewel thin handlers

### Test Files ✅
- `impl/claude/protocols/cli/_tests/test_dimensions.py` (59 tests)
- `impl/claude/protocols/cli/_tests/test_projection.py` (21 tests)
- `impl/claude/protocols/cli/_tests/test_validation.py` (40+ tests)
- `impl/claude/protocols/cli/_tests/test_chat_projection.py` (68 tests)
- `impl/claude/protocols/cli/_tests/test_help_projection.py` (17 tests)
- `impl/claude/protocols/agentese/chat/_tests/*` (207 chat tests)

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing commands | Feature flags, progressive rollout |
| Performance regression | Benchmark each wave |
| Incomplete aspect metadata | Validation at registration |
| Test coverage gaps | Require tests before merge |

---

## Next Actions

1. [x] ~~Create child plans (Wave 0-5)~~ - Waves 0-3 + Chat created
2. [x] ~~Implement dimension derivation system (Wave 0)~~ - Complete
3. [x] ~~Migrate first Crown Jewel (brain) as proof-of-concept~~ - Complete
4. [x] ~~Establish migration checklist template~~ - In wave1-crown-jewels.md
5. [ ] Wave 4: OTEL observability - spans in all handlers
6. [ ] Wave 5: Cleanup + final validation pass
7. [ ] Remaining ~15% handler migration (DevEx, Bootstrap)

---

## Completion Summary (2025-12-17)

| Wave | Status | Tests | Key Deliverables |
|------|--------|-------|------------------|
| Wave 0 | ✅ Complete | 85 | `dimensions.py`, `validation.py`, 6-dimensional command space |
| Wave 1 | ✅ Complete | 532 | `projection.py`, Crown Jewel @aspect coverage |
| Wave 2 | ✅ Complete | — | Forest, Joy, Soul extensions in AGENTESE nodes |
| Wave 3 | ✅ Complete | 17 | `help_projector.py`, `completions.py`, global help |
| Chat | ✅ Complete | 207 | Chat protocol, persistence, observability, REPL |
| Wave 4 | 🔴 Pending | — | OTEL spans in handlers |
| Wave 5 | 🔴 Pending | — | Cleanup, final validation |

**Total CLI Tests**: 581

---

*This is a Forest Protocol plan. Last major update: 2025-12-17.*
