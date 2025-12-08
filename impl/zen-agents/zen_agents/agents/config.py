"""
Config Resolution as Ground + Sublate.

Configuration tiers are grounded facts that may conflict.
Tiers: session > portal > defaults.

THE BOOTSTRAP PARADOX:
> Ground cannot be bypassed. LLMs can amplify but not replace Ground.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union
import json
import os

from bootstrap import (
    Agent,
    Ground,
    Facts,
    PersonaSeed,
    WorldSeed,
    Sublate,
    Tension,
    TensionMode,
    Synthesis,
    ResolutionType,
    HoldTension,
)


# Default configuration
DEFAULT_CONFIG = {
    "poll_interval": 1.0,
    "grace_period": 5.0,
    "max_sessions": 10,
    "scrollback_lines": 50000,
    "default_shell": os.environ.get("SHELL", "/bin/bash"),
    "tmux_prefix": "zen",
}


@dataclass
class ZenConfig:
    """Merged configuration for zen-agents."""
    poll_interval: float = 1.0
    grace_period: float = 5.0
    max_sessions: int = 10
    scrollback_lines: int = 50000
    default_shell: str = "/bin/bash"
    tmux_prefix: str = "zen"

    # Session type commands
    session_commands: dict[str, str] = field(default_factory=lambda: {
        "claude": "claude",
        "codex": "codex",
        "gemini": "gemini",
        "shell": os.environ.get("SHELL", "/bin/bash"),
        "openrouter": "python -m openrouter_cli",
        # LLM-backed kgents - show usage instructions (use printf for portability, no read -p)
        "creativity": "printf '🎨 CREATIVITY SESSION\\n\\nThis session uses CreativityCoach for idea expansion.\\n\\nUsage (from TUI LogViewer):\\n  /connect <idea>    Find associations\\n  /constrain <idea>  Add creative limitations\\n  /question <idea>   Challenge assumptions\\n  <idea>             Expand variations (default)\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
        "robin": "printf '🔬 ROBIN SESSION\\n\\nRobin is your scientific companion.\\nComposes K-gent + HypothesisEngine + HegelAgent.\\n\\nUsage:\\n  Enter scientific queries for dialectic-refined exploration.\\n  Hypotheses will be generated with falsification tests.\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
        "hypothesis": "printf '🧪 HYPOTHESIS SESSION\\n\\nUses HypothesisEngine for Popperian hypothesis generation.\\n\\nUsage:\\n  Enter observations to generate falsifiable hypotheses.\\n  Each hypothesis includes suggested falsification tests.\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
        "kgent": "printf '🤖 K-GENT SESSION\\n\\nPersonalized dialogue with Kent simulacra.\\n\\nDialogue modes:\\n  /challenge <msg>  Pushback, devils advocate\\n  /advise <msg>     Actionable suggestions\\n  /explore <msg>    Open-ended exploration\\n  <msg>             Reflect mode (default)\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
    })

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ZenConfig":
        """Create config from dictionary."""
        # Merge session_commands with defaults (don't replace with empty dict)
        default_commands = {
            "claude": "claude",
            "codex": "codex",
            "gemini": "gemini",
            "shell": os.environ.get("SHELL", "/bin/bash"),
            "openrouter": "python -m openrouter_cli",
            # LLM-backed kgents (use printf for portability, no read -p)
            "creativity": "printf '🎨 CREATIVITY SESSION\\n\\nThis session uses CreativityCoach for idea expansion.\\n\\nUsage (from TUI LogViewer):\\n  /connect <idea>    Find associations\\n  /constrain <idea>  Add creative limitations\\n  /question <idea>   Challenge assumptions\\n  <idea>             Expand variations (default)\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
            "robin": "printf '🔬 ROBIN SESSION\\n\\nRobin is your scientific companion.\\nComposes K-gent + HypothesisEngine + HegelAgent.\\n\\nUsage:\\n  Enter scientific queries for dialectic-refined exploration.\\n  Hypotheses will be generated with falsification tests.\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
            "hypothesis": "printf '🧪 HYPOTHESIS SESSION\\n\\nUses HypothesisEngine for Popperian hypothesis generation.\\n\\nUsage:\\n  Enter observations to generate falsifiable hypotheses.\\n  Each hypothesis includes suggested falsification tests.\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
            "kgent": "printf '🤖 K-GENT SESSION\\n\\nPersonalized dialogue with Kent simulacra.\\n\\nDialogue modes:\\n  /challenge <msg>  Pushback, devils advocate\\n  /advise <msg>     Actionable suggestions\\n  /explore <msg>    Open-ended exploration\\n  <msg>             Reflect mode (default)\\n\\nSelect this session and use \"l\" to view logs, then Analyze.\\n\\n[Press Enter to continue] ' && read && exec $SHELL",
        }
        session_commands = {**default_commands, **data.get("session_commands", {})}

        return cls(
            poll_interval=data.get("poll_interval", 1.0),
            grace_period=data.get("grace_period", 5.0),
            max_sessions=data.get("max_sessions", 10),
            scrollback_lines=data.get("scrollback_lines", 50000),
            default_shell=data.get("default_shell", "/bin/bash"),
            tmux_prefix=data.get("tmux_prefix", "zen"),
            session_commands=session_commands,
        )


def load_config_file(path: Path) -> dict[str, Any]:
    """Load config from JSON file if it exists."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


class ConfigGround(Ground):
    """
    Load config from all tiers.

    Grounds the irreducible facts: what the user/environment has configured.
    """

    def __init__(
        self,
        session_config: Optional[dict[str, Any]] = None,
        portal_dir: Optional[Path] = None,
    ):
        """
        Initialize with optional session-level config and portal directory.

        session_config: Direct config for this session
        portal_dir: Directory containing .zen-agents.json
        """
        self._session_config = session_config or {}
        self._portal_dir = portal_dir or Path.cwd()

    @property
    def name(self) -> str:
        return "ConfigGround"

    async def invoke(self, _: None) -> Facts:
        """
        Load config from all tiers and return as Facts.

        Tiers (lowest to highest priority):
        1. Default config
        2. User config (~/.config/zen-agents/config.json)
        3. Portal config (.zen-agents.json in portal_dir)
        4. Session config (passed at runtime)
        """
        # Load each tier
        default_config = DEFAULT_CONFIG.copy()

        user_config_path = Path.home() / ".config" / "zen-agents" / "config.json"
        user_config = load_config_file(user_config_path)

        portal_config_path = self._portal_dir / ".zen-agents.json"
        portal_config = load_config_file(portal_config_path)

        session_config = self._session_config

        return Facts(
            persona=PersonaSeed(
                name="zen-agents",
                roles=["session-manager", "ai-orchestrator"],
                preferences={
                    "poll_interval": session_config.get(
                        "poll_interval",
                        portal_config.get(
                            "poll_interval",
                            user_config.get("poll_interval", 1.0)
                        )
                    ),
                    "grace_period": session_config.get(
                        "grace_period",
                        portal_config.get(
                            "grace_period",
                            user_config.get("grace_period", 5.0)
                        )
                    ),
                    "max_sessions": session_config.get(
                        "max_sessions",
                        portal_config.get(
                            "max_sessions",
                            user_config.get("max_sessions", 10)
                        )
                    ),
                },
                patterns={
                    "iteration": ["Fix-based polling", "no while-True loops"],
                    "conflict": ["Contradict detection", "Sublate resolution"],
                },
                values=["composability", "explicit conflict handling", "contemplative UI"],
                dislikes=["silent failures", "monolithic functions", "implicit state"],
            ),
            world=WorldSeed(
                date=datetime.now().isoformat(),
                context={
                    "tiers": {
                        "default": default_config,
                        "user": user_config,
                        "portal": portal_config,
                        "session": session_config,
                    },
                    "portal_dir": str(self._portal_dir),
                },
                active_projects=[],
            ),
        )


class ConfigTension(Tension):
    """Tension between config tiers."""

    def __init__(
        self,
        mode: "TensionMode",
        thesis: Any,
        antithesis: Any,
        description: str,
        key: str,
        tier_a: str,
        tier_b: str,
        value_a: Any,
        value_b: Any,
        severity: float = 0.5,
    ):
        super().__init__(
            mode=mode,
            thesis=thesis,
            antithesis=antithesis,
            description=description,
            severity=severity,
        )
        self.key = key
        self.tier_a = tier_a
        self.tier_b = tier_b
        self.value_a = value_a
        self.value_b = value_b


class ConfigSublate(Sublate):
    """
    Merge config tiers: session > portal > user > default.

    This is straightforward precedence-based merge, not complex synthesis.
    """

    @property
    def name(self) -> str:
        return "ConfigSublate"

    async def invoke(self, tension: Tension) -> Union[Synthesis, HoldTension]:
        """
        Resolve config tension by tier precedence.

        Higher tiers always win (session > portal > user > default).
        """
        if not isinstance(tension, ConfigTension):
            # For generic config tensions, merge with standard precedence
            if hasattr(tension, "thesis") and isinstance(tension.thesis, dict):
                tiers = tension.thesis
                merged = {
                    **tiers.get("default", {}),
                    **tiers.get("user", {}),
                    **tiers.get("portal", {}),
                    **tiers.get("session", {}),
                }
                return Synthesis(
                    resolution_type=ResolutionType.ELEVATE,
                    result=merged,
                    explanation="Merged with session > portal > user > default precedence",
                    preserved=list(tiers.values()),
                    negated=[],
                )

            # Unknown tension type
            return HoldTension(
                tension=tension,
                reason="Unknown config tension type",
                revisit_conditions=["Handler implemented for this tension type"],
            )

        # Specific key conflict - higher tier wins
        config_tension = tension
        tier_order = ["default", "user", "portal", "session"]

        tier_a_idx = tier_order.index(config_tension.tier_a)
        tier_b_idx = tier_order.index(config_tension.tier_b)

        if tier_a_idx > tier_b_idx:
            winner = config_tension.value_a
            winner_tier = config_tension.tier_a
        else:
            winner = config_tension.value_b
            winner_tier = config_tension.tier_b

        return Synthesis(
            resolution_type=ResolutionType.NEGATE,
            result={config_tension.key: winner},
            explanation=f"{winner_tier} config takes precedence for '{config_tension.key}'",
            preserved=[winner],
            negated=[
                config_tension.value_a if winner != config_tension.value_a else config_tension.value_b
            ],
        )


class ResolveConfig(Agent[Facts, ZenConfig]):
    """
    Resolve grounded Facts into final ZenConfig.

    Merges all tiers and returns usable configuration.
    """

    @property
    def name(self) -> str:
        return "ResolveConfig"

    async def invoke(self, facts: Facts) -> ZenConfig:
        """Merge config tiers and return ZenConfig."""
        tiers = facts.world.context.get("tiers", {})

        # Merge with precedence
        merged = {
            **tiers.get("default", {}),
            **tiers.get("user", {}),
            **tiers.get("portal", {}),
            **tiers.get("session", {}),
        }

        return ZenConfig.from_dict(merged)
