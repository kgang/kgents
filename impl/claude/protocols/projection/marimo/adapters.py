"""
marimo Adapters: Map projection widgets to mo.ui.* components.

Each widget type maps to an appropriate marimo component:
- Text → mo.md() / mo.Html()
- Select → mo.ui.dropdown() / mo.ui.multiselect()
- Progress → mo.status.progress_bar()
- Table → mo.ui.table()
- Graph → mo.ui.plotly() / mo.ui.altair()

Note: These adapters return marimo-compatible objects.
Import marimo only when adapters are called (lazy import).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from protocols.projection.schema import (
    CacheMeta,
    ErrorInfo,
    RefusalInfo,
    WidgetEnvelope,
    WidgetMeta,
)

if TYPE_CHECKING:
    import marimo as mo


def text_to_marimo(
    content: str,
    variant: str = "plain",
    highlight: str | None = None,
) -> Any:
    """
    Convert text widget to marimo component.

    Args:
        content: Text content.
        variant: plain, code, heading, quote, markdown.
        highlight: Optional regex pattern to highlight.

    Returns:
        marimo.md() or marimo.Html() component.
    """
    import marimo as mo

    match variant:
        case "code":
            return mo.md(f"```\n{content}\n```")
        case "heading":
            return mo.md(f"# {content}")
        case "quote":
            return mo.md(f"> {content}")
        case "markdown":
            return mo.md(content)
        case "plain" | _:
            if highlight:
                import re

                highlighted = re.sub(
                    f"({highlight})",
                    r"**\1**",
                    content,
                    flags=re.IGNORECASE,
                )
                return mo.md(highlighted)
            return mo.md(content)


def select_to_marimo(
    options: list[dict[str, str]],
    value: str | list[str] | None = None,
    multiple: bool = False,
    searchable: bool = False,
    label: str | None = None,
) -> Any:
    """
    Convert select widget to marimo dropdown/multiselect.

    Args:
        options: List of {"value": str, "label": str} options.
        value: Currently selected value(s).
        multiple: Allow multiple selection.
        searchable: Enable search (not all marimo versions support).
        label: Optional label.

    Returns:
        marimo.ui.dropdown() or marimo.ui.multiselect().
    """
    import marimo as mo

    # Convert options to marimo format {label: value}
    option_dict = {opt["label"]: opt["value"] for opt in options}

    if multiple:
        return mo.ui.multiselect(
            options=option_dict,
            value=value if isinstance(value, list) else ([value] if value else []),
            label=label or "",
        )
    return mo.ui.dropdown(
        options=option_dict,
        value=value if isinstance(value, str) else None,
        label=label or "",
    )


def progress_to_marimo(
    value: int = 0,
    label: str | None = None,
    indeterminate: bool = False,
) -> Any:
    """
    Convert progress widget to marimo progress bar.

    Args:
        value: Progress value 0-100.
        label: Optional label.
        indeterminate: Show indeterminate progress.

    Returns:
        marimo.status.progress_bar().
    """
    import marimo as mo

    # marimo.status.progress_bar expects 0-1 range
    normalized = max(0, min(100, value or 0)) / 100

    # progress_bar has different signatures - use spinner for indeterminate
    if indeterminate:
        return mo.status.spinner(title=label)

    # Return simple progress display as HTML
    return mo.md(f"**{label or 'Progress'}**: {int(normalized * 100)}%")


def table_to_marimo(
    columns: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    page_size: int = 10,
    selectable: bool = False,
) -> Any:
    """
    Convert table widget to marimo table.

    Args:
        columns: Column definitions with key, label.
        rows: Row data as list of dicts.
        page_size: Rows per page.
        selectable: Enable row selection.

    Returns:
        marimo.ui.table().
    """
    import marimo as mo

    # Rename columns to labels
    display_rows = []
    column_map = {col["key"]: col.get("label", col["key"]) for col in columns}

    for row in rows:
        display_row = {column_map.get(k, k): v for k, v in row.items()}
        display_rows.append(display_row)

    return mo.ui.table(
        data=display_rows,
        selection="multi" if selectable else None,
        page_size=page_size,
    )


def graph_to_marimo(
    graph_type: str,
    labels: list[str],
    datasets: list[dict[str, Any]],
    title: str | None = None,
    stacked: bool = False,
) -> Any:
    """
    Convert graph widget to marimo chart.

    Uses plotly via mo.ui.plotly() for interactive charts.

    Args:
        graph_type: line, bar, pie, doughnut, radar.
        labels: X-axis labels.
        datasets: List of {label, data, ...} datasets.
        title: Chart title.
        stacked: Stack bars/areas.

    Returns:
        marimo.ui.plotly() component.
    """
    import marimo as mo

    try:
        import plotly.graph_objects as go
    except ImportError:
        # Fallback to text representation
        return mo.md(
            f"**{title or 'Chart'}**\n\n"
            f"Type: {graph_type}\n"
            f"Labels: {', '.join(labels)}\n"
            f"Datasets: {len(datasets)}"
        )

    fig = go.Figure()

    for ds in datasets:
        match graph_type:
            case "line":
                fig.add_trace(
                    go.Scatter(
                        x=labels,
                        y=ds["data"],
                        name=ds.get("label", ""),
                        mode="lines+markers",
                    )
                )
            case "bar":
                fig.add_trace(
                    go.Bar(
                        x=labels,
                        y=ds["data"],
                        name=ds.get("label", ""),
                    )
                )
            case "pie" | "doughnut":
                fig.add_trace(
                    go.Pie(
                        labels=labels,
                        values=ds["data"],
                        hole=0.4 if graph_type == "doughnut" else 0,
                    )
                )
            case "radar":
                fig.add_trace(
                    go.Scatterpolar(
                        r=ds["data"],
                        theta=labels,
                        fill="toself",
                        name=ds.get("label", ""),
                    )
                )
            case _:
                fig.add_trace(
                    go.Scatter(
                        x=labels,
                        y=ds["data"],
                        name=ds.get("label", ""),
                    )
                )

    if title:
        fig.update_layout(title=title)

    if stacked and graph_type == "bar":
        fig.update_layout(barmode="stack")

    return mo.ui.plotly(fig)


def error_to_marimo(error: ErrorInfo) -> Any:
    """
    Convert error info to marimo callout.

    Args:
        error: Error information.

    Returns:
        marimo.callout() with error styling.
    """
    import marimo as mo

    emoji_map = {
        "network": "📡",
        "notFound": "🔍",
        "permission": "🔐",
        "timeout": "⏱️",
        "validation": "❌",
        "unknown": "⚠️",
    }

    emoji = emoji_map.get(error.category, "⚠️")

    content = f"""
{emoji} **{error.message}**

Code: `{error.code}`
"""

    if error.trace_id:
        content += f"\nTrace: `{error.trace_id}`"

    if error.retry_after_seconds:
        content += f"\n\n*Retry in {error.retry_after_seconds}s...*"

    if error.fallback_action:
        content += f"\n\n💡 {error.fallback_action}"

    return mo.callout(mo.md(content), kind="danger")


def refusal_to_marimo(refusal: RefusalInfo) -> Any:
    """
    Convert refusal info to marimo callout.

    Args:
        refusal: Refusal information.

    Returns:
        marimo.callout() with refusal styling.
    """
    import marimo as mo

    content = f"""
🛑 **Action Refused**

{refusal.reason}
"""

    if refusal.consent_required:
        content += f"\n**Requires:** {refusal.consent_required}"

    if refusal.appeal_to:
        content += f"\n\n*Appeal path:* `{refusal.appeal_to}`"

    if refusal.override_cost is not None:
        content += f"\n*Override cost:* {refusal.override_cost} tokens"

    return mo.callout(mo.md(content), kind="warn")


def cached_badge_to_marimo(cache: CacheMeta) -> Any:
    """
    Convert cache metadata to marimo badge.

    Args:
        cache: Cache metadata.

    Returns:
        marimo.md() with badge styling.
    """
    from datetime import datetime, timezone

    import marimo as mo

    age = ""
    if cache.cached_at:
        now = datetime.now(timezone.utc)
        diff = now - cache.cached_at
        seconds = int(diff.total_seconds())

        if seconds < 60:
            age = f"{seconds}s ago"
        elif seconds < 3600:
            age = f"{seconds // 60}m ago"
        elif seconds < 86400:
            age = f"{seconds // 3600}h ago"
        else:
            age = f"{seconds // 86400}d ago"

    badge_text = f"⚡ **[CACHED{f' {age}' if age else ''}]**"

    return mo.md(badge_text)


class MarimoAdapter:
    """
    Unified adapter for converting projection widgets to marimo components.

    Provides a single interface for all widget conversions.
    """

    @staticmethod
    def adapt(envelope: "WidgetEnvelope[Any]", widget_type: str) -> Any:
        """
        Adapt a widget envelope to marimo component.

        Args:
            envelope: Widget envelope with data and metadata.
            widget_type: Type of widget (text, select, table, etc.).

        Returns:
            marimo component.
        """
        import marimo as mo

        meta = envelope.meta
        result = []

        # Add cache badge if cached
        if meta.cache and meta.cache.is_cached:
            result.append(cached_badge_to_marimo(meta.cache))

        # Check for error/refusal states
        if meta.error:
            result.append(error_to_marimo(meta.error))
            return mo.vstack(result)

        if meta.refusal:
            result.append(refusal_to_marimo(meta.refusal))
            return mo.vstack(result)

        # Adapt main content
        data = envelope.data
        match widget_type:
            case "text":
                result.append(
                    text_to_marimo(
                        content=data.get("content", ""),
                        variant=data.get("variant", "plain"),
                        highlight=data.get("highlight"),
                    )
                )
            case "select":
                result.append(
                    select_to_marimo(
                        options=data.get("options", []),
                        value=data.get("value"),
                        multiple=data.get("multiple", False),
                        label=data.get("label"),
                    )
                )
            case "progress":
                result.append(
                    progress_to_marimo(
                        value=data.get("value", 0),
                        label=data.get("label"),
                        indeterminate=data.get("indeterminate", False),
                    )
                )
            case "table":
                result.append(
                    table_to_marimo(
                        columns=data.get("columns", []),
                        rows=data.get("rows", []),
                        page_size=data.get("pageSize", 10),
                        selectable=data.get("selectable", False),
                    )
                )
            case "graph":
                result.append(
                    graph_to_marimo(
                        graph_type=data.get("type", "line"),
                        labels=data.get("labels", []),
                        datasets=data.get("datasets", []),
                        title=data.get("title"),
                        stacked=data.get("stacked", False),
                    )
                )
            case _:
                result.append(mo.md(f"Unknown widget type: {widget_type}"))

        return mo.vstack(result) if len(result) > 1 else result[0]


def adapt_to_marimo(envelope: "WidgetEnvelope[Any]", widget_type: str) -> Any:
    """
    Convenience function for adapting envelope to marimo.

    Args:
        envelope: Widget envelope.
        widget_type: Widget type string.

    Returns:
        marimo component.
    """
    return MarimoAdapter.adapt(envelope, widget_type)
