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
    """Cache for data from different API endpoints."""

    def __init__(self, client, refresh_interval=timedelta(minutes=1)):
        self._client = client
        self._refresh_interval = refresh_interval
        self._cpe_data = None
        self._newstatus_data = None
        self._last_update = None
        self._lock = asyncio.Lock()

    async def get_data(self, endpoint):
        """Get cached data for a specified endpoint or update if needed."""
        async with self._lock:
            now = datetime.now()
            if endpoint == "cpe_detect":
                if not self._cpe_data or not self._last_update or now - self._last_update > self._refresh_interval:
                    self._cpe_data = await self._client.cpe_detect()
                    self._last_update = now
                    _LOGGER.debug(f"Data from cpe_detect updated: {self._cpe_data}")
                else:
                    _LOGGER.debug("Using cached data from cpe_detect")
                return self._cpe_data
            elif endpoint == "newstatus":
                if not self._newstatus_data or not self._last_update or now - self._last_update > self._refresh_interval:
                    self._newstatus_data = await self._client._get_api("xqdtcustom/newstatus")
                    self._last_update = now
                    _LOGGER.debug(f"Data from newstatus updated: {self._newstatus_data}")
                else:
                    _LOGGER.debug("Using cached data from newstatus")
                return self._newstatus_data

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up MiWiFi sensors based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    data_cache = DataCache(client)

    # Define sensors with different endpoints
    sensors = (
        create_general_sensors(client, data_cache) +
        create_specific_sensors(client, data_cache) +
        create_newstatus_sensors(client, data_cache)
    )
    async_add_entities(sensors, True)

def create_general_sensors(client, data_cache):
    """Define the list of general sensors from the cpe_detect endpoint."""
    return [
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.cell_band", "Cell Band", icon="mdi:satellite"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.cell_band_5g", "Cell Band 5G", icon="mdi:satellite-variant"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.ci", "Cell ID", icon="mdi:map-marker"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.datausage", "Data Usage", native_unit=UnitOfInformation.MEGABYTES, device_class=SensorDeviceClass.DATA_SIZE, icon="mdi:database", state_class=SensorStateClass.TOTAL),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.linktype", "Link Type", icon="mdi:network"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.operator", "Operator", icon="mdi:cellphone"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.freqband", "Frequency Band", icon="mdi:signal"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.rsrp", "RSRP", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.rsrp_5g", "RSRP 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.rsrq", "RSRQ", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.rsrq_5g", "RSRQ 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, device_class=SensorDeviceClass.SIGNAL_STRENGTH, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.snr", "SNR", native_unit=SIGNAL_STRENGTH_DECIBELS, icon="mdi:signal", state_class=SensorStateClass.MEASUREMENT),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.info.snr_5g", "SNR 5G", native_unit=SIGNAL_STRENGTH_DECIBELS, icon="mdi:signal-variant", state_class=SensorStateClass.MEASUREMENT),
    ]

def create_specific_sensors(client, data_cache):
    """Define additional specific sensors for IP, mask, and DNS entries from the cpe_detect endpoint."""
    return [
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv4info.ipv4", "IPv4 Address", data_path="ip", icon="mdi:ip"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv4info.ipv4", "IPv4 Netmask", data_path="mask", icon="mdi:ip"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv4info.dns", "IPv4 DNS 1", data_path=0, icon="mdi:dns"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv4info.dns", "IPv4 DNS 2", data_path=1, icon="mdi:dns"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv6info.ip6addr", "IPv6 Address", data_path="ip", icon="mdi:ip"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv6info.dns", "IPv6 DNS 1", data_path=0, icon="mdi:dns"),
        BaseMiWiFiSensor(client, data_cache, "cpe_detect", "net.ipv6info.dns", "IPv6 DNS 2", data_path=1, icon="mdi:dns"),
    ]

def create_newstatus_sensors(client, data_cache):
    """Define additional sensors for the newstatus endpoint."""
    return [
        BaseMiWiFiSensor(client, data_cache, "newstatus", "hardware.mac", "MAC Address", icon="mdi:barcode"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "hardware.sn", "Serial Number", icon="mdi:identifier"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "hardware.version", "Firmware Version", icon="mdi:update"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "hardware.imei", "IMEI", icon="mdi:cellphone"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "2g.ssid", "SSID 2.4GHz", icon="mdi:wifi"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "5g.ssid", "SSID 5GHz", icon="mdi:wifi"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "2g.online_sta_count", "Online Devices 2.4GHz", icon="mdi:devices"),
        BaseMiWiFiSensor(client, data_cache, "newstatus", "5g.online_sta_count", "Online Devices 5GHz", icon="mdi:devices"),
    ]

class BaseMiWiFiSensor(SensorEntity):
    """Base class for all MiWiFi sensors."""

    def __init__(self, client, data_cache, endpoint, sensor_key, name, data_path=None, native_unit=None, device_class=None, icon=None, state_class=None):
        """Initialize the sensor with endpoint flexibility."""
        self._client = client
        self._data_cache = data_cache
        self._endpoint = endpoint  # Specifies which endpoint to use
        self._sensor_key = sensor_key
        self._name = name
        self._data_path = data_path
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
            "sw_version": self._client.firmware_version,
        }

    @property
    def device_class(self):
        return self._device_class

    @property
    def native_unit_of_measurement(self):
        return self._native_unit_of_measurement

    @property
    def icon(self):
        return self._icon

    @property
    def state_class(self):
        return self._state_class

    @property
    def unique_id(self):
        """Generate a unique ID for each sensor based on its sensor key and data path."""
        # Create a base ID using the MAC address and the sensor key
        base_id = f"{self._mac_address}_{self._sensor_key.replace('.', '_')}"
        
        # Append data_path information if available (e.g., 'ip', 'mask', or index for DNS)
        if self._data_path is not None:
            unique_suffix = str(self._data_path) if isinstance(self._data_path, int) else self._data_path
            return f"{base_id}_{unique_suffix}"
        
        # Return the base ID if no data_path is specified
        return base_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def available(self):
        return self._available

    async def async_update(self):
        """Fetch data from the specified endpoint and update the sensor state."""
        data = await self._data_cache.get_data(self._endpoint)
        _LOGGER.debug(f"Fetched data for endpoint '{self._endpoint}': {data}")

        if data:
            # Traverse nested keys in `sensor_key` to locate the specific data value
            keys = self._sensor_key.split(".")
            value = data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key, {})
                else:
                    _LOGGER.warning(f"Key '{key}' missing in data for sensor '{self._name}'")
                    value = None
                    break

            # Process `data_path` for additional extraction, handling both dict and list cases
            if value is not None and self._data_path is not None:
                if isinstance(value, dict) and isinstance(self._data_path, str):
                    value = value.get(self._data_path)
                elif isinstance(value, list):
                    if isinstance(self._data_path, int) and self._data_path < len(value):
                        value = value[self._data_path]
                    elif isinstance(self._data_path, str):
                        # Handle lists of dicts with named fields
                        value = [item.get(self._data_path) for item in value if isinstance(item, dict)]
                        value = ', '.join(filter(None, value))  # Join non-None values into a string
                else:
                    _LOGGER.warning(f"Data path '{self._data_path}' not found for sensor '{self._name}'")

            if isinstance(value, list) and len(value) > 0:
                if all(isinstance(item, list) for item in value):
                    value = ', '.join(map(str, [subitem for sublist in value for subitem in sublist]))
                else:
                    value = value[0]

            # Convert final value to None if it’s still a dictionary (not displayable as state)
            if isinstance(value, dict):
                value = None

            # Update sensor state and availability
            self._state = value if value is not None else None
            self._available = value is not None
            _LOGGER.debug(f"Sensor '{self._name}' updated: State = {self._state}, Available = {self._available}")
