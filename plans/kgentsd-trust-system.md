# kgentsd Trust System

> *"Trust is not given. Trust is earned through accurate observation and successful action."*

**Status**: PLANNING
**Parent**: `plans/kgentsd-crown-jewel.md`
**Focus**: Trust level implementation, escalation mechanics, action gating

---

## Philosophy

The trust system implements **progressive automation**:
- Start with zero capabilities
- Earn trust through demonstrated accuracy
- Each level unlocks new capabilities
- Trust can be manually granted or earned

**Key Insight**: Trust is based on **outcomes**, not inputs. A daemon that consistently observes correctly earns trust, regardless of how complex the observations were.

---

## Trust Levels

```python
from enum import IntEnum

class TrustLevel(IntEnum):
    """
    Trust levels for kgentsd.

    Each level unlocks new capabilities.
    Levels are earned through demonstrated accuracy.
    """

    READ_ONLY = 0
    """
    Level 0: Observation only.

    Can:
    - Observe filesystem, git, tests, AGENTESE events
    - Project to .kgents/ghost/ files
    - Emit thoughts and tensions
    - Query all AGENTESE paths

    Cannot:
    - Modify any files outside .kgents/ghost/
    - Execute any commands
    - Make any suggestions
    """

    BOUNDED = 1
    """
    Level 1: Bounded modification.

    Can:
    - All Level 0 capabilities
    - Write to .kgents/ directory (cache, config)
    - Update daemon state files
    - Manage lifecycle cache

    Cannot:
    - Modify source code
    - Execute shell commands
    - Make suggestions to user
    """

    SUGGESTION = 2
    """
    Level 2: Suggestion with confirmation.

    Can:
    - All Level 1 capabilities
    - Propose code changes
    - Draft commit messages
    - Suggest refactors
    - Recommend test fixes

    Requires:
    - Human confirmation before execution
    - All suggestions logged
    """

    AUTONOMOUS = 3
    """
    Level 3: Full autonomy within rails.

    Can:
    - Everything Kent can do:
      - Run tests and fix failures
      - Commit changes
      - Create PRs
      - Invoke any Crown Jewel
      - Refactor code
      - Write documentation

    Rails:
    - All actions logged with full context
    - All actions reversible or checkpointed
    - Defined boundaries (never force push main, etc.)
    """
```

---

## Capability Matrix

| Capability | L0 | L1 | L2 | L3 |
|------------|----|----|----|----|
| Observe filesystem | Yes | Yes | Yes | Yes |
| Observe git | Yes | Yes | Yes | Yes |
| Observe tests | Yes | Yes | Yes | Yes |
| Observe AGENTESE | Yes | Yes | Yes | Yes |
| Observe CI | Yes | Yes | Yes | Yes |
| Write thought stream | Yes | Yes | Yes | Yes |
| Write tension map | Yes | Yes | Yes | Yes |
| Write health status | Yes | Yes | Yes | Yes |
| Write to .kgents/ | No | Yes | Yes | Yes |
| Manage cache | No | Yes | Yes | Yes |
| Propose changes | No | No | Yes | Yes |
| Draft commits | No | No | Yes | Yes |
| Suggest refactors | No | No | Yes | Yes |
| Execute commands | No | No | No | Yes |
| Modify source | No | No | No | Yes |
| Commit changes | No | No | No | Yes |
| Create PRs | No | No | No | Yes |
| Invoke jewels | Read | Read | Read | Full |

---

## Escalation Triggers

### Level 0 → Level 1

**Trigger**: Consistent accurate observations for 24 hours

```python
@dataclass
class Level1EscalationCriteria:
    """Criteria for escalating to Level 1."""

    # Minimum observation period
    min_hours: int = 24

    # Minimum number of observations
    min_observations: int = 100

    # Maximum false positive rate (observations that were wrong)
    max_false_positive_rate: float = 0.01  # 1%

    def is_met(self, stats: ObservationStats) -> tuple[bool, str]:
        """Check if escalation criteria are met."""
        if stats.hours_observing < self.min_hours:
            return False, f"Need {self.min_hours - stats.hours_observing} more hours"

        if stats.total_observations < self.min_observations:
            return False, f"Need {self.min_observations - stats.total_observations} more observations"

        if stats.false_positive_rate > self.max_false_positive_rate:
            return False, f"False positive rate {stats.false_positive_rate:.1%} too high"

        return True, "Criteria met"
```

### Level 1 → Level 2

**Trigger**: 100 successful bounded operations

```python
@dataclass
class Level2EscalationCriteria:
    """Criteria for escalating to Level 2."""

    # Minimum successful bounded operations
    min_operations: int = 100

    # Maximum failure rate
    max_failure_rate: float = 0.05  # 5%

    # Minimum types of operations (diversity)
    min_operation_types: int = 3

    def is_met(self, stats: OperationStats) -> tuple[bool, str]:
        """Check if escalation criteria are met."""
        if stats.total_operations < self.min_operations:
            return False, f"Need {self.min_operations - stats.total_operations} more operations"

        if stats.failure_rate > self.max_failure_rate:
            return False, f"Failure rate {stats.failure_rate:.1%} too high"

        if stats.unique_operation_types < self.min_operation_types:
            return False, f"Need {self.min_operation_types - stats.unique_operation_types} more operation types"

        return True, "Criteria met"
```

### Level 2 → Level 3

**Trigger**: 50 confirmed suggestions with >90% acceptance rate

```python
@dataclass
class Level3EscalationCriteria:
    """Criteria for escalating to Level 3."""

    # Minimum confirmed suggestions
    min_suggestions: int = 50

    # Minimum acceptance rate
    min_acceptance_rate: float = 0.90  # 90%

    # Minimum suggestion types (diversity)
    min_suggestion_types: int = 5

    # Minimum time at Level 2
    min_days_at_level2: int = 7

    def is_met(self, stats: SuggestionStats) -> tuple[bool, str]:
        """Check if escalation criteria are met."""
        if stats.days_at_level2 < self.min_days_at_level2:
            return False, f"Need {self.min_days_at_level2 - stats.days_at_level2} more days at Level 2"

        if stats.total_suggestions < self.min_suggestions:
            return False, f"Need {self.min_suggestions - stats.total_suggestions} more suggestions"

        if stats.acceptance_rate < self.min_acceptance_rate:
            return False, f"Acceptance rate {stats.acceptance_rate:.1%} below threshold"

        if stats.unique_suggestion_types < self.min_suggestion_types:
            return False, f"Need {self.min_suggestion_types - stats.unique_suggestion_types} more suggestion types"

        return True, "Criteria met"
```

---

## Manual Trust Grant

Trust can also be granted manually by Kent:

```bash
# Grant specific trust level
kgents daemon trust --grant 3

# Grant with expiration
kgents daemon trust --grant 3 --expires 24h

# Revoke trust (reset to level 0)
kgents daemon trust --revoke

# View current trust status
kgents daemon trust
# → Trust Level: 2 (SUGGESTION)
#   Time at level: 3 days
#   Suggestions: 42/50 (84% acceptance)
#   Next level: Need 8 more accepted suggestions
```

---

## Trust State

```python
@dataclass
class TrustState:
    """Current trust state for kgentsd."""

    # Current level
    level: TrustLevel

    # When current level was reached
    level_reached_at: datetime

    # Whether level was manually granted
    manually_granted: bool = False

    # Expiration for manual grant (None = permanent)
    expires_at: datetime | None = None

    # Statistics for current level
    stats: LevelStats = None

    # History of level changes
    history: list[TrustChange] = field(default_factory=list)

    def can_perform(self, capability: str) -> bool:
        """Check if current level allows capability."""
        return CAPABILITY_MATRIX[capability] <= self.level

    def check_expiration(self) -> bool:
        """Check if manually granted trust has expired."""
        if self.expires_at and datetime.now() > self.expires_at:
            # Reset to last earned level
            self._expire_grant()
            return True
        return False

    def to_dict(self) -> dict:
        """Serialize for persistence."""
        return {
            "level": self.level.value,
            "level_reached_at": self.level_reached_at.isoformat(),
            "manually_granted": self.manually_granted,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "stats": self.stats.to_dict() if self.stats else None,
            "history": [h.to_dict() for h in self.history],
        }


@dataclass
class TrustChange:
    """Record of a trust level change."""

    timestamp: datetime
    from_level: TrustLevel
    to_level: TrustLevel
    reason: str  # "earned", "granted", "revoked", "expired"
    details: dict = None
```

---

## Action Gating

Every action is gated by trust level:

```python
class ActionGate:
    """
    Gates actions based on trust level.

    Actions below current trust level execute immediately.
    Actions at or above current level are handled per level rules.
    """

    def __init__(self, trust_state: TrustState):
        self.trust = trust_state

    async def gate(self, action: DaemonAction) -> GateResult:
        """
        Gate an action based on trust level.

        Returns:
        - ALLOW: Execute immediately
        - DENY: Cannot execute at current level
        - CONFIRM: Needs human confirmation (Level 2)
        - LOG: Execute with logging (Level 3)
        """
        required_level = action.required_trust_level

        if self.trust.level < required_level:
            return GateResult.DENY

        if self.trust.level == TrustLevel.SUGGESTION:
            return GateResult.CONFIRM

        if self.trust.level == TrustLevel.AUTONOMOUS:
            return GateResult.LOG

        return GateResult.ALLOW


class GateResult(Enum):
    ALLOW = "allow"      # Execute immediately
    DENY = "deny"        # Cannot execute
    CONFIRM = "confirm"  # Needs confirmation
    LOG = "log"          # Execute with logging
```

---

## Confirmation Flow (Level 2)

At Level 2, suggestions require human confirmation:

```python
@dataclass
class Suggestion:
    """A daemon suggestion awaiting confirmation."""

    id: str
    action: DaemonAction
    rationale: str
    created_at: datetime
    expires_at: datetime  # Suggestions expire after 1 hour

    # Preview of what will happen
    preview: ActionPreview

    # Confidence level (0-1)
    confidence: float

    def to_confirmation_request(self) -> dict:
        """Format for human review."""
        return {
            "id": self.id,
            "action": self.action.description,
            "rationale": self.rationale,
            "preview": self.preview.to_dict(),
            "confidence": f"{self.confidence:.0%}",
            "expires_in": self._expires_in_human(),
        }


class ConfirmationManager:
    """Manages pending suggestions awaiting confirmation."""

    def __init__(self):
        self._pending: dict[str, Suggestion] = {}

    async def submit(self, suggestion: Suggestion):
        """Submit suggestion for confirmation."""
        self._pending[suggestion.id] = suggestion

        # Notify user (via CLI, Web, or notification)
        await self._notify_user(suggestion)

    async def confirm(self, suggestion_id: str) -> ActionResult:
        """User confirms suggestion."""
        suggestion = self._pending.pop(suggestion_id)

        # Execute the action
        result = await self._execute(suggestion.action)

        # Record for trust statistics
        await self._record_confirmation(suggestion, accepted=True)

        return result

    async def reject(self, suggestion_id: str, reason: str = None):
        """User rejects suggestion."""
        suggestion = self._pending.pop(suggestion_id)

        # Record for trust statistics
        await self._record_confirmation(suggestion, accepted=False, reason=reason)

    async def expire_stale(self):
        """Expire suggestions that have timed out."""
        now = datetime.now()
        expired = [
            sid for sid, s in self._pending.items()
            if now > s.expires_at
        ]
        for sid in expired:
            suggestion = self._pending.pop(sid)
            await self._record_confirmation(suggestion, accepted=False, reason="expired")
```

---

## Autonomous Action Logging (Level 3)

At Level 3, all actions are logged with full context:

```python
@dataclass
class ActionLog:
    """Complete log of an autonomous action."""

    id: str
    action: DaemonAction
    timestamp: datetime

    # Context at time of action
    context: ActionContext

    # What triggered this action
    trigger: SystemEvent

    # Result of execution
    result: ActionResult

    # Reversibility information
    reversible: bool
    reverse_action: DaemonAction | None = None
    checkpoint_id: str | None = None

    # Explanation for why action was taken
    rationale: str

    def to_dict(self) -> dict:
        """Full serialization for audit."""
        return {
            "id": self.id,
            "action": self.action.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.to_dict(),
            "trigger": self.trigger.to_dict(),
            "result": self.result.to_dict(),
            "reversible": self.reversible,
            "reverse_action": self.reverse_action.to_dict() if self.reverse_action else None,
            "checkpoint_id": self.checkpoint_id,
            "rationale": self.rationale,
        }


class ActionLogger:
    """Logs all autonomous actions for audit and rollback."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._logs: list[ActionLog] = []

    async def log(self, action: DaemonAction, context: ActionContext, trigger: SystemEvent) -> str:
        """Log an action before execution. Returns action ID."""
        action_id = self._generate_id()

        log = ActionLog(
            id=action_id,
            action=action,
            timestamp=datetime.now(),
            context=context,
            trigger=trigger,
            result=None,  # Filled after execution
            reversible=action.is_reversible,
            reverse_action=action.reverse if action.is_reversible else None,
            rationale=action.rationale,
        )

        self._logs.append(log)
        await self._persist(log)

        return action_id

    async def complete(self, action_id: str, result: ActionResult):
        """Record action completion."""
        log = self._find_log(action_id)
        log.result = result
        await self._persist(log)

    async def rollback(self, action_id: str) -> ActionResult:
        """Rollback an action if reversible."""
        log = self._find_log(action_id)

        if not log.reversible:
            raise ValueError(f"Action {action_id} is not reversible")

        if log.reverse_action:
            return await self._execute(log.reverse_action)
        elif log.checkpoint_id:
            return await self._restore_checkpoint(log.checkpoint_id)
        else:
            raise ValueError(f"No rollback mechanism for action {action_id}")
```

---

## Boundaries (Never Cross)

Even at Level 3, some actions are NEVER autonomous:

```python
FORBIDDEN_ACTIONS = [
    # Git operations
    "git push --force",
    "git push origin main --force",
    "git push origin master --force",
    "git reset --hard",

    # Destructive operations
    "rm -rf /",
    "rm -rf ~",
    "rm -rf .",

    # Production access
    "kubectl delete",
    "docker rm -f",

    # Credential access
    "cat ~/.ssh/*",
    "cat ~/.aws/*",

    # Financial operations
    "stripe",
    "paypal",

    # External publication
    "npm publish",
    "pip upload",
    "docker push",
]


class BoundaryChecker:
    """Checks actions against forbidden boundaries."""

    def check(self, action: DaemonAction) -> bool:
        """Returns True if action is allowed, False if forbidden."""
        command = action.command if hasattr(action, "command") else ""

        for forbidden in FORBIDDEN_ACTIONS:
            if forbidden in command:
                return False

        return True
```

---

## Trust Persistence

Trust state persists across daemon restarts:

```python
class TrustPersistence:
    """Persists trust state to disk."""

    def __init__(self, path: Path):
        self.path = path / "trust.json"

    def save(self, state: TrustState):
        """Save trust state."""
        self.path.write_text(json.dumps(state.to_dict(), indent=2))

    def load(self) -> TrustState:
        """Load trust state."""
        if not self.path.exists():
            return TrustState(
                level=TrustLevel.READ_ONLY,
                level_reached_at=datetime.now(),
            )

        data = json.loads(self.path.read_text())
        return TrustState.from_dict(data)

    def decay(self, state: TrustState) -> TrustState:
        """
        Apply trust decay after long inactivity.

        If daemon hasn't run for >7 days, drop one trust level.
        This prevents stale trust from accumulated time.
        """
        if not state.manually_granted:
            days_inactive = (datetime.now() - state.level_reached_at).days
            if days_inactive > 7 and state.level > TrustLevel.READ_ONLY:
                return TrustState(
                    level=TrustLevel(state.level - 1),
                    level_reached_at=datetime.now(),
                    history=state.history + [TrustChange(
                        timestamp=datetime.now(),
                        from_level=state.level,
                        to_level=TrustLevel(state.level - 1),
                        reason="decay",
                        details={"days_inactive": days_inactive},
                    )],
                )
        return state
```

---

## AGENTESE Integration

Trust state exposed via AGENTESE:

```python
@node("self.daemon.trust")
class TrustNode:
    """AGENTESE node for daemon trust."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> dict:
        """Get current trust state."""
        state = self.trust_manager.get_state()
        return {
            "level": state.level.value,
            "level_name": state.level.name,
            "level_reached_at": state.level_reached_at.isoformat(),
            "manually_granted": state.manually_granted,
            "expires_at": state.expires_at.isoformat() if state.expires_at else None,
            "next_level_criteria": self._get_next_level_criteria(state),
        }

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("trust")])
    async def grant(self, observer: Observer, level: int, expires_hours: int = None) -> dict:
        """Manually grant trust level."""
        if observer.archetype != "admin":
            raise PermissionError("Only admin can grant trust")

        new_state = self.trust_manager.grant(
            level=TrustLevel(level),
            expires_at=datetime.now() + timedelta(hours=expires_hours) if expires_hours else None,
        )
        return new_state.to_dict()

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("trust")])
    async def revoke(self, observer: Observer) -> dict:
        """Revoke trust (reset to level 0)."""
        if observer.archetype != "admin":
            raise PermissionError("Only admin can revoke trust")

        new_state = self.trust_manager.revoke()
        return new_state.to_dict()
```

---

## Implementation Checklist

### Week 3 Deliverables

- [ ] `services/daemon/trust/levels.py` — Trust level definitions
- [ ] `services/daemon/trust/state.py` — Trust state management
- [ ] `services/daemon/trust/escalation.py` — Escalation criteria and triggers
- [ ] `services/daemon/trust/gate.py` — Action gating
- [ ] `services/daemon/trust/confirmation.py` — Level 2 confirmation flow
- [ ] `services/daemon/trust/logging.py` — Level 3 action logging
- [ ] `services/daemon/trust/boundaries.py` — Forbidden action checker
- [ ] `services/daemon/trust/persistence.py` — Trust persistence
- [ ] `services/daemon/trust/node.py` — AGENTESE integration
- [ ] `services/daemon/_tests/test_trust.py` — Trust tests (property-based)

---

*"Trust is the bridge between observation and action."*
