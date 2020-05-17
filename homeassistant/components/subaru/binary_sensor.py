"""Support for Subaru binary sensor."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from . import DOMAIN as SUBARU_DOMAIN, SubaruDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Subaru binary_sensors by config_entry."""
    async_add_entities(
        [
            SubaruBinarySensor(
                device,
                hass.data[SUBARU_DOMAIN][config_entry.entry_id]["controller"],
                "connectivity",
                config_entry,
            )
            for device in hass.data[SUBARU_DOMAIN][config_entry.entry_id]["devices"][
                "binary_sensor"
            ]
        ],
        True,
    )


class SubaruBinarySensor(SubaruDevice, BinarySensorEntity):
    """Implement an Subaru binary sensor for charger."""

    def __init__(self, subaru_device, controller, sensor_type, config_entry):
        """Initialise of a Subaru binary sensor."""
        super().__init__(subaru_device, controller, config_entry)
        self._state = False
        self._sensor_type = sensor_type

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._state

    async def async_update(self):
        """Update the state of the device."""
        _LOGGER.debug("Updating sensor: %s", self._name)
        await super().async_update()
        self._state = self.subaru_device.get_value()
