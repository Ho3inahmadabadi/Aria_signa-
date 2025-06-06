import os
import time
import pandas as pd
import requests

from multi_timeframe_analyzer import MultiTimeframeAnalyzer
from futures_backtest import fetch_klines


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials not set")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "TRXUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "DOTUSDT",
    "LTCUSDT",
    "SHIBUSDT",
    "ETCUSDT",
    "ATOMUSDT",
    "AVAXUSDT",
    "UNIUSDT",
    "BCHUSDT",
    "ICPUSDT",
    "APTUSDT",
]

ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
CONFIDENCE_THRESHOLD = 0.75


def run() -> None:
    tfs = ["1m", "3m", "5m", "15m"]
    state = {}
    for symbol in SYMBOLS:
        data = {tf: fetch_klines(symbol, tf, limit=200) for tf in tfs}
        last_times = {tf: df.iloc[-1]["open_time"] for tf, df in data.items()}
        state[symbol] = {"data": data, "last_times": last_times, "last_signal": None}

    while True:
        for symbol in SYMBOLS:
            data = state[symbol]["data"]
            last_times = state[symbol]["last_times"]
            for tf in tfs:
                last_ts = last_times[tf]
                start_ms = int((last_ts + pd.Timedelta(minutes=1)).timestamp() * 1000)
                new = fetch_klines(symbol, tf, limit=2, start_time=start_ms)
                if not new.empty:
                    new = new[new["open_time"] > last_ts]
                    if not new.empty:
                        data[tf] = pd.concat([data[tf], new]).iloc[-200:]
                        last_times[tf] = new.iloc[-1]["open_time"]

            analyzer = MultiTimeframeAnalyzer(
                data,
                atr_sl=ATR_SL_MULT,
                atr_tp=ATR_TP_MULT,
                confidence_threshold=CONFIDENCE_THRESHOLD,
            )
            ts = data["1m"].iloc[-1]["open_time"]
            final, details, conf = analyzer.analyze(ts)
            if final in ["LONG", "SHORT"] and final != state[symbol]["last_signal"]:
                msg = (
                    f"{symbol} | Time: {ts} | Signal: {final} | Conf: {conf:.2f}\n"
                    f"Details: {details}"
                )
                send_telegram(msg)
                state[symbol]["last_signal"] = final

        time.sleep(60)


if __name__ == "__main__":
    run()
