import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfInformation, SIGNAL_STRENGTH_DECIBELS
from custom_components.miwifi_cb0401v2.sensor import (
    DataCache,
    BaseMiWiFiSensor,
    create_general_sensors,
    create_specific_sensors,
    create_newstatus_sensors
)

@pytest.fixture
def mock_client():
    """Fixture to create a mock MiWiFiClient."""
    client = MagicMock()
    client._host = "192.168.31.1"
    client.mac_address = "AA:BB:CC:DD:EE:FF"
    client.firmware_version = "1.0.0"
    return client

@pytest.fixture
async def mock_data_cache(mock_client):
    """Fixture to create a DataCache with mock data."""
    data_cache = DataCache(mock_client)
    data_cache.get_data = AsyncMock()

    # Set mock data for endpoints
    data_cache.get_data.side_effect = lambda endpoint: {
        "cpe_detect": {
            "net": {
                "info": {
                    "cell_band": "4G",
                    "cell_band_5g": "5G",
                    "ci": 12345,
                    "datausage": 200,
                    "linktype": "Ethernet",
                    "operator": "MyOperator",
                    "freqband": "700 MHz",
                    "rsrp": -80,
                    "rsrp_5g": -70,
                    "rsrq": -10,
                    "rsrq_5g": -8,
                    "snr": 15,
                    "snr_5g": 20,
                },
                "ipv4info": {
                    "ipv4": {"ip": "192.168.1.2", "mask": "255.255.255.0"},
                    "dns": ["8.8.8.8", "8.8.4.4"],
                },
                "ipv6info": {
                    "ip6addr": {"ip": "fe80::1"},
                    "dns": ["2001:4860:4860::8888", "2001:4860:4860::8844"],
                },
            }
        },
        "newstatus": {
            "hardware": {
                "mac": "AA:BB:CC:DD:EE:FF",
                "sn": "SN123456789",
                "version": "1.0.0",
                "imei": "123456789012345",
            },
            "2g": {
                "online_sta_count": 3,
                "ssid": "MySSID_2G"
            },
            "5g": {
                "online_sta_count": 5,
                "ssid": "MySSID_5G"
            }
        }
    }.get(endpoint, {})

    return data_cache

@pytest.mark.asyncio
async def test_general_sensors(mock_client, mock_data_cache):
    """Test creation and data retrieval of general sensors."""
    sensors = create_general_sensors(mock_client, mock_data_cache)
    assert len(sensors) > 0

    for sensor in sensors:
        await sensor.async_update()
        if sensor._sensor_key == "net.info.cell_band":
            assert sensor.state == "4G"
            assert sensor.icon == "mdi:satellite"
        elif sensor._sensor_key == "net.info.rsrp":
            assert sensor.state == -80
            assert sensor.native_unit_of_measurement == SIGNAL_STRENGTH_DECIBELS
            assert sensor.device_class == SensorDeviceClass.SIGNAL_STRENGTH

@pytest.mark.asyncio
async def test_specific_sensors(mock_client, mock_data_cache):
    """Test creation and data retrieval of specific sensors for IP and DNS."""
    sensors = create_specific_sensors(mock_client, mock_data_cache)
    assert len(sensors) > 0

    for sensor in sensors:
        await sensor.async_update()
        if sensor._sensor_key == "net.ipv4info.ipv4" and sensor._data_path == "ip":
            assert sensor.state == "192.168.1.2"
            assert sensor.icon == "mdi:ip"
        elif sensor._sensor_key == "net.ipv4info.dns" and sensor._data_path == 0:
            assert sensor.state == "8.8.8.8"
            assert sensor.icon == "mdi:dns"

@pytest.mark.asyncio
async def test_newstatus_sensors(mock_client, mock_data_cache):
    """Test creation and data retrieval of newstatus sensors."""
    sensors = create_newstatus_sensors(mock_client, mock_data_cache)
    assert len(sensors) > 0

    for sensor in sensors:
        await sensor.async_update()
        if sensor._sensor_key == "serial_number":
            assert sensor.state == "SN123456789"
            assert sensor.icon == "mdi:identifier"
        elif sensor._sensor_key == "ssid_2g":
            assert sensor.state == "MySSID_2G"
            assert sensor.icon == "mdi:wifi"
        elif sensor._sensor_key == "online_sta_count_2g":
            assert sensor.state == 3
            assert sensor.native_unit_of_measurement == "devices"
            assert sensor.icon == "mdi:devices"
