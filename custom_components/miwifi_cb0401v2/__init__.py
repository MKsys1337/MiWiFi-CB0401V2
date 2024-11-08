import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .api import MiWiFiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""
    client = MiWiFiClient(
        host=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"],
        session=hass.helpers.aiohttp_client.async_get_clientsession()
    )
    await client.login()  # Log in and fetch token

    if not client.mac_address:
        _LOGGER.error("MAC address not found. Device will not be properly registered.")
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
