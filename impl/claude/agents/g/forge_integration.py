"""
G-gent Phase 5: F-gent (Forge) Integration

Bridges G-gent tongue synthesis with F-gent artifact forging.

From spec/g-gents/integration.md "F-gent Integration" and "The Spellbook Pattern":
- F-gent uses G-gent to create interface languages for artifacts
- Artifacts become "spellbooks" with G-gent-defined command languages
- Invocation via DSL: `artifact.invoke(command)` uses `tongue.parse >> tongue.execute`

Key Functions:
- `create_artifact_interface()`: Generate a Tongue for an artifact's command interface
- `embed_tongue_in_contract()`: Bundle tongue metadata with F-gent contract
- `create_invocation_handler()`: Create a function that parses and executes DSL commands
- `forge_with_interface()`: Complete flow from intent to artifact with G-gent interface
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from agents.g.grammarian import Grammarian, reify_command, reify_schema
from agents.g.interpreter import execute_with_tongue
from agents.g.parser import parse_with_tongue
from agents.g.types import (
    ExecutionResult,
    GrammarFormat,
    GrammarLevel,
    ParseResult,
    Tongue,
)

# F-gent imports (may not be available)
try:
    from agents.f.contract import CompositionRule, Contract, Invariant
    from agents.f.intent import Intent

    FGENT_AVAILABLE = True
except ImportError:
    FGENT_AVAILABLE = False
    Contract = None
    Intent = None


@dataclass
class InterfaceTongue:
    """
    A Tongue bundled with F-gent artifact metadata.

    This represents a G-gent-generated interface language that has been
    prepared for embedding in an F-gent contract/artifact.

    Attributes:
        tongue: The underlying Tongue artifact
        artifact_name: Name of the artifact this interface serves
        operations: Mapping of verbs to their semantic descriptions
        handlers: Optional handler functions for execution
        examples: Example commands showing usage
    """

    tongue: Tongue
    artifact_name: str
    operations: dict[str, str] = field(default_factory=dict)
    handlers: dict[str, Callable] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    def parse(self, command: str) -> ParseResult:
        """Parse a DSL command using the embedded tongue."""
        return parse_with_tongue(command, self.tongue)

    def execute(self, command: str, context: Optional[dict] = None) -> ExecutionResult:
        """Parse and execute a DSL command."""
        parse_result = self.parse(command)
        if not parse_result.success:
            return ExecutionResult(
                success=False,
                value=None,
                error="; ".join(parse_result.errors) if parse_result.errors else None,
            )

        return execute_with_tongue(
            parse_result.ast,
            self.tongue,
            handlers=self.handlers,
            context=context or {},
        )

    def invoke(self, command: str, context: Optional[dict] = None) -> Any:
        """
        High-level invocation: parse, execute, return result or raise.

        This is the main entry point for artifact users:
        `artifact.interface.invoke("CHECK 2024-12-15")`

        Args:
            command: DSL command string
            context: Optional execution context

        Returns:
            Execution result value

        Raises:
            ValueError: If parsing or execution fails
        """
        result = self.execute(command, context)
        if not result.success:
            errors = result.errors or ["Unknown execution error"]
            raise ValueError(f"Command failed: {'; '.join(errors)}")
        return result.value


@dataclass
class TongueEmbedding:
    """
    Metadata for embedding a tongue in an F-gent contract.

    This is the serializable representation that gets stored
    in the contract/artifact for later reconstruction.

    Attributes:
        tongue_name: Name of the tongue
        tongue_domain: Domain this tongue serves
        tongue_level: Grammar level (SCHEMA, COMMAND, RECURSIVE)
        tongue_format: Grammar format (BNF, PYDANTIC, etc.)
        grammar_spec: The grammar specification string
        constraints: List of constraints encoded in grammar
        operations: Available operations (verbs)
        examples: Example usage strings
    """

    tongue_name: str
    tongue_domain: str
    tongue_level: str
    tongue_format: str
    grammar_spec: str
    constraints: list[str] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dict for storage in contract."""
        return {
            "tongue_name": self.tongue_name,
            "tongue_domain": self.tongue_domain,
            "tongue_level": self.tongue_level,
            "tongue_format": self.tongue_format,
            "grammar_spec": self.grammar_spec,
            "constraints": self.constraints,
            "operations": self.operations,
            "examples": self.examples,
        }

    @staticmethod
    def from_dict(data: dict) -> "TongueEmbedding":
        """Deserialize from dict."""
        return TongueEmbedding(
            tongue_name=data["tongue_name"],
            tongue_domain=data["tongue_domain"],
            tongue_level=data["tongue_level"],
            tongue_format=data["tongue_format"],
            grammar_spec=data["grammar_spec"],
            constraints=data.get("constraints", []),
            operations=data.get("operations", []),
            examples=data.get("examples", []),
        )

    @staticmethod
    def from_tongue(tongue: Tongue) -> "TongueEmbedding":
        """Create embedding from a Tongue artifact."""
        # Extract operations from grammar (simple heuristic for BNF)
        operations = []
        if tongue.grammar_format == GrammarFormat.BNF:
            # Extract verbs from BNF grammar like: <verb> ::= "CHECK" | "ADD"
            import re

            verb_match = re.search(r"<verb>\s*::=\s*(.+?)(?:\n|$)", tongue.grammar)
            if verb_match:
                verbs = re.findall(r'"(\w+)"', verb_match.group(1))
                operations = verbs

        # Tongue.constraints is tuple[str, ...] (plain strings)
        # Tongue.constraint_proofs is tuple[ConstraintProof, ...] (objects with .constraint attr)
        constraints = list(tongue.constraints)

        return TongueEmbedding(
            tongue_name=tongue.name,
            tongue_domain=tongue.domain,
            tongue_level=tongue.level.name,
            tongue_format=tongue.grammar_format.name,
            grammar_spec=tongue.grammar,
            constraints=constraints,
            operations=operations,
            examples=[ex.input for ex in tongue.examples] if tongue.examples else [],
        )


async def create_artifact_interface(
    domain: str,
    constraints: Optional[list[str]] = None,
    operations: Optional[dict[str, str]] = None,
    level: GrammarLevel = GrammarLevel.COMMAND,
    examples: Optional[list[str]] = None,
    artifact_name: Optional[str] = None,
) -> InterfaceTongue:
    """
    Create a G-gent interface tongue for an F-gent artifact.

    This is the primary bridge function: given a domain and constraints,
    it synthesizes a Tongue that defines the artifact's command interface.

    From spec/g-gents/integration.md "The Spellbook Pattern":
    - F-gent uses G-gent to create interface languages for artifacts
    - The tongue defines what commands the artifact accepts
    - Constraints become grammatically impossible operations

    Args:
        domain: The artifact's operational domain (e.g., "Calendar Management")
        constraints: Safety constraints (e.g., ["No deletes", "No overwrites"])
        operations: Optional mapping of verbs to descriptions
        level: Grammar complexity level (default: COMMAND for verb-noun)
        examples: Example commands showing usage
        artifact_name: Name of the artifact (default: derived from domain)

    Returns:
        InterfaceTongue ready for embedding in an artifact

    Example:
        >>> interface = await create_artifact_interface(
        ...     domain="Calendar Management",
        ...     constraints=["No deletes", "No modifications"],
        ...     operations={"CHECK": "View calendar entries", "ADD": "Create new entry"}
        ... )
        >>> interface.invoke("CHECK 2024-12-15")
    """
    constraints = constraints or []
    operations = operations or {}
    examples = examples or []

    # Derive artifact name from domain if not provided
    if artifact_name is None:
        # "Calendar Management" -> "CalendarAgent"
        artifact_name = domain.replace(" ", "").split()[0] + "Agent"

    # Use Grammarian to synthesize tongue
    grammarian = Grammarian()

    if level == GrammarLevel.COMMAND:
        tongue = await reify_command(
            domain=domain,
            constraints=constraints,
            examples=examples,  # Pass strings directly; reify_command expects list[str]
        )
    elif level == GrammarLevel.SCHEMA:
        tongue = await reify_schema(
            domain=domain,
            constraints=constraints,
        )
    else:
        # Recursive level
        tongue = await grammarian.reify(
            domain=domain,
            constraints=constraints,
            level=level,
        )

    # Build operations dict from grammar if not provided
    if not operations and tongue.grammar_format == GrammarFormat.BNF:
        import re

        verb_match = re.search(r"<verb>\s*::=\s*(.+?)(?:\n|$)", tongue.grammar)
        if verb_match:
            verbs = re.findall(r'"(\w+)"', verb_match.group(1))
            operations = {verb: f"{verb} operation" for verb in verbs}

    return InterfaceTongue(
        tongue=tongue,
        artifact_name=artifact_name,
        operations=operations,
        handlers={},  # Handlers added later via bind_handlers()
        examples=examples,
    )


def embed_tongue_in_contract(
    contract: "Contract",
    interface_tongue: InterfaceTongue,
) -> "Contract":
    """
    Embed tongue metadata into an F-gent contract.

    This bundles the G-gent-generated interface language with the
    F-gent contract, enabling the artifact to be invoked via DSL.

    From spec/g-gents/integration.md:
    - Contract structure includes interface tongue
    - Artifact invocation via `tongue.parse >> tongue.execute`

    Args:
        contract: F-gent Contract to augment
        interface_tongue: G-gent InterfaceTongue to embed

    Returns:
        New Contract with tongue embedding

    Raises:
        ValueError: If F-gent is not available

    Note:
        This creates a new contract; the original is not modified.
    """
    if not FGENT_AVAILABLE:
        raise ValueError("F-gent is not available. Cannot embed tongue in contract.")

    # Create tongue embedding
    embedding = TongueEmbedding.from_tongue(interface_tongue.tongue)

    # Add tongue-related invariants
    tongue_invariants = [
        Invariant(
            description=f"Interface language: {interface_tongue.tongue.name}",
            property=f"invocable via DSL: {interface_tongue.tongue.domain}",
            category="structural",
        ),
    ]

    # Add constraint invariants from tongue (constraints are plain strings)
    for constraint in interface_tongue.tongue.constraints:
        tongue_invariants.append(
            Invariant(
                description=f"DSL constraint: {constraint}",
                property=f"structural: {constraint}",
                category="structural",
            )
        )

    # Create tongue embedding for storage
    embedding = TongueEmbedding.from_tongue(interface_tongue.tongue)

    # Create new contract with tongue metadata
    return Contract(
        agent_name=contract.agent_name,
        input_type=f"DSL<{interface_tongue.tongue.domain}>",  # Input is now DSL
        output_type=contract.output_type,
        invariants=list(contract.invariants) + tongue_invariants,
        composition_rules=list(contract.composition_rules),
        semantic_intent=contract.semantic_intent,
        raw_intent=contract.raw_intent,
        interface_tongue=embedding.to_dict(),  # Store tongue embedding
    )


def create_invocation_handler(
    interface_tongue: InterfaceTongue,
    handlers: Optional[dict[str, Callable]] = None,
) -> Callable[[str, Optional[dict]], Any]:
    """
    Create a function that handles DSL command invocation.

    This produces the `invoke()` function that artifacts use to
    process user commands through the G-gent tongue.

    Args:
        interface_tongue: The interface tongue defining the DSL
        handlers: Mapping of verbs to handler functions

    Returns:
        Function (command: str, context: dict) -> Any

    Example:
        >>> invoke = create_invocation_handler(interface, handlers={
        ...     "CHECK": lambda noun, ctx: calendar.check(noun),
        ...     "ADD": lambda noun, ctx: calendar.add(noun),
        ... })
        >>> result = invoke("CHECK 2024-12-15", {})
    """
    if handlers:
        interface_tongue.handlers.update(handlers)

    def invoke_handler(command: str, context: Optional[dict] = None) -> Any:
        return interface_tongue.invoke(command, context)

    return invoke_handler


def bind_handlers(
    interface_tongue: InterfaceTongue,
    handlers: dict[str, Callable],
) -> InterfaceTongue:
    """
    Bind handler functions to an interface tongue.

    Handlers are functions that execute when a verb is invoked:
    `handler(noun: str, context: dict) -> result`

    Args:
        interface_tongue: The interface tongue to bind handlers to
        handlers: Mapping of verbs to handler functions

    Returns:
        Same InterfaceTongue with handlers bound

    Example:
        >>> interface = await create_artifact_interface(domain="Calendar")
        >>> interface = bind_handlers(interface, {
        ...     "CHECK": lambda noun, ctx: f"Checking {noun}",
        ...     "ADD": lambda noun, ctx: f"Adding {noun}",
        ... })
    """
    interface_tongue.handlers.update(handlers)
    return interface_tongue


async def forge_with_interface(
    intent_text: str,
    domain: str,
    constraints: Optional[list[str]] = None,
    operations: Optional[dict[str, str]] = None,
    handlers: Optional[dict[str, Callable]] = None,
) -> tuple["Contract", InterfaceTongue]:
    """
    Complete flow: Create F-gent contract with G-gent interface.

    This is the full "Spellbook Pattern" from spec/g-gents/integration.md:
    1. Analyze intent
    2. Generate G-gent interface tongue
    3. Synthesize F-gent contract
    4. Embed tongue in contract
    5. Return (contract, interface) pair

    Args:
        intent_text: Natural language description of the artifact
        domain: Operational domain for the interface
        constraints: Safety constraints
        operations: Verb -> description mapping
        handlers: Verb -> handler function mapping

    Returns:
        Tuple of (Contract, InterfaceTongue)

    Raises:
        ValueError: If F-gent is not available

    Example:
        >>> contract, interface = await forge_with_interface(
        ...     intent_text="Calendar agent that can only add and check events",
        ...     domain="Calendar Management",
        ...     constraints=["No deletes", "No modifications"],
        ...     handlers={"CHECK": check_calendar, "ADD": add_event}
        ... )
        >>> result = interface.invoke("CHECK 2024-12-15")
    """
    if not FGENT_AVAILABLE:
        raise ValueError(
            "F-gent is not available. Cannot create artifact with interface."
        )

    from agents.f.contract import synthesize_contract
    from agents.f.intent import parse_intent

    constraints = constraints or []
    operations = operations or {}
    handlers = handlers or {}

    # 1. Parse intent
    intent = parse_intent(intent_text)

    # 2. Generate G-gent interface tongue
    interface = await create_artifact_interface(
        domain=domain,
        constraints=constraints,
        operations=operations,
        artifact_name=intent.purpose.split()[0] + "Agent",
    )

    # 3. Bind handlers if provided
    if handlers:
        interface = bind_handlers(interface, handlers)

    # 4. Synthesize F-gent contract
    base_contract = synthesize_contract(intent, agent_name=interface.artifact_name)

    # 5. Embed tongue in contract
    contract = embed_tongue_in_contract(base_contract, interface)

    return contract, interface


# Convenience type alias
ArtifactInterface = InterfaceTongue
