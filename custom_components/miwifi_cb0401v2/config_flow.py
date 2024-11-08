import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult

from .api import MiWiFiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Konfigurationsschema für die Eingabemaske
CONFIG_SCHEMA = vol.Schema({
    vol.Required("host"): str,
    vol.Required("username"): str,
    vol.Required("password"): str,
})

class MiWiFiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for MiWiFi CB0401V2 integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Versuche, die Zugangsdaten zu testen
            host = user_input["host"]
            username = user_input["username"]
            password = user_input["password"]

            # Erstelle eine Client-Instanz und führe den Login durch
            session = async_get_clientsession(self.hass)
            client = MiWiFiClient(host, username, password, session)

            if await client.login():
                # Speichere die Konfiguration in Home Assistant, wenn der Login erfolgreich ist
                return self.async_create_entry(title="MiWiFi Router", data=user_input)
            else:
                # Fehlerbehandlung, wenn der Login fehlschlägt
                errors["base"] = "auth"

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)

    async def async_step_import(self, import_config):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input=import_config)
