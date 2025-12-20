"""
W-gent Fidelity Adapters: Auto-detect and render at appropriate detail level.

W-gents operate at three fidelity levels, auto-detected or user-specified:

1. Teletype (Raw Stream): Plain text logs, Matrix green on black
2. Documentarian (Rendered Output): Markdown → HTML, reader mode
3. LiveWire (Structured Dashboard): JSON state → interactive cards

The adapter pattern: W-gent adapts to agent capabilities rather than
dictating format.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from .protocol import WireEvent, WireReader


class Fidelity(Enum):
    """The three fidelity levels for wire visualization."""

    TELETYPE = "teletype"  # Raw text stream
    DOCUMENTARIAN = "documentarian"  # Rendered markdown
    LIVEWIRE = "livewire"  # Structured dashboard


def detect_fidelity(reader: WireReader) -> Fidelity:
    """
    Auto-detect appropriate fidelity level based on available data.

    Detection order:
    1. LiveWire: If state.json exists with structured data
    2. Documentarian: If output/*.md files exist
    3. Teletype: Fallback to raw logs

    Args:
        reader: WireReader pointing to agent's .wire directory

    Returns:
        Detected Fidelity level
    """
    if not reader.exists():
        return Fidelity.TELETYPE

    # Check for structured state
    state = reader.read_state()
    if state is not None and state.progress is not None:
        return Fidelity.LIVEWIRE

    # Check for markdown outputs
    outputs = reader.list_outputs()
    if any(f.endswith(".md") for f in outputs):
        return Fidelity.DOCUMENTARIAN

    # Fallback
    return Fidelity.TELETYPE


@dataclass
class RenderResult:
    """Result of rendering wire state."""

    html: str
    content_type: str = "text/html"
    refresh_seconds: Optional[int] = None  # For auto-refresh


class FidelityAdapter(ABC):
    """Base class for fidelity adapters."""

    def __init__(self, reader: WireReader) -> None:
        self.reader = reader

    @property
    @abstractmethod
    def fidelity(self) -> Fidelity:
        """The fidelity level this adapter handles."""
        ...

    @abstractmethod
    def render(self) -> RenderResult:
        """Render the current state to HTML."""
        ...

    @abstractmethod
    def render_stream_event(self, event: WireEvent) -> str:
        """Render a single stream event for SSE."""
        ...


class TeletypeAdapter(FidelityAdapter):
    """
    Teletype adapter: Raw text stream.

    Aesthetic: Matrix green on black, monospace, minimal processing.

    When: Agent outputs plain text logs
    Serves: Raw text with minimal formatting
    """

    @property
    def fidelity(self) -> Fidelity:
        return Fidelity.TELETYPE

    def render(self) -> RenderResult:
        """Render teletype view."""
        events = self.reader.read_stream(tail=50)

        event_lines = []
        for event in events:
            ts = event.timestamp.strftime("%H:%M:%S")
            event_lines.append(
                f'<div class="event">'
                f'<span class="time">{ts}</span> '
                f'<span class="stage">[{event.stage}]</span> '
                f"{event.message}"
                f"</div>"
            )

        events_html = "\n".join(event_lines) if event_lines else "Waiting for signal..."

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>teletype :: {self.reader.agent_name}</title>
    <style>
        body {{
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 14px;
            padding: 20px;
            margin: 0;
        }}
        .header {{
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 18px;
        }}
        .stream {{
            height: calc(100vh - 150px);
            overflow-y: auto;
        }}
        .event {{
            margin: 4px 0;
            white-space: pre-wrap;
        }}
        .time {{
            color: #888888;
        }}
        .stage {{
            color: #ffff00;
        }}
        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
        }}
        .controls a {{
            color: #00ff00;
            margin-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <span class="title">teletype :: {self.reader.agent_name}</span>
    </div>
    <div class="stream" id="stream">
        {events_html}
    </div>
    <div class="controls">
        <a href="#" onclick="location.reload()">[refresh]</a>
        <a href="/download">[download log]</a>
    </div>
    <script>
        // Auto-scroll to bottom
        const stream = document.getElementById('stream');
        stream.scrollTop = stream.scrollHeight;

        // Auto-refresh every 2 seconds
        setTimeout(() => location.reload(), 2000);
    </script>
</body>
</html>"""
        return RenderResult(html=html, refresh_seconds=2)

    def render_stream_event(self, event: WireEvent) -> str:
        """Render event for SSE."""
        ts = event.timestamp.strftime("%H:%M:%S")
        return f"{ts} [{event.stage}] {event.message}"


class DocumentarianAdapter(FidelityAdapter):
    """
    Documentarian adapter: Rendered markdown output.

    Aesthetic: Paper-like background, reader mode typography.

    When: Agent generates markdown/reports
    Serves: Rendered HTML with clean typography
    """

    @property
    def fidelity(self) -> Fidelity:
        return Fidelity.DOCUMENTARIAN

    def render(self) -> RenderResult:
        """Render documentarian view."""
        # Find markdown outputs
        outputs = self.reader.list_outputs()
        md_files = [f for f in outputs if f.endswith(".md")]

        content_html = ""
        if md_files:
            # Render the most recent markdown file
            latest = md_files[-1]
            content = self.reader.read_output(latest)
            if content:
                # Simple markdown → HTML (basic conversion)
                content_html = self._simple_markdown_to_html(content)
        else:
            content_html = "<p><em>No documents generated yet.</em></p>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>documentarian :: {self.reader.agent_name}</title>
    <style>
        body {{
            background: #fdfbf7;
            color: #1a1918;
            font-family: 'Georgia', serif;
            font-size: 18px;
            line-height: 1.6;
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .header {{
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #666;
        }}
        h1, h2, h3 {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: normal;
        }}
        h1 {{ font-size: 28px; }}
        h2 {{ font-size: 22px; margin-top: 30px; }}
        h3 {{ font-size: 18px; margin-top: 20px; }}
        code {{
            background: #f0f0f0;
            padding: 2px 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
        }}
        pre {{
            background: #f0f0f0;
            padding: 15px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
        }}
        blockquote {{
            border-left: 3px solid #ddd;
            margin-left: 0;
            padding-left: 20px;
            font-style: italic;
            color: #555;
        }}
        .controls {{
            position: fixed;
            top: 20px;
            right: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }}
        .controls a {{
            color: #666;
            margin-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        documentarian :: {self.reader.agent_name}
    </div>
    <div class="content">
        {content_html}
    </div>
    <div class="controls">
        <a href="#" onclick="location.reload()">[refresh]</a>
        <a href="/download">[download]</a>
    </div>
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>"""
        return RenderResult(html=html, refresh_seconds=5)

    def render_stream_event(self, event: WireEvent) -> str:
        """Render event for SSE."""
        return f"[{event.stage}] {event.message}"

    def _simple_markdown_to_html(self, md: str) -> str:
        """Simple markdown to HTML conversion (no dependencies)."""
        import re

        html = md

        # Headers
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Code blocks
        html = re.sub(r"```(\w*)\n(.*?)```", r"<pre><code>\2</code></pre>", html, flags=re.DOTALL)
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Blockquotes
        html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)

        # Lists
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        # Paragraphs (simple)
        lines = html.split("\n")
        result = []
        in_list = False
        for line in lines:
            if line.startswith("<li>"):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                result.append(line)
            else:
                if in_list:
                    result.append("</ul>")
                    in_list = False
                if line.strip() and not line.startswith("<"):
                    result.append(f"<p>{line}</p>")
                else:
                    result.append(line)
        if in_list:
            result.append("</ul>")

        return "\n".join(result)


class LiveWireAdapter(FidelityAdapter):
    """
    LiveWire adapter: Structured dashboard with real-time updates.

    Aesthetic: Card-based dashboard, progress bars, real-time SSE.

    When: Agent exposes structured state (JSON/API)
    Serves: Interactive dashboard with cards
    """

    @property
    def fidelity(self) -> Fidelity:
        return Fidelity.LIVEWIRE

    def render(self) -> RenderResult:
        """Render live wire view."""
        state = self.reader.read_state()
        events = self.reader.read_stream(tail=10)
        metrics = self.reader.read_metrics()

        # State card
        if state:
            phase = state.phase
            task = state.current_task or "—"
            progress = state.progress or 0.0
            progress_pct = int(progress * 100)
            progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
        else:
            phase = "unknown"
            task = "No state available"
            progress_pct = 0
            progress_bar = "░" * 20

        # Events HTML
        event_lines = []
        for event in events:
            ts = event.timestamp.strftime("%H:%M:%S")
            icon = (
                "✓"
                if event.level == "INFO"
                else "⚠"
                if event.level == "WARN"
                else "✗"
                if event.level == "ERROR"
                else "·"
            )
            event_lines.append(
                f'<div class="event"><span class="icon">{icon}</span> '
                f'<span class="time">{ts}</span> '
                f'<span class="stage">[{event.stage}]</span> '
                f"{event.message}</div>"
            )
        events_html = (
            "\n".join(event_lines) if event_lines else "<div class='event'>No events yet</div>"
        )

        # Metrics HTML
        if metrics:
            uptime_min = int(metrics.uptime_seconds / 60)
            uptime_sec = int(metrics.uptime_seconds % 60)
            uptime_str = f"{uptime_min:02d}:{uptime_sec:02d}"
            memory_str = f"{metrics.memory_mb:.0f} MB" if metrics.memory_mb else "—"
            api_str = str(metrics.api_calls) if metrics.api_calls else "—"
            tokens_str = f"{metrics.tokens_processed:,}" if metrics.tokens_processed else "—"
        else:
            uptime_str = "—"
            memory_str = "—"
            api_str = "—"
            tokens_str = "—"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>live wire :: {self.reader.agent_name}</title>
    <style>
        body {{
            background: #1a1918;
            color: #fdfbf7;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 14px;
            padding: 20px;
            margin: 0;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 18px;
        }}
        .phase {{
            padding: 4px 12px;
            border-radius: 4px;
            background: #333;
        }}
        .phase.active {{ background: #2d5016; }}
        .phase.waking {{ background: #4a3f00; }}
        .phase.waning {{ background: #4a2800; }}
        .phase.empty {{ background: #4a0000; }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: #2a2928;
            border-radius: 8px;
            padding: 20px;
        }}
        .card-title {{
            font-size: 12px;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 15px;
        }}
        .task {{
            font-size: 16px;
            margin-bottom: 10px;
        }}
        .progress {{
            font-family: monospace;
            color: #00ff00;
        }}
        .progress-pct {{
            color: #888;
            margin-left: 10px;
        }}
        .events {{
            max-height: 250px;
            overflow-y: auto;
        }}
        .event {{
            margin: 8px 0;
            font-size: 13px;
        }}
        .event .icon {{
            color: #00ff00;
        }}
        .event .time {{
            color: #666;
        }}
        .event .stage {{
            color: #888;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .metric {{
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            color: #00ff00;
        }}
        .metric-label {{
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
        }}
        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
        }}
        .controls a {{
            color: #666;
            margin-left: 20px;
            text-decoration: none;
        }}
        .controls a:hover {{
            color: #fdfbf7;
        }}
    </style>
</head>
<body>
    <div class="header">
        <span class="title">live wire :: {self.reader.agent_name}</span>
        <span class="phase {phase}">{phase}</span>
    </div>

    <div class="cards">
        <div class="card">
            <div class="card-title">Current Task</div>
            <div class="task">{task}</div>
            <div class="progress">{progress_bar}<span class="progress-pct">{progress_pct}%</span></div>
        </div>

        <div class="card">
            <div class="card-title">Event Stream</div>
            <div class="events" id="events">
                {events_html}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Metrics</div>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{uptime_str}</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{memory_str}</div>
                    <div class="metric-label">Memory</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{api_str}</div>
                    <div class="metric-label">API Calls</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{tokens_str}</div>
                    <div class="metric-label">Tokens</div>
                </div>
            </div>
        </div>
    </div>

    <div class="controls">
        <a href="#" onclick="location.reload()">[refresh]</a>
        <a href="/export">[export to I-gent]</a>
        <a href="/download">[download log]</a>
    </div>

    <script>
        // Auto-refresh every 1 second for live updates
        setTimeout(() => location.reload(), 1000);

        // Scroll events to bottom
        const events = document.getElementById('events');
        events.scrollTop = events.scrollHeight;
    </script>
</body>
</html>"""
        return RenderResult(html=html, refresh_seconds=1)

    def render_stream_event(self, event: WireEvent) -> str:
        """Render event for SSE as JSON."""
        return json.dumps(event.to_dict())


def get_adapter(reader: WireReader, fidelity: Optional[Fidelity] = None) -> FidelityAdapter:
    """
    Get the appropriate adapter for a wire reader.

    Args:
        reader: WireReader pointing to agent's .wire directory
        fidelity: Explicit fidelity level (auto-detect if None)

    Returns:
        Appropriate FidelityAdapter instance
    """
    if fidelity is None:
        fidelity = detect_fidelity(reader)

    adapters: dict[Fidelity, Type[FidelityAdapter]] = {
        Fidelity.TELETYPE: TeletypeAdapter,
        Fidelity.DOCUMENTARIAN: DocumentarianAdapter,
        Fidelity.LIVEWIRE: LiveWireAdapter,
    }

    return adapters[fidelity](reader)
