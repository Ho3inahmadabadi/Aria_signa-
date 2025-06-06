# Aria Signa

This repository demonstrates a simple real‑time multi‑timeframe trading bot for USDT‑margined futures.  Signals are produced by combining four timeframes and can optionally be pushed to Telegram.

## Modules

- **indicators.py** – helper functions for EMA, RSI and ATR calculations.
- **multi_timeframe_analyzer.py** – merges signals from 1m/3m/5m/15m timeframes into a single decision.
- **futures_backtest.py** – fetches historical futures data from Binance and runs a short backtest.
- **futures_live_pro_bot.py** – real‑time signal generator for a list of futures symbols.
- **full_test.py** – simple online tester that prints the latest signal for a single symbol.

## Quick start

```bash
pip install -r requirements.txt
python full_test.py
```

`full_test.py` fetches recent candles from Binance Futures and prints the most recent signal.  For real‑time notifications set the environment variables `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` and run:

```bash
python futures_live_pro_bot.py
```

The list of symbols, ATR multipliers and confidence threshold can be tweaked at the top of `futures_live_pro_bot.py`.
