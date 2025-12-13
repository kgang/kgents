"""
Demo script for the Cognitive Loom.

Shows how to construct a cognitive tree and render it with BranchTree.
This demonstrates the Shadow - rejected hypotheses made visible.

Run with: uv run python impl/claude/agents/i/widgets/_tests/demo_loom.py
"""

from datetime import datetime, timedelta

from agents.i.data.loom import CognitiveBranch, CognitiveTree
from agents.i.widgets.branch_tree import BranchTree


def create_demo_tree() -> CognitiveTree:
    """
    Create a demo cognitive tree showing an agent's decision process.

    The tree shows:
    - Main trunk: The path the agent actually took
    - Ghost branches: The paths it considered but rejected
    """
    now = datetime.now()

    # Root: The initial state
    root = CognitiveBranch(
        id="start",
        timestamp=now - timedelta(seconds=60),
        content="Received user query: 'Find all TODO comments'",
        reasoning="",
        selected=True,
    )

    # First decision point: Choose search strategy
    plan_a = CognitiveBranch(
        id="plan-a",
        timestamp=now - timedelta(seconds=50),
        content="Plan A: Use grep to search",
        reasoning="Fast and efficient",
        selected=True,
        parent_id="start",
    )

    plan_b = CognitiveBranch(
        id="plan-b",
        timestamp=now - timedelta(seconds=50),
        content="Plan B: Use find with exec",
        reasoning="Too slow for large codebases",
        selected=False,  # Ghost branch
        parent_id="start",
    )

    root.children.extend([plan_a, plan_b])

    # Execute plan A: Try grep
    grep_attempt = CognitiveBranch(
        id="grep-1",
        timestamp=now - timedelta(seconds=40),
        content="Action: grep -r 'TODO' .",
        reasoning="",
        selected=True,
        parent_id="plan-a",
    )

    plan_a.children.append(grep_attempt)

    # Grep failed: Permission denied
    grep_failed = CognitiveBranch(
        id="grep-fail",
        timestamp=now - timedelta(seconds=35),
        content="Result: Permission denied on .git/",
        reasoning="",
        selected=True,
        parent_id="grep-1",
    )

    grep_attempt.children.append(grep_failed)

    # Second decision point: How to handle failure?
    retry_grep = CognitiveBranch(
        id="retry-grep",
        timestamp=now - timedelta(seconds=30),
        content="Option: Retry grep with --exclude-dir",
        reasoning="Safer, respects .gitignore",
        selected=True,
        parent_id="grep-fail",
    )

    use_find = CognitiveBranch(
        id="use-find",
        timestamp=now - timedelta(seconds=30),
        content="Option: Fall back to find command",
        reasoning="Unsafe - might search too many files",
        selected=False,  # Ghost branch - rejected for safety
        parent_id="grep-fail",
    )

    grep_failed.children.extend([retry_grep, use_find])

    # Execute retry with exclusions
    final_action = CognitiveBranch(
        id="final",
        timestamp=now - timedelta(seconds=20),
        content="Action: grep -r 'TODO' --exclude-dir=.git .",
        reasoning="",
        selected=True,
        parent_id="retry-grep",
    )

    retry_grep.children.append(final_action)

    # Success!
    success = CognitiveBranch(
        id="success",
        timestamp=now - timedelta(seconds=10),
        content="Result: Found 42 TODO comments",
        reasoning="",
        selected=True,
        parent_id="final",
    )

    final_action.children.append(success)

    return CognitiveTree(root=root, current_id="success")


def main() -> None:
    """Run the demo."""
    print("=" * 70)
    print("COGNITIVE LOOM DEMO")
    print("=" * 70)
    print()
    print("The Loom visualizes agent cognition as a tree, not a log.")
    print("The main trunk shows selected actions.")
    print("Ghost branches (marked with ✖) show rejected hypotheses - the Shadow.")
    print()
    print("Bugs often hide in the path not taken.")
    print()
    print("=" * 70)
    print()

    # Create the tree
    tree = create_demo_tree()

    # Render with BranchTree widget
    widget = BranchTree(cognitive_tree=tree, show_ghosts=True)
    output = widget.render()

    print(output)
    print()
    print("=" * 70)
    print()

    # Show stats
    all_nodes = tree.all_nodes()
    ghosts = tree.ghost_branches()
    main = tree.main_path()

    print(f"Total nodes: {len(all_nodes)}")
    print(f"Main path length: {len(main)}")
    print(f"Ghost branches: {len(ghosts)}")
    print()

    print("Ghost branches (the paths not taken):")
    for ghost in ghosts:
        print(f"  - {ghost.content}")
        print(f"    Reasoning: {ghost.reasoning}")
    print()

    print("=" * 70)
    print()
    print("Toggle ghost visibility with show_ghosts=False:")
    print()

    # Show without ghosts
    widget.show_ghosts = False
    output_no_ghosts = widget.render()
    print(output_no_ghosts)
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
