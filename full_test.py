import argparse
import pandas as pd

from futures_backtest import fetch_klines, prepare_data, backtest
from multi_timeframe_analyzer import MultiTimeframeAnalyzer


def load_offline() -> dict[str, pd.DataFrame]:
    tfs = ["1m", "3m", "5m", "15m"]
    data = {}
    for tf in tfs:
        df = pd.read_csv(f"tests/data/{tf}.csv", parse_dates=["open_time", "close_time"])
        data[tf] = df
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="use bundled data")
    args = parser.parse_args()

    if args.offline:
        data = load_offline()
    else:
        data = prepare_data("BTCUSDT")

    analyzer = MultiTimeframeAnalyzer(data)
    ts = data["1m"].iloc[-1]["open_time"]
    final, details = analyzer.analyze(ts)
    print(f"Latest Final Signal: {final} | Details: {details}")

    print("Running backtest...")
    backtest("BTCUSDT", data if args.offline else None)


if __name__ == "__main__":
    main()
