"""
Tests for the context system (.kgents workspace awareness).

Tests cover:
1. Workspace detection (find_workspace_root)
2. Config loading (load_config)
3. Default values
4. Override behavior
5. Path resolution
6. Workspace initialization
"""

import tempfile
from pathlib import Path

import pytest

# Check if PyYAML is available
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

requires_yaml = pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve symlinks (macOS /var -> /private/var)
        yield Path(tmpdir).resolve()


@pytest.fixture
def workspace(temp_dir):
    """Create a .kgents workspace in temp directory."""
    kgents_dir = temp_dir / ".kgents"
    kgents_dir.mkdir()

    config = """\
version: "1.0"

project:
  name: "test-project"
  root: "."

defaults:
  target: "src/"
  principles: "custom/principles.md"
  budget: "high"
  output: "json"

registry:
  path: ".kgents/catalog.json"
"""
    (kgents_dir / "config.yaml").write_text(config)

    # Create catalog
    (kgents_dir / "catalog.json").write_text('{"version": "1.0", "entries": []}\n')

    return temp_dir


# =============================================================================
# Workspace Detection
# =============================================================================


class TestWorkspaceDetection:
    """Test find_workspace_root."""

    def test_find_workspace_in_cwd(self, workspace, monkeypatch):
        """Find workspace when in root directory."""
        monkeypatch.chdir(workspace)

        from protocols.cli.context import find_workspace_root

        root = find_workspace_root()
        # Compare resolved paths (macOS /var -> /private/var symlink)
        assert root.resolve() == workspace.resolve()

    def test_find_workspace_in_subdirectory(self, workspace, monkeypatch):
        """Find workspace when in subdirectory."""
        subdir = workspace / "src" / "components"
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        from protocols.cli.context import find_workspace_root

        root = find_workspace_root()
        # Compare resolved paths (macOS /var -> /private/var symlink)
        assert root.resolve() == workspace.resolve()

    def test_no_workspace_returns_none(self, temp_dir, monkeypatch):
        """Return None when no .kgents found."""
        monkeypatch.chdir(temp_dir)

        from protocols.cli.context import find_workspace_root

        root = find_workspace_root()
        assert root is None


# =============================================================================
# Config Loading
# =============================================================================


class TestConfigLoading:
    """Test load_config."""

    @requires_yaml
    def test_load_existing_config(self, workspace):
        """Load config from existing file."""
        from protocols.cli.context import load_config

        config = load_config(workspace)

        assert config.version == "1.0"
        assert config.project_name == "test-project"
        assert config.default_target == "src/"
        assert config.default_principles == "custom/principles.md"
        assert config.default_budget == "high"
        assert config.default_output == "json"

    def test_missing_config_uses_defaults(self, temp_dir):
        """Missing config file uses defaults."""
        # Create .kgents dir without config
        (temp_dir / ".kgents").mkdir()

        from protocols.cli.context import load_config

        config = load_config(temp_dir)

        assert config.version == "1.0"
        assert config.default_target == "."
        assert config.default_budget == "medium"
        assert config.default_output == "rich"

    def test_invalid_yaml_uses_defaults(self, temp_dir):
        """Invalid YAML uses defaults."""
        kgents_dir = temp_dir / ".kgents"
        kgents_dir.mkdir()
        (kgents_dir / "config.yaml").write_text("{{invalid yaml}}")

        from protocols.cli.context import load_config

        config = load_config(temp_dir)

        # Should return defaults, not crash
        assert config.default_output == "rich"


# =============================================================================
# KgentsConfig
# =============================================================================


class TestKgentsConfig:
    """Test KgentsConfig dataclass."""

    def test_from_dict_full(self):
        """Create config from complete dict."""
        from protocols.cli.context import KgentsConfig

        data = {
            "version": "2.0",
            "project": {"name": "my-proj", "root": "."},
            "defaults": {
                "target": "lib/",
                "principles": "PRINCIPLES.md",
                "budget": "unlimited",
                "output": "markdown",
            },
            "registry": {"path": "custom/catalog.json"},
            "history": {
                "enabled": False,
                "path": "custom/history.db",
                "retention": "7d",
            },
        }

        config = KgentsConfig.from_dict(data, Path("/test"))

        assert config.version == "2.0"
        assert config.project_name == "my-proj"
        assert config.default_target == "lib/"
        assert config.default_budget == "unlimited"
        assert config.registry_path == "custom/catalog.json"
        assert config.history_enabled is False

    def test_from_dict_partial(self):
        """Create config from partial dict."""
        from protocols.cli.context import KgentsConfig

        data = {"project": {"name": "partial-proj"}}

        config = KgentsConfig.from_dict(data, Path("/test"))

        assert config.project_name == "partial-proj"
        assert config.default_target == "."  # default
        assert config.default_budget == "medium"  # default


# =============================================================================
# WorkspaceContext
# =============================================================================


class TestWorkspaceContext:
    """Test WorkspaceContext."""

    @requires_yaml
    def test_effective_values_no_override(self, workspace):
        """effective_* returns config values when no override."""
        from protocols.cli.context import WorkspaceContext, load_config

        config = load_config(workspace)
        ctx = WorkspaceContext(root=workspace, config=config, is_workspace=True)

        assert ctx.effective_format == "json"  # from config
        assert ctx.effective_budget == "high"  # from config
        assert ctx.effective_target == "src/"  # from config

    def test_effective_values_with_override(self, workspace):
        """effective_* returns override when provided."""
        from protocols.cli.context import WorkspaceContext, load_config

        config = load_config(workspace)
        ctx = WorkspaceContext(
            root=workspace,
            config=config,
            is_workspace=True,
            format_override="rich",
            budget_override="low",
            target_override="test/",
        )

        assert ctx.effective_format == "rich"  # override wins
        assert ctx.effective_budget == "low"  # override wins
        assert ctx.effective_target == "test/"  # override wins

    def test_resolve_path_absolute(self, workspace):
        """resolve_path returns absolute paths unchanged."""
        from protocols.cli.context import WorkspaceContext, load_config

        config = load_config(workspace)
        ctx = WorkspaceContext(root=workspace, config=config, is_workspace=True)

        abs_path = Path("/absolute/path/to/file.py")
        resolved = ctx.resolve_path(str(abs_path))

        assert resolved == abs_path

    def test_resolve_path_relative_in_workspace(self, workspace):
        """resolve_path resolves relative paths from workspace root."""
        from protocols.cli.context import WorkspaceContext, load_config

        config = load_config(workspace)
        ctx = WorkspaceContext(root=workspace, config=config, is_workspace=True)

        resolved = ctx.resolve_path("src/main.py")

        assert resolved == (workspace / "src/main.py").resolve()


# =============================================================================
# get_context
# =============================================================================


class TestGetContext:
    """Test get_context helper."""

    def test_get_context_in_workspace(self, workspace, monkeypatch):
        """get_context finds workspace and loads config."""
        monkeypatch.chdir(workspace)

        from protocols.cli.context import get_context

        ctx = get_context()

        assert ctx.is_workspace is True
        # Compare resolved paths (macOS /var -> /private/var symlink)
        assert ctx.root.resolve() == workspace.resolve()
        # project_name only populated if PyYAML is available
        if HAS_YAML:
            assert ctx.config.project_name == "test-project"

    def test_get_context_outside_workspace(self, temp_dir, monkeypatch):
        """get_context works outside workspace with defaults."""
        monkeypatch.chdir(temp_dir)

        from protocols.cli.context import get_context

        ctx = get_context()

        assert ctx.is_workspace is False
        assert ctx.root is None
        assert ctx.effective_budget == "medium"

    def test_get_context_with_overrides(self, workspace, monkeypatch):
        """get_context applies overrides."""
        monkeypatch.chdir(workspace)

        from protocols.cli.context import get_context

        ctx = get_context(format_override="markdown", budget_override="unlimited")

        assert ctx.effective_format == "markdown"
        assert ctx.effective_budget == "unlimited"


# =============================================================================
# Workspace Initialization
# =============================================================================


class TestWorkspaceInit:
    """Test init_workspace."""

    def test_init_creates_directory_structure(self, temp_dir):
        """init_workspace creates .kgents/ with config."""
        from protocols.cli.context import init_workspace

        root = init_workspace(temp_dir)

        assert root == temp_dir
        assert (temp_dir / ".kgents").is_dir()
        assert (temp_dir / ".kgents" / "config.yaml").exists()
        assert (temp_dir / ".kgents" / "catalog.json").exists()

    @requires_yaml
    def test_init_creates_default_config(self, temp_dir):
        """init_workspace creates valid default config."""
        from protocols.cli.context import init_workspace, load_config

        init_workspace(temp_dir)
        config = load_config(temp_dir)

        assert config.version == "1.0"
        assert config.project_name == temp_dir.name
        assert config.default_budget == "medium"

    def test_init_preserves_existing_config(self, workspace):
        """init_workspace doesn't overwrite existing config."""
        original_content = (workspace / ".kgents" / "config.yaml").read_text()

        from protocols.cli.context import init_workspace

        init_workspace(workspace)

        new_content = (workspace / ".kgents" / "config.yaml").read_text()
        assert new_content == original_content

    def test_init_uses_cwd_if_no_path(self, temp_dir, monkeypatch):
        """init_workspace uses cwd if no path provided."""
        monkeypatch.chdir(temp_dir)

        from protocols.cli.context import init_workspace

        root = init_workspace()

        # Compare resolved paths (macOS /var -> /private/var symlink)
        assert root.resolve() == temp_dir.resolve()
        assert (temp_dir / ".kgents").is_dir()
