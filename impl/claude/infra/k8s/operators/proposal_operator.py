"""Proposal Operator - Risk-aware change governance.

The proposal operator manages the lifecycle of Proposal CRs:
1. On CREATE: Calculate risk (base + velocity + magnitude)
2. On TIMER: Check for expired proposals, update velocity metrics
3. On APPROVAL: Verify approvals meet requirements
4. On MERGE: Execute the change and emit result pheromone

Risk Model:
    cumulative_risk = base_risk * (1 + velocity_penalty) * magnitude_factor / test_coverage

Where:
    - base_risk: Fixed by change type (0.1-0.9)
    - velocity_penalty: Increases with recent changes (resets on human approval)
    - magnitude_factor: 1.0 + log2(lines_changed + files_touched)
    - test_coverage: 1.0 - 0.5 * (tests_added / (tests_added + tests_removed + 1))

T-gent Integration:
    - Emits REVIEW_REQUEST pheromone when tGentValidation=true
    - Waits for REVIEW_COMPLETE pheromone from T-gent
    - Updates status.tGentValidation based on response

Principle alignment:
- T-gent (Algebraic Reliability): Changes are type-checked operations
- B-gent (Economics): Risk budget is a fiscal constraint
- E-gent (Thermodynamics): Velocity penalty = entropy accumulation
"""

from __future__ import annotations

import builtins
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

try:
    import kopf
    from kubernetes import client
    from kubernetes.client.rest import ApiException

    KOPF_AVAILABLE = True
except ImportError:
    KOPF_AVAILABLE = False
    kopf = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# ==============================================================================
# Constants and Configuration
# ==============================================================================

# Base risk values by change type (from fiscal constitution)
BASE_RISK_BY_TYPE: dict[str, float] = {
    # Code changes
    "CODE_PATCH": 0.1,
    "CODE_FEATURE": 0.3,
    "CODE_REFACTOR": 0.4,
    "CODE_DELETE": 0.5,
    # Config changes
    "CONFIG_UPDATE": 0.2,
    "CONFIG_SECRET": 0.6,
    # Agent changes
    "AGENT_DEPLOY": 0.3,
    "AGENT_SCALE": 0.1,
    "AGENT_DELETE": 0.7,
    "AGENT_UPGRADE": 0.4,
    # Memory changes
    "MEMORY_MIGRATE": 0.6,
    "MEMORY_COMPACT": 0.3,
    "MEMORY_DELETE": 0.8,
    # Governance changes
    "POLICY_UPDATE": 0.5,
    "RISK_OVERRIDE": 0.9,
}

# Risk level thresholds
RISK_LEVEL_THRESHOLDS = {
    "LOW": 0.2,  # Auto-merge eligible
    "MEDIUM": 0.5,  # Needs one approval
    "HIGH": 0.8,  # Needs multiple approvals
    "CRITICAL": 1.0,  # Needs human override
}

# Auto-merge threshold (proposals below this can be auto-merged)
AUTO_MERGE_THRESHOLD = 0.2

# Velocity penalty constants
VELOCITY_DECAY_HOURS = 1.0  # Penalty decays over this window
VELOCITY_INCREMENT = 0.1  # Each proposal adds this to velocity

# Operator timing
EXPIRY_CHECK_INTERVAL = 60.0  # Check for expired proposals every minute
DEFAULT_TTL_SECONDS = 86400  # 24 hours default TTL


# ==============================================================================
# Data Classes
# ==============================================================================


class ProposalPhase(Enum):
    """Proposal lifecycle phases."""

    PENDING = "Pending"
    REVIEWING = "Reviewing"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    MERGED = "Merged"
    EXPIRED = "Expired"
    SUPERSEDED = "Superseded"


class RiskLevel(Enum):
    """Human-readable risk levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskAssessment:
    """Calculated risk metrics for a proposal."""

    base_risk: float
    velocity_penalty: float
    magnitude_factor: float
    test_coverage: float
    cumulative_risk: float
    risk_level: RiskLevel
    calculated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for K8s status."""
        return {
            "baseRisk": self.base_risk,
            "velocityPenalty": self.velocity_penalty,
            "magnitudeFactor": self.magnitude_factor,
            "testCoverage": self.test_coverage,
            "cumulativeRisk": self.cumulative_risk,
            "riskLevel": self.risk_level.value,
            "calculatedAt": self.calculated_at.isoformat(),
        }


@dataclass
class ProposalSpec:
    """Parsed Proposal CRD spec."""

    name: str
    namespace: str
    change_type: str
    target_kind: str
    target_name: str
    proposer: str
    description: str = ""
    rationale: str = ""
    lines_added: int = 0
    lines_removed: int = 0
    files_changed: int = 0
    tests_added: int = 0
    tests_removed: int = 0
    auto_merge: bool = True
    required_approvers: int = 0
    required_reviewers: list[str] = field(default_factory=list)
    t_gent_validation: bool = True
    max_cumulative_risk: float = 0.3
    velocity_window: str = "1h"
    ttl_seconds: int = DEFAULT_TTL_SECONDS


# ==============================================================================
# Risk Calculation Functions
# ==============================================================================


def get_base_risk(change_type: str) -> float:
    """Get base risk for a change type."""
    return BASE_RISK_BY_TYPE.get(change_type, 0.5)


def calculate_magnitude_factor(
    lines_added: int,
    lines_removed: int,
    files_changed: int,
) -> float:
    """Calculate magnitude factor based on scope.

    Uses log2 to prevent large changes from dominating.
    Minimum factor is 1.0.
    """
    total_lines = lines_added + lines_removed
    total_impact = total_lines + (files_changed * 10)  # Weight files

    if total_impact <= 0:
        return 1.0

    # log2(x+1) + 1 gives us:
    # 0 lines/files -> 1.0
    # 10 lines -> ~4.5
    # 100 lines -> ~7.7
    # 1000 lines -> ~11.0
    return 1.0 + math.log2(total_impact + 1) * 0.1


def calculate_test_coverage_factor(
    tests_added: int,
    tests_removed: int,
) -> float:
    """Calculate test coverage factor.

    Adding tests reduces risk, removing tests increases risk.
    Returns value between 0.5 (excellent coverage) and 1.5 (poor coverage).
    """
    net_tests = tests_added - tests_removed

    if net_tests > 0:
        # Adding tests reduces risk
        # log2(tests+1) * 0.1 gives reduction
        return max(0.5, 1.0 - math.log2(net_tests + 1) * 0.05)
    elif net_tests < 0:
        # Removing tests increases risk
        return min(1.5, 1.0 + math.log2(abs(net_tests) + 1) * 0.1)

    return 1.0


def get_risk_level(cumulative_risk: float) -> RiskLevel:
    """Map cumulative risk to risk level."""
    if cumulative_risk <= RISK_LEVEL_THRESHOLDS["LOW"]:
        return RiskLevel.LOW
    elif cumulative_risk <= RISK_LEVEL_THRESHOLDS["MEDIUM"]:
        return RiskLevel.MEDIUM
    elif cumulative_risk <= RISK_LEVEL_THRESHOLDS["HIGH"]:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def calculate_risk(
    spec: ProposalSpec,
    velocity_penalty: float = 0.0,
) -> RiskAssessment:
    """Calculate full risk assessment for a proposal."""
    base_risk = get_base_risk(spec.change_type)

    magnitude_factor = calculate_magnitude_factor(
        spec.lines_added,
        spec.lines_removed,
        spec.files_changed,
    )

    test_coverage = calculate_test_coverage_factor(
        spec.tests_added,
        spec.tests_removed,
    )

    # Core risk formula
    cumulative_risk = (
        base_risk * (1 + velocity_penalty) * magnitude_factor * test_coverage
    )

    # Clamp to [0, 1]
    cumulative_risk = max(0.0, min(1.0, cumulative_risk))

    return RiskAssessment(
        base_risk=base_risk,
        velocity_penalty=velocity_penalty,
        magnitude_factor=magnitude_factor,
        test_coverage=test_coverage,
        cumulative_risk=cumulative_risk,
        risk_level=get_risk_level(cumulative_risk),
        calculated_at=datetime.now(timezone.utc),
    )


def parse_proposal_spec(
    spec: dict[str, Any],
    meta: dict[str, Any],
) -> ProposalSpec:
    """Parse CRD spec into ProposalSpec dataclass."""
    target = spec.get("target", {})
    magnitude = spec.get("magnitude", {})
    review = spec.get("reviewRequirements", {})
    budget = spec.get("riskBudget", {})

    return ProposalSpec(
        name=meta.get("name", ""),
        namespace=meta.get("namespace", "kgents-agents"),
        change_type=spec.get("changeType", "CODE_PATCH"),
        target_kind=target.get("kind", ""),
        target_name=target.get("name", ""),
        proposer=spec.get("proposer", ""),
        description=spec.get("description", ""),
        rationale=spec.get("rationale", ""),
        lines_added=magnitude.get("linesAdded", 0),
        lines_removed=magnitude.get("linesRemoved", 0),
        files_changed=magnitude.get("filesChanged", 0),
        tests_added=magnitude.get("testsAdded", 0),
        tests_removed=magnitude.get("testsRemoved", 0),
        auto_merge=review.get("autoMerge", True),
        required_approvers=review.get("requiredApprovers", 0),
        required_reviewers=review.get("requiredReviewers", []),
        t_gent_validation=review.get("tGentValidation", True),
        max_cumulative_risk=budget.get("maxCumulativeRisk", 0.3),
        velocity_window=budget.get("velocityWindow", "1h"),
        ttl_seconds=spec.get("ttlSeconds", DEFAULT_TTL_SECONDS),
    )


def generate_review_pheromone(
    proposal_name: str,
    namespace: str,
    spec: ProposalSpec,
    risk: RiskAssessment,
) -> dict[str, Any]:
    """Generate a REVIEW_REQUEST pheromone for T-gent validation."""
    import json

    payload = json.dumps(
        {
            "proposal": proposal_name,
            "changeType": spec.change_type,
            "target": f"{spec.target_kind}/{spec.target_name}",
            "risk": risk.cumulative_risk,
            "riskLevel": risk.risk_level.value,
        }
    )

    return {
        "apiVersion": "kgents.io/v1",
        "kind": "Pheromone",
        "metadata": {
            "name": f"review-{proposal_name}",
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/part-of": "kgents",
                "app.kubernetes.io/managed-by": "proposal-operator",
                "kgents.io/proposal": proposal_name,
            },
        },
        "spec": {
            "type": "INTENT",  # T-gent watches INTENT pheromones
            "intensity": min(
                1.0, risk.cumulative_risk + 0.3
            ),  # Higher risk = stronger signal
            "source": "proposal-operator",
            "payload": payload,
            "decay_rate": 0.05,  # Slow decay - wait for T-gent
            "ttl_seconds": 3600,  # 1 hour TTL
        },
    }


# ==============================================================================
# Kopf Handlers (only registered if kopf is available)
# ==============================================================================

if KOPF_AVAILABLE:

    @kopf.on.create("kgents.io", "v1", "proposals")  # type: ignore[arg-type]
    async def on_proposal_create(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Calculate risk and initialize proposal status."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")

        logger.info(f"Processing proposal: {name}")

        # Parse spec
        proposal_spec = parse_proposal_spec(spec, meta)

        # Calculate velocity penalty from recent proposals
        velocity_penalty = await _get_velocity_penalty(namespace)

        # Calculate risk
        risk = calculate_risk(proposal_spec, velocity_penalty)

        logger.info(
            f"Proposal {name}: risk={risk.cumulative_risk:.3f} "
            f"level={risk.risk_level.value}"
        )

        # Update status with risk assessment
        now = datetime.now(timezone.utc).isoformat()
        patch.status["riskAssessment"] = risk.to_dict()
        patch.status["approvals"] = []
        patch.status["rejections"] = []

        # Determine initial phase based on risk and auto-merge settings
        if (
            proposal_spec.auto_merge
            and risk.cumulative_risk <= AUTO_MERGE_THRESHOLD
            and proposal_spec.required_approvers == 0
            and not proposal_spec.t_gent_validation
        ):
            # Auto-merge eligible
            patch.status["phase"] = ProposalPhase.APPROVED.value
            patch.status["conditions"] = [
                {
                    "type": "AutoMergeEligible",
                    "status": "True",
                    "reason": "LowRisk",
                    "message": f"Risk {risk.cumulative_risk:.3f} below threshold {AUTO_MERGE_THRESHOLD}",
                    "lastTransitionTime": now,
                }
            ]
            return {"autoMerge": True, "risk": risk.cumulative_risk}

        # Needs review
        patch.status["phase"] = ProposalPhase.REVIEWING.value

        # Emit T-gent review pheromone if validation required
        if proposal_spec.t_gent_validation:
            custom_api = client.CustomObjectsApi()
            pheromone = generate_review_pheromone(name, namespace, proposal_spec, risk)

            try:
                custom_api.create_namespaced_custom_object(
                    group="kgents.io",
                    version="v1",
                    namespace=namespace,
                    plural="pheromones",
                    body=pheromone,
                )
                patch.status["tGentValidation"] = {
                    "requested": True,
                    "pheromoneEmitted": pheromone["metadata"]["name"],
                    "result": "PENDING",
                }
                logger.info(f"Emitted T-gent review pheromone for {name}")
            except ApiException as e:
                if e.status == 409:
                    logger.warning(f"Review pheromone already exists for {name}")
                else:
                    logger.error(f"Failed to emit pheromone: {e}")
                    patch.status["tGentValidation"] = {
                        "requested": True,
                        "result": "SKIPPED",
                    }
        else:
            patch.status["tGentValidation"] = {
                "requested": False,
                "result": "SKIPPED",
            }

        patch.status["conditions"] = [
            {
                "type": "Ready",
                "status": "False",
                "reason": "AwaitingReview",
                "message": f"Risk level {risk.risk_level.value} requires review",
                "lastTransitionTime": now,
            }
        ]

        return {
            "created": True,
            "risk": risk.cumulative_risk,
            "level": risk.risk_level.value,
        }

    @kopf.timer("kgents.io", "v1", "proposals", interval=EXPIRY_CHECK_INTERVAL)  # type: ignore[arg-type]
    async def check_proposal_expiry(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any] | None:
        """Check if proposal has expired."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        current_phase = status.get("phase")

        # Skip if already in terminal state
        if current_phase in (
            ProposalPhase.MERGED.value,
            ProposalPhase.REJECTED.value,
            ProposalPhase.EXPIRED.value,
            ProposalPhase.SUPERSEDED.value,
        ):
            return None

        # Check TTL
        ttl_seconds = spec.get("ttlSeconds", DEFAULT_TTL_SECONDS)
        created_str = meta.get("creationTimestamp")
        if created_str:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age = (now - created).total_seconds()

            if age >= ttl_seconds:
                logger.info(
                    f"Proposal {name} expired (age={age:.0f}s, ttl={ttl_seconds}s)"
                )
                patch.status["phase"] = ProposalPhase.EXPIRED.value
                patch.status["conditions"] = [
                    {
                        "type": "Ready",
                        "status": "False",
                        "reason": "Expired",
                        "message": f"Proposal expired after {ttl_seconds}s",
                        "lastTransitionTime": now.isoformat(),
                    }
                ]
                return {"expired": True, "age": age}

        return None

    @kopf.on.field("kgents.io", "v1", "proposals", field="status.approvals")  # type: ignore[arg-type]
    async def on_approval_change(
        old: list[dict[str, Any]] | None,
        new: list[dict[str, Any]] | None,
        meta: dict[str, Any],
        spec: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> None:
        """Handle new approvals."""
        name = meta["name"]
        current_phase = status.get("phase")

        # Only process if in Reviewing phase
        if current_phase != ProposalPhase.REVIEWING.value:
            return

        old_count = len(old or [])
        new_count = len(new or [])

        if new_count > old_count:
            # New approval received
            new_approvals = (new or [])[old_count:]
            for approval in new_approvals:
                logger.info(f"Proposal {name} approved by {approval.get('approver')}")

            # Check if we have enough approvals
            required = spec.get("reviewRequirements", {}).get("requiredApprovers", 0)
            if new_count >= required:
                # Check T-gent validation
                t_gent_result = status.get("tGentValidation", {}).get(
                    "result", "SKIPPED"
                )
                if t_gent_result in ("PASSED", "SKIPPED"):
                    logger.info(
                        f"Proposal {name} has sufficient approvals, marking approved"
                    )
                    patch.status["phase"] = ProposalPhase.APPROVED.value
                    patch.status["conditions"] = [
                        {
                            "type": "Ready",
                            "status": "True",
                            "reason": "Approved",
                            "message": f"{new_count} approvals received",
                            "lastTransitionTime": datetime.now(
                                timezone.utc
                            ).isoformat(),
                        }
                    ]

    async def _get_velocity_penalty(namespace: str) -> float:
        """Calculate velocity penalty from recent proposals.

        Looks at proposals created in the last hour and calculates
        cumulative penalty.
        """
        try:
            custom_api = client.CustomObjectsApi()
            proposals = custom_api.list_namespaced_custom_object(
                group="kgents.io",
                version="v1",
                namespace=namespace,
                plural="proposals",
            )

            now = datetime.now(timezone.utc)
            window = timedelta(hours=VELOCITY_DECAY_HOURS)
            penalty = 0.0

            for proposal in proposals.get("items", []):
                meta = proposal.get("metadata", {})
                created_str = meta.get("creationTimestamp")
                if created_str:
                    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    age = now - created
                    if age < window:
                        # Linear decay: more recent = higher penalty
                        decay_factor = 1.0 - (
                            age.total_seconds() / window.total_seconds()
                        )
                        penalty += VELOCITY_INCREMENT * decay_factor

            return penalty

        except Exception as e:
            logger.warning(f"Failed to calculate velocity penalty: {e}")
            return 0.0


# ==============================================================================
# Mock Implementation (for testing without K8s)
# ==============================================================================


@dataclass
class MockProposal:
    """In-memory proposal for testing without K8s."""

    name: str
    namespace: str
    spec: ProposalSpec
    risk: RiskAssessment | None = None
    phase: ProposalPhase = ProposalPhase.PENDING
    approvals: list[dict[str, Any]] = field(default_factory=list)
    rejections: list[dict[str, Any]] = field(default_factory=list)
    t_gent_validation: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_risk(self, velocity_penalty: float = 0.0) -> RiskAssessment:
        """Calculate and store risk assessment."""
        self.risk = calculate_risk(self.spec, velocity_penalty)
        return self.risk

    def approve(self, approver: str, comment: str = "") -> bool:
        """Add an approval."""
        if self.phase != ProposalPhase.REVIEWING:
            return False

        self.approvals.append(
            {
                "approver": approver,
                "approvedAt": datetime.now(timezone.utc).isoformat(),
                "comment": comment,
            }
        )

        # Check if enough approvals
        if len(self.approvals) >= self.spec.required_approvers:
            if self.t_gent_validation.get("result", "SKIPPED") in ("PASSED", "SKIPPED"):
                self.phase = ProposalPhase.APPROVED

        return True

    def reject(self, rejector: str, reason: str) -> bool:
        """Reject the proposal."""
        if self.phase not in (ProposalPhase.PENDING, ProposalPhase.REVIEWING):
            return False

        self.rejections.append(
            {
                "rejector": rejector,
                "rejectedAt": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            }
        )
        self.phase = ProposalPhase.REJECTED
        return True

    def merge(self, executor: str) -> bool:
        """Merge the proposal."""
        if self.phase != ProposalPhase.APPROVED:
            return False

        self.phase = ProposalPhase.MERGED
        return True

    def is_expired(self) -> bool:
        """Check if proposal has expired."""
        if self.phase in (
            ProposalPhase.MERGED,
            ProposalPhase.REJECTED,
            ProposalPhase.EXPIRED,
        ):
            return False

        age = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return age >= self.spec.ttl_seconds


class MockProposalRegistry:
    """In-memory proposal registry for testing without K8s."""

    def __init__(self) -> None:
        self._proposals: dict[str, MockProposal] = {}
        self._velocity_penalty: float = 0.0

    def create(
        self,
        name: str,
        spec: ProposalSpec,
        namespace: str = "kgents-agents",
    ) -> MockProposal:
        """Create a new proposal."""
        proposal = MockProposal(
            name=name,
            namespace=namespace,
            spec=spec,
        )

        # Calculate risk with current velocity
        risk = proposal.calculate_risk(self._velocity_penalty)

        # Update velocity penalty
        self._velocity_penalty += VELOCITY_INCREMENT

        # Determine initial phase
        if (
            spec.auto_merge
            and risk.cumulative_risk <= AUTO_MERGE_THRESHOLD
            and spec.required_approvers == 0
            and not spec.t_gent_validation
        ):
            proposal.phase = ProposalPhase.APPROVED
        else:
            proposal.phase = ProposalPhase.REVIEWING
            if spec.t_gent_validation:
                proposal.t_gent_validation = {
                    "requested": True,
                    "result": "PENDING",
                }

        self._proposals[name] = proposal
        logger.info(
            f"Created proposal: {name} "
            f"risk={risk.cumulative_risk:.3f} "
            f"phase={proposal.phase.value}"
        )
        return proposal

    def get(self, name: str) -> MockProposal | None:
        """Get a proposal by name."""
        return self._proposals.get(name)

    def list(self) -> builtins.list[MockProposal]:
        """List all proposals."""
        return builtins.list(self._proposals.values())

    def delete(self, name: str) -> bool:
        """Delete a proposal."""
        if name in self._proposals:
            del self._proposals[name]
            return True
        return False

    def decay_velocity(self, hours: float = 1.0) -> None:
        """Simulate velocity decay over time."""
        decay_factor = max(0.0, 1.0 - hours / VELOCITY_DECAY_HOURS)
        self._velocity_penalty *= decay_factor

    def reset_velocity(self) -> None:
        """Reset velocity penalty (e.g., on human approval)."""
        self._velocity_penalty = 0.0

    def get_velocity_penalty(self) -> float:
        """Get current velocity penalty."""
        return self._velocity_penalty

    def expire_proposals(self) -> "builtins.list[str]":
        """Check and expire old proposals. Returns list of expired names."""
        expired = []
        for name, proposal in self._proposals.items():
            if proposal.is_expired():
                proposal.phase = ProposalPhase.EXPIRED
                expired.append(name)
        return expired


# Global mock registry for testing
_mock_registry: MockProposalRegistry | None = None


def get_mock_registry() -> MockProposalRegistry:
    """Get or create the global mock proposal registry."""
    global _mock_registry
    if _mock_registry is None:
        _mock_registry = MockProposalRegistry()
    return _mock_registry


def reset_mock_registry() -> None:
    """Reset the global mock registry (for testing)."""
    global _mock_registry
    _mock_registry = None
