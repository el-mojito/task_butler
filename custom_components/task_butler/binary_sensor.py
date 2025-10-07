"""Binary sensor platform for Task Butler."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Butler binary sensors."""
    # TODO: Create binary sensor entities based on config entry
    entities = []

    # Example: Create a single binary sensor for now
    entities.append(TaskDueBinarySensor(config_entry))

    async_add_entities(entities)


class TaskDueBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if a task is due."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data.get('task_name', 'Task')} Due"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_due"
        self._attr_device_class = "problem"

    @property
    def is_on(self) -> bool:
        """Return true if the task is due."""
        # TODO: Implement task due logic
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        # TODO: Add relevant attributes like next_due_date, days_overdue, etc.
        return {}

    async def async_update(self) -> None:
        """Update the sensor."""
        # TODO: Implement update logic
        pass
