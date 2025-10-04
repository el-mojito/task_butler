"""My Integration init file."""

from homeassistant.core import HomeAssistant

DOMAIN = "task_butler"


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration."""
    hass.states.async_set(f"{DOMAIN}.example", "Hello World")
    return True
