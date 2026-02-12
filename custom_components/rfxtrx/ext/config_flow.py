"""Config flow for RFXtrx stateful blinds."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.helpers.typing import VolDictType

from .const import (
    CONF_CLOSE_SECONDS,
    CONF_COLOUR_ICON,
    CONF_CUSTOM_ICON,
    CONF_OPEN_SECONDS,
    CONF_PARTIAL_CLOSED,
    CONF_ROLLER_MID_ON_CLOSE,
    CONF_SIGNAL_REPETITIONS,
    CONF_SIGNAL_REPETITIONS_DELAY_MS,
    CONF_STATE_SUPPORT,
    CONF_STEPS_MID,
    CONF_SUPPORTS_MID,
    CONF_SYNC_MID,
    CONF_SYNC_SECONDS,
    CONF_TILT_CLOSED_ICON,
    CONF_TILT_LIFTED_ICON,
    CONF_TILT_OPEN_ICON,
    CONF_TILT_POS1_MS,
    CONF_TILT_POS2_MS,
    DEF_CLOSE_SECONDS,
    DEF_COLOUR_ICON,
    DEF_CUSTOM_ICON,
    DEF_OPEN_SECONDS,
    DEF_PARTIAL_CLOSED,
    DEF_ROLLER_MID_ON_CLOSE,
    DEF_SIGNAL_REPETITIONS,
    DEF_SIGNAL_REPETITIONS_DELAY_MS,
    DEF_STATE_SUPPORT,
    DEF_STEPS_MID,
    DEF_SUPPORTS_MID,
    DEF_SYNC_MID,
    DEF_SYNC_SECONDS,
    DEF_TILT_CLOSED_ICON,
    DEF_TILT_LIFTED_ICON,
    DEF_TILT_OPEN_ICON,
    DEF_TILT_POS1_MS,
    DEF_TILT_POS2_MS,
    DEVICE_PACKET_SUBTYPE_BLINDST19,
    DEVICE_PACKET_SUBTYPE_LIGHTING2_AC,
    DEVICE_PACKET_TYPE_BLINDS1,
    DEVICE_PACKET_TYPE_LIGHTING2,
    DEVICE_PACKET_TYPE_RFY,
)

_LOGGER = logging.getLogger(__name__)


def update_device_options(device: dict[str, Any], user_input: dict[str, Any]) -> None:
    """Update device options from user input."""
    device[CONF_STATE_SUPPORT] = user_input.get(CONF_STATE_SUPPORT, DEF_STATE_SUPPORT)
    device[CONF_SUPPORTS_MID] = user_input.get(CONF_SUPPORTS_MID, DEF_SUPPORTS_MID)
    device[CONF_SYNC_MID] = user_input.get(CONF_SYNC_MID, DEF_SYNC_MID)
    device[CONF_STEPS_MID] = user_input.get(CONF_STEPS_MID, DEF_STEPS_MID)
    device[CONF_OPEN_SECONDS] = user_input.get(CONF_OPEN_SECONDS, DEF_OPEN_SECONDS)
    device[CONF_CLOSE_SECONDS] = user_input.get(CONF_CLOSE_SECONDS, DEF_CLOSE_SECONDS)
    device[CONF_SYNC_SECONDS] = user_input.get(CONF_SYNC_SECONDS, DEF_SYNC_SECONDS)
    device[CONF_TILT_POS1_MS] = user_input.get(CONF_TILT_POS1_MS, DEF_TILT_POS1_MS)
    device[CONF_TILT_POS2_MS] = user_input.get(CONF_TILT_POS2_MS, DEF_TILT_POS2_MS)
    device[CONF_CUSTOM_ICON] = user_input.get(CONF_CUSTOM_ICON, DEF_CUSTOM_ICON)
    device[CONF_COLOUR_ICON] = user_input.get(CONF_COLOUR_ICON, DEF_COLOUR_ICON)
    device[CONF_PARTIAL_CLOSED] = user_input.get(
        CONF_PARTIAL_CLOSED, DEF_PARTIAL_CLOSED
    )
    device[CONF_SIGNAL_REPETITIONS] = user_input.get(
        CONF_SIGNAL_REPETITIONS, DEF_SIGNAL_REPETITIONS
    )
    device[CONF_SIGNAL_REPETITIONS_DELAY_MS] = user_input.get(
        CONF_SIGNAL_REPETITIONS_DELAY_MS, DEF_SIGNAL_REPETITIONS_DELAY_MS
    )
    device[CONF_ROLLER_MID_ON_CLOSE] = user_input.get(
        CONF_ROLLER_MID_ON_CLOSE, DEF_ROLLER_MID_ON_CLOSE
    )
    device[CONF_TILT_OPEN_ICON] = user_input.get(
        CONF_TILT_OPEN_ICON, DEF_TILT_OPEN_ICON
    )
    device[CONF_TILT_CLOSED_ICON] = user_input.get(
        CONF_TILT_CLOSED_ICON, DEF_TILT_CLOSED_ICON
    )
    device[CONF_TILT_LIFTED_ICON] = user_input.get(
        CONF_TILT_LIFTED_ICON, DEF_TILT_LIFTED_ICON
    )


def update_data_schema(data_schema: VolDictType, device_object, device_data) -> None:
    """Update data schema with device specific options."""
    if device_object.device.packettype == DEVICE_PACKET_TYPE_RFY:
        # Add Somfy RFY venetian tilt options
        data_schema.update(
            {
                vol.Optional(
                    CONF_STATE_SUPPORT,
                    default=device_data.get(CONF_STATE_SUPPORT, DEF_STATE_SUPPORT),
                ): bool,
                vol.Optional(
                    CONF_SIGNAL_REPETITIONS,
                    default=device_data.get(
                        CONF_SIGNAL_REPETITIONS, DEF_SIGNAL_REPETITIONS
                    ),
                ): int,
                vol.Optional(
                    CONF_SIGNAL_REPETITIONS_DELAY_MS,
                    default=device_data.get(
                        CONF_SIGNAL_REPETITIONS_DELAY_MS,
                        DEF_SIGNAL_REPETITIONS_DELAY_MS,
                    ),
                ): int,
                vol.Optional(
                    CONF_OPEN_SECONDS,
                    default=device_data.get(CONF_OPEN_SECONDS, DEF_OPEN_SECONDS),
                ): int,
                vol.Optional(
                    CONF_CLOSE_SECONDS,
                    default=device_data.get(CONF_CLOSE_SECONDS, DEF_CLOSE_SECONDS),
                ): int,
                vol.Optional(
                    CONF_SYNC_SECONDS,
                    default=device_data.get(CONF_SYNC_SECONDS, DEF_SYNC_SECONDS),
                ): int,
                vol.Optional(
                    CONF_TILT_POS1_MS,
                    default=device_data.get(CONF_TILT_POS1_MS, DEF_TILT_POS1_MS),
                ): int,
                vol.Optional(
                    CONF_TILT_POS2_MS,
                    default=device_data.get(CONF_TILT_POS2_MS, DEF_TILT_POS2_MS),
                ): int,
                vol.Optional(
                    CONF_CUSTOM_ICON,
                    default=device_data.get(CONF_CUSTOM_ICON, DEF_CUSTOM_ICON),
                ): bool,
                vol.Optional(
                    CONF_COLOUR_ICON,
                    default=device_data.get(CONF_COLOUR_ICON, DEF_COLOUR_ICON),
                ): bool,
                vol.Optional(
                    CONF_TILT_OPEN_ICON,
                    default=device_data.get(CONF_TILT_OPEN_ICON, DEF_TILT_OPEN_ICON),
                ): str,
                vol.Optional(
                    CONF_TILT_CLOSED_ICON,
                    default=device_data.get(
                        CONF_TILT_CLOSED_ICON, DEF_TILT_CLOSED_ICON
                    ),
                ): str,
                vol.Optional(
                    CONF_TILT_LIFTED_ICON,
                    default=device_data.get(
                        CONF_TILT_LIFTED_ICON, DEF_TILT_LIFTED_ICON
                    ),
                ): str,
                vol.Optional(
                    CONF_PARTIAL_CLOSED,
                    default=device_data.get(CONF_PARTIAL_CLOSED, DEF_PARTIAL_CLOSED),
                ): bool,
                vol.Optional(
                    CONF_ROLLER_MID_ON_CLOSE,
                    default=device_data.get(
                        CONF_ROLLER_MID_ON_CLOSE, DEF_ROLLER_MID_ON_CLOSE
                    ),
                ): bool,
            }
        )
    elif (
        device_object.device.packettype == DEVICE_PACKET_TYPE_LIGHTING2
        and device_object.device.subtype == DEVICE_PACKET_SUBTYPE_LIGHTING2_AC
    ):
        # Add Timed Shutter options for Lighting2 AC
        data_schema.update(
            {
                vol.Optional(
                    CONF_STATE_SUPPORT,
                    default=device_data.get(CONF_STATE_SUPPORT, DEF_STATE_SUPPORT),
                ): bool,
                vol.Optional(
                    CONF_OPEN_SECONDS,
                    default=device_data.get(CONF_OPEN_SECONDS, DEF_OPEN_SECONDS),
                ): int,
                vol.Optional(
                    CONF_CLOSE_SECONDS,
                    default=device_data.get(CONF_CLOSE_SECONDS, DEF_CLOSE_SECONDS),
                ): int,
                vol.Optional(
                    CONF_CUSTOM_ICON,
                    default=device_data.get(CONF_CUSTOM_ICON, DEF_CUSTOM_ICON),
                ): bool,
                vol.Optional(
                    CONF_COLOUR_ICON,
                    default=device_data.get(CONF_COLOUR_ICON, DEF_COLOUR_ICON),
                ): bool,
            }
        )
    elif (
        device_object.device.packettype == DEVICE_PACKET_TYPE_BLINDS1
        and device_object.device.subtype == DEVICE_PACKET_SUBTYPE_BLINDST19
    ):
        # Add Lovolite Vogue vertical tilt options
        data_schema.update(
            {
                vol.Optional(
                    CONF_STATE_SUPPORT,
                    default=device_data.get(CONF_STATE_SUPPORT, DEF_STATE_SUPPORT),
                ): bool,
                vol.Optional(
                    CONF_SIGNAL_REPETITIONS,
                    default=device_data.get(
                        CONF_SIGNAL_REPETITIONS, DEF_SIGNAL_REPETITIONS
                    ),
                ): int,
                vol.Optional(
                    CONF_SIGNAL_REPETITIONS_DELAY_MS,
                    default=device_data.get(
                        CONF_SIGNAL_REPETITIONS_DELAY_MS,
                        DEF_SIGNAL_REPETITIONS_DELAY_MS,
                    ),
                ): int,
                vol.Optional(
                    CONF_OPEN_SECONDS,
                    default=device_data.get(CONF_OPEN_SECONDS, DEF_OPEN_SECONDS),
                ): int,
                vol.Optional(
                    CONF_CLOSE_SECONDS,
                    default=device_data.get(CONF_CLOSE_SECONDS, DEF_CLOSE_SECONDS),
                ): int,
                vol.Optional(
                    CONF_CUSTOM_ICON,
                    default=device_data.get(CONF_CUSTOM_ICON, DEF_CUSTOM_ICON),
                ): bool,
                vol.Optional(
                    CONF_COLOUR_ICON,
                    default=device_data.get(CONF_COLOUR_ICON, DEF_COLOUR_ICON),
                ): bool,
                vol.Optional(
                    CONF_PARTIAL_CLOSED,
                    default=device_data.get(CONF_PARTIAL_CLOSED, DEF_PARTIAL_CLOSED),
                ): bool,
            }
        )
