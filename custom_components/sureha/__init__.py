"""The surepetcare integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from random import choice
from typing import Any

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from surepy import Surepy
from surepy.entities import SurepyEntity
from surepy.enums import EntityType, Location, LockState
from surepy.exceptions import SurePetcareAuthenticationError, SurePetcareError
import voluptuous as vol

# pylint: disable=import-error
from .const import (
    ATTR_FLAP_ID,
    ATTR_LOCK_STATE,
    ATTR_PET_ID,
    ATTR_VOLTAGE_FULL,
    ATTR_VOLTAGE_LOW,
    ATTR_WHERE,
    DOMAIN,
    SERVICE_PET_LOCATION,
    SERVICE_SET_LOCK_STATE,
    SPC,
    SURE_API_TIMEOUT,
    SURE_BATT_VOLTAGE_FULL,
    SURE_BATT_VOLTAGE_LOW,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER, Platform.SENSOR]
SCAN_INTERVAL = timedelta(minutes=3)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            vol.All(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            )
        )
    },
    extra=vol.ALLOW_EXTRA,
)

CATS = [
    "/ᐠ｡▿｡ᐟ\\*ᵖᵘʳʳ",
    "/ᐠ_ꞈ_ᐟ\\ɴʏᴀ~",
    "/ᐠ ._. ᐟ\\ﾉ",
    "/ᐠ. ｡.ᐟ\\ᵐᵉᵒʷˎˊ",
    "ᶠᵉᵉᵈ ᵐᵉ /ᐠ-ⱉ-ᐟ\\ﾉ",
    "(≗ᆽ ≗)ﾉ",
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up."""

    hass.data.setdefault(DOMAIN, {})

    # set option defaults
    if not entry.options:
        hass.config_entries.async_update_entry(
            entry,
            options={
                ATTR_VOLTAGE_FULL: SURE_BATT_VOLTAGE_FULL,
                ATTR_VOLTAGE_LOW: SURE_BATT_VOLTAGE_LOW,
            },
        )

    try:
        surepy = Surepy(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            auth_token=entry.data[CONF_TOKEN] if CONF_TOKEN in entry.data else None,
            api_timeout=SURE_API_TIMEOUT,
            session=async_get_clientsession(hass),
        )
    except SurePetcareAuthenticationError:
        _LOGGER.error(
            "🐾 \x1b[38;2;255;26;102m·\x1b[0m unable to auth. to surepetcare.io: wrong credentials"
        )
        return False
    except SurePetcareError as error:
        _LOGGER.error(
            "🐾 \x1b[38;2;255;26;102m·\x1b[0m unable to connect to surepetcare.io: %s",
            error,
        )
        return False

    spc = SurePetcareAPI(hass, entry, surepy)

    async def async_update_data():

        try:
            async with async_timeout.timeout(20):
                return await spc.surepy.get_entities(refresh=True)

        except SurePetcareAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except SurePetcareError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    spc.coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sureha_sensors",
        update_method=async_update_data,
        update_interval=timedelta(seconds=150),
    )

    await spc.coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][SPC] = spc

    return await spc.async_setup()


class SurePetcareAPI:
    """Define a generic Sure Petcare object."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, surepy: Surepy
    ) -> None:
        """Initialize the Sure Petcare object."""

        self.coordinator: DataUpdateCoordinator

        self.hass = hass
        self.config_entry = config_entry
        self.surepy = surepy

        self.states: dict[int, Any] = {}

    async def set_pet_location(self, pet_id: int, location: Location) -> None:
        """Update the lock state of a flap."""

        await self.surepy.sac.set_pet_location(pet_id, location)

    async def set_lock_state(self, flap_id: int, state: str) -> None:
        """Update the lock state of a flap."""

        lock_states = {
            LockState.UNLOCKED.name.lower(): self.surepy.sac.unlock,
            LockState.LOCKED_IN.name.lower(): self.surepy.sac.lock_in,
            LockState.LOCKED_OUT.name.lower(): self.surepy.sac.lock_out,
            LockState.LOCKED_ALL.name.lower(): self.surepy.sac.lock,
        }

        await lock_states[state
