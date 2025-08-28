import logging

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import GlueLockCoordinator
from . import GlueLockConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: GlueLockConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button platform."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: GlueLockCoordinator = config_entry.runtime_data.coordinator

    buttons = [GlueLockButton(coordinator, hass), GlueUnlockButton(coordinator, hass)]

    async_add_entities(buttons, update_before_add=True)


class GlueLockButton(CoordinatorEntity, ButtonEntity):
    # Implement one of these methods.
    def __init__(self, coordinator: GlueLockCoordinator, hass: HomeAssistant) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.glue_lock = coordinator.glue_lock_data.device
        self._attr_name = "Glue Lock Button"
        self.entity_id = generate_entity_id("button.{}", "glue_lock_button", hass=hass)
        self._attr_unique_id = (
            f"{DOMAIN}-{coordinator.glue_lock_data.device.serial_number}-button"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.glue_lock.control_lock(type="lock")
        except Exception as e:
            _LOGGER.error("Error pressing lock button: %s", e)

    @property
    def name(self) -> str:
        """Return the name of the button."""
        return "Lock"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the button."""
        return self._attr_unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the button."""
        return "mdi:lock"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return self.coordinator.glue_lock_data.device_data

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return ButtonDeviceClass.IDENTIFY


class GlueUnlockButton(CoordinatorEntity, ButtonEntity):
    # Implement one of these methods.
    def __init__(self, coordinator: GlueLockCoordinator, hass: HomeAssistant) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.glue_lock = coordinator.glue_lock_data
        self._attr_name = "Glue Unlock Button"
        self.entity_id = generate_entity_id(
            "button.{}", "glue_lock_unlock_button", hass=hass
        )
        self._attr_unique_id = (
            f"{DOMAIN}-{coordinator.glue_lock_data.device.serial_number}-unlock-button"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.glue_lock.control_lock(type="unlock")
        except Exception as e:
            _LOGGER.error("Error pressing toggle lock button: %s", e)

    @property
    def name(self) -> str:
        """Return the name of the button."""
        return "Unlock"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the button."""
        return self._attr_unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the button."""
        return "mdi:lock-open"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return self.coordinator.glue_lock_data.device_data

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return ButtonDeviceClass.IDENTIFY
