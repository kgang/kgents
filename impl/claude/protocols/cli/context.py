"""
Context System - .kgents workspace awareness.

This module implements the context system from docs/cli-integration-plan.md:
- Workspace detection (find nearest .kgents/)
- Config loading (config.yaml)
- Default handling (target, principles, budget, output)
- Context creation for commands

Like git, kgents commands are context-aware:
- `kgents check` uses defaults from .kgents/config.yaml
- `kgents check --target=src/` overrides context

STORAGE ARCHITECTURE (2025-12-20):
- Global state: ~/.local/share/kgents/membrane.db (via StorageProvider)
- Per-project config: .kgents/config.yaml
- CLI session history: unified in membrane.db (cli_sessions, cli_session_events tables)
- The `history` section in config.yaml is DEPRECATED

Example .kgents/config.yaml:
```yaml
version: "1.0"
project:
  name: "my-project"
  root: "."

defaults:
  target: "src/"
  principles: "spec/principles.md"
  budget: "medium"
  output: "rich"

registry:
  path: ".kgents/catalog.json"

# DEPRECATED: History is now in ~/.local/share/kgents/membrane.db
# This section is kept for backward compatibility but ignored.
# history:
#   enabled: true
#   path: ".kgents/history.db"
#   retention: "30d"
```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KgentsConfig:
    """Configuration loaded from .kgents/config.yaml."""

    version: str = "1.0"
    project_name: str = ""
    project_root: Path = field(default_factory=Path.cwd)

    # Defaults
    default_target: str = "."
    default_principles: str = "spec/principles.md"
    default_budget: str = "medium"
    default_output: str = "rich"

    # Registry
    registry_path: str = ".kgents/catalog.json"

    # History - DEPRECATED (2025-12-20)
    # Session history is now unified in ~/.local/share/kgents/membrane.db
    # These fields are kept for backward compatibility but are ignored.
    # Use StorageProvider from instance_db for session tracking.
    history_enabled: bool = True  # DEPRECATED: ignored
    history_path: str = ".kgents/history.db"  # DEPRECATED: ignored
    history_retention: str = "30d"  # DEPRECATED: ignored

    @classmethod
    def from_dict(cls, data: dict[str, Any], root: Path) -> "KgentsConfig":
        """Create config from parsed YAML dict."""
        project = data.get("project", {})
        defaults = data.get("defaults", {})
        registry = data.get("registry", {})
        history = data.get("history", {})

        return cls(
            version=data.get("version", "1.0"),
            project_name=project.get("name", ""),
            project_root=root,
            default_target=defaults.get("target", "."),
            default_principles=defaults.get("principles", "spec/principles.md"),
            default_budget=defaults.get("budget", "medium"),
            default_output=defaults.get("output", "rich"),
            registry_path=registry.get("path", ".kgents/catalog.json"),
            history_enabled=history.get("enabled", True),
            history_path=history.get("path", ".kgents/history.db"),
            history_retention=history.get("retention", "30d"),
        )


@dataclass
class WorkspaceContext:
    """
    Context for the current kgents workspace.

    This combines:
    - Workspace root (where .kgents/ is)
    - Config from config.yaml
    - Runtime overrides from CLI flags
    """

    root: Path | None
    config: KgentsConfig
    is_workspace: bool = False

    # Runtime overrides
    format_override: str | None = None
    budget_override: str | None = None
    target_override: str | None = None

    @property
    def effective_format(self) -> str:
        """Get effective output format (override > config > default)."""
        return self.format_override or self.config.default_output

    @property
    def effective_budget(self) -> str:
        """Get effective budget level (override > config > default)."""
        return self.budget_override or self.config.default_budget

    @property
    def effective_target(self) -> str:
        """Get effective target path (override > config > default)."""
        return self.target_override or self.config.default_target

    def resolve_path(self, path: str) -> Path:
        """
        Resolve a path relative to workspace root.

        If path is absolute, return as-is.
        If path is relative and we have a workspace, resolve from root.
        Otherwise, resolve from cwd.
        """
        p = Path(path)
        if p.is_absolute():
            return p

        if self.root:
            return (self.root / path).resolve()

        return Path.cwd() / path


def find_workspace_root() -> Path | None:
    """
    Find the nearest .kgents directory.

    Walks up from cwd looking for .kgents/.
    Returns the directory containing .kgents, or None if not found.
    """
    current = Path.cwd()

    while current != current.parent:
        if (current / ".kgents").is_dir():
            return current
        current = current.parent

    # Check root
    if (current / ".kgents").is_dir():
        return current

    return None


def load_config(root: Path) -> KgentsConfig:
    """
    Load configuration from .kgents/config.yaml.

    Returns default config if file doesn't exist or can't be parsed.
    """
    config_path = root / ".kgents" / "config.yaml"

    if not config_path.exists():
        return KgentsConfig(project_root=root)

    try:
        import yaml

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        return KgentsConfig.from_dict(data, root)
    except ImportError:
        # PyYAML not installed
        return KgentsConfig(project_root=root)
    except Exception:
        # Failed to parse
        return KgentsConfig(project_root=root)


def get_context(
    format_override: str | None = None,
    budget_override: str | None = None,
    target_override: str | None = None,
) -> WorkspaceContext:
    """
    Get the current workspace context.

    This is the main entry point for commands to get context:
    ```python
    ctx = get_context(format_override=args.format)
    target = ctx.resolve_path(args.target or ctx.effective_target)
    ```
    """
    root = find_workspace_root()

    if root:
        config = load_config(root)
        is_workspace = True
    else:
        config = KgentsConfig()
        is_workspace = False

    return WorkspaceContext(
        root=root,
        config=config,
        is_workspace=is_workspace,
        format_override=format_override,
        budget_override=budget_override,
        target_override=target_override,
    )


def init_workspace(path: Path | None = None) -> Path:
    """
    Initialize a .kgents workspace.

    Creates:
    - .kgents/
    - .kgents/config.yaml (with defaults)
    - .kgents/catalog.json (empty)

    Returns the workspace root.
    """
    root = path or Path.cwd()
    kgents_dir = root / ".kgents"

    # Create directory
    kgents_dir.mkdir(exist_ok=True)

    # Create default config
    config_path = kgents_dir / "config.yaml"
    if not config_path.exists():
        default_config = """\
version: "1.0"

project:
  name: "{name}"
  root: "."

defaults:
  target: "."
  principles: "spec/principles.md"
  budget: "medium"
  output: "rich"

registry:
  path: ".kgents/catalog.json"

# Session history is stored globally in ~/.local/share/kgents/membrane.db
# via the StorageProvider. No per-project history configuration needed.
"""
        config_path.write_text(default_config.format(name=root.name))

    # Create empty catalog
    catalog_path = kgents_dir / "catalog.json"
    if not catalog_path.exists():
        catalog_path.write_text('{"version": "1.0", "entries": []}\n')

    return root
