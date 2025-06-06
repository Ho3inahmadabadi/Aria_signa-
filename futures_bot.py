import os
import time
from datetime import datetime
from typing import List, Tuple, Dict

import pandas as pd
import requests

BINANCE_BASE = "https://fapi.binance.com"
KLINES_ENDPOINT = f"{BINANCE_BASE}/fapi/v1/klines"

CANDLE_LIMIT = 150  # enough history for indicators
MESSAGE_DELAY = 20  # seconds between Telegram alerts
LOOP_DELAY = 300  # 5 minutes between full scans
SYMBOL_DELAY = 2  # delay between symbol scans
TIMEFRAMES = ["1m", "3m", "5m", "15m"]

# Fixed list of 20 popular USDT‑margined futures pairs
TOP_SYMBOLS: List[str] = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "SHIBUSDT",
    "DOTUSDT",
    "NEARUSDT",
    "TRXUSDT",
    "SUIUSDT",
    "APTUSDT",
    "LINKUSDT",
    "UNIUSDT",
    "HBARUSDT",
    "MATICUSDT",
    "ZECUSDT",
    "WLDUSDT",
]


def get_top_symbols(limit: int = len(TOP_SYMBOLS)) -> List[str]:
    """Return the fixed list of symbols (optionally truncated)."""
    return TOP_SYMBOLS[:limit]


def fetch_klines(symbol: str, interval: str, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        resp = requests.get(KLINES_ENDPOINT, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch klines for {symbol}: {exc}")
        return pd.DataFrame()
    data = resp.json()
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "qav",
        "trades",
        "tbbav",
        "tbqav",
        "ignore",
    ]
    df = pd.DataFrame(data, columns=cols)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    for span in [9, 21, 50, 200]:
        df[f"EMA{span}"] = ema(df["close"], span)
    df["RSI"] = rsi(df["close"], 14)
    df["ATR"] = atr(df["high"], df["low"], df["close"], 14)
    df["VOL_AVG20"] = df["volume"].rolling(window=20).mean()
    return df


def detect_signal(df: pd.DataFrame) -> Tuple[str, float]:
    """Return timeframe signal and ATR value."""
    if len(df) < 22:
        return "", 0.0

    last = df.iloc[-1]
    prev = df.iloc[-2]

    long_cross = prev["EMA9"] < prev["EMA21"] and last["EMA9"] > last["EMA21"]
    short_cross = prev["EMA9"] > prev["EMA21"] and last["EMA9"] < last["EMA21"]

    atr_breakout = (last["high"] - last["low"]) > 1.2 * last["ATR"]
    vol_spike = last["volume"] > 1.3 * last["VOL_AVG20"]

    if long_cross and 50 < last["RSI"] < 70 and atr_breakout and vol_spike:
        return "LONG", last["ATR"]
    if short_cross and 30 < last["RSI"] < 50 and atr_breakout and vol_spike:
        return "SHORT", last["ATR"]
    return "", 0.0


def levels(signal: str, price: float, atr_value: float) -> Tuple[float, float]:
    risk = atr_value * 1.5
    if signal == "LONG":
        sl = price - risk
        tp = price + 2 * risk
    else:
        sl = price + risk
        tp = price - 2 * risk
    return sl, tp


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials not set")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message})
    except requests.RequestException as exc:
        print(f"Telegram error: {exc}")


def format_message(symbol: str, signal: str, price: float, sl: float, tp: float, confidence: int) -> str:
    """Return a nicely formatted Telegram message."""
    time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return (
        "\ud83d\ude80 \u0633\u06cc\u06af\u0646\u0627\u0644 \u062c\u062f\u06cc\u062f!\n"
        f"\ud83d\udccd \u0627\u0631\u0632: {symbol}\n"
        f"\ud83d\udc4d \u062c\u0647\u062a: {signal}\n"
        f"\ud83d\udcb5 \u0642\u06cc\u0645\u062a \u0641\u0639\u0644\u06cc: {price:.2f} USDT\n"
        f"\ud83c\udfaf \u0646\u0642\u0637\u0647 \u0648\u0631\u0648\u062f: {price:.2f} USDT\n"
        f"\ud83d\udee1\ufe0f \u062d\u062f \u0636\u0631\u0631 (SL): {sl:.2f} USDT\n"
        f"\ud83c\udf81 \u062d\u062f \u0633\u0648\u062f (TP): {tp:.2f} USDT\n"
        f"\ud83d\udcca \u0627\u0639\u062a\u0628\u0627\u0631 \u0633\u06cc\u06af\u0646\u0627\u0644: {confidence}%\n"
        f"\u23f3 \u062a\u0627\u06cc\u0645\u200c\u0641\u0631\u06cc\u0645: 1m/3m/5m/15m\n"
        "\ud83d\udcc8 \u062a\u0648\u0636\u06cc\u062d: \u06a9\u0631\u0627\u0633 EMA + \u062a\u0627\u06cc\u06cc\u062f RSI + \u062d\u062c\u0645 \u0628\u0627\u0644\u0627\n"
        f"\u23f0 \u0632\u0645\u0627\u0646: {time_str}"
    )


def analyze_symbol(symbol: str) -> Tuple[str, float, float, float, int]:
    """Fetch data for all timeframes and determine final signal."""
    data: Dict[str, pd.DataFrame] = {}
    signals: Dict[str, str] = {}
    atrs: Dict[str, float] = {}
    vol_ok = True

    for tf in TIMEFRAMES:
        df = fetch_klines(symbol, tf)
        if df.empty:
            return "", 0.0, 0.0, 0.0, 0
        df = compute_indicators(df)
        sig, atr_val = detect_signal(df)
        signals[tf] = sig if sig else "NO_SIGNAL"
        atrs[tf] = atr_val
        data[tf] = df
        if tf == "5m":
            last = df.iloc[-1]
            vol_ok = last["volume"] > 1.3 * last["VOL_AVG20"]

    final = "NO_SIGNAL"
    if (
        signals.get("5m") == "LONG"
        and signals.get("3m") == "LONG"
        and signals.get("1m") == "LONG"
        and signals.get("15m") in ["LONG", "NO_SIGNAL"]
    ):
        final = "LONG"
    elif (
        signals.get("5m") == "SHORT"
        and signals.get("3m") == "SHORT"
        and signals.get("1m") == "SHORT"
        and signals.get("15m") in ["SHORT", "NO_SIGNAL"]
    ):
        final = "SHORT"

    if final == "NO_SIGNAL" or not vol_ok:
        return "", 0.0, 0.0, 0.0, 0

    price = data["5m"].iloc[-1]["close"]
    sl, tp = levels(final, price, atrs["5m"])
    confidence = sum(1 for tf in TIMEFRAMES if signals.get(tf) == final)
    conf_pct = confidence / len(TIMEFRAMES) * 100
    return final, price, sl, tp, int(conf_pct)


def main() -> None:
    last_msg_time = 0.0
    while True:
        for symbol in get_top_symbols():
            signal, price, sl, tp, conf = analyze_symbol(symbol)
            if signal and conf >= 80:
                msg = format_message(symbol, signal, price, sl, tp, conf)
                now = time.time()
                wait = MESSAGE_DELAY - (now - last_msg_time)
                if wait > 0:
                    time.sleep(wait)
                send_telegram(msg)
                print(f"Sent signal for {symbol}: {signal} ({conf}%)")
                last_msg_time = time.time()
            time.sleep(SYMBOL_DELAY)
        time.sleep(LOOP_DELAY)


if __name__ == "__main__":
    main()

