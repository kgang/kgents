"""
Skill Injection AGENTESE Node: @node("self.skill")

Exposes the JIT Skill Injection system through the AGENTESE protocol.

AGENTESE Paths:
- self.skill.manifest   - Registry status and statistics
- self.skill.active     - Currently active/injected skills
- self.skill.inject     - Inject skills for a task
- self.skill.evolve     - Trigger skill evolution from usage patterns
- self.skill.search     - Search for skills by keyword
- self.skill.gotchas    - Get gotchas for a task

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "Skills surface exactly when needed, not before."
    "Context-aware activation based on task patterns."

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .activation_engine import ActivationConditionEngine, get_activation_engine
from .bootstrap import bootstrap_skills
from .jit_injector import JITInjector, get_jit_injector
from .registry import SkillRegistry, get_skill_registry
from .stigmergic_memory import StigmergicMemory, get_stigmergic_memory
from .types import (
    InjectionResult,
    SkillActivation,
    SkillCategory,
    TaskContext,
    UsageOutcome,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer


# === Contract Types ===


@dataclass
class SkillManifestResponse:
    """Response for skill manifest request."""

    total_skills: int
    total_compositions: int
    skills_by_category: dict[str, int]
    memory_stats: dict[str, Any]
    bootstrapped: bool


@dataclass
class InjectRequest:
    """Request to inject skills for a task."""

    task: str
    active_files: list[str] | None = None
    error_messages: list[str] | None = None
    user_keywords: list[str] | None = None
    max_skills: int = 3


@dataclass
class InjectResponse:
    """Response with injected skill content."""

    content: str
    activated_skills: list[dict[str, Any]]
    composition: dict[str, Any] | None
    total_read_time_minutes: int


@dataclass
class SearchRequest:
    """Request to search for skills."""

    keywords: list[str]
    category: str | None = None
    limit: int = 5


@dataclass
class SearchResponse:
    """Response with search results."""

    results: list[dict[str, Any]]
    total_matches: int


@dataclass
class GotchasRequest:
    """Request for gotchas only."""

    task: str


@dataclass
class GotchasResponse:
    """Response with gotchas content."""

    content: str
    skill_count: int


@dataclass
class RecordOutcomeRequest:
    """Request to record skill usage outcome."""

    outcome: str  # "success", "partial", "failure", "skipped"
    feedback: str = ""
    duration_seconds: float = 0.0


@dataclass
class RecordOutcomeResponse:
    """Response after recording outcome."""

    recorded: bool
    skill_count: int


@dataclass
class EvolveResponse:
    """Response with skill evolution suggestions."""

    suggested_compositions: list[dict[str, Any]]
    skills_to_boost: list[str]
    skills_to_demote: list[str]


# === Renderings ===


@dataclass(frozen=True)
class SkillManifestRendering:
    """Rendering for skill manifest."""

    response: SkillManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "skill_manifest",
            "total_skills": self.response.total_skills,
            "total_compositions": self.response.total_compositions,
            "skills_by_category": self.response.skills_by_category,
            "memory_stats": self.response.memory_stats,
            "bootstrapped": self.response.bootstrapped,
        }

    def to_text(self) -> str:
        lines = [
            "Skill Injection Service",
            "=======================",
            f"Total Skills: {self.response.total_skills}",
            f"Total Compositions: {self.response.total_compositions}",
            f"Bootstrapped: {self.response.bootstrapped}",
            "",
            "Skills by Category:",
        ]
        for cat, count in self.response.skills_by_category.items():
            lines.append(f"  - {cat}: {count}")

        return "\n".join(lines)


@dataclass(frozen=True)
class InjectRendering:
    """Rendering for injection result."""

    result: InjectionResult

    def to_dict(self) -> dict[str, Any]:
        return self.result.to_dict()

    def to_text(self) -> str:
        if not self.result.content:
            return "No skills activated for this context."

        lines = [
            f"Injected {len(self.result.activations)} skill(s) "
            f"(~{self.result.total_read_time_minutes} min read time)",
            "",
            self.result.content,
        ]
        return "\n".join(lines)


# === Node ===


@node(
    "self.skill",
    description="JIT Skill Injection - Skills surface exactly when needed",
    dependencies=(),  # No external dependencies
    contracts={
        "manifest": Response(SkillManifestResponse),
        "inject": Contract(InjectRequest, InjectResponse),
        "search": Contract(SearchRequest, SearchResponse),
        "gotchas": Contract(GotchasRequest, GotchasResponse),
        "record": Contract(RecordOutcomeRequest, RecordOutcomeResponse),
        "evolve": Response(EvolveResponse),
    },
    examples=[
        ("manifest", {}, "Show skill registry status"),
        (
            "inject",
            {"task": "Add a new AGENTESE node for the Atelier service"},
            "Inject relevant skills",
        ),
        ("search", {"keywords": ["agent", "state machine"]}, "Search for skills"),
        ("gotchas", {"task": "Building a Crown Jewel"}, "Get just gotchas"),
        ("evolve", {}, "Get skill evolution suggestions"),
    ],
)
class SkillNode(BaseLogosNode):
    """
    AGENTESE node for JIT Skill Injection.

    Exposes skill registry, injection, and learning through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/skill/inject
        {"task": "Add a Crown Jewel service"}

        # Via Logos directly
        await logos.invoke("self.skill.inject", observer, task="Add agent")

        # Via CLI
        kgents skill inject "Add a Crown Jewel service"
    """

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        engine: ActivationConditionEngine | None = None,
        memory: StigmergicMemory | None = None,
        injector: JITInjector | None = None,
    ) -> None:
        """
        Initialize SkillNode.

        All dependencies are optional and will use global instances if not provided.
        """
        self._registry = registry or get_skill_registry()
        self._engine = engine or get_activation_engine()
        self._memory = memory or get_stigmergic_memory()
        self._injector = injector or get_jit_injector()
        self._bootstrapped = False

    @property
    def handle(self) -> str:
        return "self.skill"

    def _ensure_bootstrapped(self) -> None:
        """Ensure skills are bootstrapped."""
        if not self._bootstrapped:
            bootstrap_skills(registry=self._registry)
            self._bootstrapped = True

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access for developers/operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "inject", "search", "gotchas", "record", "evolve")

        # Read + inject for architects/researchers
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "inject", "search", "gotchas")

        # Read-only for newcomers
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return ("manifest", "search")

        # Guest: manifest only
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest skill registry status.

        AGENTESE: self.skill.manifest
        """
        self._ensure_bootstrapped()

        stats = self._registry.stats()
        memory_stats = self._memory.stats_summary()

        response = SkillManifestResponse(
            total_skills=stats["total_skills"],
            total_compositions=stats["total_compositions"],
            skills_by_category=stats["skills_by_category"],
            memory_stats=memory_stats,
            bootstrapped=self._bootstrapped,
        )

        return SkillManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        self._ensure_bootstrapped()

        if aspect == "inject":
            task = kwargs.get("task", "")
            if not task:
                return {"error": "task required"}

            result = await self._injector.inject_for_task(
                task=task,
                active_files=kwargs.get("active_files", []),
                error_messages=kwargs.get("error_messages", []),
                user_keywords=kwargs.get("user_keywords", []),
            )

            return InjectRendering(result=result).to_dict()

        elif aspect == "search":
            keywords = kwargs.get("keywords", [])
            if not keywords:
                return {"error": "keywords required"}

            category_str = kwargs.get("category")
            limit = kwargs.get("limit", 5)

            # Search by keywords
            matches = self._registry.find_by_keywords(keywords)

            # Filter by category if specified
            if category_str:
                try:
                    category = SkillCategory(category_str)
                    matches = [m for m in matches if m.skill.category == category]
                except ValueError:
                    pass

            # Limit results
            matches = matches[:limit]

            return {
                "results": [
                    {
                        "skill_id": m.skill.id,
                        "name": m.skill.name,
                        "category": m.skill.category.value,
                        "score": m.score,
                        "match_reason": m.match_reason,
                    }
                    for m in matches
                ],
                "total_matches": len(matches),
            }

        elif aspect == "gotchas":
            task = kwargs.get("task", "")
            if not task:
                return {"error": "task required"}

            content = await self._injector.inject_gotchas_only(task)
            skill_count = content.count("## Gotchas:")

            return {
                "content": content,
                "skill_count": skill_count,
            }

        elif aspect == "record":
            outcome_str = kwargs.get("outcome", "")
            if not outcome_str:
                return {"error": "outcome required"}

            try:
                outcome = UsageOutcome(outcome_str)
            except ValueError:
                return {"error": f"Invalid outcome: {outcome_str}"}

            self._injector.record_outcome(
                outcome=outcome,
                feedback=kwargs.get("feedback", ""),
                duration_seconds=kwargs.get("duration_seconds", 0.0),
            )

            return {
                "recorded": True,
                "skill_count": len(self._injector._current_activations),
            }

        elif aspect == "evolve":
            # Get evolution suggestions from memory
            suggested = self._memory.suggest_compositions(min_usage=3)

            # Analyze success rates
            skills_to_boost: list[str] = []
            skills_to_demote: list[str] = []

            for skill in self._registry.list_skills():
                rate = self._memory.get_success_rate(skill.id)
                if rate is not None:
                    if rate > 0.8:
                        skills_to_boost.append(skill.id)
                    elif rate < 0.3:
                        skills_to_demote.append(skill.id)

            return {
                "suggested_compositions": [c.to_dict() for c in suggested],
                "skills_to_boost": skills_to_boost,
                "skills_to_demote": skills_to_demote,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "EvolveResponse",
    "GotchasRequest",
    "GotchasResponse",
    "InjectRendering",
    "InjectRequest",
    "InjectResponse",
    "RecordOutcomeRequest",
    "RecordOutcomeResponse",
    "SearchRequest",
    "SearchResponse",
    "SkillManifestRendering",
    "SkillManifestResponse",
    "SkillNode",
]
