import logging
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfInformation, SIGNAL_STRENGTH_DECIBELS
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DataCache:
    """Cache for data from cpe_detect."""

    def __init__(self, client, refresh_interval=timedelta(minutes=1)):
        self._client = client
        self._refresh_interval = refresh_interval
        self._data = None
        self._last_update = None
        self._lock = asyncio.Lock()

    async def get_data(self):
        """Get cached data or update if needed."""
        async with self._lock:
            now = datetime.now()
            if not self._data or not self._last_update or now - self._last_update > self._refresh_interval:
                self._data = await self._client.cpe_detect()
                self._last_update = now
                _LOGGER.debug(f"Data from cpe_detect updated: {self._data}")
            else:
                _LOGGER.debug("Using cached data from cpe_detect")
            return self._data

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up MiWiFi sensors based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    data_cache = DataCache(client)

    sensors = [
        BaseMiWiFiSensor(client, data_cache, "net.ipv6info.ip6addr", "IPv6 Address", icon="mdi:ip"),
        BaseMiWiFiSensor(client, data_cache, "net.ipv6info.dns", "IPv6 DNS", icon="mdi:dns"),
        BaseMiWiFiSensor(client, data_cache, "net.ipv4info.ipv4", "IPv4 Address", icon="mdi:ip"),
        BaseMiWiFiSensor(client, data_cache, "net.ipv4info.dns", "IPv4 DNS", icon="mdi:dns"),
        BaseMiWiFiSensor(client, data_cache, "net.info.cell_band", "Cell Band", icon="mdi:satellite"),
        BaseMiWiFiSensor(client, data_cache, "net.info.cell_band_5g", "Cell Band 5G", icon="mdi:satellite-variant"),
        BaseMiWiFiSensor(client, data_cache, "net.info.ci", "Cell ID", icon="mdi:map-marker"),
        BaseMiWiFiSensor(client, data_cache, "net.info.datausage", "Data Usage", native_unit=UnitOfInformation.MEGABYTES, device_class=SensorDeviceClass.DATA_SIZE, icon="mdi:database", state_class=SensorStateClass.TOTAL),
        BaseMiWiFiSensor(client, data_cache, "net.info.linktype", "Link Type", icon="mdi:network"),
        BaseMiWiFiSensor(client, data_cache, "net.info.operator", "Operator", icon="mdi:cellphone"),
        BaseMiWiFiSensor(client, data_cache, "net.info.freqband", "Frequency Band", icon="mdi:signal"),
        BaseMiWiFiSensor(client, data_cache, "net.info.rsrp", "RSRP", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "net.info.rsrp_5g", "RSRP 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "net.info.rsrq", "RSRQ", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "net.info.rsrq_5g", "RSRQ 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "net.info.snr", "SNR", native_unit=SIGNAL_STRENGTH_DECIBELS, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "net.info.snr_5g", "SNR 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
    ]
    async_add_entities(sensors, True)

class BaseMiWiFiSensor(SensorEntity):
    """Base class for all MiWiFi sensors."""

    def __init__(self, client, data_cache, sensor_key, name, native_unit=None, device_class=None, icon=None, state_class=None):
        self._client = client
        self._data_cache = data_cache
        self._sensor_key = sensor_key
        self._name = name
        self._native_unit_of_measurement = native_unit
        self._device_class = device_class
        self._icon = icon
        self._state_class = state_class
        self._state = None
        self._available = False
        self._mac_address = client.mac_address

    @property
    def device_info(self):
        """Return device information to associate this entity with a device."""
        return {
            "identifiers": {(DOMAIN, self._mac_address)},
            "name": f"Xiaomi Router {self._client._host}",
            "manufacturer": "Xiaomi",
            "model": "CB0401V2",
            "sw_version": self._client.firmware_version,  # Extracted from init_info
        }

    @property
    def device_class(self):
        """Return the device class for the sensor."""
        return self._device_class

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self._native_unit_of_measurement

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return self._icon

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def unique_id(self):
        """Return a unique ID for this sensor to enable UI management."""
        return f"{self._mac_address}_{self._sensor_key.replace('.', '_')}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self):
        """Return True if sensor is available."""
        return self._available

    @property
    def should_poll(self):
        """Return True if the entity should be polled."""
        return True

    async def async_update(self):
        """Fetch data from the cache and update the sensor state."""
        data = await self._data_cache.get_data()
        
        keys = self._sensor_key.split(".")
        value = data
        for key in keys:
            value = value.get(key, {})

        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
            value = value[0]
        
        if value:
            self._state = value
            self._available = True
        else:
            self._state = None
            self._available = False
