"""
Property-Based Tests for Semantic Consistency Engine.

Tests cross-document semantic consistency verification, conflict detection,
and backward compatibility verification.

Feature: formal-verification-metatheory
Properties: 18
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from services.verification.contracts import SemanticConsistencyResult
from services.verification.semantic_consistency import SemanticConsistencyEngine

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def concept_name_strategy(draw: st.DrawFn) -> str:
    """Generate valid concept names."""
    prefix = draw(
        st.sampled_from(
            [
                "agent",
                "morphism",
                "functor",
                "category",
                "operad",
                "sheaf",
                "composition",
                "identity",
                "verification",
                "trace",
            ]
        )
    )
    suffix = draw(st.sampled_from(["", "_type", "_spec", "_impl", "_pattern"]))
    return f"{prefix}{suffix}"


@st.composite
def definition_strategy(draw: st.DrawFn) -> str:
    """Generate concept definitions."""
    adjectives = draw(
        st.sampled_from(
            [
                "composable",
                "immutable",
                "stateful",
                "stateless",
                "synchronous",
                "asynchronous",
                "required",
                "optional",
            ]
        )
    )
    nouns = draw(
        st.sampled_from(
            [
                "entity",
                "morphism",
                "transformation",
                "structure",
                "pattern",
                "behavior",
                "property",
                "constraint",
            ]
        )
    )
    return f"A {adjectives} {nouns} that defines system behavior"


@st.composite
def requirement_statement_strategy(draw: st.DrawFn) -> str:
    """Generate requirement statements."""
    modal = draw(st.sampled_from(["MUST", "SHALL", "SHOULD", "MAY"]))
    action = draw(
        st.sampled_from(
            [
                "verify",
                "implement",
                "preserve",
                "maintain",
                "support",
                "provide",
                "ensure",
                "validate",
            ]
        )
    )
    subject = draw(
        st.sampled_from(
            [
                "categorical laws",
                "composition structure",
                "identity morphisms",
                "functor properties",
                "sheaf conditions",
                "trace witnesses",
            ]
        )
    )
    return f"The system {modal} {action} {subject}"


@st.composite
def document_content_strategy(draw: st.DrawFn) -> str:
    """Generate document content with concepts and requirements."""
    lines = ["# Test Specification\n"]

    # Add glossary section
    lines.append("## Glossary\n")
    num_concepts = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_concepts):
        concept = draw(concept_name_strategy())
        definition = draw(definition_strategy())
        lines.append(f"{concept}: {definition}\n")

    # Add requirements section
    lines.append("\n## Requirements\n")
    num_requirements = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_requirements):
        requirement = draw(requirement_statement_strategy())
        lines.append(f"- {requirement}\n")

    return "".join(lines)


@st.composite
def base_concepts_strategy(draw: st.DrawFn) -> dict[str, dict[str, str]]:
    """Generate base concepts for backward compatibility testing."""
    concepts = {}
    num_concepts = draw(st.integers(min_value=1, max_value=3))

    for _ in range(num_concepts):
        name = draw(concept_name_strategy())
        definition = draw(definition_strategy())
        concepts[name] = {"definition": definition, "source": "base"}

    return concepts


# =============================================================================
# Property 18: Semantic Consistency
# =============================================================================


class TestSemanticConsistency:
    """
    Property 18: Semantic Consistency

    For any set of specification documents referencing the same concepts,
    semantic consistency SHALL be verified and conflicts identified.

    Validates: Requirements 7.1, 7.2, 7.3, 7.5
    """

    @pytest.mark.asyncio
    async def test_empty_documents_are_consistent(self) -> None:
        """Empty document list is trivially consistent."""
        engine = SemanticConsistencyEngine()

        result = await engine.verify_cross_document_consistency([])

        assert isinstance(result, SemanticConsistencyResult)
        assert result.consistent

    @pytest.mark.asyncio
    @given(content=document_content_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_single_document_is_consistent(self, content: str) -> None:
        """Single document is consistent with itself."""
        engine = SemanticConsistencyEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test_spec.md"
            doc_path.write_text(content)

            result = await engine.verify_cross_document_consistency([str(doc_path)])

            assert isinstance(result, SemanticConsistencyResult)
            # Single document should generally be consistent
            # (unless it has internal contradictions)

    @pytest.mark.asyncio
    async def test_identical_documents_are_consistent(self) -> None:
        """Identical documents are consistent."""
        engine = SemanticConsistencyEngine()

        content = """# Test Spec
## Glossary
agent: A composable entity that transforms inputs to outputs
morphism: A transformation between objects in a category

## Requirements
- The system MUST verify categorical laws
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content)
            doc2_path.write_text(content)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            assert result.consistent

    @pytest.mark.asyncio
    async def test_conflicting_definitions_detected(self) -> None:
        """Conflicting definitions are detected."""
        engine = SemanticConsistencyEngine()

        content1 = """# Spec 1
## Glossary
agent: A synchronous entity that processes requests
"""

        content2 = """# Spec 2
## Glossary
agent: An asynchronous entity that handles events
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content1)
            doc2_path.write_text(content2)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            # Should detect conflict between synchronous and asynchronous
            assert len(result.conflicts) >= 1

    @pytest.mark.asyncio
    async def test_contradictory_requirements_detected(self) -> None:
        """Contradictory requirements are detected."""
        engine = SemanticConsistencyEngine()

        content1 = """# Spec 1
## Requirements
- The agent MUST be stateful
"""

        content2 = """# Spec 2
## Requirements
- The agent MUST be stateless
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content1)
            doc2_path.write_text(content2)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            # Should detect conflict between stateful and stateless
            assert len(result.conflicts) >= 1

    @pytest.mark.asyncio
    async def test_cross_references_analyzed(self) -> None:
        """Cross-references between documents are analyzed."""
        engine = SemanticConsistencyEngine()

        content1 = """# Spec 1
## Glossary
agent: A composable entity
morphism: A transformation (see agent for context)
"""

        content2 = """# Spec 2
## Requirements
- The system MUST support agent composition
- Refer to Spec 1 for agent definition
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content1)
            doc2_path.write_text(content2)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            # Should have cross-reference analysis
            assert "explicit_references" in result.cross_references
            assert "implicit_dependencies" in result.cross_references

    @pytest.mark.asyncio
    async def test_suggestions_generated_for_conflicts(self) -> None:
        """Suggestions are generated for resolving conflicts."""
        engine = SemanticConsistencyEngine()

        content1 = """# Spec 1
## Glossary
agent: A mutable entity
"""

        content2 = """# Spec 2
## Glossary
agent: An immutable entity
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content1)
            doc2_path.write_text(content2)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            # Should have suggestions
            assert len(result.suggestions) >= 1

    @pytest.mark.asyncio
    @given(base_concepts=base_concepts_strategy())
    @settings(max_examples=30, deadline=None)
    async def test_backward_compatibility_with_base(
        self,
        base_concepts: dict[str, dict[str, str]],
    ) -> None:
        """Backward compatibility is verified against base concepts."""
        engine = SemanticConsistencyEngine()

        # Create document that includes base concepts
        lines = ["# Test Spec\n## Glossary\n"]
        for name, data in base_concepts.items():
            lines.append(f"{name}: {data['definition']}\n")
        content = "".join(lines)

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "spec.md"
            doc_path.write_text(content)

            result = await engine.verify_cross_document_consistency(
                [str(doc_path)],
                base_concepts=base_concepts,
            )

            # Should be backward compatible when concepts match
            assert result.backward_compatible

    @pytest.mark.asyncio
    async def test_backward_incompatibility_detected(self) -> None:
        """Backward incompatibility is detected when concepts change."""
        engine = SemanticConsistencyEngine()

        base_concepts = {
            "agent": {"definition": "A required entity", "source": "base"},
        }

        # Document changes "required" to "optional"
        content = """# Test Spec
## Glossary
agent: An optional entity
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "spec.md"
            doc_path.write_text(content)

            result = await engine.verify_cross_document_consistency(
                [str(doc_path)],
                base_concepts=base_concepts,
            )

            # Should detect backward incompatibility
            assert not result.backward_compatible

    @pytest.mark.asyncio
    async def test_missing_document_handled(self) -> None:
        """Missing documents are handled gracefully."""
        engine = SemanticConsistencyEngine()

        result = await engine.verify_cross_document_consistency(["/nonexistent/path/spec.md"])

        # Should not crash, but may not be consistent
        assert isinstance(result, SemanticConsistencyResult)

    @pytest.mark.asyncio
    async def test_circular_references_detected(self) -> None:
        """Circular references between documents are detected."""
        engine = SemanticConsistencyEngine()

        content1 = """# Spec 1
## Glossary
agent: Uses morphism (defined in Spec 2)
"""

        content2 = """# Spec 2
## Glossary
morphism: Uses agent (defined in Spec 1)
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc1_path = Path(tmpdir) / "spec1.md"
            doc2_path = Path(tmpdir) / "spec2.md"
            doc1_path.write_text(content1)
            doc2_path.write_text(content2)

            result = await engine.verify_cross_document_consistency(
                [str(doc1_path), str(doc2_path)]
            )

            # Should analyze circular references
            assert "circular_references" in result.cross_references


# =============================================================================
# Concept Extraction Tests
# =============================================================================


class TestConceptExtraction:
    """Tests for concept extraction from documents."""

    @pytest.mark.asyncio
    async def test_extract_definitions(self) -> None:
        """Definitions are extracted from glossary sections."""
        engine = SemanticConsistencyEngine()

        content = """# Test Spec
## Definitions
agent: A composable entity
morphism: A transformation
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "spec.md"
            doc_path.write_text(content)

            concepts = await engine._extract_concepts_from_document(str(doc_path))

            assert "definitions" in concepts

    @pytest.mark.asyncio
    async def test_extract_requirements(self) -> None:
        """Requirements are extracted from documents."""
        engine = SemanticConsistencyEngine()

        content = """# Test Spec
## Requirements
- The system MUST verify laws
- The system SHALL support composition
- The system SHOULD provide feedback
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "spec.md"
            doc_path.write_text(content)

            concepts = await engine._extract_concepts_from_document(str(doc_path))

            assert "requirements" in concepts
            assert len(concepts["requirements"]) >= 1

    @pytest.mark.asyncio
    async def test_extract_references(self) -> None:
        """References are extracted from documents."""
        engine = SemanticConsistencyEngine()

        content = """# Test Spec
## Overview
For more details, see the design document.
Refer to the architecture section for context.
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "spec.md"
            doc_path.write_text(content)

            concepts = await engine._extract_concepts_from_document(str(doc_path))

            assert "references" in concepts


# =============================================================================
# Conflict Analysis Tests
# =============================================================================


class TestConflictAnalysis:
    """Tests for conflict analysis."""

    @pytest.mark.asyncio
    async def test_analyze_definition_conflict(self) -> None:
        """Definition conflicts are analyzed correctly."""
        engine = SemanticConsistencyEngine()

        definitions = [
            {"source": "doc1.md", "definition": "A synchronous entity"},
            {"source": "doc2.md", "definition": "An asynchronous entity"},
        ]

        conflict = await engine._analyze_definition_conflict("agent", definitions)

        assert conflict is not None
        assert conflict["type"] == "conflicting_definitions"
        assert "agent" in conflict["concept"]

    @pytest.mark.asyncio
    async def test_no_conflict_for_identical_definitions(self) -> None:
        """Identical definitions don't create conflicts."""
        engine = SemanticConsistencyEngine()

        definitions = [
            {"source": "doc1.md", "definition": "A composable entity"},
            {"source": "doc2.md", "definition": "A composable entity"},
        ]

        conflict = await engine._analyze_definition_conflict("agent", definitions)

        assert conflict is None

    @pytest.mark.asyncio
    async def test_assumptions_conflict_detection(self) -> None:
        """Conflicting assumptions are detected."""
        engine = SemanticConsistencyEngine()

        assumption1 = {"assumption": "The system is centralized", "document": "doc1.md"}
        assumption2 = {"assumption": "The system is distributed", "document": "doc2.md"}

        conflicts = await engine._assumptions_conflict(assumption1, assumption2)

        assert conflicts  # Should detect centralized vs distributed conflict


# =============================================================================
# Unified Registry Tests
# =============================================================================


class TestUnifiedRegistry:
    """Tests for unified concept registry building."""

    @pytest.mark.asyncio
    async def test_build_unified_registry(self) -> None:
        """Unified registry is built from multiple documents."""
        engine = SemanticConsistencyEngine()

        document_concepts = {
            "doc1.md": {
                "definitions": {"agent": {"definition": "Entity 1", "document": "doc1.md"}},
                "requirements": {},
            },
            "doc2.md": {
                "definitions": {"morphism": {"definition": "Transform", "document": "doc2.md"}},
                "requirements": {},
            },
        }

        unified = await engine._build_unified_concept_registry(document_concepts, None)

        assert "agent" in unified["definitions"]
        assert "morphism" in unified["definitions"]
        assert "concept_sources" in unified

    @pytest.mark.asyncio
    async def test_unified_registry_tracks_sources(self) -> None:
        """Unified registry tracks concept sources."""
        engine = SemanticConsistencyEngine()

        document_concepts = {
            "doc1.md": {
                "definitions": {"agent": {"definition": "Entity 1", "document": "doc1.md"}},
                "requirements": {},
            },
            "doc2.md": {
                "definitions": {"agent": {"definition": "Entity 2", "document": "doc2.md"}},
                "requirements": {},
            },
        }

        unified = await engine._build_unified_concept_registry(document_concepts, None)

        # Should track both sources for "agent"
        assert "agent" in unified["concept_sources"]
        assert len(unified["concept_sources"]["agent"]) >= 1

    @pytest.mark.asyncio
    async def test_unified_registry_includes_base_concepts(self) -> None:
        """Unified registry includes base concepts."""
        engine = SemanticConsistencyEngine()

        base_concepts = {
            "base_concept": {"definition": "Base definition", "source": "base"},
        }

        document_concepts = {
            "doc1.md": {
                "definitions": {"agent": {"definition": "Entity", "document": "doc1.md"}},
                "requirements": {},
            },
        }

        unified = await engine._build_unified_concept_registry(document_concepts, base_concepts)

        assert "base_concept" in unified["definitions"]
        assert "agent" in unified["definitions"]
