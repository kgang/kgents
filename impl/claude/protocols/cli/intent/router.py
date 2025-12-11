"""
Intent Router - The Natural Language Intent Dispatcher.

The 'do' command takes complex, multi-step natural language intents
and routes them to the appropriate command sequence.

Example:
  kgents do "take input.py, check it against the laws, and fix any issues"

This generates and confirms a flow:
  1. kgents check input.py
  2. kgents fix input.py (if issues found)

Key Features:
- Intent classification using heuristics (lightweight) or Haiku (if available)
- Dry-run by design: shows plan before execution
- Safety: destructive operations default to NO
- Flow generation: can export plan as flowfile

See: docs/cli-integration-plan.md Part 2 (The Intent Router)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum

# =============================================================================
# Types
# =============================================================================


class IntentCategory(Enum):
    """High-level intent categories."""

    CREATION = "creation"  # new, create, generate, scaffold
    VERIFICATION = "verification"  # check, verify, validate, test
    REPAIR = "repair"  # fix, repair, correct
    ANALYSIS = "analysis"  # think, analyze, review, examine
    OBSERVATION = "observation"  # watch, observe, monitor
    SEARCH = "search"  # find, search, discover
    LANGUAGE = "language"  # speak, define, grammar
    EVALUATION = "evaluation"  # judge, evaluate, assess
    EXECUTION = "execution"  # run, execute, deploy
    COMPOSITE = "composite"  # multiple intents combined


class RiskLevel(Enum):
    """Risk level for operations."""

    SAFE = "safe"  # Read-only, no side effects
    MODERATE = "moderate"  # Creates/modifies files
    ELEVATED = "elevated"  # Destructive, network, system


@dataclass
class Step:
    """A single step in the execution plan."""

    id: int
    command: str
    args: list[str]
    description: str
    risk: RiskLevel = RiskLevel.SAFE
    condition: str | None = None  # e.g., "if step 1 found issues"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "command": self.command,
            "args": self.args,
            "description": self.description,
            "risk": self.risk.value,
            "condition": self.condition,
        }

    def render_cli(self) -> str:
        """Render as CLI command string."""
        args_str = " ".join(self.args) if self.args else ""
        return f"kgents {self.command} {args_str}".strip()


@dataclass
class ExecutionPlan:
    """A plan for executing a complex intent."""

    intent: str
    category: IntentCategory
    confidence: float
    risk_level: RiskLevel
    steps: list[Step] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "category": self.category.value,
            "confidence": self.confidence,
            "risk_level": self.risk_level.value,
            "steps": [s.to_dict() for s in self.steps],
            "notes": self.notes,
        }


# =============================================================================
# Intent Classification
# =============================================================================


# Keyword patterns for intent classification
INTENT_PATTERNS = {
    IntentCategory.CREATION: [
        r"\b(create|new|scaffold|generate|make|build)\b",
    ],
    IntentCategory.VERIFICATION: [
        r"\b(check|verify|validate|test|ensure|confirm)\b",
    ],
    IntentCategory.REPAIR: [
        r"\b(fix|repair|correct|heal|restore|patch)\b",
    ],
    IntentCategory.ANALYSIS: [
        r"\b(think|analyze|review|examine|investigate|explore|understand)\b",
    ],
    IntentCategory.OBSERVATION: [
        r"\b(watch|observe|monitor|track|follow)\b",
    ],
    IntentCategory.SEARCH: [
        r"\b(find|search|discover|locate|lookup|look up)\b",
    ],
    IntentCategory.LANGUAGE: [
        r"\b(speak|define|grammar|dsl|language|tongue)\b",
    ],
    IntentCategory.EVALUATION: [
        r"\b(judge|evaluate|assess|rate|score|grade)\b",
    ],
    IntentCategory.EXECUTION: [
        r"\b(run|execute|deploy|launch|start|trigger)\b",
    ],
}

# Destructive keywords that elevate risk
DESTRUCTIVE_KEYWORDS = [
    r"\b(delete|remove|destroy|wipe|clear|purge|drop)\b",
    r"\b(deploy|push|publish|release)\b",
    r"\b(migrate|upgrade|convert)\b",
]


def classify_intent(intent: str) -> tuple[IntentCategory, float]:
    """
    Classify intent into category with confidence score.

    Returns tuple of (category, confidence).
    Uses keyword matching as lightweight classifier.
    """
    intent_lower = intent.lower()
    scores: dict[IntentCategory, float] = {}

    for category, patterns in INTENT_PATTERNS.items():
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, intent_lower):
                score += 0.3
        scores[category] = min(score, 1.0)

    # Check for composite (multiple categories detected)
    categories_detected = [c for c, s in scores.items() if s > 0]

    if len(categories_detected) > 1:
        # Weight composite by number of categories
        return IntentCategory.COMPOSITE, 0.7 + (0.05 * len(categories_detected))
    elif len(categories_detected) == 1:
        return categories_detected[0], scores[categories_detected[0]]
    else:
        # Default to analysis if we can't classify
        return IntentCategory.ANALYSIS, 0.3


def assess_risk(intent: str, steps: list[Step]) -> RiskLevel:
    """Assess risk level for intent and steps."""
    intent_lower = intent.lower()

    # Check for destructive keywords
    for pattern in DESTRUCTIVE_KEYWORDS:
        if re.search(pattern, intent_lower):
            return RiskLevel.ELEVATED

    # Check step risk levels
    step_risks = [s.risk for s in steps]
    if RiskLevel.ELEVATED in step_risks:
        return RiskLevel.ELEVATED
    if RiskLevel.MODERATE in step_risks:
        return RiskLevel.MODERATE

    return RiskLevel.SAFE


# =============================================================================
# Plan Generation
# =============================================================================


def extract_targets(intent: str) -> list[str]:
    """Extract file/directory targets from intent."""
    targets = []

    # Look for file paths
    file_patterns = [
        r"([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)",  # file.ext
        r"(\./[a-zA-Z0-9_\-./]+)",  # ./path
        r"(src/[a-zA-Z0-9_\-./]*)",  # src/...
        r"(tests?/[a-zA-Z0-9_\-./]*)",  # test/...
    ]

    for pattern in file_patterns:
        matches = re.findall(pattern, intent)
        targets.extend(matches)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique


def generate_plan(intent: str) -> ExecutionPlan:
    """
    Generate execution plan from natural language intent.

    This is the core planning engine that translates intent to steps.
    """
    category, confidence = classify_intent(intent)
    targets = extract_targets(intent)
    intent_lower = intent.lower()

    steps: list[Step] = []
    step_id = 1

    # Generate steps based on category and keywords
    if category == IntentCategory.VERIFICATION or "check" in intent_lower:
        target = targets[0] if targets else "."
        steps.append(
            Step(
                id=step_id,
                command="check",
                args=[target],
                description=f"Verify {target} against principles",
                risk=RiskLevel.SAFE,
            )
        )
        step_id += 1

    if category == IntentCategory.REPAIR or "fix" in intent_lower:
        target = targets[0] if targets else "."
        condition = f"if step {step_id - 1} found issues" if steps else None
        steps.append(
            Step(
                id=step_id,
                command="fix",
                args=[target],
                description=f"Repair {target}",
                risk=RiskLevel.MODERATE,
                condition=condition,
            )
        )
        step_id += 1

    if (
        category == IntentCategory.ANALYSIS
        or "think" in intent_lower
        or "analyze" in intent_lower
    ):
        # Extract topic from intent
        topic = intent.replace("think about", "").replace("analyze", "").strip()
        steps.append(
            Step(
                id=step_id,
                command="think",
                args=[f'"{topic}"'],
                description=f"Generate hypotheses about: {topic[:50]}",
                risk=RiskLevel.SAFE,
            )
        )
        step_id += 1

    if category == IntentCategory.EVALUATION or "judge" in intent_lower:
        target = targets[0] if targets else intent
        steps.append(
            Step(
                id=step_id,
                command="judge",
                args=[f'"{target}"' if not targets else target],
                description="Evaluate against 7 principles",
                risk=RiskLevel.SAFE,
            )
        )
        step_id += 1

    if (
        category == IntentCategory.EXECUTION
        or "run" in intent_lower
        or "test" in intent_lower
    ):
        # Extract intent for run
        run_intent = intent.replace("run", "").replace("execute", "").strip()
        steps.append(
            Step(
                id=step_id,
                command="run",
                args=[f'"{run_intent}"'],
                description=f"Execute: {run_intent[:50]}",
                risk=RiskLevel.MODERATE,
            )
        )
        step_id += 1

    if category == IntentCategory.OBSERVATION or "watch" in intent_lower:
        target = targets[0] if targets else "."
        steps.append(
            Step(
                id=step_id,
                command="watch",
                args=[target],
                description=f"Observe {target}",
                risk=RiskLevel.SAFE,
            )
        )
        step_id += 1

    if category == IntentCategory.SEARCH or "find" in intent_lower:
        # Extract query from intent
        query = intent.replace("find", "").replace("search for", "").strip()
        steps.append(
            Step(
                id=step_id,
                command="find",
                args=[f'"{query}"'],
                description=f"Search catalog for: {query[:50]}",
                risk=RiskLevel.SAFE,
            )
        )
        step_id += 1

    if (
        category == IntentCategory.LANGUAGE
        or "speak" in intent_lower
        or "tongue" in intent_lower
    ):
        # Extract domain from intent
        domain = intent.replace("speak", "").replace("create tongue for", "").strip()
        steps.append(
            Step(
                id=step_id,
                command="speak",
                args=[f'"{domain}"'],
                description=f"Create tongue for: {domain[:50]}",
                risk=RiskLevel.MODERATE,
            )
        )
        step_id += 1

    if (
        category == IntentCategory.CREATION
        or "create" in intent_lower
        or "new" in intent_lower
    ):
        # Extract what to create
        if "agent" in intent_lower:
            name = targets[0] if targets else "new-agent"
            steps.append(
                Step(
                    id=step_id,
                    command="new",
                    args=["agent", f'"{name}"'],
                    description=f"Create agent: {name}",
                    risk=RiskLevel.MODERATE,
                )
            )
        elif "flow" in intent_lower:
            name = targets[0] if targets else "new-flow"
            steps.append(
                Step(
                    id=step_id,
                    command="new",
                    args=["flow", f'"{name}"'],
                    description=f"Create flowfile: {name}",
                    risk=RiskLevel.MODERATE,
                )
            )
        step_id += 1

    # Handle composite intents (multiple actions detected)
    if category == IntentCategory.COMPOSITE and not steps:
        # Re-analyze with all patterns
        for cat, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, intent_lower):
                    # Recursively generate for each detected category
                    sub_plan = _generate_single_category_step(
                        cat, intent, targets, step_id
                    )
                    if sub_plan:
                        steps.append(sub_plan)
                        step_id += 1

    # Fallback: if no steps, do analysis
    if not steps:
        steps.append(
            Step(
                id=1,
                command="think",
                args=[f'"{intent}"'],
                description=f"Analyze: {intent[:50]}",
                risk=RiskLevel.SAFE,
            )
        )

    # Assess overall risk
    risk_level = assess_risk(intent, steps)

    # Generate notes
    notes = []
    if risk_level == RiskLevel.ELEVATED:
        notes.append("This plan includes destructive operations. Review carefully.")
    if category == IntentCategory.COMPOSITE:
        notes.append("Multiple intents detected. Steps will execute sequentially.")

    return ExecutionPlan(
        intent=intent,
        category=category,
        confidence=confidence,
        risk_level=risk_level,
        steps=steps,
        notes=notes,
    )


def _generate_single_category_step(
    category: IntentCategory,
    intent: str,
    targets: list[str],
    step_id: int,
) -> Step | None:
    """Generate a single step for a category."""
    target = targets[0] if targets else "."

    category_to_command = {
        IntentCategory.VERIFICATION: ("check", [target], RiskLevel.SAFE),
        IntentCategory.REPAIR: ("fix", [target], RiskLevel.MODERATE),
        IntentCategory.OBSERVATION: ("watch", [target], RiskLevel.SAFE),
        IntentCategory.SEARCH: ("find", [f'"{intent}"'], RiskLevel.SAFE),
        IntentCategory.EVALUATION: ("judge", [target], RiskLevel.SAFE),
    }

    if category in category_to_command:
        cmd, args, risk = category_to_command[category]
        return Step(
            id=step_id,
            command=cmd,
            args=args,
            description=f"{cmd.title()} operation",
            risk=risk,
        )

    return None


# =============================================================================
# Execution
# =============================================================================


async def execute_plan_async(plan: ExecutionPlan) -> dict:
    """
    Execute a plan, running each step via actual agent handlers.

    Returns execution results.
    """
    from protocols.cli.mcp.server import (
        handle_check,
        handle_find,
        handle_fix,
        handle_judge,
        handle_speak,
        handle_think,
    )

    # Map commands to handlers
    command_handlers = {
        "check": lambda args: handle_check(args[0] if args else "."),
        "judge": lambda args: handle_judge(args[0] if args else ""),
        "think": lambda args: handle_think(args[0].strip('"') if args else ""),
        "fix": lambda args: handle_fix(args[0] if args else ""),
        "speak": lambda args: handle_speak(args[0].strip('"') if args else ""),
        "find": lambda args: handle_find(args[0].strip('"') if args else ""),
    }

    results = []
    prev_result = None

    for step in plan.steps:
        # Check condition (simple evaluation)
        if step.condition and prev_result:
            # Skip if condition references previous success but it failed
            if (
                "found issues" in step.condition
                and prev_result.get("status") != "issues_found"
            ):
                results.append(
                    {
                        "step_id": step.id,
                        "command": step.render_cli(),
                        "status": "skipped",
                        "output": f"Condition not met: {step.condition}",
                    }
                )
                continue

        # Execute step via actual handler
        handler = command_handlers.get(step.command)
        if handler:
            try:
                mcp_result = await handler(step.args)
                result = {
                    "step_id": step.id,
                    "command": step.render_cli(),
                    "status": "success" if mcp_result.success else "failed",
                    "output": mcp_result.content[:500] if mcp_result.content else "",
                }
            except Exception as e:
                result = {
                    "step_id": step.id,
                    "command": step.render_cli(),
                    "status": "error",
                    "output": f"Error: {e}",
                }
        else:
            # Fallback for commands without handlers
            result = {
                "step_id": step.id,
                "command": step.render_cli(),
                "status": "pending",
                "output": f"Handler not implemented for: {step.command}",
            }

        results.append(result)
        prev_result = result

    return {
        "plan": plan.to_dict(),
        "executed": len([r for r in results if r["status"] == "success"]),
        "total": len(results),
        "results": results,
    }


def execute_plan(plan: ExecutionPlan) -> dict:
    """
    Execute a plan synchronously (wrapper for async execution).

    Returns execution results.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, execute_plan_async(plan))
                return future.result()
        else:
            return loop.run_until_complete(execute_plan_async(plan))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(execute_plan_async(plan))


# =============================================================================
# CLI Handler
# =============================================================================

DO_HELP = """\
kgents do - Natural language intent router

USAGE:
  kgents do "<intent>" [options]

The 'do' command takes complex, multi-step natural language intents
and generates an execution plan. Plans are shown for confirmation
before execution (dry-run by design).

OPTIONS:
  --yes, -y             Execute without confirmation
  --dry-run             Show plan only, don't offer to execute
  --export=<path>       Export plan as flowfile
  --verbose             Show detailed plan reasoning
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents do "take input.py, check it against the laws, and fix any issues"
  kgents do "analyze the codebase and generate hypotheses"
  kgents do "find all parsers and verify they follow principles"
  kgents do "clean up the temp folder" --dry-run

SAFETY:
  - Plans are shown before execution (unless --yes)
  - Destructive operations require explicit confirmation
  - Default answer is NO for elevated-risk operations
"""


def cmd_do(args: list[str]) -> int:
    """Natural language intent router."""
    if not args or args[0] in ("--help", "-h"):
        print(DO_HELP)
        return 0

    # Parse options
    opts = {}
    positional = []

    for arg in args:
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                opts[key.replace("-", "_")] = value
            else:
                opts[arg[2:].replace("-", "_")] = True
        elif arg in ("-y",):
            opts["yes"] = True
        else:
            positional.append(arg)

    use_json = opts.get("format") == "json"
    dry_run = opts.get("dry_run", False)
    auto_yes = opts.get("yes", False)
    export_path = opts.get("export")
    verbose = opts.get("verbose", False)

    if not positional:
        print("Error: do requires an intent")
        print('Usage: kgents do "<intent>"')
        print('Example: kgents do "check and fix input.py"')
        return 1

    intent = positional[0].strip('"').strip("'")

    # Generate plan
    plan = generate_plan(intent)

    if use_json:
        print(json.dumps(plan.to_dict(), indent=2))
        if not dry_run and not auto_yes:
            return 0  # JSON mode doesn't prompt
    else:
        _print_plan_rich(plan, verbose)

    # Export if requested
    if export_path:
        _export_as_flowfile(plan, export_path)
        print(f"\nExported plan to: {export_path}")

    # Dry run - don't execute
    if dry_run:
        return 0

    # Prompt for execution (unless auto-yes)
    if not auto_yes and not use_json:
        # Determine default based on risk
        if plan.risk_level == RiskLevel.ELEVATED:
            prompt = "Execute? [y/N] "  # Default NO
            default = False
        else:
            prompt = "Execute? [Y/n] "  # Default YES
            default = True

        try:
            response = input(prompt).strip().lower()
            if not response:
                should_execute = default
            else:
                should_execute = response in ("y", "yes")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled")
            return 0

        if not should_execute:
            print("Plan cancelled")
            return 0

    # Execute the plan
    result = execute_plan(plan)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Execution Complete ===")
        print(f"Steps executed: {result['executed']}")
        for r in result["results"]:
            status_icon = "+" if r["status"] == "success" else "x"
            print(f"  [{status_icon}] {r['command']}")

    return 0


def _print_plan_rich(plan: ExecutionPlan, verbose: bool) -> None:
    """Print plan in rich format with box drawing."""
    # Header
    risk_indicator = {
        RiskLevel.SAFE: "",
        RiskLevel.MODERATE: " [MODERATE RISK]",
        RiskLevel.ELEVATED: " [ELEVATED RISK]",
    }

    print()
    print("+" + "-" * 60 + "+")
    print(f"| Intent Detected{risk_indicator.get(plan.risk_level, '')}".ljust(61) + "|")
    print("+" + "-" * 60 + "+")
    print(f"| Category: {plan.category.value.title()}".ljust(61) + "|")
    print(f"| Confidence: {plan.confidence:.2f}".ljust(61) + "|")
    print("|" + " " * 60 + "|")
    print("| Generated Plan:".ljust(61) + "|")

    for step in plan.steps:
        cmd_line = f"|   {step.id}. {step.render_cli()}"
        print(cmd_line.ljust(61) + "|")
        if step.condition:
            cond_line = f"|      ({step.condition})"
            print(cond_line.ljust(61) + "|")

    if plan.notes:
        print("|" + " " * 60 + "|")
        for note in plan.notes:
            note_line = f"| Note: {note}"
            # Wrap long notes
            while len(note_line) > 60:
                print(note_line[:60].ljust(61) + "|")
                note_line = "|   " + note_line[60:]
            print(note_line.ljust(61) + "|")

    print("+" + "-" * 60 + "+")
    print()


def _export_as_flowfile(plan: ExecutionPlan, path: str) -> None:
    """Export plan as a flowfile."""
    import yaml

    flowfile = {
        "version": "1.0",
        "name": f"Generated from: {plan.intent[:50]}",
        "description": f"Auto-generated flow for intent: {plan.intent}",
        "steps": [],
    }

    for step in plan.steps:
        flow_step = {
            "id": f"step_{step.id}",
            "command": step.command,
            "args": step.args,
        }
        if step.condition:
            flow_step["condition"] = step.condition
        flowfile["steps"].append(flow_step)

    with open(path, "w") as f:
        yaml.dump(flowfile, f, default_flow_style=False)
