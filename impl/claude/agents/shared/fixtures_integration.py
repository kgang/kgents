"""
Shared test fixtures for kgents tests.

Provides common fixtures for Intent, Contract, SourceCode, and other
frequently-used test data structures. Import and use these in your tests
to reduce duplication.

Usage:
    from agents.shared.fixtures_integration import (
        make_sample_intent,
        make_sample_contract,
        make_sample_source_code,
        make_sample_catalog_entry,
    )
"""

from __future__ import annotations

from agents.f.contract import (
    CompositionRule,
    Contract,
    Invariant,
)
from agents.f.intent import (
    Dependency,
    DependencyType,
    Example,
    Intent,
)
from agents.f.prototype import SourceCode
from agents.l.catalog import CatalogEntry


def make_sample_intent(
    purpose: str = "Fetch weather data for a given location",
    agent_name: str = "WeatherFetcher",
) -> Intent:
    """
    Create a sample Intent for testing.

    Args:
        purpose: Override the default purpose
        agent_name: Used in examples (not stored in Intent directly)

    Returns:
        Intent with realistic test data
    """
    return Intent(
        purpose=purpose,
        behavior=["Query weather API", "Return structured JSON"],
        constraints=["Timeout < 5s", "Idempotent", "Handle network errors"],
        tone="Professional, concise",
        dependencies=[
            Dependency(
                name="WeatherAPI",
                type=DependencyType.REST_API,
                description="External weather service",
                required=True,
            )
        ],
        examples=[
            Example(
                input="Seattle, WA",
                expected_output={"temp": 55, "condition": "cloudy"},
                description="Standard query",
            ),
            Example(
                input="New York, NY",
                expected_output={"temp": 72, "condition": "sunny"},
                description="Different location",
            ),
        ],
        raw_text=f"Create an agent that {purpose.lower()}",
    )


def make_sample_contract(
    agent_name: str = "WeatherFetcher",
    input_type: str = "str",
    output_type: str = "WeatherData",
) -> Contract:
    """
    Create a sample Contract for testing.

    Args:
        agent_name: Name of the agent
        input_type: Input type string
        output_type: Output type string

    Returns:
        Contract with realistic invariants and composition rules
    """
    return Contract(
        agent_name=agent_name,
        input_type=input_type,
        output_type=output_type,
        invariants=[
            Invariant(
                description="Response time < 5s",
                property="execution_time < 5.0",
                category="performance",
            ),
            Invariant(
                description="Idempotent",
                property="f(x) == f(x)",
                category="correctness",
            ),
        ],
        composition_rules=[
            CompositionRule(
                mode="sequential",
                description="Can compose with data processors",
                type_constraint=f"{output_type} -> Report",
            )
        ],
        semantic_intent="Fetch current weather data",
        raw_intent=make_sample_intent(),
    )


def make_sample_source_code(
    agent_name: str = "WeatherFetcher",
    valid: bool = True,
) -> SourceCode:
    """
    Create a sample SourceCode for testing.

    Args:
        agent_name: Name of the agent class
        valid: Whether the code should be valid

    Returns:
        SourceCode with a simple agent implementation
    """
    from agents.f.prototype import StaticAnalysisReport

    code = f'''
class {agent_name}:
    """Fetch weather data from API."""

    def invoke(self, location: str) -> dict:
        """Fetch weather for location."""
        return {{"temp": 55, "condition": "cloudy"}}
'''
    return SourceCode(
        code=code,
        analysis_report=StaticAnalysisReport(results=[], passed=valid),
        generation_attempt=1,
    )


def make_simple_agent_code(agent_name: str, input_val: str, output_val: str) -> str:
    """
    Create minimal agent code for testing.

    Args:
        agent_name: Name of the agent class
        input_val: Expected input value
        output_val: Value to return

    Returns:
        Python source code string
    """
    return f"""
class {agent_name}:
    def invoke(self, x):
        return {output_val!r}
"""


# Catalog entry factory (for L-gent tests)
def make_sample_catalog_entry(
    name: str = "TestAgent",
    description: str = "A test agent for unit tests",
    author: str = "test",
) -> CatalogEntry:
    """
    Create a sample CatalogEntry for testing.

    Note: Imports CatalogEntry lazily to avoid circular imports.
    """
    from agents.l.catalog import CatalogEntry, EntityType, Status

    return CatalogEntry(
        id="test-agent-1",
        version="1.0.0",
        name=name,
        entity_type=EntityType.AGENT,
        description=description,
        author=author,
        keywords=["test", "sample"],
        input_type="str",
        output_type="str",
        status=Status.ACTIVE,
    )
