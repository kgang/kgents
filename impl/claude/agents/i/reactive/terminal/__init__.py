"""
Terminal Rendering: Wave 7 of the Reactive Substrate.

ANSI colors, box drawing, ASCII art, and terminal-native display.
All rendering is pure and deterministic. The terminal is the canvas.

Components:
- ansi: ANSI color and style system
- box: Unicode box drawing characters
- art: ASCII art primitives (bars, sparklines, gauges)
- adapter: Terminal capability detection and graceful degradation

Example:
    from agents.i.reactive.terminal import (
        ANSIColor,
        Color,
        BoxRenderer,
        BoxSpec,
        BoxStyle,
        TerminalCapabilities,
        TerminalOutput,
        render_hbar,
        render_sparkline,
        HBar,
        Sparkline,
    )

    # Detect terminal capabilities
    caps = TerminalCapabilities.detect()
    term = TerminalOutput(caps)

    # Draw a box
    renderer = BoxRenderer()
    lines = renderer.box(BoxSpec(width=40, height=10, title="Dashboard"))

    # Draw colored content
    for line in lines:
        term.writeln(line)

    # Add a progress bar
    term.writeln(render_hbar(HBar(value=0.7, width=30)))

    # Add a sparkline
    term.writeln(render_sparkline(Sparkline(values=(0.1, 0.4, 0.8, 0.5, 0.3))))

    term.flush()
"""

# ANSI Color System
# Terminal Adapter
from agents.i.reactive.terminal.adapter import (
    DegradedRenderer,
    LayoutConstraints,
    ResponsiveLayout,
    TerminalCapabilities,
    TerminalOutput,
    UnicodeSupport,
    full_capabilities,
    minimal_capabilities,
)
from agents.i.reactive.terminal.ansi import (
    ANSIColor,
    ANSISequence,
    ANSIStyle,
    Color,
    ColorMode,
    ColorScheme,
    SemanticColors,
    StyleSpec,
    get_scheme,
    phase_to_color,
)

# ASCII Art Primitives
from agents.i.reactive.terminal.art import (
    BarStyle,
    Gauge,
    HBar,
    Panel,
    ProgressBar,
    Sparkline,
    VBar,
    align_text,
    horizontal_concat,
    render_gauge,
    render_hbar,
    render_panel,
    render_progress,
    render_sparkline,
    render_vbar,
    spinner_frame,
    vertical_concat,
)

# Box Drawing
from agents.i.reactive.terminal.box import (
    BoxChars,
    BoxRenderer,
    BoxSpec,
    BoxStyle,
    ColumnSpec,
    NestedBox,
    TableRenderer,
    TableSpec,
    content_box,
    get_chars,
    horizontal_rule,
    simple_box,
    vertical_rule,
)

__all__ = [
    # ANSI
    "ANSIColor",
    "ANSISequence",
    "ANSIStyle",
    "Color",
    "ColorMode",
    "ColorScheme",
    "SemanticColors",
    "StyleSpec",
    "get_scheme",
    "phase_to_color",
    # Box Drawing
    "BoxChars",
    "BoxRenderer",
    "BoxSpec",
    "BoxStyle",
    "ColumnSpec",
    "NestedBox",
    "TableRenderer",
    "TableSpec",
    "content_box",
    "get_chars",
    "horizontal_rule",
    "simple_box",
    "vertical_rule",
    # ASCII Art
    "BarStyle",
    "Gauge",
    "HBar",
    "Panel",
    "ProgressBar",
    "Sparkline",
    "VBar",
    "align_text",
    "horizontal_concat",
    "render_gauge",
    "render_hbar",
    "render_panel",
    "render_progress",
    "render_sparkline",
    "render_vbar",
    "spinner_frame",
    "vertical_concat",
    # Terminal Adapter
    "DegradedRenderer",
    "LayoutConstraints",
    "ResponsiveLayout",
    "TerminalCapabilities",
    "TerminalOutput",
    "UnicodeSupport",
    "full_capabilities",
    "minimal_capabilities",
]
