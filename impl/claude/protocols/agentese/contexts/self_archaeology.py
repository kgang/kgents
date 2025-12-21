"""
AGENTESE Self Archaeology Context: Mining git history for patterns.

Knowledge-related nodes for self.memory.archaeology.* paths:
- ArchaeologyNode: Repository archaeology and pattern extraction

This node provides AGENTESE access to the Archaeology service for
mining git history, extracting patterns, and generating priors for ASHC.

AGENTESE Paths:
    self.memory.archaeology.manifest    - Show archaeology summary
    self.memory.archaeology.mine        - Mine git history for patterns
    self.memory.archaeology.priors      - Extract ASHC causal priors
    self.memory.archaeology.crystals    - Generate Brain crystals
    self.memory.archaeology.seed        - Seed ASHC CausalGraph

See: services/archaeology/
See: spec/protocols/repo-archaeology.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# ArchaeologyNode: AGENTESE Interface to Archaeology
# =============================================================================


# Archaeology affordances
ARCHAEOLOGY_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "mine",
    "priors",
    "crystals",
    "seed",
)


@node(
    "self.memory.archaeology",
    description="Repository archaeology and pattern extraction",
)
@dataclass
class ArchaeologyNode(BaseLogosNode):
    """
    self.memory.archaeology - Repository archaeology and pattern mining.

    Archaeology mines git history to:
    1. Classify feature health (THRIVING, STABLE, ABANDONED, etc.)
    2. Extract patterns that correlate with success
    3. Generate priors for ASHC's causal learning
    4. Create HistoryCrystals for Brain memory

    Philosophy: "Mining our own history for causal patterns."

    AGENTESE: self.memory.archaeology.*
    """

    _handle: str = "self.memory.archaeology"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Archaeology affordances available to all archetypes."""
        return ARCHAEOLOGY_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show archaeology summary and capabilities.

        Returns:
            Summary of what archaeology can do
        """
        manifest_data = {
            "path": self.handle,
            "description": "Repository archaeology and pattern extraction",
            "capabilities": [
                "mine: Parse git history and classify features",
                "priors: Extract causal priors for ASHC",
                "crystals: Generate HistoryCrystals for Brain",
                "seed: Seed ASHC CausalGraph with archaeological priors",
            ],
            "feature_statuses": [
                "THRIVING: Active development, tests passing",
                "STABLE: Mature, low activity, solid tests",
                "LANGUISHING: Started strong, activity dropped",
                "ABANDONED: No recent activity, broken/no tests",
                "OVER_ENGINEERED: High complexity, low usage",
            ],
            "patterns_extracted": [
                "early_test_adoption: Tests in first 10 commits",
                "sustained_momentum: High velocity sustained",
                "conventional_commits: feat:, fix:, etc.",
                "spec_impl_coevolution: Spec+impl evolve together",
            ],
        }

        return BasicRendering(
            summary="Repository Archaeology",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Archaeology-specific aspects."""
        match aspect:
            case "mine":
                return await self._mine_history(**kwargs)
            case "priors":
                return await self._extract_priors(**kwargs)
            case "crystals":
                return await self._generate_crystals(**kwargs)
            case "seed":
                return await self._seed_ashc(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    async def _mine_history(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> dict[str, Any]:
        """
        Mine git history and classify features.

        Args:
            repo_path: Path to repository (default: current)
            max_commits: Maximum commits to parse

        Returns:
            Feature classification report
        """
        from services.archaeology import (
            FEATURE_PATTERNS,
            classify_all_features,
            generate_report,
            parse_git_log,
        )

        try:
            # Parse commits (parse_git_log runs git internally)
            commits = parse_git_log(repo_path=repo_path, max_commits=max_commits)

            # Classify features
            trajectories = classify_all_features(FEATURE_PATTERNS, commits)

            # Generate report
            report = generate_report(trajectories)

            # Summary stats
            by_status: dict[str, int] = {}
            for t in trajectories.values():
                status_name = t.status.value
                by_status[status_name] = by_status.get(status_name, 0) + 1

            return {
                "total_commits": len(commits),
                "total_features": len(trajectories),
                "by_status": by_status,
                "report": report,
            }

        except Exception as e:
            return {
                "error": "mining_failed",
                "message": str(e),
            }

    async def _extract_priors(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> dict[str, Any]:
        """
        Extract causal priors for ASHC from git history.

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze

        Returns:
            Extracted priors and patterns
        """
        from services.archaeology import (
            FEATURE_PATTERNS,
            classify_all_features,
            extract_causal_priors,
            extract_evolution_traces,
            extract_spec_patterns,
            generate_prior_report,
            parse_git_log,
        )

        try:
            # Parse commits (parse_git_log runs git internally)
            commits = parse_git_log(repo_path=repo_path, max_commits=max_commits)
            trajectories = classify_all_features(FEATURE_PATTERNS, commits)

            # Extract priors (convert dict values to list)
            trajectory_list = list(trajectories.values())
            patterns = extract_spec_patterns(trajectory_list)
            traces = extract_evolution_traces(trajectory_list)
            priors = extract_causal_priors(trajectory_list)

            # Generate report
            report = generate_prior_report(patterns, traces, priors)

            return {
                "patterns_count": len(patterns),
                "traces_count": len(traces),
                "priors_count": len(priors),
                "patterns": [
                    {
                        "type": p.pattern_type,
                        "correlation": p.success_correlation,
                        "confidence": p.confidence,
                    }
                    for p in patterns
                ],
                "priors": [
                    {
                        "pattern": p.pattern,
                        "correlation": p.outcome_correlation,
                        "sample_size": p.sample_size,
                    }
                    for p in priors
                ],
                "report": report,
            }

        except Exception as e:
            return {
                "error": "extraction_failed",
                "message": str(e),
            }

    async def _generate_crystals(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
        min_commits: int = 5,
        store_in_brain: bool = False,
    ) -> dict[str, Any]:
        """
        Generate HistoryCrystals from git history.

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze
            min_commits: Minimum commits for a crystal
            store_in_brain: Whether to store crystals in Brain

        Returns:
            Generated crystals
        """
        from services.archaeology import (
            FEATURE_PATTERNS,
            classify_all_features,
            generate_all_crystals,
            generate_crystal_report,
            parse_git_log,
        )

        try:
            # Parse commits (parse_git_log runs git internally)
            commits = parse_git_log(repo_path=repo_path, max_commits=max_commits)
            trajectories = classify_all_features(FEATURE_PATTERNS, commits)

            # Generate crystals (convert dict values to list)
            trajectory_list = list(trajectories.values())
            crystals = generate_all_crystals(trajectory_list, min_commits=min_commits)

            # Generate report
            report = generate_crystal_report(crystals)

            crystal_data = [
                {
                    "feature": c.feature_name,
                    "status": c.status.value,
                    "valence": c.emotional_valence,
                    "commits": c.commit_count,
                    "lessons": list(c.lessons[:2]),  # First 2 lessons
                }
                for c in crystals
            ]

            response = {
                "total_crystals": len(crystals),
                "crystals": crystal_data,
                "report": report,
            }

            # Optionally store in Brain
            if store_in_brain and crystals:
                stored = await self._store_crystals(crystals)
                response["stored_in_brain"] = stored

            return response

        except Exception as e:
            return {
                "error": "crystal_generation_failed",
                "message": str(e),
            }

    async def _store_crystals(self, crystals: list[Any]) -> int:
        """Store crystals in Brain (helper)."""
        try:
            from protocols.agentese.gateway import create_gateway
            from protocols.agentese.node import Observer

            gateway = create_gateway(prefix="/agentese")
            observer = Observer.test()

            stored = 0
            for crystal in crystals:
                brain_data = crystal.to_brain_crystal()
                # Use Brain's capture via gateway
                await gateway._invoke_path(
                    "self.memory",
                    "capture",
                    observer,
                    content=brain_data["content"],
                    tags=brain_data["tags"],
                )
                stored += 1

            return stored
        except Exception:
            return 0  # Graceful degradation

    async def _seed_ashc(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> dict[str, Any]:
        """
        Seed ASHC CausalGraph with archaeological priors.

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze

        Returns:
            Seeding result
        """
        from services.archaeology import (
            FEATURE_PATTERNS,
            classify_all_features,
            extract_causal_priors,
            extract_spec_patterns,
            parse_git_log,
        )
        from services.archaeology.ashc_adapter import (
            create_seeded_learner,
            generate_priors_report,
        )

        try:
            # Parse commits (parse_git_log runs git internally)
            commits = parse_git_log(repo_path=repo_path, max_commits=max_commits)
            trajectories = classify_all_features(FEATURE_PATTERNS, commits)

            # Extract priors (convert dict values to list)
            trajectory_list = list(trajectories.values())
            patterns = extract_spec_patterns(trajectory_list)
            priors = extract_causal_priors(trajectory_list)

            # Create seeded learner
            learner, conversion_result = create_seeded_learner(
                priors=priors,
                patterns=patterns,
            )

            # Generate report
            report = generate_priors_report(conversion_result)

            return {
                "success": True,
                "edges_created": conversion_result.edges_created,
                "graph_edge_count": learner.graph.edge_count,
                "patterns_incorporated": conversion_result.patterns_incorporated,
                "warnings": conversion_result.warnings,
                "report": report,
            }

        except Exception as e:
            return {
                "error": "seeding_failed",
                "message": str(e),
            }

    # ==========================================================================
    # Public Interface (for direct calls / testing)
    # ==========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Mine git history and classify features",
    )
    async def mine(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> BasicRendering:
        """
        Mine git history and classify features (public API).

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to parse

        Returns:
            BasicRendering with classification results
        """
        data = await self._mine_history(repo_path=repo_path, max_commits=max_commits)

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=data["message"],
                metadata=data,
            )

        return BasicRendering(
            summary=f"Mined {data['total_commits']} commits, {data['total_features']} features",
            content=data.get("report", ""),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Extract ASHC causal priors from git history",
    )
    async def priors(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> BasicRendering:
        """
        Extract causal priors for ASHC (public API).

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze

        Returns:
            BasicRendering with extracted priors
        """
        data = await self._extract_priors(repo_path=repo_path, max_commits=max_commits)

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=data["message"],
                metadata=data,
            )

        return BasicRendering(
            summary=f"Extracted {data['patterns_count']} patterns, {data['priors_count']} priors",
            content=data.get("report", ""),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        help="Generate HistoryCrystals for Brain memory",
    )
    async def crystals(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
        min_commits: int = 5,
        store_in_brain: bool = False,
    ) -> BasicRendering:
        """
        Generate HistoryCrystals from git history (public API).

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze
            min_commits: Minimum commits for a crystal
            store_in_brain: Whether to store in Brain

        Returns:
            BasicRendering with generated crystals
        """
        data = await self._generate_crystals(
            repo_path=repo_path,
            max_commits=max_commits,
            min_commits=min_commits,
            store_in_brain=store_in_brain,
        )

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=data["message"],
                metadata=data,
            )

        summary = f"Generated {data['total_crystals']} crystals"
        if "stored_in_brain" in data:
            summary += f", stored {data['stored_in_brain']} in Brain"

        return BasicRendering(
            summary=summary,
            content=data.get("report", ""),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        help="Seed ASHC CausalGraph with archaeological priors",
    )
    async def seed(
        self,
        repo_path: str = ".",
        max_commits: int = 1000,
    ) -> BasicRendering:
        """
        Seed ASHC CausalGraph with archaeological priors (public API).

        Args:
            repo_path: Path to repository
            max_commits: Maximum commits to analyze

        Returns:
            BasicRendering with seeding result
        """
        data = await self._seed_ashc(repo_path=repo_path, max_commits=max_commits)

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=data["message"],
                metadata=data,
            )

        return BasicRendering(
            summary=f"Seeded ASHC with {data['edges_created']} priors ({data['graph_edge_count']} edges)",
            content=data.get("report", ""),
            metadata=data,
        )

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Repository Archaeology",
            "=" * 40,
            "",
            data["description"],
            "",
            "Capabilities:",
        ]

        for cap in data["capabilities"]:
            lines.append(f"  - {cap}")

        lines.extend(
            [
                "",
                "Feature Statuses:",
            ]
        )

        for status in data["feature_statuses"]:
            lines.append(f"  - {status}")

        lines.extend(
            [
                "",
                "Patterns Extracted:",
            ]
        )

        for pattern in data["patterns_extracted"]:
            lines.append(f"  - {pattern}")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ArchaeologyNode",
]
