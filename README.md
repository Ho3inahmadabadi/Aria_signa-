# Aria Signa

This repository demonstrates a simple multi‑timeframe trading bot for **BTCUSDT** futures. It shows how to compute common technical indicators, combine signals from several timeframes and optionally send alerts to Telegram.

## Modules

- **indicators.py** – helper functions for EMA, RSI and ATR calculations.
- **multi_timeframe_analyzer.py** – merges signals from 1m/3m/5m/15m timeframes into a single decision.
- **futures_backtest.py** – downloads historical candles from Binance and runs a short backtest while printing logs.
- **futures_live_pro_bot.py** – checks for new signals and can send a Telegram message.
- **full_test.py** – end‑to‑end script for a quick demo using historical data.

## Quick start

```bash
pip install -r requirements.txt
# Use the --offline flag to run with the sample CSVs under tests/data/
python full_test.py --offline
```

Use `--offline` to run the test with the bundled data found in `tests/data/`. Omit the flag to fetch fresh candles from Binance (requires internet access).

For live Telegram alerts set the environment variables `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` and then run:

```bash
python futures_live_pro_bot.py
```
