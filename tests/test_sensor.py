"""Regression tests for missing sensor data and polling failures."""

from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from custom_components.miwifi_cb0401v2.sensor import BaseMiWiFiSensor


class SensorUpdateTests(IsolatedAsyncioTestCase):
    async def test_missing_second_dns_server(self):
        cache = AsyncMock()
        cache.get_data.side_effect = [
            {"dns": ["192.0.2.1", "192.0.2.2"]},
            {"dns": ["192.0.2.1"]},
        ]
        sensor = BaseMiWiFiSensor(
            SimpleNamespace(mac_address="02:00:00:00:00:01"),
            cache,
            "cpe_detect",
            "dns",
            "DNS 2",
            data_path=1,
        )

        await sensor.async_update()
        self.assertEqual(sensor.state, "192.0.2.2")
        self.assertTrue(sensor.available)

        await sensor.async_update()
        self.assertIsNone(sensor.state)
        self.assertFalse(sensor.available)

    async def test_sensor_recovers_after_failed_poll(self):
        cache = AsyncMock()
        cache.get_data.side_effect = [{"count": 3}, None, {"count": 0}]
        sensor = BaseMiWiFiSensor(
            SimpleNamespace(mac_address="02:00:00:00:00:01"),
            cache,
            "msgbox_count",
            "count",
            "SMS Messages",
        )

        await sensor.async_update()
        self.assertEqual(sensor.state, 3)
        self.assertTrue(sensor.available)

        await sensor.async_update()
        self.assertIsNone(sensor.state)
        self.assertFalse(sensor.available)

        await sensor.async_update()
        self.assertEqual(sensor.state, 0)
        self.assertTrue(sensor.available)
