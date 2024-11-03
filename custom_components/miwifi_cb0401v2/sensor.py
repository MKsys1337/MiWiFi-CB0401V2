# sensor.py

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up MiWiFi sensors based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        ConnectedDevicesSensor(client),
        WanDownloadSpeedSensor(client),
        WanUploadSpeedSensor(client),
        WanMaxDownloadSpeedSensor(client),
        WanMaxUploadSpeedSensor(client),
        SystemVersionSensor(client),
        WifiStatusSensor(client),
        WifiDetailSensor(client),
        # Weitere Sensoren können hier hinzugefügt werden
    ]
    async_add_entities(sensors, True)

class BaseMiWiFiSensor(SensorEntity):
    """Base class for all MiWiFi sensors."""

    def __init__(self, client):
        self._client = client
        self._state = None
        self._name = None
        self._unit_of_measurement = None
        self._available = False

    @property
    def available(self):
        """Return True if sensor is available."""
        return self._available

    @property
    def should_poll(self):
        """Return True if the entity should be polled."""
        return True

    async def async_update(self):
        """Fetch data and update sensor state."""
        raise NotImplementedError("Must be implemented in subclass")

class ConnectedDevicesSensor(BaseMiWiFiSensor):
    """Sensor for the number of connected devices."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Verbundene Geräte"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch data from the router and update the state."""
        devices = await self._client.get_device_list()
        if devices and devices.get("list"):
            self._state = len(devices.get("list", []))
            self._available = True
        else:
            self._state = None
            self._available = False

class WanDownloadSpeedSensor(BaseMiWiFiSensor):
    """Sensor for WAN download speed."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi WAN Download Geschwindigkeit"
        self._unit_of_measurement = "KByte/s"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch data from the router and update the state."""
        stats = await self._client.get_wan_statistics()
        if stats and stats.get("statistics"):
            downspeed = stats["statistics"].get("downspeed")
            if downspeed is not None:
                self._state = round(int(downspeed) / 1024, 2)  # Convert Byte/s to KByte/s
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class WanUploadSpeedSensor(BaseMiWiFiSensor):
    """Sensor for WAN upload speed."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi WAN Upload Geschwindigkeit"
        self._unit_of_measurement = "KByte/s"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch data from the router and update the state."""
        stats = await self._client.get_wan_statistics()
        if stats and stats.get("statistics"):
            upspeed = stats["statistics"].get("upspeed")
            if upspeed is not None:
                self._state = round(int(upspeed) / 1024, 2)  # Convert Byte/s to KByte/s
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class WanMaxDownloadSpeedSensor(BaseMiWiFiSensor):
    """Sensor for maximum WAN download speed."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Maximale WAN Download Geschwindigkeit"
        self._unit_of_measurement = "KByte/s"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch data from the router and update the state."""
        stats = await self._client.get_wan_statistics()
        if stats and stats.get("statistics"):
            max_downspeed = stats["statistics"].get("maxdownloadspeed")
            if max_downspeed is not None:
                self._state = round(int(max_downspeed) / 1024, 2)  # Convert Byte/s to KByte/s
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class WanMaxUploadSpeedSensor(BaseMiWiFiSensor):
    """Sensor for maximum WAN upload speed."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Maximale WAN Upload Geschwindigkeit"
        self._unit_of_measurement = "KByte/s"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch data from the router and update the state."""
        stats = await self._client.get_wan_statistics()
        if stats and stats.get("statistics"):
            max_upspeed = stats["statistics"].get("maxuploadspeed")
            if max_upspeed is not None:
                self._state = round(int(max_upspeed) / 1024, 2)  # Convert Byte/s to KByte/s
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class SystemVersionSensor(BaseMiWiFiSensor):
    """Sensor for the system version."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Systemversion"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch data from the router and update the state."""
        info = await self._client.get_system_info()
        if info and info.get("system"):
            self._state = info["system"].get("version")
            self._available = True
        else:
            self._state = None
            self._available = False

class WifiStatusSensor(BaseMiWiFiSensor):
    """Sensor for the Wi-Fi status."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi WLAN Status"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._state is None:
            return None
        return "An" if self._state else "Aus"

    async def async_update(self):
        """Fetch data from the router and update the state."""
        status = await self._client.get_wifi_status()
        if status and status.get("wifi"):
            self._state = status["wifi"].get("on") == "1"
            self._available = True
        else:
            self._state = None
            self._available = False

class WifiDetailSensor(BaseMiWiFiSensor):
    """Sensor for Wi-Fi details (SSID)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi SSID"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch data from the router and update the state."""
        detail = await self._client.get_wifi_detail()
        if detail and detail.get("info"):
            self._state = detail["info"].get("ssid")
            self._available = True
        else:
            self._state = None
            self._available = False
