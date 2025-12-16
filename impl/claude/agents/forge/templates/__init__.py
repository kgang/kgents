"""
Forge Task Templates: Pre-defined task types for common use cases.

Templates encode:
- Coalition shape (which archetypes)
- Expected handoff patterns
- Output format
- Credit cost
- Validation rules

From the plan (coalition-forge.md):
    | Task Type | Coalition Shape | Output Format | Credits |
    |-----------|-----------------|---------------|---------|
    | Research Report | Scout + Sage + 2 specialists | Markdown | 50 |
    | Code Review | Steady + Sync + domain expert | PR comments | 30 |
    | Content Creation | Spark + Sage + audience-tuned | Multi-format | 40 |
    | Decision Analysis | Full archetype set | Pros/cons matrix | 75 |
    | Competitive Intel | Scout + 3 specialists | Briefing doc | 100 |

See: plans/core-apps/coalition-forge.md
"""

from .base import TaskTemplate
from .code_review import CODE_REVIEW_TEMPLATE, CodeReviewTask
from .competitive_intel import COMPETITIVE_INTEL_TEMPLATE, CompetitiveIntelTask
from .content_creation import CONTENT_CREATION_TEMPLATE, ContentCreationTask
from .decision_analysis import DECISION_ANALYSIS_TEMPLATE, DecisionAnalysisTask
from .research_report import RESEARCH_REPORT_TEMPLATE, ResearchReportTask

# Template registry
TASK_TEMPLATES: dict[str, TaskTemplate] = {
    "research_report": RESEARCH_REPORT_TEMPLATE,
    "code_review": CODE_REVIEW_TEMPLATE,
    "content_creation": CONTENT_CREATION_TEMPLATE,
    "decision_analysis": DECISION_ANALYSIS_TEMPLATE,
    "competitive_intel": COMPETITIVE_INTEL_TEMPLATE,
}


def get_template(template_id: str) -> TaskTemplate:
    """
    Get a template by ID.

    Args:
        template_id: Template identifier

    Returns:
        TaskTemplate instance

    Raises:
        KeyError: If template not found
    """
    if template_id not in TASK_TEMPLATES:
        available = ", ".join(TASK_TEMPLATES.keys())
        raise KeyError(f"Unknown template: {template_id}. Available: {available}")
    return TASK_TEMPLATES[template_id]


def list_templates() -> list[dict[str, str | int]]:
    """
    List all available templates with metadata.

    Returns:
        List of template summaries
    """
    return [
        {
            "id": t.template_id,
            "name": t.name,
            "description": t.description,
            "credits": t.base_credits,
            "output_format": t.output_format.name,
        }
        for t in TASK_TEMPLATES.values()
    ]


__all__ = [
    # Base
    "TaskTemplate",
    # Templates
    "ResearchReportTask",
    "CodeReviewTask",
    "ContentCreationTask",
    "DecisionAnalysisTask",
    "CompetitiveIntelTask",
    # Template objects
    "RESEARCH_REPORT_TEMPLATE",
    "CODE_REVIEW_TEMPLATE",
    "CONTENT_CREATION_TEMPLATE",
    "DECISION_ANALYSIS_TEMPLATE",
    "COMPETITIVE_INTEL_TEMPLATE",
    # Registry
    "TASK_TEMPLATES",
    "get_template",
    "list_templates",
]
