"""Task Butler integration."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    INTERVAL_MODES,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL,
    PLATFORMS,
    SCHEDULE_MODES,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_TASK,
    SERVICE_MARK_COMPLETE,
    SERVICE_UPDATE_TASK,
)
from .coordinator import TaskButlerCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Service schemas
MARK_COMPLETE_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

CREATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("schedule_mode"): vol.In(SCHEDULE_MODES),
        vol.Optional("interval_days", default=30): cv.positive_int,
        vol.Optional("interval_mode", default="hard_fixed"): vol.In(INTERVAL_MODES),
        vol.Optional("fixed_date"): cv.string,
        vol.Optional("fixed_occurrence"): cv.string,
        vol.Optional("enabled", default=True): cv.boolean,
    }
)

DELETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

UPDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("schedule_mode"): vol.In(SCHEDULE_MODES),
        vol.Optional("interval_days"): cv.positive_int,
        vol.Optional("interval_mode"): vol.In(INTERVAL_MODES),
        vol.Optional("fixed_date"): cv.string,
        vol.Optional("fixed_occurrence"): cv.string,
        vol.Optional("enabled"): cv.boolean,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Task Butler component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Task Butler from a config entry."""
    coordinator = TaskButlerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = coordinator

    # Register the frontend panel
    hass.http.register_static_path(
        "/local/task_butler",
        hass.config.path("custom_components/task_butler/frontend"),
        cache_headers=False,
    )

    await hass.async_add_executor_job(
        hass.components.frontend.async_register_built_in_panel,
        "custom",
        PANEL_TITLE,
        PANEL_ICON,
        PANEL_URL,
        {"module_url": "/local/task_butler/task_butler_panel.js"},
    )

    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_mark_complete(call: ServiceCall) -> None:
        """Handle mark task complete service call."""
        task_id = call.data["task_id"]
        await coordinator.mark_task_complete(task_id)

    async def handle_create_task(call: ServiceCall) -> None:
        """Handle create task service call."""
        await coordinator.create_task(call.data)

    async def handle_delete_task(call: ServiceCall) -> None:
        """Handle delete task service call."""
        task_id = call.data["task_id"]
        await coordinator.delete_task(task_id)

    async def handle_update_task(call: ServiceCall) -> None:
        """Handle update task service call."""
        task_id = call.data["task_id"]
        updates = {k: v for k, v in call.data.items() if k != "task_id"}
        await coordinator.update_task(task_id, updates)

    hass.services.async_register(
        DOMAIN, SERVICE_MARK_COMPLETE, handle_mark_complete, schema=MARK_COMPLETE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_TASK, handle_create_task, schema=CREATE_TASK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_TASK, handle_delete_task, schema=DELETE_TASK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_TASK, handle_update_task, schema=UPDATE_TASK_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.pop(DOMAIN)
        hass.services.async_remove(DOMAIN, SERVICE_MARK_COMPLETE)
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_TASK)
        hass.services.async_remove(DOMAIN, SERVICE_DELETE_TASK)
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_TASK)

    return unload_ok
