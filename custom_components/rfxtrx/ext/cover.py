"""Config flow for RFXtrx stateful blinds."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import ATTR_STATE
from homeassistant.helpers import entity_platform

from ..const import (
    CONF_VENETIAN_BLIND_MODE,
    CONST_VENETIAN_BLIND_MODE_EU,
    CONST_VENETIAN_BLIND_MODE_US,
)
from .const import (
    CONF_STATE_SUPPORT,
    DEF_STATE_SUPPORT,
    DEVICE_PACKET_SUBTYPE_BLINDST19,
    DEVICE_PACKET_SUBTYPE_LIGHTING2_AC,
    DEVICE_PACKET_TYPE_BLINDS1,
    DEVICE_PACKET_TYPE_LIGHTING2,
    DEVICE_PACKET_TYPE_RFY,
    SVC_UPDATE_POSITION,
)
from .louvolite_vogue_blind import LouvoliteVogueBlind
from .somfy_roller_blind import SomfyRollerBlind
from .somfy_venetian_blind import SomfyVenetianBlind
from .timed_shutter_cover import TimedShutterCover

_LOGGER = logging.getLogger(__name__)


def create_cover_entity(
    device, device_id, entity_info, event=None
) -> CoverEntity | None:
    """Create a cover entitity of any of our supported types."""
    _LOGGER.debug("Device ID %s", device_id)
    _LOGGER.debug("Info %s", entity_info)

    stateSupport = entity_info.get(CONF_STATE_SUPPORT, DEF_STATE_SUPPORT)
    _LOGGER.debug("State support = %s", stateSupport)

    if stateSupport:
        if (
            int(device_id[0], 16) == DEVICE_PACKET_TYPE_BLINDS1
            and int(device_id[1], 16) == DEVICE_PACKET_SUBTYPE_BLINDST19
        ):
            _LOGGER.info(
                "Detected a Louvolite Vogue vertical blind - let's go stateful!"
            )
            return LouvoliteVogueBlind(
                device=device, device_id=device_id, entity_info=entity_info, event=event
            )
        if int(device_id[0], 16) == DEVICE_PACKET_TYPE_RFY:
            venetian_blind_mode = entity_info.get(CONF_VENETIAN_BLIND_MODE)
            if venetian_blind_mode in (
                CONST_VENETIAN_BLIND_MODE_US,
                CONST_VENETIAN_BLIND_MODE_EU,
            ):
                _LOGGER.info("Detected a Somfy RFY venetian blind - let's go stateful!")
                return SomfyVenetianBlind(
                    device=device,
                    device_id=device_id,
                    entity_info=entity_info,
                    event=event,
                )
            _LOGGER.info("Detected a Somfy RFY roller blind - let's go stateful!")
            return SomfyRollerBlind(
                device=device,
                device_id=device_id,
                entity_info=entity_info,
                event=event,
            )
        if (
            int(device_id[0], 16) == DEVICE_PACKET_TYPE_LIGHTING2
            and int(device_id[1], 16) == DEVICE_PACKET_SUBTYPE_LIGHTING2_AC
        ):
            _LOGGER.info("Detected a Lighting2 AC blinds - let's go stateful!")
            return TimedShutterCover(
                device=device, device_id=device_id, entity_info=entity_info, event=event
            )
    return None


async def async_define_sync_services() -> None:
    """Define sync services for covers."""
    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SVC_UPDATE_POSITION,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Required(ATTR_TILT_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Required(ATTR_STATE, default="CLOSED"): str,
        },
        "async_update_cover_position",
        [CoverEntityFeature.SET_POSITION | CoverEntityFeature.SET_TILT_POSITION],
    )
