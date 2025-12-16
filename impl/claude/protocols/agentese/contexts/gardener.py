"""
AGENTESE Gardener Context: The 7th Crown Jewel

The Gardener: Autopoietic development substrate that routes all CLI
interactions through AGENTESE paths.

> *"The form that generates forms. The garden that tends itself."*

Core paths:
- concept.gardener.manifest → View Gardener status
- concept.gardener.route → Route natural language to AGENTESE path (LLM-powered)
- concept.gardener.propose → Get proactive suggestions
- concept.gardener.session.* → Session management (create, resume, advance)

The Gardener is not Kent's tool. It is Kent's collaborator.

Synergies with other Crown Jewels:
- Uses GARDENER_PATHS from crown_jewels.py for path registry
- Integrates with forest context for session persistence hints
- Routes to ALL crown jewel paths (Atelier, Coalition, Brain, Park, etc.)

Per plans/core-apps/the-gardener.md Phase 1: AGENTESE-First CLI Refactor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..node import BaseLogosNode, BasicRendering

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# OTEL tracer for observability
_tracer = trace.get_tracer("kgents.gardener")


# =============================================================================
# Route Method Enum for type safety
# =============================================================================


class RouteMethod(str, Enum):
    """How a route was resolved."""

    EXACT = "exact"
    PATTERN = "pattern"
    LLM = "llm"
    FALLBACK = "fallback"
    CROWN_JEWEL = "crown_jewel"  # Matched from crown jewel registry


# =============================================================================
# Command → AGENTESE Path Mapping
# =============================================================================

# Maps CLI commands (from hollow.py COMMAND_REGISTRY) to AGENTESE paths
# Format: "command_name" -> "agentese.path"
#
# This mapping enables:
# 1. Direct command invocation: `kg forest` → `kg self.forest.manifest`
# 2. Tab completion in shells
# 3. Natural language routing fallback
#
# All Crown Jewel shortcuts are also mapped here for consistency.
COMMAND_TO_PATH: dict[str, str] = {
    # ==========================================================================
    # AGENTESE Context Commands (already native)
    # ==========================================================================
    "self": "self.status.manifest",
    "world": "world.manifest",
    "concept": "concept.manifest",
    "void": "void.manifest",
    "time": "time.manifest",
    # ==========================================================================
    # Crown Jewel 1: Atelier Experience
    # ==========================================================================
    "atelier": "world.atelier.manifest",
    "studio": "world.atelier.session.create",
    "gallery": "world.atelier.gallery.manifest",
    "tokens": "self.tokens.manifest",
    # ==========================================================================
    # Crown Jewel 2: Coalition Forge
    # ==========================================================================
    "forge": "world.forge.manifest",
    "coalition": "world.coalition.manifest",
    "task": "concept.task.manifest",
    "credits": "self.credits.manifest",
    # ==========================================================================
    # Crown Jewel 3: Holographic Brain
    # ==========================================================================
    "brain": "self.memory.manifest",
    "memory": "self.memory.manifest",
    "capture": "self.memory.capture",
    "recall": "self.memory.recall",
    "crystal": "self.memory.crystal.manifest",
    "cartography": "self.memory.cartography.manifest",
    "ghost": "self.memory.ghost.surface",
    # ==========================================================================
    # Crown Jewel 4: Punchdrunk Park
    # ==========================================================================
    "park": "world.town.manifest",
    "town": "world.town.manifest",
    "inhabit": "world.town.inhabit.start",
    "scenario": "world.town.scenario.manifest",
    "consent": "self.consent.manifest",
    # ==========================================================================
    # Crown Jewel 5: Domain Simulation
    # ==========================================================================
    "sim": "world.simulation.manifest",
    "simulation": "world.simulation.manifest",
    "drill": "concept.drill.manifest",
    # ==========================================================================
    # Crown Jewel 6: Gestalt Visualizer
    # ==========================================================================
    "gestalt": "world.codebase.manifest",
    "arch": "world.codebase.manifest",
    "architecture": "world.codebase.manifest",
    "drift": "world.codebase.drift.witness",
    "governance": "concept.governance.manifest",
    # ==========================================================================
    # Crown Jewel 7: The Gardener (self-reference)
    # ==========================================================================
    "garden": "concept.gardener.manifest",
    "gardener": "concept.gardener.manifest",
    "route": "concept.gardener.route",
    "propose": "concept.gardener.propose",
    "session": "concept.gardener.session.manifest",
    # ==========================================================================
    # Forest / Planning
    # ==========================================================================
    "forest": "self.forest.manifest",
    "focus": "self.focus.manifest",
    "epilogues": "time.forest.epilogues",
    "meta": "self.meta.manifest",
    # ==========================================================================
    # Joy-Inducing Commands → AGENTESE mappings
    # ==========================================================================
    "challenge": "self.soul.challenge",
    "oblique": "void.entropy.oblique",
    "constrain": "concept.constraint.manifest",
    "yes-and": "self.soul.yes_and",
    "surprise-me": "void.entropy.sip",
    "surprise": "void.entropy.sip",
    "sip": "void.entropy.sip",
    "project": "world.project.manifest",
    "why": "concept.rationale.manifest",
    "tension": "concept.tension.manifest",
    # ==========================================================================
    # Soul / K-gent
    # ==========================================================================
    "soul": "self.soul.manifest",
    "dialogue": "self.soul.dialogue",
    "reflect": "self.soul.reflect",
    # ==========================================================================
    # Bootstrap Commands
    # ==========================================================================
    "init": "self.init",
    "wipe": "self.wipe",
    "migrate": "self.migrate",
    # ==========================================================================
    # Query/Subscribe
    # ==========================================================================
    "query": "concept.query",
    "subscribe": "world.subscribe",
    # ==========================================================================
    # Grow (Autopoietic generator)
    # ==========================================================================
    "grow": "self.grow.manifest",
    # ==========================================================================
    # Play (shortcuts)
    # ==========================================================================
    "play": "world.town.play",
}

# Natural language patterns → AGENTESE path mappings
# Used by the LLM router as a reference guide
#
# Patterns are lowercase and matched as substrings.
# Multiple patterns can map to the same path.
NL_PATTERN_HINTS: dict[str, list[str]] = {
    # -------------------------------------------------------------------------
    # Forest / Planning
    # -------------------------------------------------------------------------
    "self.forest.manifest": [
        "show forest",
        "forest status",
        "what plans",
        "plan status",
        "project status",
        "forest health",
        "canopy",
    ],
    # -------------------------------------------------------------------------
    # Soul / K-gent
    # -------------------------------------------------------------------------
    "self.soul.dialogue": [
        "talk to",
        "chat with",
        "dialogue",
        "conversation",
        "discuss",
        "let's talk",
    ],
    "self.soul.challenge": [
        "challenge me",
        "push me",
        "critique",
        "devil's advocate",
        "argue with",
    ],
    # -------------------------------------------------------------------------
    # Entropy / Void
    # -------------------------------------------------------------------------
    "void.entropy.sip": [
        "surprise me",
        "random",
        "serendipity",
        "inspire me",
        "something unexpected",
        "oblique strategy",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 3: Holographic Brain
    # -------------------------------------------------------------------------
    "self.memory.manifest": [
        "brain status",
        "memory status",
        "what do I know",
        "knowledge",
        "my brain",
        "holographic",
    ],
    "self.memory.capture": [
        "remember this",
        "save this",
        "capture this",
        "note this",
        "store this",
    ],
    "self.memory.recall": [
        "recall",
        "remember when",
        "find in memory",
        "search memory",
        "what was",
    ],
    "self.memory.crystal.manifest": [
        "crystals",
        "crystallized",
        "knowledge crystals",
    ],
    "self.memory.cartography.manifest": [
        "cartography",
        "knowledge map",
        "topology",
        "brain map",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 4: Punchdrunk Park
    # -------------------------------------------------------------------------
    "world.town.manifest": [
        "town status",
        "citizens",
        "agents",
        "town",
        "park status",
        "agent town",
    ],
    "world.town.inhabit.start": [
        "inhabit",
        "become citizen",
        "roleplay",
        "enter town",
        "embody",
    ],
    "world.town.scenario.manifest": [
        "scenarios",
        "available scenarios",
        "scenario list",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 1: Atelier
    # -------------------------------------------------------------------------
    "world.atelier.manifest": [
        "atelier",
        "workshop",
        "creation",
        "building",
        "studio",
    ],
    "world.atelier.gallery.manifest": [
        "gallery",
        "artifacts",
        "creations",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 2: Coalition Forge
    # -------------------------------------------------------------------------
    "world.forge.manifest": [
        "forge",
        "coalitions",
        "teams",
        "agent teams",
    ],
    "concept.task.manifest": [
        "tasks",
        "task templates",
        "available tasks",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 5: Domain Simulation
    # -------------------------------------------------------------------------
    "world.simulation.manifest": [
        "simulation",
        "simulate",
        "sim",
        "domain sim",
    ],
    "concept.drill.manifest": [
        "drills",
        "drill templates",
        "training",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 6: Gestalt Visualizer
    # -------------------------------------------------------------------------
    "world.codebase.manifest": [
        "architecture",
        "codebase",
        "gestalt",
        "modules",
        "code structure",
    ],
    "world.codebase.drift.witness": [
        "drift",
        "code drift",
        "what changed",
        "architectural drift",
    ],
    "concept.governance.manifest": [
        "governance",
        "policies",
        "code policies",
    ],
    # -------------------------------------------------------------------------
    # Crown Jewel 7: The Gardener
    # -------------------------------------------------------------------------
    "concept.gardener.propose": [
        "what should I do",
        "suggest",
        "propose",
        "next steps",
        "recommendations",
        "help me decide",
        "what now",
    ],
    "concept.gardener.manifest": [
        "gardener status",
        "gardener",
        "garden status",
    ],
}

# =============================================================================
# Gardener Affordances by Role
# =============================================================================

GARDENER_ROLE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    # Guest: can only query
    "guest": ("manifest", "route"),
    # Developer: can create sessions and get suggestions
    "developer": (
        "manifest",
        "route",
        "propose",
        "session.manifest",
        "session.create",
        "session.resume",
    ),
    # Meta: full access
    "meta": (
        "manifest",
        "route",
        "propose",
        "session.manifest",
        "session.create",
        "session.resume",
        "session.advance",
    ),
    "default": ("manifest", "route"),
}


# =============================================================================
# Route Result
# =============================================================================


@dataclass
class RouteResult:
    """Result of routing natural language to an AGENTESE path."""

    original_input: str
    resolved_path: str
    confidence: float  # 0.0 to 1.0
    method: str  # "exact", "pattern", "llm", "fallback"
    alternatives: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_input": self.original_input,
            "resolved_path": self.resolved_path,
            "confidence": self.confidence,
            "method": self.method,
            "alternatives": self.alternatives,
            "explanation": self.explanation,
        }


# =============================================================================
# Session State
# =============================================================================


@dataclass
class GardenerSession:
    """A Gardener development session."""

    session_id: str
    name: str
    created_at: datetime
    plan_path: str | None = None
    current_phase: str = "PLAN"
    progress: float = 0.0
    last_action: str = ""
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "plan_path": self.plan_path,
            "current_phase": self.current_phase,
            "progress": self.progress,
            "last_action": self.last_action,
            "checkpoints": self.checkpoints,
        }


# =============================================================================
# Gardener Node
# =============================================================================


@dataclass
class GardenerNode(BaseLogosNode):
    """
    Gardener context node: The 7th Crown Jewel.

    Provides AGENTESE handles for autopoietic development:
    - concept.gardener.manifest → Gardener status
    - concept.gardener.route → Natural language to AGENTESE path
    - concept.gardener.propose → Proactive suggestions
    - concept.gardener.session.* → Session management
    """

    _handle: str = "concept.gardener"

    # Active sessions (in-memory for now)
    _sessions: dict[str, GardenerSession] = field(default_factory=dict)

    # LLM client for routing (injected)
    _llm_client: Any = None

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-gated affordances."""
        return GARDENER_ROLE_AFFORDANCES.get(
            archetype, GARDENER_ROLE_AFFORDANCES["default"]
        )

    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """
        Return Gardener status view.

        AGENTESE: concept.gardener.manifest
        """
        with _tracer.start_as_current_span("gardener.manifest"):
            active_sessions = list(self._sessions.values())
            session_count = len(active_sessions)

            lines = [
                "🌱 GARDENER STATUS",
                "=" * 40,
                f"Active Sessions: {session_count}",
                "",
            ]

            if active_sessions:
                lines.append("Sessions:")
                for session in active_sessions[:5]:
                    phase_emoji = {
                        "PLAN": "📋",
                        "RESEARCH": "🔍",
                        "DEVELOP": "🛠️",
                        "IMPLEMENT": "⚙️",
                        "TEST": "🧪",
                        "REFLECT": "🪞",
                    }.get(session.current_phase, "📌")
                    lines.append(
                        f"  {phase_emoji} {session.name} ({session.current_phase})"
                    )
                    if session.plan_path:
                        lines.append(f"     Plan: {session.plan_path}")

            lines.extend(
                [
                    "",
                    "Commands:",
                    "  kg concept.gardener.route '<intent>'  → Route to path",
                    "  kg concept.gardener.propose          → Get suggestions",
                    "  kg /garden                           → Shortcut",
                ]
            )

            return BasicRendering(
                summary="Gardener Status",
                content="\n".join(lines),
                metadata={
                    "session_count": session_count,
                    "sessions": [s.to_dict() for s in active_sessions],
                },
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""
        match aspect:
            case "manifest":
                return await self.manifest(observer)
            case "route":
                return await self._route(observer, **kwargs)
            case "propose":
                return await self._propose(observer, **kwargs)
            case "session.manifest":
                return await self._session_manifest(observer, **kwargs)
            case "session.create":
                return await self._session_create(observer, **kwargs)
            case "session.resume":
                return await self._session_resume(observer, **kwargs)
            case "session.advance":
                return await self._session_advance(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # concept.gardener.route - Natural Language → AGENTESE Path
    # =========================================================================

    async def _route(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Route natural language to an AGENTESE path.

        AGENTESE: concept.gardener.route

        Five-stage resolution:
        1. Exact command match (from COMMAND_TO_PATH)
        2. Direct AGENTESE path validation
        3. Pattern match (from NL_PATTERN_HINTS)
        4. LLM inference (if client available)
        5. Fallback to concept.gardener.propose

        Args:
            input: Natural language input or command
            use_llm: Whether to use LLM for fuzzy routing (default: True)

        Returns:
            BasicRendering with resolved path and metadata
        """
        with _tracer.start_as_current_span("gardener.route") as span:
            input_text = kwargs.get("input", "")
            use_llm = kwargs.get("use_llm", True)

            # Set span attributes for observability
            span.set_attribute("gardener.input", input_text)
            span.set_attribute("gardener.input_length", len(input_text))

            # Handle empty input gracefully
            if not input_text:
                span.set_status(Status(StatusCode.ERROR, "No input provided"))
                return BasicRendering(
                    summary="No input provided",
                    content="Usage: kg concept.gardener.route --input '<your intent>'",
                    metadata={"error": "no_input"},
                )

            # Handle whitespace-only input
            if not input_text.strip():
                span.set_status(Status(StatusCode.ERROR, "Empty input"))
                return BasicRendering(
                    summary="Empty input",
                    content="Please provide a command or intent to route.",
                    metadata={"error": "empty_input"},
                )

            try:
                # Stage 1: Exact command match
                result = self._try_exact_match(input_text)
                if result.confidence > 0.9:
                    span.set_attribute("gardener.method", RouteMethod.EXACT.value)
                    span.set_attribute("gardener.resolved_path", result.resolved_path)
                    span.set_attribute("gardener.confidence", result.confidence)
                    span.set_status(Status(StatusCode.OK))
                    return self._render_route_result(result)

                # Stage 2: Pattern match
                result = self._try_pattern_match(input_text)
                if result.confidence > 0.6:
                    span.set_attribute("gardener.method", RouteMethod.PATTERN.value)
                    span.set_attribute("gardener.resolved_path", result.resolved_path)
                    span.set_attribute("gardener.confidence", result.confidence)
                    span.set_status(Status(StatusCode.OK))
                    return self._render_route_result(result)

                # Stage 3: LLM inference
                if use_llm and self._llm_client:
                    result = await self._try_llm_route(input_text)
                    if result.confidence > 0.5:
                        span.set_attribute("gardener.method", RouteMethod.LLM.value)
                        span.set_attribute(
                            "gardener.resolved_path", result.resolved_path
                        )
                        span.set_attribute("gardener.confidence", result.confidence)
                        span.set_status(Status(StatusCode.OK))
                        return self._render_route_result(result)

                # Stage 4: Fallback with suggestions
                span.set_attribute("gardener.method", RouteMethod.FALLBACK.value)
                alternatives = self._get_similar_paths(input_text)
                span.set_attribute("gardener.alternatives_count", len(alternatives))

                result = RouteResult(
                    original_input=input_text,
                    resolved_path="concept.gardener.propose",
                    confidence=0.3,
                    method=RouteMethod.FALLBACK.value,
                    alternatives=alternatives,
                    explanation="Could not confidently route. Try 'propose' for suggestions.",
                )
                span.set_status(Status(StatusCode.OK))
                return self._render_route_result(result)

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                return BasicRendering(
                    summary="Routing error",
                    content=f"Error routing '{input_text}': {e}",
                    metadata={"error": "routing_error", "exception": str(e)},
                )

    def _try_exact_match(self, input_text: str) -> RouteResult:
        """Try exact command match from COMMAND_TO_PATH."""
        # Normalize input
        normalized = input_text.lower().strip()

        # Check direct command name
        if normalized in COMMAND_TO_PATH:
            return RouteResult(
                original_input=input_text,
                resolved_path=COMMAND_TO_PATH[normalized],
                confidence=1.0,
                method="exact",
                explanation=f"Command '{normalized}' → {COMMAND_TO_PATH[normalized]}",
            )

        # Check if input IS an AGENTESE path already
        if "." in normalized and normalized.split(".")[0] in {
            "world",
            "self",
            "concept",
            "void",
            "time",
        }:
            return RouteResult(
                original_input=input_text,
                resolved_path=normalized,
                confidence=1.0,
                method="exact",
                explanation=f"Direct AGENTESE path: {normalized}",
            )

        return RouteResult(
            original_input=input_text,
            resolved_path="",
            confidence=0.0,
            method="exact",
        )

    def _try_pattern_match(self, input_text: str) -> RouteResult:
        """Try pattern match from NL_PATTERN_HINTS."""
        normalized = input_text.lower().strip()
        best_match = ""
        best_score = 0.0

        for path, patterns in NL_PATTERN_HINTS.items():
            for pattern in patterns:
                # Simple substring matching
                if pattern in normalized:
                    score = len(pattern) / max(len(normalized), 1)
                    if score > best_score:
                        best_score = score
                        best_match = path

        if best_match and best_score > 0.3:
            return RouteResult(
                original_input=input_text,
                resolved_path=best_match,
                confidence=min(0.8, best_score + 0.3),
                method="pattern",
                explanation=f"Pattern matched: '{input_text}' → {best_match}",
            )

        return RouteResult(
            original_input=input_text,
            resolved_path="",
            confidence=0.0,
            method="pattern",
        )

    async def _try_llm_route(self, input_text: str) -> RouteResult:
        """Use LLM to route natural language to AGENTESE path."""
        if not self._llm_client:
            return RouteResult(
                original_input=input_text,
                resolved_path="",
                confidence=0.0,
                method="llm",
            )

        # Build available paths for LLM context
        available_paths = list(COMMAND_TO_PATH.values())
        available_paths.extend(NL_PATTERN_HINTS.keys())

        prompt = f"""You are routing natural language to an AGENTESE path.

Available paths and their meanings:
- self.forest.manifest → Show project/plan status
- self.soul.dialogue → Have a conversation
- self.soul.challenge → Get challenged/critiqued
- void.entropy.sip → Get random/serendipitous suggestion
- self.memory.manifest → Brain/knowledge status
- self.memory.capture → Save something to memory
- self.memory.recall → Search memory
- world.town.manifest → Agent Town status
- world.atelier.manifest → Creation workshop
- world.codebase.manifest → Architecture view
- concept.gardener.propose → Get suggestions

User input: "{input_text}"

Respond with ONLY the best matching AGENTESE path. No explanation."""

        try:
            response = await self._llm_client.complete(prompt, max_tokens=50)
            # Extract path from response
            path = response.strip()
            # Validate it looks like a path
            if "." in path and path.split(".")[0] in {
                "world",
                "self",
                "concept",
                "void",
                "time",
            }:
                return RouteResult(
                    original_input=input_text,
                    resolved_path=path,
                    confidence=0.7,
                    method="llm",
                    explanation=f"LLM routed: '{input_text}' → {path}",
                )
        except Exception:
            pass

        return RouteResult(
            original_input=input_text,
            resolved_path="",
            confidence=0.0,
            method="llm",
        )

    def _get_similar_paths(self, input_text: str) -> list[str]:
        """Get paths that might be similar to the input."""
        words = set(input_text.lower().split())
        suggestions = []

        for path, patterns in NL_PATTERN_HINTS.items():
            for pattern in patterns:
                pattern_words = set(pattern.lower().split())
                if words & pattern_words:  # Any overlap
                    suggestions.append(path)
                    break

        return list(set(suggestions))[:5]

    def _render_route_result(self, result: RouteResult) -> BasicRendering:
        """Render a RouteResult as BasicRendering."""
        lines = [
            f"🔄 ROUTING: {result.original_input}",
            "",
            f"  → {result.resolved_path}",
            "",
            f"  Method: {result.method}",
            f"  Confidence: {result.confidence:.0%}",
        ]

        if result.explanation:
            lines.append(f"  Explanation: {result.explanation}")

        if result.alternatives:
            lines.append("")
            lines.append("  Alternatives:")
            for alt in result.alternatives[:3]:
                lines.append(f"    - {alt}")

        return BasicRendering(
            summary=f"Route: {result.resolved_path}",
            content="\n".join(lines),
            metadata=result.to_dict(),
        )

    # =========================================================================
    # concept.gardener.propose - Proactive Suggestions
    # =========================================================================

    async def _propose(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Get proactive suggestions for what to do next.

        AGENTESE: concept.gardener.propose

        Analyzes:
        - Active Gardener sessions
        - Forest status (via self.forest.manifest)
        - Recent activity
        - Accursed share (dormant plans)
        """
        with _tracer.start_as_current_span("gardener.propose"):
            suggestions: list[dict[str, str]] = []

            # Check for active sessions
            active_sessions = list(self._sessions.values())
            for session in active_sessions:
                suggestions.append(
                    {
                        "action": f"kg concept.gardener.session.resume --id {session.session_id}",
                        "reason": f"Resume '{session.name}' at {session.current_phase}",
                        "priority": "high",
                    }
                )

            # Default suggestions if no active sessions
            if not suggestions:
                suggestions = [
                    {
                        "action": "kg self.forest.manifest",
                        "reason": "Check project health and status",
                        "priority": "medium",
                    },
                    {
                        "action": "kg void.entropy.sip",
                        "reason": "Get creative inspiration",
                        "priority": "low",
                    },
                    {
                        "action": "kg concept.gardener.session.create --name 'New Feature'",
                        "reason": "Start a new development session",
                        "priority": "medium",
                    },
                ]

            lines = [
                "💡 GARDENER SUGGESTIONS",
                "=" * 40,
                "",
            ]

            for i, s in enumerate(suggestions[:5], 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    s["priority"], "⚪"
                )
                lines.append(f"{i}. {priority_emoji} {s['reason']}")
                lines.append(f"   → {s['action']}")
                lines.append("")

            return BasicRendering(
                summary="Gardener Suggestions",
                content="\n".join(lines),
                metadata={
                    "suggestion_count": len(suggestions),
                    "suggestions": suggestions,
                },
            )

    # =========================================================================
    # Session Management
    # =========================================================================

    async def _session_manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Show current session state.

        AGENTESE: concept.gardener.session.manifest
        """
        session_id = kwargs.get("id")

        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            lines = [
                f"📋 SESSION: {session.name}",
                "=" * 40,
                f"ID: {session.session_id}",
                f"Phase: {session.current_phase}",
                f"Progress: {session.progress:.0%}",
                f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            ]
            if session.plan_path:
                lines.append(f"Plan: {session.plan_path}")
            if session.last_action:
                lines.append(f"Last Action: {session.last_action}")

            return BasicRendering(
                summary=f"Session: {session.name}",
                content="\n".join(lines),
                metadata=session.to_dict(),
            )

        # List all sessions
        sessions = list(self._sessions.values())
        if not sessions:
            return BasicRendering(
                summary="No Active Sessions",
                content="No active sessions. Use concept.gardener.session.create to start one.",
                metadata={"sessions": []},
            )

        lines = ["📋 ACTIVE SESSIONS", "=" * 40, ""]
        for session in sessions:
            lines.append(f"• {session.name} ({session.session_id[:8]})")
            lines.append(f"  Phase: {session.current_phase}")
            lines.append("")

        return BasicRendering(
            summary=f"{len(sessions)} Sessions",
            content="\n".join(lines),
            metadata={"sessions": [s.to_dict() for s in sessions]},
        )

    async def _session_create(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Create a new development session.

        AGENTESE: concept.gardener.session.create
        """
        import uuid

        name = kwargs.get("name", "New Session")
        plan_path = kwargs.get("plan")

        session_id = str(uuid.uuid4())[:8]
        session = GardenerSession(
            session_id=session_id,
            name=name,
            created_at=datetime.now(),
            plan_path=plan_path,
            current_phase="PLAN",
            progress=0.0,
        )

        self._sessions[session_id] = session

        return BasicRendering(
            summary=f"Session Created: {name}",
            content=f"""✅ SESSION CREATED

ID: {session_id}
Name: {name}
Phase: PLAN
Plan: {plan_path or "(none)"}

Next steps:
  kg concept.gardener.session.manifest --id {session_id}
  kg concept.gardener.session.advance --id {session_id}
""",
            metadata=session.to_dict(),
        )

    async def _session_resume(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Resume an existing session.

        AGENTESE: concept.gardener.session.resume
        """
        session_id = kwargs.get("id")

        if not session_id:
            return BasicRendering(
                summary="Session ID Required",
                content="Usage: kg concept.gardener.session.resume --id <session_id>",
                metadata={"error": "no_session_id"},
            )

        if session_id not in self._sessions:
            return BasicRendering(
                summary="Session Not Found",
                content=f"No session with ID '{session_id}'",
                metadata={"error": "session_not_found"},
            )

        session = self._sessions[session_id]
        session.last_action = f"Resumed at {datetime.now().strftime('%H:%M')}"

        return BasicRendering(
            summary=f"Resumed: {session.name}",
            content=f"""🔄 SESSION RESUMED

Name: {session.name}
Phase: {session.current_phase}
Progress: {session.progress:.0%}

Ready to continue.
""",
            metadata=session.to_dict(),
        )

    async def _session_advance(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Advance session to next N-Phase.

        AGENTESE: concept.gardener.session.advance
        """
        session_id = kwargs.get("id")

        if not session_id or session_id not in self._sessions:
            return BasicRendering(
                summary="Invalid Session",
                content="Session not found. Use --id <session_id>",
                metadata={"error": "invalid_session"},
            )

        session = self._sessions[session_id]

        # N-Phase progression
        phases = [
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "REFLECT",
        ]

        current_idx = phases.index(session.current_phase)
        if current_idx < len(phases) - 1:
            session.current_phase = phases[current_idx + 1]
            session.progress = (current_idx + 1) / len(phases)
            session.last_action = f"Advanced to {session.current_phase}"

            return BasicRendering(
                summary=f"Advanced to {session.current_phase}",
                content=f"""⏩ PHASE ADVANCED

Session: {session.name}
Phase: {phases[current_idx]} → {session.current_phase}
Progress: {session.progress:.0%}
""",
                metadata=session.to_dict(),
            )
        else:
            return BasicRendering(
                summary="Session Complete",
                content=f"Session '{session.name}' is at REFLECT (final phase).",
                metadata=session.to_dict(),
            )


# =============================================================================
# Gardener Context Resolver
# =============================================================================


@dataclass
class GardenerContextResolver:
    """
    Resolver for concept.gardener.* paths.

    Routes all gardener paths to the singleton GardenerNode.
    """

    _node: GardenerNode | None = None
    _llm_client: Any = None

    def resolve(self, holon: str, rest: list[str]) -> GardenerNode:
        """Resolve to GardenerNode singleton."""
        if self._node is None:
            self._node = GardenerNode(_llm_client=self._llm_client)
        return self._node


# =============================================================================
# Factory Functions
# =============================================================================


def create_gardener_resolver(llm_client: Any = None) -> GardenerContextResolver:
    """
    Create a GardenerContextResolver.

    Args:
        llm_client: Optional LLM client for natural language routing
    """
    return GardenerContextResolver(_llm_client=llm_client)


def create_gardener_node(llm_client: Any = None) -> GardenerNode:
    """Create a standalone GardenerNode."""
    return GardenerNode(_llm_client=llm_client)


def resolve_command_to_path(command: str) -> str | None:
    """
    Resolve a CLI command name to its AGENTESE path.

    Args:
        command: Command name (e.g., "forest", "town")

    Returns:
        AGENTESE path or None if not found
    """
    return COMMAND_TO_PATH.get(command.lower().strip())


def get_all_command_mappings() -> dict[str, str]:
    """Get all command → path mappings."""
    return COMMAND_TO_PATH.copy()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "COMMAND_TO_PATH",
    "NL_PATTERN_HINTS",
    "GARDENER_ROLE_AFFORDANCES",
    # Enums
    "RouteMethod",
    # Data classes
    "RouteResult",
    "GardenerSession",
    # Node
    "GardenerNode",
    # Resolver
    "GardenerContextResolver",
    # Factory functions
    "create_gardener_resolver",
    "create_gardener_node",
    "resolve_command_to_path",
    "get_all_command_mappings",
]
