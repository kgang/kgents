"""
AGENTESE Self.System Context - Autopoietic Kernel Interface.

self.system.* handles for introspection and self-modification:
- self.system.manifest    - Project to observer's view
- self.system.audit       - Drift detection (spec vs impl)
- self.system.compile     - Spec → Impl generation
- self.system.reflect     - Impl → Spec extraction
- self.system.evolve      - Apply mutations
- self.system.witness     - History of changes (N-gent trace)

This is the autopoietic interface - the system's ability to describe,
modify, and regenerate itself.

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from ..registry import get_registry, node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Types ===


class DriftStatus(str, Enum):
    """Status of spec-impl alignment."""

    ALIGNED = "aligned"  # Spec and impl match
    DIVERGED = "diverged"  # Spec and impl differ
    MISSING_SPEC = "missing_spec"  # Impl exists without spec
    MISSING_IMPL = "missing_impl"  # Spec exists without impl
    UNKNOWN = "unknown"  # Cannot determine


@dataclass(frozen=True)
class DriftReport:
    """Report of spec-impl drift for a single module."""

    module: str
    status: DriftStatus
    spec_path: str | None = None
    impl_path: str | None = None
    spec_hash: str | None = None
    impl_hash: str | None = None
    details: str = ""


@dataclass
class AuditResult:
    """Result of a full system audit."""

    timestamp: datetime
    total_modules: int
    aligned: int
    diverged: int
    missing_spec: int
    missing_impl: int
    reports: list[DriftReport] = field(default_factory=list)
    autopoiesis_score: float = 0.0

    @property
    def healthy(self) -> bool:
        """Is the system healthy (all aligned)?"""
        return self.diverged == 0 and self.missing_impl == 0


@dataclass
class CompileResult:
    """Result of compiling a spec to impl."""

    spec_path: str
    impl_path: str
    success: bool
    generated_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ReflectResult:
    """Result of reflecting impl to spec."""

    impl_path: str
    spec_content: str
    confidence: float = 0.0  # How confident in extraction


# === Affordances ===


SYSTEM_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "audit",
    "compile",
    "reflect",
    "evolve",
    "witness",
)


# === Node Implementation ===


@node("self.system", description="Autopoietic kernel interface")
@dataclass
class SystemNode(BaseLogosNode):
    """
    self.system - The autopoietic kernel interface.

    Provides introspection and self-modification capabilities for kgents.
    This is the system's ability to describe, modify, and regenerate itself.

    The Three Functors:
    - Compile: SpecCat → ImplCat (generate implementation from spec)
    - Project: ImplCat → PathCat (make service discoverable)
    - Reflect: ImplCat → SpecCat (extract spec from implementation)

    Autopoiesis Fixed Point: Reflect(Compile(S)) ≅ S
    """

    _handle: str = "self.system"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes get same affordances for system introspection."""
        return SYSTEM_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View system architecture and health",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        What is kgents? Project to observer's view.

        Returns the metaphysical agent stack (AD-009) with current health metrics.
        """
        # Get observer archetype
        archetype = "guest"
        if hasattr(observer, "archetype"):
            archetype = observer.archetype
        elif hasattr(observer, "dna"):
            archetype = getattr(observer.dna, "archetype", "guest")

        # Build stack visualization
        stack = """
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
"""
        return BasicRendering(
            summary="kgents Metaphysical Agent Stack (AD-009)",
            content=stack,
            metadata={
                "observer": archetype,
                "route": "/system",
                "stack_layers": 7,
            },
        )

    def _ensure_operad_imports(self) -> None:
        """Ensure all operad modules are imported so they register."""
        # These imports trigger OperadRegistry.register() calls
        try:
            import agents.brain.operad  # noqa: F401
        except ImportError:
            pass
        try:
            import agents.design.operad  # noqa: F401
        except ImportError:
            pass

    def _collect_operad_audit(self) -> dict[str, Any]:
        """Collect operad registry data."""
        # Ensure all operads are imported first
        self._ensure_operad_imports()
        try:
            from agents.operad.core import OperadRegistry

            operads = OperadRegistry.all_operads()
            return {
                "count": len(operads),
                "names": list(operads.keys()),
                "laws_total": sum(len(o.laws) for o in operads.values()),
                "operations_total": sum(len(o.operations) for o in operads.values()),
            }
        except ImportError:
            return {"count": 0, "names": [], "error": "OperadRegistry not importable"}

    def _ensure_node_imports(self) -> None:
        """Ensure all node modules are imported so they register."""
        # These imports trigger @node registrations
        try:
            from services.atelier import node as atelier_node  # noqa: F401
        except ImportError:
            pass

    def _collect_node_audit(self) -> dict[str, Any]:
        """Collect AGENTESE node registry data."""
        # Ensure all nodes are imported first
        self._ensure_node_imports()
        registry = get_registry()
        all_paths = registry.list_paths()
        return {
            "count": len(all_paths),
            "paths": all_paths,
            "contexts": list({p.split(".")[0] for p in all_paths}),
        }

    def _collect_jewel_audit(self) -> list[dict[str, Any]]:
        """Collect Crown Jewel compliance data."""
        # The 7 Crown Jewels with their expected layers
        jewels: list[dict[str, str | None]] = [
            {
                "name": "Brain",
                "path": "self.memory",
                "poly": "BRAIN_POLYNOMIAL",
                "operad": "BrainOperad",
            },
            {
                "name": "Town",
                "path": "world.town",
                "poly": "CITIZEN_POLYNOMIAL",
                "operad": "TownOperad",
            },
            {
                "name": "Gardener",
                "path": "concept.gardener",
                "poly": None,
                "operad": "GrowthOperad",
            },
            # Gestalt removed 2025-12-21 (Crown Jewel Cleanup)
            {
                "name": "Atelier",
                "path": "world.atelier",
                "poly": "WORKSHOP_POLYNOMIAL",
                "operad": "AtelierOperad",
            },
            # Park, Coalition removed 2025-12-21 (Crown Jewel Cleanup)
        ]

        registry = get_registry()
        try:
            from agents.operad.core import OperadRegistry

            operads = OperadRegistry.all_operads()
        except ImportError:
            operads = {}

        results: list[dict[str, Any]] = []
        for jewel in jewels:
            path = jewel["path"]
            operad_name = jewel["operad"]
            has_node = registry.has(path) if path else False
            has_operad = operad_name in operads if operad_name else False
            compliance = sum([has_node, has_operad]) / 2 * 100
            results.append(
                {
                    "name": jewel["name"],
                    "path": path,
                    "has_node": has_node,
                    "has_operad": has_operad,
                    "compliance": compliance,
                }
            )
        return results

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Detect spec-impl drift across the system",
    )
    async def audit(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        What needs fixing? Run drift detection.

        Compares specs against implementations and calculates autopoiesis score.
        Real introspection of OperadRegistry and NodeRegistry.
        """
        # Collect real audit data
        operad_data = self._collect_operad_audit()
        node_data = self._collect_node_audit()
        jewel_data = self._collect_jewel_audit()

        # Calculate autopoiesis score: jewels with full compliance / total jewels
        compliant_jewels = sum(1 for j in jewel_data if j["compliance"] >= 100)
        autopoiesis_score = compliant_jewels / len(jewel_data) if jewel_data else 0.0

        # Build jewel table
        jewel_table = "\n".join(
            [
                f"| {j['name']:<12} | {j['path']:<20} | {'✅' if j['has_node'] else '❌'} | {'✅' if j['has_operad'] else '❌'} | {j['compliance']:.0f}% |"
                for j in jewel_data
            ]
        )

        audit = AuditResult(
            timestamp=datetime.now(),
            total_modules=operad_data["count"] + node_data["count"],
            aligned=compliant_jewels,
            diverged=0,
            missing_spec=0,
            missing_impl=len(jewel_data) - compliant_jewels,
            reports=[],
            autopoiesis_score=autopoiesis_score,
        )

        content = f"""
## System Audit

**Timestamp:** {audit.timestamp.isoformat()}
**Autopoiesis Score:** {audit.autopoiesis_score:.1%}

---

### Operad Registry
- **Registered**: {operad_data["count"]} operads
- **Total Laws**: {operad_data.get("laws_total", 0)}
- **Total Operations**: {operad_data.get("operations_total", 0)}
- **Names**: {", ".join(operad_data["names"][:8])}{"..." if len(operad_data["names"]) > 8 else ""}

### AGENTESE Node Registry
- **Registered**: {node_data["count"]} paths
- **Contexts**: {", ".join(sorted(node_data["contexts"]))}
- **Paths**: {", ".join(node_data["paths"][:10])}{"..." if len(node_data["paths"]) > 10 else ""}

---

### Crown Jewel Compliance (7-Layer AD-009)

| Jewel        | Path                 | Node | Operad | Compliance |
|--------------|----------------------|------|--------|------------|
{jewel_table}

---

### Phoenix Metric

```
Autopoiesis Score = (Jewels with full compliance) / (Total jewels)
                  = {compliant_jewels} / {len(jewel_data)}
                  = {audit.autopoiesis_score:.1%}

Target: ≥0.9 (90%)
```

### Recommendations
{"- ✅ System healthy: all jewels compliant!" if audit.healthy else ""}

Run `kg self.system.witness` to see evolution history.
"""
        return BasicRendering(
            summary=f"System Audit: {audit.autopoiesis_score:.1%} autopoiesis ({compliant_jewels}/{len(jewel_data)} jewels)",
            content=content,
            metadata={
                "timestamp": audit.timestamp.isoformat(),
                "autopoiesis_score": audit.autopoiesis_score,
                "healthy": audit.healthy,
                "operads": operad_data,
                "nodes": node_data,
                "jewels": jewel_data,
            },
        )

    def _get_kgents_root(self) -> Path:
        """Get the kgents project root directory."""
        # self_system.py is at: impl/claude/protocols/agentese/contexts/
        # parents[0] = contexts/, [1] = agentese/, [2] = protocols/,
        # [3] = claude/, [4] = impl/, [5] = kgents/
        return Path(__file__).parents[5]

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.WRITES("impl/")],
        help="Generate implementation from spec",
    )
    async def compile(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        spec_path: str | None = None,
        dry_run: bool = True,
    ) -> Renderable:
        """
        Spec → Impl: Generate implementation from specification.

        The Compile functor transforms SpecCat → ImplCat.

        Args:
            spec_path: Path to spec file (relative to kgents root or absolute)
            dry_run: If True (default), show what would be generated without writing
        """
        if not spec_path:
            return BasicRendering(
                summary="Compile requires spec_path",
                content="Usage: `kg self.system.compile spec_path=spec/town/operad.md`\n\n"
                "Options:\n"
                "  dry_run=true  (default) Show what would be generated\n"
                "  dry_run=false Actually write files",
                metadata={"error": "missing_spec_path"},
            )

        # Import specgraph
        try:
            from ..specgraph import compile_spec, parse_spec_file
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        # Resolve paths
        kgents_root = self._get_kgents_root()
        spec_file = Path(spec_path)
        if not spec_file.is_absolute():
            spec_file = kgents_root / spec_file

        if not spec_file.exists():
            return BasicRendering(
                summary=f"Spec file not found: {spec_path}",
                content=f"Looking for: {spec_file}",
                metadata={"error": "file_not_found"},
            )

        # Parse spec
        try:
            spec_node = parse_spec_file(spec_file)
        except Exception as e:
            return BasicRendering(
                summary=f"Failed to parse spec: {spec_path}",
                content=f"Error: {e}",
                metadata={"error": "parse_error"},
            )

        # Compile
        impl_root = kgents_root / "impl" / "claude"
        result = compile_spec(spec_node, impl_root, dry_run=dry_run)

        # Format output
        if result.success:
            files_list = "\n".join(f"  - {f}" for f in result.generated_files)
            warnings_list = (
                "\n".join(f"  ⚠️ {w}" for w in result.warnings) if result.warnings else ""
            )
            content = f"""## Compile Result

**Spec**: {spec_node.full_path}
**Source**: {spec_path}
**Impl Dir**: {result.impl_path}
**Mode**: {"DRY RUN" if dry_run else "WRITTEN"}

### Generated Files
{files_list or "  (none)"}

### Spec Analysis
- Polynomial: {"✅" if spec_node.has_polynomial else "❌"} ({len(spec_node.polynomial.positions) if spec_node.polynomial else 0} positions)
- Operad: {"✅" if spec_node.has_operad else "❌"} ({len(spec_node.operad.operations) if spec_node.operad else 0} operations)
- AGENTESE: {"✅" if spec_node.agentese else "❌"} ({spec_node.agentese.path if spec_node.agentese else "none"})

{warnings_list}

{"To actually write files, run with `dry_run=false`" if dry_run else "✅ Files written successfully!"}
"""
        else:
            errors_list = "\n".join(f"  ❌ {e}" for e in result.errors)
            content = f"""## Compile Failed

**Spec**: {spec_path}
**Errors**:
{errors_list}
"""

        return BasicRendering(
            summary=f"Compile: {spec_node.full_path} → {'DRY RUN' if dry_run else 'WRITTEN'}",
            content=content,
            metadata={
                "spec_path": str(spec_file),
                "impl_path": result.impl_path,
                "success": result.success,
                "dry_run": dry_run,
                "generated_files": result.generated_files,
                "warnings": result.warnings,
            },
        )

    # Known Crown Jewel holons that span agents/ + services/
    _CROWN_JEWEL_HOLONS: frozenset[str] = frozenset(
        {
            "brain",
            "town",
            "atelier",
            "park",
            "f",
        }
    )

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.READS("impl/")],
        help="Extract spec from implementation",
    )
    async def reflect(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        impl_path: str | None = None,
        holon: str | None = None,
    ) -> Renderable:
        """
        Impl → Spec: Extract specification from implementation.

        The Reflect functor transforms ImplCat → SpecCat.
        Used to verify autopoiesis: Reflect(Compile(S)) ≅ S

        Args:
            impl_path: Path to impl directory (relative to kgents root or absolute)
                       e.g., "agents/town" or "impl/claude/agents/town"
            holon: Crown Jewel holon name (e.g., "town", "brain", "park")
                   Use this for jewels that span agents/ + services/
        """
        if not impl_path and not holon:
            return BasicRendering(
                summary="Reflect requires impl_path or holon",
                content="Usage:\n\n"
                "**Option 1 - By holon name** (recommended for Crown Jewels):\n"
                "  `kg self.system.reflect holon=town`\n\n"
                "**Option 2 - By path**:\n"
                "  `kg self.system.reflect impl_path=agents/town`\n\n"
                "**Crown Jewels** (use holon= for 100% coverage):\n"
                "  brain, atelier, f",
                metadata={"error": "missing_impl_path"},
            )

        # Import specgraph
        try:
            from ..specgraph import reflect_impl, reflect_jewel
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        kgents_root = self._get_kgents_root()
        impl_root = kgents_root / "impl" / "claude"

        # Determine reflection mode
        if holon:
            # Crown Jewel mode: use reflect_jewel (merges agents/ + services/)
            result = reflect_jewel(holon, impl_root)
            impl_dir = Path(result.impl_path)
            mode = "jewel"
        else:
            # Direct path mode (impl_path is guaranteed non-None here)
            assert impl_path is not None  # Already checked above
            impl_dir = Path(impl_path)
            if not impl_dir.is_absolute():
                # Try multiple resolutions
                candidates = [
                    impl_root / impl_path,
                    kgents_root / impl_path,
                ]
                for candidate in candidates:
                    if candidate.exists():
                        impl_dir = candidate
                        break

            if not impl_dir.exists():
                return BasicRendering(
                    summary=f"Impl directory not found: {impl_path}",
                    content=f"Tried:\n  - {impl_root / impl_path}\n  - {kgents_root / impl_path}",
                    metadata={"error": "directory_not_found"},
                )

            # Check if this is a Crown Jewel path and suggest holon= mode
            detected_holon = impl_dir.name
            is_jewel = detected_holon in self._CROWN_JEWEL_HOLONS

            if is_jewel:
                # Auto-upgrade to jewel mode for better coverage
                result = reflect_jewel(detected_holon, impl_root)
                mode = "jewel (auto)"
            else:
                result = reflect_impl(impl_dir)
                mode = "direct"

        if not result.spec_node:
            return BasicRendering(
                summary=f"Reflect failed: {holon or impl_path}",
                content=f"Could not extract spec structure.\nErrors: {result.errors}",
                metadata={"error": "reflect_failed", "errors": result.errors},
            )

        spec_node = result.spec_node

        # Format output
        content = f"""## Reflect Result

**Holon**: {spec_node.holon}
**Mode**: {mode} {"(Crown Jewel: merges agents/ + services/)" if "jewel" in mode else "(single directory)"}
**Confidence**: {result.confidence:.0%}

### Extracted Structure
- **Domain**: {spec_node.domain.value}
- **Holon**: {spec_node.holon}
- **AGENTESE Path**: {spec_node.full_path}

### Components Found
| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | {"✅" if spec_node.has_polynomial else "❌"} | {len(spec_node.polynomial.positions) if spec_node.polynomial else 0} positions |
| Operad | {"✅" if spec_node.has_operad else "❌"} | {len(spec_node.operad.operations) if spec_node.operad else 0} operations, {len(spec_node.operad.laws) if spec_node.operad else 0} laws |
| AGENTESE Node | {"✅" if spec_node.agentese else "❌"} | {spec_node.agentese.path if spec_node.agentese else "none"} |

### Generated Spec (YAML Frontmatter)

```yaml
{result.spec_content}```

---

**Next steps:**
1. Copy the YAML above to create/update `spec/{spec_node.holon}/index.md`
2. Run `kg self.system.audit` to verify alignment
3. Use `kg self.system.compile spec_path=spec/{spec_node.holon}/index.md` to regenerate
"""

        return BasicRendering(
            summary=f"Reflect: {spec_node.full_path} ({result.confidence:.0%} confidence)",
            content=content,
            metadata={
                "impl_path": str(impl_dir),
                "full_path": spec_node.full_path,
                "confidence": result.confidence,
                "mode": mode,
                "has_polynomial": spec_node.has_polynomial,
                "has_operad": spec_node.has_operad,
                "has_agentese": spec_node.agentese is not None,
                "spec_yaml": result.spec_content,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("impl/"), Effect.WRITES("spec/")],
        help="Apply evolution/mutation to system",
    )
    async def evolve(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        mutation: str | None = None,
    ) -> Renderable:
        """
        Apply consolidation/mutation to the system.

        Requires explicit confirmation from observer with appropriate capabilities.
        """
        # Check observer has evolve capability
        capabilities: frozenset[str] = frozenset()
        if hasattr(observer, "capabilities"):
            capabilities = observer.capabilities

        if "evolve" not in capabilities and "admin" not in capabilities:
            return BasicRendering(
                summary="Evolve requires elevated capabilities",
                content="Observer must have 'evolve' or 'admin' capability",
                metadata={"error": "insufficient_capabilities"},
            )

        if not mutation:
            return BasicRendering(
                summary="Evolve requires mutation specification",
                content="Usage: `kg self.system.evolve mutation=operad_unification`",
                metadata={"error": "missing_mutation"},
            )

        # TODO: Implement mutation application
        return BasicRendering(
            summary=f"Evolve: {mutation}",
            content=f"Would apply mutation: {mutation}",
            metadata={
                "mutation": mutation,
                "applied": False,
            },
        )

    def _get_git_log(self, limit: int = 10) -> list[dict[str, str]]:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--max-count={limit}",
                    "--format=%H|%an|%s|%ar",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parents[4],  # kgents root
                timeout=5,
            )
            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        commits.append(
                            {
                                "hash": parts[0][:8],
                                "author": parts[1],
                                "message": parts[2][:60] + ("..." if len(parts[2]) > 60 else ""),
                                "when": parts[3],
                            }
                        )
            return commits
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View history of system changes",
    )
    async def witness(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        limit: int = 10,
    ) -> Renderable:
        """
        History of changes: N-gent trace of system evolution.

        Shows recent commits, mutations, and evolution events.
        Uses git log as the source of truth for system history.
        """
        commits = self._get_git_log(limit)

        if not commits:
            return BasicRendering(
                summary="System History (unavailable)",
                content="Git history not available.",
                metadata={"limit": limit, "events": []},
            )

        # Build commit table
        commit_table = "\n".join(
            [
                f"| `{c['hash']}` | {c['author']:<15} | {c['message']:<50} | {c['when']} |"
                for c in commits
            ]
        )

        content = f"""
## System History (N-gent Trace)

Last {len(commits)} evolution events:

| Hash     | Author          | Message                                            | When |
|----------|-----------------|----------------------------------------------------| -----|
{commit_table}

---

### Evolution Patterns

The system evolves through:
1. **Operad Unification** - Consolidating composition grammars
2. **Path Registration** - Adding AGENTESE discoverability
3. **Jewel Compilation** - Implementing vertical slices

Run `kg self.system.audit` to see current system health.
"""
        return BasicRendering(
            summary=f"System History: {len(commits)} recent events",
            content=content,
            metadata={
                "limit": limit,
                "events": commits,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        aspect_methods: dict[str, Any] = {
            "audit": self.audit,
            "compile": self.compile,
            "reflect": self.reflect,
            "evolve": self.evolve,
            "witness": self.witness,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory Functions ===

_system_node: SystemNode | None = None


def get_system_node() -> SystemNode:
    """Get or create the singleton SystemNode."""
    global _system_node
    if _system_node is None:
        _system_node = SystemNode()
    return _system_node


def create_system_node() -> SystemNode:
    """Create a new SystemNode (for testing)."""
    return SystemNode()


# === Spec Command Node ===


SPEC_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "audit",
    "reflect",
    "gaps",
    "health",
)


@node("self.system.spec", description="Spec-Impl alignment commands (kg spec.*)")
@dataclass
class SpecCommandNode(BaseLogosNode):
    """
    self.system.spec - SpecGraph command interface.

    Provides convenient access to spec-impl alignment tools:
    - audit: Run full spec-impl audit
    - reflect: Reflect a specific holon to extract spec
    - gaps: Show actionable gaps only
    - health: Crown Jewel health dashboard

    These are the `kg spec.*` commands for DevEx.
    """

    _handle: str = "self.system.spec"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes get same affordances for spec commands."""
        return SPEC_AFFORDANCES

    def _get_kgents_root(self) -> Path:
        """Get the kgents project root directory."""
        return Path(__file__).parents[5]

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View spec command options",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        View available spec commands.

        Shows the four spec commands and their usage.
        """
        content = """## Spec Commands (`kg self.system.spec.*`)

These commands help you maintain spec-impl alignment.

### Available Commands

| Command | Description |
|---------|-------------|
| `self.system.spec.audit` | Run full spec-impl audit showing alignment status |
| `self.system.spec.reflect holon=<name>` | Reflect a holon to extract spec from impl |
| `self.system.spec.gaps [severity=<level>]` | Show only gaps in actionable format |
| `self.system.spec.health` | Crown Jewel health dashboard |

### Examples

```bash
# Check overall alignment
kg self.system.spec.audit

# See Crown Jewel health
kg self.system.spec.health

# Reflect a specific holon
kg self.system.spec.reflect holon=town

# Show only critical gaps
kg self.system.spec.gaps severity=critical
```

### Philosophy

> *"The spec is the compression. Reflect extracts; Compile expands. The fixed point is truth."*
"""

        return BasicRendering(
            summary="Spec Commands: 4 available",
            content=content,
            metadata={
                "commands": ["audit", "reflect", "gaps", "health"],
                "route": "/system/spec",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Run full spec-impl audit showing alignment status",
    )
    async def audit(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        verbose: bool = False,
    ) -> Renderable:
        """
        Run full spec-impl audit.

        Shorthand for running the full SpecGraph audit pipeline.
        Shows alignment score and lists all gaps.

        Args:
            verbose: If True, include file paths and additional details
        """
        try:
            from ..specgraph import full_audit, print_audit_report
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        kgents_root = self._get_kgents_root()
        spec_root = kgents_root / "spec"
        impl_root = kgents_root / "impl" / "claude"

        discovery, audit_report = full_audit(spec_root, impl_root)

        # Format report
        report_text = print_audit_report(audit_report, verbose=verbose)

        return BasicRendering(
            summary=f"Spec Audit: {audit_report.alignment_score:.1%} aligned ({len(audit_report.aligned)}/{audit_report.total_components})",
            content=report_text,
            metadata={
                "alignment_score": audit_report.alignment_score,
                "total_components": audit_report.total_components,
                "aligned_count": len(audit_report.aligned),
                "gap_count": len(audit_report.gaps),
                "critical_gaps": len(audit_report.critical_gaps),
                "specs_parsed": discovery.total_specs,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Reflect a specific holon to extract spec from impl",
    )
    async def reflect(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        holon: str | None = None,
    ) -> Renderable:
        """
        Reflect a specific holon to extract spec.

        Extracts polynomial, operad, and node from implementation,
        generating YAML frontmatter suitable for spec files.

        Args:
            holon: Crown Jewel name (e.g., "town", "brain", "park", "f")
        """
        if not holon:
            return BasicRendering(
                summary="Reflect requires holon name",
                content="Usage: `kg self.system.spec.reflect holon=town`\n\n"
                "**Available holons**: brain, atelier, f",
                metadata={"error": "missing_holon"},
            )

        try:
            from ..specgraph import reflect_jewel
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        kgents_root = self._get_kgents_root()
        impl_root = kgents_root / "impl" / "claude"

        result = reflect_jewel(holon, impl_root)

        if not result.spec_node:
            return BasicRendering(
                summary=f"Reflect failed: {holon}",
                content=f"Could not extract spec structure.\nErrors: {result.errors}",
                metadata={"error": "reflect_failed", "errors": result.errors},
            )

        spec = result.spec_node

        # Build confidence meter
        confidence_bar = "█" * int(result.confidence * 10) + "░" * (
            10 - int(result.confidence * 10)
        )

        content = f"""## Reflect: {holon}

**Confidence**: [{confidence_bar}] {result.confidence:.0%}
**Path**: {spec.full_path}

### Components Found

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | {"✅" if spec.has_polynomial else "❌"} | {len(spec.polynomial.positions) if spec.polynomial else 0} positions |
| Operad | {"✅" if spec.has_operad else "❌"} | {len(spec.operad.operations) if spec.operad else 0} ops, {len(spec.operad.laws) if spec.operad else 0} laws |
| Node | {"✅" if spec.agentese else "❌"} | {spec.agentese.path if spec.agentese else "none"} |

### Generated YAML Frontmatter

```yaml
{result.spec_content}```

---

Copy to `spec/{holon}/{holon}.md` to create/update spec.
"""

        return BasicRendering(
            summary=f"Reflect: {holon} ({result.confidence:.0%} confidence)",
            content=content,
            metadata={
                "holon": holon,
                "confidence": result.confidence,
                "full_path": spec.full_path,
                "has_polynomial": spec.has_polynomial,
                "has_operad": spec.has_operad,
                "has_node": spec.agentese is not None,
                "yaml": result.spec_content,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show only gaps in actionable format",
    )
    async def gaps(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        severity: str | None = None,
    ) -> Renderable:
        """
        Show only gaps in actionable format.

        Focused view of what needs to be fixed, grouped by holon.

        Args:
            severity: Filter by severity: "critical", "important", or "minor"
        """
        try:
            from ..specgraph import GapSeverity, full_audit
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        kgents_root = self._get_kgents_root()
        spec_root = kgents_root / "spec"
        impl_root = kgents_root / "impl" / "claude"

        _, audit_report = full_audit(spec_root, impl_root)

        # Filter gaps by severity if specified
        gaps = audit_report.gaps
        if severity:
            try:
                sev = GapSeverity(severity.lower())
                gaps = [g for g in gaps if g.severity == sev]
            except ValueError:
                return BasicRendering(
                    summary="Invalid severity",
                    content=f"Valid severities: critical, important, minor\nGot: {severity}",
                    metadata={"error": "invalid_severity"},
                )

        if not gaps:
            return BasicRendering(
                summary="✅ No gaps found!",
                content="All specs are aligned with implementations.\n\nRun `kg self.system.spec.health` to see Crown Jewel status.",
                metadata={"gap_count": 0},
            )

        # Group gaps by holon
        gaps_by_holon: dict[str, list[Any]] = {}
        for gap in gaps:
            holon = gap.spec_path.split(".")[-1]
            if holon not in gaps_by_holon:
                gaps_by_holon[holon] = []
            gaps_by_holon[holon].append(gap)

        # Build actionable list
        lines = ["## Gaps to Fix\n"]
        for holon, holon_gaps in sorted(gaps_by_holon.items()):
            lines.append(f"### {holon}")
            for gap in holon_gaps:
                icon = {"critical": "🔴", "important": "🟡", "minor": "⚪"}[gap.severity.value]
                lines.append(f"- {icon} **{gap.component.value}**: {gap.message}")
            lines.append("")

        lines.append("---")
        lines.append("\n**To fix**: Create missing files or update spec YAML frontmatter.")

        return BasicRendering(
            summary=f"Gaps: {len(gaps)} {'(' + severity + ')' if severity else ''}",
            content="\n".join(lines),
            metadata={
                "gap_count": len(gaps),
                "filter": severity,
                "by_holon": {h: len(g) for h, g in gaps_by_holon.items()},
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Crown Jewel health dashboard",
    )
    async def health(
        self,
        observer: Observer | "Umwelt[Any, Any]",
    ) -> Renderable:
        """
        Crown Jewel health dashboard.

        Shows confidence scores for all 6 Crown Jewels based on
        what's implemented vs what's specified.
        """
        try:
            from ..specgraph import reflect_crown_jewels
        except ImportError as e:
            return BasicRendering(
                summary="SpecGraph not available",
                content=f"Failed to import specgraph: {e}",
                metadata={"error": "import_error"},
            )

        kgents_root = self._get_kgents_root()
        impl_root = kgents_root / "impl" / "claude"

        results = reflect_crown_jewels(impl_root)

        # Build health table
        table_rows = []
        all_healthy = True
        total_confidence = 0.0

        for holon, result in sorted(results.items(), key=lambda x: x[1].confidence, reverse=True):
            spec = result.spec_node
            conf = result.confidence
            total_confidence += conf

            status = "✅" if conf >= 1.0 else ("🟡" if conf >= 0.66 else "❌")
            if conf < 1.0:
                all_healthy = False

            poly_str = f"{len(spec.polynomial.positions)} pos" if spec and spec.polynomial else "—"
            operad_str = f"{len(spec.operad.operations)} ops" if spec and spec.operad else "—"
            node_str = spec.agentese.path if spec and spec.agentese else "—"

            table_rows.append(
                f"| {status} {holon:<10} | {conf:.0%} | {poly_str:<8} | {operad_str:<8} | {node_str:<15} |"
            )

        avg_confidence = total_confidence / len(results) if results else 0.0

        content = f"""## Crown Jewel Health

**Overall**: {avg_confidence:.0%} average confidence
**Status**: {"✅ All Healthy" if all_healthy else "⚠️ Needs Attention"}

| Jewel       | Conf | Polynomial | Operad   | AGENTESE Path   |
|-------------|------|------------|----------|-----------------|
{chr(10).join(table_rows)}

---

### Legend
- ✅ 100% - All components present and extractable
- 🟡 67%+ - Partial implementation
- ❌ <67% - Critical components missing

### Next Steps
{"✅ All Crown Jewels are healthy!" if all_healthy else "Run `kg self.system.spec.gaps` to see what needs fixing."}
"""

        return BasicRendering(
            summary=f"Crown Jewel Health: {avg_confidence:.0%} avg ({len(results)} jewels)",
            content=content,
            metadata={
                "average_confidence": avg_confidence,
                "all_healthy": all_healthy,
                "jewels": {
                    h: {
                        "confidence": r.confidence,
                        "path": r.spec_node.full_path if r.spec_node else None,
                    }
                    for h, r in results.items()
                },
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        aspect_methods: dict[str, Any] = {
            "manifest": self.manifest,
            "audit": self.audit,
            "reflect": self.reflect,
            "gaps": self.gaps,
            "health": self.health,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


_spec_node: SpecCommandNode | None = None


def get_spec_node() -> SpecCommandNode:
    """Get or create the singleton SpecCommandNode."""
    global _spec_node
    if _spec_node is None:
        _spec_node = SpecCommandNode()
    return _spec_node


# === Exports ===

__all__ = [
    # Types
    "DriftStatus",
    "DriftReport",
    "AuditResult",
    "CompileResult",
    "ReflectResult",
    # Constants
    "SYSTEM_AFFORDANCES",
    "SPEC_AFFORDANCES",
    # Nodes
    "SystemNode",
    "SpecCommandNode",
    # Factory
    "get_system_node",
    "create_system_node",
    "get_spec_node",
]
