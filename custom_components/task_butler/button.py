from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import TaskButlerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TaskButlerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TaskDoneButton(coordinator, task_id)
        for task_id in coordinator.data
    ]

    async_add_entities(entities)


class TaskDoneButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator: TaskButlerCoordinator, task_id: str):
        super().__init__(coordinator)
        self._task_id = task_id
        self._attr_unique_id = f"{task_id}_done"
        self._attr_name = f"Mark {task_id} done"

    async def async_press(self):
        await self.coordinator.async_mark_done(self._task_id)
