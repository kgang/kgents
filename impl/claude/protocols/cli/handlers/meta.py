"""
Meta Handler: Meta-Construction Visualization.

DevEx for the generative machinery: primitives, operads, sheaves.

Usage:
    kgents meta                   # Show meta-construction health
    kgents meta primitives        # List all 17 primitives
    kgents meta operads           # List all 7 operads
    kgents meta soul              # Visualize KENT_SOUL emergence
    kgents meta laws              # Verify operad laws

Examples:
    $ kgents meta
    [META] Meta-Construction Health
      Primitives: 17 (7 bootstrap, 3 perception, 3 entropy, 2 memory, 2 teleological)
      Operads: 7 (1 universal + 6 domain)
      Contexts: 6 (eigenvector soul contexts)
      KENT_SOUL: 6 local souls → 1 emergent global

    $ kgents meta soul
    [META] KENT_SOUL Emergence Visualization

      AESTHETIC ──┐
      CATEGORICAL ─┤
      GRATITUDE ───┼──▶ KENT_SOUL (emergent)
      HETERARCHY ──┤
      GENERATIVITY ┤
      JOY ─────────┘

The Key Insight:
    The emergent soul has capabilities NO single local soul possesses.
    This is mathematically-grounded emergence via sheaf gluing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for meta command."""
    print(__doc__)


def cmd_meta(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Meta-construction visualization.

    Shows health and structure of the generative machinery.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    if not args:
        return _show_health(ctx)

    subcommand = args[0].lower()

    match subcommand:
        case "health":
            return _show_health(ctx)
        case "primitives":
            return _show_primitives(ctx)
        case "operads":
            return _show_operads(ctx)
        case "soul":
            return _show_soul(ctx)
        case "laws":
            return _verify_laws(ctx)
        case _:
            _emit(
                f"[META] Unknown subcommand: {subcommand}", {"error": subcommand}, ctx
            )
            return 1


def _show_health(ctx: "InvocationContext | None") -> int:
    """Show meta-construction health overview."""
    from agents.operad.core import OperadRegistry
    from agents.operad.domains import (
        EVOLUTION_OPERAD,
        MEMORY_OPERAD,
        NARRATIVE_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        SOUL_OPERAD,
    )
    from agents.poly import PRIMITIVES
    from agents.sheaf import (
        AESTHETIC,
        CATEGORICAL,
        GENERATIVITY,
        GRATITUDE,
        HETERARCHY,
        JOY,
        SOUL_SHEAF,
    )

    # Ensure operads registered
    for operad in [
        SOUL_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        MEMORY_OPERAD,
        EVOLUTION_OPERAD,
        NARRATIVE_OPERAD,
    ]:
        OperadRegistry.register(operad)

    # Count primitives by category
    bootstrap = ["id", "ground", "judge", "contradict", "sublate", "compose", "fix"]
    perception = ["manifest", "witness", "lens"]
    entropy = ["sip", "tithe", "define"]
    memory = ["remember", "forget"]
    teleological = ["evolve", "narrate"]

    n_primitives = len(PRIMITIVES)
    n_operads = len(OperadRegistry.all_operads())
    n_contexts = len(SOUL_SHEAF.contexts)

    _emit(
        "[META] Meta-Construction Health",
        {"status": "healthy"},
        ctx,
    )
    _emit("", {}, ctx)

    # Primitives
    _emit(
        f"  Primitives: {n_primitives}",
        {"primitives": n_primitives},
        ctx,
    )
    _emit(
        f"    Bootstrap:    {len(bootstrap)} (id, ground, judge, contradict, sublate, compose, fix)",
        {"bootstrap": len(bootstrap)},
        ctx,
    )
    _emit(
        f"    Perception:   {len(perception)} (manifest, witness, lens)",
        {"perception": len(perception)},
        ctx,
    )
    _emit(
        f"    Entropy:      {len(entropy)} (sip, tithe, define)",
        {"entropy": len(entropy)},
        ctx,
    )
    _emit(
        f"    Memory:       {len(memory)} (remember, forget)",
        {"memory": len(memory)},
        ctx,
    )
    _emit(
        f"    Teleological: {len(teleological)} (evolve, narrate)",
        {"teleological": len(teleological)},
        ctx,
    )

    _emit("", {}, ctx)

    # Operads
    operads = OperadRegistry.all_operads()
    domain_operads = [n for n in operads if n != "AgentOperad"]
    _emit(
        f"  Operads: {n_operads} (1 universal + {len(domain_operads)} domain)",
        {"operads": n_operads},
        ctx,
    )
    _emit(
        "    Universal: AgentOperad (seq, par, branch, fix, trace)",
        {"universal": "AgentOperad"},
        ctx,
    )
    for name in sorted(domain_operads):
        operad = operads[name]
        domain_ops = [
            op
            for op in operad.operations.keys()
            if op not in ["seq", "par", "branch", "fix", "trace"]
        ]
        _emit(
            f"    {name}: {', '.join(domain_ops[:3])}{'...' if len(domain_ops) > 3 else ''}",
            {"operad": name, "ops": domain_ops},
            ctx,
        )

    _emit("", {}, ctx)

    # Contexts
    contexts = [AESTHETIC, CATEGORICAL, GRATITUDE, HETERARCHY, GENERATIVITY, JOY]
    _emit(
        f"  Contexts: {n_contexts} (eigenvector soul contexts)",
        {"contexts": n_contexts},
        ctx,
    )
    for c in contexts:
        caps = ", ".join(sorted(c.capabilities)[:3])
        _emit(
            f"    {c.name}: {caps}",
            {"context": c.name},
            ctx,
        )

    _emit("", {}, ctx)

    # Emergence
    _emit(
        "  KENT_SOUL: 6 local souls → 1 emergent global",
        {"emergence": "6 → 1"},
        ctx,
    )
    _emit(
        "    The emergent soul has capabilities NO single local soul possesses.",
        {},
        ctx,
    )

    return 0


def _show_primitives(ctx: "InvocationContext | None") -> int:
    """List all primitives with details."""
    from agents.poly import PRIMITIVES

    _emit(
        "[META] Primitives (17 atomic polynomial agents)",
        {"count": len(PRIMITIVES)},
        ctx,
    )
    _emit("", {}, ctx)

    categories = {
        "Bootstrap (7)": [
            "id",
            "ground",
            "judge",
            "contradict",
            "sublate",
            "compose",
            "fix",
        ],
        "Perception (3)": ["manifest", "witness", "lens"],
        "Entropy (3)": ["sip", "tithe", "define"],
        "Memory (2)": ["remember", "forget"],
        "Teleological (2)": ["evolve", "narrate"],
    }

    for category, names in categories.items():
        _emit(f"  {category}:", {"category": category}, ctx)
        for name in names:
            p = PRIMITIVES.get(name)
            if p:
                _emit(
                    f"    {name.upper()}: {len(p.positions)} positions",
                    {"primitive": name, "positions": len(p.positions)},
                    ctx,
                )
        _emit("", {}, ctx)

    return 0


def _show_operads(ctx: "InvocationContext | None") -> int:
    """List all operads with operations."""
    from agents.operad.core import OperadRegistry
    from agents.operad.domains import (
        EVOLUTION_OPERAD,
        MEMORY_OPERAD,
        NARRATIVE_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        SOUL_OPERAD,
    )

    # Ensure operads registered
    for operad in [
        SOUL_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        MEMORY_OPERAD,
        EVOLUTION_OPERAD,
        NARRATIVE_OPERAD,
    ]:
        OperadRegistry.register(operad)

    operads = OperadRegistry.all_operads()

    _emit(
        f"[META] Operads ({len(operads)} registered)",
        {"count": len(operads)},
        ctx,
    )
    _emit("", {}, ctx)

    universal = ["seq", "par", "branch", "fix", "trace"]

    for name, operad in sorted(operads.items()):
        all_ops = list(operad.operations.keys())
        domain_ops = [op for op in all_ops if op not in universal]

        _emit(
            f"  {name}:",
            {"operad": name},
            ctx,
        )
        _emit(
            f"    {operad.description}",
            {"description": operad.description},
            ctx,
        )
        _emit(
            f"    Operations: {len(all_ops)} ({len(domain_ops)} domain-specific)",
            {"operations": len(all_ops)},
            ctx,
        )
        if domain_ops:
            _emit(
                f"    Domain: {', '.join(domain_ops)}",
                {"domain_ops": domain_ops},
                ctx,
            )
        _emit(
            f"    Laws: {len(operad.laws)}",
            {"laws": len(operad.laws)},
            ctx,
        )
        _emit("", {}, ctx)

    return 0


def _show_soul(ctx: "InvocationContext | None") -> int:
    """Visualize KENT_SOUL emergence."""
    from agents.sheaf import KENT_SOUL, query_soul
    from agents.sheaf.protocol import (
        AESTHETIC,
        CATEGORICAL,
        GENERATIVITY,
        GRATITUDE,
        HETERARCHY,
        JOY,
    )

    _emit(
        "[META] KENT_SOUL Emergence Visualization",
        {"visualization": "soul"},
        ctx,
    )
    _emit("", {}, ctx)

    # ASCII art visualization
    _emit(
        "  AESTHETIC ────────┐",
        {},
        ctx,
    )
    _emit(
        "  CATEGORICAL ──────┤",
        {},
        ctx,
    )
    _emit(
        "  GRATITUDE ────────┼───▶ KENT_SOUL (emergent)",
        {},
        ctx,
    )
    _emit(
        "  HETERARCHY ───────┤",
        {},
        ctx,
    )
    _emit(
        "  GENERATIVITY ─────┤",
        {},
        ctx,
    )
    _emit(
        "  JOY ──────────────┘",
        {},
        ctx,
    )

    _emit("", {}, ctx)

    # Show each local soul's question
    _emit(
        "  Local Souls (each asks a different question):",
        {},
        ctx,
    )

    contexts = [
        (AESTHETIC, "Does this need to exist?", "minimalism"),
        (CATEGORICAL, "What's the morphism?", "abstraction"),
        (GRATITUDE, "What deserves more respect?", "sacred lean"),
        (HETERARCHY, "Could this be peer-to-peer?", "peer lean"),
        (GENERATIVITY, "What can this generate?", "generation lean"),
        (JOY, "Where's the delight?", "playfulness"),
    ]

    for context, question, metric in contexts:
        result = query_soul("test input", context)
        value = result.get(metric.replace(" ", "_"), result.get(metric.split()[0], 0))
        _emit(
            f'    {context.name}: "{question}" ({metric}: {value})',
            {"context": context.name, "question": question},
            ctx,
        )

    _emit("", {}, ctx)

    # Show emergent capabilities
    _emit(
        "  Emergent Capabilities (global soul only):",
        {},
        ctx,
    )
    _emit(
        "    - Can answer questions in ANY eigenvector context",
        {},
        ctx,
    )
    _emit(
        "    - Combines constraints from ALL 6 local souls",
        {},
        ctx,
    )
    _emit(
        "    - Has positions = union of all local positions",
        {},
        ctx,
    )
    _emit(
        f"    - Total positions: {len(KENT_SOUL.positions)}",
        {"positions": len(KENT_SOUL.positions)},
        ctx,
    )

    _emit("", {}, ctx)

    # Sample query
    _emit(
        "  Sample Query:",
        {},
        ctx,
    )
    result = query_soul("Should I add this feature?")
    _emit(
        '    Input: "Should I add this feature?"',
        {},
        ctx,
    )
    _emit(
        f"    Response context: {result.get('context', 'global')}",
        {},
        ctx,
    )
    _emit(
        f"    Question asked: {result.get('question', 'N/A')}",
        {},
        ctx,
    )
    _emit(
        f"    Judgment: {result.get('judgment', 'N/A')}",
        {},
        ctx,
    )

    return 0


def _verify_laws(ctx: "InvocationContext | None") -> int:
    """Verify operad laws."""
    from agents.operad.core import OperadRegistry
    from agents.operad.domains import (
        EVOLUTION_OPERAD,
        MEMORY_OPERAD,
        NARRATIVE_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        SOUL_OPERAD,
    )
    from agents.poly import from_function

    # Ensure operads registered
    for operad in [
        SOUL_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        MEMORY_OPERAD,
        EVOLUTION_OPERAD,
        NARRATIVE_OPERAD,
    ]:
        OperadRegistry.register(operad)

    _emit(
        "[META] Operad Law Verification",
        {},
        ctx,
    )
    _emit("", {}, ctx)

    # Test agents
    a: Any = from_function("A", lambda x: x)
    b: Any = from_function("B", lambda x: x)
    c: Any = from_function("C", lambda x: x)

    total_laws = 0
    passed_laws = 0

    for name, operad in sorted(OperadRegistry.all_operads().items()):
        _emit(
            f"  {name}:",
            {"operad": name},
            ctx,
        )

        for law in operad.laws:
            total_laws += 1
            try:
                result = law.verify(a, b, c)
                status = "PASS" if result.passed else "FAIL"
                if result.passed:
                    passed_laws += 1
                _emit(
                    f"    [{status}] {law.name}: {law.equation}",
                    {"law": law.name, "status": status},
                    ctx,
                )
            except Exception as e:
                _emit(
                    f"    [ERR] {law.name}: {e}",
                    {"law": law.name, "error": str(e)},
                    ctx,
                )

        _emit("", {}, ctx)

    _emit(
        f"  Summary: {passed_laws}/{total_laws} laws verified",
        {"passed": passed_laws, "total": total_laws},
        ctx,
    )

    return 0


def _emit(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
