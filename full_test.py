import argparse
import pandas as pd
from futures_backtest import fetch_klines
from multi_timeframe_analyzer import MultiTimeframeAnalyzer


TFS = ["1m", "3m", "5m", "15m"]


def load_recent(symbol: str) -> dict[str, pd.DataFrame]:
    data = {}
    for tf in TFS:
        data[tf] = fetch_klines(symbol, tf, limit=200)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT", help="futures symbol")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="minimum confidence for reporting a signal",
    )
    args = parser.parse_args()

    data = load_recent(args.symbol)
    analyzer = MultiTimeframeAnalyzer(data, confidence_threshold=args.threshold)
    ts = data["1m"].iloc[-1]["open_time"]
    final, details, confidence = analyzer.analyze(ts)
    print(f"Symbol: {args.symbol} | Final: {final} | Confidence: {confidence:.2f} | Details: {details}")


if __name__ == "__main__":
    main()
