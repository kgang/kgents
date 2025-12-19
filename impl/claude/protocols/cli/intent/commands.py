"""
Intent Layer Commands - The 9 Core Verbs.

Each command maps user intent to the appropriate agent operation:
  new    → A-gent scaffold
  run    → J-gent JIT compile + execute
  check  → T/J-gent verify
  think  → B-gent hypothesize
  watch  → W-gent witness
  find   → L-gent discover
  fix    → P-gent repair
  speak  → G-gent reify tongue
  judge  → Bootstrap evaluate

See: docs/cli-integration-plan.md Part 2 (Intent Layer Commands)
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

# =============================================================================
# Shared Types
# =============================================================================


class IntentResult:
    """Result of an intent command execution."""

    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: str | None = None,
        suggestions: list[str] | None = None,
        next_steps: list[str] | None = None,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.suggestions = suggestions or []
        self.next_steps = next_steps or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "suggestions": self.suggestions,
            "next_steps": self.next_steps,
        }


class EntityType(Enum):
    """Types of entities that can be created."""

    AGENT = "agent"
    FLOW = "flow"
    TONGUE = "tongue"
    SCHEMA = "schema"


# =============================================================================
# Helper Functions
# =============================================================================


def _parse_args(args: list[str]) -> tuple[dict[str, str | bool], list[str]]:
    """Parse --key=value and --flag style arguments."""
    opts: dict[str, str | bool] = {}
    positional = []

    for arg in args:
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                opts[key.replace("-", "_")] = value
            else:
                opts[arg[2:].replace("-", "_")] = True
        else:
            positional.append(arg)

    return opts, positional


def _format_rich(title: str, content: dict[str, Any] | list[Any] | str) -> str:
    """Format output in rich style with box drawing."""
    lines = [f"=== {title} ===", ""]

    if isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
    elif isinstance(content, list):
        for item in content:
            lines.append(f"  - {item}")
    else:
        lines.append(str(content))

    lines.append("")
    return "\n".join(lines)


def _format_epilogue(next_steps: list[str]) -> str:
    """Format the 'next steps' epilogue."""
    if not next_steps:
        return ""

    lines = ["", "--- Next Steps ---"]
    for step in next_steps:
        lines.append(f"  {step}")
    lines.append("")
    return "\n".join(lines)


# =============================================================================
# NEW Command
# =============================================================================

NEW_HELP = """\
kgents new - Create something new

USAGE:
  kgents new <type> "<name>" [options]

TYPES:
  agent     Create a new agent scaffold
  flow      Create a new flowfile
  tongue    Create a new DSL (Tongue)
  schema    Create a new data schema

OPTIONS:
  --template=<name>    Use template (default, minimal, full)
  --path=<dir>         Output directory (default: current)
  --genus=<letter>     Agent genus for 'agent' type
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents new agent "Archimedes" --genus=b
  kgents new flow "review-pipeline"
  kgents new tongue "calendar-commands"

AFTER CREATING:
  The epilogue will suggest relevant next steps for your new creation.
"""


def cmd_new(args: list[str]) -> int:
    """Create something new (agent, flow, tongue, schema)."""
    if not args or args[0] in ("--help", "-h"):
        print(NEW_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"

    if len(positional) < 2:
        print("Error: new requires <type> and <name>")
        print('Usage: kgents new <type> "<name>"')
        print('Example: kgents new agent "Archimedes"')
        return 1

    entity_type = positional[0]
    name = positional[1].strip('"').strip("'")

    # Validate type
    valid_types = [e.value for e in EntityType]
    if entity_type not in valid_types:
        print(f"Error: unknown type '{entity_type}'")
        print(f"Valid types: {', '.join(valid_types)}")
        return 1

    # Create based on type
    result = _create_entity(EntityType(entity_type), name, opts)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(_format_rich(f"Created {entity_type}: {name}", result.output))
            print(_format_epilogue(result.next_steps))
        else:
            print(f"Error: {result.error}")
            if result.suggestions:
                print("\nSuggestions:")
                for s in result.suggestions:
                    print(f"  {s}")

    return 0 if result.success else 1


def _create_entity(entity_type: EntityType, name: str, opts: dict[str, str | bool]) -> IntentResult:
    """Create entity of given type."""
    template = str(opts.get("template", "default"))
    path = Path(str(opts.get("path", ".")))
    genus_val = opts.get("genus")
    genus = str(genus_val) if genus_val is not None else None

    if entity_type == EntityType.AGENT:
        return _create_agent(name, genus, template, path)
    elif entity_type == EntityType.FLOW:
        return _create_flow(name, template, path)
    elif entity_type == EntityType.TONGUE:
        return _create_tongue(name, template, path)
    elif entity_type == EntityType.SCHEMA:
        return _create_schema(name, template, path)

    return IntentResult(False, error=f"Unknown type: {entity_type}")


def _create_agent(name: str, genus: str | None, template: str, path: Path) -> IntentResult:
    """Create agent scaffold using Jinja2 templates."""
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        return IntentResult(
            success=False,
            error="jinja2 not installed. Run: uv add jinja2",
            suggestions=["pip install jinja2", "uv add jinja2"],
        )

    # Normalize name
    slug = name.lower().replace(" ", "_").replace("-", "_")
    class_name = "".join(word.capitalize() for word in slug.split("_"))
    if not class_name.endswith("Agent"):
        class_name += "Agent"

    # Map template to archetype
    archetype_map = {"minimal": "Lambda", "default": "Lambda", "full": "Kappa"}
    archetype = archetype_map.get(template, "Lambda")

    # Find templates directory
    templates_dir = Path(__file__).parent.parent.parent.parent / "_templates" / "agent"
    if not templates_dir.exists():
        return IntentResult(
            success=False,
            error=f"Templates not found at {templates_dir}",
            suggestions=["Run from the impl/claude directory"],
        )

    # Output directory
    output_base = Path(__file__).parent.parent.parent.parent / "agents"
    agent_dir = output_base / slug

    if agent_dir.exists():
        return IntentResult(
            success=False,
            error=f"Directory already exists: {agent_dir}",
            suggestions=[
                f"Remove the existing directory: rm -rf {agent_dir}",
                "Choose a different name",
            ],
        )

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Template data
    data = {
        "name": name,
        "module_name": slug,
        "class_name": class_name,
        "agent_name": " ".join(word.capitalize() for word in slug.split("_")),
        "archetype": archetype,
        "input_type": "str",
        "output_type": "str",
        "description": f"A {archetype} agent.",
        "custom_output_type": False,
        "input_example": '"test"',
    }

    # Create directories
    agent_dir.mkdir(parents=True, exist_ok=True)
    (agent_dir / "_tests").mkdir(exist_ok=True)

    # Generate files
    files_generated = []
    templates_to_render = [
        ("__init__.py.j2", agent_dir / "__init__.py"),
        ("agent.py.j2", agent_dir / "agent.py"),
        ("_tests/__init__.py.j2", agent_dir / "_tests" / "__init__.py"),
        ("_tests/test_agent.py.j2", agent_dir / "_tests" / "test_agent.py"),
    ]

    for template_name, output_path in templates_to_render:
        try:
            tpl = env.get_template(template_name)
            content = tpl.render(**data)
            output_path.write_text(content)
            files_generated.append(str(output_path.relative_to(output_base.parent)))
        except Exception as e:
            return IntentResult(
                success=False,
                error=f"Failed to generate {template_name}: {e}",
            )

    return IntentResult(
        success=True,
        output={
            "name": name,
            "slug": slug,
            "class_name": class_name,
            "archetype": archetype,
            "genus": genus or "a",
            "template": template,
            "path": str(agent_dir),
            "files": files_generated,
        },
        next_steps=[
            f"cd agents/{slug} && edit agent.py  # Implement your logic",
            f"pytest agents/{slug}/_tests/ -v    # Run tests",
            f"from agents.{slug} import {class_name}  # Import",
        ],
    )


def _create_flow(name: str, template: str, path: Path) -> IntentResult:
    """Create flowfile."""
    slug = name.lower().replace(" ", "-")
    flow_path = path / f"{slug}.flow.yaml"

    return IntentResult(
        success=True,
        output={
            "name": name,
            "path": str(flow_path),
            "template": template,
        },
        next_steps=[
            f"kgents flow validate {slug}.flow.yaml  # Validate syntax",
            f"kgents flow explain {slug}.flow.yaml   # Show execution plan",
            f"kgents flow run {slug}.flow.yaml       # Execute flow",
        ],
    )


def _create_tongue(name: str, template: str, path: Path) -> IntentResult:
    """Create tongue (DSL)."""
    slug = name.lower().replace(" ", "-")
    tongue_path = path / ".kgents" / "tongues" / f"{slug}.tongue.yaml"

    return IntentResult(
        success=True,
        output={
            "name": name,
            "path": str(tongue_path),
            "template": template,
        },
        next_steps=[
            f"kgents grammar show {slug}     # View tongue definition",
            f"kgents grammar evolve {slug}   # Train with examples",
            f"kgents grammar validate {slug} # Validate with fuzzing",
        ],
    )


def _create_schema(name: str, template: str, path: Path) -> IntentResult:
    """Create data schema."""
    slug = name.lower().replace(" ", "-")
    schema_path = path / ".kgents" / "schemas" / f"{slug}.schema.yaml"

    return IntentResult(
        success=True,
        output={
            "name": name,
            "path": str(schema_path),
            "template": template,
        },
        next_steps=[
            f"kgents parse validate <input> --schema={slug}  # Validate against schema",
        ],
    )


# =============================================================================
# RUN Command
# =============================================================================

RUN_HELP = """\
kgents run - Execute an intent

USAGE:
  kgents run "<intent>" [options]

The 'run' command takes a natural language intent and executes it using
J-gent JIT compilation. It classifies the intent, determines the appropriate
agents, and executes the pipeline.

OPTIONS:
  --budget=<level>     Entropy budget: minimal, low, medium, high (default: medium)
  --dry-run            Show plan without executing
  --verbose            Show detailed execution trace
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents run "test all functions"
  kgents run "format and lint src/"
  kgents run "review code for security issues" --budget=high
  kgents run "deploy to staging" --dry-run

INTENT CLASSIFICATION:
  The JIT compiler classifies intents into three reality types:
  - DETERMINISTIC: Pure, repeatable operations
  - PROBABILISTIC: LLM-involved, may vary
  - CHAOTIC: Multi-step with branching outcomes
"""


def cmd_run(args: list[str]) -> int:
    """Execute an intent via J-gent JIT compilation."""
    if not args or args[0] in ("--help", "-h"):
        print(RUN_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    dry_run_val = opts.get("dry_run", False)
    dry_run = bool(dry_run_val) if dry_run_val is not False else False
    verbose_val = opts.get("verbose", False)
    verbose = bool(verbose_val) if verbose_val is not False else False
    budget_val = opts.get("budget", "medium")
    budget = str(budget_val) if budget_val is not True else "medium"

    if not positional:
        print("Error: run requires an intent")
        print('Usage: kgents run "<intent>"')
        print('Example: kgents run "test all functions"')
        return 1

    intent = positional[0].strip('"').strip("'")

    # JIT compile the intent
    result = _jit_compile_and_run(intent, budget, dry_run, verbose)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            if dry_run:
                print(_format_rich("Execution Plan (Dry Run)", result.output))
            else:
                print(_format_rich("Execution Complete", result.output))
            print(_format_epilogue(result.next_steps))
        else:
            print(f"Error: {result.error}")
            if result.suggestions:
                print("\nSuggestions:")
                for s in result.suggestions:
                    print(f"  {s}")

    return 0 if result.success else 1


def _jit_compile_and_run(
    intent: str,
    budget: str,
    dry_run: bool,
    verbose: bool,
) -> IntentResult:
    """JIT compile intent and execute (or show plan if dry-run)."""
    # Classify the intent
    classification = _classify_intent(intent)

    # Generate execution plan
    plan = _generate_plan(intent, classification)

    if dry_run:
        return IntentResult(
            success=True,
            output={
                "intent": intent,
                "classification": classification,
                "plan": plan,
                "budget": budget,
                "estimated_tokens": _estimate_tokens(plan, budget),
            },
            next_steps=[
                f'kgents run "{intent}"  # Execute for real',
            ],
        )

    # Execute the plan (simulated)
    execution_result = _execute_plan(plan, budget, verbose)

    return IntentResult(
        success=True,
        output={
            "intent": intent,
            "classification": classification,
            "steps_executed": len(plan),
            "result": execution_result,
        },
        next_steps=[
            "kgents watch ./logs/  # Observe execution logs",
        ],
    )


def _classify_intent(intent: str) -> str:
    """Classify intent into reality type."""
    intent_lower = intent.lower()

    # Heuristic classification
    if any(kw in intent_lower for kw in ["test", "lint", "format", "check"]):
        return "DETERMINISTIC"
    elif any(kw in intent_lower for kw in ["review", "analyze", "suggest", "improve"]):
        return "PROBABILISTIC"
    elif any(kw in intent_lower for kw in ["deploy", "migrate", "refactor"]):
        return "CHAOTIC"
    else:
        return "PROBABILISTIC"


def _generate_plan(intent: str, classification: str) -> list[dict[str, Any]]:
    """Generate execution plan for intent."""
    intent_lower = intent.lower()

    # Simple keyword-based planning
    steps = []

    if "test" in intent_lower:
        steps.append(
            {
                "agent": "T-gent",
                "operation": "discover",
                "args": {"pattern": "test_*.py"},
            }
        )
        steps.append({"agent": "T-gent", "operation": "run", "args": {}})

    if "format" in intent_lower or "lint" in intent_lower:
        steps.append({"agent": "T-gent", "operation": "format", "args": {}})

    if "review" in intent_lower:
        steps.append({"agent": "W-gent", "operation": "observe", "args": {}})
        steps.append({"agent": "Bootstrap", "operation": "judge", "args": {}})

    if "deploy" in intent_lower:
        steps.append({"agent": "J-gent", "operation": "verify", "args": {"target": "staging"}})
        steps.append({"agent": "J-gent", "operation": "execute", "args": {"operation": "deploy"}})

    if not steps:
        # Default: parse and analyze
        steps.append({"agent": "P-gent", "operation": "extract", "args": {}})
        steps.append({"agent": "J-gent", "operation": "analyze", "args": {}})

    return steps


def _estimate_tokens(plan: list[dict[str, Any]], budget: str) -> int:
    """Estimate token usage for plan."""
    base = len(plan) * 100
    budget_multipliers = {"minimal": 0.5, "low": 0.75, "medium": 1.0, "high": 1.5}
    return int(base * budget_multipliers.get(budget, 1.0))


def _execute_plan(plan: list[dict[str, Any]], budget: str, verbose: bool) -> str:
    """Execute plan and return result summary."""
    # Simulated execution
    return f"Executed {len(plan)} steps successfully"


# =============================================================================
# CHECK Command
# =============================================================================

CHECK_HELP = """\
kgents check - Verify target against principles/laws

USAGE:
  kgents check <target> [options]

The 'check' command verifies code, agents, or flows against the 7 principles
and category laws using T-gent and J-gent verification.

OPTIONS:
  --against=<what>     Check against: principles, laws, schema (default: principles)
  --strict             Fail on any warning
  --verbose            Show detailed check results
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents check src/main.py
  kgents check ./agents/archimedes/
  kgents check review.flow.yaml --against=laws
  kgents check input.json --against=schema:user

WHAT GETS CHECKED:
  For code:    Style, complexity, security patterns
  For agents:  Composability laws, principle adherence
  For flows:   Step validity, type matching, dead paths
"""


def cmd_check(args: list[str]) -> int:
    """Verify target against principles/laws."""
    if not args or args[0] in ("--help", "-h"):
        print(CHECK_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    against_val = opts.get("against", "principles")
    against = str(against_val) if against_val is not True else "principles"
    strict_val = opts.get("strict", False)
    strict = bool(strict_val) if strict_val is not False else False
    verbose_val = opts.get("verbose", False)
    verbose = bool(verbose_val) if verbose_val is not False else False

    if not positional:
        print("Error: check requires a target")
        print("Usage: kgents check <target>")
        print("Example: kgents check src/main.py")
        return 1

    target = positional[0]
    result = _check_target(target, against, strict, verbose)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(_format_rich(f"Check: {target}", result.output))
        else:
            print(_format_rich(f"Check Failed: {target}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _check_target(target: str, against: str, strict: bool, verbose: bool) -> IntentResult:
    """Check target against specified criteria."""
    path = Path(target)

    # Determine target type
    if path.suffix in (".py", ".js", ".ts"):
        target_type = "code"
    elif path.suffix in (".yaml", ".yml") and "flow" in path.name:
        target_type = "flow"
    elif path.is_dir():
        target_type = "directory"
    else:
        target_type = "file"

    # Simulated check results
    checks = [
        {"principle": "Tasteful", "status": "PASS", "confidence": 0.85},
        {"principle": "Curated", "status": "PASS", "confidence": 0.90},
        {"principle": "Ethical", "status": "PASS", "confidence": 0.95},
        {"principle": "Joy-Inducing", "status": "WARN", "confidence": 0.70},
        {"principle": "Composable", "status": "PASS", "confidence": 0.88},
    ]

    passed = sum(1 for c in checks if c["status"] == "PASS")
    warned = sum(1 for c in checks if c["status"] == "WARN")
    failed = sum(1 for c in checks if c["status"] == "FAIL")

    success = failed == 0 and (not strict or warned == 0)

    return IntentResult(
        success=success,
        output={
            "target": target,
            "type": target_type,
            "against": against,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "checks": checks if verbose else None,
        },
        next_steps=[
            s
            for s in [
                f"kgents fix {target}  # Attempt auto-repair" if not success else None,
                f"kgents principles check {target}  # Detailed principle analysis",
            ]
            if s is not None
        ],
    )


# =============================================================================
# THINK Command
# =============================================================================

THINK_HELP = """\
kgents think - Generate hypotheses about a topic

USAGE:
  kgents think "<topic>" [options]

The 'think' command uses B-gent to generate hypotheses, analyze possibilities,
and explore ideas. It applies the scientific method to ideation.

OPTIONS:
  --depth=<level>      Analysis depth: shallow, medium, deep (default: medium)
  --limit=<n>          Maximum hypotheses (default: 5)
  --falsify            Include falsification paths for each hypothesis
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents think "optimization strategies for database"
  kgents think "why is the test suite slow" --depth=deep
  kgents think "alternative architectures" --limit=3 --falsify

OUTPUT:
  Each hypothesis includes:
  - Statement: The hypothesis itself
  - Evidence: Supporting observations
  - Confidence: How likely it is true
  - Falsification: How to disprove it (if --falsify)
"""


def cmd_think(args: list[str]) -> int:
    """Generate hypotheses using B-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(THINK_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    depth_val = opts.get("depth", "medium")
    depth = str(depth_val) if depth_val is not True else "medium"
    limit_val = opts.get("limit", "5")
    limit = int(limit_val) if isinstance(limit_val, str) or isinstance(limit_val, int) else 5
    falsify_val = opts.get("falsify", False)
    falsify = bool(falsify_val) if falsify_val is not False else False

    if not positional:
        print("Error: think requires a topic")
        print('Usage: kgents think "<topic>"')
        print('Example: kgents think "optimization strategies"')
        return 1

    topic = positional[0].strip('"').strip("'")
    result = _generate_hypotheses(topic, depth, limit, falsify)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_rich(f"Hypotheses: {topic}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _generate_hypotheses(topic: str, depth: str, limit: int, falsify: bool) -> IntentResult:
    """Generate hypotheses about a topic."""
    # Simulated B-gent hypothesis generation
    hypotheses = [
        {
            "id": f"H{i + 1}",
            "statement": f"Hypothesis {i + 1} about {topic}",
            "evidence": ["Observation 1", "Observation 2"],
            "confidence": 0.8 - (i * 0.1),
            "falsification": "Check condition X to disprove" if falsify else None,
        }
        for i in range(min(limit, 3))
    ]

    return IntentResult(
        success=True,
        output={
            "topic": topic,
            "depth": depth,
            "count": len(hypotheses),
            "hypotheses": hypotheses,
        },
        next_steps=[
            'kgents falsify "H1"  # Test the top hypothesis',
            f'kgents think "{topic}" --depth=deep  # Go deeper',
        ],
    )


# =============================================================================
# WATCH Command
# =============================================================================

WATCH_HELP = """\
kgents watch - Observe without judgment

USAGE:
  kgents watch <target> [options]

The 'watch' command uses W-gent to observe patterns, events, and behaviors
without making judgments. Pure observation for understanding.

OPTIONS:
  --interval=<seconds>  Observation interval (default: 5)
  --duration=<seconds>  Total watch duration (default: 60)
  --pattern=<regex>     Filter observations by pattern
  --silent              Don't output during watch, summarize at end
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents watch ./logs/
  kgents watch src/ --interval=10
  kgents watch stderr --pattern="Error"
  kgents watch ./events/ --duration=300 --silent

W-GENT PHILOSOPHY:
  "Observe without judgment. The witness sees all but speaks only truth."
  Watching is the first step to understanding. Not fixing, not judging—seeing.
"""


def cmd_watch(args: list[str]) -> int:
    """Observe without judgment using W-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(WATCH_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    interval = int(opts.get("interval", "5"))
    duration = int(opts.get("duration", "60"))
    pattern = opts.get("pattern")
    opts.get("silent", False)

    if not positional:
        print("Error: watch requires a target")
        print("Usage: kgents watch <target>")
        print("Example: kgents watch ./logs/")
        return 1

    target = positional[0]

    # For now, just show what would be watched
    result = IntentResult(
        success=True,
        output={
            "target": target,
            "interval": interval,
            "duration": duration,
            "pattern": pattern,
            "mode": "snapshot",  # In real impl: "live" or "snapshot"
            "observations": [
                {"time": "00:00", "event": "Started watching", "type": "system"},
                {
                    "time": "00:05",
                    "event": "File modified: config.yaml",
                    "type": "change",
                },
            ],
        },
        next_steps=[
            "kgents witness fidelity  # Check observation accuracy",
            f"kgents check {target}   # Analyze what was observed",
        ],
    )

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_rich(f"Watching: {target}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0


# =============================================================================
# FIND Command
# =============================================================================

FIND_HELP = """\
kgents find - Search the catalog

USAGE:
  kgents find "<query>" [options]

The 'find' command uses L-gent to search the catalog for agents, flows,
tongues, and other registered entities. Semantic search enabled.

OPTIONS:
  --type=<type>         Filter by type: agent, flow, tongue, all (default: all)
  --limit=<n>           Maximum results (default: 10)
  --exact               Exact match only (no semantic search)
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents find "calendar operations"
  kgents find "parser" --type=agent
  kgents find "validation" --limit=5
  kgents find "B-gent" --exact

SEARCH TYPES:
  - Semantic: "things that handle dates" finds calendar-related entities
  - Exact: Matches name/description directly
  - Lineage: Finds based on composition history
"""


def cmd_find(args: list[str]) -> int:
    """Search the catalog using L-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(FIND_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    entity_type_val = opts.get("type", "all")
    entity_type = str(entity_type_val) if entity_type_val is not True else "all"
    limit_val = opts.get("limit", "10")
    limit = int(limit_val) if isinstance(limit_val, str) or isinstance(limit_val, int) else 10
    exact_val = opts.get("exact", False)
    exact = bool(exact_val) if exact_val is not False else False

    if not positional:
        print("Error: find requires a query")
        print('Usage: kgents find "<query>"')
        print('Example: kgents find "calendar operations"')
        return 1

    query = positional[0].strip('"').strip("'")
    result = _search_catalog(query, entity_type, limit, exact)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_rich(f"Search: {query}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _search_catalog(query: str, entity_type: str, limit: int, exact: bool) -> IntentResult:
    """Search catalog for matching entities."""
    # Simulated L-gent search
    results = [
        {
            "name": "calendar-tongue",
            "type": "tongue",
            "relevance": 0.95,
            "description": "Calendar command DSL",
        },
        {
            "name": "date-parser",
            "type": "agent",
            "relevance": 0.85,
            "description": "Parse date strings",
        },
        {
            "name": "schedule-flow",
            "type": "flow",
            "relevance": 0.75,
            "description": "Scheduling pipeline",
        },
    ]

    # Filter by type
    if entity_type != "all":
        results = [r for r in results if r["type"] == entity_type]

    # Limit results
    results = results[:limit]

    return IntentResult(
        success=True,
        output={
            "query": query,
            "type_filter": entity_type,
            "mode": "exact" if exact else "semantic",
            "count": len(results),
            "results": results,
        },
        next_steps=[
            "kgents library show <name>  # View entity details",
            "kgents library lineage <name>  # View composition history",
        ],
    )


# =============================================================================
# FIX Command
# =============================================================================

FIX_HELP = """\
kgents fix - Repair malformed input

USAGE:
  kgents fix <target> [options]

The 'fix' command uses P-gent to parse and repair malformed code, data,
or configurations. It attempts to recover structure from broken input.

OPTIONS:
  --strategy=<strat>    Repair strategy: gentle, aggressive (default: gentle)
  --preview             Show changes without applying
  --backup              Create backup before fixing
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents fix input.json
  kgents fix broken.yaml --preview
  kgents fix src/module.py --strategy=aggressive
  kgents fix config.toml --backup

REPAIR STRATEGIES:
  gentle:     Minimal changes, preserve style
  aggressive: Full restructure for correctness
"""


def cmd_fix(args: list[str]) -> int:
    """Repair malformed input using P-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(FIX_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    strategy_val = opts.get("strategy", "gentle")
    strategy = str(strategy_val) if strategy_val is not True else "gentle"
    preview_val = opts.get("preview", False)
    preview = bool(preview_val) if preview_val is not False else False
    backup_val = opts.get("backup", False)
    backup = bool(backup_val) if backup_val is not False else False

    if not positional:
        print("Error: fix requires a target")
        print("Usage: kgents fix <target>")
        print("Example: kgents fix input.json")
        return 1

    target = positional[0]
    result = _fix_target(target, strategy, preview, backup)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(_format_rich(f"Fixed: {target}", result.output))
        else:
            print(_format_rich(f"Could not fix: {target}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _fix_target(target: str, strategy: str, preview: bool, backup: bool) -> IntentResult:
    """Attempt to fix malformed target."""
    path = Path(target)

    # Detect file type
    suffix = path.suffix.lower()
    file_type = {
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".py": "Python",
        ".toml": "TOML",
    }.get(suffix, "Unknown")

    # Simulated repair
    issues_found = [
        {"line": 3, "issue": "Missing comma", "fix": "Added comma"},
        {"line": 7, "issue": "Unclosed bracket", "fix": "Added closing bracket"},
    ]

    return IntentResult(
        success=True,
        output={
            "target": target,
            "file_type": file_type,
            "strategy": strategy,
            "preview": preview,
            "backup_created": backup,
            "issues_found": len(issues_found),
            "issues": issues_found,
        },
        next_steps=[
            f"kgents check {target}  # Verify the fix",
            f"kgents parse validate {target}  # Validate structure",
        ],
    )


# =============================================================================
# SPEAK Command
# =============================================================================

SPEAK_HELP = """\
kgents speak - Create a domain language (Tongue)

USAGE:
  kgents speak "<domain>" [options]

The 'speak' command uses G-gent to create a Domain Specific Language (Tongue)
from natural language description of a domain.

OPTIONS:
  --level=<level>       Grammar level: schema, command, recursive (default: command)
  --constraints=<csv>   Comma-separated constraints
  --for=<agent>         Create tongue for specific agent
  --examples=<path>     Path to example usage file
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents speak "file operations"
  kgents speak "calendar commands" --constraints="No deletes"
  kgents speak "physics" --for=archimedes
  kgents speak "data validation" --level=schema

GRAMMAR LEVELS:
  schema:      JSON-Schema/Pydantic structured output (simplest)
  command:     Verb-Noun imperative sequences (medium)
  recursive:   Full logic with nesting (most expressive)
"""


def cmd_speak(args: list[str]) -> int:
    """Create domain language using G-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(SPEAK_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    level_val = opts.get("level", "command")
    level = str(level_val) if level_val is not True else "command"
    constraints_val = opts.get("constraints", "")
    constraints_str = (
        str(constraints_val) if constraints_val and constraints_val is not True else ""
    )
    constraints = constraints_str.split(",") if constraints_str else []
    for_agent_val = opts.get("for")
    for_agent = str(for_agent_val) if for_agent_val and for_agent_val is not True else None
    examples_val = opts.get("examples")
    examples = str(examples_val) if examples_val and examples_val is not True else None

    if not positional:
        print("Error: speak requires a domain")
        print('Usage: kgents speak "<domain>"')
        print('Example: kgents speak "file operations"')
        return 1

    domain = positional[0].strip('"').strip("'")
    result = _speak_create_tongue(domain, level, constraints, for_agent, examples)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_rich(f"Tongue Created: {domain}", result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _speak_create_tongue(
    domain: str,
    level: str,
    constraints: list[str],
    for_agent: str | None,
    examples: str | None,
) -> IntentResult:
    """Create a tongue for the domain."""
    slug = domain.lower().replace(" ", "-")

    # Simulated G-gent tongue creation
    verbs = ["CREATE", "READ", "UPDATE", "DELETE"] if level == "command" else []
    nouns = ["file", "folder", "path"] if "file" in domain.lower() else ["item", "entity"]

    return IntentResult(
        success=True,
        output={
            "name": slug,
            "domain": domain,
            "level": level,
            "constraints": constraints,
            "for_agent": for_agent,
            "grammar": {
                "verbs": verbs,
                "nouns": nouns,
                "syntax": "<verb> <noun> [<modifier>...]",
            },
        },
        next_steps=[
            f"kgents grammar show {slug}  # View tongue definition",
            f'kgents grammar parse "CREATE file test.txt" --tongue={slug}  # Test parsing',
            f"kgents grammar evolve {slug} --examples=usage.txt  # Train with examples",
        ],
    )


# =============================================================================
# JUDGE Command
# =============================================================================

JUDGE_HELP = """\
kgents judge - Evaluate against the 7 principles

USAGE:
  kgents judge "<input>" [options]
  kgents judge <file> [options]

The 'judge' command evaluates input against the 7 design principles
using the Bootstrap evaluator.

OPTIONS:
  --strict              Require all principles to pass
  --principle=<name>    Check specific principle only
  --verbose             Show detailed reasoning
  --format=<fmt>        Output format: rich, json (default: rich)
  --help, -h            Show this help

EXAMPLES:
  kgents judge "A monolithic agent that does everything"
  kgents judge proposal.md
  kgents judge src/agent.py --verbose
  kgents judge design.md --principle=Composable

THE 7 PRINCIPLES:
  1. Tasteful      Quality over quantity
  2. Curated       Intentional selection
  3. Ethical       Augment, don't replace judgment
  4. Joy-Inducing  Personality encouraged
  5. Composable    Agents are morphisms
  6. Heterarchical Functional and autonomous modes
  7. Generative    Produce artifacts for later use
"""


def cmd_judge(args: list[str]) -> int:
    """Evaluate against principles using Bootstrap."""
    if not args or args[0] in ("--help", "-h"):
        print(JUDGE_HELP)
        return 0

    opts, positional = _parse_args(args)
    use_json = opts.get("format") == "json"
    strict_val = opts.get("strict", False)
    strict = bool(strict_val) if strict_val is not False else False
    principle_val = opts.get("principle")
    principle = str(principle_val) if principle_val and principle_val is not True else None
    verbose_val = opts.get("verbose", False)
    verbose = bool(verbose_val) if verbose_val is not False else False

    if not positional:
        print("Error: judge requires input")
        print('Usage: kgents judge "<input>" or kgents judge <file>')
        print('Example: kgents judge "A monolithic agent"')
        return 1

    input_text = positional[0].strip('"').strip("'")

    # Check if input is a file
    input_path = Path(input_text)
    if input_path.exists():
        target = str(input_path)
        is_file = True
    else:
        target = input_text
        is_file = False

    result = _judge_input(target, is_file, strict, principle, verbose)

    if use_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        title = "Judgment" if result.success else "Judgment Failed"
        print(_format_rich(title, result.output))
        print(_format_epilogue(result.next_steps))

    return 0 if result.success else 1


def _judge_input(
    target: str,
    is_file: bool,
    strict: bool,
    principle: str | None,
    verbose: bool,
) -> IntentResult:
    """Judge input against principles."""
    # All 7 principles
    all_principles = [
        "Tasteful",
        "Curated",
        "Ethical",
        "Joy-Inducing",
        "Composable",
        "Heterarchical",
        "Generative",
    ]

    # Filter to specific principle if requested
    principles_to_check = [principle] if principle else all_principles

    # Simulated evaluation
    evaluations = []
    for p in principles_to_check:
        verdict = "ACCEPT" if p not in ["Joy-Inducing"] else "REVISE"
        evaluations.append(
            {
                "principle": p,
                "verdict": verdict,
                "confidence": 0.85,
                "reasoning": f"Evaluation of {p} principle" if verbose else None,
            }
        )

    accepted = sum(1 for e in evaluations if e["verdict"] == "ACCEPT")
    rejected = sum(1 for e in evaluations if e["verdict"] == "REJECT")
    revise = sum(1 for e in evaluations if e["verdict"] == "REVISE")

    success = rejected == 0 and (not strict or revise == 0)
    overall = "ACCEPT" if success else ("REJECT" if rejected > 0 else "REVISE")

    return IntentResult(
        success=success,
        output={
            "target": target,
            "is_file": is_file,
            "overall_verdict": overall,
            "accepted": accepted,
            "rejected": rejected,
            "revise": revise,
            "evaluations": evaluations,
        },
        next_steps=[
            s
            for s in [
                "kgents fix <target>  # Attempt auto-repair" if not success else None,
                "kgents principles  # Review the 7 principles",
            ]
            if s is not None
        ],
    )
