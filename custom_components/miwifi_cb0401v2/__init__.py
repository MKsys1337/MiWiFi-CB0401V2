# __init__.py

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import MiWiFiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up MiWiFi CB0401V2 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    session = hass.helpers.aiohttp_client.async_get_clientsession()
    client = MiWiFiClient(
        host=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"],
        session=session
    )

    # Versuche, dich beim Router anzumelden
    login_successful = await client.login()
    if not login_successful:
        _LOGGER.error("Login fehlgeschlagen. Bitte überprüfe die Anmeldedaten.")
        return False

    hass.data[DOMAIN][entry.entry_id] = client

    # Sensoren einrichten
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, "sensor")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
