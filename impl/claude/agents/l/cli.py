"""
LibraryCLI - CLI interface for L-gent (Library/Catalog).

The Synaptic Librarian for knowledge curation, semantic discovery,
and ecosystem connectivity.

Commands:
- catalog: List catalog entries
- discover: Search catalog semantically
- register: Register new artifact
- show: Show entry details
- lineage: Show artifact lineage
- compose: Verify composition compatibility
- types: List registered types
- stats: Show catalog statistics

See: spec/protocols/prism.md
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class LibraryCLI(CLICapable):
    """
    CLI interface for L-gent (Library/Catalog).

    The Synaptic Librarian navigates knowledge through curation,
    semantic discovery, and ecosystem connectivity.
    """

    @property
    def genus_name(self) -> str:
        return "library"

    @property
    def cli_description(self) -> str:
        return "L-gent Library/Catalog operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "catalog": self.catalog,
            "discover": self.discover,
            "register": self.register,
            "show": self.show,
            "lineage": self.lineage,
            "compose": self.compose,
            "types": self.types,
            "stats": self.stats,
        }

    @expose(
        help="List catalog entries",
        examples=[
            "kgents library catalog",
            "kgents library catalog --type=agent",
        ],
        aliases=["ls"],
    )
    async def catalog(
        self,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        List all catalog entries.

        Filter by entity type: agent, tongue, tool, hypothesis, artifact, script, document
        """
        from agents.l import EntityType, Registry

        registry = Registry()

        # Map string to EntityType
        type_filter = None
        if type:
            type_map = {
                "agent": EntityType.AGENT,
                "tongue": EntityType.TONGUE,
                "tool": EntityType.TOOL,
                "hypothesis": EntityType.HYPOTHESIS,
                "artifact": EntityType.ARTIFACT,
                "script": EntityType.SCRIPT,
                "document": EntityType.DOCUMENT,
            }
            type_filter = type_map.get(type.lower())

        entries = await registry.find(entity_type=type_filter)

        return {
            "entries": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.entity_type.value if e.entity_type else "unknown",
                    "status": e.status.value if e.status else "unknown",
                    "description": e.description,
                }
                for e in entries
            ],
            "count": len(entries),
        }

    @expose(
        help="Search catalog semantically",
        examples=[
            'kgents library discover "calendar operations"',
            'kgents library discover "parse JSON" --semantic',
        ],
    )
    async def discover(
        self,
        query: str,
        semantic: bool = False,
        keyword: bool = False,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Search catalog using keyword or semantic search.

        Default is hybrid search combining both approaches.
        """
        from agents.l import create_semantic_registry

        registry = await create_semantic_registry()

        if semantic:
            results = await registry.find_semantic(query, limit=limit)
        elif keyword:
            results = await registry.find(query=query, limit=limit)
        else:
            # Hybrid search
            results = await registry.find_hybrid(query, limit=limit)

        return {
            "query": query,
            "results": [
                {
                    "id": r.entry.id if hasattr(r, "entry") else r.id,
                    "name": r.entry.name if hasattr(r, "entry") else r.name,
                    "type": r.entry.entity_type.value
                    if hasattr(r, "entry") and r.entry.entity_type
                    else "unknown",
                    "score": r.score if hasattr(r, "score") else 1.0,
                    "description": r.entry.description
                    if hasattr(r, "entry")
                    else getattr(r, "description", None),
                }
                for r in results
            ],
            "count": len(results),
        }

    @expose(
        help="Register new artifact",
        examples=[
            "kgents library register ./my_agent.py --type=agent",
            "kgents library register ./grammar.tongue --type=tongue",
        ],
    )
    async def register(
        self,
        path: str,
        type: str = "agent",
        name: str | None = None,
    ) -> dict[str, Any]:
        """
        Register new artifact in catalog.

        Types: agent, tongue, tool, hypothesis, artifact, script, document
        """
        import uuid

        from agents.l import CatalogEntry, EntityType, Registry, Status

        type_map = {
            "agent": EntityType.AGENT,
            "tongue": EntityType.TONGUE,
            "tool": EntityType.TOOL,
            "hypothesis": EntityType.HYPOTHESIS,
            "artifact": EntityType.ARTIFACT,
            "script": EntityType.SCRIPT,
            "document": EntityType.DOCUMENT,
        }

        # Infer name from path if not provided
        artifact_name = name or Path(path).stem

        entry = CatalogEntry(
            id=str(uuid.uuid4())[:8],
            name=artifact_name,
            entity_type=type_map.get(type.lower(), EntityType.ARTIFACT),
            status=Status.ACTIVE,
            description=f"Registered from {path}",
        )

        registry = Registry()
        await registry.register(entry)

        return {
            "id": entry.id,
            "name": entry.name,
            "type": type,
            "path": path,
        }

    @expose(
        help="Show entry details",
        examples=["kgents library show agent-123"],
    )
    async def show(self, id: str) -> dict[str, Any] | None:
        """
        Show detailed information about a catalog entry.
        """
        from agents.l import Registry

        registry = Registry()
        entry = await registry.get(id)

        if entry is None:
            return {"error": f"Entry not found: {id}"}

        return {
            "id": entry.id,
            "name": entry.name,
            "type": entry.entity_type.value if entry.entity_type else None,
            "status": entry.status.value if entry.status else None,
            "description": entry.description,
            "input_type": entry.input_type,
            "output_type": entry.output_type,
            "version": entry.version,
        }

    @expose(
        help="Show artifact lineage",
        examples=[
            "kgents library lineage agent-123",
            "kgents library lineage agent-123 --ancestors --depth=3",
        ],
    )
    async def lineage(
        self,
        id: str,
        ancestors: bool = False,
        descendants: bool = False,
        depth: int = 5,
    ) -> dict[str, Any]:
        """
        Show artifact lineage (ancestors and/or descendants).

        Returns the dependency graph for the specified artifact.
        """
        from agents.l import LineageGraph

        graph = LineageGraph()

        result: dict[str, Any] = {"id": id}

        if not descendants:
            ancestor_list = graph.get_ancestors(id, max_depth=depth)
            result["ancestors"] = list(ancestor_list)

        if not ancestors:
            descendant_list = graph.get_descendants(id, max_depth=depth)
            result["descendants"] = list(descendant_list)

        return result

    @expose(
        help="Verify composition compatibility",
        examples=[
            "kgents library compose parser validator analyzer",
            "kgents library compose agent-a agent-b",
        ],
    )
    async def compose(
        self,
        ids: str,
    ) -> dict[str, Any]:
        """
        Verify that agents can be composed in the given order.

        Checks type signatures for compatibility.
        """
        from agents.l import Registry, create_lattice

        id_list = ids.split()
        if len(id_list) < 2:
            return {"error": "At least 2 IDs required for composition check"}

        registry = Registry()
        lattice = create_lattice(registry)

        verification = await lattice.verify_pipeline(id_list)

        return {
            "valid": verification.valid,
            "pipeline": " >> ".join(id_list),
            "stages": [
                {
                    "from": s.from_agent,
                    "to": s.to_agent,
                    "compatible": s.compatible,
                }
                for s in verification.stages
            ]
            if verification.stages
            else [],
            "error": verification.error if hasattr(verification, "error") else None,
        }

    @expose(
        help="List registered types",
        examples=["kgents library types"],
    )
    async def types(self) -> dict[str, Any]:
        """
        List all registered types in the type lattice.
        """
        from agents.l import Registry, create_lattice

        registry = Registry()
        lattice = create_lattice(registry)

        type_list = list(lattice.types.values())

        return {
            "types": [
                {"id": t.id, "name": t.name, "kind": t.kind.value} for t in type_list
            ],
            "count": len(type_list),
        }

    @expose(
        help="Show catalog statistics",
        examples=["kgents library stats"],
    )
    async def stats(self) -> dict[str, Any]:
        """
        Show catalog statistics: total entries, by type, active/deprecated.
        """
        from agents.l import Registry, Status

        registry = Registry()
        all_entries = await registry.find()

        by_type: dict[str, int] = {}
        active = 0
        deprecated = 0

        for e in all_entries:
            t = e.entity_type.value if e.entity_type else "unknown"
            by_type[t] = by_type.get(t, 0) + 1

            if e.status == Status.ACTIVE:
                active += 1
            elif e.status == Status.DEPRECATED:
                deprecated += 1

        return {
            "total": len(all_entries),
            "by_type": by_type,
            "active": active,
            "deprecated": deprecated,
        }
