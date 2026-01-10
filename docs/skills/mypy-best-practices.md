# Mypy Best Practices for kgents

> *"Type checking is not about catching bugs—it's about making the codebase self-documenting."*

This skill covers mypy configuration, error resolution patterns, and best practices for maintaining type safety in kgents.

---

## Quick Reference

```bash
# Standard check (uses mypy.ini)
cd impl/claude && uv run mypy .

# Fast incremental check (daemon mode, 5-10x faster)
dmypy run -- --strict --explicit-package-bases agents/ services/

# Check specific module
uv run mypy agents/t/probes/

# Check with verbose output
uv run mypy . --show-error-context --pretty
```

---

## Configuration Philosophy

Our mypy configuration follows the **"strict globally, relax locally"** pattern:

```ini
[mypy]
strict = True  # Enforce strict typing everywhere

# Then relax per-module as needed:
[mypy-services.forge.node]
disable_error_code = arg-type, assignment  # Specific relaxations
```

### Key Config Settings (mypy.ini)

| Setting | Value | Purpose |
|---------|-------|---------|
| `strict = True` | Global | Maximum type safety |
| `explicit_package_bases = True` | Global | Correct imports |
| `incremental = True` | Global | Cache-based speedup |
| `show_error_codes = True` | Global | Enable targeted ignores |
| `plugins = sqlalchemy.ext.mypy.plugin` | Global | ORM typing (deprecated) |

### Exclude Patterns

These directories are excluded from checking:
- `_archive/` - Archived code
- `*-archived/` - Legacy archived directories
- `scripts/` - Utility scripts

---

## When to Add Module Relaxations

### Valid Reasons
1. **External library decorators** (FastAPI, pytest, kopf)
2. **Generated code** (protobuf, alembic migrations)
3. **Example/demo files** (not production code)
4. **Test files** (fixtures, mocks need flexibility)
5. **WIP modules** (temporary, track in comments)

### Invalid Reasons (Fix the Code Instead)
- "It's too hard to type" - usually indicates design smell
- "We don't have time" - typing prevents future bugs
- "This module is special" - if it's production, it needs types

---

## Error Resolution Patterns

### Pattern 1: Missing Type Parameters

```python
# Bad
def process(data: dict) -> list:
    ...

# Good
def process(data: dict[str, Any]) -> list[ProcessedItem]:
    ...
```

**Config fix if pervasive:**
```ini
[mypy-services.some_module]
disable_error_code = type-arg
```

### Pattern 2: Return Type Any

```python
# Bad - returns Any from typed function
def get_value(key: str) -> str:
    return some_dict.get(key)  # type: ignore[no-any-return]

# Good - explicit handling
def get_value(key: str) -> str:
    value = some_dict.get(key)
    if value is None:
        raise KeyError(key)
    return str(value)
```

### Pattern 3: Union/Optional Attributes

```python
# Bad
def process(item: Item | None) -> str:
    return item.name  # error: union-attr

# Good
def process(item: Item | None) -> str:
    if item is None:
        return "unknown"
    return item.name
```

### Pattern 4: Override Errors

```python
# Bad - violates Liskov substitution
class Parent:
    def method(self, x: int) -> str: ...

class Child(Parent):
    def method(self, x: float) -> str: ...  # error: override

# Good - maintain signature
class Child(Parent):
    def method(self, x: int) -> str: ...
```

---

## Type Ignore Best Practices

### Always Use Specific Error Codes

```python
# Bad - blanket ignore hides all errors
x = something()  # type: ignore

# Good - targeted ignore
x = something()  # type: ignore[arg-type]
```

### When to Use Inline vs Config

| Situation | Use Inline | Use Config |
|-----------|------------|------------|
| One-off edge case | `# type: ignore[code]` | No |
| Multiple in one file | No | `disable_error_code` |
| Pattern across module | No | Per-module section |
| External lib issues | No | `ignore_missing_imports` |

---

## Test File Configuration

Test files get relaxed checking via module patterns:

```ini
# Pattern for test_*.py files
[mypy-*.test_*]
disallow_untyped_defs = False
disallow_untyped_calls = False
disable_error_code = no-untyped-def, arg-type, attr-defined, var-annotated, union-attr
```

### Why Relax Tests?
- **Fixtures** often have complex/dynamic types
- **Mocks** return Any by design
- **Assertions** access private attributes
- **Parameterized tests** have flexible signatures

---

## External Library Handling

### Option 1: Install Type Stubs (Preferred)

```bash
uv add --dev types-redis types-PyYAML types-stripe
```

Then remove from mypy.ini:
```ini
# DELETE THIS
[mypy-redis.*]
ignore_missing_imports = True
```

### Option 2: Ignore Missing Imports

When stubs don't exist:
```ini
[mypy-some_lib.*]
ignore_missing_imports = True
```

### Option 3: Generate Stubs

```bash
stubgen -p some_lib -o stubs/
```

Then add to mypy path:
```ini
mypy_path = stubs
```

---

## Performance Tips

### 1. Use Daemon Mode

```bash
# First run starts daemon
dmypy run -- .

# Subsequent runs are 5-10x faster
dmypy run -- .

# Restart after branch switch
dmypy stop && dmypy run -- .
```

### 2. Check Only Changed Files

```bash
# Check specific module after editing
uv run mypy services/witness/

# Check files in git diff
git diff --name-only | grep '\.py$' | xargs uv run mypy
```

### 3. Incremental Cache

Already enabled in config:
```ini
incremental = True
```

Clear if corrupted:
```bash
rm -rf .mypy_cache
```

---

## Common Gotchas

### 1. SQLAlchemy Plugin Deprecated

The `sqlalchemy.ext.mypy.plugin` is deprecated in SQLAlchemy 2.1. Use native typing:

```python
# Old (plugin required)
class User(Base):
    name = Column(String)  # type: str

# New (native typing)
class User(Base):
    name: Mapped[str] = mapped_column(String)
```

### 2. Property Decorator Stacking

```python
# Error: Decorators on top of @property are not supported
@cached_property
@property  # Can't stack!
def value(self): ...

# Fix: Use just @cached_property or restructure
@cached_property
def value(self): ...
```

### 3. Callable vs callable

```python
# Wrong
def takes_func(f: callable) -> None: ...  # error: valid-type

# Right
from typing import Callable
def takes_func(f: Callable[..., Any]) -> None: ...
```

---

## Adding New Module Relaxations

When you need to add a new module to mypy.ini:

1. **First try to fix the actual errors** - often reveals design issues
2. **Use targeted error codes** - not `ignore_errors = True`
3. **Add comments explaining why** - for future maintainers
4. **Group with similar modules** - keep config organized

```ini
# Forge nodes - Observer vs Umwelt override pattern
[mypy-services.forge.node]
disable_error_code = arg-type, assignment, override, union-attr
```

---

## Migration Path: Stricter Typing

To progressively tighten types:

1. **Run mypy and count errors** - `mypy . | grep -c error`
2. **Pick highest-value modules** - core business logic first
3. **Remove one relaxation at a time** - track error delta
4. **Fix errors or justify keeping relaxation**
5. **Enable stricter settings** - e.g., `enable_error_code = ignore-without-code`

---

## Resources

- [mypy Documentation](https://mypy.readthedocs.io/)
- [mypy Error Codes](https://mypy.readthedocs.io/en/stable/error_codes.html)
- [Professional-grade mypy config (Wolt)](https://careers.wolt.com/en/blog/tech/professional-grade-mypy-configuration)
- [typeshed (type stub repository)](https://github.com/python/typeshed)

---

*Last updated: 2025-01-10*
*Error count: 639 → 218 → 147 (Phase 2: 66% reduction, Phase 3: 33% further reduction)*

### Phase 3 Changes (2025-01-10)

Focus on fixing actual errors and enforcing specific error codes in type ignores:

1. **Enabled `ignore-without-code`** - All `# type: ignore` comments now require specific error codes (e.g., `# type: ignore[arg-type]`). This prevents blanket ignores from hiding new errors.

2. **Key error patterns fixed**:
   - **SQLAlchemy 2.0 typing** - Use `Mapped[]` and `mapped_column()`, set `__table_args__: Any` in Base class
   - **Duck-typed returns** - Use `cast()` for type narrowing with storage returns that may be `dict | Model`
   - **Any comparisons** - Wrap in `bool()` for comparisons involving Any-typed values
   - **Override signatures** - Match parameter names exactly (e.g., `aspect_name` → `aspect`)
   - **Relative imports** - Convert to absolute imports when crossing package boundaries

3. **Common error code patterns**:
   ```python
   # arg-type: Wrong argument type
   self._queue.put_nowait(sentinel)  # type: ignore[arg-type]

   # attr-defined: Attribute not found (duck typing)
   if hasattr(obj, "method"):
       obj.method()  # type: ignore[attr-defined]

   # override: Method signature differs from parent
   @property
   def name(self) -> str:  # type: ignore[override]

   # misc: Class-level issues (e.g., multiple inheritance)
   class MyProbe(Base, Protocol):  # type: ignore[misc]
   ```

4. **Files fixed** (representative samples):
   - `models/kblock.py` - dict type parameters, `__table_args__` typing
   - `services/zero_seed/operator_calculus.py` - ABC `__init__` method
   - `services/portal/resolvers/mark.py` - duck-typing with hasattr + cast()
   - `agents/t/probes/witness_probe.py` - override and misc error codes
   - `services/code/service.py` - relative → absolute imports

### Phase 2 Changes (2025-01-10)

Major improvements from discovering that mypy glob patterns were **silently invalid**:

1. **Test file exclusion via regex** - Patterns like `[mypy-test_*]` and `[mypy-*.test_*]` were invalid (mypy globs don't support underscore in first segment). Fixed by adding test file patterns to the `exclude` regex.

2. **Type stubs installed** - Added `types-redis` and `types-stripe` to dev dependencies.

3. **Verification scripts excluded** - Added `verify_[^/]*\.py$` to exclude pattern.

4. **Targeted module configs** - Added configs for high-error modules with documented reasons:
   - `services/witness/persistence.py` - SQLAlchemy 2.0 mapped_column + deprecated plugin
   - `services/kgentsd/pty_bridge.py` - intentional override for PTY wrapper
   - `services/brain/persistence.py` - optional session_factory pattern
   - And many more (see mypy.ini comments)
