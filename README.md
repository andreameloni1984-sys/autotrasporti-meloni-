# AUTOTRASPORTI MELONI

Bot di base per il monitoraggio di incentivi, contributi, rimborsi, carburanti, mezzi, rimessa, officina, energia, formazione e novità normative per l'autotrasporto.

## Stato

- Ricerca automatica periodica: **DISATTIVATA**
- Workflow GitHub: avvio solo manuale
- Telegram: supportato tramite secrets
- Database SQLite: locale al workflow

## Comandi Telegram

- /start
- /nuovi
- /aggiorna

## Secrets

Configurare in GitHub Actions:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

La ricerca automatica non viene eseguita da uno scheduler: il workflow è volutamente `workflow_dispatch` per rispettare lo stop della ricerca.
