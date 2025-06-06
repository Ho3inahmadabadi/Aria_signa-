# Aria Signa

This project implements a small crypto futures scalping bot for **Binance Futures**.
It focuses on a single symbol (`BTCUSDT`) and analyses four timeframes (1m, 3m, 5m, 15m)
using EMA, RSI and ATR indicators. A signal is emitted only when all four timeframes
agree on `LONG` or `SHORT`.

## Modules

- **indicators.py** – indicator helpers (EMA, RSI, ATR).
- **multi_timeframe_analyzer.py** – merges timeframe signals into a final one.
- **futures_backtest.py** – backtest logic printing detailed logs.
- **futures_live_pro_bot.py** – fetches live candles and sends Telegram alerts.
- **full_test.py** – simple script that runs an end‑to‑end test.

## Quick start

```bash
pip install -r requirements.txt
python full_test.py --offline  # run a short offline test
```

To run live with Telegram alerts set the environment variables
`TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` then execute:

```bash
python futures_live_pro_bot.py
```

Sample CSV data is provided under `tests/data/` for the offline mode.
