"""Central CSS definitions for zen-agents design system."""

from .themes import (
    Theme,
    ThemeName,
    THEMES,
    DEFAULT_THEME,
    get_theme,
    get_theme_names,
)

# Modal base styles
MODAL_CSS = """
.modal-base {
    align: center middle;
}

.modal-base #dialog {
    height: auto;
    max-height: 90%;
    padding: 1 2;
    background: $surface;
    border: round $surface-lighten-1;
    overflow-y: auto;
}

.modal-sm #dialog {
    width: 50vw;
    min-width: 40;
    max-width: 50;
}

.modal-md #dialog {
    width: 60vw;
    min-width: 50;
    max-width: 65;
}

.modal-left {
    align: left middle;
}

.modal-left #dialog {
    margin-left: 2;
}
"""

# Container system
CONTAINER_CSS = """
.elastic {
    height: auto;
    min-height: 0;
}

.hidden {
    display: none;
}
"""

# Common UI patterns
COMMON_CSS = """
.dialog-title {
    text-align: center;
    width: 100%;
    margin-bottom: 1;
    color: $text-muted;
}

.field-label {
    margin-top: 1;
    color: $text-disabled;
}

.dialog-hint {
    text-align: center;
    color: $text-disabled;
    margin-top: 1;
}

.list-container {
    height: auto;
    padding: 0;
    overflow-y: auto;
}

.list-sm {
    max-height: 20vh;
    min-height: 5;
}

.list-md {
    max-height: 30vh;
    min-height: 8;
}

.list-row {
    height: 1;
    padding: 0 1;
}

.list-row:hover {
    background: $surface-lighten-1;
}

.list-row.selected {
    background: $surface-lighten-1;
}

.empty-list {
    color: $text-disabled;
    padding: 2;
    text-align: center;
}
"""

# Notification styles
NOTIFICATION_CSS = """
ZenNotificationRack {
    height: auto;
    width: 100%;
    align-horizontal: left;
}

ZenNotification {
    width: auto;
    height: 3;
    padding: 0 2;
    margin-left: 2;
    content-align: center middle;
    text-align: center;
    background: $surface;
    border: round $surface-lighten-1;
    color: $text-muted;
}

ZenNotification.-success {
    border: round $surface-lighten-1;
    color: $text-muted;
}

ZenNotification.-warning {
    border: round $warning-darken-2;
    color: $warning;
}

ZenNotification.-error {
    border: round $error-darken-2;
    color: $error;
}

ZenNotification {
    opacity: 1;
}

ZenNotification.-dismissing {
    opacity: 0;
}
"""

# Flat buttons
FLAT_BUTTON_CSS = """
Button.flat {
    background: transparent;
    border: none;
    color: $text-muted;
}

Button.flat:hover {
    background: $surface-lighten-1;
    color: $text;
}

Button.flat:focus {
    background: $surface-lighten-1;
    color: $text;
}
"""

# Combined base CSS
BASE_CSS = MODAL_CSS + CONTAINER_CSS + COMMON_CSS + NOTIFICATION_CSS + FLAT_BUTTON_CSS

__all__ = [
    "BASE_CSS",
    "Theme",
    "ThemeName",
    "THEMES",
    "DEFAULT_THEME",
    "get_theme",
    "get_theme_names",
]
