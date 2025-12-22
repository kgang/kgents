"""
Witness Workflow Templates: Pre-Built Cross-Jewel Patterns.

"Tasteful > feature-complete" — these workflows embody the vision.

Pre-built workflow templates for common developer scenarios:

1. TEST_FAILURE_RESPONSE: Tests fail → Analyze → Fix → Retest → Capture
2. CODE_CHANGE_RESPONSE: File changes → Analyze → Document → Capture
3. PR_REVIEW_WORKFLOW: PR opened → Analyze → Test → Summarize → Capture
4. MORNING_STANDUP: Memory query → CI status → Gestalt → Summary
5. CI_MONITOR: Periodic CI check → Alert on failure

Each template is a composable Pipeline that can be:
- Used directly via run_workflow()
- Extended with >> composition
- Scheduled for later execution

Philosophy:
    "The daemon runs continuously; workflows embody recurring intention."

See: plans/kgentsd-cross-jewel.md
See: spec/principles.md (Composable principle)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from .pipeline import Branch, Pipeline, Step, branch, step

if TYPE_CHECKING:
    pass


# =============================================================================
# Workflow Categories
# =============================================================================


class WorkflowCategory(Enum):
    """Categories of workflow templates."""

    REACTIVE = auto()  # Respond to events
    PROACTIVE = auto()  # Scheduled/periodic
    DIAGNOSTIC = auto()  # Health checks
    DOCUMENTATION = auto()  # Generate docs


# =============================================================================
# Workflow Templates
# =============================================================================


@dataclass(frozen=True)
class WorkflowTemplate:
    """
    A pre-built workflow template.

    Attributes:
        name: Human-readable name
        description: What this workflow does
        category: Workflow category
        pipeline: The actual Pipeline
        required_trust: Minimum trust level (0-3)
        estimated_duration: Estimated execution time
        tags: Semantic tags for discovery
    """

    name: str
    description: str
    category: WorkflowCategory
    pipeline: Pipeline
    required_trust: int = 0  # 0=READ_ONLY, 3=AUTONOMOUS
    estimated_duration: timedelta = timedelta(seconds=30)
    tags: frozenset[str] = frozenset()

    def __call__(self, **kwargs: Any) -> Pipeline:
        """
        Get the pipeline with optional parameter overrides.

        Templates are callable for easy instantiation.
        """
        # For now, return the pipeline as-is
        # Future: could support parameter injection
        return self.pipeline


# =============================================================================
# Test Failure Response
# =============================================================================


def _build_test_failure_response() -> Pipeline:
    """
    Build the test failure response workflow.

    Tests fail → Analyze failure → Attempt fix → Retest → Capture result
    """
    return (
        step("world.gestalt.analyze")  # Analyze the failure
        >> branch(
            condition=lambda r: r.get("issues", 0) > 0,
            if_true=step("world.forge.fix"),  # Apply fix
            if_false=step("self.memory.capture", content="Analysis found no issues"),
        )
        >> step("world.test.run")  # Rerun tests
        >> step("self.memory.capture")  # Capture result
    )


TEST_FAILURE_RESPONSE = WorkflowTemplate(
    name="Test Failure Response",
    description="Analyze test failures, attempt fixes, and retest",
    category=WorkflowCategory.REACTIVE,
    pipeline=_build_test_failure_response(),
    required_trust=3,  # AUTONOMOUS - applies fixes
    estimated_duration=timedelta(minutes=2),
    tags=frozenset({"tests", "fix", "automated"}),
)


# =============================================================================
# Code Change Response
# =============================================================================


def _build_code_change_response() -> Pipeline:
    """
    Build the code change response workflow.

    File changes → Analyze patterns → Update docs → Capture in memory
    """
    return (
        step("world.gestalt.analyze")  # Analyze the changes
        >> step("self.memory.capture")  # Capture analysis
        >> step("world.forge.document")  # Generate/update docs
    )


CODE_CHANGE_RESPONSE = WorkflowTemplate(
    name="Code Change Response",
    description="Analyze code changes and update documentation",
    category=WorkflowCategory.REACTIVE,
    pipeline=_build_code_change_response(),
    required_trust=3,  # AUTONOMOUS - modifies docs
    estimated_duration=timedelta(minutes=1),
    tags=frozenset({"code", "docs", "analysis"}),
)


# =============================================================================
# PR Review Workflow
# =============================================================================


def _build_pr_review_workflow() -> Pipeline:
    """
    Build the PR review workflow.

    PR opened → Analyze changes → Run tests → Generate summary → Capture
    """
    return (
        step("world.gestalt.analyze")  # Analyze PR changes
        >> step("world.test.run")  # Run affected tests
        >> branch(
            condition=lambda r: r.get("passed", False),
            if_true=step("world.forge.summarize"),  # Generate summary
            if_false=step("self.memory.capture", content="Tests failed - PR needs fixes"),
        )
        >> step("self.memory.capture")  # Store review result
    )


PR_REVIEW_WORKFLOW = WorkflowTemplate(
    name="PR Review",
    description="Analyze PR, run tests, and generate review summary",
    category=WorkflowCategory.REACTIVE,
    pipeline=_build_pr_review_workflow(),
    required_trust=1,  # BOUNDED - read-heavy with summary generation
    estimated_duration=timedelta(minutes=3),
    tags=frozenset({"pr", "review", "tests", "summary"}),
)


# =============================================================================
# Morning Standup Workflow
# =============================================================================


def _build_morning_standup() -> Pipeline:
    """
    Build the morning standup preparation workflow.

    Query yesterday → Check CI → Get current state → Generate summary
    """
    return (
        step("self.memory.manifest")  # Get recent memory
        >> step("world.ci.manifest")  # Check CI status
        >> step("world.gestalt.manifest")  # Current codebase state
    )


MORNING_STANDUP = WorkflowTemplate(
    name="Morning Standup",
    description="Prepare standup summary: yesterday's work, CI status, current state",
    category=WorkflowCategory.PROACTIVE,
    pipeline=_build_morning_standup(),
    required_trust=0,  # READ_ONLY - just gathering info
    estimated_duration=timedelta(seconds=30),
    tags=frozenset({"standup", "morning", "summary", "status"}),
)


# =============================================================================
# CI Monitor Workflow
# =============================================================================


def _build_ci_monitor() -> Pipeline:
    """
    Build the CI monitoring workflow.

    Check CI → Capture status (with alert on failure)
    """
    return (
        step("world.ci.manifest")  # Get CI status
        >> branch(
            condition=lambda r: r.get("status") != "passing",
            if_true=step("self.memory.capture", content="CI failing - attention needed"),
            if_false=step("self.memory.capture", content="CI passing"),
        )
    )


CI_MONITOR = WorkflowTemplate(
    name="CI Monitor",
    description="Check CI status and alert on failures",
    category=WorkflowCategory.DIAGNOSTIC,
    pipeline=_build_ci_monitor(),
    required_trust=0,  # READ_ONLY - just monitoring
    estimated_duration=timedelta(seconds=15),
    tags=frozenset({"ci", "monitor", "alerts"}),
)


# =============================================================================
# Health Check Workflow
# =============================================================================


def _build_health_check() -> Pipeline:
    """
    Build the system health check workflow.

    Check all manifests to verify system health.
    """
    return (
        step("self.witness.manifest")  # Witness status
        >> step("self.memory.manifest")  # Memory status
        >> step("world.gestalt.manifest")  # Gestalt status
    )


HEALTH_CHECK = WorkflowTemplate(
    name="Health Check",
    description="Verify health of all Crown Jewels",
    category=WorkflowCategory.DIAGNOSTIC,
    pipeline=_build_health_check(),
    required_trust=0,  # READ_ONLY
    estimated_duration=timedelta(seconds=10),
    tags=frozenset({"health", "diagnostic", "status"}),
)


# =============================================================================
# Crystallization Workflow
# =============================================================================


def _build_crystallization() -> Pipeline:
    """
    Build the experience crystallization workflow.

    Trigger crystallization of current session's thoughts.
    """
    return (
        step("time.witness.manifest")  # Get crystallization status
        >> step("time.witness.crystallize")  # Trigger crystallization
    )


CRYSTALLIZATION = WorkflowTemplate(
    name="Experience Crystallization",
    description="Crystallize current session's thoughts into durable memory",
    category=WorkflowCategory.PROACTIVE,
    pipeline=_build_crystallization(),
    required_trust=1,  # BOUNDED - writes to .kgents/
    estimated_duration=timedelta(seconds=20),
    tags=frozenset({"crystal", "memory", "session"}),
)


# =============================================================================
# Registry
# =============================================================================


WORKFLOW_REGISTRY: dict[str, WorkflowTemplate] = {
    "test-failure": TEST_FAILURE_RESPONSE,
    "code-change": CODE_CHANGE_RESPONSE,
    "pr-review": PR_REVIEW_WORKFLOW,
    "standup": MORNING_STANDUP,
    "ci-monitor": CI_MONITOR,
    "health-check": HEALTH_CHECK,
    "crystallize": CRYSTALLIZATION,
}


def get_workflow(name: str) -> WorkflowTemplate | None:
    """Get a workflow template by name."""
    return WORKFLOW_REGISTRY.get(name)


def list_workflows(
    category: WorkflowCategory | None = None,
    max_trust: int | None = None,
) -> list[WorkflowTemplate]:
    """
    List available workflow templates.

    Args:
        category: Filter by category
        max_trust: Filter by maximum required trust level

    Returns:
        List of matching templates
    """
    templates = list(WORKFLOW_REGISTRY.values())

    if category:
        templates = [t for t in templates if t.category == category]

    if max_trust is not None:
        templates = [t for t in templates if t.required_trust <= max_trust]

    return templates


def search_workflows(tag: str) -> list[WorkflowTemplate]:
    """
    Search workflows by tag.

    Args:
        tag: Tag to search for

    Returns:
        List of workflows containing the tag
    """
    return [t for t in WORKFLOW_REGISTRY.values() if tag in t.tags]


# =============================================================================
# Workflow Composition Helpers
# =============================================================================


def extend_workflow(
    base: WorkflowTemplate,
    *extensions: Step,
) -> Pipeline:
    """
    Extend a workflow template with additional steps.

    Example:
        extended = extend_workflow(
            MORNING_STANDUP,
            step("world.forge.summarize"),
            step("self.memory.capture"),
        )
    """
    pipeline = base.pipeline
    for ext in extensions:
        pipeline = pipeline >> ext
    return pipeline


def chain_workflows(*templates: WorkflowTemplate) -> Pipeline:
    """
    Chain multiple workflow templates together.

    Example:
        full_morning = chain_workflows(HEALTH_CHECK, MORNING_STANDUP)
    """
    if not templates:
        return Pipeline([])

    result = templates[0].pipeline
    for template in templates[1:]:
        result = result >> template.pipeline

    return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Template type
    "WorkflowTemplate",
    "WorkflowCategory",
    # Templates
    "TEST_FAILURE_RESPONSE",
    "CODE_CHANGE_RESPONSE",
    "PR_REVIEW_WORKFLOW",
    "MORNING_STANDUP",
    "CI_MONITOR",
    "HEALTH_CHECK",
    "CRYSTALLIZATION",
    # Registry
    "WORKFLOW_REGISTRY",
    "get_workflow",
    "list_workflows",
    "search_workflows",
    # Composition
    "extend_workflow",
    "chain_workflows",
]
