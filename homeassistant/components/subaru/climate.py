"""Support for Subaru HVAC system."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT

from . import DOMAIN as SUBARU_DOMAIN, SubaruDevice

_LOGGER = logging.getLogger(__name__)

SUPPORT_HVAC = [HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru binary_sensors by config_entry."""
    async_add_entities(
        [
            SubaruThermostat(
                device,
                hass.data[SUBARU_DOMAIN][config_entry.entry_id]["controller"],
                config_entry,
            )
            for device in hass.data[SUBARU_DOMAIN][config_entry.entry_id]["devices"][
                "climate"
            ]
        ],
        True,
    )


class SubaruThermostat(SubaruDevice, ClimateEntity):
    """Representation of a Subaru climate."""

    def __init__(self, subaru_device, controller, config_entry):
        """Initialize the Subaru device."""
        super().__init__(subaru_device, controller, config_entry)
        self._target_temperature = None
        self._temperature = None

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        if self.subaru_device.is_hvac_enabled():
            return HVAC_MODE_HEAT_COOL
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes.

        Need to be a subset of HVAC_MODES.
        """
        return SUPPORT_HVAC

    async def async_update(self):
        """Call by the Subaru device callback to update state."""
        _LOGGER.debug("Updating: %s", self._name)
        await super().async_update()
        self._target_temperature = self.subaru_device.get_goal_temp()

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        subaru_temp_units = self.subaru_device.measurement

        if subaru_temp_units == "F":
            return TEMP_FAHRENHEIT
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        _LOGGER.debug("Setting temperature for: %s", self._name)
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature:
            await self.subaru_device.set_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug("Setting mode for: %s", self._name)
        if hvac_mode == HVAC_MODE_OFF:
            await self.subaru_device.set_status(False)
        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            await self.subaru_device.set_status(True)
