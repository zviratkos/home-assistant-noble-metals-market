# Noble Metals Market

## Instalation
### Manual
Copy `custom_components/noble_metals_market/` to `config/custom_components/` and restart HA.
### Automatic
Add custom repo to HACS and search for Noble Metal Markets

## Configuration
UI: Settings → Devices and services → Add integration → Noble Metals Market

Steps Kroky:
1. **Choose currency** — read live z API, select currency (CZK, USD, EUR, ...)
2. **Select combinations** — check combinations (Gold troy oz / CZK, Silver gram / USD, ...)
3. **Settings** — refresh interval (min. 60s) and number of decimal places 

## Reload
Settings → Devices and services → Noble Metals Market → Reload
or: `service: noble_metals_market.reload`
