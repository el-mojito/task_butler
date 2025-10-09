"""Task Butler integration following Home Maintenance structure."""

from __future__ import annotations

import logging
import os
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import websocket_api
from homeassistant.components.http import StaticPathConfig
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_MARK_COMPLETE,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_TASK,
    SERVICE_UPDATE_TASK,
    PANEL_URL,
    PANEL_TITLE,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_API_PATH,
    SCHEDULE_MODES,
    INTERVAL_MODES,
)
from .coordinator import TaskButlerCoordinator

from .panel import (
    async_register_panel,
    async_unregister_panel,
)

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
    # Initialize coordinator
    coordinator = TaskButlerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = coordinator

    # Register WebSocket commands
    websocket_api.async_register_command(hass, ws_get_tasks)
    websocket_api.async_register_command(hass, ws_create_task)
    websocket_api.async_register_command(hass, ws_mark_complete)
    websocket_api.async_register_command(hass, ws_delete_task)
    websocket_api.async_register_command(hass, ws_update_task)

    # Setup frontend panel (following Home Maintenance pattern)
    await async_register_panel(hass)

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await _async_register_services(hass, coordinator)

    return True


async def _async_register_services(
    hass: HomeAssistant, coordinator: TaskButlerCoordinator
) -> None:
    """Register Task Butler services."""

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

    # Register all services
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


# WebSocket API Commands
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/get_tasks",
    }
)
@websocket_api.async_response
async def ws_get_tasks(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Handle get tasks WebSocket command."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]
    connection.send_result(
        msg["id"],
        {
            "tasks": list(coordinator.tasks.values()),
            "date_format": coordinator.date_format,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/create_task",
        vol.Required("task_data"): dict,
    }
)
@websocket_api.async_response
async def ws_create_task(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Handle create task WebSocket command."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]
    try:
        task_id = await coordinator.create_task(msg["task_data"])
        connection.send_result(msg["id"], {"task_id": task_id, "success": True})
    except Exception as err:
        connection.send_error(msg["id"], "create_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/mark_complete",
        vol.Required("task_id"): str,
    }
)
@websocket_api.async_response
async def ws_mark_complete(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Handle mark task complete WebSocket command."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]
    try:
        await coordinator.mark_task_complete(msg["task_id"])
        connection.send_result(msg["id"], {"success": True})
    except Exception as err:
        connection.send_error(msg["id"], "mark_complete_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/delete_task",
        vol.Required("task_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_task(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Handle delete task WebSocket command."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]
    try:
        await coordinator.delete_task(msg["task_id"])
        connection.send_result(msg["id"], {"success": True})
    except Exception as err:
        connection.send_error(msg["id"], "delete_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/update_task",
        vol.Required("task_id"): str,
        vol.Required("updates"): dict,
    }
)
@websocket_api.async_response
async def ws_update_task(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Handle update task WebSocket command."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]
    try:
        await coordinator.update_task(msg["task_id"], msg["updates"])
        connection.send_result(msg["id"], {"success": True})
    except Exception as err:
        connection.send_error(msg["id"], "update_failed", str(err))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.pop(DOMAIN)

        # Remove services
        hass.services.async_remove(DOMAIN, SERVICE_MARK_COMPLETE)
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_TASK)
        hass.services.async_remove(DOMAIN, SERVICE_DELETE_TASK)
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_TASK)

    async_unregister_panel(hass)

    return unload_ok
