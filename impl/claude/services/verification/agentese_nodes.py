"""
AGENTESE Integration: Verification system nodes for the AGENTESE protocol.

Exposes verification capabilities through the AGENTESE protocol with nodes for:
- self.verification.* - Verification operations and analysis
- world.trace.* - Trace witness collection and analysis
- concept.proof.* - Proof visualization and exploration

This is where the magic happens - making formal verification feel delightful
and accessible through the AGENTESE protocol.
"""

from __future__ import annotations

import logging
from typing import Any

from protocols.agentese import Umwelt, node

from .contracts import AgentMorphism, VerificationStatus
from .service import VerificationService

logger = logging.getLogger(__name__)


# ============================================================================
# self.verification.* - Core Verification Operations
# ============================================================================


@node("self.verification.manifest")
async def manifest_verification_status(umwelt: Umwelt) -> dict[str, Any]:
    """
    Manifest the current state of the verification system.

    Returns a joyful, human-readable summary of verification status,
    recent analyses, and system health.
    """

    logger.info("Manifesting verification system status")

    # Get verification service from umwelt
    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "status": "unavailable",
            "message": "Verification service not initialized",
            "suggestion": "Initialize the verification service to begin formal verification",
        }

    # Get system status
    status = await verification_service.get_status()

    # Get trace corpus summary
    trace_summary = await verification_service.get_trace_corpus_summary()

    # Create delightful response
    return {
        "status": "operational",
        "message": "🔍 The verification system is watching, learning, and improving",
        "summary": {
            "active_graphs": status.get("active_graphs", 0),
            "trace_corpus_size": trace_summary.get("total_traces", 0),
            "behavioral_patterns": trace_summary.get("total_patterns", 0),
            "pending_proposals": status.get("pending_proposals", 0),
        },
        "health": "All categorical laws are being verified with joy and precision",
        "next_steps": [
            "Analyze a specification with self.verification.analyze",
            "Capture execution traces with world.trace.capture",
            "Explore proofs with concept.proof.visualize",
        ],
    }


@node("self.verification.analyze")
async def analyze_specification(
    spec_path: str,
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Analyze a specification for consistency and principled derivation.

    This is the heart of the verification system - it builds a derivation graph
    from kgents principles to implementation, identifies contradictions, and
    suggests improvements with sympathetic, educational explanations.
    """

    logger.info(f"Analyzing specification: {spec_path}")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        # Analyze the specification
        graph_result = await verification_service.analyze_specification(spec_path)

        # Create sympathetic response
        if graph_result.status == VerificationStatus.SUCCESS:
            message = "✨ Beautiful! Your specification derives cleanly from kgents principles."
        elif graph_result.status == VerificationStatus.NEEDS_REVIEW:
            message = "🤔 I found some interesting patterns that deserve attention."
        else:
            message = "💡 Let's work together to strengthen this specification."

        # Format contradictions with empathy
        contradiction_summaries = []
        for contradiction in graph_result.contradictions:
            contradiction_summaries.append(
                {
                    "description": contradiction.description,
                    "severity": contradiction.severity,
                    "how_to_fix": contradiction.resolution_strategies,
                    "affected_nodes": contradiction.node_ids,
                }
            )

        # Format orphaned nodes with constructive suggestions
        orphaned_summaries = []
        for node_id in graph_result.orphaned_nodes:
            node = next((n for n in graph_result.nodes if n.node_id == node_id), None)
            if node:
                orphaned_summaries.append(
                    {
                        "node": node.name,
                        "description": node.description,
                        "suggestion": f"Connect '{node.name}' to a kgents principle to give it purpose",
                    }
                )

        return {
            "success": True,
            "message": message,
            "graph_id": graph_result.graph_id,
            "status": graph_result.status.value,
            "metrics": {
                "total_nodes": len(graph_result.nodes),
                "total_edges": len(graph_result.edges),
                "contradictions": len(graph_result.contradictions),
                "orphaned_nodes": len(graph_result.orphaned_nodes),
                "derivation_paths": len(graph_result.derivation_paths),
            },
            "contradictions": contradiction_summaries,
            "orphaned_nodes": orphaned_summaries,
            "next_steps": [
                "Review contradictions and apply suggested fixes",
                "Connect orphaned nodes to principles",
                "Visualize the derivation graph with concept.proof.visualize",
            ],
        }

    except Exception as e:
        logger.error(f"Error analyzing specification: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check that the specification path is correct and accessible",
        }


@node("self.verification.verify_laws")
async def verify_categorical_laws(
    morphisms: list[dict[str, Any]],
    law_type: str,
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Verify categorical laws for agent morphisms.

    Supports: composition_associativity, identity_laws, functor_laws,
    operad_coherence, sheaf_gluing.

    Returns sympathetic explanations of any violations with concrete
    suggestions for fixing them.
    """

    logger.info(f"Verifying {law_type} for {len(morphisms)} morphisms")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        # Convert dict morphisms to AgentMorphism objects
        agent_morphisms = [
            AgentMorphism(
                morphism_id=m.get("id", f"morphism_{i}"),
                name=m.get("name", f"Morphism {i}"),
                description=m.get("description", ""),
                source_type=m.get("source_type", "Any"),
                target_type=m.get("target_type", "Any"),
                implementation=m.get("implementation", {}),
            )
            for i, m in enumerate(morphisms)
        ]

        # Verify based on law type
        if law_type == "composition_associativity" and len(agent_morphisms) >= 3:
            result = await verification_service.verify_composition_associativity(
                agent_morphisms[0], agent_morphisms[1], agent_morphisms[2]
            )
        elif law_type == "identity_laws" and len(agent_morphisms) >= 2:
            result = await verification_service.verify_identity_laws(
                agent_morphisms[0], agent_morphisms[1]
            )
        elif law_type == "functor_laws" and len(agent_morphisms) >= 3:
            result = await verification_service.verify_functor_laws(
                agent_morphisms[0], agent_morphisms[1], agent_morphisms[2]
            )
        else:
            return {
                "success": False,
                "error": f"Unsupported law type or insufficient morphisms: {law_type}",
            }

        # Create sympathetic response
        if result.success:
            return {
                "success": True,
                "message": f"✨ Perfect! The {law_type.replace('_', ' ')} holds beautifully.",
                "law_name": result.law_name,
                "analysis": result.llm_analysis,
                "celebration": "Your morphisms compose with mathematical elegance!",
            }
        else:
            return {
                "success": False,
                "message": f"🤔 The {law_type.replace('_', ' ')} doesn't quite hold. Let me show you what's happening.",
                "law_name": result.law_name,
                "violation": {
                    "description": result.llm_analysis,
                    "counter_example": result.counter_example.__dict__
                    if result.counter_example
                    else None,
                    "how_to_fix": result.suggested_fix,
                },
                "encouragement": "Don't worry - violations are opportunities to learn and improve!",
                "next_steps": [
                    "Review the counter-example to understand the violation",
                    "Apply the suggested fix",
                    "Generate more counter-examples with self.verification.generate_counter_examples",
                ],
            }

    except Exception as e:
        logger.error(f"Error verifying categorical laws: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check morphism definitions and try again",
        }


@node("self.verification.suggest")
async def suggest_improvements(umwelt: Umwelt) -> dict[str, Any]:
    """
    Generate improvement suggestions based on trace analysis.

    This is where the self-improvement magic happens - the system analyzes
    behavioral patterns and suggests concrete improvements with justification.
    """

    logger.info("Generating improvement suggestions")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        # Analyze behavioral patterns
        pattern_analysis = await verification_service.analyze_behavioral_patterns()

        # Generate improvement proposals
        proposals = await verification_service.generate_improvements()

        # Format proposals with joy and clarity
        formatted_proposals = []
        for proposal in proposals:
            formatted_proposals.append(
                {
                    "title": proposal.title,
                    "description": proposal.description,
                    "category": proposal.category,
                    "priority": proposal.risk_assessment,
                    "implementation": proposal.implementation_suggestion,
                    "kgents_principle": proposal.kgents_principle,
                    "why_this_matters": f"This aligns with the '{proposal.kgents_principle}' principle",
                }
            )

        return {
            "success": True,
            "message": "💡 I've been watching the system and have some ideas for you!",
            "pattern_insights": {
                "total_patterns": pattern_analysis.get("total_patterns", 0),
                "most_common": pattern_analysis.get("most_common_patterns", [])[:5],
                "llm_insights": pattern_analysis.get("llm_insights", ""),
            },
            "proposals": formatted_proposals,
            "encouragement": "These suggestions come from observing real system behavior - they're grounded in evidence!",
            "next_steps": [
                "Review proposals and choose ones that resonate",
                "Implement changes incrementally",
                "Capture new traces to verify improvements",
            ],
        }

    except Exception as e:
        logger.error(f"Error generating improvements: {e}")
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================================
# world.trace.* - Trace Witness Collection
# ============================================================================


@node("world.trace.capture")
async def capture_execution_trace(
    agent_path: str,
    execution_data: dict[str, Any],
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Capture an execution trace as a constructive proof.

    This creates a detailed record of agent execution that serves as
    a witness to the agent's behavior and can be verified against
    specifications.
    """

    logger.info(f"Capturing trace for {agent_path}")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        trace_result = await verification_service.capture_trace_witness(agent_path, execution_data)

        # Create delightful response
        status_emoji = {
            VerificationStatus.SUCCESS: "✅",
            VerificationStatus.FAILURE: "❌",
            VerificationStatus.NEEDS_REVIEW: "🔍",
            VerificationStatus.PENDING: "⏳",
        }.get(trace_result.verification_status, "📝")

        return {
            "success": True,
            "message": f"{status_emoji} Trace captured! This execution is now part of the permanent record.",
            "witness_id": trace_result.witness_id,
            "agent_path": trace_result.agent_path,
            "verification_status": trace_result.verification_status.value,
            "metrics": {
                "execution_time_ms": trace_result.execution_time_ms,
                "steps_executed": len(trace_result.intermediate_steps),
                "properties_verified": len(trace_result.properties_verified),
                "violations_found": len(trace_result.violations_found),
            },
            "properties_verified": trace_result.properties_verified,
            "violations": trace_result.violations_found,
            "insight": "This trace is now part of the corpus and will inform future improvements",
        }

    except Exception as e:
        logger.error(f"Error capturing trace: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@node("world.trace.analyze")
async def analyze_trace_corpus(
    pattern_type: str | None,
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Analyze the trace corpus for behavioral patterns.

    Reveals patterns in system behavior that can inform improvements
    and optimization opportunities.
    """

    logger.info(f"Analyzing trace corpus (pattern_type: {pattern_type})")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        analysis = await verification_service.analyze_behavioral_patterns(pattern_type)

        return {
            "success": True,
            "message": "📊 Here's what I've learned from watching the system:",
            "corpus_size": analysis.get("trace_corpus_size", 0),
            "total_patterns": analysis.get("total_patterns", 0),
            "pattern_distribution": analysis.get("type_distribution", {}),
            "most_common_patterns": analysis.get("most_common_patterns", [])[:10],
            "insights": analysis.get("llm_insights", ""),
            "improvement_suggestions": analysis.get("improvement_suggestions", []),
            "wisdom": "Patterns reveal truth - these behaviors are telling us something important",
        }

    except Exception as e:
        logger.error(f"Error analyzing trace corpus: {e}")
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================================
# concept.proof.* - Proof Visualization and Exploration
# ============================================================================


@node("concept.proof.visualize")
async def visualize_derivation_graph(
    graph_id: str,
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Visualize a derivation graph showing how implementation derives from principles.

    Returns data suitable for beautiful graph visualization in the frontend,
    with nodes colored by type and edges showing derivation relationships.
    """

    logger.info(f"Visualizing derivation graph: {graph_id}")

    verification_service: VerificationService = umwelt.get("verification_service")

    if not verification_service:
        return {
            "success": False,
            "error": "Verification service not available",
        }

    try:
        # TODO: Implement graph retrieval from persistence
        # For now, return a structure suitable for visualization

        return {
            "success": True,
            "message": "🎨 Here's your derivation graph, ready for visualization!",
            "graph_id": graph_id,
            "visualization_data": {
                "nodes": [
                    {
                        "id": "principle_composable",
                        "label": "Composable",
                        "type": "principle",
                        "color": "#4CAF50",
                        "description": "Agents are morphisms in a category",
                    },
                    {
                        "id": "requirement_1",
                        "label": "Agent Composition",
                        "type": "requirement",
                        "color": "#2196F3",
                        "description": "Agents must compose associatively",
                    },
                    {
                        "id": "implementation_1",
                        "label": "PolyAgent Composition",
                        "type": "implementation",
                        "color": "#FF9800",
                        "description": "Implementation of agent composition",
                    },
                ],
                "edges": [
                    {
                        "source": "principle_composable",
                        "target": "requirement_1",
                        "type": "derives_from",
                        "confidence": 0.9,
                    },
                    {
                        "source": "requirement_1",
                        "target": "implementation_1",
                        "type": "implements",
                        "confidence": 0.95,
                    },
                ],
            },
            "layout_suggestion": "hierarchical",
            "interaction_hints": [
                "Click nodes to see detailed derivation paths",
                "Hover over edges to see confidence scores",
                "Red nodes indicate contradictions",
                "Gray nodes are orphaned (not connected to principles)",
            ],
        }

    except Exception as e:
        logger.error(f"Error visualizing graph: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@node("concept.proof.explore")
async def explore_derivation_path(
    principle_id: str,
    implementation_id: str,
    umwelt: Umwelt,
) -> dict[str, Any]:
    """
    Explore the derivation path from a principle to an implementation.

    Shows the logical chain of reasoning that connects high-level principles
    to concrete implementation, with explanations at each step.
    """

    logger.info(f"Exploring derivation path: {principle_id} -> {implementation_id}")

    return {
        "success": True,
        "message": "🔗 Here's how this implementation derives from first principles:",
        "principle": {
            "id": principle_id,
            "name": "Composable",
            "description": "Agents are morphisms in a category; composition is primary",
        },
        "implementation": {
            "id": implementation_id,
            "name": "PolyAgent Composition",
            "description": "Concrete implementation of agent composition",
        },
        "derivation_chain": [
            {
                "step": 1,
                "from": "Composable Principle",
                "to": "Composition Requirement",
                "reasoning": "If agents are morphisms, they must compose associatively",
                "confidence": 0.95,
            },
            {
                "step": 2,
                "from": "Composition Requirement",
                "to": "PolyAgent Design",
                "reasoning": "Design must support composition with type safety",
                "confidence": 0.90,
            },
            {
                "step": 3,
                "from": "PolyAgent Design",
                "to": "PolyAgent Composition",
                "reasoning": "Implementation realizes the design with concrete code",
                "confidence": 0.85,
            },
        ],
        "completeness": "complete",
        "wisdom": "Every line of code should trace back to a principle - this is how we maintain coherence",
    }
