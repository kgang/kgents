"""
Code artifact schemas - Function-level crystals for code tracking.

Every function is a self-justifying crystal with:
- Identity (qualified name, file path, line range)
- Content (signature, docstring, body hash)
- Dependencies (imports, calls, called_by)
- Derivation (spec_id, derived_from)
- K-block membership
- Ghost status
- Proof (GaloisWitnessedProof)

A function crystal is a unit of derivation tracking. When we ask "why does this
function exist?", we consult its proof. When we ask "what depends on this?",
we consult its dependency graph. When we ask "is this coherent?", we compute
its Galois loss.

Philosophy:
- Every function is a crystal (self-contained unit of meaning)
- Every crystal has a proof (self-justifying existence)
- Every crystal exists in a K-block (coherence window)
- Ghost crystals mark implied/missing functions
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .proof import GaloisWitnessedProof


@dataclass(frozen=True)
class ParamInfo:
    """
    Function parameter metadata.

    Captures full signature information for a single parameter,
    including type hints, defaults, and special parameter types.
    """

    name: str
    """Parameter name."""

    type_annotation: str | None = None
    """Type annotation as string (e.g., 'int', 'list[str]', 'Agent[S, A, B]')."""

    default: str | None = None
    """Default value as string, None if no default."""

    is_variadic: bool = False
    """True if this is *args."""

    is_keyword: bool = False
    """True if this is **kwargs."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "name": self.name,
            "type_annotation": self.type_annotation,
            "default": self.default,
            "is_variadic": self.is_variadic,
            "is_keyword": self.is_keyword,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParamInfo":
        """Deserialize from dict."""
        return cls(
            name=data["name"],
            type_annotation=data.get("type_annotation"),
            default=data.get("default"),
            is_variadic=data.get("is_variadic", False),
            is_keyword=data.get("is_keyword", False),
        )


@dataclass(frozen=True)
class FunctionCrystal:
    """
    Function-level crystal for code artifact tracking (v1).

    Every function in the codebase becomes a crystal with:
    - Identity: qualified_name, file_path, line_range
    - Content: signature, docstring, body_hash
    - Dependencies: imports, calls, called_by
    - Derivation: spec_id, derived_from (parent functions)
    - Context: layer (Zero Seed level), kblock_id (coherence window)
    - Ghost: is_ghost, ghost_reason (if placeholder)
    - Proof: GaloisWitnessedProof (self-justification)

    Example qualified_name:
        "agents.d.galois.compute_crystal_loss"
        "services.witness.store.MarkStore.create_mark"

    Dependencies:
        imports: {"dataclasses.dataclass", "typing.Any"}
        calls: {"agents.d.galois.extract_terms", "math.log"}
        called_by: {"services.witness.persistence.save_with_loss"}

    Derivation:
        spec_id: "spec/protocols/witness.md#mark-creation"
        derived_from: ("services.witness.store.MarkStore.__init__",)

    The function crystal is the atomic unit of code tracking. It answers:
    - "Why does this function exist?" → proof.claim
    - "What spec justifies it?" → spec_id
    - "What does it depend on?" → imports, calls
    - "What depends on it?" → called_by
    - "Is it coherent with its context?" → proof.galois_loss
    """

    id: str
    """Unique identifier (typically qualified_name hash)."""

    qualified_name: str
    """Fully qualified name (e.g., 'agents.d.galois.compute_crystal_loss')."""

    file_path: str
    """Absolute or repo-relative file path."""

    line_range: tuple[int, int]
    """(start_line, end_line) inclusive."""

    signature: str
    """Function signature as string (e.g., 'def foo(x: int, y: str = "bar") -> bool')."""

    proof: GaloisWitnessedProof
    """Self-justifying proof for this function's existence (required for L5 crystals)."""

    docstring: str | None = None
    """Docstring if present, None otherwise."""

    body_hash: str = ""
    """Hash of function body for change detection."""

    parameters: tuple[ParamInfo, ...] = ()
    """Parameter metadata."""

    return_type: str | None = None
    """Return type annotation as string."""

    imports: frozenset[str] = frozenset()
    """Module/symbol imports used in this function."""

    calls: frozenset[str] = frozenset()
    """Qualified names of functions called by this function."""

    called_by: frozenset[str] = frozenset()
    """Qualified names of functions that call this function."""

    layer: int = 5
    """Zero Seed epistemic layer (default L5: Actions)."""

    spec_id: str | None = None
    """Reference to spec section that justifies this function."""

    derived_from: tuple[str, ...] = ()
    """Parent function(s) this was derived from (qualified names)."""

    kblock_id: str | None = None
    """K-block ID this function belongs to."""

    is_ghost: bool = False
    """True if this is a placeholder for an implied function."""

    ghost_reason: str | None = None
    """Why this ghost exists (if is_ghost=True)."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this crystal was first created."""

    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this crystal was last updated."""

    author: str = "system"
    """Who created this function (git author)."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "qualified_name": self.qualified_name,
            "file_path": self.file_path,
            "line_range": list(self.line_range),
            "signature": self.signature,
            "docstring": self.docstring,
            "body_hash": self.body_hash,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "imports": list(self.imports),
            "calls": list(self.calls),
            "called_by": list(self.called_by),
            "layer": self.layer,
            "spec_id": self.spec_id,
            "derived_from": list(self.derived_from),
            "kblock_id": self.kblock_id,
            "is_ghost": self.is_ghost,
            "ghost_reason": self.ghost_reason,
            "proof": self.proof.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FunctionCrystal":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            qualified_name=data["qualified_name"],
            file_path=data["file_path"],
            line_range=tuple(data["line_range"]),
            signature=data["signature"],
            docstring=data.get("docstring"),
            body_hash=data.get("body_hash", ""),
            parameters=tuple(ParamInfo.from_dict(p) for p in data.get("parameters", [])),
            return_type=data.get("return_type"),
            imports=frozenset(data.get("imports", [])),
            calls=frozenset(data.get("calls", [])),
            called_by=frozenset(data.get("called_by", [])),
            layer=data.get("layer", 5),
            spec_id=data.get("spec_id"),
            derived_from=tuple(data.get("derived_from", [])),
            kblock_id=data.get("kblock_id"),
            is_ghost=data.get("is_ghost", False),
            ghost_reason=data.get("ghost_reason"),
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(UTC),
            author=data.get("author", "system"),
        )


@dataclass(frozen=True)
class TestCrystal:
    """
    Test-level crystal for test tracking (v1).

    Every test becomes a crystal linked to its target function. It captures:
    - Identity: id, path, test_name
    - Target: target_id (FunctionCrystal ID being tested)
    - Type: test_type (unit, integration, property, chaos)
    - Results: last_result, last_run
    - Coverage: assertion_count
    - Derivation: spec_id (if spec-driven testing)
    - Proof: GaloisWitnessedProof (why this test exists)

    Test Types:
        "unit": Single function in isolation
        "integration": Multiple functions/modules
        "property": Property-based testing (Hypothesis)
        "chaos": Chaos engineering tests

    Results:
        "pass": Test passed on last run
        "fail": Test failed on last run
        "skip": Test was skipped

    The test crystal answers:
    - "Is this function tested?" → exists(target_id)
    - "What kind of tests cover it?" → test_type
    - "When was it last verified?" → last_run
    - "Why does this test exist?" → proof.claim
    """

    id: str
    """Unique identifier for this test."""

    path: str
    """Test file path (e.g., 'impl/claude/agents/d/_tests/test_galois.py')."""

    test_name: str
    """Test function name (e.g., 'test_compute_crystal_loss')."""

    target_id: str
    """FunctionCrystal ID of the function being tested."""

    proof: GaloisWitnessedProof
    """Self-justifying proof for why this test exists (required for L5 crystals)."""

    spec_id: str | None = None
    """Reference to spec section if spec-driven testing."""

    test_type: str = "unit"
    """Test type: 'unit', 'integration', 'property', 'chaos'."""

    last_result: str = "skip"
    """Last test result: 'pass', 'fail', 'skip'."""

    last_run: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this test was last executed."""

    assertion_count: int = 0
    """Number of assertions in this test."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this test was first created."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "path": self.path,
            "test_name": self.test_name,
            "target_id": self.target_id,
            "test_type": self.test_type,
            "last_result": self.last_result,
            "last_run": self.last_run.isoformat(),
            "assertion_count": self.assertion_count,
            "spec_id": self.spec_id,
            "proof": self.proof.to_dict(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestCrystal":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            path=data["path"],
            test_name=data["test_name"],
            target_id=data["target_id"],
            test_type=data.get("test_type", "unit"),
            last_result=data.get("last_result", "skip"),
            last_run=datetime.fromisoformat(data["last_run"])
            if "last_run" in data
            else datetime.now(UTC),
            assertion_count=data.get("assertion_count", 0),
            spec_id=data.get("spec_id"),
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(UTC),
        )

    @property
    def is_passing(self) -> bool:
        """Check if this test is currently passing."""
        return self.last_result == "pass"

    @property
    def is_failing(self) -> bool:
        """Check if this test is currently failing."""
        return self.last_result == "fail"


# Schema for Universe registration
from agents.d.universe import DataclassSchema

FUNCTION_CRYSTAL_SCHEMA = DataclassSchema(name="code.function", type_cls=FunctionCrystal)

TEST_CRYSTAL_SCHEMA = DataclassSchema(name="code.test", type_cls=TestCrystal)


__all__ = [
    "ParamInfo",
    "FunctionCrystal",
    "FUNCTION_CRYSTAL_SCHEMA",
    "TestCrystal",
    "TEST_CRYSTAL_SCHEMA",
]
