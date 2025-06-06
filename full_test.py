import argparse
import pandas as pd
from futures_backtest import fetch_klines, prepare_data, backtest
from multi_timeframe_analyzer import MultiTimeframeAnalyzer


def load_offline_data(symbol: str) -> dict[str, pd.DataFrame]:
    tfs = ["1m", "3m", "5m", "15m"]
    data = {}
    for tf in tfs:
        path = f"tests/data/{tf}.csv"
        df = pd.read_csv(path, parse_dates=["open_time", "close_time"])
        data[tf] = df
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="use bundled data instead of Binance API")
    args = parser.parse_args()

    symbol = "BTCUSDT"
    data = load_offline_data(symbol) if args.offline else prepare_data(symbol)
    analyzer = MultiTimeframeAnalyzer(data)
    ts = data["1m"].iloc[-1]["open_time"]
    final, details = analyzer.analyze(ts)
    print(f"Latest Final Signal: {final} | Details: {details}")
    print("Running short backtest...")
    backtest(symbol, data if args.offline else None)


if __name__ == "__main__":
    main()
