"""
SpecGraph: Autopoietic Spec-Impl Compilation Infrastructure.

The SpecGraph provides the three functors for autopoiesis:

    SpecCat ──Compile──▶ ImplCat ──Project──▶ PathCat
        ▲                    │                    │
        │                    ▼                    │
        └────Reflect────◀ DriftCheck ◀───────────┘

Modules:
- types: Core data structures (SpecNode, SpecGraph, DriftReport)
- parser: Parse YAML frontmatter from spec/*.md files
- compile: Generate impl scaffolding from spec
- reflect: Extract spec structure from impl
- drift: Compare spec vs impl and detect divergence
- discovery: Spec-driven gap detection and stub generation (Option C)

Usage:
    from protocols.agentese.specgraph import (
        parse_spec_file,
        compile_spec,
        reflect_impl,
        check_drift,
        # Discovery mode (Option C)
        discover_from_spec,
        audit_impl,
        generate_stubs,
        full_audit,
    )

    # Parse a spec
    node = parse_spec_file(Path("spec/town/operad.md"))

    # Compile to impl (dry run)
    result = compile_spec(node, Path("impl/claude/"), dry_run=True)

    # Reflect from impl (single directory)
    reflected = reflect_impl(Path("impl/claude/agents/town"))

    # Reflect Crown Jewel (merges agents/ + services/)
    # Use this for holons that span both directories
    town_reflected = reflect_jewel("town", Path("impl/claude/"))

    # Check drift
    drift = check_drift(
        Path("spec/town/operad.md"),
        Path("impl/claude/agents/town"),
    )

    # Discovery mode (Option C: Hybrid Spec-Driven Discovery)
    discovery, audit = full_audit(spec_root, impl_root)
    print(print_audit_report(audit))
    if audit.has_gaps:
        result = generate_stubs(audit.gaps, impl_root, dry_run=False)

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from .compile import compile_spec
from .discovery import (
    AuditReport,
    ComponentType,
    DiscoveryReport,
    Gap,
    GapSeverity,
    StubResult,
    audit_impl,
    discover_from_spec,
    full_audit,
    generate_stubs,
    print_audit_report,
)
from .drift import audit_all_jewels, check_drift
from .parser import (
    ParseError,
    generate_frontmatter,
    parse_frontmatter,
    parse_spec_directory,
    parse_spec_file,
)
from .reflect import (
    reflect_crown_jewels,
    reflect_impl,
    reflect_jewel,
    reflect_node,
    reflect_operad,
    reflect_polynomial,
)
from .types import (
    AgentesePath,
    AspectCategory,
    AspectSpec,
    CompileResult,
    DriftReport,
    DriftStatus,
    LawSpec,
    OperadSpec,
    OperationSpec,
    PolynomialSpec,
    ReflectResult,
    ServiceSpec,
    SheafSpec,
    SpecDomain,
    SpecGraph,
    SpecNode,
)

__all__ = [
    # Enums
    "SpecDomain",
    "DriftStatus",
    "AspectCategory",
    # Spec components
    "PolynomialSpec",
    "OperationSpec",
    "LawSpec",
    "OperadSpec",
    "SheafSpec",
    "AspectSpec",
    "AgentesePath",
    "ServiceSpec",
    # Core types
    "SpecNode",
    "SpecGraph",
    # Results
    "CompileResult",
    "ReflectResult",
    "DriftReport",
    # Discovery types
    "GapSeverity",
    "ComponentType",
    "Gap",
    "DiscoveryReport",
    "AuditReport",
    "StubResult",
    # Parser
    "ParseError",
    "parse_frontmatter",
    "parse_spec_file",
    "parse_spec_directory",
    "generate_frontmatter",
    # Compile
    "compile_spec",
    # Reflect
    "reflect_polynomial",
    "reflect_operad",
    "reflect_node",
    "reflect_impl",
    "reflect_jewel",
    "reflect_crown_jewels",
    # Drift
    "check_drift",
    "audit_all_jewels",
    # Discovery (Option C)
    "discover_from_spec",
    "audit_impl",
    "generate_stubs",
    "full_audit",
    "print_audit_report",
]
