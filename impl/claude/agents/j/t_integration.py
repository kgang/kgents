"""
J-gent + T-gent Integration: Template-Based Tool Generation.

Cross-pollination: Phase 7 (T-gents Cross-Genus Integration)
    Problem: Tools are often one-off implementations, no reusable templates
    Solution: J-gent JIT compilation generates Tool[A,B] agents from templates
    Impact: Rapid tool creation with full categorical composition

This module provides JIT compilation of tools from natural language intent
or predefined templates. Generated tools are fully composable via >> and
execute in sandboxed environments for security.

Key Types:
- ToolTemplate: Template for generating Tool[A,B] agents
- JITToolMeta: Extended metadata for JIT-compiled tools
- JITToolWrapper: Makes JIT code behave as Tool[A,B]

Primary Functions:
- compile_tool_from_intent: Natural language → Tool[A,B]
- compile_tool_from_template: Template + params → Tool[A,B]
- create_tool_from_source: AgentSource → Tool[A,B]

Architecture:
```
Natural Language Intent
    ↓
J-gent MetaArchitect (compile)
    ↓
AgentSource (validated Python)
    ↓
JITToolWrapper[A,B] (sandboxed execution)
    ↓
Tool[A,B] (composable via >>)
```

Example:
    >>> from agents.j.t_integration import compile_tool_from_intent
    >>> from agents.u import ToolCapabilities
    >>>
    >>> # Generate tool from natural language
    >>> tool = await compile_tool_from_intent(
    ...     "Parse JSON and extract the 'error' field",
    ...     input_type=str,
    ...     output_type=str,
    ...     capabilities=ToolCapabilities(requires_network=False),
    ... )
    >>>
    >>> # Use tool
    >>> result = await tool.invoke('{"error": "Connection failed"}')
    >>> assert result.unwrap() == "Connection failed"
    >>>
    >>> # Compose with other tools
    >>> pipeline = parse_tool >> validate_tool >> log_tool
    >>> await pipeline.invoke(raw_data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from agents.u.core import Tool, ToolError, ToolErrorType, ToolMeta
from agents.u.permissions import ToolCapabilities
from bootstrap.types import Result, err, ok

from .chaosmonger import StabilityConfig, analyze_stability
from .factory_integration import JITAgentMeta
from .meta_architect import (
    AgentSource,
    ArchitectConstraints,
    ArchitectInput,
    MetaArchitect,
)
from .sandbox import SandboxConfig, execute_in_sandbox

# Type variables for tool generics
A = TypeVar("A")
B = TypeVar("B")


@dataclass(frozen=True)
class ToolTemplate:
    """
    Template for generating Tool[A,B] agents.

    A tool template captures the common structure of a tool type
    and allows parameterization for specific use cases.

    Example:
        >>> json_parser_template = ToolTemplate(
        ...     name="JSON Parser",
        ...     description="Parse JSON and extract field",
        ...     template_source='''
        ...         import json
        ...         def invoke(input_data: str) -> str:
        ...             parsed = json.loads(input_data)
        ...             return parsed.get("{field_name}", "")
        ...     ''',
        ...     parameters={"field_name": "error"},
        ... )
    """

    name: str
    description: str
    template_source: str
    parameters: dict[str, Any] = field(default_factory=dict)
    capabilities: ToolCapabilities = field(default_factory=ToolCapabilities)


@dataclass(frozen=True)
class JITToolMeta:
    """
    Extended metadata for JIT-compiled tools.

    Carries full provenance:
    - jit_meta: JIT agent metadata (source, constraints, stability)
    - tool_meta: Tool metadata (name, description, capabilities)
    - template: Optional template used for generation
    """

    jit_meta: JITAgentMeta
    tool_meta: ToolMeta
    template: ToolTemplate | None = None


class JITToolWrapper(Tool[A, B], Generic[A, B]):
    """
    Wrapper that makes JIT-compiled code behave as Tool[A, B].

    Combines:
    - Agent[A, B] composition via >> (from Tool)
    - Sandboxed execution (from J-gent)
    - Tool capabilities and permissions (from T-gent)

    Security: Every invoke() re-executes in sandbox to prevent cached
    code from bypassing safety checks.

    Example:
        >>> source = await compile_tool_from_intent("Parse JSON", str, dict)
        >>> tool = JITToolWrapper(source, meta, jit_meta)
        >>>
        >>> # Use as normal tool
        >>> result = await tool.invoke('{"key": "value"}')
        >>>
        >>> # Compose with other tools
        >>> pipeline = tool >> format_tool >> store_tool
    """

    def __init__(
        self,
        source: AgentSource,
        meta: ToolMeta,
        jit_tool_meta: JITToolMeta,
    ):
        self._source = source
        self._meta = meta
        self._jit_tool_meta = jit_tool_meta

    @property
    def name(self) -> str:
        return str(self._meta.identity.name)

    @property
    def meta(self) -> ToolMeta:  # type: ignore[override]
        return self._meta

    @property
    def jit_tool_meta(self) -> JITToolMeta:
        return self._jit_tool_meta

    async def invoke(self, input_val: A) -> Result[B, ToolError]:  # type: ignore[override]
        """
        Execute JIT tool in sandbox.

        Intentionally returns Result[B, ToolError] instead of B to provide
        explicit error handling for sandboxed execution failures. This allows
        callers to distinguish between sandbox errors and successful tool execution.

        Steps:
        1. Execute source in sandbox with input
        2. Wrap result in Result[B, ToolError]
        3. Return success or tool error
        """
        try:
            # Execute in sandbox
            # The sandbox executes the "invoke" function defined in the template source
            sandbox_result = await execute_in_sandbox(
                source=self._source,
                method_name="invoke",
                args=(input_val,),
                config=self._jit_tool_meta.jit_meta.sandbox_config,
            )

            # Check for sandbox errors
            if not sandbox_result.success:
                return err(
                    ToolError(
                        error_type=ToolErrorType.FATAL,
                        message=f"Sandbox execution failed: {sandbox_result.error}",
                        tool_name=self._source.class_name,
                        input=input_val,
                        recoverable=False,
                    )
                )

            # Return successful result
            return ok(sandbox_result.output)

        except Exception as e:
            return err(
                ToolError(
                    error_type=ToolErrorType.FATAL,
                    message=f"JIT tool execution failed: {str(e)}",
                    tool_name=self._source.class_name,
                    input=input_val,
                    recoverable=False,
                )
            )


async def create_tool_from_source(
    source: AgentSource,
    constraints: ArchitectConstraints,
    tool_meta: ToolMeta,
    sandbox_config: SandboxConfig | None = None,
) -> JITToolWrapper[Any, Any]:
    """
    Create a Tool[A, B] from validated AgentSource.

    Args:
        source: Validated agent source code
        constraints: Safety constraints used during generation
        tool_meta: Tool metadata (name, description, capabilities)
        sandbox_config: Optional sandbox configuration

    Returns:
        JITToolWrapper that behaves as Tool[A, B]

    Example:
        >>> source = AgentSource(
        ...     class_name="JsonParser",
        ...     source="class JsonParser:\\n    def invoke(self, x: str) -> dict: ...",
        ...     imports=frozenset(["json"]),
        ...     complexity=2,
        ...     description="Parse JSON strings",
        ... )
        >>> tool = await create_tool_from_source(
        ...     source,
        ...     ArchitectConstraints(),
        ...     ToolMeta.minimal("json_parser", "Parse JSON"),
        ... )
    """
    # Analyze stability
    stability_result = analyze_stability(
        source.source,
        entropy_budget=1.0,
        config=StabilityConfig(),
    )

    # Compute stability score from result (1.0 = stable, lower = unstable)
    if stability_result.is_stable:
        stability_score = 1.0
    else:
        # Reduce score based on violation count
        stability_score = max(0.0, 1.0 - (len(stability_result.violations) * 0.2))

    # Create JIT metadata
    jit_meta = JITAgentMeta(
        source=source,
        constraints=constraints,
        stability_score=stability_score,
        sandbox_config=sandbox_config or SandboxConfig(),
    )

    # Create JIT tool metadata
    jit_tool_meta = JITToolMeta(
        jit_meta=jit_meta,
        tool_meta=tool_meta,
    )

    # Create wrapper
    return JITToolWrapper(source, tool_meta, jit_tool_meta)


async def compile_tool_from_intent(
    intent: str,
    input_type: type[A],
    output_type: type[B],
    capabilities: ToolCapabilities | None = None,
    constraints: ArchitectConstraints | None = None,
) -> JITToolWrapper[A, B]:
    """
    Generate a Tool[A, B] from natural language intent.

    Full pipeline: Intent → MetaArchitect → AgentSource → Tool[A, B]

    Args:
        intent: Natural language description of tool behavior
        input_type: Type of input the tool accepts
        output_type: Type of output the tool produces
        capabilities: Tool capabilities (network, filesystem, etc.)
        constraints: Safety constraints for generation

    Returns:
        JIT-compiled Tool[A, B] ready to use

    Example:
        >>> tool = await compile_tool_from_intent(
        ...     "Extract error messages from JSON logs",
        ...     input_type=str,
        ...     output_type=str,
        ...     capabilities=ToolCapabilities(requires_network=False),
        ... )
        >>>
        >>> result = await tool.invoke('{"level": "error", "msg": "Failed"}')
        >>> assert result.unwrap() == "Failed"
    """
    # Default constraints
    constraints = constraints or ArchitectConstraints()

    # Default capabilities
    capabilities = capabilities or ToolCapabilities()

    # Compile agent source
    architect = MetaArchitect()
    architect_input = ArchitectInput(
        intent=intent,
        constraints=constraints,
    )
    source = await architect.invoke(architect_input)

    # Create tool metadata with Any types for JIT tools

    tool_meta = ToolMeta.minimal(
        name=f"jit_{source.class_name.lower()}",
        description=intent,
        input_schema=input_type,
        output_schema=output_type,
    )

    # Create tool from source
    return await create_tool_from_source(
        source,
        constraints,
        tool_meta,
    )


async def compile_tool_from_template(
    template: ToolTemplate,
    parameters: dict[str, Any] | None = None,
    constraints: ArchitectConstraints | None = None,
) -> JITToolWrapper[Any, Any]:
    """
    Generate a Tool[A, B] from a template with parameters.

    Templates allow reusable tool patterns with parameterization.

    Args:
        template: Tool template with parameterized source
        parameters: Parameters to substitute into template
        constraints: Safety constraints for validation

    Returns:
        JIT-compiled Tool[A, B] ready to use

    Example:
        >>> template = ToolTemplate(
        ...     name="Field Extractor",
        ...     description="Extract field from JSON",
        ...     template_source='''
        ...         import json
        ...         def invoke(data: str) -> str:
        ...             parsed = json.loads(data)
        ...             return parsed.get("{field}", "")
        ...     ''',
        ...     capabilities=ToolCapabilities(requires_network=False),
        ... )
        >>>
        >>> tool = await compile_tool_from_template(
        ...     template,
        ...     parameters={"field": "error"},
        ... )
    """
    # Merge parameters
    params = {**template.parameters, **(parameters or {})}

    # Substitute parameters into template
    source_code = template.template_source.format(**params)

    # Extract class name from template name
    class_name = template.name.replace(" ", "")

    # Create agent source with correct field names
    source = AgentSource(
        source=source_code,
        class_name=class_name,
        imports=frozenset({"json"}) if "json" in source_code else frozenset(),
        complexity=2,  # Templates are simple
        description=template.description,
    )

    # Create tool metadata with Any types for template tools
    from typing import Any as AnyType

    tool_meta = ToolMeta.minimal(
        name=template.name.lower().replace(" ", "_"),
        description=template.description,
        input_schema=AnyType,
        output_schema=AnyType,
    )

    # Default constraints
    constraints = constraints or ArchitectConstraints()

    # Create JIT tool metadata with template
    jit_meta = JITAgentMeta(
        source=source,
        constraints=constraints,
        stability_score=1.0,  # Templates assumed stable
        sandbox_config=SandboxConfig(),
    )

    jit_tool_meta = JITToolMeta(
        jit_meta=jit_meta,
        tool_meta=tool_meta,
        template=template,
    )

    # Create wrapper
    return JITToolWrapper(source, tool_meta, jit_tool_meta)


# --- Common Tool Templates ---

# Template: JSON field extractor
JSON_FIELD_EXTRACTOR = ToolTemplate(
    name="JSON Field Extractor",
    description="Extract a specific field from JSON data",
    template_source="""
class JSONFieldExtractor:
    '''Extract a specific field from JSON data.'''

    def invoke(self, data: str) -> str:
        '''Extract {field} from JSON string.'''
        try:
            parsed = json.loads(data)
            return str(parsed.get("{field}", ""))
        except Exception:
            return ""
""",
    parameters={"field": "error"},
    capabilities=ToolCapabilities(requires_network=False),
)

# Template: Text transformer
TEXT_TRANSFORMER = ToolTemplate(
    name="Text Transformer",
    description="Transform text using a function",
    template_source="""
class TextTransformer:
    '''Transform text using a string method.'''

    def invoke(self, text: str) -> str:
        '''Transform text: {transform_description}'''
        return text.{transform_method}()
""",
    parameters={
        "transform_method": "upper",
        "transform_description": "Convert to uppercase",
    },
    capabilities=ToolCapabilities(requires_network=False),
)

# Template: Filter
FILTER_TEMPLATE = ToolTemplate(
    name="Filter",
    description="Filter items based on condition",
    template_source="""
class Filter:
    '''Filter items based on condition.'''

    def invoke(self, items: list) -> list:
        '''Filter items where {condition}'''
        return [item for item in items if {condition_code}]
""",
    parameters={
        "condition": "item > 0",
        "condition_code": "item > 0",
    },
    capabilities=ToolCapabilities(requires_network=False),
)
