"""
Intent parsing for F-gents (Phase 1: Understand).

This module implements the NaturalLanguage → Intent morphism from spec/f-gents/forge.md.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DependencyType(Enum):
    """Types of external dependencies an agent might have."""

    REST_API = "rest_api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    EXTERNAL_AGENT = "external_agent"
    LIBRARY = "library"
    OTHER = "other"


@dataclass
class Dependency:
    """An external system or resource the agent interacts with."""

    name: str  # Human-readable name (e.g., "WeatherAPI", "PostgreSQL")
    type: DependencyType  # Category of dependency
    description: str = ""  # Optional details about how it's used
    required: bool = True  # Whether dependency is mandatory


@dataclass
class Example:
    """A test case demonstrating expected behavior."""

    input: Any  # Example input to the agent
    expected_output: Any  # Expected output
    description: str = ""  # Optional explanation of what this tests


@dataclass
class Intent:
    """
    Structured representation of user intent for artifact creation.

    This is the output of Phase 1 (Understand) and input to Phase 2 (Contract).

    Fields align with spec/f-gents/forge.md Phase 1 outputs.
    """

    purpose: str  # One-sentence description of what the agent does
    behavior: list[str] = field(default_factory=list)  # Specific capabilities
    constraints: list[str] = field(default_factory=list)  # Requirements, limits
    tone: str | None = None  # Optional personality/style
    dependencies: list[Dependency] = field(default_factory=list)  # External systems
    examples: list[Example] = field(default_factory=list)  # User-provided test cases

    # Metadata
    raw_text: str = ""  # Original natural language input (for reference)
    ambiguities: list[str] = field(
        default_factory=list
    )  # Detected ambiguities (for H-gent resolution)


def parse_intent(natural_language: str) -> Intent:
    """
    Parse natural language description into structured Intent.

    This is the core morphism of Phase 1 (Understand):
        NaturalLanguage → Intent

    Current implementation uses simple heuristics. Future versions will use:
    - LLM for semantic understanding
    - H-gent for ambiguity resolution
    - L-gent for similarity search

    Args:
        natural_language: User's description of desired agent

    Returns:
        Structured Intent object

    Examples:
        >>> intent = parse_intent("Create an agent that summarizes papers to JSON")
        >>> intent.purpose
        'Summarize papers to JSON'
        >>> intent.dependencies[0].type
        <DependencyType.FILE_SYSTEM: 'file_system'>
    """
    # Extract purpose (first sentence or entire text if short)
    purpose = _extract_purpose(natural_language)

    # Extract behavior keywords
    behavior = _extract_behavior(natural_language)

    # Extract constraints
    constraints = _extract_constraints(natural_language)

    # Detect tone/personality
    tone = _extract_tone(natural_language)

    # Analyze dependencies
    dependencies = _analyze_dependencies(natural_language)

    # Detect ambiguities
    ambiguities = _detect_ambiguities(natural_language)

    return Intent(
        purpose=purpose,
        behavior=behavior,
        constraints=constraints,
        tone=tone,
        dependencies=dependencies,
        examples=[],  # Examples usually provided separately
        raw_text=natural_language,
        ambiguities=ambiguities,
    )


def _extract_purpose(text: str) -> str:
    """Extract the primary purpose (one-sentence summary)."""
    # Simple heuristic: first sentence or first 100 chars
    sentences = text.split(".")
    first_sentence = sentences[0].strip()

    # Remove common prefixes
    prefixes = [
        "Create an agent that ",
        "I need an agent that ",
        "Build an agent that ",
        "Make an agent that ",
        "I want an agent that ",
    ]
    for prefix in prefixes:
        if first_sentence.lower().startswith(prefix.lower()):
            first_sentence = first_sentence[len(prefix) :].strip()
            break

    return first_sentence


def _extract_behavior(text: str) -> list[str]:
    """Extract specific behaviors/capabilities mentioned."""
    behaviors = []
    lower_text = text.lower()

    # Action verbs commonly used in agent descriptions
    action_patterns = [
        ("fetch", "Fetch data"),
        ("retrieve", "Retrieve information"),
        ("summarize", "Summarize content"),
        ("analyze", "Analyze data"),
        ("generate", "Generate output"),
        ("process", "Process input"),
        ("transform", "Transform data"),
        ("validate", "Validate input"),
        ("format", "Format output"),
        ("export", "Export results"),
        ("query", "Query sources"),
        ("parse", "Parse data"),
    ]

    for keyword, behavior_desc in action_patterns:
        if keyword in lower_text:
            behaviors.append(behavior_desc)

    return behaviors


def _extract_constraints(text: str) -> list[str]:
    """Extract constraints/requirements from text."""
    constraints = []
    lower_text = text.lower()

    # Common constraint patterns
    constraint_patterns = [
        ("concise", "Output should be concise"),
        ("objective", "Maintain objective tone"),
        ("no jargon", "Avoid technical jargon"),
        ("timeout", "Respect timeout limits"),
        ("idempotent", "Must be idempotent"),
        ("error handling", "Robust error handling required"),
        ("no hallucination", "No hallucinations allowed"),
        ("deterministic", "Must be deterministic"),
        ("fast", "Performance should be fast"),
        ("secure", "Security requirements must be met"),
    ]

    for keyword, constraint_desc in constraint_patterns:
        if keyword in lower_text:
            constraints.append(constraint_desc)

    # Extract explicit constraints (sentences with "must", "should", "require")
    for sentence in text.split("."):
        if any(word in sentence.lower() for word in ["must", "should", "require"]):
            constraints.append(sentence.strip())

    return constraints


def _extract_tone(text: str) -> str | None:
    """Detect if a tone/personality is specified."""
    lower_text = text.lower()

    tone_keywords = {
        "friendly": "friendly",
        "formal": "formal",
        "casual": "casual",
        "professional": "professional",
        "concise": "concise",
        "verbose": "verbose",
        "humorous": "humorous",
        "serious": "serious",
    }

    for keyword, tone_value in tone_keywords.items():
        if keyword in lower_text:
            return tone_value

    return None


def _analyze_dependencies(text: str) -> list[Dependency]:
    """Identify external dependencies mentioned in the text."""
    dependencies = []
    lower_text = text.lower()

    # Dependency detection patterns
    dependency_patterns = [
        # REST APIs
        (["api", "rest", "endpoint", "http"], DependencyType.REST_API, "External API"),
        # Databases
        (
            ["database", "postgres", "mysql", "mongodb", "sql"],
            DependencyType.DATABASE,
            "Database",
        ),
        # File system
        (
            ["file", "csv", "json file", "pdf", "document"],
            DependencyType.FILE_SYSTEM,
            "File system",
        ),
        # Network
        (["fetch", "download", "network"], DependencyType.NETWORK, "Network access"),
        # External agents
        (["agent", "another agent"], DependencyType.EXTERNAL_AGENT, "External agent"),
    ]

    for keywords, dep_type, dep_name in dependency_patterns:
        if any(keyword in lower_text for keyword in keywords):
            # Check if we already have this type
            if not any(d.type == dep_type for d in dependencies):
                dependencies.append(
                    Dependency(
                        name=dep_name,
                        type=dep_type,
                        description=f"Detected from keywords: {keywords}",
                    )
                )

    return dependencies


def _detect_ambiguities(text: str) -> list[str]:
    """Detect potential ambiguities that may need H-gent resolution."""
    ambiguities = []
    lower_text = text.lower()

    # Vague quantifiers
    vague_terms = ["some", "several", "many", "few", "various", "multiple"]
    for term in vague_terms:
        if f" {term} " in f" {lower_text} ":
            ambiguities.append(f"Vague quantifier: '{term}' needs clarification")

    # Missing error handling specification
    if "error" not in lower_text and "fail" not in lower_text:
        ambiguities.append("Error handling strategy not specified")

    # Missing performance requirements
    if not any(word in lower_text for word in ["fast", "slow", "timeout", "latency"]):
        ambiguities.append("Performance requirements not specified")

    return ambiguities
