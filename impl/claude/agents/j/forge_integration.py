"""
J+F Integration: Template Instantiation

Cross-Pollination Opportunity T1.3 from docs/CROSS_POLLINATION_ANALYSIS.md:
Combines F-gent's permanent contract-based templates with J-gent's ephemeral
JIT compilation for the best of both worlds.

Pattern: Template[Params] + RuntimeParams → AgentSource

Workflow:
1. F-gent creates parameterized contract (permanent template)
2. J-gent receives template + runtime parameters
3. J-gent instantiates source code with parameters filled in
4. Result: Type-safe, validated agent source ready for execution

Benefits:
- Permanent structure: Template validated once via F-gent contract synthesis
- Ephemeral flexibility: Runtime customization via J-gent instantiation
- Safety: Both F-gent contract validation AND J-gent stability checking
- Reusability: One template, infinite instantiations

Example:
    # F-gent creates template
    contract = await forge_agent.invoke(
        Intent(
            purpose="Process {format} data and output {type}",
            parameters=["format", "type"],
        )
    )
    template = contract_to_template(contract)

    # J-gent instantiates at runtime
    source = await instantiate_template(
        template=template,
        params={"format": "CSV", "type": "JSON"}
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.f import Contract, synthesize_contract
from agents.j.meta_architect import (
    AgentSource,
    ArchitectConstraints,
    MetaArchitect,
)


@dataclass(frozen=True)
class ForgeTemplate:
    """
    Parameterized template created by F-gent.

    A template is a Contract with parameter placeholders that can be
    instantiated with runtime values.

    Fields:
        contract: Base contract from F-gent (with parameter placeholders)
        parameters: List of parameter names (e.g., ["format", "type"])
        default_values: Default parameter values (optional)
        metadata: Additional template metadata
    """

    contract: Contract
    parameters: tuple[str, ...]
    default_values: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateParameters:
    """
    Runtime parameters for template instantiation.

    Fields:
        values: Parameter name → value mapping
        constraints: Optional runtime constraints (overrides template defaults)
    """

    values: dict[str, Any]
    constraints: ArchitectConstraints | None = None


@dataclass(frozen=True)
class InstantiatedAgent:
    """
    Result of template instantiation.

    Fields:
        source: Generated agent source code (from J-gent)
        template: Original template used
        parameters: Parameters used for instantiation
        contract: Instantiated contract (parameters filled in)
    """

    source: AgentSource
    template: ForgeTemplate
    parameters: TemplateParameters
    contract: Contract


# --- Morphism 1: Contract → ForgeTemplate ---


def contract_to_template(
    contract: Contract,
    parameters: list[str] | None = None,
    default_values: dict[str, Any] | None = None,
) -> ForgeTemplate:
    """
    Convert F-gent Contract to parameterized template.

    Analyzes contract intent for parameter placeholders (e.g., {format}, {type})
    and extracts them as template parameters.

    Args:
        contract: Contract from F-gent synthesis
        parameters: Explicit parameter names (if not auto-detected)
        default_values: Default parameter values

    Returns:
        ForgeTemplate ready for J-gent instantiation

    Example:
        >>> contract = Contract(
        ...     agent_name="DataProcessorTemplate",
        ...     semantic_intent="Process {format} data → {output_type}",
        ...     input_type="str",
        ...     output_type="{output_type}",
        ... )
        >>> template = contract_to_template(contract)
        >>> template.parameters
        ('format', 'output_type')
    """
    # Auto-detect parameters from semantic intent
    detected_params: set[str] = set()
    if contract.semantic_intent:
        import re

        # Find {param} placeholders
        matches = re.findall(r"\{(\w+)\}", contract.semantic_intent)
        detected_params.update(matches)

    # Also check output_type for placeholders
    if contract.output_type and "{" in contract.output_type:
        matches = re.findall(r"\{(\w+)\}", contract.output_type)
        detected_params.update(matches)

    # Combine with explicit parameters
    if parameters:
        detected_params.update(parameters)

    return ForgeTemplate(
        contract=contract,
        parameters=tuple(sorted(detected_params)),
        default_values=default_values or {},
        metadata={
            "source": "f-gent",
            "template_version": "1.0.0",
        },
    )


# --- Morphism 2: Template + Parameters → AgentSource ---


async def instantiate_template(
    template: ForgeTemplate,
    params: TemplateParameters,
) -> InstantiatedAgent:
    """
    Instantiate template with runtime parameters via J-gent.

    Workflow:
    1. Fill template parameters in contract
    2. Generate intent from instantiated contract
    3. Use J-gent MetaArchitect to compile agent source
    4. Validate source with J-gent safety checks
    5. Return InstantiatedAgent with source + lineage

    Args:
        template: Parameterized template from F-gent
        params: Runtime parameter values

    Returns:
        InstantiatedAgent with generated source code

    Raises:
        ValueError: If required parameters missing
        RuntimeError: If source validation fails

    Example:
        >>> template = ForgeTemplate(
        ...     contract=Contract(...),
        ...     parameters=("format", "type"),
        ... )
        >>> params = TemplateParameters(
        ...     values={"format": "CSV", "type": "JSON"}
        ... )
        >>> agent = await instantiate_template(template, params)
        >>> print(agent.source.source)  # Generated Python code
    """
    # 1. Validate parameters
    _validate_parameters(template, params)

    # 2. Fill template parameters
    instantiated_contract = _fill_contract_parameters(template, params)

    # 3. Generate intent for J-gent
    intent = _contract_to_intent(instantiated_contract)

    # 4. Use J-gent MetaArchitect to compile
    architect = MetaArchitect()
    from agents.j import ArchitectInput

    arch_input = ArchitectInput(
        intent=intent,
        context={
            "contract": instantiated_contract,
            "template_name": template.contract.agent_name,
            "parameters": params.values,
        },
        constraints=params.constraints or ArchitectConstraints(),
    )

    source = await architect.invoke(arch_input)

    # 5. Validate source safety (with relaxed pattern matching for templates)
    constraints = params.constraints or ArchitectConstraints()
    is_safe, reason = _validate_template_source_safety(source, constraints)
    if not is_safe:
        raise RuntimeError(f"Template instantiation failed safety check: {reason}")

    return InstantiatedAgent(
        source=source,
        template=template,
        parameters=params,
        contract=instantiated_contract,
    )


def _validate_parameters(template: ForgeTemplate, params: TemplateParameters) -> None:
    """
    Validate that all required template parameters are provided.

    Raises:
        ValueError: If required parameters are missing
    """
    provided = set(params.values.keys())
    required = set(template.parameters)
    defaults = set(template.default_values.keys())

    # Required = template params not in defaults
    actually_required = required - defaults

    missing = actually_required - provided
    if missing:
        raise ValueError(
            f"Missing required parameters: {missing}. "
            f"Required: {actually_required}, Provided: {provided}"
        )


def _fill_contract_parameters(
    template: ForgeTemplate, params: TemplateParameters
) -> Contract:
    """
    Fill template parameter placeholders in contract.

    Replaces {param} with actual values from params.

    Returns:
        New Contract with parameters filled in
    """
    # Merge defaults + provided params
    all_params = dict(template.default_values)
    all_params.update(params.values)

    # Fill semantic intent
    semantic_intent = template.contract.semantic_intent
    if semantic_intent:
        for param_name, param_value in all_params.items():
            placeholder = f"{{{param_name}}}"
            semantic_intent = semantic_intent.replace(placeholder, str(param_value))

    # Fill output_type if parameterized
    output_type = template.contract.output_type
    for param_name, param_value in all_params.items():
        placeholder = f"{{{param_name}}}"
        output_type = output_type.replace(placeholder, str(param_value))

    # Fill agent name if parameterized
    agent_name = template.contract.agent_name
    for param_name, param_value in all_params.items():
        placeholder = f"{{{param_name}}}"
        agent_name = agent_name.replace(placeholder, str(param_value))

    return Contract(
        agent_name=agent_name,
        input_type=template.contract.input_type,
        output_type=output_type,
        invariants=template.contract.invariants,
        composition_rules=template.contract.composition_rules,
        semantic_intent=semantic_intent,
        raw_intent=template.contract.raw_intent,
    )


def _contract_to_intent(contract: Contract) -> str:
    """
    Convert instantiated contract to natural language intent for J-gent.

    Uses semantic_intent as primary source, falls back to agent_name.
    """
    if contract.semantic_intent:
        return contract.semantic_intent

    # Fallback: construct from agent name and types
    return (
        f"Create an agent named {contract.agent_name} that takes "
        f"{contract.input_type} as input and produces {contract.output_type}"
    )


def _validate_template_source_safety(
    source: AgentSource, constraints: ArchitectConstraints
) -> tuple[bool, str]:
    """
    Validate template source with smarter pattern matching.

    Unlike validate_source_safety, this uses regex to match actual dangerous
    usage patterns (e.g., input() function call) rather than substrings
    (e.g., "input" in "input_data").

    Args:
        source: Generated agent source
        constraints: Safety constraints

    Returns:
        (is_safe, reason) tuple
    """
    import re

    # Check complexity
    max_complexity = int(
        constraints.entropy_budget * constraints.max_cyclomatic_complexity
    )
    if source.complexity > max_complexity:
        return (
            False,
            f"Complexity {source.complexity} exceeds budget {max_complexity}",
        )

    # Check imports
    forbidden_imports = source.imports - constraints.allowed_imports
    if forbidden_imports:
        return (False, f"Forbidden imports: {forbidden_imports}")

    # Check patterns with regex (match actual function calls, not substrings)
    dangerous_patterns = {
        "eval": r"\beval\s*\(",
        "exec": r"\bexec\s*\(",
        "compile": r"\bcompile\s*\(",
        "__import__": r"\b__import__\s*\(",
        "open": r"\bopen\s*\(",  # File I/O
        "input": r"\binput\s*\(",  # User input function call
        "globals": r"\bglobals\s*\(",
        "locals": r"\blocals\s*\(",
        "os.system": r"os\.system\s*\(",
        "subprocess": r"subprocess\.",
    }

    for pattern_name, pattern_regex in dangerous_patterns.items():
        if re.search(pattern_regex, source.source):
            return (False, f"Forbidden pattern detected: {pattern_name}()")

    return (True, "Source passes safety checks")


# --- Workflow: F-gent → Template → J-gent Instantiation ---


async def forge_and_instantiate(
    intent_template: str,
    template_name: str,
    runtime_params: dict[str, Any],
    constraints: ArchitectConstraints | None = None,
) -> InstantiatedAgent:
    """
    Complete workflow: F-gent forges template → J-gent instantiates.

    This is the full T1.3 integration demonstrating permanent + ephemeral.

    Workflow:
    1. F-gent synthesizes contract from parameterized intent
    2. Convert contract to template
    3. J-gent instantiates template with runtime params
    4. Return ready-to-execute agent source

    Args:
        intent_template: Parameterized intent (e.g., "Process {format} data")
        template_name: Name for the template
        runtime_params: Parameter values for instantiation
        constraints: Optional J-gent safety constraints

    Returns:
        InstantiatedAgent with source code

    Example:
        >>> agent = await forge_and_instantiate(
        ...     intent_template="Process {format} data and output {type}",
        ...     template_name="DataProcessorTemplate",
        ...     runtime_params={"format": "CSV", "type": "JSON"},
        ... )
        >>> print(agent.source.class_name)  # Generated class name
    """
    # 1. F-gent: Create intent and synthesize contract
    # (Simplified: In production, this would use full F-gent pipeline)
    from agents.f import parse_intent

    intent_obj = parse_intent(intent_template)
    contract = synthesize_contract(intent_obj, template_name)

    # 2. Convert to template
    template = contract_to_template(contract)

    # 3. J-gent: Instantiate with runtime params
    params = TemplateParameters(values=runtime_params, constraints=constraints)
    agent = await instantiate_template(template, params)

    return agent


# --- Template Registry (Future Enhancement) ---


class TemplateRegistry:
    """
    Registry for reusable F-gent templates.

    Future enhancement: Store templates in L-gent catalog for ecosystem-wide reuse.

    Workflow:
    1. F-gent forges template → Register in L-gent
    2. J-gent queries L-gent for template by intent
    3. J-gent instantiates template with runtime params

    This enables:
    - Template discoverability (search before creating)
    - Template versioning (track improvements)
    - Template composition (combine templates)
    """

    def __init__(self):
        """Initialize empty registry."""
        self._templates: dict[str, ForgeTemplate] = {}

    def register(self, name: str, template: ForgeTemplate) -> None:
        """Register template by name."""
        self._templates[name] = template

    def get(self, name: str) -> ForgeTemplate | None:
        """Retrieve template by name."""
        return self._templates.get(name)

    def list_all(self) -> list[str]:
        """List all registered template names."""
        return list(self._templates.keys())

    def search(self, query: str) -> list[ForgeTemplate]:
        """
        Search templates by intent keywords.

        Future: Integrate with L-gent semantic search.
        """
        results = []
        query_lower = query.lower()

        for template in self._templates.values():
            if template.contract.semantic_intent:
                if query_lower in template.contract.semantic_intent.lower():
                    results.append(template)

        return results
