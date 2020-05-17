"""Support for Subaru charger switches."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON

from . import DOMAIN as SUBARU_DOMAIN, SubaruDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru binary_sensors by config_entry."""
    controller = hass.data[SUBARU_DOMAIN][config_entry.entry_id]["controller"]
    entities = []
    for device in hass.data[SUBARU_DOMAIN][config_entry.entry_id]["devices"]["switch"]:
        if device.type == "charger switch":
            entities.append(ChargerSwitch(device, controller, config_entry))
        if device.type == "location switch":
            entities.append(LocateSwitch(device, controller, config_entry))
        # entities.append(UpdateSwitch(device, controller, config_entry))
    async_add_entities(entities, True)


class ChargerSwitch(SubaruDevice, SwitchEntity):
    """Representation of a Subaru charger switch."""

    def __init__(self, subaru_device, controller, config_entry):
        """Initialise of the switch."""
        self._state = None
        super().__init__(subaru_device, controller, config_entry)

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Start charging: %s", self._name)
        await self.subaru_device.start_charge()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.debug("Stop charging not supported by Subaru API")

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._state == STATE_ON

    async def async_update(self):
        """Update the state of the switch."""
        _LOGGER.debug("Updating state for: %s", self._name)
        await super().async_update()
        self._state = STATE_ON if self.subaru_device.is_charging() else STATE_OFF


class UpdateSwitch(SubaruDevice, SwitchEntity):
    """Representation of a Subaru update switch."""

    def __init__(self, subaru_device, controller, config_entry):
        """Initialise the switch."""
        self._state = None
        subaru_device.type = "update switch"
        super().__init__(subaru_device, controller, config_entry)
        self._name = self._name.replace("charger", "update")
        self.vin = subaru_device._vin

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Enable updates: %s %s", self._name, self.vin)
        self.controller.set_updates(self.vin, True)

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.debug("Disable updates: %s %s", self._name, self.vin)
        self.controller.set_updates(self.vin, False)

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._state

    async def async_update(self):
        """Update the state of the switch."""
        _LOGGER.debug("Updating state for: %s %s", self._name, self.vin)
        await super().async_update()
        self._state = bool(self.controller.get_updates(self.vin))


class LocateSwitch(SubaruDevice, SwitchEntity):
    """Representation of a Subaru locate switch."""

    def __init__(self, subaru_device, controller, config_entry):
        """Initialise the switch."""
        self._state = STATE_OFF
        subaru_device.type = "location switch"
        super().__init__(subaru_device, controller, config_entry)
        self.vin = subaru_device._vin
        self.subaru_device = subaru_device

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Locate Vehicle: %s %s", self._name, self.vin)
        self._state = STATE_ON
        await self.subaru_device.locate()
        await self.async_turn_off()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        self._state = STATE_OFF

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._state

    async def async_update(self):
        """Update the state of the switch."""
        await super().async_update()
