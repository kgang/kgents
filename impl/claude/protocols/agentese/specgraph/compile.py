"""
SpecGraph Compile Functor: Spec -> Impl generation.

The Compile functor transforms SpecCat -> ImplCat:
- Input: SpecNode with polynomial/operad/sheaf/agentese blocks
- Output: Python module scaffolding that compiles

This is NOT a full code generator - it generates scaffolding with TODOs.
The generated code should compile and pass basic smoke tests.

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent, indent

from .types import (
    CompileResult,
    OperadSpec,
    PolynomialSpec,
    SpecNode,
)

# === Code Templates ===


POLYNOMIAL_TEMPLATE = '''\
"""
{holon_title}Polynomial: {description}

Auto-generated from: {source_path}
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent


# =============================================================================
# Phase Enum (Positions in the Polynomial)
# =============================================================================


class {phase_enum}(Enum):
    """
    Positions in the {holon} polynomial.

    These are interpretive frames, not internal states.
    """

{phase_members}


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class {holon_title}Input:
    """Generic input for {holon} transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class {holon_title}Output:
    """Output from {holon} transitions."""

    phase: {phase_enum}
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def {directions_fn}(phase: {phase_enum}) -> FrozenSet[Any]:
    """
    Valid inputs for each {holon} phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({{Any}})


# =============================================================================
# Transition Function
# =============================================================================


def {transition_fn}(
    phase: {phase_enum}, input: Any
) -> tuple[{phase_enum}, {holon_title}Output]:
    """
    {holon_title} state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, {holon_title}Output(
        phase=phase,
        success=True,
        message=f"Processed {{type(input).__name__}} in {{phase.name}}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


{polynomial_name}: PolyAgent[{phase_enum}, Any, {holon_title}Output] = PolyAgent(
    name="{holon_title}Polynomial",
    positions=frozenset({phase_enum}),
    _directions={directions_fn},
    _transition={transition_fn},
)
"""
The {holon_title} polynomial agent.

Positions: {position_count} phases
Generated from: {source_path}
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "{phase_enum}",
    # Input/Output
    "{holon_title}Input",
    "{holon_title}Output",
    # Functions
    "{directions_fn}",
    "{transition_fn}",
    # Polynomial
    "{polynomial_name}",
]
'''


OPERAD_TEMPLATE = '''\
"""
{holon_title}Operad: Formal Composition Grammar for {holon_title}.

Auto-generated from: {source_path}
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function


# =============================================================================
# Operations
# =============================================================================

{operation_functions}

# =============================================================================
# Laws
# =============================================================================

{law_functions}

# =============================================================================
# Operad Creation
# =============================================================================


def create_{holon}_operad() -> Operad:
    """
    Create the {holon_title} Operad.

    Extends AGENT_OPERAD with {holon}-specific operations.
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add {holon}-specific operations
{add_operations}

    # Inherit universal laws and add {holon}-specific ones
    laws = list(AGENT_OPERAD.laws) + [
{add_laws}
    ]

    return Operad(
        name="{holon_title}Operad",
        operations=ops,
        laws=laws,
        description="Composition grammar for {holon_title}",
    )


# =============================================================================
# Global Operad Instance
# =============================================================================


{operad_name} = create_{holon}_operad()
"""
The {holon_title} Operad.

Operations: {operation_count}
Laws: {law_count}
Generated from: {source_path}
"""

# Register with the operad registry
OperadRegistry.register({operad_name})


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "{operad_name}",
    "create_{holon}_operad",
]
'''


NODE_TEMPLATE = '''\
"""
{holon_title} AGENTESE Node: {path}

Auto-generated from: {source_path}
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Affordances
# =============================================================================


{holon_upper}_AFFORDANCES: tuple[str, ...] = {aspects}


# =============================================================================
# Node Implementation
# =============================================================================


@node("{path}", description="{holon_title} service")
@dataclass
class {holon_title}Node(BaseLogosNode):
    """
    {path} - {holon_title} AGENTESE node.

    TODO: Implement aspect methods.
    """

    _handle: str = "{path}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return {holon_upper}_AFFORDANCES

{aspect_methods}

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        aspect_methods: dict[str, Any] = {{
{aspect_routing}
        }}

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {{aspect}}")


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "{holon_upper}_AFFORDANCES",
    "{holon_title}Node",
]
'''


# === Code Generators ===


def _title_case(s: str) -> str:
    """Convert snake_case or kebab-case to TitleCase."""
    return "".join(word.capitalize() for word in s.replace("-", "_").split("_"))


def _generate_polynomial_code(node: SpecNode) -> str:
    """Generate polynomial.py code from spec."""
    if not node.polynomial:
        return ""

    holon = node.holon
    holon_title = _title_case(holon)
    phase_enum = f"{holon_title}Phase"
    polynomial_name = (
        f"{holon_upper}_POLYNOMIAL" if (holon_upper := holon.upper()) else "POLYNOMIAL"
    )

    # Generate phase enum members
    phase_members = "\n".join(f"    {pos.upper()} = auto()" for pos in node.polynomial.positions)

    # Use provided function names or generate defaults
    transition_fn = node.polynomial.transition_fn or f"{holon}_transition"
    directions_fn = node.polynomial.directions_fn or f"{holon}_directions"

    return POLYNOMIAL_TEMPLATE.format(
        holon=holon,
        holon_title=holon_title,
        holon_upper=holon.upper(),
        description=f"State machine for {holon_title}",
        source_path=node.source_path,
        phase_enum=phase_enum,
        phase_members=phase_members,
        transition_fn=transition_fn,
        directions_fn=directions_fn,
        polynomial_name=polynomial_name,
        position_count=len(node.polynomial.positions),
    )


def _generate_operation_function(op_name: str, arity: int, signature: str) -> str:
    """Generate a single operation compose function.

    Handles:
    - Fixed arity (arity > 0): generates named parameters
    - Variadic (arity == -1 or arity == 0): generates *args
    """
    # Handle variadic operations (arity -1 or 0)
    if arity <= 0:
        params = "*agents: PolyAgent[Any, Any, Any]"
        param_names_expr = "[a.name for a in agents]"
        name_format = "', '.join(a.name for a in agents)"
        return dedent(f'''\
            def _{op_name}_compose(
                {params},
            ) -> PolyAgent[Any, Any, Any]:
                """
                Compose a {op_name} operation (variadic).

                {signature}
                """

                def {op_name}_fn(input: Any) -> dict[str, Any]:
                    return {{
                        "operation": "{op_name}",
                        "participants": {param_names_expr},
                        "input": input,
                    }}

                return from_function(f"{op_name}({{{name_format}}})", {op_name}_fn)
        ''')

    # Fixed arity
    params = ", ".join(f"agent_{chr(97 + i)}: PolyAgent[Any, Any, Any]" for i in range(arity))
    param_names = ", ".join(f"agent_{chr(97 + i)}.name" for i in range(arity))

    return dedent(f'''\
        def _{op_name}_compose(
            {params},
        ) -> PolyAgent[Any, Any, Any]:
            """
            Compose a {op_name} operation.

            {signature}
            """

            def {op_name}_fn(input: Any) -> dict[str, Any]:
                return {{
                    "operation": "{op_name}",
                    "participants": [{param_names}],
                    "input": input,
                }}

            return from_function(f"{op_name}({{{param_names}}})", {op_name}_fn)
    ''')


def _generate_law_function(law_name: str, equation: str) -> str:
    """Generate a single law verify function."""
    return dedent(f'''\
        def _verify_{law_name}(
            *agents: PolyAgent[Any, Any, Any],
            context: Any = None,
        ) -> LawVerification:
            """
            Verify: {equation}

            TODO: Implement actual verification logic.
            """
            return LawVerification(
                law_name="{law_name}",
                status=LawStatus.PASSED,
                message="{law_name} verification pending implementation",
            )
    ''')


def _generate_operad_code(node: SpecNode) -> str:
    """Generate operad.py code from spec."""
    if not node.operad:
        return ""

    holon = node.holon
    holon_title = _title_case(holon)
    operad_name = f"{holon.upper()}_OPERAD"

    # Generate operation functions
    op_functions = []
    add_ops = []
    for op in node.operad.operations:
        op_functions.append(_generate_operation_function(op.name, op.arity, op.signature))
        add_ops.append(
            f'    ops["{op.name}"] = Operation(\n'
            f'        name="{op.name}",\n'
            f"        arity={op.arity},\n"
            f'        signature="{op.signature}",\n'
            f"        compose=_{op.name}_compose,\n"
            f'        description="{op.description}",\n'
            f"    )"
        )

    # Generate law functions
    law_functions = []
    add_laws = []
    for law in node.operad.laws:
        law_functions.append(_generate_law_function(law.name, law.equation))
        add_laws.append(
            f"        Law(\n"
            f'            name="{law.name}",\n'
            f'            equation="{law.equation}",\n'
            f"            verify=_verify_{law.name},\n"
            f'            description="{law.description}",\n'
            f"        ),"
        )

    return OPERAD_TEMPLATE.format(
        holon=holon,
        holon_title=holon_title,
        source_path=node.source_path,
        operation_functions="\n\n".join(op_functions)
        if op_functions
        else "# No operations defined",
        law_functions="\n\n".join(law_functions) if law_functions else "# No laws defined",
        add_operations="\n".join(add_ops) if add_ops else "    pass  # No operations",
        add_laws="\n".join(add_laws) if add_laws else "        # No laws",
        operad_name=operad_name,
        operation_count=len(node.operad.operations),
        law_count=len(node.operad.laws),
    )


def _generate_aspect_method(aspect_name: str) -> str:
    """Generate a single aspect method."""
    return dedent(f'''\
        @aspect(
            category=AspectCategory.PERCEPTION,
            effects=[],
            help="{aspect_name.title()} aspect",
        )
        async def {aspect_name}(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
            """
            {aspect_name.title()} aspect.

            TODO: Implement actual logic.
            """
            return BasicRendering(
                summary="{aspect_name.title()}",
                content="TODO: Implement {aspect_name}",
                metadata={{}},
            )
    ''')


def _generate_node_code(node: SpecNode) -> str:
    """Generate node.py code from spec."""
    if not node.agentese:
        return ""

    holon = node.holon
    holon_title = _title_case(holon)
    path = node.agentese.path
    aspects = node.agentese.aspects or ("manifest",)

    # Generate aspect methods
    aspect_methods = []
    aspect_routing = []
    for aspect_name in aspects:
        aspect_methods.append(indent(_generate_aspect_method(aspect_name), "    "))
        aspect_routing.append(f'            "{aspect_name}": self.{aspect_name},')

    return NODE_TEMPLATE.format(
        holon=holon,
        holon_title=holon_title,
        holon_upper=holon.upper(),
        path=path,
        source_path=node.source_path,
        aspects=repr(aspects),
        aspect_methods="\n".join(aspect_methods) if aspect_methods else "    pass",
        aspect_routing="\n".join(aspect_routing),
    )


# === Main Compile Function ===


def compile_spec(
    node: SpecNode,
    impl_root: Path,
    dry_run: bool = False,
) -> CompileResult:
    """
    Compile a SpecNode into implementation files.

    Args:
        node: The parsed spec node
        impl_root: Root of impl directory (e.g., impl/claude/)
        dry_run: If True, don't write files, just report what would be generated

    Returns:
        CompileResult with generated files and any errors
    """
    result = CompileResult(
        spec_path=str(node.source_path),
        impl_path="",
        success=True,
        generated_files=[],
        errors=[],
        warnings=[],
    )

    # Determine output directory based on domain
    if node.domain.value == "world":
        # world.town -> agents/town/
        output_dir = impl_root / "agents" / node.holon
    elif node.domain.value == "self":
        # self.memory -> agents/brain/ (special case) or services/<holon>/
        if node.holon == "memory":
            output_dir = impl_root / "agents" / "brain"
        else:
            output_dir = impl_root / "services" / node.holon
    elif node.domain.value == "concept":
        # concept.gardener -> protocols/agentese/contexts/
        output_dir = impl_root / "protocols" / "agentese" / "contexts"
    else:
        output_dir = impl_root / "agents" / node.holon

    result.impl_path = str(output_dir)

    # Generate files
    files_to_write: list[tuple[Path, str]] = []

    # Generate polynomial.py
    if node.polynomial:
        poly_code = _generate_polynomial_code(node)
        if poly_code:
            files_to_write.append((output_dir / "polynomial.py", poly_code))

    # Generate operad.py
    if node.operad:
        operad_code = _generate_operad_code(node)
        if operad_code:
            files_to_write.append((output_dir / "operad.py", operad_code))

    # Generate node.py
    if node.agentese:
        node_code = _generate_node_code(node)
        if node_code:
            files_to_write.append((output_dir / "node.py", node_code))

    # Write files (or report in dry run)
    for file_path, content in files_to_write:
        result.generated_files.append(str(file_path))
        if not dry_run:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
            except OSError as e:
                result.errors.append(f"Failed to write {file_path}: {e}")
                result.success = False

    # Add warnings for missing components
    if not node.polynomial:
        result.warnings.append("No polynomial spec - skipping polynomial.py generation")
    if not node.operad:
        result.warnings.append("No operad spec - skipping operad.py generation")
    if not node.agentese:
        result.warnings.append("No agentese spec - skipping node.py generation")

    if not files_to_write:
        result.warnings.append("No files generated - spec may be incomplete")

    return result


# === Exports ===

__all__ = [
    "compile_spec",
]
