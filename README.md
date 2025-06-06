# Aria Signa

This repository provides a simple crypto futures scalping bot for **Binance Futures**. It scans a fixed list of twenty high-volume USDT pairs every five minutes, looks for high-probability LONG/SHORT setups and optionally sends alerts to Telegram.

## Files

- **futures_bot.py** – main script running the scalping loop and Telegram alerts.
- **indicators.py** – helper functions for EMA, RSI and ATR calculations.
- **multi_timeframe_analyzer.py** – earlier example of multi‑timeframe logic (kept for reference).
- **futures_backtest.py** and **full_test.py** – basic backtesting utilities.

## Quick start

```bash
pip install -r requirements.txt
python futures_bot.py
```

For testing without internet access use the bundled sample data:

```bash
python full_test.py --offline
```

Set the environment variables `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` to enable Telegram notifications. The bot fetches live data from Binance Futures, so it requires internet access when running live.

