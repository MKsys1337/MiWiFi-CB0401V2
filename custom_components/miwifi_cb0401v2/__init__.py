# __init__.py

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MiWiFiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up MiWiFi CB0401V2 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    session = async_get_clientsession(hass)
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

    # Abrufen der MAC-Adresse nach erfolgreichem Login
    mac_address = await client.fetch_mac_address()
    if not mac_address:
        _LOGGER.error("MAC address not found. Device will not be properly registered.")
        return False

    # Gerät im Geräteregister anlegen
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, mac_address)},
        manufacturer="Xiaomi",
        name=f"Xiaomi Router {entry.data['host']}",
        model="CB0401V2",
        sw_version="3.0.6"  # Beispiel: Passe die Software-Version an, wenn nötig
    )

    hass.data[DOMAIN][entry.entry_id] = client

    # Sensoren einrichten
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

