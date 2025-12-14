"""Minimal anywidget test for marimo."""

import marimo

app = marimo.App()


@app.cell
def __():
    import anywidget
    import marimo as mo
    import traitlets

    class SimpleWidget(anywidget.AnyWidget):
        _esm = """
        export function render({ model, el }) {
            el.innerHTML = '<div style="padding: 20px; background: #1a1a2e; color: #e0e0e0; border-radius: 4px;">Hello from anywidget!</div>';
        }
        """
        value = traitlets.Unicode("test").tag(sync=True)

    _raw_widget = SimpleWidget()
    # Wrap with mo.ui.anywidget for proper marimo integration
    widget = mo.ui.anywidget(_raw_widget)
    widget
    return mo, anywidget, traitlets, SimpleWidget, widget


if __name__ == "__main__":
    app.run()
