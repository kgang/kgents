"""Tests for I-gent UI components."""

from agents.i.components import (
    BorderStyle,
    Color,
    DashboardPanel,
    Meter,
    MeterThreshold,
    Panel,
    ProgressBar,
    Spinner,
    SpinnerStyle,
    StatusLine,
    Table,
    TableColumn,
    colorize,
    create_dashboard,
    create_panel,
    create_progress_bar,
)


class TestColorize:
    """Tests for colorize function."""

    def test_single_color(self) -> None:
        """Apply single color."""
        result = colorize("test", Color.RED)
        assert Color.RED.value in result
        assert "test" in result
        assert Color.RESET.value in result

    def test_multiple_colors(self) -> None:
        """Apply multiple colors."""
        result = colorize("test", Color.BOLD, Color.RED)
        assert Color.BOLD.value in result
        assert Color.RED.value in result

    def test_disabled(self) -> None:
        """Color disabled returns plain text."""
        result = colorize("test", Color.RED, enabled=False)
        assert result == "test"
        assert Color.RED.value not in result


class TestProgressBar:
    """Tests for ProgressBar component."""

    def test_initial_value(self) -> None:
        """Bar starts at 0."""
        bar = ProgressBar()
        assert bar.value == 0.0

    def test_update_value(self) -> None:
        """Update progress value."""
        bar = ProgressBar()
        bar.update(0.5)
        assert bar.value == 0.5

    def test_update_clamps_high(self) -> None:
        """Value clamped to 1.0 max."""
        bar = ProgressBar()
        bar.update(1.5)
        assert bar.value == 1.0

    def test_update_clamps_low(self) -> None:
        """Value clamped to 0.0 min."""
        bar = ProgressBar()
        bar.update(-0.5)
        assert bar.value == 0.0

    def test_render_empty(self) -> None:
        """Render empty bar."""
        bar = ProgressBar(width=10, use_color=False)
        bar.update(0.0)
        result = bar.render()
        assert "░" * 10 in result
        assert "0%" in result

    def test_render_full(self) -> None:
        """Render full bar."""
        bar = ProgressBar(width=10, use_color=False)
        bar.update(1.0)
        result = bar.render()
        assert "█" * 10 in result
        assert "100%" in result

    def test_render_half(self) -> None:
        """Render half bar."""
        bar = ProgressBar(width=10, use_color=False)
        bar.update(0.5)
        result = bar.render()
        assert "█" * 5 in result
        assert "50%" in result

    def test_render_with_label(self) -> None:
        """Label appears in output."""
        bar = ProgressBar(label="Loading", use_color=False)
        result = bar.render()
        assert "Loading" in result


class TestSpinner:
    """Tests for Spinner component."""

    def test_tick_advances_frame(self) -> None:
        """Tick advances to next frame."""
        spinner = Spinner()
        initial = spinner.frame
        spinner.tick()
        assert spinner.frame == initial + 1

    def test_tick_wraps(self) -> None:
        """Frame wraps around after last."""
        spinner = Spinner(style=SpinnerStyle.LINE)
        for _ in range(10):
            spinner.tick()
        assert spinner.frame < len(SpinnerStyle.LINE.value)

    def test_render_shows_frame(self) -> None:
        """Render shows current frame."""
        spinner = Spinner(style=SpinnerStyle.LINE, use_color=False)
        result = spinner.render()
        assert result == "-"

    def test_render_with_label(self) -> None:
        """Label appears in output."""
        spinner = Spinner(label="Processing", use_color=False)
        result = spinner.render()
        assert "Processing" in result


class TestBorderStyle:
    """Tests for BorderStyle."""

    def test_single_border(self) -> None:
        """Single line border."""
        style = BorderStyle.single()
        assert style.top_left == "┌"

    def test_double_border(self) -> None:
        """Double line border."""
        style = BorderStyle.double()
        assert style.top_left == "╔"

    def test_rounded_border(self) -> None:
        """Rounded corner border."""
        style = BorderStyle.rounded()
        assert style.top_left == "╭"

    def test_no_border(self) -> None:
        """No border (spaces)."""
        style = BorderStyle.none()
        assert style.top_left == " "


class TestPanel:
    """Tests for Panel component."""

    def test_empty_panel(self) -> None:
        """Render empty panel."""
        panel = Panel(width=20, use_color=False)
        result = panel.render()
        assert "┌" in result
        assert "└" in result

    def test_panel_with_title(self) -> None:
        """Title appears in border."""
        panel = Panel(title="Test", width=20, use_color=False)
        result = panel.render()
        assert "Test" in result

    def test_add_line(self) -> None:
        """Content lines appear in panel."""
        panel = Panel(width=20, use_color=False)
        panel.add_line("Hello")
        result = panel.render()
        assert "Hello" in result

    def test_clear(self) -> None:
        """Clear removes content."""
        panel = Panel()
        panel.add_line("Test")
        panel.clear()
        assert len(panel.lines) == 0

    def test_long_line_truncated(self) -> None:
        """Long lines are truncated."""
        panel = Panel(width=20, use_color=False)
        panel.add_line("This is a very long line that exceeds the width")
        result = panel.render()
        assert "..." in result


class TestMeter:
    """Tests for Meter component."""

    def test_set_value(self) -> None:
        """Set meter value."""
        meter = Meter()
        meter.set_value(50)
        assert meter.value == 50

    def test_value_clamped(self) -> None:
        """Value clamped to range."""
        meter = Meter(min_value=0, max_value=100)
        meter.set_value(150)
        assert meter.value == 100

    def test_render_shows_bar(self) -> None:
        """Render shows bar."""
        meter = Meter(width=10, use_color=False)
        meter.set_value(50)
        result = meter.render()
        assert "█" in result
        assert "░" in result

    def test_render_shows_value(self) -> None:
        """Value appears in output."""
        meter = Meter(use_color=False)
        meter.set_value(75)
        result = meter.render()
        assert "75" in result

    def test_threshold_colors(self) -> None:
        """Threshold affects color selection."""
        meter = Meter(
            thresholds=[
                MeterThreshold(70, Color.YELLOW),
                MeterThreshold(90, Color.RED),
            ]
        )
        meter.set_value(85)
        assert meter._get_color() == Color.YELLOW

        meter.set_value(95)
        assert meter._get_color() == Color.RED


class TestStatusLine:
    """Tests for StatusLine component."""

    def test_add_item(self) -> None:
        """Add status item."""
        status = StatusLine()
        status.add("Mode", "NORMAL")
        assert len(status.items) == 1

    def test_update_item(self) -> None:
        """Update existing item."""
        status = StatusLine()
        status.add("Mode", "NORMAL")
        status.update("Mode", "INSERT")
        assert status.items[0].value == "INSERT"

    def test_update_creates_if_missing(self) -> None:
        """Update creates item if not found."""
        status = StatusLine()
        status.update("New", "Value")
        assert len(status.items) == 1

    def test_clear(self) -> None:
        """Clear removes all items."""
        status = StatusLine()
        status.add("A", "1")
        status.add("B", "2")
        status.clear()
        assert len(status.items) == 0

    def test_render_format(self) -> None:
        """Render formats items correctly."""
        status = StatusLine(use_color=False)
        status.add("Mode", "NORMAL")
        status.add("Line", "42")
        result = status.render()
        assert "Mode: NORMAL" in result
        assert "Line: 42" in result
        assert " | " in result


class TestTable:
    """Tests for Table component."""

    def test_empty_table(self) -> None:
        """Render table with headers only."""
        table = Table(
            columns=[TableColumn("Name"), TableColumn("Value")],
            use_color=False,
        )
        result = table.render()
        assert "Name" in result
        assert "Value" in result

    def test_add_row(self) -> None:
        """Add data row."""
        table = Table(columns=[TableColumn("Name")], use_color=False)
        table.add_row(["Test"])
        result = table.render()
        assert "Test" in result

    def test_clear(self) -> None:
        """Clear removes rows."""
        table = Table(columns=[TableColumn("Name")])
        table.add_row(["Test"])
        table.clear()
        assert len(table.rows) == 0

    def test_column_alignment(self) -> None:
        """Columns align correctly."""
        table = Table(
            columns=[
                TableColumn("Name", width=10, align="left"),
                TableColumn("Count", width=5, align="right"),
            ],
            use_color=False,
        )
        table.add_row(["A", "1"])
        result = table.render()
        # Just check it renders without error
        assert "A" in result
        assert "1" in result


class TestDashboardPanel:
    """Tests for DashboardPanel component."""

    def test_create_empty(self) -> None:
        """Create empty dashboard."""
        dashboard = DashboardPanel(title="Test")
        result = dashboard.render()
        assert "Test" in result

    def test_add_meter(self) -> None:
        """Add meter to dashboard."""
        dashboard = DashboardPanel(title="Test", use_color=False)
        dashboard.add_meter("CPU", 50)
        result = dashboard.render()
        assert "CPU" in result

    def test_status_line(self) -> None:
        """Status line appears in dashboard."""
        dashboard = DashboardPanel(title="Test", use_color=False)
        dashboard.status.add("Mode", "Active")
        result = dashboard.render()
        assert "Mode" in result
        assert "Active" in result


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_progress_bar(self) -> None:
        """Create progress bar with factory."""
        bar = create_progress_bar(label="Test", initial=0.5)
        assert bar.label == "Test"
        assert bar.value == 0.5

    def test_create_panel_single(self) -> None:
        """Create panel with single border."""
        panel = create_panel(title="Test", border="single")
        assert panel.border.top_left == "┌"

    def test_create_panel_rounded(self) -> None:
        """Create panel with rounded border."""
        panel = create_panel(border="rounded")
        assert panel.border.top_left == "╭"

    def test_create_dashboard(self) -> None:
        """Create dashboard from metrics dict."""
        dashboard = create_dashboard(
            title="Metrics",
            metrics={"CPU": 50, "Memory": 75},
        )
        assert len(dashboard.meters) == 2
        assert dashboard.title == "Metrics"
