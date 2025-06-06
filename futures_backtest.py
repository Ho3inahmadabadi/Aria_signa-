import pandas as pd
import requests
from typing import Dict, Optional

from multi_timeframe_analyzer import MultiTimeframeAnalyzer


BASE_URL = "https://api.binance.com/api/v3/klines"


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 500,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> pd.DataFrame:
    """Fetch klines from Binance API."""
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if start_time is not None:
        params["startTime"] = start_time
    if end_time is not None:
        params["endTime"] = end_time
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch klines {symbol} {interval}: {exc}")
        return pd.DataFrame()
    data = response.json()
    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    df = pd.DataFrame(data, columns=columns)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def prepare_data(symbol: str) -> Dict[str, pd.DataFrame]:
    tfs = ["1m", "3m", "5m", "15m"]
    return {tf: fetch_klines(symbol, tf, limit=500) for tf in tfs}


def backtest(symbol: str = "BTCUSDT", data: Optional[Dict[str, pd.DataFrame]] = None) -> None:
    if data is None:
        data = prepare_data(symbol)
    analyzer = MultiTimeframeAnalyzer(data)
    base = data["1m"]

    position = None
    entry_price = 0.0
    trades = []

    for _, row in base.iterrows():
        ts = row["open_time"]
        final, details = analyzer.analyze(ts)
        log = f"Time: {ts} | Final Signal: {final} | Details: {details}"
        trade_result = "NONE"

        if position and final != position and final != "NO_SIGNAL":
            exit_price = row["open"]
            profit = exit_price - entry_price if position == "LONG" else entry_price - exit_price
            trade_result = "WIN" if profit > 0 else "LOSS"
            trades.append(trade_result)
            position = None

        if final in ["LONG", "SHORT"] and position is None:
            position = final
            entry_price = row["open"]

        if trade_result != "NONE":
            print(f"{log} | Trade Result: {trade_result}")
        else:
            print(log)

    # Close remaining open position at end of backtest
    if position is not None:
        last_close = base.iloc[-1]["close"]
        profit = last_close - entry_price if position == "LONG" else entry_price - last_close
        trade_result = "WIN" if profit > 0 else "LOSS"
        trades.append(trade_result)
        print(
            f"Time: {base.iloc[-1]['open_time']} | Final Signal: END | Details: close position"
            f" | Trade Result: {trade_result}"
        )

    total = len(trades)
    wins = trades.count("WIN")
    losses = trades.count("LOSS")
    win_rate = (wins / total * 100) if total else 0
    print(f"Total Trades: {total} | Wins: {wins} | Losses: {losses} | Win Rate: {win_rate:.2f}%")


if __name__ == "__main__":
    backtest()
