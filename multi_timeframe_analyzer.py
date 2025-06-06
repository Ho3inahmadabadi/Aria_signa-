import pandas as pd
from indicators import compute_indicators


class TimeframeSignal:
    """Analyze a single timeframe dataframe and produce signals."""

    def __init__(self, df: pd.DataFrame):
        self.df = compute_indicators(df.copy())

    def _determine(self, row: pd.Series) -> str:
        if (
            row["close"] > row["EMA200"]
            and row["EMA9"] > row["EMA21"] > row["EMA50"] > row["EMA200"]
            and row["RSI"] > 55
        ):
            return "LONG"
        if (
            row["close"] < row["EMA200"]
            and row["EMA9"] < row["EMA21"] < row["EMA50"] < row["EMA200"]
            and row["RSI"] < 45
        ):
            return "SHORT"
        return "NO_SIGNAL"

    def signal_at(self, timestamp: pd.Timestamp) -> str:
        rows = self.df[self.df["open_time"] <= timestamp]
        if rows.empty:
            return "NO_SIGNAL"
        row = rows.iloc[-1]
        return self._determine(row)


class MultiTimeframeAnalyzer:
    """Combine multiple timeframe signals into a final signal."""

    def __init__(self, data: dict[str, pd.DataFrame]):
        self.analyzers = {tf: TimeframeSignal(df) for tf, df in data.items()}

    def analyze(self, timestamp: pd.Timestamp) -> tuple[str, dict[str, str]]:
        details = {tf: an.signal_at(timestamp) for tf, an in self.analyzers.items()}
        final = "NO_SIGNAL"
        if (
            details.get("5m") == "LONG"
            and details.get("3m") == "LONG"
            and details.get("1m") == "LONG"
            and details.get("15m") in ["LONG", "NO_SIGNAL"]
        ):
            final = "LONG"
        elif (
            details.get("5m") == "SHORT"
            and details.get("3m") == "SHORT"
            and details.get("1m") == "SHORT"
            and details.get("15m") in ["SHORT", "NO_SIGNAL"]
        ):
            final = "SHORT"
        return final, details
