"""
Zero Seed LLM Types: Data structures for Galois operations.

These types model the mathematical structures from Galois modularization:
- Module: Atomic semantic unit (axiom, theorem, lemma, definition)
- ModularContent: DAG of modules with dependency edges
- Context: Domain context for restructuring
- Style: Output style for reconstitution

See: spec/protocols/zero-seed1/llm.md Appendix A
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class LossAxis(Enum):
    """Axis along which to measure Galois loss.

    Different axes capture different semantic notions:
    - SEMANTIC: Raw information preservation
    - LOGICAL: Proof validity preservation
    - STYLISTIC: Tone/voice preservation
    - STRUCTURAL: Modular decomposition preservation
    """

    SEMANTIC = "semantic"
    LOGICAL = "logical"
    STYLISTIC = "stylistic"
    STRUCTURAL = "structural"


class Style(Enum):
    """Output style for reconstitution.

    The same modular content can be reconstituted in different styles:
    - FORMAL: Rigorous mathematical prose
    - CONCISE: Minimal, compressed prose
    - INTUITIVE: Explanatory, pedagogical
    - PROOF: Derivation format with steps
    - THEOREM: Statement format
    """

    FORMAL = "formal"
    CONCISE = "concise"
    INTUITIVE = "intuitive"
    PROOF = "proof"
    THEOREM = "theorem"

    @property
    def description(self) -> str:
        """Human-readable description for prompts."""
        descriptions = {
            Style.FORMAL: "Rigorous, formal mathematical prose with precise definitions",
            Style.CONCISE: "Minimal prose, compressed for brevity",
            Style.INTUITIVE: "Explanatory prose with examples and intuitions",
            Style.PROOF: "Step-by-step derivation with explicit justifications",
            Style.THEOREM: "Clear theorem statement format",
        }
        return descriptions.get(self, "Standard prose")


# -----------------------------------------------------------------------------
# Core Data Classes
# -----------------------------------------------------------------------------


@dataclass
class Module:
    """Atomic semantic unit in modular content.

    A module is the minimal unit of meaning that can be:
    - Referenced by other modules (via id)
    - Verified for internal consistency
    - Reconstituted independently

    Types:
        axiom: Foundational assumption (no deps)
        definition: Named concept
        lemma: Intermediate result
        theorem: Main result
    """

    id: str
    type: str  # axiom | theorem | lemma | definition
    content: str
    deps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "deps": self.deps,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Module:
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            content=data.get("content", ""),
            deps=data.get("deps", []),
        )

    def __eq__(self, other: object) -> bool:
        """Content-based equality (ignores id)."""
        if not isinstance(other, Module):
            return False
        return (
            self.type == other.type
            and self.content == other.content
            and set(self.deps) == set(other.deps)
        )


@dataclass
class ModularContent:
    """DAG of modules with dependency edges.

    Represents the result of restructuring prose into atomic modules.
    The dependency graph must be acyclic for valid modular content.

    Invariants:
        - edges reference valid module ids
        - no circular dependencies
        - all deps listed in module.deps appear in edges
    """

    modules: list[Module] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)  # (from_id, to_id)
    compression_ratio: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "modules": [m.to_dict() for m in self.modules],
            "edges": self.edges,
            "compression_ratio": self.compression_ratio,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModularContent:
        """Deserialize from dictionary."""
        modules_data = data.get("modules", [])
        modules = [Module.from_dict(m) for m in modules_data]

        # Convert edges from list of lists to list of tuples
        edges_data = data.get("edges", [])
        edges = [(e[0], e[1]) for e in edges_data if len(e) >= 2]

        return cls(
            modules=modules,
            edges=edges,
            compression_ratio=data.get("compression_ratio", 1.0),
        )

    def is_dag(self) -> bool:
        """Check if the dependency graph is acyclic."""
        if not self.modules:
            return True

        # Build adjacency list
        graph: dict[str, list[str]] = {m.id: [] for m in self.modules}
        for from_id, to_id in self.edges:
            if from_id in graph:
                graph[from_id].append(to_id)

        # Topological sort via DFS
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for module in self.modules:
            if module.id not in visited:
                if has_cycle(module.id):
                    return False

        return True

    def is_isomorphic_to(self, other: ModularContent) -> bool:
        """Check if two modular contents are structurally equivalent.

        Ignores module ids, compares content-based equality.
        """
        if len(self.modules) != len(other.modules):
            return False

        # Compare modules by content (ignoring ids)
        self_contents = sorted([m.content for m in self.modules])
        other_contents = sorted([m.content for m in other.modules])

        return self_contents == other_contents

    def render_for_llm(self) -> str:
        """Render modules in human-readable format for prompts."""
        lines = []
        for module in self.modules:
            deps_str = ", ".join(module.deps) if module.deps else "none"
            lines.append(f"[{module.id}] ({module.type}, deps: {deps_str})")
            lines.append(f"  {module.content}")
            lines.append("")
        return "\n".join(lines)


@dataclass
class Context:
    """Domain context for restructuring.

    Provides background information to guide modularization:
    - Known axioms that don't need re-extraction
    - Existing modules to avoid duplication
    - Domain hints for terminology
    """

    axioms: list[Axiom] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)
    domain: str = ""

    @classmethod
    def empty(cls) -> Context:
        """Create empty context."""
        return cls()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Context:
        """Create from dictionary."""
        axioms = [Axiom.from_dict(a) for a in data.get("axioms", [])]
        modules = [Module.from_dict(m) for m in data.get("modules", [])]
        return cls(
            axioms=axioms,
            modules=modules,
            domain=data.get("domain", ""),
        )

    def render(self) -> str:
        """Render context for inclusion in prompts."""
        parts = []

        if self.domain:
            parts.append(f"Domain: {self.domain}")

        if self.axioms:
            parts.append("Known Axioms:")
            for axiom in self.axioms:
                parts.append(f"  - [{axiom.id}] {axiom.content}")

        if self.modules:
            parts.append("Existing Modules:")
            for module in self.modules:
                parts.append(f"  - [{module.id}] {module.content[:100]}...")

        return "\n".join(parts) if parts else "No context provided."


# -----------------------------------------------------------------------------
# Derived Types
# -----------------------------------------------------------------------------


@dataclass
class Axiom:
    """A fixed-point module: R(C(axiom)) = axiom.

    Axioms are modules that are semantically atomic - they cannot be
    further decomposed without information loss.
    """

    id: str
    content: str
    stability_score: float = 1.0  # How stable under R/C round-trip

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "stability_score": self.stability_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Axiom:
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            stability_score=data.get("stability_score", 1.0),
        )


@dataclass
class Proof:
    """A derivation from axioms to conclusion.

    Contains the logical steps that establish a theorem.
    Can be rendered as prose for LLM processing.
    """

    conclusion: str
    steps: list[str] = field(default_factory=list)
    axioms: list[Axiom] = field(default_factory=list)

    def render_as_prose(self) -> str:
        """Render proof as natural language prose."""
        lines = ["We prove: " + self.conclusion, "", "Proof:"]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"  Step {i}: {step}")

        if self.axioms:
            lines.append("")
            lines.append("Using axioms:")
            for axiom in self.axioms:
                lines.append(f"  - {axiom.content}")

        lines.append("")
        lines.append("QED.")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str) -> Proof:
        """Parse proof from markdown format."""
        lines = markdown.strip().split("\n")
        conclusion = ""
        steps: list[str] = []
        axioms: list[Axiom] = []

        in_steps = False
        in_axioms = False

        for line in lines:
            line = line.strip()
            if line.startswith("We prove:") or line.startswith("Theorem:"):
                conclusion = line.split(":", 1)[1].strip()
            elif "Proof:" in line:
                in_steps = True
                in_axioms = False
            elif "Using axioms:" in line or "Axioms:" in line:
                in_axioms = True
                in_steps = False
            elif line.startswith("Step") or (in_steps and line.startswith("-")):
                step = line.split(":", 1)[-1].strip() if ":" in line else line.lstrip("- ")
                if step:
                    steps.append(step)
            elif in_axioms and line.startswith("-"):
                axiom_content = line.lstrip("- ").strip()
                if axiom_content:
                    axioms.append(Axiom(id=f"axiom_{len(axioms)}", content=axiom_content))

        return cls(conclusion=conclusion, steps=steps, axioms=axioms)


@dataclass
class Theorem:
    """A generated theorem with coherence metrics."""

    statement: str
    derived_from: list[str] = field(default_factory=list)  # Module ids
    loss_score: float = 0.0  # Galois loss
    coherence_score: float = 1.0  # 1 - combined_loss

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "derived_from": self.derived_from,
            "loss_score": self.loss_score,
            "coherence_score": self.coherence_score,
        }


@dataclass
class Contradiction:
    """A detected contradiction between statement and axiom."""

    statement: str
    conflicts_with: Axiom
    loss_excess: float  # How much loss exceeds additive (super-additivity)

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "conflicts_with": self.conflicts_with.to_dict(),
            "loss_excess": self.loss_excess,
        }


@dataclass
class ValidationResult:
    """Result of proof validation."""

    valid: bool
    loss: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "loss": self.loss,
            "error": self.error,
        }


@dataclass
class Alternative:
    """An alternative phrasing with loss score."""

    text: str
    style: Style
    loss: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "style": self.style.value,
            "loss": self.loss,
        }


__all__ = [
    # Enums
    "LossAxis",
    "Style",
    # Core types
    "Module",
    "ModularContent",
    "Context",
    # Derived types
    "Axiom",
    "Proof",
    "Theorem",
    "Contradiction",
    "ValidationResult",
    "Alternative",
]
