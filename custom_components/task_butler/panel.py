"""Custom panel for Task Butler."""

import logging
import os

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PANEL_URL,
    PANEL_TITLE,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_API_PATH,
    PANEL_API_URL,
)

_LOGGER = logging.getLogger(__name__)


async def async_register_panel(hass: HomeAssistant) -> None:
    """Set up the Task Butler panel."""
    try:
        # Register static files
        integration_dir = os.path.dirname(__file__)
        frontend_dir = os.path.join(integration_dir, "frontend", "dist")

        if not hass.data.setdefault("task_butler_static_path_registered", False):
            await hass.http.async_register_static_paths(
                [StaticPathConfig(PANEL_API_PATH, frontend_dir, cache_headers=False)]
            )
            hass.data["task_butler_static_path_registered"] = True

        # Register the panel
        await panel_custom.async_register_panel(
            hass,
            webcomponent_name=PANEL_NAME,
            frontend_url_path=PANEL_URL,
            module_url=PANEL_API_URL,
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            require_admin=False,
            config={},
            # config={"module_url": f"/local/{DOMAIN}/task-butler-panel.js"},
        )

        _LOGGER.info("Task Butler panel registered successfully")

    except Exception as err:
        _LOGGER.error("Failed to register Task Butler panel: %s", err)
        # Continue without panel - core functionality still works


async def async_register_panel_x(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register custom panel for Task Butler."""
    static_path = os.path.join(os.path.dirname(__file__), "panel", "dist")  # noqa: PTH118, PTH120

    # Register static path only once, since it cannot be removed on unload
    if not hass.data.setdefault("task_butler_static_path_registered", False):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_API_PATH, static_path, cache_headers=False)]
        )
        hass.data["task_butler_static_path_registered"] = True

    admin_only = entry.options.get("admin_only", entry.data.get("admin_only", True))
    sidebar_title = entry.options.get(
        "sidebar_title", entry.data.get("sidebar_title", PANEL_TITLE)
    )

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=PANEL_URL,
        module_url=PANEL_API_URL,
        sidebar_title=sidebar_title,
        sidebar_icon=PANEL_ICON,
        require_admin=admin_only,
        config={},
    )


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove custom panel for Task Butler."""
    frontend.async_remove_panel(hass, PANEL_URL)
    _LOGGER.debug("Removing panel")
