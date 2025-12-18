---
path: docs/skills/codebase-analysis
status: active
progress: 80
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps/gestalt-architecture-visualizer
session_notes: |
  Initial creation. Documents Gestalt extension patterns for DevEx.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: complete
  QA: touched
  TEST: touched
  EDUCATE: complete
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.03
  returned: 0.02
---

# Skill: Codebase Analysis (Gestalt)

> Extend Gestalt with new language analyzers, custom governance rules, and health metrics.

**Difficulty**: Medium
**Prerequisites**: Understanding of import/dependency graphs, familiarity with AST parsing
**Files Touched**: `protocols/gestalt/analysis.py`, `protocols/gestalt/governance.py`, `protocols/gestalt/reactive.py`, tests
**References**: `plans/core-apps/gestalt-architecture-visualizer.md`, `protocols/gestalt/`

---

## Overview

Gestalt is the living architecture visualizer for kgents. It provides:

1. **Static Analysis** - Parse imports and build dependency graphs
2. **Health Scoring** - Compute coupling, cohesion, complexity, drift metrics
3. **Governance** - Layer/ring rules for architectural drift detection
4. **Reactive Substrate** - Signal/Computed for live updates
5. **Multi-Surface Projection** - CLI, Web, marimo, JSON outputs

This skill covers extending each of these capabilities.

---

## Architecture Quick Reference

```
protocols/gestalt/
├── analysis.py      # Core types + Python/TS analyzers
├── governance.py    # Layer/ring rules, drift detection
├── reactive.py      # GestaltStore (Signal/Computed)
├── handler.py       # AGENTESE CLI handler
└── _tests/          # Test files
```

### Core Types

```python
@dataclass(frozen=True)
class DependencyEdge:
    """Import relationship between modules."""
    source: str
    target: str
    import_type: str = "standard"  # standard, from, dynamic
    line_number: int = 0
    is_type_only: bool = False

@dataclass
class ModuleHealth:
    """Health metrics (0-1 normalized)."""
    name: str
    coupling: float = 0.0     # lower = better
    cohesion: float = 1.0     # higher = better
    drift: float = 0.0        # lower = better
    complexity: float = 0.0   # lower = better
    churn: float = 0.0        # lower = better
    coverage: float = 1.0     # higher = better
    instability: float | None = None  # Martin metric

@dataclass
class Module:
    """A code module (file or package)."""
    name: str
    path: Path | None = None
    lines_of_code: int = 0
    imports: list[DependencyEdge]
    exported_symbols: list[str]
    health: ModuleHealth | None = None
    layer: str | None = None

@dataclass
class ArchitectureGraph:
    """Full dependency graph with health."""
    modules: dict[str, Module]
    edges: list[DependencyEdge]
    root_path: Path | None
    language: str
```

---

## Task 1: Adding a New Language Analyzer

### Step 1: Create the Import Parser

**File**: `protocols/gestalt/analysis.py`

**Pattern**: Follow the existing Python/TypeScript analyzers:

```python
# ============================================================================
# Go Import Analysis (Example)
# ============================================================================

# Regex patterns for Go imports
GO_IMPORT_SINGLE = re.compile(r'^import\s+"([^"]+)"')
GO_IMPORT_GROUP = re.compile(r'^\s+"([^"]+)"')

def analyze_go_imports(
    source: str,
    module_name: str = "unknown",
) -> list[DependencyEdge]:
    """
    Extract imports from Go source code.

    Handles:
    - import "fmt"
    - import ( "fmt" "strings" )

    Args:
        source: Go source code
        module_name: Name of the module being analyzed

    Returns:
        List of DependencyEdge objects
    """
    imports: list[DependencyEdge] = []
    lines = source.splitlines()
    in_import_block = False

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Start of import block
        if stripped.startswith("import ("):
            in_import_block = True
            continue

        # End of import block
        if in_import_block and stripped == ")":
            in_import_block = False
            continue

        # Single import
        if match := GO_IMPORT_SINGLE.match(stripped):
            imports.append(
                DependencyEdge(
                    source=module_name,
                    target=match.group(1),
                    import_type="standard",
                    line_number=line_no,
                )
            )

        # Import within block
        if in_import_block and (match := GO_IMPORT_GROUP.match(line)):
            imports.append(
                DependencyEdge(
                    source=module_name,
                    target=match.group(1),
                    import_type="standard",
                    line_number=line_no,
                )
            )

    return imports


def analyze_go_file(path: Path) -> Module:
    """Analyze a single Go file."""
    module_name = path.stem

    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return Module(name=module_name, path=path)

    # Count lines (excluding comments and blanks)
    lines = source.splitlines()
    loc = len([l for l in lines if l.strip() and not l.strip().startswith("//")])

    # Extract imports
    imports = analyze_go_imports(source, module_name)

    # Extract exports (public functions/types start with uppercase)
    exports: list[str] = []
    func_pattern = re.compile(r"^func\s+(\w+)")
    type_pattern = re.compile(r"^type\s+(\w+)")
    for line in lines:
        if match := func_pattern.match(line):
            name = match.group(1)
            if name[0].isupper():  # Public in Go
                exports.append(name)
        if match := type_pattern.match(line):
            name = match.group(1)
            if name[0].isupper():
                exports.append(name)

    return Module(
        name=module_name,
        path=path,
        lines_of_code=loc,
        imports=imports,
        exported_symbols=exports,
    )
```

### Step 2: Create the Discovery Function

```python
def discover_go_modules(root: Path) -> Iterator[Path]:
    """Discover Go modules in a directory tree."""
    for path in root.rglob("*.go"):
        parts = path.parts
        if any(
            p in parts
            for p in ["vendor", "node_modules", ".git", "testdata"]
        ):
            continue
        # Skip test files
        if path.name.endswith("_test.go"):
            continue
        yield path
```

### Step 3: Integrate with Graph Builder

**File**: `protocols/gestalt/analysis.py`

Add to `build_architecture_graph()`:

```python
def build_architecture_graph(
    root: Path,
    language: str = "python",
) -> ArchitectureGraph:
    """Build architecture graph for a codebase."""
    graph = ArchitectureGraph(root_path=root, language=language)
    seen_edges: set[tuple[str, str]] = set()

    def add_unique_edges(module: Module) -> None:
        for edge in module.imports:
            edge_key = (edge.source, edge.target)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                graph.edges.append(edge)

    if language == "python":
        # ... existing code ...
    elif language == "typescript":
        # ... existing code ...
    elif language == "go":  # NEW
        for path in discover_go_modules(root):
            module = analyze_go_file(path)
            try:
                rel_path = path.relative_to(root)
                module.name = str(rel_path.with_suffix("")).replace("/", ".")
            except ValueError:
                pass
            for edge in module.imports:
                object.__setattr__(edge, "source", module.name)
            graph.modules[module.name] = module
            add_unique_edges(module)

    # Compute health metrics...
    return graph
```

### Step 4: Add Tests

**File**: `protocols/gestalt/_tests/test_go_analysis.py`

```python
"""Tests for Go import analysis."""

import pytest
from pathlib import Path
from protocols.gestalt.analysis import (
    analyze_go_imports,
    analyze_go_file,
    discover_go_modules,
)


class TestGoImports:
    """Tests for Go import parsing."""

    def test_single_import(self) -> None:
        """Parse single import statement."""
        source = 'import "fmt"'
        imports = analyze_go_imports(source, "main")

        assert len(imports) == 1
        assert imports[0].target == "fmt"

    def test_import_block(self) -> None:
        """Parse import block."""
        source = '''import (
    "fmt"
    "strings"
)'''
        imports = analyze_go_imports(source, "main")

        assert len(imports) == 2
        assert imports[0].target == "fmt"
        assert imports[1].target == "strings"

    def test_standard_library(self) -> None:
        """Standard library imports are detected."""
        source = '''import (
    "encoding/json"
    "net/http"
)'''
        imports = analyze_go_imports(source, "main")

        assert len(imports) == 2
        assert "encoding/json" in [i.target for i in imports]
```

---

## Task 2: Creating Custom Governance Rules

### Understanding Rule Types

```python
class RuleType(Enum):
    LAYER = "layer"  # Layered architecture
    RING = "ring"    # Onion/clean architecture
    ALLOW = "allow"  # Explicit allow
    DENY = "deny"    # Explicit deny
    TAG = "tag"      # Tag-based
```

### Creating a LayerRule

**Use case**: Enforce that `presentation` layer can only depend on `application` layer.

```python
from protocols.gestalt.governance import LayerRule, GovernanceConfig

# Define the rule
presentation_rule = LayerRule(
    layer="presentation",
    allowed_dependencies=["presentation", "application"],
    description="Presentation may only depend on Application layer",
)

# Add to config
config = GovernanceConfig(
    layer_rules=[presentation_rule],
    layer_patterns={
        "presentation": ["web.*", "cli.*", "api.*"],
        "application": ["services.*", "handlers.*"],
        "domain": ["models.*", "entities.*"],
        "infrastructure": ["db.*", "external.*"],
    },
)
```

### Creating a RingRule

**Use case**: Enforce clean architecture (outer rings depend on inner rings only).

```python
from protocols.gestalt.governance import RingRule, GovernanceConfig

ring_rule = RingRule(
    ring_order=["domain", "application", "infrastructure", "presentation"],
    description="Clean architecture: outer rings depend on inner only",
)

config = GovernanceConfig(
    ring_rule=ring_rule,
    ring_patterns={
        "domain": ["*.models", "*.entities", "*.types"],
        "application": ["*.services", "*.usecases"],
        "infrastructure": ["*.db", "*.api", "*.clients"],
        "presentation": ["*.web", "*.cli", "*.handlers"],
    },
)
```

### Creating a Custom DriftRule

**Use case**: Forbid circular dependencies.

```python
from protocols.gestalt.governance import DriftRule, DependencyEdge, Module

def no_circular_rule() -> DriftRule:
    """Create rule that forbids A->B->A cycles."""

    def check_not_circular(
        edge: DependencyEdge,
        source_module: Module,
        target_module: Module,
    ) -> bool:
        """Return True if allowed (no direct cycle)."""
        # Check if target has an edge back to source
        for imp in target_module.imports:
            if imp.target == source_module.name:
                return False  # Circular! Not allowed
        return True

    return DriftRule(
        name="no-direct-cycles",
        predicate=check_not_circular,
        description="Direct circular dependencies are forbidden",
        severity="error",
    )

# Add to config
config = GovernanceConfig(
    drift_rules=[no_circular_rule()],
)
```

### Using Declarative YAML Config (Future)

**File**: `.gestalt/rules.yaml`

```yaml
# Layer architecture rules
layers:
  presentation:
    allowed: [presentation, application]
    patterns: ["web.*", "cli.*", "api.*"]
  application:
    allowed: [application, domain]
    patterns: ["services.*", "handlers.*"]
  domain:
    allowed: [domain]
    patterns: ["models.*", "entities.*"]

# Ring architecture rules
rings:
  order: [domain, application, infrastructure, presentation]
  patterns:
    domain: ["*.types", "*.base"]
    application: ["*.services"]
    infrastructure: ["*.db", "*.clients"]
    presentation: ["*.web", "*.cli"]

# Custom rules
custom_rules:
  - name: no-direct-cycles
    severity: error
    description: Direct circular dependencies are forbidden

# Suppressions (known violations to ignore)
suppressions:
  - source: "legacy.module"
    target: "old.dependency"
    reason: "Legacy code, will refactor in Q2"
    expires: "2025-06-01"
```

---

## Task 3: Extending Health Metrics

### Adding a New Metric

**File**: `protocols/gestalt/analysis.py`

```python
@dataclass
class ModuleHealth:
    """Health metrics for a code module."""
    name: str
    coupling: float = 0.0
    cohesion: float = 1.0
    drift: float = 0.0
    complexity: float = 0.0
    churn: float = 0.0
    coverage: float = 1.0
    instability: float | None = None

    # NEW: Add your metric
    test_ratio: float = 1.0  # 0-1, higher = better (tests/production code)

    @property
    def overall_health(self) -> float:
        """Compute overall health score."""
        return (
            (1 - self.drift) * 0.25
            + (1 - self.coupling) * 0.20
            + self.cohesion * 0.15
            + (1 - self.complexity) * 0.15
            + (1 - self.churn) * 0.10
            + self.coverage * 0.10  # Reduced from 0.15
            + self.test_ratio * 0.05  # NEW: 5% weight
        )
```

### Computing the New Metric

In `build_architecture_graph()`:

```python
def _compute_test_ratio(graph: ArchitectureGraph, module_name: str) -> float:
    """Compute test file to production file ratio for a module."""
    # Find test modules for this module
    test_patterns = [
        f"test_{module_name}",
        f"{module_name}_test",
        f"tests.{module_name}",
    ]

    test_modules = [
        m for m in graph.modules.values()
        if any(p in m.name for p in test_patterns)
    ]

    if not test_modules:
        return 0.0  # No tests = worst score

    module = graph.modules.get(module_name)
    if not module or module.lines_of_code == 0:
        return 0.5  # Unknown

    test_loc = sum(m.lines_of_code for m in test_modules)
    ratio = test_loc / module.lines_of_code

    # Normalize: 0.5 ratio = perfect (tests are half the size of code)
    # Below 0.2 = poor, above 1.0 = excessive
    return min(1.0, ratio / 0.5)
```

---

## Task 4: Wiring to AGENTESE

### Understanding the Path Structure

Gestalt uses `world.codebase.*` paths:

| Path | Aspect | Handler |
|------|--------|---------|
| `world.codebase.manifest` | manifest | Full architecture graph |
| `world.codebase.health.manifest` | manifest | Health metrics |
| `world.codebase.drift.witness` | witness | Drift violations |
| `world.codebase.module[name].manifest` | manifest | Module details |
| `world.codebase.scan` | - | Force rescan |

### Adding a New Path

**Example**: Add `world.codebase.hotspots.manifest` for high-churn modules.

**Step 1**: Add handler function

**File**: `protocols/gestalt/handler.py`

```python
def handle_hotspots_manifest(
    args: list[str],
    json_output: bool = False,
    store: "GestaltStore | None" = None,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.hotspots.manifest

    Returns modules with high churn (change frequency).
    """
    display_path_header(
        path="world.codebase.hotspots.manifest",
        aspect="manifest",
        effects=["HOTSPOTS_IDENTIFIED"],
    )

    if store is None:
        store = _get_store()
        asyncio.run(_ensure_scanned(store))

    graph = store.graph.value

    # Sort modules by complexity + coupling (proxy for hotspot)
    hotspots = sorted(
        [m for m in graph.modules.values() if m.health],
        key=lambda m: (m.health.complexity + m.health.coupling) if m.health else 0,
        reverse=True,
    )[:10]

    result = {
        "hotspot_count": len(hotspots),
        "hotspots": [
            {
                "name": m.name,
                "complexity": round(m.health.complexity, 2) if m.health else 0,
                "coupling": round(m.health.coupling, 2) if m.health else 0,
                "loc": m.lines_of_code,
            }
            for m in hotspots
        ],
    }

    if json_output:
        return result

    lines = ["Architectural Hotspots (high complexity + coupling):", ""]
    for h in hotspots:
        name = h["name"]
        complexity = h["complexity"]
        coupling = h["coupling"]
        lines.append(f"  {name}: complexity={complexity}, coupling={coupling}")

    return "\n".join(lines)
```

**Step 2**: Wire into CLI router

```python
def cmd_codebase(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """CLI handler for world.codebase.* commands."""
    # ... existing code ...

    if not args or args[0] in ("manifest", "status"):
        result = handle_codebase_manifest(args[1:] if args else [], json_output, store)
    elif args[0] == "health":
        result = handle_health_manifest(args[1:], json_output, store)
    elif args[0] == "drift":
        result = handle_drift_witness(args[1:], json_output, store)
    elif args[0] == "hotspots":  # NEW
        result = handle_hotspots_manifest(args[1:], json_output, store)
    # ... rest of handlers ...
```

**Step 3**: Register in Crown Jewels

**File**: `protocols/agentese/crown_jewels.py`

```python
# In GESTALT_PATHS
"world.codebase.hotspots.manifest": {
    "handler": "protocols.gestalt.handler:handle_hotspots_manifest",
    "aspect": "manifest",
    "effects": ["HOTSPOTS_IDENTIFIED"],
},
```

---

## Task 5: Creating a Custom GestaltStore

### Understanding GestaltStore

GestaltStore wraps analysis in reactive primitives:

```python
class GestaltStore:
    """Reactive store for architecture analysis."""

    # Core signals
    graph: Signal[ArchitectureGraph]      # Source of truth
    violations: Signal[list[DriftViolation]]

    # Derived computeds
    module_count: Computed[int]
    edge_count: Computed[int]
    average_health: Computed[float]
    overall_grade: Computed[str]
    drift_count: Computed[int]
    grade_distribution: Computed[dict[str, int]]
```

### Creating a Custom Store with Injected Config

```python
from protocols.gestalt.reactive import GestaltStore
from protocols.gestalt.governance import GovernanceConfig, LayerRule

# Custom governance config
my_config = GovernanceConfig(
    layer_rules=[
        LayerRule(
            layer="handlers",
            allowed_dependencies=["handlers", "services", "models"],
        ),
    ],
    layer_patterns={
        "handlers": ["api.*", "web.*"],
        "services": ["services.*"],
        "models": ["models.*", "db.*"],
    },
)

# Create store with custom config
store = GestaltStore(
    root=Path("./my_project"),
    language="python",
    config=my_config,  # Pass custom config
)

# Scan and access reactive values
await store.scan()
print(f"Modules: {store.module_count.value}")
print(f"Grade: {store.overall_grade.value}")
print(f"Violations: {store.drift_count.value}")
```

### Subscribing to Changes

```python
# Subscribe to graph changes
def on_graph_change(graph: ArchitectureGraph) -> None:
    print(f"Graph updated: {graph.module_count} modules")

unsub = store.subscribe_to_changes(on_graph_change)

# Subscribe to violations
def on_violations_change(violations: list[DriftViolation]) -> None:
    active = len([v for v in violations if not v.suppressed])
    if active > 0:
        print(f"Warning: {active} active drift violations")

store.subscribe_to_violations(on_violations_change)

# Start file watching
await store.start_watching()

# Later: unsubscribe
unsub()
```

---

## Testing Patterns

### Unit Tests for Analyzers

```python
class TestAnalyzer:
    """Tests for language analyzer."""

    def test_import_extraction(self) -> None:
        """Imports are correctly extracted."""
        source = "..."  # Language-specific source
        imports = analyze_imports(source, "test_module")

        assert len(imports) == expected_count
        assert imports[0].target == "expected_target"

    def test_handles_malformed_source(self) -> None:
        """Malformed source doesn't crash."""
        source = "not valid code {{{"
        imports = analyze_imports(source, "broken")

        assert imports == []  # Empty, not crash
```

### Integration Tests for Governance

```python
class TestGovernance:
    """Tests for governance rules."""

    def test_layer_violation_detected(self) -> None:
        """Layer violations are detected."""
        config = create_test_config()
        graph = create_test_graph_with_violation()

        violations = check_drift(graph, config)

        assert len(violations) > 0
        assert any(v.rule_type == RuleType.LAYER for v in violations)
```

### Property-Based Tests

```python
from hypothesis import given, strategies as st

class TestHealthInvariants:
    """Property-based tests for health metrics."""

    @given(
        coupling=st.floats(min_value=0.0, max_value=1.0),
        cohesion=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_health_bounded(self, coupling: float, cohesion: float) -> None:
        """Overall health is always between 0 and 1."""
        health = ModuleHealth(
            name="test",
            coupling=coupling,
            cohesion=cohesion,
        )

        assert 0.0 <= health.overall_health <= 1.0
```

---

## Common Pitfalls

### 1. Forgetting Edge Deduplication

**Problem**: Multiple imports of same target inflate coupling.

**Fix**: Use `seen_edges` set in `build_architecture_graph()`:
```python
seen_edges: set[tuple[str, str]] = set()
edge_key = (edge.source, edge.target)
if edge_key not in seen_edges:
    seen_edges.add(edge_key)
    graph.edges.append(edge)
```

### 2. Not Handling Encoding Errors

**Problem**: Non-UTF-8 files crash the analyzer.

**Fix**: Always wrap file reads:
```python
try:
    source = path.read_text(encoding="utf-8")
except Exception:
    return Module(name=module_name, path=path)
```

### 3. Blocking in Reactive Callbacks

**Problem**: Heavy computation in Signal callbacks blocks the event loop.

**Fix**: Use incremental updates, not full rescans:
```python
# BAD
store.graph.subscribe(lambda g: expensive_analysis(g))

# GOOD
store.graph.subscribe(lambda g: schedule_background_analysis(g))
```

### 4. Not Normalizing Module Names

**Problem**: Different path separators cause duplicate modules.

**Fix**: Always use `.` separator:
```python
module.name = str(rel_path.with_suffix("")).replace("/", ".")
```

---

## Verification Commands

### Verify Analyzer

```bash
cd impl/claude
uv run python -c "
from pathlib import Path
from protocols.gestalt.analysis import analyze_go_imports

source = '''import \"fmt\"'''
imports = analyze_go_imports(source, 'main')
print(f'Found {len(imports)} imports')
"
```

### Verify Governance Rules

```bash
uv run python -c "
from protocols.gestalt.governance import check_drift, create_kgents_config
from protocols.gestalt.analysis import build_architecture_graph
from pathlib import Path

graph = build_architecture_graph(Path('.'), 'python')
config = create_kgents_config()
violations = check_drift(graph, config)
print(f'Found {len(violations)} violations')
"
```

### Run Tests

```bash
cd impl/claude
uv run pytest protocols/gestalt/_tests/ -v
```

### Full Scan

```bash
uv run python -m protocols.cli.main world codebase
```

---

## Related Skills

- [agentese-path](agentese-path.md) - Adding AGENTESE paths
- [handler-patterns](handler-patterns.md) - CLI handler patterns
- [reactive-primitives](reactive-primitives.md) - Signal/Computed usage
- [test-patterns](test-patterns.md) - Testing conventions

---

## Changelog

- 2025-12-16: Initial creation documenting Gestalt extension patterns
