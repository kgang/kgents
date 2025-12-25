"""
Spec schema - L4 of the Zero Seed holarchy.

Specifications are formal contracts derived from prompts or values.
They define interfaces, behaviors, and constraints with witnessed proofs.

L4 (Spec): HAS proof field - derived artifact

AGENTESE path: concept.spec.*

Spec: spec/protocols/zero-seed.md
"""

from dataclasses import dataclass, field
from typing import Any

from .proof import GaloisWitnessedProof
from ..universe import DataclassSchema

__all__ = [
    # Contracts
    "SpecCrystal",
    # Schemas
    "SPEC_SCHEMA",
]


# =============================================================================
# L4: Spec Crystal (Formal Specifications)
# =============================================================================


@dataclass(frozen=True)
class SpecCrystal:
    """
    L4: Formal specification derived from prompts/values with witnessed proof.

    Specifications are contracts that govern implementation. They:
    - HAVE proof field (derived artifact, not axiomatic)
    - Define interfaces, behaviors, or constraints
    - Can be executable (code) or declarative (docs)
    - Trace derivation from goal prompts
    - Include dependency tracking
    - Use AST hashing for code specs

    Types of specs:
    - interface: API contracts, type signatures
    - behavior: Operational semantics, algorithms
    - constraint: Invariants, preconditions, postconditions
    - protocol: Communication patterns, event flows
    - schema: Data structures, validation rules

    Example Interface Spec:
        spec_type: "interface"
        language: "python"
        content: "def process(data: str) -> Result: ..."
        dependencies: ["spec:result-type"]
        goal_prompt_id: "prompt:data-processing"

    Example Behavior Spec:
        spec_type: "behavior"
        language: "markdown"
        content: "## Processing Flow\n1. Validate\n2. Transform\n..."
        dependencies: []
        goal_prompt_id: "prompt:system-design"

    Attributes:
        spec_type: Type of specification (interface, behavior, constraint, etc.)
        language: Language/format (python, typescript, markdown, etc.)
        content: The specification content (code, documentation, schema)
        ast_hash: SHA-256 hash of AST (for code specs, None for docs)
        dependencies: IDs of specs this depends on
        goal_prompt_id: ID of the prompt this spec was generated from
        proof: GaloisWitnessedProof of derivation
    """

    spec_type: str
    """Type of specification (interface, behavior, constraint, protocol, schema)."""

    language: str
    """Language or format (python, typescript, markdown, json, etc.)."""

    content: str
    """The specification content (code, documentation, schema definition)."""

    ast_hash: str | None
    """SHA-256 hash of parsed AST (for code specs, None for non-code)."""

    dependencies: tuple[str, ...]
    """IDs of specs this specification depends on."""

    goal_prompt_id: str
    """ID of the goal prompt this spec was derived from."""

    proof: GaloisWitnessedProof
    """Galois-witnessed proof of derivation from prompt/values."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "spec_type": self.spec_type,
            "language": self.language,
            "content": self.content,
            "ast_hash": self.ast_hash,
            "dependencies": list(self.dependencies),
            "goal_prompt_id": self.goal_prompt_id,
            "proof": self.proof.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpecCrystal":
        """Deserialize from dict."""
        return cls(
            spec_type=data["spec_type"],
            language=data["language"],
            content=data["content"],
            ast_hash=data.get("ast_hash"),
            dependencies=tuple(data["dependencies"]),
            goal_prompt_id=data["goal_prompt_id"],
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
        )


SPEC_SCHEMA = DataclassSchema(
    name="concept.spec",
    type_cls=SpecCrystal,
)
"""
Schema for concept.spec v1.

L4 derived schema. Specs HAVE proof field - they are witnessed
derivations from prompts and values.

AGENTESE path: concept.spec.*
"""
