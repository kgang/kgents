"""
WASM Survivors Game Adapter

Playwright-based adapter for WASM Survivors (Vampire Survivors-like game).
Each adapter instance runs in its own isolated browser context.

Communication:
- Debug API: JavaScript bridge for game state
- Screen capture: For visual perception
- Input simulation: Keyboard/mouse events

Time Scaling:
- Uses game's time scale setting for fast-forward
- 4x scale allows 4 minutes of game time in 1 minute wall time
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page  # type: ignore[import-not-found]

logger = logging.getLogger("kgents.playthrough.adapters.wasm_survivors")

# Game URL (can be localhost or deployed)
DEFAULT_GAME_URL = "http://localhost:8080"


@dataclass
class GameConfig:
    """Configuration for WASM Survivors game."""

    url: str = DEFAULT_GAME_URL
    time_scale: float = 1.0
    debug_mode: bool = True
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720


class WasmSurvivorsAdapter:
    """
    Playwright adapter for WASM Survivors game.

    Implements the GameAdapter protocol for use with PlaythroughFarm.

    Architecture:
        Browser Context (isolated)
        └── Page
            └── Game Canvas
                ├── Debug API (JS bridge)
                ├── Screen Capture
                └── Input Events

    Thread Safety:
        Each adapter instance has its own browser context,
        so multiple adapters can run in parallel safely.
    """

    def __init__(
        self,
        context: "BrowserContext",
        page: "Page",
        config: GameConfig,
    ):
        """
        Initialize adapter with browser context and page.

        Use WasmSurvivorsFactory.create_context() to create instances.
        """
        self._context = context
        self._page = page
        self._config = config
        self._is_running = False
        self._last_state: dict[str, Any] = {}

    async def capture_screen(self) -> bytes:
        """
        Capture current game screen.

        Returns PNG bytes of the canvas element.
        """
        try:
            # Get canvas element
            canvas = await self._page.query_selector("canvas")
            if canvas:
                screenshot: bytes = await canvas.screenshot(type="png")
                return screenshot
            else:
                # Fallback to full page
                screenshot = await self._page.screenshot(type="png")
                return screenshot
        except Exception as e:
            logger.warning(f"Screen capture failed: {e}")
            return b""

    async def get_debug_state(self) -> dict[str, Any]:
        """
        Get game state via JavaScript bridge.

        The game exposes a debug API at window.gameDebug that provides:
        - Player state (position, health, upgrades)
        - Enemy positions and states
        - Projectile data
        - Wave information
        - Available upgrades
        """
        try:
            state = await self._page.evaluate("""
                () => {
                    if (window.gameDebug && typeof window.gameDebug.getState === 'function') {
                        return window.gameDebug.getState();
                    }
                    return null;
                }
            """)

            if state:
                self._last_state = dict(state)
                return self._last_state
            else:
                # Return cached state if debug API unavailable
                return self._last_state

        except Exception as e:
            logger.warning(f"Debug state fetch failed: {e}")
            return self._last_state

    async def get_audio_cues(self) -> list[dict[str, Any]]:
        """
        Get recent audio cues from the game.

        Audio cues can signal events before they're visible:
        - Telegraph sounds (enemy attacks)
        - Damage sounds
        - Pickup/upgrade sounds
        """
        try:
            cues = await self._page.evaluate("""
                () => {
                    if (window.gameDebug && typeof window.gameDebug.getAudioCues === 'function') {
                        return window.gameDebug.getAudioCues();
                    }
                    return [];
                }
            """)
            return cues or []

        except Exception as e:
            logger.warning(f"Audio cues fetch failed: {e}")
            return []

    async def send_action(self, action: Any) -> None:
        """
        Send action to game via input simulation.

        Actions are translated to keyboard/mouse events:
        - move: Arrow keys or WASD
        - attack: Left click or space
        - select_upgrade: Number keys 1-3
        - ability: Q, E, R keys
        """
        if not hasattr(action, "type"):
            return

        try:
            match action.type:
                case "move":
                    await self._send_move(action)
                case "attack":
                    await self._send_attack(action)
                case "select_upgrade":
                    await self._send_upgrade_selection(action)
                case "ability":
                    await self._send_ability(action)
                case "retreat":
                    await self._send_retreat()
                case "none":
                    pass  # No action

        except Exception as e:
            logger.warning(f"Action send failed: {e}")

    async def _send_move(self, action: Any) -> None:
        """Send movement input."""
        if not action.direction:
            return

        dx, dy = action.direction

        # Release all movement keys first
        for key in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]:
            await self._page.keyboard.up(key)

        # Press appropriate keys based on direction
        if dy < -0.3:
            await self._page.keyboard.down("ArrowUp")
        elif dy > 0.3:
            await self._page.keyboard.down("ArrowDown")

        if dx < -0.3:
            await self._page.keyboard.down("ArrowLeft")
        elif dx > 0.3:
            await self._page.keyboard.down("ArrowRight")

    async def _send_attack(self, action: Any) -> None:
        """Send attack input (usually automatic in Survivors-like games)."""
        # Most Survivors-like games auto-attack, but we can trigger manual abilities
        await self._page.keyboard.press("Space")

    async def _send_upgrade_selection(self, action: Any) -> None:
        """Send upgrade selection input."""
        upgrade_name = action.parameters.get("upgrade", "")

        # Try to find and click the upgrade button
        # This assumes upgrades are shown as clickable elements
        try:
            # First try clicking by text content
            selector = f"button:has-text('{upgrade_name}')"
            button = await self._page.query_selector(selector)
            if button:
                await button.click()
                return

            # Fallback to number keys (1, 2, 3 for first three options)
            # Get current upgrades and find index
            state = await self.get_debug_state()
            upgrades = state.get("upgrades", [])

            for i, upgrade in enumerate(upgrades):
                if upgrade.get("name", "").lower() == upgrade_name.lower():
                    # Press corresponding number key (1-indexed)
                    await self._page.keyboard.press(str(i + 1))
                    return

            # Last resort: press 1 for first option
            await self._page.keyboard.press("1")

        except Exception as e:
            logger.warning(f"Upgrade selection failed: {e}")

    async def _send_ability(self, action: Any) -> None:
        """Send ability activation."""
        ability = action.parameters.get("ability", "")
        ability_keys = {"q": "q", "e": "e", "r": "r", "ultimate": "r"}

        key = ability_keys.get(ability.lower(), "q")
        await self._page.keyboard.press(key)

    async def _send_retreat(self) -> None:
        """Send retreat movement (move away from enemies)."""
        state = await self.get_debug_state()
        enemies = state.get("enemies", [])
        player = state.get("player", {}).get("position", {"x": 400, "y": 300})

        if not enemies:
            return

        # Calculate centroid of enemies
        enemy_x = sum(e.get("position", {}).get("x", 0) for e in enemies) / len(enemies)
        enemy_y = sum(e.get("position", {}).get("y", 0) for e in enemies) / len(enemies)

        # Move away from centroid
        dx = player.get("x", 0) - enemy_x
        dy = player.get("y", 0) - enemy_y

        # Normalize
        dist = (dx**2 + dy**2) ** 0.5
        if dist > 0:
            dx /= dist
            dy /= dist

        from ..agent import Action

        await self._send_move(Action.move((dx, dy)))

    async def start_game(self) -> None:
        """
        Initialize and start the game.

        Steps:
        1. Navigate to game URL
        2. Wait for game to load
        3. Set time scale
        4. Enable debug mode
        5. Start new game
        """
        logger.info(f"Starting game at {self._config.url}")

        # Navigate to game
        await self._page.goto(self._config.url)

        # Wait for game canvas to be ready
        await self._page.wait_for_selector("canvas", timeout=30000)

        # Wait a bit for game to initialize
        await asyncio.sleep(1)

        # Enable debug mode if available
        if self._config.debug_mode:
            await self._page.evaluate("""
                () => {
                    if (window.gameDebug && typeof window.gameDebug.enable === 'function') {
                        window.gameDebug.enable();
                    }
                }
            """)

        # Set time scale
        if self._config.time_scale != 1.0:
            await self._page.evaluate(f"""
                () => {{
                    if (window.gameDebug && typeof window.gameDebug.setTimeScale === 'function') {{
                        window.gameDebug.setTimeScale({self._config.time_scale});
                    }}
                }}
            """)

        # Try to start a new game (click start button if present)
        try:
            start_button = await self._page.query_selector(
                "button:has-text('Start'), button:has-text('Play'), #start-button"
            )
            if start_button:
                await start_button.click()
                await asyncio.sleep(0.5)
        except Exception:
            pass  # Game might auto-start

        self._is_running = True
        logger.info("Game started successfully")

    async def close(self) -> None:
        """Clean up resources."""
        self._is_running = False

        try:
            # Release all keys
            for key in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"]:
                await self._page.keyboard.up(key)
        except Exception:
            pass

        try:
            await self._context.close()
        except Exception as e:
            logger.warning(f"Context close failed: {e}")


class WasmSurvivorsFactory:
    """
    Factory for creating isolated WASM Survivors game adapters.

    Each adapter runs in its own browser context for isolation.
    Uses Playwright for browser automation.

    Usage:
        async with WasmSurvivorsFactory() as factory:
            adapter = await factory.create_context(time_scale=4.0)
            # Use adapter...
            await adapter.close()
    """

    def __init__(
        self,
        browser: "Browser | None" = None,
        game_url: str = DEFAULT_GAME_URL,
        headless: bool = True,
    ):
        """
        Initialize factory.

        Args:
            browser: Existing Playwright browser instance, or None to create one
            game_url: URL of the WASM Survivors game
            headless: Whether to run browser headlessly
        """
        self._browser = browser
        self._owns_browser = browser is None
        self._game_url = game_url
        self._headless = headless
        self._playwright: Any = None

    async def __aenter__(self) -> "WasmSurvivorsFactory":
        """Async context manager entry."""
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self._headless)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._owns_browser and self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def create_context(
        self,
        time_scale: float = 1.0,
    ) -> WasmSurvivorsAdapter:
        """
        Create a new isolated game context.

        Each context has its own browser context and page,
        allowing multiple games to run in parallel without
        state pollution.

        Args:
            time_scale: Game speed multiplier (e.g., 4.0 = 4x speed)

        Returns:
            WasmSurvivorsAdapter with isolated browser context
        """
        if self._browser is None:
            raise RuntimeError(
                "Factory not initialized. Use 'async with WasmSurvivorsFactory()' context manager."
            )

        config = GameConfig(
            url=self._game_url,
            time_scale=time_scale,
            headless=self._headless,
        )

        # Create isolated browser context
        context = await self._browser.new_context(
            viewport={"width": config.viewport_width, "height": config.viewport_height},
            # Disable features that could interfere
            ignore_https_errors=True,
            java_script_enabled=True,
        )

        # Create page in context
        page = await context.new_page()

        return WasmSurvivorsAdapter(
            context=context,
            page=page,
            config=config,
        )
