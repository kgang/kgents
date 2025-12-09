"""
G-gent Catalog Integration

Integration between G-gent (Grammarian) and L-gent (Librarian).
Enables tongue registration, discovery, and compatibility checking.

Phase 4 Implementation:
- register_tongue: Register tongue with L-gent catalog
- find_tongue: Search for tongues by domain/constraints
- check_compatibility: Verify tongue compatibility
- find_composable: Find tongues that can compose
"""

from agents.g.types import Tongue, GrammarLevel
from agents.l import Registry, CatalogEntry, EntityType, CompatibilityReport


async def register_tongue(
    tongue: Tongue,
    registry: Registry,
    author: str = "G-gent",
    forged_from: str | None = None,
) -> str:
    """
    Register a tongue with L-gent catalog.

    Args:
        tongue: The tongue artifact to register
        registry: L-gent registry instance
        author: Creator identifier (defaults to "G-gent")
        forged_from: Optional intent/prompt that created the tongue

    Returns:
        Entry ID in the catalog
    """
    # Generate unique ID from tongue name and version
    entry_id = f"tongue:{tongue.name.lower().replace(' ', '_')}:{tongue.version}"

    # Create catalog entry
    entry = CatalogEntry(
        id=entry_id,
        entity_type=EntityType.TONGUE,
        name=tongue.name,
        version=tongue.version,
        description=f"Tongue for {tongue.domain}",
        keywords=[tongue.domain, tongue.level.value, tongue.format.value]
        + list(tongue.constraints),
        author=author,
        forged_from=forged_from,
        # Tongue-specific metadata
        tongue_domain=tongue.domain,
        tongue_constraints=list(tongue.constraints),
        tongue_level=tongue.level.value,
        tongue_format=tongue.format.value,
        # Type information (for lattice)
        input_type=tongue.mime_type,  # Tongues accept text
        output_type=tongue.mime_type,  # Tongues produce AST (represented as mime_type)
    )

    # Register with L-gent
    return await registry.register(entry)


async def find_tongue(
    registry: Registry,
    domain: str | None = None,
    constraints: list[str] | None = None,
    level: GrammarLevel | None = None,
    limit: int = 10,
) -> list[CatalogEntry]:
    """
    Find tongues in the catalog.

    Args:
        registry: L-gent registry instance
        domain: Filter by domain (fuzzy match on description/keywords)
        constraints: Filter by constraints (subset match)
        level: Filter by grammar level
        limit: Maximum number of results

    Returns:
        List of matching tongue entries, sorted by relevance
    """
    # Build search query
    query = domain if domain else None

    # Build keyword filters
    keywords = []
    if constraints:
        keywords.extend(constraints)
    if level:
        keywords.append(level.value)

    # Search L-gent registry
    results = await registry.find(
        query=query,
        entity_type=EntityType.TONGUE,
        keywords=keywords if keywords else None,
        limit=limit,
    )

    # Extract entries and filter by constraint subset match
    filtered_entries = []
    for result in results:
        entry = result.entry

        # If constraints specified, check if entry has all requested constraints
        if constraints:
            entry_constraints_lower = [c.lower() for c in entry.tongue_constraints]
            if all(c.lower() in entry_constraints_lower for c in constraints):
                filtered_entries.append(entry)
        else:
            filtered_entries.append(entry)

    return filtered_entries[:limit]


async def check_compatibility(
    tongue_a: Tongue,
    tongue_b: Tongue,
) -> CompatibilityReport:
    """
    Check if two tongues are compatible.

    Compatibility analysis:
    1. Domain overlap (do they serve the same domain?)
    2. Constraint conflicts (do they have conflicting constraints?)
    3. Composability (can output of A feed into B?)

    Args:
        tongue_a: First tongue
        tongue_b: Second tongue

    Returns:
        CompatibilityReport with analysis
    """
    # 1. Domain overlap analysis
    domain_overlap = 0.0
    if tongue_a.domain.lower() == tongue_b.domain.lower():
        domain_overlap = 1.0
    else:
        # Simple word overlap heuristic
        words_a = set(tongue_a.domain.lower().split())
        words_b = set(tongue_b.domain.lower().split())
        if words_a and words_b:
            domain_overlap = len(words_a & words_b) / len(words_a | words_b)

    # 2. Constraint conflict analysis
    constraint_conflicts = []
    constraints_a = set(c.lower() for c in tongue_a.constraints)
    constraints_b = set(c.lower() for c in tongue_b.constraints)

    # Check for direct contradictions (very simple heuristic)
    # Example: "no deletes" conflicts with "allows deletes"
    for ca in constraints_a:
        for cb in constraints_b:
            if "no" in ca and cb.replace("no ", "").replace("allows ", "") in ca:
                constraint_conflicts.append(f"'{ca}' conflicts with '{cb}'")
            elif "no" in cb and ca.replace("no ", "").replace("allows ", "") in cb:
                constraint_conflicts.append(f"'{ca}' conflicts with '{cb}'")

    # 3. Composability analysis
    # Tongues are composable if:
    # - They operate on different domains (sequential composition)
    # - They have compatible levels (SCHEMA can compose with COMMAND/RECURSIVE)
    composable = False
    composition_type = None

    if domain_overlap < 0.5:
        # Different domains → sequential composition possible
        composable = True
        composition_type = "sequential"
    elif tongue_a.level == tongue_b.level and domain_overlap > 0.7:
        # Same level, similar domain → parallel composition possible
        composable = True
        composition_type = "parallel"

    # Overall compatibility decision
    compatible = domain_overlap < 0.8 and len(constraint_conflicts) == 0

    # Generate reason
    if compatible:
        reason = f"Compatible tongues. Domain overlap: {domain_overlap:.2f}, no constraint conflicts."
    elif constraint_conflicts:
        reason = f"Incompatible due to constraint conflicts: {'; '.join(constraint_conflicts)}"
    elif domain_overlap > 0.8:
        reason = f"High domain overlap ({domain_overlap:.2f}) suggests redundancy, not incompatibility."
    else:
        reason = "Incompatible for unknown reasons."

    # Generate suggestions
    suggestions = []
    if composable and composition_type == "sequential":
        suggestions.append(
            f"Consider sequential composition: {tongue_a.name} >> {tongue_b.name}"
        )
    if domain_overlap > 0.5 and not constraint_conflicts:
        suggestions.append(
            "Tongues serve similar domains - consider merging or differentiating"
        )
    if constraint_conflicts:
        suggestions.append(
            "Resolve constraint conflicts through H-gent dialectic synthesis"
        )

    return CompatibilityReport(
        compatible=compatible,
        reason=reason,
        suggestions=suggestions,
        domain_overlap=domain_overlap,
        constraint_conflicts=constraint_conflicts,
        composable=composable,
        composition_type=composition_type,
    )


async def find_composable(
    tongue: Tongue,
    registry: Registry,
    composition_type: str = "sequential",
    limit: int = 5,
) -> list[CatalogEntry]:
    """
    Find tongues that can compose with the given tongue.

    Args:
        tongue: Source tongue
        registry: L-gent registry instance
        composition_type: "sequential" or "parallel"
        limit: Maximum number of results

    Returns:
        List of composable tongue entries
    """
    # Get all tongues from registry
    all_tongues = await registry.list(entity_type=EntityType.TONGUE, limit=100)

    composable_entries = []
    for entry in all_tongues:
        # Skip self
        entry_id = f"tongue:{tongue.name.lower().replace(' ', '_')}:{tongue.version}"
        if entry.id == entry_id:
            continue

        # Reconstruct minimal tongue from entry for compatibility check
        # (We only need domain, constraints, and level for the check)
        other_tongue_minimal = type(
            "Tongue",
            (),
            {
                "name": entry.name,
                "domain": entry.tongue_domain or "",
                "constraints": tuple(entry.tongue_constraints),
                "level": GrammarLevel(entry.tongue_level)
                if entry.tongue_level
                else GrammarLevel.SCHEMA,
            },
        )()

        # Check compatibility
        compat = await check_compatibility(tongue, other_tongue_minimal)

        # Filter by composition type
        if compat.composable and compat.composition_type == composition_type:
            composable_entries.append(entry)

    # Sort by usage metrics (higher usage = better tested composition)
    composable_entries.sort(key=lambda e: e.usage_count, reverse=True)

    return composable_entries[:limit]


async def update_tongue_metrics(
    tongue: Tongue,
    registry: Registry,
    success: bool = True,
    error: str | None = None,
) -> None:
    """
    Update usage metrics for a tongue in the catalog.

    Args:
        tongue: The tongue that was used
        registry: L-gent registry instance
        success: Whether the usage was successful
        error: Optional error message if failed
    """
    entry_id = f"tongue:{tongue.name.lower().replace(' ', '_')}:{tongue.version}"
    await registry.update_usage(entry_id, success=success, error=error)
