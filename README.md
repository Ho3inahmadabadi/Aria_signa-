# Aria Signa

This repository contains a simple multi-timeframe trading bot example for **BTCUSDT** futures. It demonstrates computing technical indicators, combining signals across multiple timeframes and sending alerts to Telegram.

## Modules

- **indicators.py** – helper functions for EMA, RSI and ATR calculation.
- **multi_timeframe_analyzer.py** – combines indicator data from 1m/3m/5m/15m timeframes into a final LONG/SHORT/NO_SIGNAL decision.
- **futures_backtest.py** – downloads historical candles from Binance and runs a simple backtest while printing logs.
- **futures_live_pro_bot.py** – checks for new signals and optionally sends a Telegram message.
- **full_test.py** – quick end‑to‑end test downloading data and running the backtest.

## Quick start

```bash
pip install -r requirements.txt
python full_test.py --offline
```

Use `--offline` to run the test with bundled sample data. Omit the flag to
download fresh candles from Binance (requires internet access).

For live Telegram alerts set the environment variables `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` then run:

```bash
python futures_live_pro_bot.py
```
