"""Constants for Task Butler integration."""

from __future__ import annotations

from typing import Final

VERSION = "0.1.0"
NAME = "Task Butler"
MANUFACTURER = "@el-mojito"

DOMAIN: Final = "task_butler"

# Config keys
CONF_DATE_FORMAT: Final = "date_format"

# Date format options
DATE_FORMAT_DD_MM_YYYY: Final = "dd.mm.yyyy"
DATE_FORMAT_DDDD_DD_MM_YYYY: Final = "dddd dd.mm.yyyy"
DATE_FORMAT_MM_DD_YYYY: Final = "mm/dd/yyyy"
DATE_FORMAT_DDDD_MM_DD_YYYY: Final = "dddd mm/dd/yyyy"

DATE_FORMATS: Final = [
    DATE_FORMAT_DD_MM_YYYY,
    DATE_FORMAT_DDDD_DD_MM_YYYY,
    DATE_FORMAT_MM_DD_YYYY,
    DATE_FORMAT_DDDD_MM_DD_YYYY,
]

# Task scheduling modes
SCHEDULE_FIXED_DATE: Final = "fixed_date"
SCHEDULE_FIXED_OCCURRENCE: Final = "fixed_occurrence"
SCHEDULE_FIXED_INTERVAL: Final = "fixed_interval"

SCHEDULE_MODES: Final = [
    SCHEDULE_FIXED_DATE,
    SCHEDULE_FIXED_OCCURRENCE,
    SCHEDULE_FIXED_INTERVAL,
]

# Interval modes for fixed interval scheduling
INTERVAL_HARD_FIXED: Final = "hard_fixed"
INTERVAL_AFTER_COMPLETION: Final = "after_completion"

INTERVAL_MODES: Final = [
    INTERVAL_HARD_FIXED,
    INTERVAL_AFTER_COMPLETION,
]

# Default values
DEFAULT_DATE_FORMAT: Final = DATE_FORMAT_DDDD_DD_MM_YYYY
DEFAULT_SCHEDULE_MODE: Final = SCHEDULE_FIXED_INTERVAL
DEFAULT_INTERVAL_MODE: Final = INTERVAL_HARD_FIXED
DEFAULT_INTERVAL_DAYS: Final = 30

# Service names
SERVICE_MARK_COMPLETE: Final = "mark_task_complete"
SERVICE_CREATE_TASK: Final = "create_task"
SERVICE_DELETE_TASK: Final = "delete_task"
SERVICE_UPDATE_TASK: Final = "update_task"

# Platforms
PLATFORMS: Final = ["binary_sensor", "sensor"]

# Panel constants
PANEL_URL: Final = "task-butler"
PANEL_TITLE: Final = NAME
PANEL_ICON: Final = "mdi:clipboard-check"
PANEL_NAME: Final = "task-butler-panel"
PANEL_API_PATH: Final = "/task_butler_static"
PANEL_API_URL: Final = PANEL_API_PATH + "/task-butler-panel.js"
