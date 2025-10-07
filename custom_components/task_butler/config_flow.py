"""Config flow for Task Butler integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_TASK_NAME,
    CONF_INTERVAL_DAYS,
    CONF_SCHEDULE_TYPE,
    CONF_ENABLED,
    SCHEDULE_FIXED,
    SCHEDULE_COMPLETION_BASED,
    DEFAULT_INTERVAL_DAYS,
    DEFAULT_ENABLED,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TASK_NAME): str,
        vol.Required(CONF_INTERVAL_DAYS, default=DEFAULT_INTERVAL_DAYS): int,
        vol.Required(CONF_SCHEDULE_TYPE, default=SCHEDULE_FIXED): vol.In(
            [
                SCHEDULE_FIXED,
                SCHEDULE_COMPLETION_BASED,
            ]
        ),
        vol.Required(CONF_ENABLED, default=DEFAULT_ENABLED): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # TODO: Add validation logic here
    return {"title": data[CONF_TASK_NAME]}


class TaskButlerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Task Butler."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
