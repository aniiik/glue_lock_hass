"""Integration 101 Template integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_API_KEY,
    CONF_LOCK_ID,
    CONF_LOCK_NAME,
    DEFAULT_SCAN_INTERVAL,
)
from pygluelock.glue_lock import GlueLock

_LOGGER = logging.getLogger(__name__)


@dataclass
class GlueLockData:
    device: GlueLock
    device_data: dict[str, Any] = None


class GlueLockCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.username = config_entry.data[CONF_USERNAME]
        self.password = config_entry.data[CONF_PASSWORD]
        self.api_key = config_entry.data[CONF_API_KEY]
        self.lock_id = config_entry.data[CONF_LOCK_ID]
        self.lock_name = config_entry.data[CONF_LOCK_NAME]

        super().__init__(
            hass,
            _LOGGER,
            name=self.lock_name,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        client_session = aiohttp_client.async_get_clientsession(hass)
        self.glue_lock_data = GlueLockData(
            device=GlueLock(
                username=self.username,
                password=self.password,
                lock_id=self.lock_id,
                session=client_session,
            )
        )

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        if not self.glue_lock_data.device.is_connected:
            await self.glue_lock_data.device.connect()
        try:
            await self.glue_lock_data.device.update()
            if self.glue_lock_data.device_data is None:
                self.glue_lock_data.device_data = DeviceInfo(
                    name=self.glue_lock_data.device.name,
                    manufacturer="Glue",
                    serial_number=self.glue_lock_data.device.serial_number,
                    sw_version=self.glue_lock_data.device.firmware_version,
                    identifiers={
                        (
                            DOMAIN,
                            self.glue_lock_data.device.serial_number,
                        )
                    },
                )
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch devices: {err}") from err

        return self.glue_lock_data
