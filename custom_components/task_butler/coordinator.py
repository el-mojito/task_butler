from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .models import Task

_LOGGER = logging.getLogger(__name__)


class TaskButlerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            _LOGGER,
            name="Task Butler",
            update_interval=timedelta(minutes=10),
        )

        # Temporary hardcoded tasks (MVP)
        self.tasks: list[Task] = [
            Task(
                id="clean_oven",
                name="Clean Oven",
                interval_days=90,
                strict=True,
                last_done=None,
            ),
            Task(
                id="descale_coffee",
                name="Descale Coffee Machine",
                interval_days=30,
                strict=False,
                last_done=None,
            ),
        ]

    async def _async_update_data(self):
        now = dt_util.now()

        data = {}
        for task in self.tasks:
            data[task.id] = {
                "task": task,
                "is_due": task.is_due(now),
                "days": task.days_until(now),
                "next_due": task.next_due(now),
            }

        return data

    async def async_mark_done(self, task_id: str):
        now = dt_util.now()

        for task in self.tasks:
            if task.id == task_id:
                task.last_done = now

        await self.async_request_refresh()
