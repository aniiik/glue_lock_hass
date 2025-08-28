"""Config flow for Glue Lock integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_LOCK_NAME, CONF_API_KEY, CONF_LOCK_ID
from pygluelock.glue_lock import GlueLock
from pygluelock.glue_lock import AuthorizationFailedExcepion

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    client_session = aiohttp_client.async_get_clientsession(hass)
    glue_lock = GlueLock(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        session=client_session,
    )
    try:
        await glue_lock.connect()
    except AuthorizationFailedExcepion as e:
        _LOGGER.warning("Incorrect username or password")
        raise InvalidAuth("Invalid username or password") from e

    # Return info that you want to store in the config entry.
    return glue_lock


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Glue Lock."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                glue_lock_connection = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self._step_data = glue_lock_connection
                return await self.async_step_settings()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the second step.

        Our second config flow step.
        Works just the same way as the first step.
        Except as it is our last step, we create the config entry after any validation.
        """

        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.

            if "base" not in errors:
                # ----------------------------------------------------------------------------
                # Validation was successful, so create the config entry.
                # ----------------------------------------------------------------------------
                lock_id = await self._step_data.get_lock_id_from_name(
                    name=user_input[CONF_LOCK_NAME]
                )
                lock_name = user_input[CONF_LOCK_NAME]
                self._data = {
                    CONF_USERNAME: self._step_data.username,
                    CONF_PASSWORD: self._step_data.password,
                    CONF_API_KEY: self._step_data.api_key,
                    CONF_LOCK_ID: lock_id,
                    CONF_LOCK_NAME: lock_name,
                }
                return self.async_create_entry(title=lock_name, data=self._data)

        available_locks = await self._step_data.get_all_locks()
        _LOGGER.debug("Available locks: %s", available_locks)

        STEP_SETTINGS_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_LOCK_NAME): selector(
                    {
                        "select": {
                            "options": [lock["name"] for lock in available_locks],
                            "mode": "dropdown",
                            "translation_key": "select_lock",
                        }
                    }
                ),
            }
        )

        # ----------------------------------------------------------------------------
        # Show settings form.  The step id always needs to match the bit after async_step_ in your method.
        # Set last_step to True here if it is last step.
        # ----------------------------------------------------------------------------
        return self.async_show_form(
            step_id="settings",
            data_schema=STEP_SETTINGS_DATA_SCHEMA,
            errors=errors,
            last_step=True,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
