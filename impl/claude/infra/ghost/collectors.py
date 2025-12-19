"""
Ghost Collectors - Gather real signals from the development environment.

Each collector is responsible for one domain of truth:
- GitCollector: Version control state
- FlinchCollector: Test failure patterns
- InfraCollector: K-Terrarium cluster status
- TraceGhostCollector: Trace analysis data
- MemoryCollector: Four Pillars memory statistics

Collectors are composable and fail gracefully with proper timeout handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from infra.ghost.cache import GlassCacheManager

logger = logging.getLogger(__name__)

# Default timeout for subprocess operations (seconds)
DEFAULT_SUBPROCESS_TIMEOUT = 30.0


@dataclass
class CollectorResult:
    """Result from a collector's gather operation."""

    source: str  # Collector name
    timestamp: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def health_line(self) -> str:
        """One-line summary for health status."""
        if not self.success:
            return f"{self.source}:error"
        return str(self.data.get("health_line", f"{self.source}:ok"))


class GhostCollector(ABC):
    """
    Base class for ghost data collectors.

    Each collector gathers data from one domain and returns
    a CollectorResult with structured data.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Collector identifier."""
        pass

    @abstractmethod
    async def collect(self) -> CollectorResult:
        """Gather data and return result."""
        pass


class GitCollector(GhostCollector):
    """
    Collect git repository state.

    Gathers:
    - Current branch
    - Uncommitted changes (staged/unstaged)
    - Recent commits (last 24h)
    - Dirty file count
    """

    def __init__(self, repo_path: Path | None = None):
        self.repo_path = repo_path or Path.cwd()

    @property
    def name(self) -> str:
        return "git"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        try:
            data: dict[str, Any] = {}

            # Current branch
            result = await self._run_git("rev-parse", "--abbrev-ref", "HEAD")
            if result.returncode == 0:
                data["branch"] = result.stdout.strip()
            else:
                return CollectorResult(
                    source=self.name,
                    timestamp=timestamp,
                    success=False,
                    error="Not a git repository",
                )

            # Status (porcelain for parsing)
            result = await self._run_git("status", "--porcelain")
            if result.returncode == 0:
                lines = [l for l in result.stdout.split("\n") if l.strip()]
                data["dirty_count"] = len(lines)
                data["staged"] = len([l for l in lines if l[0] != " " and l[0] != "?"])
                data["unstaged"] = len([l for l in lines if l[1] != " "])
                data["untracked"] = len([l for l in lines if l.startswith("??")])

            # Recent commits (last 24h)
            result = await self._run_git(
                "log",
                "--oneline",
                "--since=24 hours ago",
                "--format=%h %s",
            )
            if result.returncode == 0:
                commits = [l for l in result.stdout.split("\n") if l.strip()]
                data["commits_24h"] = len(commits)
                data["recent_commits"] = commits[:5]  # Last 5

            # Build health line
            parts = [f"branch:{data.get('branch', 'unknown')}"]
            dirty = data.get("dirty_count", 0)
            if dirty > 0:
                parts.append(f"dirty:{dirty}")
            commits = data.get("commits_24h", 0)
            if commits > 0:
                parts.append(f"commits:{commits}")
            data["health_line"] = " ".join(parts)

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )

    async def _run_git(
        self, *args: str, timeout: float = DEFAULT_SUBPROCESS_TIMEOUT
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a git command asynchronously with timeout.

        Args:
            *args: Git command arguments
            timeout: Timeout in seconds (default: 30s)

        Returns:
            CompletedProcess with stdout/stderr decoded as strings
        """
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=str(self.repo_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return subprocess.CompletedProcess(
                args=["git", *args],
                returncode=proc.returncode or 0,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
            )
        except asyncio.TimeoutError:
            # Kill the process on timeout
            proc.kill()
            await proc.wait()
            logger.warning(f"Git command timed out after {timeout}s: git {' '.join(args)}")
            return subprocess.CompletedProcess(
                args=["git", *args],
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
            )


class FlinchCollector(GhostCollector):
    """
    Collect test failure patterns from FlinchStore.

    Parses .kgents/ghost/test_flinches.jsonl and analyzes:
    - Total flinch count
    - Recent failures (last hour, last 24h)
    - Hot files (most failures)
    - Recurring patterns
    """

    def __init__(self, flinch_path: Path | None = None):
        self.flinch_path = flinch_path or Path.cwd() / ".kgents/ghost/test_flinches.jsonl"

    @property
    def name(self) -> str:
        return "flinch"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        if not self.flinch_path.exists():
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data={
                    "total": 0,
                    "health_line": "flinch:empty",
                },
            )

        try:
            # Parse JSONL
            flinches: list[dict[str, Any]] = []
            with open(self.flinch_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            flinches.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            now = datetime.now().timestamp()
            hour_ago = now - 3600
            day_ago = now - 86400

            # Time-based analysis
            recent_hour = [flinch for flinch in flinches if flinch.get("ts", 0) > hour_ago]
            recent_day = [flinch for flinch in flinches if flinch.get("ts", 0) > day_ago]

            # Hot files (most failures)
            file_counts: dict[str, int] = {}
            for flinch in flinches:
                test = flinch.get("test", "")
                # Extract file path from test name
                if "::" in test:
                    file_path = test.split("::")[0]
                    file_counts[file_path] = file_counts.get(file_path, 0) + 1

            hot_files = sorted(file_counts.items(), key=lambda x: -x[1])[:5]

            # Recurring tests (failed multiple times)
            test_counts: dict[str, int] = {}
            for flinch in flinches:
                test = flinch.get("test", "")
                test_counts[test] = test_counts.get(test, 0) + 1
            recurring = [(t, c) for t, c in test_counts.items() if c > 1]
            recurring.sort(key=lambda x: -x[1])

            data = {
                "total": len(flinches),
                "last_hour": len(recent_hour),
                "last_24h": len(recent_day),
                "hot_files": hot_files,
                "recurring_count": len(recurring),
                "top_recurring": recurring[:5],
            }

            # Build health line
            if len(recent_hour) > 0:
                health = f"flinch:{len(recent_hour)}h/{len(recent_day)}d"
            elif len(recent_day) > 0:
                health = f"flinch:0h/{len(recent_day)}d"
            else:
                health = f"flinch:quiet ({len(flinches)} total)"
            data["health_line"] = health

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )

    def get_patterns(self) -> dict[str, Any]:
        """
        Analyze failure patterns (synchronous for CLI).

        Returns detailed pattern analysis for `kgents flinch --patterns`.
        """
        if not self.flinch_path.exists():
            return {"patterns": [], "message": "No flinch data found"}

        flinches: list[dict[str, Any]] = []
        try:
            with open(self.flinch_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            flinches.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError as e:
            logger.warning(f"Failed to read flinch file: {e}")
            return {"patterns": [], "message": f"Error reading flinch data: {e}"}

        # Group by test module
        module_groups: dict[str, list[dict[str, Any]]] = {}
        for flinch in flinches:
            test = flinch.get("test", "")
            if not isinstance(test, str):
                continue
            if "::" in test:
                module = test.split("::")[0]
            else:
                module = test
            if module not in module_groups:
                module_groups[module] = []
            module_groups[module].append(flinch)

        # Identify patterns
        patterns = []
        for module, failures in module_groups.items():
            if len(failures) >= 3:  # Recurring pattern threshold
                # Check for common test names
                test_names = [failure.get("test", "").split("::")[-1] for failure in failures]
                name_counts: dict[str, int] = {}
                for name in test_names:
                    name_counts[name] = name_counts.get(name, 0) + 1

                if name_counts:
                    top_test = max(name_counts.items(), key=lambda x: x[1])
                    patterns.append(
                        {
                            "module": module,
                            "total_failures": len(failures),
                            "most_common_test": top_test[0],
                            "most_common_count": top_test[1],
                        }
                    )

        patterns.sort(key=lambda x: -int(str(x["total_failures"])))

        return {
            "patterns": patterns[:10],
            "total_modules_with_failures": len(module_groups),
            "total_flinches": len(flinches),
        }

    def get_hot_files(self, limit: int = 10) -> list[tuple[str, int]]:
        """
        Get files with highest failure rate (synchronous for CLI).

        Returns list of (file_path, failure_count) tuples.
        """
        if not self.flinch_path.exists():
            return []

        file_counts: dict[str, int] = {}
        try:
            with open(self.flinch_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            flinch = json.loads(line)
                            test = flinch.get("test", "")
                            if isinstance(test, str) and "::" in test:
                                file_path = test.split("::")[0]
                                file_counts[file_path] = file_counts.get(file_path, 0) + 1
                        except json.JSONDecodeError:
                            continue
        except OSError as e:
            logger.warning(f"Failed to read flinch file for hot files: {e}")
            return []

        return sorted(file_counts.items(), key=lambda x: -x[1])[:limit]


class InfraCollector(GhostCollector):
    """
    Collect K-Terrarium cluster status.

    Gathers:
    - Cluster state (running/paused/stopped/not_found)
    - Pod count and status
    - Recent deployments
    """

    @property
    def name(self) -> str:
        return "infra"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        try:
            # Import here to avoid circular imports
            from infra.k8s import ClusterStatus, KindCluster

            cluster = KindCluster()
            status = cluster.status()

            status_map = {
                ClusterStatus.RUNNING: "running",
                ClusterStatus.PAUSED: "paused",
                ClusterStatus.STOPPED: "stopped",
                ClusterStatus.NOT_FOUND: "not_found",
                ClusterStatus.ERROR: "error",
            }

            data: dict[str, Any] = {
                "cluster_status": status_map.get(status, "unknown"),
            }

            if status == ClusterStatus.RUNNING:
                # Get pod info with timeout
                proc = await asyncio.create_subprocess_exec(
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    "kgents-agents",
                    "-o",
                    "json",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    stdout, _ = await asyncio.wait_for(
                        proc.communicate(), timeout=DEFAULT_SUBPROCESS_TIMEOUT
                    )

                    if proc.returncode == 0:
                        pods_data = json.loads(stdout.decode())
                        # Validate pods_data structure
                        if isinstance(pods_data, dict):
                            items = pods_data.get("items", [])
                            if isinstance(items, list):
                                data["pod_count"] = len(items)

                                # Count by phase with type validation
                                phases: dict[str, int] = {}
                                for item in items:
                                    if isinstance(item, dict):
                                        status_dict = item.get("status", {})
                                        if isinstance(status_dict, dict):
                                            phase = status_dict.get("phase", "Unknown")
                                            if isinstance(phase, str):
                                                phases[phase] = phases.get(phase, 0) + 1
                                data["pod_phases"] = phases
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    logger.warning("kubectl get pods timed out")
                    data["pod_timeout"] = True
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse kubectl output: {e}")

                data["health_line"] = (
                    f"infra:{data['cluster_status']} pods:{data.get('pod_count', 0)}"
                )
            else:
                data["health_line"] = f"infra:{data['cluster_status']}"

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except ImportError:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data={
                    "cluster_status": "not_available",
                    "health_line": "infra:not_available",
                },
            )
        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )


class MetaGhostCollector(GhostCollector):
    """
    Collect meta-construction system health.

    Gathers:
    - Polynomial primitives count
    - Registered operads
    - Compositions generated
    - Sheaf gluings performed
    - Operad law verification status
    """

    @property
    def name(self) -> str:
        return "meta"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        try:
            data: dict[str, Any] = {}

            # Polynomial primitives
            try:
                from agents.poly import primitive_names

                data["primitives_count"] = len(primitive_names())
                data["primitives"] = primitive_names()
            except ImportError:
                data["primitives_count"] = 0
                data["primitives"] = []

            # Registered operads
            try:
                from agents.operad import OperadRegistry

                operads = OperadRegistry.all_operads()
                data["operads_count"] = len(operads)
                data["operads"] = list(operads.keys())

                # Get operation counts per operad
                data["operations_by_operad"] = {
                    name: len(op.operations) for name, op in operads.items()
                }
            except ImportError:
                data["operads_count"] = 0
                data["operads"] = []

            # Sheaf info
            try:
                from agents.sheaf import SOUL_SHEAF

                data["soul_sheaf_contexts"] = len(SOUL_SHEAF.contexts)
            except ImportError:
                data["soul_sheaf_contexts"] = 0

            # Build health line
            parts = [
                f"primitives:{data['primitives_count']}",
                f"operads:{data['operads_count']}",
            ]
            if data.get("soul_sheaf_contexts", 0) > 0:
                parts.append(f"contexts:{data['soul_sheaf_contexts']}")

            data["health_line"] = " ".join(parts)

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )


class TraceGhostCollector(GhostCollector):
    """
    Collect trace analysis data for ghost projection.

    Uses TraceDataProvider to gather:
    - Static analysis metrics (files, definitions, calls)
    - Hottest functions (most callers)
    - Runtime trace status
    - Detected anomalies

    Projects to trace_summary.json in ghost directory.
    """

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or Path.cwd()

    @property
    def name(self) -> str:
        return "trace"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        try:
            from agents.i.data.trace_provider import (
                TraceDataProvider,
                TraceMetrics,
            )

            # Get singleton provider
            provider = TraceDataProvider.get_instance()

            # Set base path for analysis
            impl_path = self.base_path / "impl" / "claude"
            if impl_path.exists():
                provider.set_base_path(str(impl_path))
            else:
                provider.set_base_path(str(self.base_path))

            # Collect metrics (include static analysis)
            metrics: TraceMetrics = await provider.collect_metrics(include_static=True)

            # Build data payload
            data: dict[str, Any] = {
                "static_analysis": {
                    "files_analyzed": metrics.static.files_analyzed,
                    "definitions_found": metrics.static.definitions_found,
                    "calls_found": metrics.static.calls_found,
                    "ghost_calls_found": metrics.static.ghost_calls_found,
                    "analysis_time_ms": metrics.static.analysis_time_ms,
                    "last_analyzed": (
                        metrics.static.last_analyzed.isoformat()
                        if metrics.static.last_analyzed
                        else None
                    ),
                    "is_available": metrics.static.is_available,
                    "hottest_functions": metrics.static.hottest_functions,
                },
                "runtime": {
                    "total_events": metrics.runtime.total_events,
                    "unique_functions": metrics.runtime.unique_functions,
                    "avg_depth": metrics.runtime.avg_depth,
                    "max_depth": metrics.runtime.max_depth,
                    "threads_observed": metrics.runtime.threads_observed,
                    "is_collecting": metrics.runtime.is_collecting,
                    "is_available": metrics.runtime.is_available,
                    "hot_paths": metrics.runtime.hot_paths,
                },
                "anomalies": [
                    {
                        "type": a.type,
                        "description": a.description,
                        "location": a.location,
                        "severity": a.severity,
                        "detected_at": a.detected_at.isoformat(),
                    }
                    for a in metrics.anomalies
                ],
                "collected_at": metrics.collected_at.isoformat(),
            }

            # Build health line
            if not metrics.static.is_available:
                health_line = "trace:unavailable"
            else:
                anomaly_count = len(metrics.anomalies)
                health_parts = [
                    f"trace:{metrics.static.files_analyzed}files",
                    f"defs:{metrics.static.definitions_found}",
                ]
                if anomaly_count > 0:
                    health_parts.append(f"anomalies:{anomaly_count}")
                health_line = " ".join(health_parts)

            data["health_line"] = health_line

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except ImportError as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,  # Graceful degradation
                data={
                    "health_line": "trace:not_available",
                    "error": f"TraceDataProvider not available: {e}",
                },
            )
        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )


class MemoryCollector(GhostCollector):
    """
    Collect Four Pillars memory data for ghost projection.

    Uses MemoryDataProvider to gather:
    - Memory Crystal statistics (dimension, resolution, hot concepts)
    - Pheromone Field statistics (traces, deposits, evaporation)
    - Active Inference statistics (precision, entropy, beliefs)
    - Overall memory health metrics

    Projects to memory_summary.json in ghost directory.
    """

    def __init__(self, cache_manager: "GlassCacheManager | None" = None):
        """
        Initialize MemoryCollector.

        Args:
            cache_manager: Optional GlassCacheManager for writing to cache.
                          If None, collector only returns data without caching.
        """
        self.cache_manager = cache_manager

    @property
    def name(self) -> str:
        return "memory"

    async def collect(self) -> CollectorResult:
        timestamp = datetime.now().isoformat()

        try:
            from agents.i.data.memory_provider import (
                MemoryDataProvider,
                create_memory_provider_async,
            )

            # Create provider in demo mode for now
            # In the future, this will connect to live agent memory
            provider: MemoryDataProvider = await create_memory_provider_async(demo_mode=True)

            # Gather all Four Pillars stats
            crystal_stats = provider.get_crystal_stats()
            field_stats = await provider.get_field_stats()
            inference_stats = provider.get_inference_stats()
            health_report = provider.compute_health()

            # Build data payload
            data: dict[str, Any] = {
                "crystal": crystal_stats,
                "field": field_stats,
                "inference": inference_stats,
                "health": health_report,
            }

            # Write to cache if manager is available
            if self.cache_manager is not None:
                if crystal_stats:
                    self.cache_manager.write(
                        key="memory/crystal",
                        data=crystal_stats,
                        agentese_path="self.memory.crystal.manifest",
                    )
                if field_stats:
                    self.cache_manager.write(
                        key="memory/field",
                        data=field_stats,
                        agentese_path="self.memory.field.manifest",
                    )
                if inference_stats:
                    self.cache_manager.write(
                        key="memory/inference",
                        data=inference_stats,
                        agentese_path="self.memory.inference.manifest",
                    )
                self.cache_manager.write(
                    key="memory/health",
                    data=health_report,
                    agentese_path="self.memory.health.manifest",
                )

            # Build health line
            if health_report["status"] == "HEALTHY":
                health_parts = [
                    f"memory:{health_report['status'].lower()}",
                    f"score:{health_report['health_score']:.0%}",
                ]
            elif health_report["status"] == "DEGRADED":
                health_parts = [
                    f"memory:{health_report['status'].lower()}",
                    f"score:{health_report['health_score']:.0%}",
                ]
            else:
                health_parts = [
                    f"memory:{health_report['status'].lower()}",
                    f"score:{health_report['health_score']:.0%}",
                ]

            # Add concept count if available
            if crystal_stats:
                health_parts.append(f"concepts:{crystal_stats['concept_count']}")

            health_line = " ".join(health_parts)
            data["health_line"] = health_line

            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,
                data=data,
            )

        except ImportError as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=True,  # Graceful degradation
                data={
                    "health_line": "memory:not_available",
                    "error": f"MemoryDataProvider not available: {e}",
                },
            )
        except Exception as e:
            return CollectorResult(
                source=self.name,
                timestamp=timestamp,
                success=False,
                error=str(e),
            )


def create_all_collectors(project_root: Path | None = None) -> list[GhostCollector]:
    """
    Create all available collectors.

    Args:
        project_root: Project root path (defaults to cwd)

    Returns:
        List of configured collectors
    """
    if project_root is None:
        project_root = Path.cwd()

    # Import CISignalCollector here to avoid circular imports
    from .ci_collector import CISignalCollector

    return [
        GitCollector(repo_path=project_root),
        FlinchCollector(flinch_path=project_root / ".kgents/ghost/test_flinches.jsonl"),
        CISignalCollector(signal_path=project_root / ".kgents/ghost/ci_signals.jsonl"),
        InfraCollector(),
        MetaGhostCollector(),
        TraceGhostCollector(base_path=project_root),
        MemoryCollector(),
    ]
