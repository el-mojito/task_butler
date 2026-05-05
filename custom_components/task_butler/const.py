"""Constants for task_butler."""

from logging import Logger, getLogger

from homeassistant.util import dt as dt_util

LOGGER: Logger = getLogger(__package__)

DOMAIN = "task_butler"
PLATFORMS = ["binary_sensor", "button"]
