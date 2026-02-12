"""Support for RFXtrx timed shutter covers."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import RFXtrx as rfxtrxmod

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import ATTR_MANUFACTURER, ATTR_MODEL
from homeassistant.core import callback

from .. import DeviceTuple
from ..entity import RfxtrxCommandEntity
from .const import (
    CONF_CLOSE_SECONDS,
    CONF_OPEN_SECONDS,
    DEF_CLOSE_SECONDS,
    DEF_OPEN_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

MANUFACTURER_NAME = "Timed Shutter"
DEVICE_TYPE = "Timed Shutter Blind"


class TimedShutterCover(RfxtrxCommandEntity, CoverEntity):
    """Representation of a Timed Shutter RFXtrx cover."""

    _device: rfxtrxmod.LightingDevice

    def __init__(
        self,
        device: rfxtrxmod.RFXtrxDevice,
        device_id: DeviceTuple,
        entity_info: dict[str, Any],
        event: rfxtrxmod.RFXtrxEvent = None,
    ) -> None:
        """Initialize the Timed Shutter RFXtrx cover device."""
        device.type_string = DEVICE_TYPE

        super().__init__(device, device_id, event)

        self._attr_device_info.update(
            {ATTR_MANUFACTURER: MANUFACTURER_NAME, ATTR_MODEL: DEVICE_TYPE}
        )

        self._attr_is_closed: bool | None = True
        self._attr_current_cover_position = 0
        self._attr_device_class = CoverDeviceClass.SHUTTER

        self._attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )

        self._myattr_close_secs = entity_info.get(CONF_CLOSE_SECONDS, DEF_CLOSE_SECONDS)
        self._myattr_open_secs = entity_info.get(CONF_OPEN_SECONDS, DEF_OPEN_SECONDS)

        self._move_task: asyncio.Task | None = None
        self._target_position: int | None = None

    async def async_added_to_hass(self) -> None:
        """Restore device state."""
        await super().async_added_to_hass()

        if self._event is None:
            old_state = await self.async_get_last_state()
            if old_state is not None:
                self._attr_current_cover_position = old_state.attributes.get(
                    "current_position", 0
                )
                self._attr_is_closed = self._attr_current_cover_position == 0

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening or not."""
        return self._attr_is_opening

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing or not."""
        return self._attr_is_closing

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Move the cover up."""
        await self._async_handle_move(100, kwargs.get("skip_send", False))

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Move the cover down."""
        await self._async_handle_move(0, kwargs.get("skip_send", False))

    async def _async_handle_move(self, position: int, skip_send: bool) -> None:
        """Internal move handler to check state."""
        moving_up = position > self._attr_current_cover_position
        if (moving_up and self.is_opening) or (not moving_up and self.is_closing):
            _LOGGER.debug("Already moving in that direction, toggle to stop")
            await self.async_stop_cover(skip_send=skip_send)
            return

        _LOGGER.debug("Moving cover to %s (skip_send=%s)", position, skip_send)
        await self._async_move_to(position, skip_send)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        if not self._move_task:
            return

        skip_send = kwargs.get("skip_send", False)
        was_opening = self._attr_is_opening

        if self._move_task:
            self._move_task.cancel()
            self._move_task = None

        self._attr_is_opening = False
        self._attr_is_closing = False
        self.async_write_ha_state()

        if not skip_send:
            _LOGGER.debug("Stopping cover by repeating last command")
            if was_opening:
                await self._async_send(self._device.send_on)
            else:
                await self._async_send(self._device.send_off)
        else:
            _LOGGER.debug("Stopping cover (remote already sent command)")

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        if ATTR_POSITION in kwargs:
            await self._async_move_to(kwargs[ATTR_POSITION], False)

    async def _async_move_to(self, position: int, skip_send: bool) -> None:
        """Move cover to a specific position."""
        if position == self._attr_current_cover_position:
            return

        if self._move_task:
            self._move_task.cancel()

        self._target_position = position
        self._move_task = asyncio.create_task(self._async_move_task(skip_send))

    async def _async_move_task(self, skip_send: bool) -> None:
        """Update position while moving."""
        start_pos = self._attr_current_cover_position
        target_pos = self._target_position

        moving_up = target_pos > start_pos
        self._attr_is_opening = moving_up
        self._attr_is_closing = not moving_up

        # Send physical command
        if not skip_send:
            if moving_up:
                await self._async_send(self._device.send_on)
                duration = self._myattr_open_secs
            else:
                await self._async_send(self._device.send_off)
                duration = self._myattr_close_secs
        else:
            duration = self._myattr_open_secs if moving_up else self._myattr_close_secs

        total_distance = abs(target_pos - start_pos)
        # Time to move the distance
        total_time = (total_distance / 100.0) * duration

        start_time = time.time()

        _LOGGER.debug(
            "Moving from %s to %s (duration %s)", start_pos, target_pos, total_time
        )

        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= total_time:
                    break

                # Update position for UI
                progress = elapsed / total_time
                if moving_up:
                    self._attr_current_cover_position = int(
                        start_pos + progress * total_distance
                    )
                else:
                    self._attr_current_cover_position = int(
                        start_pos - progress * total_distance
                    )

                self.async_write_ha_state()
                await asyncio.sleep(1)

            # Finished
            self._attr_current_cover_position = target_pos
            self._attr_is_closed = self._attr_current_cover_position == 0

            # Send stop command if at intermediate position
            if 0 < target_pos < 100:
                _LOGGER.debug("Stopping cover at intermediate position")
                if moving_up:
                    await self._async_send(self._device.send_on)
                else:
                    await self._async_send(self._device.send_off)

        except asyncio.CancelledError:
            _LOGGER.debug("Movement cancelled")
            # Calculate final position based on elapsed time
            elapsed = time.time() - start_time
            progress = min(elapsed / total_time, 1.0)
            if moving_up:
                self._attr_current_cover_position = int(
                    start_pos + progress * total_distance
                )
            else:
                self._attr_current_cover_position = int(
                    start_pos - progress * total_distance
                )
            raise
        finally:
            self._attr_is_opening = False
            self._attr_is_closing = False
            self._move_task = None
            self.async_write_ha_state()

    def _apply_event(self, event: rfxtrxmod.RFXtrxEvent) -> None:
        """Apply command from rfxtrx (remote control)."""
        assert isinstance(event, rfxtrxmod.ControlEvent)
        super()._apply_event(event)

    @callback
    def _handle_event(
        self, event: rfxtrxmod.RFXtrxEvent, device_id: DeviceTuple
    ) -> None:
        """Handle incoming event from gateway."""
        if device_id != self._device_id:
            return

        # Map remote commands to actions
        # On typically opens, Off typically closes
        command = event.values.get("Command")
        if command == "On":
            self.hass.async_create_task(self.async_open_cover(skip_send=True))
        elif command == "Off":
            self.hass.async_create_task(self.async_close_cover(skip_send=True))

        self.async_write_ha_state()
