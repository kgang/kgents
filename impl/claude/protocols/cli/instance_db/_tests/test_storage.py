"""
Tests for StorageProvider and XDGPaths.

Tests configuration loading, provider creation, and path resolution.
"""

from pathlib import Path

import pytest

from ..providers.sqlite import (
    FilesystemBlobStore,
    InMemoryRelationalStore,
    NumpyVectorStore,
    SQLiteRelationalStore,
    SQLiteTelemetryStore,
)
from ..storage import (
    InfrastructureConfig,
    ProviderConfig,
    RetentionConfig,
    StorageProvider,
    XDGPaths,
)


class TestXDGPaths:
    """Tests for XDG path resolution."""

    def test_default_paths(self, monkeypatch):
        """Should use default paths when env vars not set."""
        # Clear XDG env vars
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

        paths = XDGPaths.resolve()
        home = Path.home()

        assert paths.config == home / ".config" / "kgents"
        assert paths.data == home / ".local" / "share" / "kgents"
        assert paths.cache == home / ".cache" / "kgents"

    def test_custom_paths_from_env(self, monkeypatch):
        """Should use paths from environment variables."""
        monkeypatch.setenv("XDG_CONFIG_HOME", "/custom/config")
        monkeypatch.setenv("XDG_DATA_HOME", "/custom/data")
        monkeypatch.setenv("XDG_CACHE_HOME", "/custom/cache")

        paths = XDGPaths.resolve()

        assert paths.config == Path("/custom/config/kgents")
        assert paths.data == Path("/custom/data/kgents")
        assert paths.cache == Path("/custom/cache/kgents")

    def test_ensure_dirs(self, tmp_path, monkeypatch):
        """Should create directories."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        paths = XDGPaths.resolve()
        paths.ensure_dirs()

        assert paths.config.exists()
        assert paths.data.exists()
        assert paths.cache.exists()


class TestRetentionConfig:
    """Tests for retention configuration."""

    def test_default_values(self):
        """Should have sensible defaults."""
        config = RetentionConfig()
        assert config.hot_days == 30
        assert config.warm_days == 365
        assert config.cold_days is None

    def test_custom_values(self):
        """Should accept custom values."""
        config = RetentionConfig(hot_days=7, warm_days=90, cold_days=365)
        assert config.hot_days == 7
        assert config.warm_days == 90
        assert config.cold_days == 365


class TestProviderConfig:
    """Tests for provider configuration."""

    def test_from_dict_minimal(self):
        """Should create from minimal dict."""
        config = ProviderConfig.from_dict({"type": "sqlite"})
        assert config.type == "sqlite"
        assert config.wal_mode is True  # default

    def test_from_dict_full(self):
        """Should create from full dict."""
        config = ProviderConfig.from_dict(
            {
                "type": "sqlite",
                "connection": "/path/to/db.sqlite",
                "wal_mode": False,
                "dimensions": 512,
                "retention": {
                    "hot_days": 14,
                    "warm_days": 180,
                },
            }
        )

        assert config.type == "sqlite"
        assert config.connection == "/path/to/db.sqlite"
        assert config.wal_mode is False
        assert config.dimensions == 512
        assert config.retention.hot_days == 14


class TestInfrastructureConfig:
    """Tests for infrastructure configuration."""

    def test_from_dict(self):
        """Should create from YAML-like dict."""
        data = {
            "profile": "test-profile",
            "providers": {
                "relational": {"type": "sqlite", "connection": "/tmp/test.db"},
                "vector": {"type": "numpy", "dimensions": 256},
                "blob": {"type": "filesystem", "path": "/tmp/blobs"},
                "telemetry": {"type": "sqlite", "connection": "/tmp/telemetry.db"},
            },
        }

        config = InfrastructureConfig.from_dict(data)

        assert config.profile == "test-profile"
        assert config.relational.type == "sqlite"
        assert config.vector.dimensions == 256
        assert config.blob.path == "/tmp/blobs"

    def test_default_config(self, tmp_path, monkeypatch):
        """Should create default local-first config."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        paths = XDGPaths.resolve()

        config = InfrastructureConfig.default(paths)

        assert config.profile == "local-canonical"
        assert config.relational.type == "sqlite"
        assert "membrane.db" in config.relational.connection
        assert config.vector.type == "numpy"


class TestStorageProvider:
    """Tests for StorageProvider."""

    @pytest.mark.asyncio
    async def test_from_config_dict(self, tmp_path):
        """Should create provider from config dict."""
        config = {
            "profile": "test",
            "providers": {
                "relational": {
                    "type": "sqlite",
                    "connection": str(tmp_path / "test.db"),
                },
                "vector": {
                    "type": "numpy",
                    "path": str(tmp_path / "vectors.json"),
                },
                "blob": {
                    "type": "filesystem",
                    "path": str(tmp_path / "blobs"),
                },
                "telemetry": {
                    "type": "sqlite",
                    "connection": str(tmp_path / "telemetry.db"),
                },
            },
        }

        paths = XDGPaths(
            config=tmp_path / "config",
            data=tmp_path / "data",
            cache=tmp_path / "cache",
        )

        provider = await StorageProvider.from_config_dict(config, paths)

        assert isinstance(provider.relational, SQLiteRelationalStore)
        assert isinstance(provider.vector, NumpyVectorStore)
        assert isinstance(provider.blob, FilesystemBlobStore)
        assert isinstance(provider.telemetry, SQLiteTelemetryStore)

        await provider.close()

    @pytest.mark.asyncio
    async def test_create_minimal(self):
        """Should create minimal in-memory provider."""
        provider = await StorageProvider.create_minimal()

        assert isinstance(provider.relational, InMemoryRelationalStore)
        assert provider.config.profile == "minimal-fallback"

        await provider.close()

    @pytest.mark.asyncio
    async def test_run_migrations(self, tmp_path):
        """Should run migrations to create schema."""
        config = {
            "profile": "test",
            "providers": {
                "relational": {
                    "type": "sqlite",
                    "connection": str(tmp_path / "test.db"),
                },
                "vector": {"type": "memory"},
                "blob": {"type": "memory"},
                "telemetry": {"type": "memory"},
            },
        }

        paths = XDGPaths(
            config=tmp_path / "config",
            data=tmp_path / "data",
            cache=tmp_path / "cache",
        )

        provider = await StorageProvider.from_config_dict(config, paths)
        await provider.run_migrations()

        # Check that tables exist
        tables = await provider.relational.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t["name"] for t in tables]

        assert "instances" in table_names
        assert "shapes" in table_names
        assert "dreams" in table_names
        assert "embedding_metadata" in table_names
        assert "schema_version" in table_names

        await provider.close()

    @pytest.mark.asyncio
    async def test_env_var_expansion(self, tmp_path, monkeypatch):
        """Should expand environment variables in config."""
        monkeypatch.setenv("TEST_DB_PATH", str(tmp_path / "from_env.db"))

        config = {
            "profile": "test",
            "providers": {
                "relational": {
                    "type": "sqlite",
                    "connection": "${TEST_DB_PATH}",
                },
                "vector": {"type": "memory"},
                "blob": {"type": "memory"},
                "telemetry": {"type": "memory"},
            },
        }

        paths = XDGPaths(
            config=tmp_path / "config",
            data=tmp_path / "data",
            cache=tmp_path / "cache",
        )

        provider = await StorageProvider.from_config_dict(config, paths)
        await provider.relational.execute("SELECT 1")

        # DB should be created at the env var path
        assert (tmp_path / "from_env.db").exists()

        await provider.close()

    @pytest.mark.asyncio
    async def test_close_all_providers(self, tmp_path):
        """Should close all providers."""
        config = {
            "profile": "test",
            "providers": {
                "relational": {
                    "type": "sqlite",
                    "connection": str(tmp_path / "test.db"),
                },
                "vector": {
                    "type": "numpy",
                    "path": str(tmp_path / "vectors.json"),
                },
                "blob": {
                    "type": "filesystem",
                    "path": str(tmp_path / "blobs"),
                },
                "telemetry": {
                    "type": "sqlite",
                    "connection": str(tmp_path / "telemetry.db"),
                },
            },
        }

        paths = XDGPaths(
            config=tmp_path / "config",
            data=tmp_path / "data",
            cache=tmp_path / "cache",
        )

        provider = await StorageProvider.from_config_dict(config, paths)

        # Use providers
        await provider.relational.execute("SELECT 1")

        # Close should not raise
        await provider.close()


class TestStorageProviderFromFile:
    """Tests for loading config from file."""

    @pytest.mark.asyncio
    async def test_from_config_file(self, tmp_path):
        """Should load config from JSON file."""
        import json

        config_dir = tmp_path / "config" / "kgents"
        config_dir.mkdir(parents=True)

        config_file = (
            config_dir / "infrastructure.yaml"
        )  # .yaml extension, but JSON content is fine
        config_file.write_text(
            json.dumps(
                {
                    "profile": "from-file",
                    "providers": {
                        "relational": {
                            "type": "sqlite",
                            "connection": str(tmp_path / "data" / "test.db"),
                        },
                        "vector": {
                            "type": "numpy",
                            "path": str(tmp_path / "data" / "vectors.json"),
                        },
                        "blob": {
                            "type": "filesystem",
                            "path": str(tmp_path / "data" / "blobs"),
                        },
                        "telemetry": {
                            "type": "sqlite",
                            "connection": str(tmp_path / "data" / "telemetry.db"),
                        },
                    },
                }
            )
        )

        paths = XDGPaths(
            config=config_dir,
            data=tmp_path / "data",
            cache=tmp_path / "cache",
        )

        provider = await StorageProvider.from_config(
            config_path=config_file,
            paths=paths,
        )

        assert provider.config.profile == "from-file"

        await provider.close()

    @pytest.mark.asyncio
    async def test_fallback_when_no_config(self, tmp_path):
        """Should use defaults when no config file exists."""
        paths = XDGPaths(
            config=tmp_path / "config" / "kgents",
            data=tmp_path / "data" / "kgents",
            cache=tmp_path / "cache" / "kgents",
        )

        provider = await StorageProvider.from_config(
            config_path=tmp_path / "nonexistent.yaml",
            paths=paths,
        )

        # Should use default profile
        assert provider.config.profile == "local-canonical"

        await provider.close()
