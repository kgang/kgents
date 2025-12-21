# DI Enlightened Resolution: Required vs Optional Dependencies

> *"The signature already contains the wisdom; the container should listen."*

**Created**: 2025-12-21
**Status**: APPROVED
**Sessions**: 3 (can parallelize 2+3)
**Risk**: Medium (changes core DI behavior)

---

## The Problem

Silent skip on missing dependencies causes:
1. Delayed `TypeError: NoneType has no attribute X` far from root cause
2. Debugging nightmare with no hint about DI
3. False confidence in tests that pass with partial deps

Current mitigation (`AGENTESE_STRICT=1`) is opt-in and forgotten.

## The Insight

Python's signature **already expresses** required vs optional:

```python
def __init__(self, brain: BrainPersistence):              # REQUIRED
def __init__(self, brain: BrainPersistence | None = None): # OPTIONAL
```

The container should respect this, not invent a parallel "strict mode" system.

---

## Session 1: Core Container Change

**Goal**: Make `create_node` respect required vs optional from signature.

**Files**:
- `protocols/agentese/container.py` (~50 lines changed)

**Changes**:

```python
# 1. Update _inspect_dependencies to return (required, optional) tuple
def _inspect_dependencies(self, cls: type[T]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Returns (required_deps, optional_deps) based on defaults."""
    sig = inspect.signature(cls.__init__)
    required, optional = [], []

    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            optional.append(name)

    return tuple(required), tuple(optional)

# 2. Update create_node to fail on missing required, skip missing optional
async def create_node(self, cls, meta=None):
    if meta and meta.dependencies:
        # Declared deps override signature inspection
        # DECISION POINT: Should declared deps be treated as required?
        required_deps = meta.dependencies
        optional_deps = ()
    else:
        required_deps, optional_deps = self._inspect_dependencies(cls)

    kwargs = {}

    # Required: fail if missing
    for name in required_deps:
        if not self.has(name):
            raise DependencyNotFoundError(
                f"Required dependency '{name}' not registered for {cls.__name__}. "
                f"Add get_{name}() to services/providers.py and register it."
            )
        kwargs[name] = await self.resolve(name)

    # Optional: skip gracefully
    for name in optional_deps:
        if self.has(name):
            kwargs[name] = await self.resolve(name)

    return cls(**kwargs)

# 3. Remove AGENTESE_STRICT env var (no longer needed)
```

**Tests to Update**:
- `test_container.py::TestNodeCreation::test_create_node_with_some_deps_registered`
  - Currently expects TypeError; should now expect DependencyNotFoundError
- Add new test: `test_optional_deps_skipped_gracefully`
- Add new test: `test_required_deps_fail_immediately`

**Decisions Applied**:
- Declared deps → all required (no signature inspection)
- Error message → sympathetic, concise, detailed (see Decisions section)
- Optional skip logging → DEBUG level only

---

## Session 2: Audit Existing Nodes

**Goal**: Ensure existing nodes have correct signatures (required vs optional).

**Files**: All `@node` decorated classes

**Process**:
```bash
# Find all nodes with dependencies
grep -r "dependencies=(" protocols/agentese/contexts/ services/
```

**Audit Checklist**:

| Node | Dependencies | Action Needed |
|------|--------------|---------------|
| BrainNode | brain_persistence | Verify registered |
| SoulNode | kgent_soul | Verify registered OR make signature optional |
| DataNode | dgent | Verify registered |
| ... | ... | ... |

*Run `grep -r "dependencies=(" protocols/agentese/contexts/ services/` to find all*

**Decision Applied**: Fail hard across the board.
- SoulNode must have kgent_soul registered (or make signature optional)
- No special cases — consistent behavior everywhere
- Tests mirror production: required = required

---

## Session 3: Update Documentation & Teaching

**Goal**: Update Teaching sections to reflect new behavior.

**Files**:
- `protocols/agentese/container.py` — Update Teaching section
- `services/providers.py` — Update Teaching section
- `docs/skills/agentese-node-registration.md` — Update "Silent Skip Problem" section
- `CLAUDE.md` — Update DI Container Silent Skip warning

**New Teaching Content**:

```python
"""
Teaching:
    gotcha: Dependencies are REQUIRED by default (no default in __init__).
            Missing required deps raise DependencyNotFoundError immediately.
            To make a dependency optional, add a default: `brain: Brain | None = None`
            (Evidence: test_container.py::TestNodeCreation::test_required_deps_fail_immediately)

    gotcha: Optional dependencies are skipped gracefully if not registered.
            The node's __init__ default is used. This is intentional for
            graceful degradation (e.g., SoulNode without LLM).
            (Evidence: test_container.py::TestNodeCreation::test_optional_deps_skipped_gracefully)
"""
```

---

## Migration Path

**Backward Compatibility**:
- Nodes with all-optional deps (defaults for everything) → No change
- Nodes with required deps that ARE registered → No change
- Nodes with required deps that ARE NOT registered → **Will now fail**

**Risk Mitigation**:
1. Run full test suite after Session 1
2. Any new failures indicate nodes that were silently broken before
3. Fix by either:
   - Registering the missing dependency (correct fix)
   - Making the dependency optional with `| None = None` (if degradation is ok)

---

## Success Criteria

- [ ] `AGENTESE_STRICT` env var removed
- [ ] Required deps fail immediately with actionable error
- [ ] Optional deps skip gracefully (no warning spam)
- [ ] All existing tests pass (or are updated with correct expectations)
- [ ] Teaching sections updated
- [ ] No silent NoneType errors in production paths

---

## Decisions (Resolved 2025-12-21)

1. **Declared dependencies**: ✅ All required
   - `@node(dependencies=("foo",))` → foo is required, period

2. **Graceful degradation**: ✅ Fail hard across the board
   - No special cases. If you need it, register it.
   - Nodes that want optional deps must use `| None = None` in signature

3. **Error verbosity**: ✅ Sympathetic, concise, detailed
   ```
   DependencyNotFoundError: Missing required dependency 'brain_persistence' for BrainNode.

   This usually means the provider wasn't registered during startup.

   Fix: In services/providers.py, add:
     container.register("brain_persistence", get_brain_persistence, singleton=True)

   If this dependency should be optional, update the node's __init__:
     def __init__(self, brain_persistence: BrainPersistence | None = None): ...
   ```

4. **Logging for optional skips**: ✅ Debug/silent
   - No WARNING spam for optional deps
   - DEBUG level only (visible with KGENTS_LOG_LEVEL=DEBUG)

---

## Timeline

| Session | Effort | Depends On |
|---------|--------|------------|
| 1: Core Change | 1-2 hours | None |
| 2: Audit Nodes | 1 hour | Session 1 |
| 3: Documentation | 30 min | Session 1 |

Sessions 2 and 3 can run in parallel after Session 1.

---

*"The proof is not in the prose. The proof is in the functor."*
