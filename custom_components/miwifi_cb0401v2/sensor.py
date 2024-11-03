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
        LteSignalStrengthSensor(client),
        LteSignalQualitySensor(client),
        LteNetworkTypeSensor(client),
        LteOperatorSensor(client),
        LteDataUsageSensor(client),
        LteCellBandSensor(client),
        Lte5GSignalStrengthSensor(client),
        Lte5GSignalQualitySensor(client),
        Lte5GCellBandSensor(client),
        LteFrequencyBandsSensor(client),
        LteDownlinkBandwidthSensor(client),
        LteUplinkBandwidthSensor(client),
        LteArfcnSensor(client),
        LtePciSensor(client),
        Lte5GPciSensor(client),
        LteCiSensor(client),
        Lte5GCiSensor(client),
        SimStatusSensor(client),
        SimPinRetrySensor(client),
        SimPukRetrySensor(client),
        MobileDataEnabledSensor(client),
        NetworkRoamingEnabledSensor(client),
        NetworkTypeSettingSensor(client),
        CurrentApnSensor(client),
        # Sensoren basierend auf init_info
        RouterNameSensor(client),
        FirmwareVersionSensor(client),
        HardwareModelSensor(client),
        MeshSupportSensor(client),
        Support160MHzSensor(client),
        LanguageSensor(client),
        CountryCodeSensor(client),
        # Sensoren basierend auf wifi_display für jedes WLAN
        WifiSsidSensor(client, wifi_index=1),
        WifiStatusSensor(client, wifi_index=1),
        WifiBandwidthSensor(client, wifi_index=1),
        WifiChannelSensor(client, wifi_index=1),
        WifiHiddenSensor(client, wifi_index=1),
        WifiSsidSensor(client, wifi_index=2),
        WifiStatusSensor(client, wifi_index=2),
        WifiBandwidthSensor(client, wifi_index=2),
        WifiChannelSensor(client, wifi_index=2),
        WifiHiddenSensor(client, wifi_index=2),
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

class LteSignalStrengthSensor(BaseMiWiFiSensor):
    """Sensor für die LTE-Signalstärke (RSRP)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Signalstärke"
        self._unit_of_measurement = "dBm"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            rsrp = data["net"]["info"].get("rsrp")
            if rsrp:
                self._state = float(rsrp)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteSignalQualitySensor(BaseMiWiFiSensor):
    """Sensor für die LTE-Signalqualität (RSRQ)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Signalqualität"
        self._unit_of_measurement = "dB"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Kann ein Float-Wert sein

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            rsrq = data["net"]["info"].get("rsrq")
            if rsrq:
                self._state = float(rsrq)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteNetworkTypeSensor(BaseMiWiFiSensor):
    """Sensor für den LTE Netzwerktyp."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Netzwerktyp"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "5G NSA"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            linktype = data["net"]["info"].get("linktype")
            if linktype:
                self._state = linktype
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteOperatorSensor(BaseMiWiFiSensor):
    """Sensor für den LTE Netzbetreiber."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Netzbetreiber"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "Telekom.de"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            operator = data["net"]["info"].get("operator")
            if operator:
                self._state = operator
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteDataUsageSensor(BaseMiWiFiSensor):
    """Sensor für die verbrauchte Datenmenge."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Datenverbrauch"
        self._unit_of_measurement = "MB"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Float-Wert in MB

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            datausage = data["net"]["info"].get("datausage")
            if datausage:
                self._state = float(datausage)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteCellBandSensor(BaseMiWiFiSensor):
    """Sensor für das LTE Empfangsband."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Empfangsband"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "B3(FDD 1800+)"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            cell_band = data["net"]["info"].get("cell_band")
            if cell_band:
                self._state = cell_band
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class Lte5GSignalStrengthSensor(BaseMiWiFiSensor):
    """Sensor für die 5G Signalstärke (RSRP 5G)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi 5G Signalstärke"
        self._unit_of_measurement = "dBm"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Float-Wert in dBm

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            rsrp_5g = data["net"]["info"].get("rsrp_5g")
            if rsrp_5g and rsrp_5g != "-":
                self._state = float(rsrp_5g)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class Lte5GSignalQualitySensor(BaseMiWiFiSensor):
    """Sensor für die 5G Signalqualität (RSRQ 5G)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi 5G Signalqualität"
        self._unit_of_measurement = "dB"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Float-Wert in dB

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            rsrq_5g = data["net"]["info"].get("rsrq_5g")
            if rsrq_5g and rsrq_5g != "-":
                self._state = float(rsrq_5g)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class Lte5GCellBandSensor(BaseMiWiFiSensor):
    """Sensor für das 5G Empfangsband."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi 5G Empfangsband"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "n78(TDD 3500)"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            cell_band_5g = data["net"]["info"].get("cell_band_5g")
            if cell_band_5g and cell_band_5g != "-":
                self._state = cell_band_5g
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteFrequencyBandsSensor(BaseMiWiFiSensor):
    """Sensor für die genutzten Frequenzbänder."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE Frequenzbänder"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "B3+B8+n78"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            freqband = data["net"]["info"].get("freqband")
            if freqband:
                self._state = freqband
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteDownlinkBandwidthSensor(BaseMiWiFiSensor):
    """Sensor für die Downlink-Bandbreite."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Downlink Bandbreite"
        self._unit_of_measurement = "MHz"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "20,10,90"

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            dl_bw = data["net"]["info"].get("dl_bw")
            if dl_bw:
                self._state = dl_bw
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteUplinkBandwidthSensor(BaseMiWiFiSensor):
    """Sensor für die Uplink-Bandbreite."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Uplink Bandbreite"
        self._unit_of_measurement = "MHz"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "20,90"

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            ul_bw = data["net"]["info"].get("ul_bw")
            if ul_bw:
                self._state = ul_bw
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteArfcnSensor(BaseMiWiFiSensor):
    """Sensor für die ARFCN (Absolute Radio Frequency Channel Number)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE ARFCN"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "1300,3749,641760"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            arfcn = data["net"]["info"].get("arfcn")
            if arfcn:
                self._state = arfcn
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LtePciSensor(BaseMiWiFiSensor):
    """Sensor für die Physical Cell ID (PCI)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE PCI"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "459"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            pci = data["net"]["info"].get("pci")
            if pci:
                self._state = int(pci)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class Lte5GPciSensor(BaseMiWiFiSensor):
    """Sensor für die 5G Physical Cell ID (PCI 5G)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi 5G PCI"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "724"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            pci_5g = data["net"]["info"].get("pci_5g")
            if pci_5g and pci_5g != "-":
                self._state = int(pci_5g)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class LteCiSensor(BaseMiWiFiSensor):
    """Sensor für die Cell ID (CI)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi LTE CI"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "28600576"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            ci = data["net"]["info"].get("ci")
            if ci:
                self._state = int(ci)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

class Lte5GCiSensor(BaseMiWiFiSensor):
    """Sensor für die 5G Cell ID (CI 5G)."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi 5G CI"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Kann ein Integer sein oder "-"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("net") and data["net"].get("info"):
            ci_5g = data["net"]["info"].get("ci_5g")
            if ci_5g and ci_5g != "-":
                self._state = int(ci_5g)
                self._available = True
            else:
                self._state = None
                self._available = False
        else:
            self._state = None
            self._available = False

# Sensoren für SIM-Informationen

class SimStatusSensor(BaseMiWiFiSensor):
    """Sensor für den SIM-Kartenstatus."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi SIM-Kartenstatus"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "Eingesteckt" oder "Nicht vorhanden"

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("sim") and data["sim"].get("status") is not None:
            status = data["sim"]["status"]
            self._state = "Eingesteckt" if status == 1 else "Nicht vorhanden"
            self._available = True
        else:
            self._state = None
            self._available = False

class SimPinRetrySensor(BaseMiWiFiSensor):
    """Sensor für verbleibende PIN-Eingabeversuche."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi SIM PIN-Versuche"
        self._unit_of_measurement = "Versuche"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Integer-Wert

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("sim") and data["sim"].get("pinretry") is not None:
            self._state = int(data["sim"]["pinretry"])
            self._available = True
        else:
            self._state = None
            self._available = False

class SimPukRetrySensor(BaseMiWiFiSensor):
    """Sensor für verbleibende PUK-Eingabeversuche."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi SIM PUK-Versuche"
        self._unit_of_measurement = "Versuche"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Integer-Wert

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.cpe_detect()
        if data and data.get("sim") and data["sim"].get("pukretry") is not None:
            self._state = int(data["sim"]["pukretry"])
            self._available = True
        else:
            self._state = None
            self._available = False

# Sensoren für Netzwerkeinstellungen aus get_mobile_net_cfg

class MobileDataEnabledSensor(BaseMiWiFiSensor):
    """Sensor, ob mobile Daten aktiviert sind."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Mobile Daten"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "An" oder "Aus"

    async def async_update(self):
        data = await self._client.get_mobile_net_cfg()
        if data and data.get("networkdata") is not None:
            self._state = "An" if data["networkdata"] == 1 else "Aus"
            self._available = True
        else:
            self._state = None
            self._available = False

class NetworkRoamingEnabledSensor(BaseMiWiFiSensor):
    """Sensor, ob Roaming aktiviert ist."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Roaming"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "An" oder "Aus"

    async def async_update(self):
        data = await self._client.get_mobile_net_cfg()
        if data and data.get("networkroam") is not None:
            self._state = "An" if data["networkroam"] == 1 else "Aus"
            self._available = True
        else:
            self._state = None
            self._available = False

class NetworkTypeSettingSensor(BaseMiWiFiSensor):
    """Sensor für die Netzwerkeinstellung (z.B. "auto")."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Netzwerktypeinstellung"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "auto"

    async def async_update(self):
        data = await self._client.get_mobile_net_cfg()
        if data and data.get("networktype"):
            self._state = data["networktype"]
            self._available = True
        else:
            self._state = None
            self._available = False

# Sensor für aktuellen APN aus get_apn_info

class CurrentApnSensor(BaseMiWiFiSensor):
    """Sensor für den aktuellen APN."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Aktueller APN"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # APN-Name

    async def async_update(self):
        data = await self._client.get_apn_info()
        if data and data.get("curid") and data.get("apnlist"):
            curid = data["curid"]
            apnlist = data["apnlist"]
            for apn in apnlist:
                if apn.get("id") == curid:
                    self._state = apn.get("apn")
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False

class RouterNameSensor(BaseMiWiFiSensor):
    """Sensor für den Namen des Routers."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Routername"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "cb0401_minet_35f1fc"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("routername"):
            self._state = data["routername"]
            self._available = True
        else:
            self._state = None
            self._available = False

class FirmwareVersionSensor(BaseMiWiFiSensor):
    """Sensor für die Firmware-Version des Routers."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Firmware-Version"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "3.0.59"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("romversion"):
            self._state = data["romversion"]
            self._available = True
        else:
            self._state = None
            self._available = False


class HardwareModelSensor(BaseMiWiFiSensor):
    """Sensor für das Hardware-Modell des Routers."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Hardware-Modell"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "CB0401V2"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("hardware"):
            self._state = data["hardware"]
            self._available = True
        else:
            self._state = None
            self._available = False

class MeshSupportSensor(BaseMiWiFiSensor):
    """Sensor, ob der Router Mesh unterstützt."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Mesh-Unterstützung"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "Ja" oder "Nein"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("isSupportMesh") is not None:
            self._state = "Ja" if data["isSupportMesh"] == 1 else "Nein"
            self._available = True
        else:
            self._state = None
            self._available = False

class LanguageSensor(BaseMiWiFiSensor):
    """Sensor für die Sprache des Routers."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Sprache"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "de"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("language"):
            self._state = data["language"]
            self._available = True
        else:
            self._state = None
            self._available = False


class CountryCodeSensor(BaseMiWiFiSensor):
    """Sensor für den Ländercode des Routers."""

    def __init__(self, client):
        super().__init__(client)
        self._name = "MiWiFi Ländercode"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # z.B. "DE"

    async def async_update(self):
        data = await self._client.get_init_info()
        if data and data.get("countrycode"):
            self._state = data["countrycode"]
            self._available = True
        else:
            self._state = None
            self._available = False

class WifiSsidSensor(BaseMiWiFiSensor):
    """Sensor für die SSID des WLANs."""

    def __init__(self, client, wifi_index):
        super().__init__(client)
        self._wifi_index = wifi_index
        self._name = f"MiWiFi SSID WLAN {wifi_index}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # SSID

    async def async_update(self):
        data = await self._client.get_wifi_display()
        if data and data.get("info"):
            for wifi in data["info"]:
                if wifi.get("wifiIndex") == self._wifi_index:
                    self._state = wifi.get("ssid")
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False

class WifiStatusSensor(BaseMiWiFiSensor):
    """Sensor für den Status des WLANs (An/Aus)."""

    def __init__(self, client, wifi_index):
        super().__init__(client)
        self._wifi_index = wifi_index
        self._name = f"MiWiFi WLAN {wifi_index} Status"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "An" oder "Aus"

    async def async_update(self):
        data = await self._client.get_wifi_display()
        if data and data.get("info"):
            for wifi in data["info"]:
                if wifi.get("wifiIndex") == self._wifi_index:
                    on = wifi.get("on")
                    self._state = "An" if on == "1" else "Aus"
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False

class WifiBandwidthSensor(BaseMiWiFiSensor):
    """Sensor für die Bandbreite des WLANs."""

    def __init__(self, client, wifi_index):
        super().__init__(client)
        self._wifi_index = wifi_index
        self._name = f"MiWiFi WLAN {wifi_index} Bandbreite"
        self._unit_of_measurement = "MHz"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Bandbreite in MHz

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        data = await self._client.get_wifi_display()
        if data and data.get("info"):
            for wifi in data["info"]:
                if wifi.get("wifiIndex") == self._wifi_index:
                    bandwidth = wifi.get("bandwidth")
                    self._state = bandwidth
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False

class WifiChannelSensor(BaseMiWiFiSensor):
    """Sensor für den Kanal des WLANs."""

    def __init__(self, client, wifi_index):
        super().__init__(client)
        self._wifi_index = wifi_index
        self._name = f"MiWiFi WLAN {wifi_index} Kanal"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # Kanalnummer

    async def async_update(self):
        data = await self._client.get_wifi_display()
        if data and data.get("info"):
            for wifi in data["info"]:
                if wifi.get("wifiIndex") == self._wifi_index:
                    channel = wifi.get("channel")
                    self._state = channel
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False

class WifiHiddenSensor(BaseMiWiFiSensor):
    """Sensor, ob das WLAN versteckt ist."""

    def __init__(self, client, wifi_index):
        super().__init__(client)
        self._wifi_index = wifi_index
        self._name = f"MiWiFi WLAN {wifi_index} Versteckt"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state  # "Ja" oder "Nein"

    async def async_update(self):
        data = await self._client.get_wifi_display()
        if data and data.get("info"):
            for wifi in data["info"]:
                if wifi.get("wifiIndex") == self._wifi_index:
                    hidden = wifi.get("hidden")
                    self._state = "Ja" if hidden == "1" else "Nein"
                    self._available = True
                    return
            self._state = None
            self._available = False
        else:
            self._state = None
            self._available = False
