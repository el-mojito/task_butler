"""Sensor platform for Task Butler."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
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
    """Set up Task Butler sensors based on a config entry."""
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN]

    @coordinator.async_add_listener
    def _add_entities():
        """Add entities when tasks are created."""
        entities = []
        for task_id in coordinator.tasks:
            entities.extend(
                [
                    TaskNextDueSensor(coordinator, task_id),
                    TaskLastCompletedSensor(coordinator, task_id),
                ]
            )
        if entities:
            async_add_entities(entities, True)

    # Add initial entities
    _add_entities()


class TaskNextDueSensor(CoordinatorEntity, SensorEntity):
    """Sensor for task next due date."""

    def __init__(self, coordinator: TaskButlerCoordinator, task_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.task_id = task_id

    @property
    def task_data(self) -> dict[str, Any]:
        """Get task data from coordinator."""
        return self.coordinator.tasks.get(self.task_id, {})

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task_name = self.task_data.get("name", "Unknown Task")
        return f"{task_name} Next Due"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{DOMAIN}_{self.task_id}_next_due"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        next_due = self.task_data.get("next_due")
        if next_due:
            if isinstance(next_due, str):
                next_due = datetime.fromisoformat(next_due)
            return self.coordinator.format_date(next_due)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.task_id in self.coordinator.tasks


class TaskLastCompletedSensor(CoordinatorEntity, SensorEntity):
    """Sensor for task last completed date."""

    def __init__(self, coordinator: TaskButlerCoordinator, task_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.task_id = task_id

    @property
    def task_data(self) -> dict[str, Any]:
        """Get task data from coordinator."""
        return self.coordinator.tasks.get(self.task_id, {})

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task_name = self.task_data.get("name", "Unknown Task")
        return f"{task_name} Last Completed"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{DOMAIN}_{self.task_id}_last_completed"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        last_completed = self.task_data.get("last_completed")
        if last_completed:
            if isinstance(last_completed, str):
                last_completed = datetime.fromisoformat(last_completed)
            return self.coordinator.format_date(last_completed)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.task_id in self.coordinator.tasks
