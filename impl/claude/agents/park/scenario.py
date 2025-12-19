"""
ScenarioTemplate: Structured Scenarios for Punchdrunk Park.

A scenario is a pre-designed situation with:
- Citizens with specific archetypes and eigenvectors
- A trigger condition that starts the action
- Success criteria that define completion

The Five Scenario Types:
- MYSTERY: Information asymmetry, deduction, revelation
- COLLABORATION: Joint problem-solving, resource pooling
- CONFLICT: Competing interests, negotiation, resolution
- EMERGENCE: Open-ended exploration, emergent behavior
- PRACTICE: Skill development, rehearsal, coaching

Design Philosophy:
    Scenarios are not scripts. They provide initial conditions
    and success criteria; what happens in between is emergent.
    Like Punchdrunk's Sleep No More, participants create meaning
    through movement and encounter.

Heritage:
- PUNCHDRUNK: Immersive theater, environmental storytelling
- SIMULACRA: Generative agents with memory streams
- AGENT HOSPITAL: Domain-specific roleplay scenarios

See: spec/protocols/park.md, Crown Jewel #4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable
from uuid import uuid4

from agents.town.citizen import Citizen, Cosmotechnics, Eigenvectors

# =============================================================================
# Scenario Types
# =============================================================================


class ScenarioType(Enum):
    """
    The five scenario types for Punchdrunk Park.

    Each type represents a different narrative structure and
    interaction pattern. The type determines:
    - Valid trigger conditions
    - Success criteria patterns
    - Default citizen configurations
    """

    MYSTERY = auto()  # Information asymmetry, deduction
    COLLABORATION = auto()  # Joint problem-solving
    CONFLICT = auto()  # Competing interests
    EMERGENCE = auto()  # Open-ended exploration
    PRACTICE = auto()  # Skill development


# =============================================================================
# Citizen Spec (for scenario definition)
# =============================================================================


@dataclass
class CitizenSpec:
    """
    Specification for a citizen in a scenario.

    This is the blueprint, not the instantiated citizen.
    Each spec can produce multiple citizens with variance.
    """

    name: str
    archetype: str
    region: str
    eigenvectors: Eigenvectors = field(default_factory=Eigenvectors)
    cosmotechnics: Cosmotechnics | None = None
    backstory: str = ""
    # Role-specific metadata (e.g., "has_the_secret" for mystery)
    metadata: dict[str, Any] = field(default_factory=dict)

    def spawn(self, id_prefix: str = "") -> Citizen:
        """
        Spawn an actual Citizen from this spec.

        Args:
            id_prefix: Optional prefix for citizen ID

        Returns:
            Instantiated Citizen
        """
        from agents.town.citizen import GATHERING

        citizen = Citizen(
            name=self.name,
            archetype=self.archetype,
            region=self.region,
            eigenvectors=self.eigenvectors,
            cosmotechnics=self.cosmotechnics or GATHERING,
        )
        if id_prefix:
            citizen.id = f"{id_prefix}-{citizen.id}"
        return citizen


# =============================================================================
# Trigger Conditions
# =============================================================================


@dataclass
class TriggerCondition:
    """
    Condition that starts a scenario.

    Triggers can be:
    - immediate: Start right away
    - time_based: Start at a specific time
    - event_based: Start when an event occurs
    - citizen_count: Start when N citizens are present
    """

    kind: str  # immediate, time_based, event_based, citizen_count
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def immediate(cls) -> TriggerCondition:
        """Create an immediate trigger."""
        return cls(kind="immediate")

    @classmethod
    def time_based(cls, delay_seconds: float) -> TriggerCondition:
        """Create a time-based trigger."""
        return cls(kind="time_based", params={"delay_seconds": delay_seconds})

    @classmethod
    def event_based(cls, event_type: str) -> TriggerCondition:
        """Create an event-based trigger."""
        return cls(kind="event_based", params={"event_type": event_type})

    @classmethod
    def citizen_count(cls, min_count: int) -> TriggerCondition:
        """Create a citizen count trigger."""
        return cls(kind="citizen_count", params={"min_count": min_count})

    def is_satisfied(self, context: dict[str, Any]) -> bool:
        """
        Check if the trigger condition is satisfied.

        Args:
            context: Current scenario context with keys like
                     "citizens", "time_elapsed", "events"

        Returns:
            True if trigger should fire
        """
        match self.kind:
            case "immediate":
                return True
            case "time_based":
                elapsed = context.get("time_elapsed", 0.0)
                return elapsed >= self.params.get("delay_seconds", 0.0)
            case "event_based":
                events = context.get("events", [])
                target = self.params.get("event_type")
                return any(e.get("type") == target for e in events)
            case "citizen_count":
                citizens = context.get("citizens", [])
                return len(citizens) >= self.params.get("min_count", 0)
            case _:
                return False


# =============================================================================
# Success Criteria
# =============================================================================


@dataclass
class SuccessCriterion:
    """
    A single success criterion for a scenario.

    Criteria have:
    - kind: The type of criterion
    - description: Human-readable explanation
    - checker: Function to evaluate completion
    """

    kind: str
    description: str
    params: dict[str, Any] = field(default_factory=dict)
    _checker: Callable[[dict[str, Any]], bool] | None = field(default=None, repr=False)

    def is_met(self, context: dict[str, Any]) -> bool:
        """Check if this criterion is met."""
        if self._checker:
            return self._checker(context)

        # Built-in criterion types
        match self.kind:
            case "citizen_interaction":
                # Check if specific citizens have interacted
                interactions = context.get("interactions", [])
                required = self.params.get("required_pairs", [])
                for pair in required:
                    if not any(
                        i.get("from") == pair[0] and i.get("to") == pair[1] for i in interactions
                    ):
                        return False
                return True

            case "information_revealed":
                # Check if information has been revealed
                revealed = context.get("revealed_info", set())
                required = set(self.params.get("required_info", []))
                return required.issubset(revealed)

            case "coalition_formed":
                # Check if a coalition was formed
                coalitions = context.get("coalitions", [])
                min_size = self.params.get("min_size", 2)
                return any(len(c.get("members", [])) >= min_size for c in coalitions)

            case "resource_pooled":
                # Check if resources were pooled
                pooled = context.get("pooled_resources", 0)
                threshold = self.params.get("threshold", 0)
                return pooled >= threshold

            case "consensus_reached":
                # Check if consensus was reached
                votes = context.get("votes", {})
                threshold = self.params.get("threshold", 0.5)
                if not votes:
                    return False
                majority = max(votes.values()) / sum(votes.values())
                return majority >= threshold

            case "time_elapsed":
                # Check if sufficient time has passed
                elapsed = context.get("time_elapsed", 0.0)
                min_time = self.params.get("min_seconds", 0.0)
                return elapsed >= min_time

            case "custom":
                # Custom checker must be provided
                return self._checker(context) if self._checker else False

            case _:
                return False


@dataclass
class SuccessCriteria:
    """
    Collection of success criteria for a scenario.

    Can require all criteria (AND) or any criteria (OR).
    """

    criteria: list[SuccessCriterion] = field(default_factory=list)
    require_all: bool = True

    def is_met(self, context: dict[str, Any]) -> bool:
        """Check if success criteria are met."""
        if not self.criteria:
            return False

        if self.require_all:
            return all(c.is_met(context) for c in self.criteria)
        else:
            return any(c.is_met(context) for c in self.criteria)

    def get_progress(self, context: dict[str, Any]) -> dict[str, bool]:
        """Get progress on each criterion."""
        return {c.description: c.is_met(context) for c in self.criteria}


# =============================================================================
# Scenario Template
# =============================================================================


@dataclass
class ScenarioTemplate:
    """
    A reusable template for scenarios.

    Templates define:
    - name: Human-readable name
    - scenario_type: One of the five types
    - citizens: List of CitizenSpecs to spawn
    - trigger: When the scenario activates
    - success_criteria: How to determine completion
    - regions: Physical spaces in the scenario
    - description: Flavor text for participants

    Templates are immutable blueprints. Scenarios are instances
    created from templates with specific citizen instantiations.
    """

    name: str
    scenario_type: ScenarioType
    citizens: list[CitizenSpec]
    trigger: TriggerCondition
    success_criteria: SuccessCriteria
    description: str = ""
    regions: list[str] = field(default_factory=list)
    # Polynomial state configuration
    polynomial_config: dict[str, Any] = field(default_factory=dict)
    # Metadata for discovery and filtering
    tags: list[str] = field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard
    estimated_duration_minutes: int = 30
    # Template ID for AGENTESE resolution
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)

    def spawn_citizens(self) -> list[Citizen]:
        """Spawn all citizens from specs."""
        return [spec.spawn(id_prefix=self.id) for spec in self.citizens]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage/API."""
        return {
            "id": self.id,
            "name": self.name,
            "scenario_type": self.scenario_type.name,
            "description": self.description,
            "citizens": [
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "region": c.region,
                    "backstory": c.backstory,
                    "eigenvectors": c.eigenvectors.to_dict(),
                    "metadata": c.metadata,
                }
                for c in self.citizens
            ],
            "trigger": {
                "kind": self.trigger.kind,
                "params": self.trigger.params,
            },
            "success_criteria": {
                "require_all": self.success_criteria.require_all,
                "criteria": [
                    {
                        "kind": c.kind,
                        "description": c.description,
                        "params": c.params,
                    }
                    for c in self.success_criteria.criteria
                ],
            },
            "regions": self.regions,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "estimated_duration_minutes": self.estimated_duration_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScenarioTemplate:
        """Deserialize from dictionary."""
        citizens = [
            CitizenSpec(
                name=c["name"],
                archetype=c["archetype"],
                region=c["region"],
                backstory=c.get("backstory", ""),
                eigenvectors=Eigenvectors.from_dict(c.get("eigenvectors", {})),
                metadata=c.get("metadata", {}),
            )
            for c in data.get("citizens", [])
        ]

        trigger_data = data.get("trigger", {})
        trigger = TriggerCondition(
            kind=trigger_data.get("kind", "immediate"),
            params=trigger_data.get("params", {}),
        )

        criteria_data = data.get("success_criteria", {})
        success_criteria = SuccessCriteria(
            require_all=criteria_data.get("require_all", True),
            criteria=[
                SuccessCriterion(
                    kind=c["kind"],
                    description=c["description"],
                    params=c.get("params", {}),
                )
                for c in criteria_data.get("criteria", [])
            ],
        )

        return cls(
            id=data.get("id", str(uuid4())[:8]),
            name=data["name"],
            scenario_type=ScenarioType[data["scenario_type"]],
            description=data.get("description", ""),
            citizens=citizens,
            trigger=trigger,
            success_criteria=success_criteria,
            regions=data.get("regions", []),
            tags=data.get("tags", []),
            difficulty=data.get("difficulty", "medium"),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 30),
        )

    def manifest(self, lod: int = 0) -> dict[str, Any]:
        """
        Manifest the scenario at a given Level of Detail.

        LOD 0: Name and type only
        LOD 1: + description, regions
        LOD 2: + citizen names and archetypes
        LOD 3: + full citizen specs, criteria
        """
        base: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "type": self.scenario_type.name,
        }

        if lod >= 1:
            base["description"] = self.description
            base["regions"] = self.regions
            base["tags"] = self.tags
            base["difficulty"] = self.difficulty

        if lod >= 2:
            base["citizens"] = [{"name": c.name, "archetype": c.archetype} for c in self.citizens]
            base["estimated_duration_minutes"] = self.estimated_duration_minutes

        if lod >= 3:
            base["citizens"] = [
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "region": c.region,
                    "backstory": c.backstory,
                    "eigenvectors": c.eigenvectors.to_dict(),
                }
                for c in self.citizens
            ]
            base["success_criteria"] = {
                "require_all": self.success_criteria.require_all,
                "criteria": [
                    {"kind": c.kind, "description": c.description}
                    for c in self.success_criteria.criteria
                ],
            }

        return base


# =============================================================================
# Scenario Registry
# =============================================================================


class ScenarioRegistry:
    """
    Registry for scenario templates.

    Provides:
    - Template storage and retrieval by ID
    - Filtering by type, tags, difficulty
    - AGENTESE path resolution for world.town.scenario.*
    """

    def __init__(self) -> None:
        self._templates: dict[str, ScenarioTemplate] = {}

    def register(self, template: ScenarioTemplate) -> None:
        """Register a scenario template."""
        self._templates[template.id] = template

    def get(self, scenario_id: str) -> ScenarioTemplate | None:
        """Get a template by ID."""
        return self._templates.get(scenario_id)

    def list_all(self) -> list[ScenarioTemplate]:
        """List all templates."""
        return list(self._templates.values())

    def filter_by_type(self, scenario_type: ScenarioType) -> list[ScenarioTemplate]:
        """Filter templates by type."""
        return [t for t in self._templates.values() if t.scenario_type == scenario_type]

    def filter_by_tag(self, tag: str) -> list[ScenarioTemplate]:
        """Filter templates by tag."""
        return [t for t in self._templates.values() if tag in t.tags]

    def filter_by_difficulty(self, difficulty: str) -> list[ScenarioTemplate]:
        """Filter templates by difficulty."""
        return [t for t in self._templates.values() if t.difficulty == difficulty]

    def search(
        self,
        scenario_type: ScenarioType | None = None,
        tags: list[str] | None = None,
        difficulty: str | None = None,
    ) -> list[ScenarioTemplate]:
        """Search templates with multiple filters."""
        results = list(self._templates.values())

        if scenario_type:
            results = [t for t in results if t.scenario_type == scenario_type]

        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]

        if difficulty:
            results = [t for t in results if t.difficulty == difficulty]

        return results


# =============================================================================
# Scenario Phases (Polynomial Positions)
# =============================================================================


class ScenarioPhase(Enum):
    """
    Phases of a running scenario (polynomial positions).

    PENDING → TRIGGERED → ACTIVE → (COMPLETED | FAILED | ABANDONED)

    Synergy: Mirrors DirectorPhase for consistent state machine patterns.
    """

    PENDING = auto()  # Waiting for trigger condition
    TRIGGERED = auto()  # Trigger fired, initializing
    ACTIVE = auto()  # Running, evaluating success criteria
    COMPLETED = auto()  # Success criteria met
    FAILED = auto()  # Failed (timeout, impossible state)
    ABANDONED = auto()  # User abandoned scenario


# =============================================================================
# Validation and Errors
# =============================================================================


class ScenarioError(Exception):
    """Base exception for scenario errors."""

    pass


class ScenarioValidationError(ScenarioError):
    """Raised when scenario validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)


class ScenarioStateError(ScenarioError):
    """Raised when scenario is in invalid state for operation."""

    def __init__(self, message: str, current_phase: ScenarioPhase) -> None:
        self.current_phase = current_phase
        super().__init__(message)


def validate_citizen_spec(spec: CitizenSpec) -> list[str]:
    """
    Validate a CitizenSpec.

    Returns list of validation errors (empty if valid).
    """
    errors: list[str] = []

    if not spec.name or not spec.name.strip():
        errors.append("CitizenSpec.name cannot be empty")

    if not spec.archetype or not spec.archetype.strip():
        errors.append("CitizenSpec.archetype cannot be empty")

    if not spec.region or not spec.region.strip():
        errors.append("CitizenSpec.region cannot be empty")

    # Validate eigenvectors are in range [0, 1]
    ev = spec.eigenvectors
    for attr in [
        "warmth",
        "curiosity",
        "trust",
        "creativity",
        "patience",
        "resilience",
        "ambition",
    ]:
        val = getattr(ev, attr)
        if not (0.0 <= val <= 1.0):
            errors.append(f"Eigenvector {attr}={val} must be in [0.0, 1.0]")

    return errors


def validate_scenario_template(template: ScenarioTemplate) -> list[str]:
    """
    Validate a ScenarioTemplate.

    Returns list of validation errors (empty if valid).
    """
    errors: list[str] = []

    if not template.name or not template.name.strip():
        errors.append("ScenarioTemplate.name cannot be empty")

    if not template.citizens:
        errors.append("ScenarioTemplate must have at least one citizen")

    # Validate each citizen spec
    for i, spec in enumerate(template.citizens):
        spec_errors = validate_citizen_spec(spec)
        for err in spec_errors:
            errors.append(f"citizens[{i}]: {err}")

    # Validate regions contain all citizen regions
    citizen_regions = {spec.region for spec in template.citizens}
    template_regions = set(template.regions)
    missing_regions = citizen_regions - template_regions
    if missing_regions and template.regions:  # Only warn if regions were specified
        errors.append(f"Regions missing citizen locations: {missing_regions}")

    # Validate success criteria
    if not template.success_criteria.criteria:
        errors.append("ScenarioTemplate should have at least one success criterion")

    # Validate difficulty
    if template.difficulty not in {"easy", "medium", "hard"}:
        errors.append(f"Invalid difficulty '{template.difficulty}'; must be easy/medium/hard")

    # Validate estimated duration
    if template.estimated_duration_minutes <= 0:
        errors.append("estimated_duration_minutes must be positive")

    return errors


# =============================================================================
# Scenario Session (Active Scenario Instance)
# =============================================================================


@dataclass
class ScenarioSession:
    """
    An active instance of a scenario.

    Sessions track:
    - Current phase (polynomial state)
    - Spawned citizens
    - Progress toward success criteria
    - Interaction history
    - Director integration

    Synergy: Integrates with DirectorAgent for pacing.
    """

    template: ScenarioTemplate
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    phase: ScenarioPhase = ScenarioPhase.PENDING
    started_at: datetime | None = None
    ended_at: datetime | None = None

    # Spawned citizens (created on start)
    _citizens: list[Citizen] = field(default_factory=list, repr=False)

    # Runtime context for success criteria evaluation
    context: dict[str, Any] = field(default_factory=dict)

    # Interaction history
    interactions: list[dict[str, Any]] = field(default_factory=list, repr=False)

    # Phase history for audit/witness
    phase_history: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        """Initialize context with defaults."""
        self.context.setdefault("interactions", self.interactions)
        self.context.setdefault("revealed_info", set())
        self.context.setdefault("coalitions", [])
        self.context.setdefault("pooled_resources", 0)
        self.context.setdefault("votes", {})
        self.context.setdefault("events", [])
        self.context.setdefault("time_elapsed", 0.0)
        # Consent debt tracking - "hosts can say no"
        # debt > 0.7 blocks beat injection
        self.context.setdefault("consent_debt", {})

    @property
    def citizens(self) -> list[Citizen]:
        """Get spawned citizens (spawns if not yet spawned)."""
        if not self._citizens and self.phase != ScenarioPhase.PENDING:
            self._citizens = self.template.spawn_citizens()
        return self._citizens

    @property
    def is_active(self) -> bool:
        """Check if scenario is still running."""
        return self.phase in {
            ScenarioPhase.PENDING,
            ScenarioPhase.TRIGGERED,
            ScenarioPhase.ACTIVE,
        }

    @property
    def is_terminal(self) -> bool:
        """Check if scenario has reached a terminal state."""
        return self.phase in {
            ScenarioPhase.COMPLETED,
            ScenarioPhase.FAILED,
            ScenarioPhase.ABANDONED,
        }

    def _record_phase_transition(
        self, from_phase: ScenarioPhase, to_phase: ScenarioPhase, reason: str = ""
    ) -> None:
        """Record a phase transition for audit trail."""
        self.phase_history.append(
            {
                "from": from_phase.name,
                "to": to_phase.name,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
            }
        )

    def start(self) -> None:
        """
        Start the scenario session.

        Transitions: PENDING → TRIGGERED → ACTIVE (if trigger is immediate)

        Raises:
            ScenarioStateError: If not in PENDING phase
        """
        if self.phase != ScenarioPhase.PENDING:
            raise ScenarioStateError(
                f"Cannot start scenario in {self.phase.name} phase",
                self.phase,
            )

        old_phase = self.phase
        self.phase = ScenarioPhase.TRIGGERED
        self._record_phase_transition(old_phase, self.phase, "start() called")
        self.started_at = datetime.now()

        # Spawn citizens
        self._citizens = self.template.spawn_citizens()
        self.context["citizens"] = [c.name for c in self._citizens]

        # Check if trigger is immediate
        if self.template.trigger.is_satisfied(self.context):
            old_phase = self.phase
            self.phase = ScenarioPhase.ACTIVE
            self._record_phase_transition(old_phase, self.phase, "immediate trigger satisfied")

    def tick(self, elapsed_seconds: float = 1.0) -> dict[str, Any]:
        """
        Tick the scenario forward.

        Updates time_elapsed and checks trigger/success criteria.

        Args:
            elapsed_seconds: Time elapsed since last tick

        Returns:
            Status dict with phase and progress info
        """
        self.context["time_elapsed"] = self.context.get("time_elapsed", 0.0) + elapsed_seconds

        # Handle different phases
        if self.phase == ScenarioPhase.TRIGGERED:
            # Check if trigger is now satisfied
            if self.template.trigger.is_satisfied(self.context):
                old_phase = self.phase
                self.phase = ScenarioPhase.ACTIVE
                self._record_phase_transition(old_phase, self.phase, "trigger satisfied")

        elif self.phase == ScenarioPhase.ACTIVE:
            # Check success criteria
            if self.template.success_criteria.is_met(self.context):
                old_phase = self.phase
                self.phase = ScenarioPhase.COMPLETED
                self._record_phase_transition(old_phase, self.phase, "success criteria met")
                self.ended_at = datetime.now()

        return {
            "phase": self.phase.name,
            "time_elapsed": self.context["time_elapsed"],
            "progress": self.template.success_criteria.get_progress(self.context),
            "is_complete": self.phase == ScenarioPhase.COMPLETED,
        }

    def record_interaction(
        self,
        from_citizen: str,
        to_citizen: str,
        interaction_type: str = "dialogue",
        content: str = "",
    ) -> None:
        """Record an interaction between citizens."""
        interaction = {
            "from": from_citizen,
            "to": to_citizen,
            "type": interaction_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.interactions.append(interaction)
        self.context["interactions"] = self.interactions

    def reveal_information(self, info_key: str) -> None:
        """Reveal information (for mystery scenarios)."""
        self.context["revealed_info"].add(info_key)

    def record_coalition(self, coalition_id: str, members: list[str]) -> None:
        """Record a coalition formation."""
        self.context["coalitions"].append(
            {
                "id": coalition_id,
                "members": members,
                "formed_at": datetime.now().isoformat(),
            }
        )

    def add_resources(self, amount: int) -> None:
        """Add to pooled resources."""
        self.context["pooled_resources"] = self.context.get("pooled_resources", 0) + amount

    def record_vote(self, option: str, count: int = 1) -> None:
        """Record votes for consensus tracking."""
        self.context["votes"][option] = self.context["votes"].get(option, 0) + count

    def abandon(self, reason: str = "") -> None:
        """Abandon the scenario."""
        if self.is_terminal:
            return  # Already terminal

        old_phase = self.phase
        self.phase = ScenarioPhase.ABANDONED
        self._record_phase_transition(old_phase, self.phase, reason or "abandoned by user")
        self.ended_at = datetime.now()

    def fail(self, reason: str = "") -> None:
        """Mark scenario as failed."""
        if self.is_terminal:
            return  # Already terminal

        old_phase = self.phase
        self.phase = ScenarioPhase.FAILED
        self._record_phase_transition(old_phase, self.phase, reason or "scenario failed")
        self.ended_at = datetime.now()

    # =========================================================================
    # Consent Debt - "Westworld where hosts can say no"
    # =========================================================================

    def get_consent_debt(self, citizen_name: str) -> float:
        """
        Get consent debt for a citizen.

        Debt accumulates when hosts are forced to act against their will.
        Debt > 0.7 blocks beat injections.

        Returns:
            Debt value between 0.0 and 1.0
        """
        return self.context["consent_debt"].get(citizen_name, 0.0)

    def incur_debt(self, citizen_name: str, amount: float = 0.1) -> float:
        """
        Incur consent debt for forcing a host to act.

        Args:
            citizen_name: The host who is being forced
            amount: Debt to add (default 0.1 per forced action)

        Returns:
            New debt level
        """
        current = self.get_consent_debt(citizen_name)
        new_debt = min(1.0, current + amount)
        self.context["consent_debt"][citizen_name] = new_debt

        # Record the event
        self.context["events"].append(
            {
                "type": "consent_debt_incurred",
                "citizen": citizen_name,
                "amount": amount,
                "new_debt": new_debt,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return new_debt

    def can_inject_beat(self, citizen_name: str) -> bool:
        """
        Check if a beat can be injected for this citizen.

        Debt > 0.7 blocks injections. The host refuses.

        Returns:
            True if beat can be injected, False if blocked by debt
        """
        debt = self.get_consent_debt(citizen_name)
        return debt <= 0.7

    def apologize(self, citizen_name: str, reduction: float = 0.15) -> float:
        """
        Reduce consent debt by apologizing/making amends.

        The visitor acknowledges they pushed too hard and makes amends.
        This reduces debt and re-enables beat injection.

        Args:
            citizen_name: The host to apologize to
            reduction: Amount to reduce debt (default 0.15)

        Returns:
            New debt level
        """
        current = self.get_consent_debt(citizen_name)
        new_debt = max(0.0, current - reduction)
        self.context["consent_debt"][citizen_name] = new_debt

        # Record the event
        self.context["events"].append(
            {
                "type": "consent_debt_reduced",
                "citizen": citizen_name,
                "reduction": reduction,
                "new_debt": new_debt,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return new_debt

    def to_dict(self) -> dict[str, Any]:
        """Serialize session state."""
        return {
            "id": self.id,
            "template_id": self.template.id,
            "template_name": self.template.name,
            "phase": self.phase.name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "citizens": [c.name for c in self._citizens],
            "context": {
                "time_elapsed": self.context.get("time_elapsed", 0.0),
                "interactions_count": len(self.interactions),
                "revealed_info": list(self.context.get("revealed_info", set())),
                "coalitions_count": len(self.context.get("coalitions", [])),
                "pooled_resources": self.context.get("pooled_resources", 0),
                # Consent debt - "hosts can say no"
                "consent_debt": self.context.get("consent_debt", {}),
            },
            "progress": self.template.success_criteria.get_progress(self.context),
            "phase_history": self.phase_history,
        }


# =============================================================================
# Scenario Polynomial (State Machine)
# =============================================================================


def _scenario_directions(phase: ScenarioPhase) -> frozenset[str]:
    """Valid inputs for each scenario phase."""
    match phase:
        case ScenarioPhase.PENDING:
            return frozenset({"start", "abandon"})
        case ScenarioPhase.TRIGGERED:
            return frozenset({"tick", "abandon"})
        case ScenarioPhase.ACTIVE:
            return frozenset(
                {
                    "tick",
                    "interaction",
                    "reveal",
                    "coalition",
                    "vote",
                    "abandon",
                    "fail",
                }
            )
        case ScenarioPhase.COMPLETED | ScenarioPhase.FAILED | ScenarioPhase.ABANDONED:
            return frozenset({"reset"})  # Terminal states only allow reset
        case _:
            return frozenset()


def create_scenario_polynomial(session: ScenarioSession) -> Any:
    """
    Create a PolyAgent for a scenario session.

    Synergy: Uses the same PolyAgent pattern as DirectorAgent.

    Returns:
        PolyAgent[ScenarioPhase, Any, dict[str, Any]]
    """
    from agents.poly.protocol import PolyAgent

    def transition(phase: ScenarioPhase, input: Any) -> tuple[ScenarioPhase, dict[str, Any]]:
        """Scenario state transition function."""
        cmd = (
            input
            if isinstance(input, str)
            else input.get("cmd", "tick")
            if isinstance(input, dict)
            else "tick"
        )

        match phase:
            case ScenarioPhase.PENDING:
                if cmd == "start":
                    session.start()
                    return session.phase, {
                        "status": "started",
                        "phase": session.phase.name,
                    }
                elif cmd == "abandon":
                    session.abandon()
                    return session.phase, {"status": "abandoned"}

            case ScenarioPhase.TRIGGERED:
                if cmd == "tick":
                    result = session.tick(
                        input.get("elapsed", 1.0) if isinstance(input, dict) else 1.0
                    )
                    return session.phase, result
                elif cmd == "abandon":
                    session.abandon()
                    return session.phase, {"status": "abandoned"}

            case ScenarioPhase.ACTIVE:
                if cmd == "tick":
                    result = session.tick(
                        input.get("elapsed", 1.0) if isinstance(input, dict) else 1.0
                    )
                    return session.phase, result
                elif cmd == "interaction" and isinstance(input, dict):
                    session.record_interaction(
                        input.get("from", ""),
                        input.get("to", ""),
                        input.get("type", "dialogue"),
                        input.get("content", ""),
                    )
                    return session.phase, {"status": "interaction_recorded"}
                elif cmd == "reveal" and isinstance(input, dict):
                    session.reveal_information(input.get("info", ""))
                    return session.phase, {"status": "info_revealed"}
                elif cmd == "coalition" and isinstance(input, dict):
                    session.record_coalition(input.get("id", ""), input.get("members", []))
                    return session.phase, {"status": "coalition_recorded"}
                elif cmd == "vote" and isinstance(input, dict):
                    session.record_vote(input.get("option", ""), input.get("count", 1))
                    return session.phase, {"status": "vote_recorded"}
                elif cmd == "abandon":
                    session.abandon()
                    return session.phase, {"status": "abandoned"}
                elif cmd == "fail":
                    session.fail(input.get("reason", "") if isinstance(input, dict) else "")
                    return session.phase, {"status": "failed"}

            case ScenarioPhase.COMPLETED | ScenarioPhase.FAILED | ScenarioPhase.ABANDONED:
                if cmd == "reset":
                    # Reset to new pending session
                    session.phase = ScenarioPhase.PENDING
                    session._citizens = []
                    session.context = {}
                    session.__post_init__()
                    return session.phase, {"status": "reset"}

        return phase, {"status": "unknown_command", "cmd": cmd}

    return PolyAgent(
        name=f"ScenarioPolynomial({session.template.name})",
        positions=frozenset(ScenarioPhase),
        _directions=_scenario_directions,
        _transition=transition,
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Enums
    "ScenarioType",
    "ScenarioPhase",
    # Specs
    "CitizenSpec",
    # Triggers
    "TriggerCondition",
    # Success
    "SuccessCriterion",
    "SuccessCriteria",
    # Template
    "ScenarioTemplate",
    # Registry
    "ScenarioRegistry",
    # Session
    "ScenarioSession",
    # Polynomial
    "create_scenario_polynomial",
    # Validation
    "ScenarioError",
    "ScenarioValidationError",
    "ScenarioStateError",
    "validate_citizen_spec",
    "validate_scenario_template",
]
