"""
Semantic Consistency Engine: Cross-document consistency verification.

Implements semantic consistency verification across specification documents,
with concept reference analysis, conflict detection, and backward compatibility
verification for specification evolution.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any
from uuid import uuid4

from .contracts import SemanticConsistencyResult

logger = logging.getLogger(__name__)


class SemanticConsistencyEngine:
    """
    Engine for verifying semantic consistency across specification documents.

    Analyzes concept references, detects conflicts, and verifies backward
    compatibility for specification evolution.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client
        self.document_cache: dict[str, dict[str, Any]] = {}
        self.concept_registry: dict[str, dict[str, Any]] = {}
        self.cross_references: dict[str, list[str]] = {}

    # ========================================================================
    # Cross-Document Consistency
    # ========================================================================

    async def verify_cross_document_consistency(
        self,
        document_paths: list[str],
        base_concepts: dict[str, Any] | None = None,
    ) -> SemanticConsistencyResult:
        """
        Verify semantic consistency across multiple specification documents.

        Analyzes concept definitions, cross-references, and identifies conflicts
        or inconsistencies between documents.
        """

        logger.info(f"Verifying consistency across {len(document_paths)} documents")

        try:
            # 1. Parse all documents and extract concepts
            document_concepts = {}
            for doc_path in document_paths:
                concepts = await self._extract_concepts_from_document(doc_path)
                document_concepts[doc_path] = concepts

            # 2. Build unified concept registry
            unified_concepts = await self._build_unified_concept_registry(
                document_concepts, base_concepts
            )

            # 3. Detect semantic conflicts
            conflicts = await self._detect_semantic_conflicts(document_concepts, unified_concepts)

            # 4. Analyze cross-references
            cross_refs = await self._analyze_cross_references(document_concepts)

            # 5. Check backward compatibility
            backward_compatible = await self._check_backward_compatibility(
                document_concepts, base_concepts
            )

            # 6. Generate suggestions for resolving conflicts
            suggestions = await self._generate_consistency_suggestions(
                conflicts, cross_refs, document_concepts
            )

            # 7. Determine overall consistency
            is_consistent = len(conflicts) == 0

            result = SemanticConsistencyResult(
                document_ids=document_paths,
                consistent=is_consistent,
                conflicts=conflicts,
                cross_references=cross_refs,
                backward_compatible=backward_compatible,
                suggestions=suggestions,
            )

            logger.info(f"Consistency check complete: {len(conflicts)} conflicts found")

            return result

        except Exception as e:
            logger.error(f"Error verifying cross-document consistency: {e}")

            return SemanticConsistencyResult(
                document_ids=document_paths,
                consistent=False,
                conflicts=[
                    {
                        "type": "verification_error",
                        "description": f"Error during verification: {str(e)}",
                        "documents": document_paths,
                    }
                ],
                cross_references={},
                backward_compatible=False,
                suggestions=[f"Fix verification error: {str(e)}"],
            )

    async def _extract_concepts_from_document(self, doc_path: str) -> dict[str, Any]:
        """Extract concepts and definitions from a document."""

        if doc_path in self.document_cache:
            return self.document_cache[doc_path]

        try:
            # Read document content
            path = Path(doc_path)
            if not path.exists():
                logger.warning(f"Document not found: {doc_path}")
                return {}

            content = path.read_text(encoding="utf-8")

            # Extract concepts using pattern matching and LLM assistance
            concepts = await self._parse_concepts_from_content(content, doc_path)

            # Cache the results
            self.document_cache[doc_path] = concepts

            return concepts

        except Exception as e:
            logger.error(f"Error extracting concepts from {doc_path}: {e}")
            return {}

    async def _parse_concepts_from_content(
        self,
        content: str,
        doc_path: str,
    ) -> dict[str, Any]:
        """Parse concepts from document content."""

        concepts = {
            "definitions": {},
            "requirements": {},
            "constraints": {},
            "references": [],
            "glossary": {},
        }

        # Simple pattern-based extraction (in real implementation, would be more sophisticated)
        lines = content.split("\n")

        current_section = None
        for line in lines:
            line = line.strip()

            # Detect section headers
            if line.startswith("# ") or line.startswith("## "):
                current_section = line.lstrip("# ").lower()
                continue

            # Extract definitions
            if ":" in line and current_section in ["definitions", "glossary"]:
                term, definition = line.split(":", 1)
                concepts["definitions"][term.strip()] = {
                    "definition": definition.strip(),
                    "section": current_section,
                    "document": doc_path,
                }

            # Extract requirements (lines starting with "MUST", "SHALL", "SHOULD")
            requirement_keywords = ["MUST", "SHALL", "SHOULD", "MAY"]
            if any(keyword in line.upper() for keyword in requirement_keywords):
                req_id = f"req_{len(concepts['requirements']) + 1}"
                concepts["requirements"][req_id] = {
                    "statement": line,
                    "section": current_section,
                    "document": doc_path,
                }

            # Extract references to other concepts (simple pattern matching)
            if "see " in line.lower() or "refer to " in line.lower():
                concepts["references"].append(
                    {
                        "line": line,
                        "section": current_section,
                        "document": doc_path,
                    }
                )

        # Use LLM to enhance concept extraction
        if self.llm_client:
            enhanced_concepts = await self._llm_enhance_concept_extraction(
                content, concepts, doc_path
            )
            concepts.update(enhanced_concepts)

        return concepts

    async def _llm_enhance_concept_extraction(
        self,
        content: str,
        basic_concepts: dict[str, Any],
        doc_path: str,
    ) -> dict[str, Any]:
        """Use LLM to enhance concept extraction."""

        # Truncate content for LLM analysis
        content_preview = content[:2000] + "..." if len(content) > 2000 else content

        prompt = f"""
        Analyze this specification document and identify key concepts:

        Document: {doc_path}
        Content preview:
        {content_preview}

        Basic concepts found: {len(basic_concepts.get("definitions", {}))} definitions

        Identify additional:
        1. Key domain concepts and their relationships
        2. Implicit assumptions or constraints
        3. Cross-references to external concepts
        4. Potential ambiguities or unclear definitions

        Focus on concepts that might conflict with other documents.
        """

        # Simulate LLM response
        llm_response = await self._simulate_llm_call(prompt)

        # Parse LLM response into structured concepts
        enhanced = {
            "implicit_concepts": {
                "agent_composition": {
                    "definition": "Agents can be composed to form more complex agents",
                    "source": "llm_analysis",
                    "document": doc_path,
                },
                "categorical_laws": {
                    "definition": "All agent operations must satisfy categorical laws",
                    "source": "llm_analysis",
                    "document": doc_path,
                },
            },
            "assumptions": [
                "Agents are morphisms in a category",
                "Composition is associative",
                "Identity morphisms exist",
            ],
            "ambiguities": [
                "Definition of 'agent' may vary between contexts",
                "Composition semantics not fully specified",
            ],
        }

        return enhanced

    async def _build_unified_concept_registry(
        self,
        document_concepts: dict[str, dict[str, Any]],
        base_concepts: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build unified concept registry from all documents."""

        unified = {
            "definitions": {},
            "requirements": {},
            "constraints": {},
            "concept_sources": {},  # Track which documents define each concept
        }

        # Add base concepts if provided
        if base_concepts:
            for concept_name, concept_data in base_concepts.items():
                unified["definitions"][concept_name] = concept_data
                unified["concept_sources"][concept_name] = ["base_concepts"]

        # Merge concepts from all documents
        for doc_path, concepts in document_concepts.items():
            # Merge definitions
            for term, definition in concepts.get("definitions", {}).items():
                if term in unified["definitions"]:
                    # Track multiple sources for the same concept
                    if term not in unified["concept_sources"]:
                        unified["concept_sources"][term] = []
                    unified["concept_sources"][term].append(doc_path)
                else:
                    unified["definitions"][term] = definition
                    unified["concept_sources"][term] = [doc_path]

            # Merge requirements
            for req_id, requirement in concepts.get("requirements", {}).items():
                full_req_id = f"{doc_path}:{req_id}"
                unified["requirements"][full_req_id] = requirement

            # Merge implicit concepts
            for concept_name, concept_data in concepts.get("implicit_concepts", {}).items():
                if concept_name not in unified["definitions"]:
                    unified["definitions"][concept_name] = concept_data
                    unified["concept_sources"][concept_name] = [doc_path]

        return unified

    async def _detect_semantic_conflicts(
        self,
        document_concepts: dict[str, dict[str, Any]],
        unified_concepts: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect semantic conflicts between documents."""

        conflicts = []

        # 1. Detect conflicting definitions
        for concept_name, sources in unified_concepts.get("concept_sources", {}).items():
            if len(sources) > 1:
                # Multiple documents define the same concept - check for conflicts
                definitions = []
                for source in sources:
                    if source == "base_concepts":
                        continue

                    doc_concepts = document_concepts.get(source, {})
                    concept_def = doc_concepts.get("definitions", {}).get(concept_name)
                    if concept_def:
                        definitions.append(
                            {
                                "source": source,
                                "definition": concept_def.get("definition", ""),
                            }
                        )

                # Check if definitions are conflicting
                if len(definitions) > 1:
                    conflict = await self._analyze_definition_conflict(concept_name, definitions)
                    if conflict:
                        conflicts.append(conflict)

        # 2. Detect requirement conflicts
        requirement_conflicts = await self._detect_requirement_conflicts(
            unified_concepts.get("requirements", {})
        )
        conflicts.extend(requirement_conflicts)

        # 3. Detect assumption conflicts
        assumption_conflicts = await self._detect_assumption_conflicts(document_concepts)
        conflicts.extend(assumption_conflicts)

        # 4. Use LLM to detect subtle semantic conflicts
        llm_conflicts = await self._llm_detect_semantic_conflicts(
            document_concepts, unified_concepts
        )
        conflicts.extend(llm_conflicts)

        return conflicts

    async def _analyze_definition_conflict(
        self,
        concept_name: str,
        definitions: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Analyze if multiple definitions of a concept are conflicting."""

        if len(definitions) < 2:
            return None

        # Simple conflict detection - check if definitions are significantly different
        def_texts = [d["definition"].lower() for d in definitions]

        # If definitions are identical, no conflict
        if len(set(def_texts)) == 1:
            return None

        # Check for contradictory keywords
        contradictory_pairs = [
            ("synchronous", "asynchronous"),
            ("mutable", "immutable"),
            ("stateful", "stateless"),
            ("required", "optional"),
            ("must", "may"),
        ]

        for def1, def2 in zip(def_texts[:-1], def_texts[1:]):
            for pos_word, neg_word in contradictory_pairs:
                if pos_word in def1 and neg_word in def2:
                    return {
                        "type": "conflicting_definitions",
                        "concept": concept_name,
                        "description": f"Conflicting definitions for '{concept_name}': one says '{pos_word}', another says '{neg_word}'",
                        "sources": [d["source"] for d in definitions],
                        "definitions": definitions,
                    }

        # If definitions are different but not obviously contradictory
        return {
            "type": "inconsistent_definitions",
            "concept": concept_name,
            "description": f"Inconsistent definitions for '{concept_name}' across documents",
            "sources": [d["source"] for d in definitions],
            "definitions": definitions,
        }

    async def _detect_requirement_conflicts(
        self,
        requirements: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Detect conflicts between requirements."""

        conflicts = []

        # Group requirements by topic/subject
        requirement_groups = {}
        for req_id, req_data in requirements.items():
            statement = req_data.get("statement", "").lower()

            # Simple grouping by key terms
            key_terms = ["agent", "composition", "morphism", "category", "verification"]
            for term in key_terms:
                if term in statement:
                    if term not in requirement_groups:
                        requirement_groups[term] = []
                    requirement_groups[term].append((req_id, req_data))

        # Check for conflicts within each group
        for topic, reqs in requirement_groups.items():
            if len(reqs) > 1:
                conflict = await self._analyze_requirement_group_conflicts(topic, reqs)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    async def _analyze_requirement_group_conflicts(
        self,
        topic: str,
        requirements: list[tuple[str, dict[str, Any]]],
    ) -> dict[str, Any] | None:
        """Analyze conflicts within a group of related requirements."""

        statements = [req[1].get("statement", "") for req in requirements]

        # Look for contradictory modal verbs
        must_statements = [s for s in statements if "MUST" in s.upper()]
        must_not_statements = [s for s in statements if "MUST NOT" in s.upper()]

        if must_statements and must_not_statements:
            return {
                "type": "contradictory_requirements",
                "topic": topic,
                "description": f"Contradictory requirements for {topic}: some say MUST, others say MUST NOT",
                "requirements": [req[0] for req in requirements],
                "statements": statements,
            }

        return None

    async def _detect_assumption_conflicts(
        self,
        document_concepts: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Detect conflicts in implicit assumptions."""

        conflicts = []

        # Collect all assumptions
        all_assumptions = []
        for doc_path, concepts in document_concepts.items():
            assumptions = concepts.get("assumptions", [])
            for assumption in assumptions:
                all_assumptions.append(
                    {
                        "assumption": assumption,
                        "document": doc_path,
                    }
                )

        # Look for contradictory assumptions
        for i, assumption1 in enumerate(all_assumptions):
            for assumption2 in all_assumptions[i + 1 :]:
                if await self._assumptions_conflict(assumption1, assumption2):
                    conflicts.append(
                        {
                            "type": "conflicting_assumptions",
                            "description": "Conflicting assumptions between documents",
                            "assumption1": assumption1,
                            "assumption2": assumption2,
                        }
                    )

        return conflicts

    async def _assumptions_conflict(
        self,
        assumption1: dict[str, Any],
        assumption2: dict[str, Any],
    ) -> bool:
        """Check if two assumptions conflict."""

        text1 = assumption1["assumption"].lower()
        text2 = assumption2["assumption"].lower()

        # Simple conflict detection
        contradictory_pairs = [
            ("synchronous", "asynchronous"),
            ("centralized", "distributed"),
            ("stateful", "stateless"),
        ]

        for pos_word, neg_word in contradictory_pairs:
            if pos_word in text1 and neg_word in text2:
                return True
            if neg_word in text1 and pos_word in text2:
                return True

        return False

    async def _llm_detect_semantic_conflicts(
        self,
        document_concepts: dict[str, dict[str, Any]],
        unified_concepts: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Use LLM to detect subtle semantic conflicts."""

        if not self.llm_client:
            return []

        # Prepare concept summary for LLM
        concept_summary = []
        for doc_path, concepts in document_concepts.items():
            definitions = concepts.get("definitions", {})
            concept_summary.append(f"Document {doc_path}: {len(definitions)} concepts")

        prompt = f"""
        Analyze these specification documents for semantic conflicts:

        {chr(10).join(concept_summary)}

        Total unified concepts: {len(unified_concepts.get("definitions", {}))}

        Look for subtle semantic conflicts such as:
        1. Implicit contradictions in concept definitions
        2. Inconsistent use of terminology
        3. Conflicting architectural assumptions
        4. Incompatible design patterns

        Focus on conflicts that might not be obvious from keyword matching.
        """

        # Simulate LLM response
        llm_response = await self._simulate_llm_call(prompt)

        # Parse LLM response into conflicts (simplified)
        return [
            {
                "type": "llm_detected_conflict",
                "description": "LLM detected potential semantic inconsistency in concept usage",
                "analysis": llm_response,
                "confidence": "medium",
            }
        ]

    # ========================================================================
    # Cross-Reference Analysis
    # ========================================================================

    async def _analyze_cross_references(
        self,
        document_concepts: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze cross-references between documents."""

        cross_refs = {
            "explicit_references": {},
            "implicit_dependencies": {},
            "missing_references": [],
            "circular_references": [],
        }

        # Extract explicit references
        for doc_path, concepts in document_concepts.items():
            references = concepts.get("references", [])
            cross_refs["explicit_references"][doc_path] = references

        # Detect implicit dependencies (concepts used but not defined)
        for doc_path, concepts in document_concepts.items():
            implicit_deps = await self._find_implicit_dependencies(
                doc_path, concepts, document_concepts
            )
            cross_refs["implicit_dependencies"][doc_path] = implicit_deps

        # Find missing references
        missing_refs = await self._find_missing_references(document_concepts)
        cross_refs["missing_references"] = missing_refs

        # Detect circular references
        circular_refs = await self._detect_circular_references(cross_refs)
        cross_refs["circular_references"] = circular_refs

        return cross_refs

    async def _find_implicit_dependencies(
        self,
        doc_path: str,
        concepts: dict[str, Any],
        all_document_concepts: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Find concepts used in a document but defined elsewhere."""

        implicit_deps = []

        # Get all concept names defined in other documents
        external_concepts = set()
        for other_doc, other_concepts in all_document_concepts.items():
            if other_doc != doc_path:
                external_concepts.update(other_concepts.get("definitions", {}).keys())

        # Check if this document uses any external concepts
        doc_text = " ".join(
            [
                str(concepts.get("definitions", {})),
                str(concepts.get("requirements", {})),
            ]
        ).lower()

        for concept_name in external_concepts:
            if concept_name.lower() in doc_text:
                # Find which document defines this concept
                defining_doc = None
                for other_doc, other_concepts in all_document_concepts.items():
                    if concept_name in other_concepts.get("definitions", {}):
                        defining_doc = other_doc
                        break

                if defining_doc:
                    implicit_deps.append(
                        {
                            "concept": concept_name,
                            "defined_in": defining_doc,
                            "used_in": doc_path,
                        }
                    )

        return implicit_deps

    async def _find_missing_references(
        self,
        document_concepts: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Find concepts that should be cross-referenced but aren't."""

        missing_refs = []

        # This is a simplified implementation
        # In practice, would use more sophisticated analysis

        return missing_refs

    async def _detect_circular_references(
        self,
        cross_refs: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect circular reference patterns."""

        circular_refs = []

        # Build dependency graph
        dependencies = {}
        for doc_path, deps in cross_refs.get("implicit_dependencies", {}).items():
            dependencies[doc_path] = [dep["defined_in"] for dep in deps]

        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: list[str]) -> list[str] | None:
            if node in rec_stack:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]

            if node in visited:
                return None

            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, []):
                cycle = has_cycle(neighbor, path + [node])
                if cycle:
                    return cycle

            rec_stack.remove(node)
            return None

        # Check each document for cycles
        for doc_path in dependencies:
            if doc_path not in visited:
                cycle = has_cycle(doc_path, [])
                if cycle:
                    circular_refs.append(
                        {
                            "type": "circular_dependency",
                            "cycle": cycle,
                            "description": f"Circular dependency: {' -> '.join(cycle)}",
                        }
                    )

        return circular_refs

    # ========================================================================
    # Backward Compatibility
    # ========================================================================

    async def _check_backward_compatibility(
        self,
        document_concepts: dict[str, dict[str, Any]],
        base_concepts: dict[str, Any] | None,
    ) -> bool:
        """Check if current documents are backward compatible with base concepts."""

        if not base_concepts:
            return True  # No base to compare against

        # Check if any base concepts have been removed or changed incompatibly
        for concept_name, base_definition in base_concepts.items():
            # Check if concept still exists
            concept_found = False
            for doc_path, concepts in document_concepts.items():
                if concept_name in concepts.get("definitions", {}):
                    concept_found = True

                    # Check if definition is compatible
                    current_def = concepts["definitions"][concept_name]
                    if not await self._definitions_compatible(base_definition, current_def):
                        return False

            if not concept_found:
                # Concept was removed - not backward compatible
                return False

        return True

    async def _definitions_compatible(
        self,
        base_definition: dict[str, Any],
        current_definition: dict[str, Any],
    ) -> bool:
        """Check if current definition is compatible with base definition."""

        # Simple compatibility check
        base_text = str(base_definition.get("definition", "")).lower()
        current_text = str(current_definition.get("definition", "")).lower()

        # If definitions are identical, they're compatible
        if base_text == current_text:
            return True

        # Check for breaking changes
        breaking_changes = [
            ("required", "optional"),  # Making something optional is usually safe
            ("must", "may"),  # Relaxing requirements is usually safe
        ]

        for old_word, new_word in breaking_changes:
            if old_word in base_text and new_word in current_text:
                # This might be a breaking change
                return False

        # If no obvious breaking changes, assume compatible
        return True

    # ========================================================================
    # Suggestion Generation
    # ========================================================================

    async def _generate_consistency_suggestions(
        self,
        conflicts: list[dict[str, Any]],
        cross_refs: dict[str, Any],
        document_concepts: dict[str, dict[str, Any]],
    ) -> list[str]:
        """Generate suggestions for resolving consistency issues."""

        suggestions = []

        # Suggestions for conflicts
        for conflict in conflicts:
            conflict_type = conflict.get("type", "unknown")

            if conflict_type == "conflicting_definitions":
                concept = conflict.get("concept", "unknown")
                suggestions.append(
                    f"Resolve conflicting definitions for '{concept}' by choosing one canonical definition"
                )

            elif conflict_type == "contradictory_requirements":
                topic = conflict.get("topic", "unknown")
                suggestions.append(
                    f"Resolve contradictory requirements for {topic} by clarifying scope and conditions"
                )

            elif conflict_type == "conflicting_assumptions":
                suggestions.append(
                    "Document and reconcile conflicting assumptions between specifications"
                )

        # Suggestions for cross-references
        missing_refs = cross_refs.get("missing_references", [])
        if missing_refs:
            suggestions.append(
                f"Add explicit cross-references for {len(missing_refs)} missing concept references"
            )

        circular_refs = cross_refs.get("circular_references", [])
        if circular_refs:
            suggestions.append(
                "Break circular dependencies by introducing intermediate abstractions"
            )

        # General suggestions
        if len(conflicts) > 3:
            suggestions.append(
                "Consider creating a unified glossary to standardize concept definitions"
            )

        if not suggestions:
            suggestions.append("Documents appear semantically consistent")

        return suggestions

    async def _simulate_llm_call(self, prompt: str) -> str:
        """Simulate LLM call for development purposes."""

        await asyncio.sleep(0.1)  # Simulate network delay

        if "conflict" in prompt.lower():
            return "Analysis shows potential inconsistencies in concept usage and terminology that should be reviewed for clarity."

        if "concept" in prompt.lower():
            return "Key concepts identified include agent composition, categorical laws, and verification properties."

        return "Analysis completed successfully."
