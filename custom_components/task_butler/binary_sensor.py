from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import TaskButlerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TaskDueSensor(coordinator, task_id)
        for task_id in coordinator.data
    ]

    async_add_entities(entities)


class TaskDueSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: TaskButlerCoordinator, task_id: str):
        super().__init__(coordinator)
        self._task_id = task_id
        self._attr_unique_id = f"{task_id}_due"
        self._attr_name = f"Task {task_id} Due"

    @property
    def is_on(self):
        return self.coordinator.data[self._task_id]["is_due"]
