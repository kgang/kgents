"""
Demo: Trail schemas in the Crystal system.

Shows how to use frozen dataclass schemas for trail navigation artifacts.
"""

from agents.d.schemas.trail import (
    TRAIL_ANNOTATION_SCHEMA,
    TRAIL_COMMITMENT_SCHEMA,
    TRAIL_SCHEMA,
    TRAIL_STEP_SCHEMA,
    Trail,
    TrailAnnotation,
    TrailCommitment,
    TrailStep,
)


def demo_trail_schemas():
    """Demonstrate trail schema usage."""
    print("=== Trail Schemas Demo ===\n")

    # 1. Create a trail
    trail = Trail(
        name="Bug Investigation",
        description="Investigating authentication timeout bug",
        created_by_id="developer-42",
        is_active=True,
    )
    print(f"1. Created trail: {trail.name}")
    trail_dict = TRAIL_SCHEMA.to_dict(trail)
    print(f"   Serialized: {trail_dict['_schema']} v{trail_dict['_version']}\n")

    # 2. Add steps to the trail
    steps = [
        TrailStep(
            trail_id="trail-auth-001",
            index=0,
            action="search",
            content="grep -r 'session_timeout' .",
            reasoning="Find all session timeout references",
            tool_name="grep",
            tool_input={"pattern": "session_timeout"},
            tool_output="Found 12 matches in 5 files",
        ),
        TrailStep(
            trail_id="trail-auth-001",
            index=1,
            action="read",
            content="Read auth/middleware.py",
            reasoning="Check middleware implementation",
            tool_name="read",
            tool_input={"file": "auth/middleware.py"},
            tool_output="File contains session validation logic",
        ),
        TrailStep(
            trail_id="trail-auth-001",
            index=2,
            action="analyze",
            content="Session timeout set to 300s but token expires at 600s",
            reasoning="Found the discrepancy causing the bug",
        ),
    ]

    print("2. Added trail steps:")
    for step in steps:
        step_dict = TRAIL_STEP_SCHEMA.to_dict(step)
        print(f"   Step {step.index}: {step.action} - {step.content[:50]}...")

    # 3. Add a commitment based on evidence
    commitment = TrailCommitment(
        trail_id="trail-auth-001",
        step_index=2,
        level="strong",
        justification=(
            "Clear evidence of timeout mismatch. "
            "Session expires at 300s but token valid for 600s. "
            "Confirmed in middleware.py and config.yaml."
        ),
    )
    print(f"\n3. Added commitment: level={commitment.level}")
    print(f"   Justification: {commitment.justification}\n")

    # 4. Add an annotation
    annotation = TrailAnnotation(
        trail_id="trail-auth-001",
        step_index=1,
        content="This middleware pattern is used in 3 other services too",
        author_id="reviewer-99",
    )
    print(f"4. Added annotation at step {annotation.step_index}")
    print(f"   Content: {annotation.content}\n")

    # 5. Show schema metadata
    print("5. Schema metadata:")
    for schema in [
        TRAIL_SCHEMA,
        TRAIL_STEP_SCHEMA,
        TRAIL_COMMITMENT_SCHEMA,
        TRAIL_ANNOTATION_SCHEMA,
    ]:
        print(f"   - {schema.name} v{schema.version}: {schema.contract.__name__}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_trail_schemas()
