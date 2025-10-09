"""Switch platform for Task Butler."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Butler switches."""
    # TODO: Create switch entities based on config entry
    entities = []

    # Example: Task enable/disable switch
    entities.append(TaskEnabledSwitch(config_entry))

    async_add_entities(entities)


class TaskEnabledSwitch(SwitchEntity):
    """Switch to enable/disable a task."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        task_name = config_entry.data.get("task_name", "Task")
        self._attr_name = f"{task_name} Enabled"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_enabled"
        self._is_on = config_entry.data.get("enabled", True)

    @property
    def is_on(self) -> bool:
        """Return true if the task is enabled."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        # TODO: Implement enable logic
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        # TODO: Implement disable logic
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the switch."""
        # TODO: Implement update logic
