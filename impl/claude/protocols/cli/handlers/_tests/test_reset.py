"""
Tests for reset command.

Tests the full reset flow including:
- Help display
- Dry run mode
- Force flag
- Unknown option handling
- Phase execution order
- Genesis flag
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from protocols.cli.handlers.reset import cmd_reset


class TestCmdResetHelp:
    """Tests for reset command help."""

    @pytest.mark.asyncio
    async def test_reset_help_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print help and return 0."""
        result = await cmd_reset(["--help"])
        assert result == 0

        captured = capsys.readouterr()
        assert "kgents reset" in captured.out
        assert "USAGE" in captured.out
        assert "OPTIONS" in captured.out
        assert "PHASES" in captured.out
        assert "--force" in captured.out
        assert "--genesis" in captured.out
        assert "--dry-run" in captured.out

    @pytest.mark.asyncio
    async def test_reset_help_short_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print help with -h flag."""
        result = await cmd_reset(["-h"])
        assert result == 0

        captured = capsys.readouterr()
        assert "kgents reset" in captured.out


class TestCmdResetDryRun:
    """Tests for reset command dry run mode."""

    @pytest.mark.asyncio
    async def test_reset_dry_run_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should show preview without executing when --dry-run is passed."""
        mock_targets = [("global", Path("/tmp/kgents"), "1.5 MB")]

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=mock_targets,
            ) as mock_collect,
            patch(
                "protocols.cli.handlers.wipe._wipe_path",
            ) as mock_wipe,
        ):
            result = await cmd_reset(["--dry-run"])

        assert result == 0

        # Verify collect was called but wipe was not
        mock_collect.assert_called_once_with("global")
        mock_wipe.assert_not_called()

        captured = capsys.readouterr()
        assert "[dry-run]" in captured.out
        assert "Would delete" in captured.out
        assert "Stopping here" in captured.out

    @pytest.mark.asyncio
    async def test_reset_dry_run_no_targets(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should show dry run output even with no targets."""
        with patch(
            "protocols.cli.handlers.wipe._collect_targets",
            return_value=[],
        ):
            result = await cmd_reset(["--dry-run"])

        assert result == 0

        captured = capsys.readouterr()
        assert "No existing data to wipe" in captured.out
        assert "[dry-run]" in captured.out


class TestCmdResetForce:
    """Tests for reset command force flag."""

    @pytest.mark.asyncio
    async def test_reset_force_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should skip confirmation with --force."""
        mock_targets = [("global", Path("/tmp/kgents"), "1.5 MB")]
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=mock_targets,
            ),
            patch(
                "protocols.cli.handlers.wipe._wipe_path",
            ) as mock_wipe,
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
            patch("builtins.input") as mock_input,
        ):
            result = await cmd_reset(["--force"])

        assert result == 0

        # Verify wipe was called
        mock_wipe.assert_called_once()

        # Verify input was NOT called (no confirmation)
        mock_input.assert_not_called()

        captured = capsys.readouterr()
        assert "Reset complete" in captured.out

    @pytest.mark.asyncio
    async def test_reset_force_short_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should skip confirmation with -f flag."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
            patch("builtins.input") as mock_input,
        ):
            result = await cmd_reset(["-f"])

        assert result == 0
        mock_input.assert_not_called()


class TestCmdResetUnknownOption:
    """Tests for reset command unknown option handling."""

    @pytest.mark.asyncio
    async def test_reset_unknown_option(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should show error for unknown option."""
        result = await cmd_reset(["--unknown"])
        assert result == 1

        captured = capsys.readouterr()
        assert "[error]" in captured.out
        assert "Unknown option" in captured.out
        assert "--unknown" in captured.out
        assert "kgents reset --help" in captured.out

    @pytest.mark.asyncio
    async def test_reset_unknown_short_option(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should show error for unknown short option."""
        result = await cmd_reset(["-x"])
        assert result == 1

        captured = capsys.readouterr()
        assert "[error]" in captured.out
        assert "Unknown option" in captured.out
        assert "-x" in captured.out


class TestCmdResetPhases:
    """Tests for reset command phase execution."""

    @pytest.mark.asyncio
    async def test_reset_phases_execute_in_order(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should execute phases in correct order: WIPE, SCAFFOLD, TABLES, GENESIS, VERIFY."""
        mock_targets = [("global", Path("/tmp/kgents"), "1.5 MB")]
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()
        call_order = []

        def track_collect(*args, **kwargs):
            call_order.append("collect_targets")
            return mock_targets

        def track_wipe(*args, **kwargs):
            call_order.append("wipe_path")

        def track_resolve():
            call_order.append("resolve_paths")
            return mock_paths

        async def track_storage(*args, **kwargs):
            call_order.append("storage_from_config")
            return mock_storage

        async def track_init_db():
            call_order.append("init_db")

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                side_effect=track_collect,
            ),
            patch(
                "protocols.cli.handlers.wipe._wipe_path",
                side_effect=track_wipe,
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                side_effect=track_resolve,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                side_effect=track_storage,
            ),
            patch(
                "models.base.init_db",
                side_effect=track_init_db,
            ),
        ):
            result = await cmd_reset(["--force"])

        assert result == 0

        # Verify order: collect -> wipe -> resolve -> storage -> init_db
        assert call_order == [
            "collect_targets",
            "wipe_path",
            "resolve_paths",
            "storage_from_config",
            "init_db",
        ]

        captured = capsys.readouterr()
        # Verify all phases appear in output
        assert "[Phase 1/5] WIPE" in captured.out
        assert "[Phase 2/5] SCAFFOLD" in captured.out
        assert "[Phase 3/5] TABLES" in captured.out
        assert "[Phase 4/5] GENESIS" in captured.out  # Skipped message
        assert "[Phase 5/5] VERIFY" in captured.out

    @pytest.mark.asyncio
    async def test_reset_tables_failure_stops_execution(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should return failure if table creation fails."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                side_effect=Exception("Database connection failed"),
            ),
        ):
            result = await cmd_reset(["--force"])

        assert result == 1

        captured = capsys.readouterr()
        assert "Failed to create instance tables" in captured.out
        assert "Database connection failed" in captured.out
        assert "Reset failed" in captured.out


class TestCmdResetGenesis:
    """Tests for reset command genesis flag."""

    @pytest.mark.asyncio
    async def test_reset_genesis_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should seed K-Blocks when --genesis flag is passed."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        # Mock genesis result
        mock_genesis_result = MagicMock()
        mock_genesis_result.success = True
        mock_genesis_result.total_kblocks = 25
        mock_genesis_result.kblock_ids = {
            "genesis:L0:axiom1": "id1",
            "genesis:L0:axiom2": "id2",
            "genesis:L1:kernel1": "id3",
            "genesis:L2:principle1": "id4",
            "genesis:L3:arch1": "id5",
        }

        # Mock seed_clean_slate_genesis function (now used with wipe_existing=True)
        mock_seed_genesis = AsyncMock(return_value=mock_genesis_result)

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
            patch(
                "services.zero_seed.clean_slate_genesis.seed_clean_slate_genesis",
                mock_seed_genesis,
            ),
        ):
            result = await cmd_reset(["--force", "--genesis"])

        assert result == 0

        # Verify genesis was called with wipe_existing=True
        mock_seed_genesis.assert_called_once_with(wipe_existing=True)

        captured = capsys.readouterr()
        assert "[Phase 4/5] GENESIS" in captured.out
        assert "Seeded 25 K-Blocks" in captured.out
        assert "L0 Axioms:" in captured.out
        assert "L1 Kernel:" in captured.out
        assert "L2 Principles:" in captured.out
        assert "L3 Architecture:" in captured.out

    @pytest.mark.asyncio
    async def test_reset_genesis_short_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should seed K-Blocks with -g flag."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        mock_genesis_result = MagicMock()
        mock_genesis_result.success = True
        mock_genesis_result.total_kblocks = 10
        mock_genesis_result.kblock_ids = {}

        # Mock seed_clean_slate_genesis function
        mock_seed_genesis = AsyncMock(return_value=mock_genesis_result)

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
            patch(
                "services.zero_seed.clean_slate_genesis.seed_clean_slate_genesis",
                mock_seed_genesis,
            ),
        ):
            result = await cmd_reset(["-f", "-g"])

        assert result == 0
        mock_seed_genesis.assert_called_once_with(wipe_existing=True)

    @pytest.mark.asyncio
    async def test_reset_genesis_skipped_by_default(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should skip genesis when flag is not provided."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
        ):
            result = await cmd_reset(["--force"])

        assert result == 0

        captured = capsys.readouterr()
        assert "GENESIS - Skipped" in captured.out
        assert "use --genesis to enable" in captured.out

    @pytest.mark.asyncio
    async def test_reset_genesis_failure_is_non_fatal(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should continue if genesis fails (non-fatal error)."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        # Mock seed_clean_slate_genesis to raise an exception
        mock_seed_genesis = AsyncMock(side_effect=Exception("Genesis storage unavailable"))

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
            patch(
                "services.zero_seed.clean_slate_genesis.seed_clean_slate_genesis",
                mock_seed_genesis,
            ),
        ):
            result = await cmd_reset(["--force", "--genesis"])

        # Should still succeed despite genesis failure
        assert result == 0

        captured = capsys.readouterr()
        assert "Genesis failed (non-fatal)" in captured.out
        assert "Genesis storage unavailable" in captured.out
        assert "Reset complete" in captured.out


class TestCmdResetConfirmation:
    """Tests for reset command confirmation handling."""

    @pytest.mark.asyncio
    async def test_reset_requires_confirmation(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should require confirmation when not using --force."""
        with patch("builtins.input", return_value="no") as mock_input:
            result = await cmd_reset([])

        assert result == 1
        mock_input.assert_called_once()

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "Aborted" in captured.out

    @pytest.mark.asyncio
    async def test_reset_confirmation_accepted(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should proceed when user types 'reset'."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch("builtins.input", return_value="reset"),
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ),
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
        ):
            result = await cmd_reset([])

        assert result == 0

        captured = capsys.readouterr()
        assert "Reset complete" in captured.out

    @pytest.mark.asyncio
    async def test_reset_keyboard_interrupt(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should handle keyboard interrupt gracefully."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = await cmd_reset([])

        assert result == 1

        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    @pytest.mark.asyncio
    async def test_reset_eof_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should handle EOF error gracefully."""
        with patch("builtins.input", side_effect=EOFError):
            result = await cmd_reset([])

        assert result == 1

        captured = capsys.readouterr()
        assert "Aborted" in captured.out


class TestCmdResetScope:
    """Tests for reset command scope handling."""

    @pytest.mark.asyncio
    async def test_reset_default_scope_is_global(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should use global scope by default."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ) as mock_collect,
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
        ):
            result = await cmd_reset(["--force"])

        assert result == 0
        mock_collect.assert_called_once_with("global")

    @pytest.mark.asyncio
    async def test_reset_all_scope(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should use 'all' scope with --all flag."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ) as mock_collect,
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
        ):
            result = await cmd_reset(["--force", "--all"])

        assert result == 0
        mock_collect.assert_called_once_with("all")

    @pytest.mark.asyncio
    async def test_reset_all_short_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should use 'all' scope with -a flag."""
        mock_paths = MagicMock()
        mock_paths.data = Path("/tmp/data")
        mock_paths.config = Path("/tmp/config")
        mock_paths.cache = Path("/tmp/cache")

        mock_storage = AsyncMock()

        with (
            patch(
                "protocols.cli.handlers.wipe._collect_targets",
                return_value=[],
            ) as mock_collect,
            patch(
                "protocols.cli.instance_db.storage.XDGPaths.resolve",
                return_value=mock_paths,
            ),
            patch(
                "protocols.cli.instance_db.storage.StorageProvider.from_config",
                return_value=mock_storage,
            ),
            patch(
                "models.base.init_db",
                new_callable=AsyncMock,
            ),
        ):
            result = await cmd_reset(["-f", "-a"])

        assert result == 0
        mock_collect.assert_called_once_with("all")
