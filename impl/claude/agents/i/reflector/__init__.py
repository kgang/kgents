"""
I-gent Reflector - Bridge between CLI Events and FluxApp TUI.

The FluxReflector connects the CLI's event stream to the Textual TUI,
enabling real-time visualization of runtime events in the semantic flux view.

Public API:
    FluxReflector    - Main reflector adapter for FluxApp
    create_flux_reflector  - Factory function

Example:
    from agents.i.reflector import FluxReflector, create_flux_reflector

    # Create reflector connected to FluxApp
    app = FluxApp()
    reflector = create_flux_reflector(app)

    # Events from CLI commands now appear in FluxApp
    reflector.on_event(command_start("status"))
"""

from .flux_reflector import FluxReflector, create_flux_reflector

__all__ = [
    "FluxReflector",
    "create_flux_reflector",
]
