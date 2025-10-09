"""DataUpdateCoordinator for Task Butler."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_DATE_FORMAT,
    DOMAIN,
    INTERVAL_AFTER_COMPLETION,
    INTERVAL_HARD_FIXED,
    SCHEDULE_FIXED_DATE,
    SCHEDULE_FIXED_INTERVAL,
    SCHEDULE_FIXED_OCCURRENCE,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_tasks"


class TaskButlerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Task Butler data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize Task Butler coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.entry = entry
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.tasks: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Load tasks from storage if not already loaded
            if not self.tasks:
                stored_data = await self.store.async_load()
                if stored_data:
                    self.tasks = stored_data.get("tasks", {})

            # Update task states (check if tasks are due)
            current_time = datetime.now()
            for task_id, task in self.tasks.items():
                task["is_due"] = self._is_task_due(task, current_time)
                task["next_due"] = self._calculate_next_due(task, current_time)

            return self.tasks
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _is_task_due(self, task: dict[str, Any], current_time: datetime) -> bool:
        """Check if a task is currently due."""
        if not task.get("enabled", True):
            return False

        next_due = self._calculate_next_due(task, current_time)
        if next_due is None:
            return False

        return current_time >= next_due

    def _calculate_next_due(
        self, task: dict[str, Any], current_time: datetime
    ) -> datetime | None:
        """Calculate when a task is next due."""
        schedule_mode = task.get("schedule_mode")
        last_completed = task.get("last_completed")

        if schedule_mode == SCHEDULE_FIXED_INTERVAL:
            interval_days = task.get("interval_days", 30)
            interval_mode = task.get("interval_mode", INTERVAL_HARD_FIXED)

            if interval_mode == INTERVAL_AFTER_COMPLETION and last_completed:
                if isinstance(last_completed, str):
                    last_completed = datetime.fromisoformat(last_completed)
                return last_completed + timedelta(days=interval_days)
            # Hard fixed interval - for now, return a placeholder
            # In real implementation, you'd store the initial start date
            return current_time + timedelta(days=interval_days)

        if schedule_mode == SCHEDULE_FIXED_DATE:
            # Implementation for fixed date (e.g., every January 15th)
            # This would need more complex date parsing
            pass

        elif schedule_mode == SCHEDULE_FIXED_OCCURRENCE:
            # Implementation for fixed occurrence (e.g., every Monday)
            # This would need day-of-week parsing
            pass

        return None

    async def mark_task_complete(self, task_id: str) -> None:
        """Mark a task as completed."""
        if task_id not in self.tasks:
            _LOGGER.error("Task %s not found", task_id)
            return

        self.tasks[task_id]["last_completed"] = datetime.now().isoformat()
        self.tasks[task_id]["is_due"] = False

        await self._save_tasks()
        await self.async_request_refresh()

    async def create_task(self, task_data: dict[str, Any]) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "id": task_id,
            "name": task_data["name"],
            "schedule_mode": task_data["schedule_mode"],
            "interval_days": task_data.get("interval_days", 30),
            "interval_mode": task_data.get("interval_mode", INTERVAL_HARD_FIXED),
            "fixed_date": task_data.get("fixed_date"),
            "fixed_occurrence": task_data.get("fixed_occurrence"),
            "enabled": task_data.get("enabled", True),
            "created_at": datetime.now().isoformat(),
            "last_completed": None,
            "is_due": False,
            "next_due": None,
        }

        await self._save_tasks()
        await self.async_request_refresh()

        return task_id

    async def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            await self._save_tasks()
            await self.async_request_refresh()

    async def update_task(self, task_id: str, updates: dict[str, Any]) -> None:
        """Update a task."""
        if task_id not in self.tasks:
            _LOGGER.error("Task %s not found", task_id)
            return

        self.tasks[task_id].update(updates)
        await self._save_tasks()
        await self.async_request_refresh()

    async def _save_tasks(self) -> None:
        """Save tasks to storage."""
        await self.store.async_save({"tasks": self.tasks})

    @property
    def date_format(self) -> str:
        """Get the configured date format."""
        return self.entry.options.get("date_format", DEFAULT_DATE_FORMAT)

    def format_date(self, date: datetime) -> str:
        """Format a date according to user preference."""
        if self.date_format == "dd.mm.yyyy":
            return date.strftime("%d.%m.%Y")
        if self.date_format == "dddd dd.mm.yyyy":
            return date.strftime("%A %d.%m.%Y")
        if self.date_format == "mm/dd/yyyy":
            return date.strftime("%m/%d/%Y")
        if self.date_format == "dddd mm/dd/yyyy":
            return date.strftime("%A %m/%d/%Y")
        return date.strftime("%d.%m.%Y")
