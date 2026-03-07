"""Sensor platform for Noble Metals Market."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    METAL_API_KEYS,
    UNIT_MULTIPLIERS,
    METAL_LABELS,
    UNIT_LABELS,
    CONF_SYMBOLS,
    CONF_DECIMALS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    conf = {**entry.data, **entry.options}
    symbols = conf[CONF_SYMBOLS]
    decimals = conf[CONF_DECIMALS]

    sensors = []
    for symbol in symbols:
        parts = symbol.split("_")  # e.g. gold_toz_usd -> [gold, toz, usd]
        if len(parts) != 3:
            _LOGGER.warning("Invalid symbol format: %s", symbol)
            continue
        metal, unit, currency = parts[0], parts[1], parts[2].upper()
        sensors.append(NobleMetalSensor(hass, entry, symbol, metal, unit, currency, decimals))

    hass.data[DOMAIN][entry.entry_id]["sensors"] = sensors

    # update_from_cache reads from already-fetched hass.data
    for sensor in sensors:
        sensor.update_from_cache()

    async_add_entities(sensors, update_before_add=False)


class NobleMetalSensor(SensorEntity):
    """A single precious metal price sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, hass, entry, symbol, metal, unit, currency, decimals):
        self.hass = hass
        self._entry = entry
        self._symbol = symbol
        self._metal = metal
        self._unit = unit
        self._currency = currency
        self._decimals = decimals

        metal_label = METAL_LABELS.get(metal, metal.capitalize())
        unit_label = UNIT_LABELS.get(unit, unit)

        self._attr_name = f"{metal_label} {unit_label} / {currency}"
        self._attr_unique_id = f"{entry.entry_id}_{symbol}"
        self._attr_native_unit_of_measurement = currency
        self._attr_icon = {
            "USD": "mdi:currency-usd",
            "EUR": "mdi:currency-eur",
            "GBP": "mdi:currency-gbp",
        }.get(currency, "mdi:cash")
        self._attr_native_value = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Noble Metals Market",
            model="Cloud API",
        )

    @property
    def extra_state_attributes(self):
        return {
            "metal": self._metal,
            "unit": self._unit,
            "currency": self._currency,
        }

    def update_from_cache(self) -> None:
        """Compute value from data cached in hass.data."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {})
        price_data = entry_data.get("price_data", {})
        currency_data = entry_data.get("currency_data", {})

        if not price_data:
            return

        try:
            eur_field, usd_field = METAL_API_KEYS[self._metal]
            multiplier = UNIT_MULTIPLIERS[self._unit]
            currency = self._currency

            if currency == "EUR":
                base_toz = float(price_data[eur_field])
            elif currency == "USD":
                base_toz = float(price_data[usd_field])
            else:
                rate = float(currency_data.get(currency.lower(), 0))
                if rate == 0:
                    _LOGGER.warning("No exchange rate for %s", currency)
                    return
                base_toz = float(price_data[eur_field]) * rate

            self._attr_native_value = round(base_toz * multiplier, self._decimals)

        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.warning("Failed to compute value for %s: %s", self._symbol, err)

    async def async_update(self) -> None:
        """Manual update — re-reads cache."""
        self.update_from_cache()
