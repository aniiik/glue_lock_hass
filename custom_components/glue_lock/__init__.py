"""The Glue Lock integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .coordinator import GlueLockCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]


type GlueLockConfigEntry = ConfigEntry[RuntimeData]  # noqa: F821


@dataclass
class RuntimeData:
    """Runtime data for the Glue Lock integration."""

    coordinator: DataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: GlueLockConfigEntry) -> bool:
    """Set up Glue Lock from a config entry."""

    coordinator = GlueLockCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.glue_lock_data.device.is_connected:
        raise ConfigEntryNotReady

    entry.runtime_data = RuntimeData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: GlueLockConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: GlueLockConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
