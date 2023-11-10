"""Remote vehicle services for Subaru integration."""
import logging
from typing import Any

from subarulink.controller import Controller
from subarulink.exceptions import SubaruException

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    EVENT_SUBARU_COMMAND_FAIL,
    EVENT_SUBARU_COMMAND_SENDING,
    EVENT_SUBARU_COMMAND_SUCCESS,
    SERVICE_UNLOCK,
    VEHICLE_NAME,
    VEHICLE_VIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_call_remote_service(
    hass: HomeAssistant,
    controller: Controller,
    cmd: str,
    vehicle_info: dict,
    arg: Any | None = None,
) -> None:
    """Execute subarulink remote command."""
    car_name = vehicle_info[VEHICLE_NAME]
    vin = vehicle_info[VEHICLE_VIN]

    _LOGGER.debug("Sending %s command command to %s", cmd, car_name)
    hass.bus.async_fire(
        EVENT_SUBARU_COMMAND_SENDING, {"command": cmd, "car_name": car_name}
    )

    success = False
    err_msg = ""
    try:
        if cmd == SERVICE_UNLOCK:
            success = await getattr(controller, cmd)(vin, arg)
        else:
            success = await getattr(controller, cmd)(vin)
    except SubaruException as err:
        err_msg = err.message

    if success:
        _LOGGER.debug("%s command successfully completed for %s", cmd, car_name)
        hass.bus.async_fire(
            EVENT_SUBARU_COMMAND_SUCCESS, {"command": cmd, "car_name": car_name}
        )
        return

    hass.bus.async_fire(
        EVENT_SUBARU_COMMAND_FAIL,
        {"command": cmd, "car_name": car_name, "message": err_msg},
    )
    raise HomeAssistantError(f"Service {cmd} failed for {car_name}: {err_msg}")
