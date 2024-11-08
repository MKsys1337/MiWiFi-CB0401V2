import pytest
from unittest.mock import AsyncMock
from custom_components.miwifi_cb0401v2.sensor import BaseMiWiFiSensor

@pytest.fixture
def sensor():
    client = AsyncMock()
    client.mac_address = "00:11:22:33:44:55"
    return BaseMiWiFiSensor(client, "net.info.cell_band", "Cell Band Sensor")

@pytest.mark.asyncio
async def test_sensor_update(sensor):
    sensor._client.cpe_detect = AsyncMock(return_value={"net": {"info": {"cell_band": "B3"}}})
    await sensor.async_update()
    assert sensor.state == "B3"
    assert sensor.available
    assert sensor.name == "Cell Band Sensor"
    assert sensor.unique_id == "net.info.cell_band"
    sensor._client.cpe_detect = AsyncMock(side_effect=ConnectionError)
    await sensor.async_update()
    assert not sensor.available
