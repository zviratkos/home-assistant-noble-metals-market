"""Config flow for Noble Metals Market."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode, SelectOptionDict

from .const import (
    DOMAIN,
    CURRENCY_URL,
    METALS,
    UNITS,
    METAL_LABELS,
    UNIT_LABELS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_DECIMALS,
    CONF_SYMBOLS,
    CONF_DECIMALS,
    CONF_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def _fetch_currencies() -> list[str]:
    """Fetch available currency codes from the API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CURRENCY_URL) as resp:
                data = await resp.json(content_type=None)
                currencies = sorted(data.get("eur", {}).keys())
                return [c.upper() for c in currencies if len(c) == 3]
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not fetch currencies: %s", err)
        return ["USD", "EUR", "GBP", "CZK", "CHF"]


def _build_symbol_options(currencies: list[str]) -> dict[str, str]:
    """Build all valid metal/unit/currency combinations as {value: label}."""
    options = {}
    for metal in METALS:
        for unit in UNITS:
            for currency in currencies:
                key = f"{metal}_{unit}_{currency.lower()}"
                label = f"{METAL_LABELS[metal]} {UNIT_LABELS[unit]} / {currency}"
                options[key] = label
    return options


class NobleMetalsMarketConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Noble Metals Market."""

    VERSION = 1

    def __init__(self):
        self._currencies: list[str] = []
        self._selected_currencies: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Step 1: Select currencies (fetched live from API)."""
        self._currencies = await _fetch_currencies()

        if user_input is not None:
            self._selected_currencies = sorted(user_input["currencies"])
            return await self.async_step_symbols()

        currency_options = {c: c for c in self._currencies}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("currencies"): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=k, label=v) for k, v in currency_options.items()],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            ),
            }),
            description_placeholders={
                "count": str(len(self._currencies)),
            },
        )

    async def async_step_symbols(self, user_input: dict[str, Any] | None = None):
        """Step 2: Select specific metal/unit/currency combinations."""
        symbol_options = _build_symbol_options(self._selected_currencies)

        if user_input is not None:
            self._symbols = user_input[CONF_SYMBOLS]
            return await self.async_step_settings()

        return self.async_show_form(
            step_id="symbols",
            data_schema=vol.Schema({
                vol.Required(CONF_SYMBOLS): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=k, label=v) for k, v in symbol_options.items()],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            ),
            }),
        )

    async def async_step_settings(self, user_input: dict[str, Any] | None = None):
        """Step 3: Update interval and decimals."""
        if user_input is not None:
            return self.async_create_entry(
                title="Noble Metals Market",
                data={
                    CONF_SYMBOLS: self._symbols,
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                    CONF_DECIMALS: user_input[CONF_DECIMALS],
                },
            )

        return self.async_show_form(
            step_id="settings",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=60, max=86400)
                ),
                vol.Required(CONF_DECIMALS, default=DEFAULT_DECIMALS): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=10)
                ),
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NobleMetalsMarketOptionsFlow(config_entry)


class NobleMetalsMarketOptionsFlow(config_entries.OptionsFlow):
    """Handle options (reconfigure existing entry)."""

    def __init__(self, config_entry):
        self._entry = config_entry
        self._currencies: list[str] = []
        self._selected_currencies: list[str] = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Step 1: Re-select currencies."""
        self._currencies = await _fetch_currencies()

        # Pre-select currencies already in use
        existing_symbols = self._entry.data.get(CONF_SYMBOLS, [])
        existing_currencies = sorted({
            s.split("_")[-1].upper() for s in existing_symbols
        })

        if user_input is not None:
            self._selected_currencies = sorted(user_input["currencies"])
            return await self.async_step_symbols()

        currency_options = {c: c for c in self._currencies}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("currencies", default=existing_currencies): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=k, label=v) for k, v in currency_options.items()],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            ),
            }),
        )

    async def async_step_symbols(self, user_input: dict[str, Any] | None = None):
        """Step 2: Re-select symbols."""
        symbol_options = _build_symbol_options(self._selected_currencies)
        existing_symbols = [
            s for s in self._entry.data.get(CONF_SYMBOLS, [])
            if s in symbol_options
        ]

        if user_input is not None:
            self._symbols = user_input[CONF_SYMBOLS]
            return await self.async_step_settings()

        return self.async_show_form(
            step_id="symbols",
            data_schema=vol.Schema({
                vol.Required(CONF_SYMBOLS, default=existing_symbols): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=k, label=v) for k, v in symbol_options.items()],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            ),
            }),
        )

    async def async_step_settings(self, user_input: dict[str, Any] | None = None):
        """Step 3: Update interval and decimals."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SYMBOLS: self._symbols,
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                    CONF_DECIMALS: user_input[CONF_DECIMALS],
                },
            )

        return self.async_show_form(
            step_id="settings",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=self._entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
                vol.Required(
                    CONF_DECIMALS,
                    default=self._entry.data.get(CONF_DECIMALS, DEFAULT_DECIMALS)
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
            }),
        )

