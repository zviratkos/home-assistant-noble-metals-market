# Noble Metals Market

## Instalace
Zkopíruj `custom_components/noble_metals_market/` do `config/custom_components/` a restartuj HA.

## Konfigurace
Přes UI: Nastavení → Zařízení a služby → Přidat integraci → Noble Metals Market

### Kroky:
1. **Výběr měn** — načteno live z API, vyber co tě zajímá (CZK, USD, EUR, ...)
2. **Výběr kombinací** — zaškrtni konkrétní kombinace (Gold troy oz / CZK, Silver gram / USD, ...)
3. **Nastavení** — interval aktualizace (min. 60s) a počet desetinných míst

## Reload
Nastavení → Zařízení a služby → Noble Metals Market → Reload
nebo: `service: noble_metals_market.reload`
