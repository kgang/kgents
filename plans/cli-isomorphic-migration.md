# CLI Isomorphic Migration Master Plan

**Status**: Active
**Priority**: High
**Progress**: 15%
**Last Updated**: 2025-12-17

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

### What's Missing (Spec Gaps)

| Spec Section | Gap | Severity |
|--------------|-----|----------|
| **Command Dimensions** | No dimension derivation from aspects | 🔴 Critical |
| **CLIProjection functor** | Missing - handlers bypass Logos | 🔴 Critical |
| **Registration validation** | No validation of aspect completeness | 🟡 High |
| **Dimension-driven UX** | Scattered conditionals remain | 🟡 High |
| **Help as affordances** | Separate help system, not projection | 🟡 High |
| **OTEL integration** | Partial - router has it, handlers don't | 🟠 Medium |
| **Sympathetic errors** | Basic error handling exists | 🟠 Medium |
| **Startup < 50ms** | ✅ Achieved via Hollow Shell | 🟢 Done |

### Handler Migration Status

Current handlers (44 files) fall into categories:

| Category | Handlers | Status |
|----------|----------|--------|
| **Crown Jewels** | brain, soul, town, atelier | 🔴 Not migrated |
| **Forest Protocol** | forest, grow, tend, garden | 🟡 Partially migrated |
| **Joy Commands** | challenge, oblique, surprise | 🔴 Not migrated |
| **Soul Extensions** | why, tension, flinch | 🔴 Not migrated |
| **Query/Subscribe** | query, subscribe | 🟡 Via router |
| **DevEx** | debug, trace, ghost | 🔴 Not migrated |
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
| 0 | [`wave0-dimension-system.md`](cli/wave0-dimension-system.md) | 2 days | 🔴 Not started |
| 1 | [`wave1-crown-jewels.md`](cli/wave1-crown-jewels.md) | 3 days | 🔴 Not started |
| 2 | [`wave2-forest-joy.md`](cli/wave2-forest-joy.md) | 2 days | 🔴 Not started |
| 3 | [`wave3-help-projection.md`](cli/wave3-help-projection.md) | 2 days | 🔴 Not started |
| 4 | [`wave4-observability.md`](cli/wave4-observability.md) | 2 days | 🔴 Not started |

**Total Estimated Duration**: ~11 days (can parallelize some work)

---

## Success Metrics (From Spec §11)

| Metric | Target | Current |
|--------|--------|---------|
| Handlers with full aspect metadata | 100% | ~5% |
| Behavioral conditionals in handlers | 0 | ~50+ |
| Dimension derivation coverage | 100% | 0% |
| Help text coverage | 100% | ~60% |
| OTEL trace coverage | 100% | ~10% |
| AI registration validation | All paths pass | Not implemented |
| Startup time | <50ms | ✅ <50ms |

---

## Key Files

### To Create
- `impl/claude/protocols/cli/dimensions.py` - Dimension derivation
- `impl/claude/protocols/cli/projection.py` - CLIProjection functor
- `impl/claude/protocols/cli/validation.py` - Registration validation

### To Modify
- `impl/claude/protocols/agentese/affordances.py` - Extend `@aspect`
- `impl/claude/protocols/cli/hollow.py` - Route through projection
- `impl/claude/protocols/cli/handlers/*.py` - All 44 handlers

### Test Files
- `impl/claude/protocols/cli/_tests/test_dimensions.py`
- `impl/claude/protocols/cli/_tests/test_projection.py`
- `impl/claude/protocols/cli/_tests/test_isomorphism.py`

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

1. [ ] Create child plans (Wave 0-5)
2. [ ] Implement dimension derivation system (Wave 0)
3. [ ] Migrate first Crown Jewel (brain) as proof-of-concept
4. [ ] Establish migration checklist template

---

*This is a Forest Protocol plan. Update progress as waves complete.*
