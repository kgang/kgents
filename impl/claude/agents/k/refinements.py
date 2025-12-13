"""
K-gent 110% Refinements: Domains 5-7.

Domain 5: AGENTESE Paths - self.soul.* paths with observer-awareness
Domain 6: Error Experience - SoulError hierarchy, GracefulDegradation
Domain 7: Deferred Capabilities - FractalExpander, HolographicConstitution

Philosophy:
    "The 110% isn't about adding features - it's about the tools
    disappearing and what remains being 'Kent on his best day.'"
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from .soul import KgentSoul


# =============================================================================
# Domain 5: AGENTESE Paths
# =============================================================================


class SoulPath(str, Enum):
    """
    AGENTESE paths for self.soul.* namespace.

    These paths provide observer-aware access to soul state.
    The same path yields different results based on who's asking.
    """

    # Core state
    MANIFEST = "self.soul.manifest"  # Full state dump
    WITNESS = "self.soul.witness"  # Historical trace
    REFINE = "self.soul.refine"  # Trigger hypnagogia

    # Eigenvectors
    EIGENVECTORS = "self.soul.eigenvectors"  # All eigenvectors
    AESTHETIC = "self.soul.aesthetic"  # Aesthetic coordinate
    CATEGORICAL = "self.soul.categorical"  # Categorical coordinate
    GRATITUDE = "self.soul.gratitude"  # Gratitude coordinate
    HETERARCHY = "self.soul.heterarchy"  # Heterarchy coordinate
    GENERATIVITY = "self.soul.generativity"  # Generativity coordinate
    JOY = "self.soul.joy"  # Joy coordinate

    # Entropy
    SIP = "self.soul.sip"  # Draw from entropy budget
    TITHE = "self.soul.tithe"  # Pay gratitude tax

    # Garden
    GARDEN = "self.soul.garden"  # PersonaGarden handle
    PLANT = "self.soul.garden.plant"  # Plant new pattern
    NURTURE = "self.soul.garden.nurture"  # Nurture existing


@dataclass
class SoulPathResult:
    """Result from invoking a soul path."""

    path: str
    value: Any
    observer: str  # Who asked
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    was_cached: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "value": self.value,
            "observer": self.observer,
            "timestamp": self.timestamp.isoformat(),
            "was_cached": self.was_cached,
        }


class SoulPathResolver:
    """
    Resolver for AGENTESE self.soul.* paths.

    Implements observer-aware resolution - the same path can yield
    different results based on who's asking (umwelt-aware).
    """

    def __init__(self, soul: "KgentSoul") -> None:
        """Initialize resolver."""
        self._soul = soul
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register path handlers."""
        self._handlers = {
            SoulPath.MANIFEST.value: self._handle_manifest,
            SoulPath.WITNESS.value: self._handle_witness,
            SoulPath.EIGENVECTORS.value: self._handle_eigenvectors,
            SoulPath.AESTHETIC.value: lambda o: self._handle_eigenvector(
                "aesthetic", o
            ),
            SoulPath.CATEGORICAL.value: lambda o: self._handle_eigenvector(
                "categorical", o
            ),
            SoulPath.GRATITUDE.value: lambda o: self._handle_eigenvector(
                "gratitude", o
            ),
            SoulPath.HETERARCHY.value: lambda o: self._handle_eigenvector(
                "heterarchy", o
            ),
            SoulPath.GENERATIVITY.value: lambda o: self._handle_eigenvector(
                "generativity", o
            ),
            SoulPath.JOY.value: lambda o: self._handle_eigenvector("joy", o),
            SoulPath.SIP.value: self._handle_sip,
            SoulPath.TITHE.value: self._handle_tithe,
            SoulPath.GARDEN.value: self._handle_garden,
        }

    async def resolve(
        self,
        path: str,
        observer: str = "anonymous",
        **kwargs: Any,
    ) -> SoulPathResult:
        """
        Resolve an AGENTESE path.

        Args:
            path: The path to resolve (e.g., "self.soul.manifest")
            observer: Who is asking (affects result)
            **kwargs: Additional arguments for the handler

        Returns:
            SoulPathResult with the resolved value
        """
        handler = self._handlers.get(path)
        if not handler:
            return SoulPathResult(
                path=path,
                value={"error": f"Unknown path: {path}"},
                observer=observer,
            )

        try:
            value = handler(observer, **kwargs) if kwargs else handler(observer)
            return SoulPathResult(path=path, value=value, observer=observer)
        except Exception as e:
            return SoulPathResult(
                path=path,
                value={"error": str(e)},
                observer=observer,
            )

    def _handle_manifest(self, observer: str) -> dict[str, Any]:
        """Handle self.soul.manifest - observer-aware state dump."""
        base_state = self._soul.manifest()

        # Adjust based on observer
        if observer == "architect":
            # Show more structure
            return {
                "structure": base_state,
                "eigenvector_graph": self._eigenvector_graph(),
            }
        elif observer == "poet":
            # Show more feeling
            return {
                "mood": self._soul.eigenvectors.joy.confidence,
                "dominant_theme": self._dominant_eigenvector(),
            }
        else:
            return asdict(base_state)

    def _handle_witness(self, observer: str) -> dict[str, Any]:
        """Handle self.soul.witness - historical trace."""
        # Return recent interaction history
        return {
            "interactions": self._soul._state.interactions_count,
            "tokens_used": self._soul._state.tokens_used_session,
            "mode_history": [self._soul._state.active_mode.value],
        }

    def _handle_eigenvectors(self, observer: str) -> dict[str, Any]:
        """Handle self.soul.eigenvectors - all coordinates."""
        ev = self._soul.eigenvectors
        return {
            "aesthetic": {
                "value": ev.aesthetic.value,
                "confidence": ev.aesthetic.confidence,
            },
            "categorical": {
                "value": ev.categorical.value,
                "confidence": ev.categorical.confidence,
            },
            "gratitude": {
                "value": ev.gratitude.value,
                "confidence": ev.gratitude.confidence,
            },
            "heterarchy": {
                "value": ev.heterarchy.value,
                "confidence": ev.heterarchy.confidence,
            },
            "generativity": {
                "value": ev.generativity.value,
                "confidence": ev.generativity.confidence,
            },
            "joy": {"value": ev.joy.value, "confidence": ev.joy.confidence},
        }

    def _handle_eigenvector(self, name: str, observer: str) -> dict[str, Any]:
        """Handle individual eigenvector path."""
        ev = getattr(self._soul.eigenvectors, name, None)
        if ev:
            return {"name": name, "value": ev.value, "confidence": ev.confidence}
        return {"error": f"Unknown eigenvector: {name}"}

    def _handle_sip(self, observer: str, amount: float = 0.1) -> dict[str, Any]:
        """Handle self.soul.sip - draw from entropy budget."""
        # Symbolic: return a random insight from patterns
        import random

        patterns = list(self._soul._persona_state.seed.patterns.values())
        if patterns and patterns[0]:
            insight = random.choice(patterns[0])
            return {"sip": insight, "amount": amount, "source": "pattern_garden"}
        return {"sip": "emptiness", "amount": amount, "source": "void"}

    def _handle_tithe(self, observer: str, gratitude: str = "") -> dict[str, Any]:
        """Handle self.soul.tithe - pay gratitude tax."""
        # Record gratitude (symbolic for now)
        return {
            "received": gratitude or "unspoken gratitude",
            "observer": observer,
            "acknowledged": True,
        }

    def _handle_garden(self, observer: str) -> dict[str, Any]:
        """Handle self.soul.garden - garden summary."""
        # Return garden summary if available
        return {
            "status": "accessible",
            "paths": ["self.soul.garden.plant", "self.soul.garden.nurture"],
        }

    def _eigenvector_graph(self) -> dict[str, list[str]]:
        """Generate eigenvector relationship graph."""
        return {
            "aesthetic": ["categorical", "generativity"],
            "categorical": ["aesthetic", "heterarchy"],
            "gratitude": ["joy", "generativity"],
            "heterarchy": ["categorical", "joy"],
            "generativity": ["aesthetic", "gratitude"],
            "joy": ["gratitude", "heterarchy"],
        }

    def _dominant_eigenvector(self) -> str:
        """Find the dominant eigenvector by confidence."""
        ev = self._soul.eigenvectors
        coords = [
            ("aesthetic", ev.aesthetic.confidence),
            ("categorical", ev.categorical.confidence),
            ("gratitude", ev.gratitude.confidence),
            ("heterarchy", ev.heterarchy.confidence),
            ("generativity", ev.generativity.confidence),
            ("joy", ev.joy.confidence),
        ]
        return max(coords, key=lambda x: x[1])[0]


# =============================================================================
# Domain 6: Error Experience
# =============================================================================


class SoulErrorSeverity(str, Enum):
    """Severity levels for soul errors."""

    WHISPER = "whisper"  # Minor issue, continue
    CONCERN = "concern"  # Notable issue, may need attention
    CRISIS = "crisis"  # Significant issue, needs attention
    CATASTROPHE = "catastrophe"  # Critical failure


@dataclass
class SoulError(Exception):
    """
    Base error class for K-gent soul errors.

    Philosophy: Errors should feel human, not robotic.
    They should guide, not blame.
    """

    message: str
    severity: SoulErrorSeverity = SoulErrorSeverity.CONCERN
    context: dict[str, Any] = field(default_factory=dict)
    suggestion: Optional[str] = None
    recovery_hint: Optional[str] = None

    def __str__(self) -> str:
        """Format error message."""
        return self.format_human()

    def format_human(self) -> str:
        """Format error for human consumption."""
        lines = [f"[{self.severity.value.upper()}] {self.message}"]

        if self.suggestion:
            lines.append(f"  Suggestion: {self.suggestion}")

        if self.recovery_hint:
            lines.append(f"  Recovery: {self.recovery_hint}")

        return "\n".join(lines)

    def format_technical(self) -> str:
        """Format error for technical logs."""
        return f"{self.severity.value}:{self.__class__.__name__}:{self.message}:{self.context}"


class DialogueError(SoulError):
    """Error in dialogue processing."""

    def __init__(self, message: str, mode: Optional[str] = None) -> None:
        """Initialize dialogue error."""
        super().__init__(
            message=message,
            severity=SoulErrorSeverity.CONCERN,
            context={"mode": mode},
            suggestion="Try rephrasing your question",
            recovery_hint="The dialogue can continue after this",
        )


class EigenvectorError(SoulError):
    """Error in eigenvector processing."""

    def __init__(self, message: str, eigenvector: str) -> None:
        """Initialize eigenvector error."""
        super().__init__(
            message=message,
            severity=SoulErrorSeverity.WHISPER,
            context={"eigenvector": eigenvector},
            suggestion="Eigenvector will use default confidence",
            recovery_hint="This typically self-corrects over time",
        )


class GardenError(SoulError):
    """Error in persona garden."""

    def __init__(self, message: str, entry_id: Optional[str] = None) -> None:
        """Initialize garden error."""
        super().__init__(
            message=message,
            severity=SoulErrorSeverity.CONCERN,
            context={"entry_id": entry_id},
            suggestion="Check if the garden entry exists",
            recovery_hint="Garden state is preserved - try again",
        )


class HypnagogiaError(SoulError):
    """Error in hypnagogia/dream processing."""

    def __init__(self, message: str, phase: Optional[str] = None) -> None:
        """Initialize hypnagogia error."""
        super().__init__(
            message=message,
            severity=SoulErrorSeverity.CONCERN,
            context={"phase": phase},
            suggestion="Dream cycle can be retried",
            recovery_hint="Patterns are preserved even on dream failure",
        )


class GracefulDegradation:
    """
    Graceful degradation handler for K-gent.

    When things go wrong, degrade gracefully rather than crash.
    """

    def __init__(self) -> None:
        """Initialize degradation handler."""
        self._degraded_features: set[str] = set()
        self._error_count: dict[str, int] = {}

    def record_error(self, feature: str, error: Exception) -> None:
        """Record an error for a feature."""
        self._error_count[feature] = self._error_count.get(feature, 0) + 1

        # Auto-degrade after 3 errors
        if self._error_count[feature] >= 3:
            self._degraded_features.add(feature)

    def is_degraded(self, feature: str) -> bool:
        """Check if a feature is degraded."""
        return feature in self._degraded_features

    def restore(self, feature: str) -> bool:
        """Attempt to restore a degraded feature."""
        if feature in self._degraded_features:
            self._degraded_features.remove(feature)
            self._error_count[feature] = 0
            return True
        return False

    def status(self) -> dict[str, Any]:
        """Get degradation status."""
        return {
            "degraded_features": list(self._degraded_features),
            "error_counts": dict(self._error_count),
        }


# =============================================================================
# Domain 7: Deferred Capabilities
# =============================================================================


@dataclass
class FractalNode:
    """A node in the fractal expansion tree."""

    content: str
    depth: int
    children: list["FractalNode"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "content": self.content,
            "depth": self.depth,
            "children": [c.to_dict() for c in self.children],
            "metadata": self.metadata,
        }


class FractalExpander:
    """
    Fractal expansion of ideas.

    Takes a seed idea and recursively expands it into
    a tree of related concepts, each at increasing depth
    of specificity.
    """

    def __init__(self, max_depth: int = 3, branching_factor: int = 3) -> None:
        """Initialize expander."""
        self._max_depth = max_depth
        self._branching_factor = branching_factor

    async def expand(
        self,
        seed: str,
        soul: Optional["KgentSoul"] = None,
    ) -> FractalNode:
        """
        Expand a seed idea into a fractal tree.

        Args:
            seed: The seed idea to expand
            soul: Optional soul for eigenvector-aware expansion

        Returns:
            FractalNode tree
        """
        root = FractalNode(content=seed, depth=0)
        await self._expand_recursive(root, soul)
        return root

    async def _expand_recursive(
        self,
        node: FractalNode,
        soul: Optional["KgentSoul"],
    ) -> None:
        """Recursively expand a node."""
        if node.depth >= self._max_depth:
            return

        # Generate child concepts (heuristic for now)
        children = self._generate_children(node.content, soul)

        for child_content in children[: self._branching_factor]:
            child = FractalNode(
                content=child_content,
                depth=node.depth + 1,
            )
            node.children.append(child)
            await self._expand_recursive(child, soul)

    def _generate_children(
        self,
        content: str,
        soul: Optional["KgentSoul"],
    ) -> list[str]:
        """Generate child concepts from content."""
        # Simple heuristic expansion
        expansions = [
            f"How does {content} apply to code?",
            f"What is the opposite of {content}?",
            f"A concrete example of {content}",
        ]

        # Eigenvector-influenced expansion
        if soul:
            ev = soul.eigenvectors
            if ev.aesthetic.confidence > 0.7:
                expansions.append(f"The minimal essence of {content}")
            if ev.categorical.confidence > 0.7:
                expansions.append(f"The category of {content}")
            if ev.joy.confidence > 0.7:
                expansions.append(f"The joy in {content}")

        return expansions


@dataclass
class ConstitutionArticle:
    """An article in the holographic constitution."""

    number: int
    title: str
    content: str
    eigenvector_weights: dict[str, float] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "eigenvector_weights": self.eigenvector_weights,
            "examples": self.examples,
        }


class HolographicConstitution:
    """
    Holographic constitution for K-gent.

    Like a hologram, every article contains the whole.
    Each principle reflects all others.
    """

    def __init__(self) -> None:
        """Initialize constitution."""
        self._articles: list[ConstitutionArticle] = []
        self._init_articles()

    def _init_articles(self) -> None:
        """Initialize the constitutional articles."""
        self._articles = [
            ConstitutionArticle(
                number=1,
                title="Minimalism",
                content="Say no more than yes. Delete before adding. Compress, don't expand.",
                eigenvector_weights={"aesthetic": 0.9, "categorical": 0.6},
                examples=[
                    "Prefer 3 lines over 30",
                    "Remove before refactoring",
                ],
            ),
            ConstitutionArticle(
                number=2,
                title="Composability",
                content="Agents are morphisms. Composition is primary. No hidden state.",
                eigenvector_weights={"categorical": 0.9, "heterarchy": 0.7},
                examples=[
                    "f >> g over f(g(x))",
                    "Dependency injection over singletons",
                ],
            ),
            ConstitutionArticle(
                number=3,
                title="Gratitude",
                content="Acknowledge the Accursed Share. Pay your tithe. Sacred over utilitarian.",
                eigenvector_weights={"gratitude": 0.9, "joy": 0.6},
                examples=[
                    "Credit your sources",
                    "Entropy has a price",
                ],
            ),
            ConstitutionArticle(
                number=4,
                title="Heterarchy",
                content="Forest over King. Peer-to-peer. No permanent orchestrator.",
                eigenvector_weights={"heterarchy": 0.9, "generativity": 0.5},
                examples=[
                    "Agents negotiate, don't command",
                    "Roles are dynamic, not fixed",
                ],
            ),
            ConstitutionArticle(
                number=5,
                title="Generativity",
                content="Spec compresses implementation. Generate, don't hand-write.",
                eigenvector_weights={"generativity": 0.9, "aesthetic": 0.5},
                examples=[
                    "One spec, many implementations",
                    "Derive when possible",
                ],
            ),
            ConstitutionArticle(
                number=6,
                title="Joy",
                content="Fun is free. Warmth over coldness. Personality matters.",
                eigenvector_weights={"joy": 0.9, "gratitude": 0.6},
                examples=[
                    "Delight in the work",
                    "Code can be playful",
                ],
            ),
        ]

    def get_article(self, number: int) -> Optional[ConstitutionArticle]:
        """Get article by number."""
        for article in self._articles:
            if article.number == number:
                return article
        return None

    def get_by_eigenvector(self, eigenvector: str) -> list[ConstitutionArticle]:
        """Get articles weighted by an eigenvector."""
        weighted = [
            (a, a.eigenvector_weights.get(eigenvector, 0)) for a in self._articles
        ]
        weighted.sort(key=lambda x: -x[1])
        return [a for a, w in weighted if w > 0]

    def holographic_lookup(
        self,
        query: str,
        soul: Optional["KgentSoul"] = None,
    ) -> list[ConstitutionArticle]:
        """
        Holographic lookup - find articles that resonate with query.

        Each article contains echoes of all others, so related
        articles amplify each other.
        """
        # Simple keyword matching
        query_lower = query.lower()
        scores: dict[int, float] = {}

        for article in self._articles:
            score = 0.0
            if article.title.lower() in query_lower:
                score += 1.0
            for word in query_lower.split():
                if word in article.content.lower():
                    score += 0.2

            # Eigenvector amplification
            if soul:
                for eigen, weight in article.eigenvector_weights.items():
                    ev = getattr(soul.eigenvectors, eigen, None)
                    if ev:
                        score += ev.confidence * weight * 0.3

            if score > 0:
                scores[article.number] = score

        # Sort by score
        sorted_numbers = sorted(scores.keys(), key=lambda n: -scores[n])
        result: list[ConstitutionArticle] = []
        for n in sorted_numbers:
            fetched = self.get_article(n)
            if fetched is not None:
                result.append(fetched)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize constitution."""
        return {
            "articles": [a.to_dict() for a in self._articles],
            "version": "1.0",
        }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Domain 5: AGENTESE Paths
    "SoulPath",
    "SoulPathResult",
    "SoulPathResolver",
    # Domain 6: Error Experience
    "SoulErrorSeverity",
    "SoulError",
    "DialogueError",
    "EigenvectorError",
    "GardenError",
    "HypnagogiaError",
    "GracefulDegradation",
    # Domain 7: Deferred Capabilities
    "FractalNode",
    "FractalExpander",
    "ConstitutionArticle",
    "HolographicConstitution",
]
