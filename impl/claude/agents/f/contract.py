"""
Contract synthesis for F-gents (Phase 2: Contract).

This module implements the Intent → Contract morphism from spec/f-gents/forge.md.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from agents.f.intent import DependencyType, Intent


@dataclass
class Invariant:
    """A testable property that the agent must satisfy."""

    description: str  # Human-readable invariant statement
    property: str  # Testable property (e.g., "f(f(x)) == f(x)" for idempotent)
    category: str  # "structural", "behavioral", or "categorical"


@dataclass
class CompositionRule:
    """Rules for how this agent composes with others."""

    mode: str  # "sequential", "parallel", "conditional", "fan-out", "fan-in"
    description: str  # Explanation of composition behavior
    type_constraint: str = ""  # Any type requirements for composition


@dataclass
class Contract:
    """
    Formal interface specification for an agent.

    This is the output of Phase 2 (Contract) and input to Phase 3 (Prototype).

    A contract defines:
    - Type signatures (what goes in, what comes out)
    - Invariants (behavioral guarantees)
    - Composition rules (how it connects to other agents)

    Fields align with spec/f-gents/forge.md Phase 2 outputs.
    """

    agent_name: str  # Derived from intent purpose
    input_type: str  # Type signature for input (e.g., "str", "dict", "Path")
    output_type: str  # Type signature for output
    invariants: list[Invariant] = field(default_factory=list)  # Testable behavioral guarantees
    composition_rules: list[CompositionRule] = field(default_factory=list)  # How agent composes
    semantic_intent: str = ""  # Human-readable "why" (from intent.purpose)

    # Metadata
    raw_intent: Intent | None = None  # Source of truth for lineage tracking

    # G-gent Integration (optional)
    # Stores tongue embedding for artifacts with DSL interfaces
    # See spec/g-gents/integration.md "F-gent Integration"
    interface_tongue: Optional[dict[str, Any]] = None  # TongueEmbedding.to_dict()


def synthesize_contract(intent: Intent, agent_name: str = "Agent") -> Contract:
    """
    Synthesize formal contract from intent.

    This is the core morphism of Phase 2 (Contract):
        Intent → Contract

    Current implementation uses heuristics for type synthesis. Future versions will use:
    - LLM for semantic type inference
    - C-gent for category law verification
    - L-gent lattice for ontology alignment

    Args:
        intent: Structured intent from Phase 1
        agent_name: Name for the agent (default: "Agent")

    Returns:
        Contract specification ready for Phase 3 (Prototype)

    Examples:
        >>> from agents.f.intent import parse_intent
        >>> intent = parse_intent("Create an agent that fetches weather from an API")
        >>> contract = synthesize_contract(intent, "WeatherAgent")
        >>> contract.input_type
        'str'
        >>> contract.output_type
        'dict'
    """
    # Type synthesis: Infer I and O from intent
    input_type = _infer_input_type(intent)
    output_type = _infer_output_type(intent)

    # Invariant extraction: Convert constraints to testable properties
    invariants = _extract_invariants(intent)

    # Composition analysis: Determine how agent composes
    composition_rules = _determine_composition_rules(intent)

    return Contract(
        agent_name=agent_name,
        input_type=input_type,
        output_type=output_type,
        invariants=invariants,
        composition_rules=composition_rules,
        semantic_intent=intent.purpose,
        raw_intent=intent,
    )


def _infer_input_type(intent: Intent) -> str:
    """
    Infer input type from intent.

    Uses heuristics based on:
    - Dependencies (REST_API → str (URL), FILE_SYSTEM → Path)
    - Behavior keywords (parse → str, query → str, process → Any)
    - Purpose statement

    Future: Replace with LLM semantic analysis.
    """
    lower_purpose = intent.purpose.lower()
    lower_text = intent.raw_text.lower()

    # Check dependencies for type hints
    for dep in intent.dependencies:
        if dep.type == DependencyType.FILE_SYSTEM:
            if "path" in lower_text or "file" in lower_text:
                return "Path"
        elif dep.type == DependencyType.REST_API:
            return "str"  # Typically URL
        elif dep.type == DependencyType.DATABASE:
            return "str"  # Typically query string

    # Check behavior patterns
    if any(keyword in lower_purpose for keyword in ["summarize", "analyze", "process text"]):
        return "str"

    if any(keyword in lower_purpose for keyword in ["parse", "read"]):
        if "json" in lower_text:
            return "str | dict"
        return "str"

    if "query" in lower_purpose:
        return "str"

    # Default: Generic input
    return "Any"


def _infer_output_type(intent: Intent) -> str:
    """
    Infer output type from intent.

    Uses heuristics based on:
    - Purpose keywords (to JSON → dict, to file → Path)
    - Constraints (structured output → dict)
    - Behavior patterns

    Future: Replace with LLM semantic analysis.
    """
    lower_purpose = intent.purpose.lower()
    lower_text = intent.raw_text.lower()

    # Explicit output format mentions
    if "json" in lower_text or "dict" in lower_text:
        return "dict"

    if "to file" in lower_text or "export" in lower_text:
        return "Path"

    if "list" in lower_text or "multiple" in lower_text:
        return "list"

    if "summary" in lower_purpose or "summarize" in lower_purpose:
        return "str"

    if "boolean" in lower_text or "true/false" in lower_text:
        return "bool"

    # Check for structured output constraints
    if any(
        "structured" in constraint.lower() or "format" in constraint.lower()
        for constraint in intent.constraints
    ):
        return "dict"

    # REST API typically returns dict/JSON
    for dep in intent.dependencies:
        if dep.type == DependencyType.REST_API:
            return "dict"

    # Default: Generic output
    return "Any"


def _extract_invariants(intent: Intent) -> list[Invariant]:
    """
    Extract testable invariants from intent constraints.

    Maps constraint keywords to formal properties:
    - "idempotent" → f(f(x)) == f(x)
    - "pure" → no side effects
    - "deterministic" → same input → same output
    - "bounded" → completes in finite time
    - "no hallucinations" → all outputs grounded in input

    These become test cases in Phase 4 (Validate).
    """
    invariants = []
    lower_text = intent.raw_text.lower()

    # Structural invariants (type-level)
    if "type" in lower_text or "typed" in lower_text:
        invariants.append(
            Invariant(
                description="Type safety",
                property="isinstance(output, expected_type)",
                category="structural",
            )
        )

    # Behavioral invariants (function-level)
    invariant_patterns = [
        (
            "idempotent",
            "Idempotency",
            "f(f(x)) == f(x)",
            "behavioral",
        ),
        (
            "deterministic",
            "Determinism",
            "f(x) == f(x) for all calls",
            "behavioral",
        ),
        (
            "pure",
            "Purity (no side effects)",
            "no state mutation or I/O",
            "behavioral",
        ),
        (
            "concise",
            "Conciseness",
            "len(output) < MAX_LENGTH",
            "behavioral",
        ),
        (
            "objective",
            "Objectivity",
            "no subjective statements",
            "behavioral",
        ),
        (
            "no hallucination",
            "No hallucinations",
            "all_citations_exist_in(input, output)",
            "behavioral",
        ),
    ]

    for keyword, desc, prop, category in invariant_patterns:
        if keyword in lower_text or keyword in intent.purpose.lower():
            invariants.append(Invariant(description=desc, property=prop, category=category))

    # Extract constraints that mention "must", "should", "require"
    for constraint in intent.constraints:
        if any(word in constraint.lower() for word in ["must", "should", "require", "no "]):
            invariants.append(
                Invariant(
                    description=constraint,
                    property=f"verify: {constraint}",
                    category="behavioral",
                )
            )

    # Categorical invariants (composition-level)
    if any(keyword in lower_text for keyword in ["compose", "pipeline", "chain", "sequence"]):
        invariants.append(
            Invariant(
                description="Associativity",
                property="(f >> g) >> h == f >> (g >> h)",
                category="categorical",
            )
        )

    return invariants


def _determine_composition_rules(intent: Intent) -> list[CompositionRule]:
    """
    Determine how this agent composes with others.

    Analyzes:
    - Dependency structure (single input/output → sequential)
    - Behavior patterns (multiple independent tasks → parallel)
    - Conditional logic (if/then/else → conditional)

    This is the "Ontology Alignment" step from spec/f-gents/forge.md Phase 2.
    """
    rules = []
    lower_text = intent.raw_text.lower()

    # Sequential composition (most common)
    if len(intent.dependencies) <= 1:
        rules.append(
            CompositionRule(
                mode="sequential",
                description="Single input/output flow, can compose via >>",
                type_constraint="Output type must match next agent's input type",
            )
        )

    # Parallel composition
    if len(intent.dependencies) > 1:
        independent_deps = sum(
            1
            for dep in intent.dependencies
            if dep.type
            in [
                DependencyType.REST_API,
                DependencyType.NETWORK,
                DependencyType.DATABASE,
            ]
        )
        if independent_deps > 1:
            rules.append(
                CompositionRule(
                    mode="parallel",
                    description="Multiple independent dependencies can execute concurrently",
                    type_constraint="Each dependency has separate input/output",
                )
            )

    # Parallel keywords
    if "parallel" in lower_text or "concurrent" in lower_text:
        if not any(rule.mode == "parallel" for rule in rules):
            rules.append(
                CompositionRule(
                    mode="parallel",
                    description="Parallel execution explicitly mentioned",
                    type_constraint="Concurrent processing of inputs",
                )
            )

    # Conditional composition
    if any(keyword in lower_text for keyword in ["if", "when", "conditional", "either", "or"]):
        rules.append(
            CompositionRule(
                mode="conditional",
                description="Routing based on input conditions",
                type_constraint="All branches must have same output type",
            )
        )

    # Fan-out (one input, multiple outputs)
    if "broadcast" in lower_text or "fan out" in lower_text:
        rules.append(
            CompositionRule(
                mode="fan-out",
                description="Single input produces multiple outputs",
                type_constraint="Input type → list[Output type]",
            )
        )

    # Fan-in (multiple inputs, one output)
    if "combine" in lower_text or "merge" in lower_text or "aggregate" in lower_text:
        rules.append(
            CompositionRule(
                mode="fan-in",
                description="Multiple inputs combined into single output",
                type_constraint="list[Input type] → Output type",
            )
        )

    # Default: assume sequential if no rules detected
    if not rules:
        rules.append(
            CompositionRule(
                mode="sequential",
                description="Default sequential composition",
                type_constraint="Standard Agent[I, O] composition",
            )
        )

    return rules
