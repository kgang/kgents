"""
Grammar Synthesis Engine

Core G-gent capability: synthesize grammars from domain intent + constraints.

This module implements the three-level grammar synthesis pipeline:
1. Domain Analysis: Extract entities, operations, constraints from intent
2. Grammar Generation: Create BNF/EBNF/Pydantic from analysis
3. Grammar Refinement: Eliminate ambiguities

The key innovation: constraints become STRUCTURAL (encoded in grammar),
not runtime checks. Forbidden operations are grammatically impossible.
"""

import re

from agents.g.types import (
    GrammarLevel,
    GrammarFormat,
    DomainAnalysis,
    ParserConfig,
    InterpreterConfig,
)


# ============================================================================
# Domain Analysis
# ============================================================================


async def analyze_domain(
    intent: str,
    constraints: list[str],
    examples: list[str] | None = None,
) -> DomainAnalysis:
    """
    Analyze a domain from natural language intent + constraints.

    This is a simplified version that uses heuristics. In production,
    this would use an LLM to extract domain primitives.

    Steps:
    1. Extract entities (nouns) from intent
    2. Extract operations (verbs) from intent
    3. Apply constraints to filter operations
    4. Build lexicon from entity/operation names

    Args:
        intent: Natural language description of domain
        constraints: List of constraint statements
        examples: Optional example inputs for the DSL

    Returns:
        DomainAnalysis with extracted primitives
    """
    # Extract entities (capitalized nouns)
    entities = _extract_entities(intent, examples or [])

    # Extract operations (verbs, action words)
    operations = _extract_operations(intent, examples or [])

    # Apply constraints (filter out forbidden operations)
    allowed_operations = _apply_constraints(operations, constraints)

    # Build lexicon
    lexicon = set()
    lexicon.update(entities)
    lexicon.update(allowed_operations)

    # Extract relationships (heuristic: "X has Y", "X contains Y")
    relationships = _extract_relationships(intent)

    return DomainAnalysis(
        entities=set(entities),
        operations=set(allowed_operations),
        constraints=constraints,
        relationships=relationships,
        lexicon=lexicon,
        semantics={},  # Will be filled in later
    )


def _extract_entities(intent: str, examples: list[str]) -> list[str]:
    """
    Extract entity names (nouns) from intent.

    Heuristics:
    - Capitalized words (e.g., "Calendar", "Event", "User")
    - Common domain nouns (file, directory, item, record)
    """
    entities = []

    # Capitalized words (but not at start of sentence)
    words = intent.split()
    for i, word in enumerate(words):
        # Strip punctuation
        clean_word = word.strip(".,;:!?")
        if clean_word and clean_word[0].isupper() and i > 0:
            entities.append(clean_word.lower())

    # Common domain nouns
    common_nouns = [
        "file",
        "directory",
        "folder",
        "item",
        "record",
        "entry",
        "document",
        "object",
        "entity",
        "resource",
        "event",
        "task",
        "user",
        "data",
        "field",
        "value",
    ]

    for noun in common_nouns:
        if noun in intent.lower():
            entities.append(noun)

    # Extract from examples
    for example in examples:
        # Look for patterns like "READ file", "ADD event"
        parts = example.split()
        if len(parts) >= 2:
            # Second word is often the entity
            entities.append(parts[1].lower())

    return list(set(entities))  # Deduplicate


def _extract_operations(intent: str, examples: list[str]) -> list[str]:
    """
    Extract operation names (verbs) from intent.

    Heuristics:
    - Common action verbs (read, write, create, delete, etc.)
    - First word in examples (often the verb in command grammars)
    """
    operations = []

    # Common action verbs
    common_verbs = [
        "read",
        "write",
        "create",
        "delete",
        "update",
        "list",
        "get",
        "set",
        "add",
        "remove",
        "check",
        "query",
        "search",
        "find",
        "copy",
        "move",
        "rename",
        "modify",
        "edit",
        "save",
        "load",
        "fetch",
        "put",
        "post",
        "patch",
    ]

    for verb in common_verbs:
        if verb in intent.lower():
            operations.append(verb.upper())

    # Extract from examples (first word is often the verb)
    for example in examples:
        parts = example.split()
        if parts:
            verb = parts[0].upper()
            operations.append(verb)

    return list(set(operations))  # Deduplicate


def _apply_constraints(operations: list[str], constraints: list[str]) -> list[str]:
    """
    Filter operations based on constraints.

    Constraints like "No deletes" or "Read-only" remove operations.
    """
    forbidden_ops = set()

    for constraint in constraints:
        lower_constraint = constraint.lower()

        # "No X" pattern
        if "no " in lower_constraint:
            # Extract forbidden operation
            match = re.search(r"no (\w+)", lower_constraint)
            if match:
                forbidden = match.group(1).upper()
                # Handle plural (e.g., "no deletes" -> "DELETE")
                if forbidden.endswith("S"):
                    forbidden = forbidden[:-1]
                forbidden_ops.add(forbidden)

        # "Read-only" pattern
        if "read-only" in lower_constraint or "readonly" in lower_constraint:
            # Only allow READ operations
            return [
                op
                for op in operations
                if "READ" in op
                or "GET" in op
                or "LIST" in op
                or "QUERY" in op
                or "CHECK" in op
            ]

        # Explicit forbidden operations
        for op in ["DELETE", "DROP", "REMOVE", "MODIFY", "UPDATE", "WRITE", "CREATE"]:
            if op.lower() in lower_constraint and "no " in lower_constraint:
                forbidden_ops.add(op)

    # Filter out forbidden operations
    return [op for op in operations if op not in forbidden_ops]


def _extract_relationships(intent: str) -> dict[str, list[str]]:
    """
    Extract entity relationships from intent.

    Heuristics:
    - "X has Y" -> {"X": ["Y"]}
    - "X contains Y" -> {"X": ["Y"]}
    """
    relationships: dict[str, list[str]] = {}

    # Pattern: "X has/contains Y"
    patterns = [
        r"(\w+)\s+has\s+(\w+)",
        r"(\w+)\s+contains\s+(\w+)",
        r"(\w+)\s+includes\s+(\w+)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, intent.lower())
        for match in matches:
            parent, child = match.groups()
            if parent not in relationships:
                relationships[parent] = []
            relationships[parent].append(child)

    return relationships


# ============================================================================
# Grammar Generation
# ============================================================================


async def synthesize_grammar(
    analysis: DomainAnalysis,
    level: GrammarLevel,
    format: GrammarFormat | None = None,
) -> str:
    """
    Generate grammar specification from domain analysis.

    Args:
        analysis: Domain analysis from analyze_domain()
        level: Grammar level (SCHEMA, COMMAND, RECURSIVE)
        format: Optional specific format (inferred from level if not provided)

    Returns:
        Grammar specification as string
    """
    # Infer format from level if not provided
    if format is None:
        format = _infer_format(level)

    match level:
        case GrammarLevel.SCHEMA:
            return _generate_schema(analysis)
        case GrammarLevel.COMMAND:
            return _generate_command_bnf(analysis)
        case GrammarLevel.RECURSIVE:
            return _generate_recursive_bnf(analysis)


def _infer_format(level: GrammarLevel) -> GrammarFormat:
    """Infer grammar format from level."""
    match level:
        case GrammarLevel.SCHEMA:
            return GrammarFormat.PYDANTIC
        case GrammarLevel.COMMAND:
            return GrammarFormat.BNF
        case GrammarLevel.RECURSIVE:
            return GrammarFormat.LARK


def _generate_schema(analysis: DomainAnalysis) -> str:
    """
    Generate Pydantic schema from domain analysis (Level 1).

    Creates a Pydantic BaseModel with fields for each entity.
    """
    lines = ["from pydantic import BaseModel, Field", "", ""]

    # Generate model class
    model_name = "GeneratedModel"
    lines.append(f"class {model_name}(BaseModel):")
    lines.append('    """Generated schema from G-gent synthesis."""')
    lines.append("")

    # Add fields for each entity
    if not analysis.entities:
        # If no entities, create a simple model
        lines.append("    name: str")
        lines.append("    value: str")
    else:
        for entity in sorted(analysis.entities):
            # Simple type inference (could be more sophisticated)
            field_name = entity.replace(" ", "_").lower()
            lines.append(f"    {field_name}: str")

    return "\n".join(lines)


def _generate_command_bnf(analysis: DomainAnalysis) -> str:
    """
    Generate BNF command grammar from domain analysis (Level 2).

    Creates a simple Verb-Noun command language.
    """
    lines = []

    # CMD production (top-level)
    lines.append("CMD ::= VERB NOUN ARGS*")

    # VERB production (only allowed operations)
    if analysis.operations:
        verb_alts = " | ".join(f'"{op}"' for op in sorted(analysis.operations))
        lines.append(f"VERB ::= {verb_alts}")
    else:
        lines.append('VERB ::= "NOOP"')

    # NOUN production (entities)
    if analysis.entities:
        noun_alts = " | ".join(f'"{ent}"' for ent in sorted(analysis.entities))
        lines.append(f"NOUN ::= {noun_alts}")
    else:
        lines.append('NOUN ::= "object"')

    # ARGS production (arguments/modifiers)
    lines.append("ARGS ::= STRING | NUMBER | MODIFIER")
    lines.append("MODIFIER ::= PREP NOUN")
    lines.append('PREP ::= "to" | "from" | "with" | "by" | "at"')

    # Terminals
    lines.append('STRING ::= "\\"" [^"]* "\\""')
    lines.append("NUMBER ::= [0-9]+")

    return "\n".join(lines)


def _generate_recursive_bnf(analysis: DomainAnalysis) -> str:
    """
    Generate recursive Lark grammar from domain analysis (Level 3).

    Creates an S-expression style grammar with full recursion.
    """
    lines = []

    # Start rule
    lines.append("start: expr")
    lines.append("")

    # Expression (recursive)
    lines.append("expr: atom")
    lines.append('    | "(" op expr* ")"')
    lines.append("")

    # Operator production (operations)
    if analysis.operations:
        op_alts = " | ".join(f'"{op.lower()}"' for op in sorted(analysis.operations))
        lines.append(f"op: {op_alts}")
    else:
        lines.append('op: "noop"')
    lines.append("")

    # Atom (terminals)
    lines.append("atom: STRING")
    lines.append("    | NUMBER")
    lines.append("    | SYMBOL")
    if analysis.entities:
        lines.append("    | ENTITY")
    lines.append("")

    # Entity references (if any)
    if analysis.entities:
        entity_alts = " | ".join(f'"{ent}"' for ent in sorted(analysis.entities))
        lines.append(f"ENTITY: {entity_alts}")
        lines.append("")

    # Terminals
    lines.append('STRING: /"[^"]*"/')
    lines.append("NUMBER: /[0-9]+/")
    lines.append("SYMBOL: /[a-z][a-z0-9_]*/")
    lines.append("")

    # Whitespace
    lines.append("%import common.WS")
    lines.append("%ignore WS")

    return "\n".join(lines)


# ============================================================================
# Configuration Generation
# ============================================================================


def generate_parser_config(
    grammar: str, level: GrammarLevel, format: GrammarFormat
) -> ParserConfig:
    """
    Generate P-gent ParserConfig from grammar and level.

    Maps grammar level/format to appropriate parsing strategy.
    """
    match level:
        case GrammarLevel.SCHEMA:
            return ParserConfig(
                strategy="pydantic",
                grammar_format=GrammarFormat.PYDANTIC,
                confidence_threshold=1.0,  # Schema validation is binary
                repair_strategy="fail",  # Pydantic handles its own validation
            )
        case GrammarLevel.COMMAND:
            return ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
                confidence_threshold=0.95,
                repair_strategy="best_effort",
            )
        case GrammarLevel.RECURSIVE:
            return ParserConfig(
                strategy="lark",
                grammar_format=GrammarFormat.LARK,
                confidence_threshold=0.9,
                repair_strategy="best_effort",
            )


def generate_interpreter_config(level: GrammarLevel) -> InterpreterConfig:
    """
    Generate J-gent InterpreterConfig from grammar level.

    Maps grammar level to appropriate execution environment.
    """
    match level:
        case GrammarLevel.SCHEMA:
            return InterpreterConfig(
                runtime="python",
                pure_functions_only=True,  # Schema processing is pure
                timeout_ms=1000,  # Fast for schemas
            )
        case GrammarLevel.COMMAND:
            return InterpreterConfig(
                runtime="python",
                pure_functions_only=False,  # Commands may have side effects
                timeout_ms=5000,
            )
        case GrammarLevel.RECURSIVE:
            return InterpreterConfig(
                runtime="sandboxed",  # Recursive execution needs isolation
                pure_functions_only=True,
                timeout_ms=10000,  # More time for complex evaluation
            )
