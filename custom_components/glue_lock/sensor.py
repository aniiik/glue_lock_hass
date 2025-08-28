import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import generate_entity_id

from . import GlueLockConfigEntry
from .const import DOMAIN
from .coordinator import GlueLockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: GlueLockConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    coordinator: GlueLockCoordinator = config_entry.runtime_data.coordinator

    sensors = [GlueBatterySensor(coordinator, hass)]

    # Create the sensors.
    async_add_entities(sensors, update_before_add=True)


class GlueBatterySensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: GlueLockCoordinator, hass: HomeAssistant) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.battery = self.coordinator.glue_lock_data.device.battery_status  # noqa: SLF001
        self.entity_id = generate_entity_id("sensor.{}", "glue_lock_battery", hass=hass)

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.BATTERY

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self.coordinator.glue_lock_data.device_data

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Battery"

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.battery

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return PERCENTAGE

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return (
            f"{DOMAIN}-{self.coordinator.glue_lock_data.device.serial_number}-battery"
        )
