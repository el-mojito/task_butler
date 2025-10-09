"""Binary sensor platform for Task Butler."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TaskButlerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Butler binary sensor based on a config entry."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]

    @coordinator.async_add_listener
    def _add_entities():
        """Add entities when tasks are created."""
        entities = []
        for task_id in coordinator.tasks:
            entities.append(TaskDueBinarySensor(coordinator, task_id))
        if entities:
            async_add_entities(entities, True)

    # Add initial entities
    _add_entities()


class TaskDueBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for task due status."""

    def __init__(self, coordinator: TaskButlerCoordinator, task_id: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def task_data(self) -> dict[str, Any]:
        """Get task data from coordinator."""
        return self.coordinator.tasks.get(self.task_id, {})

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task_name = self.task_data.get("name", "Unknown Task")
        return f"{task_name} Due"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{DOMAIN}_{self.task_id}_due"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.task_data.get("is_due", False)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.task_id in self.coordinator.tasks

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        task = self.task_data
        attributes = {
            "task_id": self.task_id,
            "schedule_mode": task.get("schedule_mode"),
            "enabled": task.get("enabled", True),
        }

        if task.get("next_due"):
            next_due = task["next_due"]
            if isinstance(next_due, str):
                from datetime import datetime

                next_due = datetime.fromisoformat(next_due)
            attributes["next_due"] = self.coordinator.format_date(next_due)

        if task.get("last_completed"):
            last_completed = task["last_completed"]
            if isinstance(last_completed, str):
                from datetime import datetime

                last_completed = datetime.fromisoformat(last_completed)
            attributes["last_completed"] = self.coordinator.format_date(last_completed)

        return attributes
