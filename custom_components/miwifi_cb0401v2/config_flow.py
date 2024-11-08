import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult

from .api import MiWiFiClient
from .const import DOMAIN, DEFAULT_HOST, DEFAULT_USERNAME

_LOGGER = logging.getLogger(__name__)

# Configuration schema for the input form, with host preset and no username field
CONFIG_SCHEMA = vol.Schema({
    vol.Required("host", default=DEFAULT_HOST): str,
    vol.Required("password"): str,
})

class MiWiFiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for MiWiFi CB0401V2 integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Use default username since it is pre-configured in the router
            host = user_input["host"]
            username = DEFAULT_USERNAME
            password = user_input["password"]

            # Create a client instance and attempt login
            session = async_get_clientsession(self.hass)
            client = MiWiFiClient(host, username, password, session)

            if await client.login():
                # Save the configuration in Home Assistant if login is successful
                user_input["username"] = username  # Add default username to config
                return self.async_create_entry(title="MiWiFi Router", data=user_input)
            else:
                # Handle login failure
                errors["base"] = "auth"

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)

    async def async_step_import(self, import_config):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input=import_config)
