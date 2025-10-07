"""Sensor platform for Task Butler."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Butler sensors."""
    # TODO: Create sensor entities based on config entry
    entities = []

    # Example sensors
    entities.extend(
        [
            TaskDaysRemainingSensor(config_entry),
            TaskLastCompletedSensor(config_entry),
        ]
    )

    async_add_entities(entities)


class TaskDaysRemainingSensor(SensorEntity):
    """Sensor showing days remaining until task is due."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        task_name = config_entry.data.get("task_name", "Task")
        self._attr_name = f"{task_name} Days Remaining"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_days_remaining"
        self._attr_native_unit_of_measurement = "days"
        self._attr_state_class = "measurement"

    @property
    def native_value(self) -> int | None:
        """Return the days remaining."""
        # TODO: Implement days remaining calculation
        return None

    async def async_update(self) -> None:
        """Update the sensor."""
        # TODO: Implement update logic
        pass


class TaskLastCompletedSensor(SensorEntity):
    """Sensor showing when task was last completed."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        task_name = config_entry.data.get("task_name", "Task")
        self._attr_name = f"{task_name} Last Completed"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_last_completed"
        self._attr_device_class = "timestamp"

    @property
    def native_value(self) -> str | None:
        """Return the last completed timestamp."""
        # TODO: Implement last completed logic
        return None

    async def async_update(self) -> None:
        """Update the sensor."""
        # TODO: Implement update logic
        pass
