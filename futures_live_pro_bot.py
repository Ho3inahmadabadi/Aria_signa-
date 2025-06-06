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


def run(symbol: str = "BTCUSDT") -> None:
    tfs = ["1m", "3m", "5m", "15m"]
    data = {tf: fetch_klines(symbol, tf, limit=200) for tf in tfs}
    last_times = {tf: df.iloc[-1]["open_time"] for tf, df in data.items()}
    analyzer = MultiTimeframeAnalyzer(data)
    last_signal = None

    while True:
        for tf in tfs:
            last_ts = last_times[tf]
            start_ms = int((last_ts + pd.Timedelta(minutes=1)).timestamp() * 1000)
            new = fetch_klines(symbol, tf, limit=1, start_time=start_ms)
            if not new.empty and new.iloc[-1]["open_time"] != last_ts:
                data[tf] = pd.concat([data[tf], new]).iloc[-200:]
                last_times[tf] = new.iloc[-1]["open_time"]

        analyzer = MultiTimeframeAnalyzer(data)
        ts = data["1m"].iloc[-1]["open_time"]
        final, details = analyzer.analyze(ts)
        if final in ["LONG", "SHORT"] and final != last_signal:
            msg = f"Time: {ts} | Final Signal: {final}\nDetails: {details}"
            send_telegram(msg)
            last_signal = final
        time.sleep(60)


if __name__ == "__main__":
    run()
