"""
Ground (⊥): The empirical seed for infrastructure.

From spec/bootstrap.md:
    Ground: Void → Facts
    Ground() = {environment, paths, initial conditions}

Ground is irreducible—it cannot be derived from logic alone.
It provides the starting material from which the system bootstraps.

For infrastructure, Ground includes:
- XDG paths (where data lives)
- Environment variables (configuration)
- infrastructure.yaml (declarative configuration)
- Platform detection (darwin, linux, etc.)

This module implements Ground as Infrastructure-as-Code.
"""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class XDGPaths:
    """
    XDG Base Directory Specification paths.

    https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

    This is Ground—the empirical fact of where data lives on this system.
    """

    config: Path  # ~/.config/kgents (user configuration)
    data: Path  # ~/.local/share/kgents (user data)
    cache: Path  # ~/.cache/kgents (non-essential cache)
    state: Path  # ~/.local/state/kgents (user state, logs)

    @classmethod
    def resolve(cls) -> XDGPaths:
        """
        Resolve XDG paths from environment or platform defaults.

        This is Ground() applied to the filesystem.
        """
        home = Path.home()

        # XDG defaults per platform
        if platform.system() == "Darwin":
            default_config = home / ".config"
            default_data = home / ".local/share"
            default_cache = home / ".cache"
            default_state = home / ".local/state"
        elif platform.system() == "Windows":
            appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
            local_appdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
            default_config = appdata
            default_data = local_appdata
            default_cache = local_appdata / "cache"
            default_state = local_appdata / "state"
        else:  # Linux and others
            default_config = home / ".config"
            default_data = home / ".local/share"
            default_cache = home / ".cache"
            default_state = home / ".local/state"

        # Environment overrides (XDG spec)
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", default_config))
        data_home = Path(os.environ.get("XDG_DATA_HOME", default_data))
        cache_home = Path(os.environ.get("XDG_CACHE_HOME", default_cache))
        state_home = Path(os.environ.get("XDG_STATE_HOME", default_state))

        return cls(
            config=config_home / "kgents",
            data=data_home / "kgents",
            cache=cache_home / "kgents",
            state=state_home / "kgents",
        )

    def ensure_dirs(self) -> None:
        """Create directories if they don't exist."""
        for path in [self.config, self.data, self.cache, self.state]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class RetentionConfig:
    """Data retention configuration (for tiered storage and composting)."""

    hot_days: int = 30  # Keep in primary store
    warm_days: int = 365  # Move to compressed storage
    cold_days: int | None = None  # Move to archive (None = never)
    compost_strategy: str = "sketch"  # "delete", "sketch", "archive"


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for a single storage provider."""

    type: str  # "sqlite", "postgres", "numpy", "qdrant", "filesystem", "s3"
    connection: str | None = None  # Connection string or path
    path: str | None = None  # Alternative path for file-based providers

    # Provider-specific options
    wal_mode: bool = True  # For SQLite
    dimensions: int = 384  # For vector stores
    fallback: str | None = None  # Fallback provider if primary fails
    threshold: int = 1000  # Auto-switch threshold (e.g., vectors count)
    retention: RetentionConfig | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ProviderConfig:
        """Create from dictionary (e.g., YAML parsed)."""
        retention_data = d.pop("retention", None)
        retention = RetentionConfig(**retention_data) if retention_data else None
        return cls(**d, retention=retention)


@dataclass
class InfrastructureConfig:
    """
    Full infrastructure configuration.

    Loaded from infrastructure.yaml or constructed programmatically.
    This is declarative Infrastructure-as-Code.
    """

    profile: str = "local-canonical"

    # The Four Stores
    relational: ProviderConfig = field(default_factory=lambda: ProviderConfig(type="sqlite"))
    vector: ProviderConfig = field(
        default_factory=lambda: ProviderConfig(type="numpy", dimensions=384)
    )
    blob: ProviderConfig = field(default_factory=lambda: ProviderConfig(type="filesystem"))
    telemetry: ProviderConfig = field(default_factory=lambda: ProviderConfig(type="sqlite"))

    # Synapse configuration
    synapse_buffer_size: int = 1000
    synapse_batch_interval_ms: int = 100

    # Dreaming configuration (maintenance cycles)
    dream_interval_hours: int = 24
    dream_time_utc: str = "03:00"  # 3 AM UTC

    # Active Inference configuration
    surprise_threshold: float = 0.5  # KL divergence threshold for flashbulb
    prediction_model: str = "exponential_smoothing"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> InfrastructureConfig:
        """Create from dictionary (e.g., YAML parsed)."""
        providers = d.get("providers", {})

        return cls(
            profile=d.get("profile", "local-canonical"),
            relational=ProviderConfig.from_dict(providers.get("relational", {"type": "sqlite"})),
            vector=ProviderConfig.from_dict(providers.get("vector", {"type": "numpy"})),
            blob=ProviderConfig.from_dict(providers.get("blob", {"type": "filesystem"})),
            telemetry=ProviderConfig.from_dict(providers.get("telemetry", {"type": "sqlite"})),
            synapse_buffer_size=d.get("synapse", {}).get("buffer_size", 1000),
            synapse_batch_interval_ms=d.get("synapse", {}).get("batch_interval_ms", 100),
            dream_interval_hours=d.get("dreaming", {}).get("interval_hours", 24),
            dream_time_utc=d.get("dreaming", {}).get("time_utc", "03:00"),
            surprise_threshold=d.get("inference", {}).get("surprise_threshold", 0.5),
            prediction_model=d.get("inference", {}).get("model", "exponential_smoothing"),
        )

    @classmethod
    def default_config(cls, paths: XDGPaths) -> InfrastructureConfig:
        """Create default configuration for given XDG paths."""
        return cls(
            profile="local-canonical",
            relational=ProviderConfig(
                type="sqlite",
                connection=str(paths.data / "membrane.db"),
                wal_mode=True,
            ),
            vector=ProviderConfig(
                type="numpy",
                path=str(paths.data / "vectors.json"),
                dimensions=384,
                fallback="numpy-cosine",
                threshold=1000,
            ),
            blob=ProviderConfig(
                type="filesystem",
                path=str(paths.data / "blobs"),
            ),
            telemetry=ProviderConfig(
                type="sqlite",
                connection=str(paths.data / "telemetry.db"),
                retention=RetentionConfig(
                    hot_days=30,
                    warm_days=365,
                    compost_strategy="sketch",
                ),
            ),
        )


@dataclass
class Ground:
    """
    The Ground bootstrap agent applied to infrastructure.

    Ground is the irreducible empirical seed. It cannot be derived—
    it must be given from the environment.

    Contents:
    - paths: Where data lives (XDG)
    - config: Infrastructure configuration (IaC)
    - platform: System detection
    - env: Environment variables
    """

    paths: XDGPaths
    config: InfrastructureConfig
    platform: str
    hostname: str
    pid: int
    env: dict[str, str]

    @classmethod
    def resolve(cls, config_path: Path | None = None) -> Ground:
        """
        Resolve Ground from the environment.

        This is the irreducible starting point—what exists before
        any kgents code runs.
        """
        # XDG paths
        paths = XDGPaths.resolve()

        # Load or create configuration
        config_file = config_path or (paths.config / "infrastructure.yaml")
        if config_file.exists():
            with open(config_file) as f:
                config_data = yaml.safe_load(f) or {}
            # Expand environment variables in config
            config_data = _expand_env_vars(config_data)
            config = InfrastructureConfig.from_dict(config_data)
        else:
            config = InfrastructureConfig.default_config(paths)

        # Platform facts
        return cls(
            paths=paths,
            config=config,
            platform=platform.system().lower(),
            hostname=platform.node(),
            pid=os.getpid(),
            env={k: v for k, v in os.environ.items() if k.startswith("KGENTS_")},
        )


def resolve_ground(config_path: Path | None = None) -> Ground:
    """
    Convenience function to resolve Ground.

    From spec/bootstrap.md:
        Ground: Void → Facts
        Ground() = {environment, paths, initial conditions}
    """
    return Ground.resolve(config_path)


def _expand_env_vars(obj: Any) -> Any:
    """Recursively expand ${VAR} patterns in config values."""
    if isinstance(obj, str):
        # Expand ${VAR} patterns
        result = obj
        while "${" in result:
            start = result.find("${")
            end = result.find("}", start)
            if end == -1:
                break
            var_name = result[start + 2 : end]
            var_value = os.environ.get(var_name, "")
            result = result[:start] + var_value + result[end + 1 :]
        return result
    elif isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    return obj
