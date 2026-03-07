"""Constants for Noble Metals Market integration."""

DOMAIN = "noble_metals_market"

PRICES_URL = "https://api.edelmetalle.de/public.json"
CURRENCY_URL = "https://latest.currency-api.pages.dev/v1/currencies/eur.json"

DEFAULT_UPDATE_INTERVAL = 300
DEFAULT_DECIMALS = 4

METALS = ["gold", "silver", "platinum", "palladium"]
UNITS = ["toz", "g", "kg"]

METAL_LABELS = {
    "gold": "Gold",
    "silver": "Silver",
    "platinum": "Platinum",
    "palladium": "Palladium",
}

UNIT_LABELS = {
    "toz": "troy oz",
    "g": "gram",
    "kg": "kilogram",
}

METAL_API_KEYS = {
    # metal -> (eur_field, usd_field)
    "gold":      ("gold_eur",      "gold_usd"),
    "silver":    ("silber_eur",    "silber_usd"),
    "platinum":  ("platin_eur",    "platin_usd"),
    "palladium": ("palladium_eur", "palladium_usd"),
}

UNIT_MULTIPLIERS = {
    "toz": 1.0,
    "g":   1 / 31.1035,
    "kg":  1000 / 31.1035,
}

# Config entry data keys
CONF_SYMBOLS = "symbols"
CONF_DECIMALS = "decimals"
CONF_UPDATE_INTERVAL = "update_interval"
