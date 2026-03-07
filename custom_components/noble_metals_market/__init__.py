"""Noble Metals Market integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, PRICES_URL, CURRENCY_URL, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Noble Metals Market from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "price_data": {},
        "currency_data": {},
        "sensors": [],
        "unsub": None,
    }

    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    # Initial fetch
    await _fetch_and_store(hass, entry.entry_id)

    # Periodic scheduler
    async def _scheduled_update(_now=None):
        await _fetch_and_store(hass, entry.entry_id)
        for sensor in hass.data[DOMAIN][entry.entry_id].get("sensors", []):
            sensor.update_from_cache()
            sensor.async_write_ha_state()

    hass.data[DOMAIN][entry.entry_id]["unsub"] = async_track_time_interval(
        hass, _scheduled_update, timedelta(seconds=update_interval)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload service
    async def _handle_reload(_call: ServiceCall) -> None:
        await hass.config_entries.async_reload(entry.entry_id)

    if not hass.services.has_service(DOMAIN, "reload"):
        hass.services.async_register(DOMAIN, "reload", _handle_reload)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unsub = hass.data[DOMAIN][entry.entry_id].get("unsub")
    if unsub:
        unsub()

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def _fetch_and_store(hass: HomeAssistant, entry_id: str) -> None:
    """Fetch prices and exchange rates, store in hass.data."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PRICES_URL) as resp:
                hass.data[DOMAIN][entry_id]["price_data"] = await resp.json(content_type=None)
            async with session.get(CURRENCY_URL) as resp:
                payload = await resp.json(content_type=None)
                hass.data[DOMAIN][entry_id]["currency_data"] = payload.get("eur", {})
        _LOGGER.debug("Noble Metals Market: data fetched OK")
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Noble Metals Market: fetch failed: %s", err)
