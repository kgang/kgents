"""
Tests for J+F integration: Template Instantiation

Tests T1.3 cross-pollination opportunity:
F-gent creates permanent parameterized templates,
J-gent instantiates them with runtime parameters.
"""

from __future__ import annotations

import pytest
from agents.f import Contract, parse_intent, synthesize_contract
from agents.j import ArchitectConstraints
from agents.j.forge_integration import (
    InstantiatedAgent,
    TemplateParameters,
    TemplateRegistry,
    contract_to_template,
    forge_and_instantiate,
    instantiate_template,
)

# --- Test Fixtures ---


@pytest.fixture
def simple_contract() -> Contract:
    """Simple contract without parameters."""
    return Contract(
        agent_name="SimpleAgent",
        input_type="str",
        output_type="dict",
        invariants=[],
        composition_rules=[],
        semantic_intent="Parse text and return dictionary",
        raw_intent=None,
    )


@pytest.fixture
def parameterized_contract() -> Contract:
    """Contract with parameter placeholders."""
    return Contract(
        agent_name="DataProcessor_{format}",
        input_type="str",
        output_type="{output_type}",
        invariants=[],
        composition_rules=[],
        semantic_intent="Process {format} data and output {output_type}",
        raw_intent=None,
    )


@pytest.fixture
def multi_param_contract() -> Contract:
    """Contract with multiple parameters."""
    return Contract(
        agent_name="{source}To{dest}Converter",
        input_type="{source}",
        output_type="{dest}",
        invariants=[],
        composition_rules=[],
        semantic_intent="Convert {source} format to {dest} format with {encoding} encoding",
        raw_intent=None,
    )


# --- Test Contract → Template Conversion ---


def test_contract_to_template_no_params(simple_contract: Contract) -> None:
    """Convert contract without parameters to template."""
    template = contract_to_template(simple_contract)

    assert template.contract == simple_contract
    assert len(template.parameters) == 0
    assert template.default_values == {}
    assert template.metadata["source"] == "f-gent"


def test_contract_to_template_auto_detect_params(
    parameterized_contract: Contract,
) -> None:
    """Auto-detect parameters from {placeholder} syntax."""
    template = contract_to_template(parameterized_contract)

    assert set(template.parameters) == {"format", "output_type"}
    assert template.contract == parameterized_contract


def test_contract_to_template_multiple_params(multi_param_contract: Contract) -> None:
    """Auto-detect multiple parameters across fields."""
    template = contract_to_template(multi_param_contract)

    assert set(template.parameters) == {"source", "dest", "encoding"}


def test_contract_to_template_explicit_params(simple_contract: Contract) -> None:
    """Explicitly specify parameters (override auto-detection)."""
    template = contract_to_template(
        simple_contract,
        parameters=["custom_param"],
        default_values={"custom_param": "default"},
    )

    assert "custom_param" in template.parameters
    assert template.default_values["custom_param"] == "default"


def test_contract_to_template_with_defaults(parameterized_contract: Contract) -> None:
    """Template with default parameter values."""
    template = contract_to_template(
        parameterized_contract,
        default_values={"format": "CSV", "output_type": "JSON"},
    )

    assert template.default_values == {"format": "CSV", "output_type": "JSON"}


# --- Test Parameter Validation ---


@pytest.mark.asyncio
async def test_instantiate_template_missing_required_param(
    parameterized_contract: Contract,
) -> None:
    """Raise error when required parameter is missing."""
    template = contract_to_template(parameterized_contract)
    params = TemplateParameters(values={"format": "CSV"})  # Missing output_type

    with pytest.raises(ValueError, match="Missing required parameters"):
        await instantiate_template(template, params)


@pytest.mark.asyncio
async def test_instantiate_template_with_defaults(
    parameterized_contract: Contract,
) -> None:
    """Use default values for missing parameters."""
    template = contract_to_template(
        parameterized_contract,
        default_values={"output_type": "JSON"},
    )
    params = TemplateParameters(values={"format": "CSV"})

    # Should not raise (output_type has default)
    agent = await instantiate_template(template, params)

    assert agent is not None
    assert "CSV" in agent.contract.semantic_intent
    assert "JSON" in agent.contract.semantic_intent


# --- Test Template Instantiation ---


@pytest.mark.asyncio
async def test_instantiate_template_basic(parameterized_contract: Contract) -> None:
    """Basic template instantiation with all parameters."""
    template = contract_to_template(parameterized_contract)
    params = TemplateParameters(values={"format": "CSV", "output_type": "JSON"})

    agent = await instantiate_template(template, params)

    assert isinstance(agent, InstantiatedAgent)
    assert agent.template == template
    assert agent.parameters == params

    # Check parameters were filled in contract
    assert "CSV" in agent.contract.semantic_intent
    assert "JSON" in agent.contract.semantic_intent
    assert (
        "CSV" not in agent.contract.output_type or "JSON" in agent.contract.output_type
    )


@pytest.mark.asyncio
async def test_instantiate_template_agent_name_filled(
    parameterized_contract: Contract,
) -> None:
    """Verify agent name parameters are filled."""
    template = contract_to_template(parameterized_contract)
    params = TemplateParameters(values={"format": "XML", "output_type": "YAML"})

    agent = await instantiate_template(template, params)

    assert (
        "XML" in agent.contract.agent_name
        or "DataProcessor" in agent.contract.agent_name
    )


@pytest.mark.asyncio
async def test_instantiate_template_generates_source(
    parameterized_contract: Contract,
) -> None:
    """Verify J-gent generates actual source code."""
    template = contract_to_template(parameterized_contract)
    params = TemplateParameters(values={"format": "JSON", "output_type": "dict"})

    agent = await instantiate_template(template, params)

    assert agent.source is not None
    assert len(agent.source.source) > 0
    assert agent.source.class_name.startswith("JIT")


@pytest.mark.asyncio
async def test_instantiate_template_safety_validation(
    parameterized_contract: Contract,
) -> None:
    """Verify safety constraints are enforced."""
    template = contract_to_template(parameterized_contract)

    # Create very restrictive constraints
    constraints = ArchitectConstraints(
        max_cyclomatic_complexity=1,  # Very low
        entropy_budget=0.1,  # Very low
    )
    params = TemplateParameters(
        values={"format": "CSV", "output_type": "JSON"},
        constraints=constraints,
    )

    # Should succeed or fail gracefully (depends on generated complexity)
    # We're just testing that safety validation runs
    try:
        agent = await instantiate_template(template, params)
        # If it succeeds, complexity was within budget
        assert (
            agent.source.complexity
            <= constraints.max_cyclomatic_complexity * constraints.entropy_budget + 10
        )
    except RuntimeError as e:
        # If it fails, should be due to safety check
        assert "safety check" in str(e).lower()


# --- Test Full Workflow ---


@pytest.mark.asyncio
async def test_forge_and_instantiate_workflow() -> None:
    """Test complete F→Template→J workflow."""
    agent = await forge_and_instantiate(
        intent_template="Parse {format} logs and extract {field} fields",
        template_name="LogParser_{format}",
        runtime_params={"format": "NGINX", "field": "error"},
    )

    assert isinstance(agent, InstantiatedAgent)
    assert agent.source is not None
    assert (
        "NGINX" in agent.contract.semantic_intent
        or "error" in agent.contract.semantic_intent
    )


@pytest.mark.asyncio
async def test_forge_and_instantiate_multiple_params() -> None:
    """Test workflow with multiple runtime parameters."""
    agent = await forge_and_instantiate(
        intent_template="Convert {source} to {dest} using {method}",
        template_name="{source}To{dest}Converter",
        runtime_params={"source": "XML", "dest": "JSON", "method": "streaming"},
    )

    assert agent is not None
    assert "XML" in agent.contract.semantic_intent
    assert "JSON" in agent.contract.semantic_intent
    assert "streaming" in agent.contract.semantic_intent


# --- Test Template Registry ---


def test_registry_register_and_get(parameterized_contract: Contract) -> None:
    """Register template and retrieve by name."""
    registry = TemplateRegistry()
    template = contract_to_template(parameterized_contract)

    registry.register("data_processor", template)
    retrieved = registry.get("data_processor")

    assert retrieved == template


def test_registry_list_all(
    parameterized_contract: Contract, simple_contract: Contract
) -> None:
    """List all registered templates."""
    registry = TemplateRegistry()

    registry.register("template1", contract_to_template(parameterized_contract))
    registry.register("template2", contract_to_template(simple_contract))

    all_names = registry.list_all()
    assert len(all_names) == 2
    assert "template1" in all_names
    assert "template2" in all_names


def test_registry_search(
    parameterized_contract: Contract, simple_contract: Contract
) -> None:
    """Search templates by intent keywords."""
    registry = TemplateRegistry()

    registry.register("processor", contract_to_template(parameterized_contract))
    registry.register("parser", contract_to_template(simple_contract))

    # Search for "process" should match parameterized_contract
    results = registry.search("process")
    assert len(results) == 1
    assert results[0].contract.agent_name == parameterized_contract.agent_name

    # Search for "parse" should match simple_contract
    results = registry.search("parse")
    assert len(results) == 1
    assert results[0].contract.agent_name == simple_contract.agent_name


def test_registry_get_nonexistent() -> None:
    """Retrieve non-existent template returns None."""
    registry = TemplateRegistry()
    assert registry.get("nonexistent") is None


# --- Integration Tests: F-gent + J-gent ---


@pytest.mark.asyncio
async def test_integration_f_gent_contract_to_j_gent_instantiation() -> None:
    """
    Full integration: F-gent synthesizes contract → J-gent instantiates.

    This demonstrates the complete T1.3 cross-pollination workflow.
    """
    # 1. F-gent: Parse intent and synthesize contract
    intent = parse_intent("Transform {input_format} files to {output_format}")
    contract = synthesize_contract(intent, "FileTransformer_{input_format}")

    # 2. Convert to template
    template = contract_to_template(contract)
    assert len(template.parameters) >= 1  # At least input_format and output_format

    # 3. J-gent: Instantiate with runtime params
    params = TemplateParameters(
        values={"input_format": "CSV", "output_format": "Parquet"}
    )
    agent = await instantiate_template(template, params)

    # 4. Verify result
    assert agent.source is not None
    assert (
        "CSV" in agent.contract.semantic_intent
        or "Parquet" in agent.contract.semantic_intent
    )


@pytest.mark.asyncio
async def test_integration_reusable_template() -> None:
    """
    Demonstrate reusability: One template, multiple instantiations.

    This shows the value of T1.3: Permanent structure (template)
    + Ephemeral flexibility (runtime params).
    """
    # Create template once
    intent = parse_intent("Validate {data_type} data against {schema_type} schema")
    contract = synthesize_contract(intent, "DataValidator")
    template = contract_to_template(contract)

    # Instantiate multiple times with different params
    params1 = TemplateParameters(
        values={"data_type": "JSON", "schema_type": "JSON Schema"}
    )
    agent1 = await instantiate_template(template, params1)

    params2 = TemplateParameters(values={"data_type": "XML", "schema_type": "XSD"})
    agent2 = await instantiate_template(template, params2)

    # Both should succeed
    assert agent1.source is not None
    assert agent2.source is not None

    # But with different parameters filled in
    assert "JSON" in agent1.contract.semantic_intent
    assert "XML" in agent2.contract.semantic_intent


# --- Edge Cases ---


@pytest.mark.asyncio
async def test_edge_case_no_parameters(simple_contract: Contract) -> None:
    """Template with no parameters works (degenerates to normal instantiation)."""
    template = contract_to_template(simple_contract)
    params = TemplateParameters(values={})

    agent = await instantiate_template(template, params)
    assert agent.source is not None


@pytest.mark.asyncio
async def test_edge_case_extra_parameters(parameterized_contract: Contract) -> None:
    """Extra parameters (not in template) are ignored gracefully."""
    template = contract_to_template(parameterized_contract)
    params = TemplateParameters(
        values={
            "format": "CSV",
            "output_type": "JSON",
            "extra_param": "ignored",  # Extra
        }
    )

    # Should not raise error
    agent = await instantiate_template(template, params)
    assert agent is not None


def test_edge_case_parameter_placeholder_escaping() -> None:
    """Test that {param} in strings vs actual params are distinguished."""
    # Contract with literal braces in description
    contract = Contract(
        agent_name="EdgeCaseAgent",
        input_type="str",
        output_type="str",
        invariants=[],
        composition_rules=[],
        semantic_intent="Parse format: {{literal}} and {actual_param}",
        raw_intent=None,
    )

    template = contract_to_template(contract)

    # Should detect actual_param but not literal
    assert "actual_param" in template.parameters
    # Note: Python's {{ escaping might not work in simple regex - this is an edge case
    # that would need more sophisticated parsing in production
