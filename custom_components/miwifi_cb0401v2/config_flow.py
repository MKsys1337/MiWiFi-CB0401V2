import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MiWiFiClient
from .const import DOMAIN, DEFAULT_HOST, DEFAULT_USERNAME

_LOGGER = logging.getLogger(__name__)

class MiWiFiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MiWiFi CB0401V2."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        self._errors = {}
        if user_input is not None:
            valid = await self._test_credentials(
                user_input["host"],
                user_input["username"],
                user_input["password"]
            )
            if valid:
                await self.async_set_unique_id(user_input["host"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="MiWiFi Router", data=user_input)
            else:
                self._errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required("host", default=DEFAULT_HOST): str,
            vol.Required("username", default=DEFAULT_USERNAME): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors
        )

    async def _test_credentials(self, host, username, password):
        """Return true if credentials are valid."""
        try:
            session = async_get_clientsession(self.hass)
            client = MiWiFiClient(host, username, password, session)
            return await client.login()
        except Exception as e:
            _LOGGER.error("Authentifizierungsfehler: %s", e)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MiWiFiOptionsFlowHandler(config_entry)

class MiWiFiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle MiWiFi options."""

    def __init__(self, config_entry):
        """Initialize MiWiFi options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the MiWiFi options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            # Füge hier Optionen hinzu, falls erforderlich
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )
