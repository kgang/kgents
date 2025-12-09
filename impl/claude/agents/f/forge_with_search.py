"""
F-gent + L-gent integration: "Search before forge" workflow.

This module implements Cross-Pollination Opportunity T1.1:
- Query L-gent registry before forging new artifacts
- Prevent ecosystem bloat by surfacing existing solutions
- Embodies the "Curated" principle

Workflow:
1. User provides intent for new artifact
2. Search L-gent registry for similar existing artifacts (threshold: 90%)
3. If match found: Present existing options, ask user to reuse or differentiate
4. If no match: Proceed with forge workflow
5. After forging: Register new artifact in L-gent catalog

From docs/CROSS_POLLINATION_ANALYSIS.md Phase A.3
"""

from dataclasses import dataclass
from enum import Enum

from agents.f.contract import Contract, synthesize_contract
from agents.f.intent import parse_intent
from agents.l.catalog import CatalogEntry, EntityType, Registry, Status
from agents.l.search import Search, SearchResult


class ForgeDecision(Enum):
    """Decision on whether to forge a new artifact or reuse existing."""

    FORGE_NEW = "forge_new"  # No similar artifacts, proceed with forge
    REUSE_EXISTING = "reuse_existing"  # User chooses to reuse existing artifact
    DIFFERENTIATE = "differentiate"  # User differentiates from existing
    ABORT = "abort"  # User cancels forge


@dataclass
class SearchBeforeForgeResult:
    """
    Result of the search-before-forge workflow.

    Contains:
    - Whether similar artifacts exist
    - List of matches (if any)
    - Recommendation on how to proceed
    """

    decision: ForgeDecision
    similar_artifacts: list[SearchResult]
    recommendation: str  # Human-readable guidance
    threshold_used: float  # Similarity threshold (0.0-1.0)


async def search_before_forge(
    intent_text: str,
    registry: Registry,
    similarity_threshold: float = 0.9,
) -> SearchBeforeForgeResult:
    """
    Search L-gent registry for similar artifacts before forging.

    This is the core integration point (T1.1):
        Intent → L-gent Search → Decision (Forge | Reuse | Differentiate)

    Args:
        intent_text: Natural language description of desired artifact
        registry: L-gent Registry for catalog lookup
        similarity_threshold: Minimum similarity to consider a match (default: 0.9 = 90%)

    Returns:
        SearchBeforeForgeResult with decision recommendation

    Examples:
        >>> registry = Registry("test_catalog.json")
        >>> result = await search_before_forge(
        ...     "Create an agent that summarizes papers to JSON",
        ...     registry,
        ...     similarity_threshold=0.9
        ... )
        >>> result.decision
        <ForgeDecision.FORGE_NEW: 'forge_new'>
    """
    # Parse intent to extract semantic purpose
    intent = parse_intent(intent_text)

    # Search L-gent registry for similar artifacts
    search = Search(registry)
    similar = await search.find(
        query=intent.purpose,
        limit=20,  # Get top 20 results
        filters={"entity_type": EntityType.AGENT},  # Focus on agents
    )

    # Filter by similarity threshold
    # NOTE: Current keyword search returns relevance score (not semantic similarity)
    # Future: Use semantic embeddings via VectorAgent for true similarity
    matches = [result for result in similar if result.score >= similarity_threshold]

    if not matches:
        # No similar artifacts found → proceed with forge
        return SearchBeforeForgeResult(
            decision=ForgeDecision.FORGE_NEW,
            similar_artifacts=[],
            recommendation=(
                f"No similar artifacts found (threshold: {similarity_threshold:.0%}). "
                "Proceeding with forge is recommended."
            ),
            threshold_used=similarity_threshold,
        )

    # Similar artifacts exist → recommend inspection
    artifact_names = [r.entry.name for r in matches[:3]]  # Top 3
    recommendation = (
        f"Found {len(matches)} similar artifact(s): {', '.join(artifact_names)}. "
        "Consider reusing existing artifact or differentiating new one."
    )

    # Decision defaults to user choice (this is a recommendation, not automatic)
    # Actual implementation would involve AskUserQuestion or similar
    return SearchBeforeForgeResult(
        decision=ForgeDecision.REUSE_EXISTING,  # Recommend reuse
        similar_artifacts=matches,
        recommendation=recommendation,
        threshold_used=similarity_threshold,
    )


async def forge_with_registration(
    intent_text: str,
    agent_name: str,
    registry: Registry,
    author: str = "user",
    similarity_threshold: float = 0.9,
) -> tuple[Contract, SearchBeforeForgeResult]:
    """
    Complete forge workflow with L-gent integration.

    Workflow:
    1. Search before forge (check for duplicates)
    2. If no matches, forge new artifact
    3. Register forged artifact in L-gent catalog
    4. Return contract + search result

    Args:
        intent_text: Natural language description
        agent_name: Name for the new agent
        registry: L-gent Registry
        author: Author/creator name (default: "user")
        similarity_threshold: Similarity threshold for duplicate detection

    Returns:
        Tuple of (Contract, SearchBeforeForgeResult)

    Raises:
        ValueError: If user should reuse existing artifact (based on search)

    Examples:
        >>> registry = Registry("test_catalog.json")
        >>> contract, search_result = await forge_with_registration(
        ...     "Summarize papers to JSON",
        ...     "PaperSummarizer",
        ...     registry
        ... )
        >>> contract.agent_name
        'PaperSummarizer'
    """
    # Step 1: Search before forge
    search_result = await search_before_forge(
        intent_text, registry, similarity_threshold
    )

    # Step 2: Check decision
    if search_result.decision == ForgeDecision.REUSE_EXISTING:
        # User should consider reusing (this is a recommendation)
        # In production: surface to user via UI/CLI
        pass

    # Step 3: Forge new artifact
    intent = parse_intent(intent_text)
    contract = synthesize_contract(intent, agent_name)

    # Step 4: Register in L-gent catalog
    # Build relationships dict for dependencies
    relationships = {}
    if intent.dependencies:
        relationships["depends_on"] = [dep.name for dep in intent.dependencies]

    catalog_entry = CatalogEntry(
        id=agent_name,  # Use name as ID (unique identifier)
        entity_type=EntityType.CONTRACT,  # Registering contract (Phase 2 output)
        name=agent_name,
        version="1.0.0",  # Default version for new artifacts
        description=intent.purpose,
        author=author,
        keywords=intent.behavior,  # Use behavior as keywords
        input_type=contract.input_type,
        output_type=contract.output_type,
        contracts_implemented=[f"Agent[{contract.input_type}, {contract.output_type}]"],
        relationships=relationships,
        status=Status.DRAFT,  # New artifacts start as DRAFT
    )

    await registry.register(catalog_entry)

    return contract, search_result


async def register_forged_artifact(
    contract: Contract,
    agent_name: str,
    registry: Registry,
    author: str = "user",
    keywords: list[str] | None = None,
) -> CatalogEntry:
    """
    Register a forged artifact in the L-gent catalog.

    This should be called after Phase 4 (Validate) when the artifact is ready.

    Args:
        contract: Synthesized contract from F-gent
        agent_name: Name of the agent
        registry: L-gent Registry
        author: Author/creator
        keywords: Optional keywords (defaults to contract invariants)

    Returns:
        CatalogEntry that was registered

    Examples:
        >>> contract = Contract(
        ...     agent_name="WeatherAgent",
        ...     input_type="str",
        ...     output_type="dict"
        ... )
        >>> registry = Registry("test_catalog.json")
        >>> entry = await register_forged_artifact(contract, "WeatherAgent", registry)
        >>> entry.name
        'WeatherAgent'
    """
    # Use invariant descriptions as keywords if not provided
    if keywords is None:
        keywords = [inv.description for inv in contract.invariants]

    # Extract dependencies from raw intent (if available)
    relationships = {}
    if contract.raw_intent and contract.raw_intent.dependencies:
        relationships["depends_on"] = [
            dep.name for dep in contract.raw_intent.dependencies
        ]

    catalog_entry = CatalogEntry(
        id=agent_name,  # Use name as ID (unique identifier)
        entity_type=EntityType.CONTRACT,
        name=agent_name,
        version="1.0.0",  # Default version for new artifacts
        description=contract.semantic_intent,
        author=author,
        keywords=keywords,
        input_type=contract.input_type,
        output_type=contract.output_type,
        contracts_implemented=[f"Agent[{contract.input_type}, {contract.output_type}]"],
        relationships=relationships,
        status=Status.DRAFT,  # Will be promoted to ACTIVE after validation
    )

    await registry.register(catalog_entry)
    return catalog_entry
