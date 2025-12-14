"""
CLI handler for N-Phase Prompt Compiler.

Design Decision (B4): Follow existing handler pattern from handlers/forest.py.

Usage:
    kg nphase compile <definition.yaml>       # Compile to stdout
    kg nphase compile <definition.yaml> -o <output.md>  # Compile to file
    kg nphase validate <definition.yaml>      # Validate only
    kg nphase bootstrap <plan.md>             # Bootstrap from existing plan
    kg nphase template <PHASE>                # Show phase template
"""

from __future__ import annotations

from pathlib import Path


def cmd_nphase(args: list[str] | None = None) -> int:
    """
    N-Phase Prompt Compiler CLI.

    Usage:
        kgents nphase compile <definition.yaml>       Compile to stdout
        kgents nphase compile <definition.yaml> -o <output.md>  Compile to file
        kgents nphase validate <definition.yaml>      Validate only
        kgents nphase bootstrap <plan.md>             Bootstrap from existing plan
        kgents nphase template <PHASE>                Show phase template

    The N-Phase Prompt Compiler generates N-Phase Meta-Prompts from
    structured ProjectDefinition YAML files.

    Examples:
        kgents nphase compile my-project.yaml
        kgents nphase compile my-project.yaml -o prompts/my-project.md
        kgents nphase validate my-project.yaml
        kgents nphase bootstrap plans/crown-jewel-next.md
        kgents nphase template PLAN
    """
    args = args or []

    if not args or args[0] in ("--help", "-h", "help"):
        print(cmd_nphase.__doc__)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    if subcommand == "compile":
        return _compile(sub_args)
    elif subcommand == "validate":
        return _validate(sub_args)
    elif subcommand == "bootstrap":
        return _bootstrap(sub_args)
    elif subcommand == "template":
        return _template(sub_args)
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Usage: kgents nphase [compile|validate|bootstrap|template]")
        return 1


def _compile(args: list[str]) -> int:
    """Compile a ProjectDefinition to N-Phase Meta-Prompt."""
    from protocols.nphase.compiler import compiler

    if not args:
        print("Error: definition path required")
        print("Usage: kgents nphase compile <definition.yaml> [-o output.md]")
        return 1

    definition_path = Path(args[0])

    # Check for output flag
    output_path: Path | None = None
    if "-o" in args:
        idx = args.index("-o")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])
        else:
            print("Error: -o requires output path")
            return 1
    elif "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])
        else:
            print("Error: --output requires output path")
            return 1

    if not definition_path.exists():
        print(f"Error: file not found: {definition_path}")
        return 1

    try:
        prompt = compiler.compile_from_yaml_file(definition_path)

        if output_path:
            prompt.save(output_path)
            print(f"Compiled to {output_path}")
        else:
            print(str(prompt))

        return 0
    except Exception as e:
        print(f"Error compiling: {e}")
        return 1


def _validate(args: list[str]) -> int:
    """Validate a ProjectDefinition without compiling."""
    from protocols.nphase.schema import ProjectDefinition

    if not args:
        print("Error: definition path required")
        print("Usage: kgents nphase validate <definition.yaml>")
        return 1

    definition_path = Path(args[0])

    if not definition_path.exists():
        print(f"Error: file not found: {definition_path}")
        return 1

    try:
        definition = ProjectDefinition.from_yaml_file(definition_path)
        result = definition.validate()

        if result.is_valid:
            print("Valid ProjectDefinition")
            if result.warnings:
                print("\nWarnings:")
                for w in result.warnings:
                    print(f"  {w}")
            return 0
        else:
            print("Invalid ProjectDefinition")
            print("\nErrors:")
            for e in result.errors:
                print(f"  {e}")
            return 1
    except Exception as e:
        print(f"Error validating: {e}")
        return 1


def _bootstrap(args: list[str]) -> int:
    """Bootstrap ProjectDefinition from existing plan file header."""
    from protocols.nphase.compiler import compiler

    if not args:
        print("Error: plan path required")
        print("Usage: kgents nphase bootstrap <plan.md> [-o output.md]")
        return 1

    plan_path = Path(args[0])

    # Check for output flag
    output_path: Path | None = None
    if "-o" in args:
        idx = args.index("-o")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])
    elif "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])

    if not plan_path.exists():
        print(f"Error: file not found: {plan_path}")
        return 1

    try:
        prompt = compiler.compile_from_plan(plan_path)

        if output_path:
            prompt.save(output_path)
            print(f"Bootstrapped and compiled to {output_path}")
        else:
            print(str(prompt))

        return 0
    except Exception as e:
        print(f"Error bootstrapping: {e}")
        return 1


def _template(args: list[str]) -> int:
    """Show template for a specific phase."""
    from protocols.nphase.templates import PHASE_TEMPLATES, get_template

    if not args:
        print("Available phases:")
        for phase in PHASE_TEMPLATES:
            print(f"  {phase}")
        print("\nUsage: kgents nphase template <PHASE>")
        return 0

    phase = args[0].upper()

    try:
        tmpl = get_template(phase)
        print(f"# {tmpl.name}\n")
        print(f"**Mission**: {tmpl.mission}\n")
        print(f"**Actions**:\n{tmpl.actions}\n")
        print(f"**Exit Criteria**:\n{tmpl.exit_criteria}\n")
        print(f"**Minimum Artifact**: {tmpl.minimum_artifact}\n")
        print(f"**Continuation**: -> {tmpl.continuation}")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = cmd_nphase(sys.argv[1:])
    sys.exit(exit_code)
