"""
Tests for StorageProvider.

Validates XDG-compliant path resolution and directory management.
"""

import os
from pathlib import Path

import pytest

from services.storage import (
    StorageProvider,
    get_cosmos_dir,
    get_exports_dir,
    get_kgents_cache_root,
    get_kgents_config_root,
    get_kgents_data_root,
    get_storage_provider,
    get_uploads_dir,
    get_vectors_dir,
    get_witness_dir,
    reset_storage_provider,
)


class TestXDGPathResolution:
    """Test XDG path resolution."""

    def test_default_data_root_is_home_kgents(self):
        """Default data root should be ~/.kgents for user-friendliness."""
        root = get_kgents_data_root()
        assert root == Path.home() / ".kgents"

    def test_default_config_root_is_xdg_config(self):
        """Default config root should be ~/.config/kgents."""
        root = get_kgents_config_root()
        expected = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kgents"
        assert root == expected

    def test_default_cache_root_is_xdg_cache(self):
        """Default cache root should be ~/.cache/kgents."""
        root = get_kgents_cache_root()
        expected = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kgents"
        assert root == expected

    def test_data_root_respects_env_override(self, monkeypatch, tmp_path):
        """KGENTS_DATA_ROOT should override default."""
        custom_root = tmp_path / "custom_data"
        monkeypatch.setenv("KGENTS_DATA_ROOT", str(custom_root))

        # Clear cached provider
        reset_storage_provider()

        root = get_kgents_data_root()
        assert root == custom_root

    def test_config_root_respects_env_override(self, monkeypatch, tmp_path):
        """KGENTS_CONFIG_ROOT should override default."""
        custom_root = tmp_path / "custom_config"
        monkeypatch.setenv("KGENTS_CONFIG_ROOT", str(custom_root))

        # Clear cached provider
        reset_storage_provider()

        root = get_kgents_config_root()
        assert root == custom_root


class TestStorageProvider:
    """Test StorageProvider functionality."""

    @pytest.fixture
    def provider(self, tmp_path):
        """Create provider with temp data root."""
        reset_storage_provider()
        return StorageProvider(data_root=tmp_path)

    def test_paths_property_returns_storage_paths(self, provider):
        """paths property should return StoragePaths with all paths."""
        paths = provider.paths
        assert paths.data_root == provider._data_root
        assert paths.cosmos == provider._data_root / "cosmos"
        assert paths.uploads == provider._data_root / "uploads"
        assert paths.vectors == provider._data_root / "vectors"
        assert paths.witness == provider._data_root / "witness"
        assert paths.exports == provider._data_root / "exports"
        assert paths.tmp == provider._data_root / "tmp"

    def test_ensure_dir_creates_directory(self, provider, tmp_path):
        """ensure_dir should create directory if it doesn't exist."""
        test_dir = tmp_path / "test_subdir"
        assert not test_dir.exists()

        result = provider.ensure_dir(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir  # Returns path for chaining

    def test_ensure_all_dirs_creates_standard_dirs(self, provider):
        """ensure_all_dirs should create all standard kgents directories."""
        paths = provider.paths

        # Verify none exist initially
        assert not paths.cosmos.exists()
        assert not paths.uploads.exists()

        provider.ensure_all_dirs()

        # Verify all exist now
        assert paths.cosmos.exists()
        assert paths.uploads.exists()
        assert paths.vectors.exists()
        assert paths.witness.exists()
        assert paths.exports.exists()
        assert paths.tmp.exists()
        assert paths.config_root.exists()
        assert paths.cache_root.exists()

    def test_validate_path_accepts_paths_inside_roots(self, provider):
        """validate_path should accept paths inside kgents roots."""
        paths = provider.paths
        provider.ensure_all_dirs()

        # Should accept paths inside data root
        test_path = paths.uploads / "test.txt"
        validated = provider.validate_path(test_path)
        assert validated.is_absolute()

    def test_validate_path_rejects_paths_outside_roots(self, provider):
        """validate_path should reject paths outside kgents roots by default."""
        # Use a path that's definitely outside any kgents root
        outside_path = Path("/completely/different/path/file.txt")

        with pytest.raises(ValueError, match="outside kgents storage roots"):
            provider.validate_path(outside_path)

    def test_validate_path_allows_outside_with_flag(self, provider):
        """validate_path should allow outside paths with allow_outside_root=True."""
        # Use a path that's definitely outside any kgents root
        outside_path = Path("/completely/different/path/file.txt")

        validated = provider.validate_path(outside_path, allow_outside_root=True)
        assert validated.is_absolute()

    def test_hash_file_computes_sha256(self, provider, tmp_path):
        """hash_file should compute SHA256 hash of file content."""
        test_file = tmp_path / "test.txt"
        test_content = b"Hello, kgents!"
        test_file.write_bytes(test_content)

        hash_val = provider.hash_file(test_file)

        # Verify it's a valid SHA256 hex digest
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)

        # Verify consistency
        hash_val2 = provider.hash_file(test_file)
        assert hash_val == hash_val2

    def test_hash_file_different_for_different_content(self, provider, tmp_path):
        """hash_file should produce different hashes for different content."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"

        file1.write_bytes(b"Content A")
        file2.write_bytes(b"Content B")

        hash1 = provider.hash_file(file1)
        hash2 = provider.hash_file(file2)

        assert hash1 != hash2

    def test_clear_cache_removes_cached_files(self, provider):
        """clear_cache should remove all files in cache directory."""
        paths = provider.paths
        provider.ensure_all_dirs()

        # Create some cache files
        cache_file1 = paths.embeddings_cache / "test1.bin"
        cache_file2 = paths.http_cache / "test2.json"
        cache_file1.write_text("cached data 1")
        cache_file2.write_text("cached data 2")

        deleted = provider.clear_cache()

        assert deleted == 2
        assert not cache_file1.exists()
        assert not cache_file2.exists()

    def test_clear_tmp_removes_tmp_files(self, provider):
        """clear_tmp should remove all files and dirs in tmp directory."""
        paths = provider.paths
        provider.ensure_all_dirs()

        # Create tmp files and dirs
        tmp_file = paths.tmp / "temp.txt"
        tmp_dir = paths.tmp / "temp_dir"
        tmp_file.write_text("temporary")
        tmp_dir.mkdir()
        (tmp_dir / "nested.txt").write_text("nested")

        deleted = provider.clear_tmp()

        assert deleted == 2  # file + dir
        assert not tmp_file.exists()
        assert not tmp_dir.exists()

    def test_get_size_bytes_for_file(self, provider, tmp_path):
        """get_size_bytes should return file size in bytes."""
        test_file = tmp_path / "test.txt"
        test_content = b"x" * 1234
        test_file.write_bytes(test_content)

        size = provider.get_size_bytes(test_file)
        assert size == 1234

    def test_get_size_bytes_for_directory(self, provider, tmp_path):
        """get_size_bytes should return total size of directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        (test_dir / "file1.txt").write_bytes(b"x" * 100)
        (test_dir / "file2.txt").write_bytes(b"x" * 200)

        size = provider.get_size_bytes(test_dir)
        assert size == 300

    def test_format_size_human_readable(self, provider):
        """format_size should return human-readable size strings."""
        assert "B" in provider.format_size(512)
        assert "KB" in provider.format_size(2048)
        assert "MB" in provider.format_size(2 * 1024 * 1024)
        assert "GB" in provider.format_size(3 * 1024 * 1024 * 1024)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_uploads_dir_returns_uploads_path(self):
        """get_uploads_dir should return uploads directory path."""
        reset_storage_provider()
        uploads = get_uploads_dir()
        assert uploads == get_kgents_data_root() / "uploads"

    def test_get_cosmos_dir_returns_cosmos_path(self):
        """get_cosmos_dir should return cosmos directory path."""
        reset_storage_provider()
        cosmos = get_cosmos_dir()
        assert cosmos == get_kgents_data_root() / "cosmos"

    def test_get_exports_dir_returns_exports_path(self):
        """get_exports_dir should return exports directory path."""
        reset_storage_provider()
        exports = get_exports_dir()
        assert exports == get_kgents_data_root() / "exports"

    def test_get_witness_dir_returns_witness_path(self):
        """get_witness_dir should return witness directory path."""
        reset_storage_provider()
        witness = get_witness_dir()
        assert witness == get_kgents_data_root() / "witness"

    def test_get_vectors_dir_returns_vectors_path(self):
        """get_vectors_dir should return vectors directory path."""
        reset_storage_provider()
        vectors = get_vectors_dir()
        assert vectors == get_kgents_data_root() / "vectors"


class TestGlobalSingleton:
    """Test global singleton behavior."""

    def test_get_storage_provider_returns_singleton(self):
        """get_storage_provider should return same instance on repeated calls."""
        reset_storage_provider()

        provider1 = get_storage_provider()
        provider2 = get_storage_provider()

        assert provider1 is provider2

    def test_reset_storage_provider_clears_singleton(self):
        """reset_storage_provider should clear cached instance."""
        reset_storage_provider()

        provider1 = get_storage_provider()
        reset_storage_provider()
        provider2 = get_storage_provider()

        assert provider1 is not provider2

    def test_custom_data_root_only_used_on_first_call(self, tmp_path):
        """Custom data_root should only be used on first call."""
        reset_storage_provider()

        custom_root = tmp_path / "custom"
        provider1 = get_storage_provider(data_root=custom_root)
        provider2 = get_storage_provider(data_root=tmp_path / "other")

        # Second call should ignore custom root since singleton already exists
        assert provider1 is provider2
        assert provider1._data_root == custom_root
