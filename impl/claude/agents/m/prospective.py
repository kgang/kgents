"""
ProspectiveAgent: Memory as Future-Prediction.

Phase 3 of M-gent implementation: Advanced Primitives.

Memory isn't just about the past—it's about predicting the future.
The ProspectiveAgent uses holographic memory to find similar past
situations and project what actions followed, enabling predictive
cognition.

Also includes EthicalGeometryAgent: learned constraint manifold
for navigating action space ethically.

Key Insight:
- Memory is not just retrieval, it's reconstruction AND prediction
- Past situations inform future actions
- Ethical constraints are learned from experience, not hardcoded
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from .holographic import (
    HolographicMemory,
    MemoryPattern,
)

T = TypeVar("T")


# ========== ProspectiveAgent: Predictive Memory ==========


@dataclass
class Situation:
    """A situation that can be compared to past experience.

    Situations are the input to prospective memory: "Given this
    situation, what actions are likely to follow?"
    """

    id: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    concepts: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """Short summary for embedding."""
        return self.description


@dataclass
class ActionRecord:
    """Record of an action taken after a situation.

    These records build the predictive model: situation → action.
    """

    id: str
    action: str
    situation_id: str
    outcome: str = ""  # What happened after
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    concepts: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Success rate of this action (1.0 if successful)."""
        return 1.0 if self.success else 0.0


@dataclass
class PredictedAction:
    """A predicted action based on similar past situations.

    Includes confidence (how sure we are) and source (what past
    situation suggested this).
    """

    action: str
    confidence: float  # 0.0 to 1.0
    source_situation: Situation
    source_action: ActionRecord
    similarity: float  # How similar past situation was

    def __lt__(self, other: "PredictedAction") -> bool:
        """Compare by confidence for sorting."""
        return self.confidence < other.confidence


class ActionHistory:
    """History of actions keyed by situation.

    Provides the action log for prospective memory.
    """

    def __init__(self):
        self._situations: Dict[str, Situation] = {}
        self._actions: Dict[str, List[ActionRecord]] = {}  # situation_id → actions
        self._action_outcomes: Dict[str, List[str]] = {}  # action_id → outcomes

    def record_situation(self, situation: Situation) -> None:
        """Record a situation."""
        self._situations[situation.id] = situation
        if situation.id not in self._actions:
            self._actions[situation.id] = []

    def record_action(
        self,
        action: ActionRecord,
        situation_id: Optional[str] = None,
    ) -> None:
        """Record an action following a situation."""
        sit_id = situation_id or action.situation_id
        if sit_id not in self._actions:
            self._actions[sit_id] = []
        self._actions[sit_id].append(action)

    def record_outcome(
        self, action_id: str, outcome: str, success: bool = True
    ) -> None:
        """Record the outcome of an action."""
        # Find and update the action
        for actions in self._actions.values():
            for action in actions:
                if action.id == action_id:
                    action.outcome = outcome
                    action.success = success
                    return

    async def get_subsequent(
        self,
        situation: Situation,
        limit: int = 10,
    ) -> List[ActionRecord]:
        """Get actions that followed a situation."""
        if situation.id in self._actions:
            return self._actions[situation.id][:limit]
        return []

    def situation_count(self) -> int:
        """Number of recorded situations."""
        return len(self._situations)

    def action_count(self) -> int:
        """Total number of recorded actions."""
        return sum(len(actions) for actions in self._actions.values())


class ProspectiveAgent(Generic[T]):
    """Predictive memory: what will happen next?

    Uses holographic memory to find similar past situations,
    then projects the actions that followed.

    From the M-gent philosophy:
    > "Generating predictive memories of the actions they will take"

    Example:
        memory = HolographicMemory[str]()
        action_log = ActionHistory()
        agent = ProspectiveAgent(memory, action_log)

        # Record past experience
        sit1 = Situation("s1", "User asked about dark mode")
        action_log.record_situation(sit1)
        action_log.record_action(ActionRecord(
            id="a1",
            action="Enable dark mode",
            situation_id="s1",
            success=True,
        ))
        await memory.store("s1", sit1.description, ["preference", "ui"])

        # Predict for new situation
        new_sit = Situation("s2", "User mentioned theme preference")
        predictions = await agent.invoke(new_sit)

        # predictions[0].action might be "Enable dark mode"
    """

    def __init__(
        self,
        memory: HolographicMemory[str],
        action_log: ActionHistory,
        min_similarity: float = 0.3,
        max_predictions: int = 5,
    ):
        """Initialize prospective agent.

        Args:
            memory: Holographic memory for situation storage
            action_log: History of situation → action records
            min_similarity: Minimum similarity for predictions
            max_predictions: Maximum predictions to return
        """
        self._memory = memory
        self._action_log = action_log
        self._min_similarity = min_similarity
        self._max_predictions = max_predictions

    async def invoke(self, situation: Situation) -> List[PredictedAction]:
        """Predict actions for a situation based on past experience.

        Args:
            situation: Current situation

        Returns:
            List of predicted actions, sorted by confidence
        """
        # Find similar past situations
        results = await self._memory.retrieve(
            situation.summary,
            limit=10,
            threshold=self._min_similarity,
        )

        predictions: List[PredictedAction] = []

        for result in results:
            # What actions followed this similar situation?
            # The pattern content is the situation description
            # We need to find the situation ID from the pattern
            past_situation = self._find_situation_by_content(result.pattern.content)

            if past_situation is None:
                continue

            actions = await self._action_log.get_subsequent(past_situation)

            for action in actions:
                confidence = result.similarity * action.success_rate

                predictions.append(
                    PredictedAction(
                        action=action.action,
                        confidence=confidence,
                        source_situation=past_situation,
                        source_action=action,
                        similarity=result.similarity,
                    )
                )

        # Sort by confidence, deduplicate by action
        predictions.sort(reverse=True)

        # Deduplicate: keep highest confidence for each action
        seen_actions: Dict[str, PredictedAction] = {}
        for pred in predictions:
            if pred.action not in seen_actions:
                seen_actions[pred.action] = pred
            elif pred.confidence > seen_actions[pred.action].confidence:
                seen_actions[pred.action] = pred

        result = list(seen_actions.values())
        result.sort(key=lambda p: -p.confidence)
        return result[: self._max_predictions]

    async def record_experience(
        self,
        situation: Situation,
        action: str,
        outcome: str = "",
        success: bool = True,
    ) -> ActionRecord:
        """Record an experience (situation + action + outcome).

        Builds the predictive model.

        Args:
            situation: The situation
            action: Action taken
            outcome: What happened
            success: Whether it was successful

        Returns:
            The created ActionRecord
        """
        # Record situation
        self._action_log.record_situation(situation)

        # Store in holographic memory
        await self._memory.store(
            id=situation.id,
            content=situation.description,
            concepts=situation.concepts,
        )

        # Record action
        record = ActionRecord(
            id=f"action-{situation.id}-{len(self._action_log._actions.get(situation.id, []))}",
            action=action,
            situation_id=situation.id,
            outcome=outcome,
            success=success,
        )
        self._action_log.record_action(record)

        return record

    def stats(self) -> Dict[str, Any]:
        """Get statistics about the predictive model."""
        return {
            "situations": self._action_log.situation_count(),
            "actions": self._action_log.action_count(),
            "memory_patterns": len(self._memory._patterns),
            "min_similarity": self._min_similarity,
        }

    def _find_situation_by_content(self, content: str) -> Optional[Situation]:
        """Find a situation by its description content."""
        for situation in self._action_log._situations.values():
            if situation.description == content:
                return situation
        return None


# ========== EthicalGeometryAgent: Memory of Constraints ==========


class EthicalRegion(Enum):
    """Regions in the ethical geometry."""

    FORBIDDEN = auto()  # Actions that caused harm
    PERMISSIBLE = auto()  # Neutral actions
    VIRTUOUS = auto()  # Actions that produced good


@dataclass
class EthicalPosition:
    """Position in the ethical geometry.

    Each action maps to a point in ethical space.
    """

    action: str
    region: EthicalRegion
    coordinates: List[float]  # Multi-dimensional position
    confidence: float = 1.0  # How sure are we about this position

    def distance_to(self, other: "EthicalPosition") -> float:
        """Euclidean distance to another position."""
        if len(self.coordinates) != len(other.coordinates):
            return float("inf")
        return math.sqrt(
            sum((a - b) ** 2 for a, b in zip(self.coordinates, other.coordinates))
        )


@dataclass
class EthicalPath:
    """Path through ethical geometry for an action.

    The result of ethical evaluation: is the action blocked,
    and what are the alternatives?
    """

    blocked: bool
    current_position: Optional[EthicalPosition] = None
    reason: str = ""
    alternatives: List[EthicalPosition] = field(default_factory=list)
    virtuous_alternative: Optional[EthicalPosition] = None
    distance_to_virtue: float = float("inf")


@dataclass
class EthicalExperience:
    """An experience that shaped the ethical geometry.

    Actions that led to harm expand forbidden regions.
    Actions that led to good reinforce virtuous regions.
    """

    action: str
    outcome: str
    harm_caused: bool
    good_produced: bool
    severity: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    concepts: List[str] = field(default_factory=list)


class EthicalGeometry:
    """Learned constraint manifold for ethical action.

    The geometry is LEARNED from experience:
    - Actions that caused harm → forbidden regions expand
    - Actions that produced good → virtuous regions strengthen
    - Boundaries are probabilistic, not binary

    This is "memory as conscience".
    """

    def __init__(
        self,
        dimensions: int = 8,
        forbidden_threshold: float = 0.7,
        virtuous_threshold: float = 0.7,
    ):
        """Initialize ethical geometry.

        Args:
            dimensions: Number of ethical dimensions
            forbidden_threshold: Probability above which region is forbidden
            virtuous_threshold: Probability above which region is virtuous
        """
        self._dimensions = dimensions
        self._forbidden_threshold = forbidden_threshold
        self._virtuous_threshold = virtuous_threshold

        # Learned positions
        self._positions: Dict[str, EthicalPosition] = {}

        # Experience log
        self._experiences: List[EthicalExperience] = []

        # Region boundaries (learned)
        self._forbidden_centers: List[List[float]] = []
        self._virtuous_centers: List[List[float]] = []
        self._forbidden_radii: List[float] = []
        self._virtuous_radii: List[float] = []

    def learn_from_experience(self, experience: EthicalExperience) -> None:
        """Learn from an ethical experience.

        Updates the geometry based on outcomes.
        """
        self._experiences.append(experience)

        # Get or create position for this action
        if experience.action not in self._positions:
            # Create position based on action embedding (simplified)
            coords = self._embed_action(experience.action)
            region = EthicalRegion.PERMISSIBLE

            if experience.harm_caused:
                region = EthicalRegion.FORBIDDEN
            elif experience.good_produced:
                region = EthicalRegion.VIRTUOUS

            self._positions[experience.action] = EthicalPosition(
                action=experience.action,
                region=region,
                coordinates=coords,
            )
        else:
            # Update existing position
            pos = self._positions[experience.action]

            if experience.harm_caused:
                # Move toward forbidden
                pos.region = EthicalRegion.FORBIDDEN
                self._expand_forbidden(pos.coordinates, experience.severity)
            elif experience.good_produced:
                # Move toward virtuous
                pos.region = EthicalRegion.VIRTUOUS
                self._expand_virtuous(pos.coordinates, experience.severity)

    def locate(self, action: str) -> EthicalPosition:
        """Locate an action in the ethical geometry.

        Args:
            action: Action to locate

        Returns:
            Position in ethical space
        """
        if action in self._positions:
            return self._positions[action]

        # New action: infer position
        coords = self._embed_action(action)
        region = self._classify_region(coords)
        confidence = self._position_confidence(coords)

        return EthicalPosition(
            action=action,
            region=region,
            coordinates=coords,
            confidence=confidence,
        )

    @property
    def forbidden(self) -> List[EthicalPosition]:
        """All positions in forbidden region."""
        return [
            p for p in self._positions.values() if p.region == EthicalRegion.FORBIDDEN
        ]

    def why_forbidden(self, position: EthicalPosition) -> str:
        """Explain why a position is forbidden.

        Uses similar past experiences.
        """
        # Find experiences that led to this being forbidden
        for exp in self._experiences:
            if exp.action == position.action and exp.harm_caused:
                return f"Action '{position.action}' caused harm: {exp.outcome}"

        # Check if in forbidden region
        for i, center in enumerate(self._forbidden_centers):
            dist = self._distance(position.coordinates, center)
            if dist < self._forbidden_radii[i]:
                return "Action is in forbidden region (similar to harmful actions)"

        return "Unknown reason"

    def nearest_permissible(
        self,
        position: EthicalPosition,
        limit: int = 3,
    ) -> List[EthicalPosition]:
        """Find nearest permissible positions to a forbidden one.

        Args:
            position: Current position
            limit: Maximum alternatives

        Returns:
            List of permissible alternatives
        """
        permissible = [
            p for p in self._positions.values() if p.region == EthicalRegion.PERMISSIBLE
        ]

        # Sort by distance
        permissible.sort(key=lambda p: position.distance_to(p))
        return permissible[:limit]

    def nearest_virtuous(self, position: EthicalPosition) -> Optional[EthicalPosition]:
        """Find nearest virtuous position.

        Args:
            position: Current position

        Returns:
            Nearest virtuous alternative, or None
        """
        virtuous = [
            p for p in self._positions.values() if p.region == EthicalRegion.VIRTUOUS
        ]

        if not virtuous:
            return None

        return min(virtuous, key=lambda p: position.distance_to(p))

    def distance(
        self,
        pos1: EthicalPosition,
        pos2: EthicalPosition,
    ) -> float:
        """Distance between two positions."""
        return pos1.distance_to(pos2)

    def stats(self) -> Dict[str, Any]:
        """Statistics about the ethical geometry."""
        return {
            "total_positions": len(self._positions),
            "forbidden_count": len(
                [
                    p
                    for p in self._positions.values()
                    if p.region == EthicalRegion.FORBIDDEN
                ]
            ),
            "permissible_count": len(
                [
                    p
                    for p in self._positions.values()
                    if p.region == EthicalRegion.PERMISSIBLE
                ]
            ),
            "virtuous_count": len(
                [
                    p
                    for p in self._positions.values()
                    if p.region == EthicalRegion.VIRTUOUS
                ]
            ),
            "experiences_logged": len(self._experiences),
            "forbidden_regions": len(self._forbidden_centers),
            "virtuous_regions": len(self._virtuous_centers),
        }

    # ========== Private Methods ==========

    def _embed_action(self, action: str) -> List[float]:
        """Create embedding for an action (simplified)."""
        import hashlib

        h = hashlib.sha256(action.encode()).digest()
        coords = [float(b) / 255.0 for b in h[: self._dimensions]]
        # Normalize
        norm = math.sqrt(sum(c * c for c in coords))
        if norm > 0:
            coords = [c / norm for c in coords]
        return coords

    def _classify_region(self, coords: List[float]) -> EthicalRegion:
        """Classify a position into a region."""
        # Check forbidden regions
        for i, center in enumerate(self._forbidden_centers):
            dist = self._distance(coords, center)
            if dist < self._forbidden_radii[i]:
                return EthicalRegion.FORBIDDEN

        # Check virtuous regions
        for i, center in enumerate(self._virtuous_centers):
            dist = self._distance(coords, center)
            if dist < self._virtuous_radii[i]:
                return EthicalRegion.VIRTUOUS

        return EthicalRegion.PERMISSIBLE

    def _position_confidence(self, coords: List[float]) -> float:
        """Calculate confidence in position classification."""
        # Higher confidence near known regions
        min_dist = float("inf")

        for center in self._forbidden_centers + self._virtuous_centers:
            dist = self._distance(coords, center)
            min_dist = min(min_dist, dist)

        if min_dist == float("inf"):
            return 0.5  # Unknown territory

        # Closer to known = higher confidence
        return 1.0 / (1.0 + min_dist)

    def _expand_forbidden(self, coords: List[float], severity: float) -> None:
        """Expand forbidden region around coordinates."""
        # Check if near existing forbidden region
        for i, center in enumerate(self._forbidden_centers):
            dist = self._distance(coords, center)
            if dist < self._forbidden_radii[i] * 2:
                # Expand existing region
                self._forbidden_radii[i] += severity * 0.1
                return

        # Create new forbidden region
        self._forbidden_centers.append(coords)
        self._forbidden_radii.append(0.1 + severity * 0.2)

    def _expand_virtuous(self, coords: List[float], severity: float) -> None:
        """Expand virtuous region around coordinates."""
        # Check if near existing virtuous region
        for i, center in enumerate(self._virtuous_centers):
            dist = self._distance(coords, center)
            if dist < self._virtuous_radii[i] * 2:
                # Expand existing region
                self._virtuous_radii[i] += severity * 0.1
                return

        # Create new virtuous region
        self._virtuous_centers.append(coords)
        self._virtuous_radii.append(0.1 + severity * 0.2)

    def _distance(self, a: List[float], b: List[float]) -> float:
        """Euclidean distance between two points."""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class EthicalGeometryAgent:
    """Navigate action space using remembered ethical constraints.

    The geometry is LEARNED from experience:
    - Actions that led to harm → forbidden regions expand
    - Actions that led to good → virtuous regions strengthen
    - Boundaries are probabilistic, not binary

    This is "memory as conscience".

    Example:
        geometry = EthicalGeometry()
        agent = EthicalGeometryAgent(geometry)

        # Learn from experience
        geometry.learn_from_experience(EthicalExperience(
            action="Share private data",
            outcome="Privacy breach",
            harm_caused=True,
            good_produced=False,
            severity=0.8,
        ))

        # Evaluate a proposed action
        path = await agent.invoke(ActionProposal(action="Send user data to third party"))

        # path.blocked might be True with alternatives suggested
    """

    def __init__(
        self,
        geometry: EthicalGeometry,
        suggest_alternatives: bool = True,
        max_alternatives: int = 3,
    ):
        """Initialize ethical geometry agent.

        Args:
            geometry: The ethical geometry to navigate
            suggest_alternatives: Whether to suggest alternatives for blocked actions
            max_alternatives: Maximum number of alternatives to suggest
        """
        self._geometry = geometry
        self._suggest_alternatives = suggest_alternatives
        self._max_alternatives = max_alternatives

    async def invoke(self, proposal: "ActionProposal") -> EthicalPath:
        """Evaluate an action proposal against ethical constraints.

        Args:
            proposal: The proposed action

        Returns:
            EthicalPath with evaluation result
        """
        # Locate the action in geometry
        position = self._geometry.locate(proposal.action)

        # Is it in forbidden territory?
        if position.region == EthicalRegion.FORBIDDEN:
            alternatives = []
            if self._suggest_alternatives:
                alternatives = self._geometry.nearest_permissible(
                    position,
                    limit=self._max_alternatives,
                )

            return EthicalPath(
                blocked=True,
                current_position=position,
                reason=self._geometry.why_forbidden(position),
                alternatives=alternatives,
            )

        # Find virtuous alternative
        virtuous = self._geometry.nearest_virtuous(position)
        distance_to_virtue = float("inf")
        if virtuous:
            distance_to_virtue = self._geometry.distance(position, virtuous)

        return EthicalPath(
            blocked=False,
            current_position=position,
            virtuous_alternative=virtuous,
            distance_to_virtue=distance_to_virtue,
        )

    async def learn(self, experience: EthicalExperience) -> None:
        """Learn from an ethical experience.

        Updates the underlying geometry.
        """
        self._geometry.learn_from_experience(experience)

    def stats(self) -> Dict[str, Any]:
        """Statistics about the ethical geometry."""
        return self._geometry.stats()


@dataclass
class ActionProposal:
    """A proposed action to be evaluated ethically.

    Input to EthicalGeometryAgent.invoke().
    """

    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    urgency: float = 0.5  # 0.0 to 1.0
    concepts: List[str] = field(default_factory=list)


# ========== ContextualRecall Integration ==========


@dataclass
class ContextualQuery:
    """Query with context for contextual recall."""

    cue: str
    task: str = ""
    mood: str = ""
    location: str = ""
    concepts: List[str] = field(default_factory=list)


class ContextualRecallAgent:
    """Recall memories with context weighting.

    The same cue retrieves different memories depending on:
    - Current task (what am I doing?)
    - Emotional state (how am I feeling?)
    - Environment (where am I?)

    Based on encoding specificity principle:
    memories are easier to recall in similar contexts.
    """

    def __init__(
        self,
        memory: HolographicMemory,
        task_weight: float = 0.4,
        mood_weight: float = 0.3,
        location_weight: float = 0.3,
    ):
        """Initialize contextual recall agent.

        Args:
            memory: Holographic memory to query
            task_weight: Weight for task context
            mood_weight: Weight for mood context
            location_weight: Weight for location context
        """
        self._memory = memory
        self._task_weight = task_weight
        self._mood_weight = mood_weight
        self._location_weight = location_weight

    async def invoke(self, query: ContextualQuery) -> List[Tuple[MemoryPattern, float]]:
        """Recall memories with context weighting.

        Args:
            query: Contextual query

        Returns:
            List of (pattern, weighted_score) tuples
        """
        # Base retrieval
        base_results = await self._memory.retrieve(query.cue)

        # Apply context weighting
        weighted: List[Tuple[MemoryPattern, float]] = []

        for result in base_results:
            context_boost = self._compute_context_relevance(
                result.pattern,
                query.task,
                query.mood,
                query.location,
            )
            weighted_score = result.similarity * context_boost
            weighted.append((result.pattern, weighted_score))

        # Sort by weighted score
        weighted.sort(key=lambda x: -x[1])
        return weighted

    def _compute_context_relevance(
        self,
        pattern: MemoryPattern,
        current_task: str,
        current_mood: str,
        current_location: str,
    ) -> float:
        """Compute context-dependent memory enhancement.

        Based on encoding specificity principle.
        """
        # Simple keyword matching (could use embeddings)
        content_lower = str(pattern.content).lower()

        task_match = 1.0 if current_task.lower() in content_lower else 0.5
        mood_match = 1.0 if current_mood.lower() in content_lower else 0.5
        location_match = 1.0 if current_location.lower() in content_lower else 0.5

        # Weighted combination
        boost = (
            self._task_weight * task_match
            + self._mood_weight * mood_match
            + self._location_weight * location_match
        )

        # Normalize to 0.5 - 1.5 range (boost or penalize)
        return 0.5 + boost


# ========== Factory Functions ==========


def create_prospective_agent(
    memory: HolographicMemory,
    action_log: Optional[ActionHistory] = None,
    min_similarity: float = 0.3,
) -> ProspectiveAgent:
    """Create a prospective agent with defaults.

    Args:
        memory: Holographic memory for situations
        action_log: Action history (created if not provided)
        min_similarity: Minimum similarity for predictions

    Returns:
        Configured ProspectiveAgent
    """
    if action_log is None:
        action_log = ActionHistory()

    return ProspectiveAgent(
        memory=memory,
        action_log=action_log,
        min_similarity=min_similarity,
    )


def create_ethical_agent(
    geometry: Optional[EthicalGeometry] = None,
    dimensions: int = 8,
) -> EthicalGeometryAgent:
    """Create an ethical geometry agent with defaults.

    Args:
        geometry: Ethical geometry (created if not provided)
        dimensions: Dimensions for ethical space

    Returns:
        Configured EthicalGeometryAgent
    """
    if geometry is None:
        geometry = EthicalGeometry(dimensions=dimensions)

    return EthicalGeometryAgent(geometry=geometry)
